import base64
import hashlib
import hmac
import json
import logging
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone

from core.models import Patient, Visit


logger = logging.getLogger(__name__)

HELP_KEYWORDS = {"help", "start", "說明", "幫助", "查詢格式", "格式", "開始"}
QUERY_PREFIXES = ("查詢", "查紀錄", "看診紀錄", "最近一次", "最近紀錄", "病歷")
LINE_TEXT_LIMIT = 5000
LINE_REPLY_MESSAGE_LIMIT = 5


def verify_line_signature(body, signature, channel_secret):
    if not channel_secret or not signature:
        return False
    digest = hmac.new(channel_secret.encode("utf-8"), body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def build_help_text():
    return (
        "OpenPediCare LINE 查詢\n"
        "請輸入孩子姓名與家長手機或 Email，系統會回覆最近一次已產生的診後紀錄。\n\n"
        "格式範例：\n"
        "查詢 Demo Child +1-555-0100\n"
        "查詢 Demo Child parent@example.test\n\n"
        "也可以分行輸入：\n"
        "姓名：Demo Child\n"
        "手機：+1-555-0100\n\n"
        "為保護隱私，姓名與聯絡資訊都吻合時才會顯示紀錄。"
    )


def message_objects_for_event(event, request):
    event_type = event.get("type")
    if event_type == "follow":
        return _text_messages("歡迎使用 OpenPediCare。\n\n" + build_help_text())

    if event_type != "message":
        return []

    message = event.get("message") or {}
    if message.get("type") != "text":
        return _text_messages("目前 LINE Bot 只支援文字查詢。\n\n" + build_help_text())

    text = (message.get("text") or "").strip()
    if not text or _is_help_request(text):
        return _text_messages(build_help_text())

    query = parse_lookup_text(text)
    if not query:
        return _text_messages("我還需要孩子姓名與家長手機或 Email 才能查詢。\n\n" + build_help_text())

    child_name, contact = query
    visit, reason = find_recent_visit(child_name, contact)
    if not visit:
        return _text_messages(_not_found_text(reason))

    return _text_messages(_visit_reply_text(visit, _public_base_url(request)))


def parse_lookup_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    fields = {}

    for line in lines:
        if "：" in line:
            label, value = line.split("：", 1)
        elif ":" in line:
            label, value = line.split(":", 1)
        else:
            continue
        key = _field_key(label)
        if key and value.strip():
            fields[key] = value.strip()

    if fields.get("name") and fields.get("contact"):
        return fields["name"], fields["contact"]

    cleaned = _strip_query_prefix(text.replace("\n", " "))
    tokens = [token.strip(" ,，;；") for token in cleaned.split() if token.strip(" ,，;；")]
    contact_index = None
    for index, token in enumerate(tokens):
        if _looks_like_contact(token):
            contact_index = index
            break

    if contact_index is None:
        return None

    contact = tokens[contact_index]
    name_tokens = tokens[:contact_index] + tokens[contact_index + 1 :]
    name_tokens = [token for token in name_tokens if not _field_key(token)]
    name = " ".join(name_tokens).strip()
    if not name:
        name = fields.get("name", "")
    if not name:
        return None
    return name, contact


def find_recent_visit(child_name, contact):
    candidates = list(_candidate_patients(child_name))
    matched_patients = [patient for patient in candidates if _contact_matches(patient, contact)]
    if not matched_patients:
        return None, "not_found"

    visits = (
        Visit.objects.filter(patient__in=matched_patients, output__isnull=False)
        .select_related("patient", "doctor", "output")
        .order_by("-created_at")
    )
    if settings.LINEBOT_ONLY_APPROVED_VISITS:
        visits = visits.filter(status=Visit.STATUS_APPROVED)

    visit = visits.first()
    if not visit:
        return None, "no_output"
    return visit, "ok"


def reply_to_line(reply_token, messages):
    if not reply_token or not messages:
        return {"ok": False, "skipped": "empty_reply"}
    if not settings.LINE_CHANNEL_ACCESS_TOKEN:
        logger.warning("LINE_CHANNEL_ACCESS_TOKEN is not configured; reply skipped.")
        return {"ok": False, "skipped": "missing_access_token"}

    payload = json.dumps({"replyToken": reply_token, "messages": messages}).encode("utf-8")
    request = Request(
        settings.LINEBOT_REPLY_ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=settings.LINEBOT_HTTP_TIMEOUT_SECONDS) as response:
            response.read()
            return {"ok": 200 <= response.status < 300, "status": response.status}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        logger.warning("LINE reply failed with HTTP %s: %s", exc.code, detail)
        return {"ok": False, "status": exc.code, "error": detail}
    except URLError as exc:
        logger.warning("LINE reply failed: %s", exc)
        return {"ok": False, "error": str(exc)}


def _candidate_patients(child_name):
    exact = Patient.objects.filter(name__iexact=child_name)
    if exact.exists():
        return exact
    return Patient.objects.filter(name__icontains=child_name)


def _contact_matches(patient, contact):
    contact_email = contact.strip().lower()
    if "@" in contact_email:
        return patient.guardian_email.strip().lower() == contact_email

    query_phone = _digits(contact)
    stored_phone = _digits(patient.guardian_phone)
    if not query_phone or not stored_phone:
        return False
    if query_phone == stored_phone:
        return True

    comparable_length = min(len(query_phone), len(stored_phone))
    return comparable_length >= 8 and query_phone[-comparable_length:] == stored_phone[-comparable_length:]


def _field_key(label):
    normalized = label.strip().lower().replace(" ", "")
    if normalized in {"姓名", "孩子姓名", "兒童姓名", "病患姓名", "患者姓名", "name", "childname"}:
        return "name"
    if normalized in {"手機", "電話", "家長手機", "家長電話", "聯絡電話", "email", "mail", "信箱", "電子信箱"}:
        return "contact"
    return ""


def _strip_query_prefix(text):
    cleaned = " ".join(text.strip().split())
    for prefix in QUERY_PREFIXES:
        if cleaned.startswith(prefix):
            return cleaned[len(prefix) :].strip(" ：:")
    return cleaned


def _looks_like_contact(value):
    if "@" in value:
        return True
    return len(_digits(value)) >= 6


def _digits(value):
    return re.sub(r"\D", "", value or "")


def _is_help_request(text):
    return text.strip().lower() in HELP_KEYWORDS


def _not_found_text(reason):
    if reason == "no_output":
        return (
            "已找到符合的孩子資料，但目前沒有可查閱的診後紀錄。\n"
            "可能是醫師尚未產生或尚未發布本次紀錄，請稍後再試或聯絡診所。"
        )
    return (
        "找不到可查閱的診後紀錄。\n"
        "請確認孩子姓名與家長手機/Email 與診所登記資料一致；為保護隱私，資料不吻合時不會顯示紀錄。"
    )


def _visit_reply_text(visit, base_url):
    output = visit.output
    created_at = timezone.localtime(visit.created_at).strftime("%Y-%m-%d %H:%M")
    portal_url = urljoin(base_url, f"portal/{visit.share_token}/")
    summary = _clip(output.visit_summary or output.parent_summary, 650)
    parent_education = _clip(output.parent_education or output.school_note, 900)
    follow_up = _clip(output.follow_up_plan, 280)
    warnings = _warning_signs_text(output.warning_signs)

    parts = [
        "OpenPediCare 最近一次診後紀錄",
        f"兒童：{visit.patient.name}（{visit.patient.age_years} 歲，{visit.patient.get_gender_display()}）",
        f"時間：{created_at}",
        f"看診類型：{visit.scenario_label}",
        f"診斷/主訴：{visit.diagnosis}",
        "",
        "看診摘要",
        summary,
        "",
        "家長照護重點",
        parent_education,
    ]
    if warnings:
        parts.extend(["", "需要留意", warnings])
    if follow_up:
        parts.extend(["", "追蹤計畫", follow_up])
    parts.extend(
        [
            "",
            "完整紀錄與 PDF",
            portal_url,
            "",
            "若孩子出現呼吸困難、精神明顯變差、持續惡化或醫師交代的警示徵兆，請立即就醫。",
        ]
    )
    return "\n".join(parts)


def _warning_signs_text(value):
    if not value:
        return ""
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value if item)
    return str(value)


def _public_base_url(request):
    configured = settings.LINEBOT_PUBLIC_BASE_URL.strip()
    if configured:
        return configured.rstrip("/") + "/"
    return request.build_absolute_uri("/")


def _text_messages(text):
    chunks = _split_for_line(text, settings.LINEBOT_MAX_REPLY_CHARS, LINE_REPLY_MESSAGE_LIMIT)
    return [{"type": "text", "text": chunk} for chunk in chunks]


def _split_for_line(text, preferred_limit, max_messages):
    limit = min(max(1, preferred_limit), LINE_TEXT_LIMIT)
    remaining = text.strip()
    chunks = []
    while remaining and len(chunks) < max_messages:
        chunk = remaining[:limit]
        if len(remaining) > limit:
            cut_at = max(chunk.rfind("\n"), chunk.rfind("。"), chunk.rfind("；"))
            if cut_at > int(limit * 0.55):
                chunk = chunk[: cut_at + 1]
        chunks.append(chunk.strip())
        remaining = remaining[len(chunk) :].strip()
    if remaining and chunks:
        suffix = "\n\n（內容較長，請開啟完整頁面查看。）"
        chunks[-1] = _clip(chunks[-1] + suffix, LINE_TEXT_LIMIT)
    return chunks or [""]


def _clip(text, max_chars):
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."
