import json
import logging
import re

from django.conf import settings
from django.utils import timezone

from core.models import Visit, VisitOutput

from .prompts import PROMPT_VERSION, build_generation_prompt, child_tone

logger = logging.getLogger(__name__)


KEYWORD_WARNING_SIGNS = {
    "fever": ["精神活動力明顯下降", "呼吸急促或困難", "持續高燒超過三天", "尿量明顯減少或脫水"],
    "cough": ["呼吸急促或胸凹", "嘴唇發紫", "喘鳴快速惡化", "高燒合併精神差"],
    "ear": ["耳後紅腫疼痛", "耳朵流膿", "高燒不退", "聽力明顯下降"],
    "vaccine": ["全身蕁麻疹或呼吸困難", "持續高燒", "抽搐", "精神活動力明顯下降"],
    "general": ["精神活動力明顯下降", "呼吸困難", "持續高燒或症狀惡化", "無法進食喝水或尿量減少"],
}


def _infer_topic(visit):
    text = f"{visit.transcript} {visit.doctor_notes}".lower()
    if any(word in text for word in ["發燒", "高燒", "退燒", "fever"]):
        return "fever"
    if any(word in text for word in ["咳", "喘", "氣喘", "呼吸", "inhaler", "asthma"]):
        return "cough"
    if any(word in text for word in ["耳", "中耳炎", "ear"]):
        return "ear"
    if any(word in text for word in ["疫苗", "接種", "vaccine"]):
        return "vaccine"
    return "general"


def _display_gender(visit):
    return visit.patient.get_gender_display() if visit.patient.gender else "未填"


def _mock_patient_education(visit):
    name = visit.patient.name
    age = visit.patient.age_years
    if age <= 5:
        return f"{name}，你的身體正在努力保護你。今天要多喝水、好好休息，不舒服就告訴大人。"
    if age <= 11:
        return (
            f"{name}，你可以把身體想成一座城堡。今天城堡裡的守衛正在處理讓你不舒服的事情。"
            "你的任務是喝水、休息，覺得更不舒服時要馬上告訴爸媽或老師。"
        )
    return (
        f"{name}，這次看診後請先把重點放在休息、補水與觀察症狀變化。"
        "請依醫師說明用藥或照護，不要勉強運動；如果呼吸、精神、疼痛或發燒明顯惡化，請主動告知家長並就醫。"
    )


def mock_generate(visit):
    topic = _infer_topic(visit)
    warnings = KEYWORD_WARNING_SIGNS[topic]
    transcript = visit.transcript or "本次沒有取得逐字稿。"
    notes = visit.doctor_notes or "醫師未補充額外備註。"
    child_style = child_tone(visit.patient.age_years).split("：", 1)[0]

    visit_summary = (
        f"患者 {visit.patient.name}（{visit.patient.age_years} 歲，{_display_gender(visit)}）完成一次兒科看診錄音分析。"
        f"逐字稿重點：{transcript}\n\n"
        f"醫師補充：{notes}\n\n"
        "AI 已依逐字稿整理看診脈絡、照護重點與需追蹤事項；此摘要供醫師審核，不取代臨床判斷。"
    )
    parent_education = (
        f"{visit.patient.name} 今天看診後，請家長先依醫師說明照護，並觀察孩子的精神、食慾、睡眠、體溫與呼吸狀況。\n\n"
        "居家照護重點：多補充水分、讓孩子休息、依藥袋或醫師說明使用藥物，不自行加減劑量。"
        f"如果出現以下狀況，請聯絡醫療院所或就醫：{'、'.join(warnings)}。\n\n"
        "若症狀穩定，請依醫師安排追蹤；若症狀快速變化，請提前回診。"
    )
    return {
        "visit_summary": visit_summary,
        "parent_education": parent_education,
        "patient_education": f"（{child_style}）{_mock_patient_education(visit)}",
        "warning_signs": warnings,
        "follow_up_plan": "依醫師安排回診或追蹤；若警示徵兆出現，請立即就醫。",
    }


def _json_from_text(text):
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1).strip()
    return json.loads(text)


def _provider_config():
    if settings.AI_PROVIDER == "openai":
        return {
            "provider": "openai",
            "api_key": settings.OPENAI_API_KEY,
            "base_url": settings.OPENAI_BASE_URL,
            "model": settings.OPENAI_CHAT_MODEL,
        }
    return {
        "provider": "ikuncode",
        "api_key": settings.IKUNCODE_API_KEY,
        "base_url": settings.IKUNCODE_BASE_URL,
        "model": settings.IKUNCODE_MODEL,
    }


def openai_compatible_generate(visit):
    from openai import OpenAI

    config = _provider_config()
    if not config["api_key"]:
        raise ValueError(f"{config['provider']} API key is not configured.")

    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
    response = client.chat.completions.create(
        model=config["model"],
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "你是嚴謹、溫和的兒科診後衛教助理，只輸出 JSON。",
            },
            {"role": "user", "content": build_generation_prompt(visit)},
        ],
    )
    content = response.choices[0].message.content or "{}"
    return _json_from_text(content), config


def generate_visit_output(visit):
    provider = settings.AI_PROVIDER
    model = ""
    try:
        payload, config = openai_compatible_generate(visit)
        provider = config["provider"]
        model = config["model"]
    except ValueError as exc:
        logger.warning("%s Falling back to local mock output.", exc)
        payload = mock_generate(visit)
        provider = f"{provider}-mock-fallback"
    except Exception:
        logger.exception("AI generation failed; falling back to local mock output.")
        payload = mock_generate(visit)
        provider = f"{provider}-mock-fallback"

    visit_summary = payload.get("visit_summary", "")
    parent_education = payload.get("parent_education", "")
    patient_education = payload.get("patient_education", "")

    output, _ = VisitOutput.objects.update_or_create(
        visit=visit,
        defaults={
            "visit_summary": visit_summary,
            "parent_education": parent_education,
            "patient_education": patient_education,
            "parent_summary": visit_summary,
            "child_explanation": patient_education,
            "school_note": parent_education,
            "warning_signs": payload.get("warning_signs", []),
            "follow_up_plan": payload.get("follow_up_plan", ""),
            "ai_provider": provider,
            "ai_model": model,
            "prompt_version": PROMPT_VERSION,
            "generated_at": timezone.now(),
            "approved_at": None,
        },
    )
    visit.status = Visit.STATUS_REVIEW
    visit.completed_at = timezone.now()
    visit.save(update_fields=["status", "completed_at", "updated_at"])
    return output


def output_to_dict(output):
    visit = output.visit
    visit_summary = output.visit_summary or output.parent_summary
    parent_education = output.parent_education or output.school_note
    patient_education = output.patient_education or output.child_explanation
    return {
        "visit_id": visit.id,
        "status": visit.status,
        "patient": {
            "id": visit.patient.id,
            "name": visit.patient.name,
            "age_years": visit.patient.age_years,
            "gender": visit.patient.gender,
            "gender_label": visit.patient.get_gender_display(),
            "age_band": visit.child_age_band,
        },
        "visit_summary": visit_summary,
        "parent_education": parent_education,
        "patient_education": patient_education,
        "parent_summary": visit_summary,
        "child_explanation": patient_education,
        "school_note": parent_education,
        "warning_signs": output.warning_signs,
        "follow_up_plan": output.follow_up_plan,
        "ai_provider": output.ai_provider,
        "ai_model": output.ai_model,
        "comic_generation_enabled": settings.COMIC_GENERATION_ENABLED,
        "comic_image_url": output.comic_image.url if output.comic_image else "",
        "comic_generated_at": output.comic_generated_at.isoformat() if output.comic_generated_at else None,
        "generated_at": output.generated_at.isoformat(),
        "approved_at": output.approved_at.isoformat() if output.approved_at else None,
        "share_url": f"/portal/{visit.share_token}/",
    }
