import base64
import json
from datetime import datetime, timedelta, timezone as dt_timezone

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.core.files.base import ContentFile
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.models import Patient, Profile, TranscriptChunk, Visit
from core.services.ai import generate_visit_output, output_to_dict
from core.services.comics import generate_comic_for_output
from core.services.pdf import build_school_note_pdf
from core.services.transcription import transcribe_audio


def _profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def _json_body(request):
    if request.content_type and "application/json" in request.content_type:
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return {}
    return request.POST.dict()


def _json_error(message, status=400, code="bad_request"):
    return JsonResponse({"ok": False, "error": {"code": code, "message": message}}, status=status)


def _token_for_user(user):
    profile = _profile(user)
    now = datetime.now(dt_timezone.utc)
    payload = {
        "iss": settings.JWT_ISSUER,
        "sub": str(user.id),
        "role": profile.role,
        "name": profile.display_name or user.get_full_name() or user.username,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_TTL_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def _bearer_user(request):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            issuer=settings.JWT_ISSUER,
        )
    except jwt.PyJWTError:
        return None
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        return User.objects.get(id=payload["sub"])
    except User.DoesNotExist:
        return None


def _actor(request, roles=None):
    user = request.user if getattr(request, "user", None) and request.user.is_authenticated else _bearer_user(request)
    if not user or isinstance(user, AnonymousUser):
        return None
    profile = _profile(user)
    if roles and profile.role not in roles:
        return None
    return user


def _patient_dict(patient):
    return {
        "id": patient.id,
        "name": patient.name,
        "guardian_name": patient.guardian_name,
        "guardian_email": patient.guardian_email,
        "guardian_phone": patient.guardian_phone,
        "age_years": patient.age_years,
        "gender": patient.gender,
        "gender_label": patient.get_gender_display(),
        "weight_kg": str(patient.weight_kg) if patient.weight_kg else "",
        "primary_language": patient.primary_language,
        "allergies": patient.allergies,
        "notes": patient.notes,
        "updated_at": patient.updated_at.isoformat(),
    }


def _visit_dict(visit):
    data = {
        "id": visit.id,
        "patient": _patient_dict(visit.patient),
        "clinical_scenario": visit.clinical_scenario,
        "scenario_label": visit.scenario_label,
        "diagnosis": visit.diagnosis,
        "status": visit.status,
        "transcript": visit.transcript,
        "doctor_notes": visit.doctor_notes,
        "share_url": f"/portal/{visit.share_token}/",
        "created_at": visit.created_at.isoformat(),
    }
    if hasattr(visit, "output"):
        data["output"] = output_to_dict(visit.output)
    return data


@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    data = _json_body(request)
    username = data.get("username") or data.get("email")
    password = data.get("password")
    user = authenticate(request, username=username, password=password)
    if not user:
        return _json_error("帳號或密碼錯誤。", status=401, code="invalid_credentials")
    profile = _profile(user)
    return JsonResponse(
        {
            "ok": True,
            "access_token": _token_for_user(user),
            "token_type": "Bearer",
            "expires_in": settings.JWT_TTL_MINUTES * 60,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": profile.role,
                "display_name": profile.display_name or user.get_full_name() or user.username,
            },
        }
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def patient_collection(request):
    actor = _actor(request, roles=[Profile.ROLE_DOCTOR])
    if not actor:
        return _json_error("需要醫師權限。", status=403, code="forbidden")

    if request.method == "GET":
        patients = Patient.objects.filter(doctor=actor)
        return JsonResponse({"ok": True, "patients": [_patient_dict(patient) for patient in patients]})

    data = _json_body(request)
    name = (data.get("name") or "").strip()
    if not name:
        return _json_error("請填寫病患姓名。")
    age_years = int(data.get("age_years") or 6)
    if age_years < 0 or age_years > 17:
        return _json_error("目前流程限定 0-17 歲兒童與青少年。")
    gender = data.get("gender") or "unknown"
    if gender not in dict(Patient.GENDER_CHOICES):
        gender = "unknown"
    patient = Patient.objects.create(
        doctor=actor,
        name=name,
        guardian_name=(data.get("guardian_name") or "").strip(),
        guardian_email=(data.get("guardian_email") or "").strip(),
        guardian_phone=(data.get("guardian_phone") or "").strip(),
        age_years=age_years,
        gender=gender,
        weight_kg=data.get("weight_kg") or None,
        primary_language=data.get("primary_language") or "zh-Hant",
        allergies=(data.get("allergies") or "").strip(),
        notes=(data.get("notes") or "").strip(),
    )
    return JsonResponse({"ok": True, "patient": _patient_dict(patient)}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def visit_start(request):
    actor = _actor(request, roles=[Profile.ROLE_DOCTOR])
    if not actor:
        return _json_error("需要醫師權限。", status=403, code="forbidden")

    data = _json_body(request)
    patient = get_object_or_404(Patient, id=data.get("patient_id"), doctor=actor)

    visit = Visit.objects.create(
        doctor=actor,
        patient=patient,
        clinical_scenario=data.get("clinical_scenario") or Visit.SCENARIO_GENERAL,
        diagnosis=(data.get("diagnosis") or "AI 分析中").strip(),
        consent_confirmed=bool(data.get("consent_confirmed", True)),
        doctor_notes=(data.get("doctor_notes") or "").strip(),
        status=Visit.STATUS_RECORDING,
    )
    return JsonResponse({"ok": True, "session_id": visit.id, "visit": _visit_dict(visit)}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def visit_transcribe(request):
    actor = _actor(request, roles=[Profile.ROLE_DOCTOR])
    if not actor:
        return _json_error("需要醫師權限。", status=403, code="forbidden")

    visit = get_object_or_404(Visit, id=request.POST.get("visit_id") or request.GET.get("visit_id"), doctor=actor)
    text = request.POST.get("text", "")
    if request.FILES.get("audio"):
        text = transcribe_audio(request.FILES["audio"]) or text
    if text:
        visit.transcript = "\n".join(part for part in [visit.transcript, text] if part)
        visit.save(update_fields=["transcript", "updated_at"])
        TranscriptChunk.objects.create(
            visit=visit,
            sequence=visit.chunks.count() + 1,
            source=TranscriptChunk.SOURCE_STT,
            text=text,
            expires_at=visit.audio_delete_after,
        )
    return JsonResponse({"ok": True, "text": text, "transcript": visit.transcript})


@csrf_exempt
@require_http_methods(["POST"])
def visit_complete(request):
    actor = _actor(request, roles=[Profile.ROLE_DOCTOR])
    if not actor:
        return _json_error("需要醫師權限。", status=403, code="forbidden")

    data = _json_body(request)
    visit = get_object_or_404(Visit, id=data.get("visit_id") or data.get("session_id"), doctor=actor)
    visit.status = Visit.STATUS_PROCESSING
    visit.transcript = (data.get("transcript") or visit.transcript or "").strip()
    visit.doctor_notes = (data.get("doctor_notes") or visit.doctor_notes or "").strip()
    visit.save(update_fields=["status", "transcript", "doctor_notes", "updated_at"])

    output = generate_visit_output(visit)
    return JsonResponse({"ok": True, "output": output_to_dict(output)})


@csrf_exempt
@require_http_methods(["GET"])
def output_detail(request, visit_id):
    actor = _actor(request, roles=[Profile.ROLE_DOCTOR, Profile.ROLE_PARENT])
    if not actor:
        return _json_error("需要登入或 JWT。", status=403, code="forbidden")
    visit = get_object_or_404(Visit, id=visit_id)
    if _profile(actor).role == Profile.ROLE_DOCTOR and visit.doctor_id != actor.id:
        return _json_error("無權限檢視此診次。", status=403, code="forbidden")
    if _profile(actor).role == Profile.ROLE_PARENT and actor.email != visit.patient.guardian_email:
        return _json_error("無權限檢視此診次。", status=403, code="forbidden")
    if not hasattr(visit, "output"):
        return _json_error("此診次尚未產生輸出。", status=404, code="not_ready")
    return JsonResponse({"ok": True, "output": output_to_dict(visit.output)})


@csrf_exempt
@require_http_methods(["POST"])
def output_approve(request, visit_id):
    actor = _actor(request, roles=[Profile.ROLE_DOCTOR])
    if not actor:
        return _json_error("需要醫師權限。", status=403, code="forbidden")
    visit = get_object_or_404(Visit, id=visit_id, doctor=actor)
    if not hasattr(visit, "output"):
        return _json_error("此診次尚未產生輸出。", status=404, code="not_ready")
    profile = _profile(actor)
    visit.status = Visit.STATUS_APPROVED
    visit.signed_at = timezone.now()
    visit.signed_by = profile.signature_text or profile.display_name or actor.get_full_name() or actor.username
    visit.save(update_fields=["status", "signed_at", "signed_by", "updated_at"])
    visit.output.approved_at = timezone.now()
    visit.output.save(update_fields=["approved_at"])
    return JsonResponse({"ok": True, "output": output_to_dict(visit.output)})


@csrf_exempt
@require_http_methods(["GET"])
def school_note_pdf(request, visit_id):
    actor = _actor(request, roles=[Profile.ROLE_DOCTOR, Profile.ROLE_PARENT])
    if not actor:
        return _json_error("需要登入或 JWT。", status=403, code="forbidden")
    visit = get_object_or_404(Visit, id=visit_id)
    if _profile(actor).role == Profile.ROLE_DOCTOR and visit.doctor_id != actor.id:
        return _json_error("無權限下載此 PDF。", status=403, code="forbidden")
    if _profile(actor).role == Profile.ROLE_PARENT and actor.email != visit.patient.guardian_email:
        return _json_error("無權限下載此 PDF。", status=403, code="forbidden")
    if not hasattr(visit, "output"):
        return _json_error("此診次尚未產生輸出。", status=404, code="not_ready")
    pdf = build_school_note_pdf(visit)
    filename = f"openpedicare-school-note-{visit.id}.pdf"
    return FileResponse(pdf, as_attachment=True, filename=filename, content_type="application/pdf")


@csrf_exempt
@require_http_methods(["POST"])
def output_comic(request, visit_id):
    actor = _actor(request, roles=[Profile.ROLE_DOCTOR])
    if not actor:
        return _json_error("需要醫師權限。", status=403, code="forbidden")
    visit = get_object_or_404(Visit, id=visit_id, doctor=actor)
    if not hasattr(visit, "output"):
        return _json_error("此診次尚未產生輸出。", status=404, code="not_ready")
    if not settings.COMIC_GENERATION_ENABLED:
        return _json_error("四宮格漫畫功能尚未設定 OPENAI_IMAGE_API_KEY。", status=400, code="image_api_not_configured")
    try:
        output = generate_comic_for_output(visit.output)
    except Exception:
        return _json_error("漫畫生成失敗，請稍後再試或確認 OpenAI image key。", status=502, code="comic_generation_failed")
    return JsonResponse({"ok": True, "output": output_to_dict(output)})


def append_audio_chunk_from_base64(visit, payload):
    audio_b64 = payload.get("data", "")
    if "," in audio_b64:
        audio_b64 = audio_b64.split(",", 1)[1]
    if not audio_b64:
        return None
    binary = base64.b64decode(audio_b64)
    sequence = visit.chunks.count() + 1
    chunk = TranscriptChunk(
        visit=visit,
        sequence=sequence,
        source=TranscriptChunk.SOURCE_BROWSER,
        expires_at=visit.audio_delete_after,
    )
    mime = payload.get("mime_type") or "audio/webm"
    ext = "webm" if "webm" in mime else "wav"
    chunk.audio_file.save(f"visit-{visit.id}-chunk-{sequence}.{ext}", ContentFile(binary), save=True)
    return chunk
