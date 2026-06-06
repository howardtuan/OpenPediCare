import base64
import logging
import urllib.request

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone


logger = logging.getLogger(__name__)


def comic_style_for_age(age_years):
    if age_years <= 5:
        return (
            "Create a child-safe 2x2 four-panel comic for ages 3-5. Use warm pink accents, soft rounded shapes, "
            "very short visual cues, minimal readable text, expressive caregivers, and concrete actions like rest, "
            "water, medicine only from an adult, and telling a grown-up when feeling worse."
        )
    if age_years <= 11:
        return (
            "Create a 2x2 four-panel comic for ages 6-11. Use a story-driven science metaphor, clear cause-and-care "
            "sequence, friendly clinic context, simple labels, and a slightly more detailed but still playful style."
        )
    return (
        "Create a 2x2 four-panel comic for ages 12-17. Use a clean, semi-clinical teen health style, respectful tone, "
        "self-management cues, concise medical icons, and a more professional layout while remaining approachable."
    )


def build_comic_prompt(output):
    visit = output.visit
    summary = output.visit_summary or output.parent_summary
    parent_education = output.parent_education or output.school_note
    patient_education = output.patient_education or output.child_explanation
    warnings = "、".join(output.warning_signs or [])
    return f"""
{comic_style_for_age(visit.patient.age_years)}

Brand context: OpenPediCare, pediatric post-visit education. Use a gentle pink primary color palette.
Format: one square image, exactly four panels in a 2x2 grid, clear panel borders, no real names, no hospital logos, no contact details.
Safety: do not show frightening procedures, blood, injections close-up, or medication doses. Avoid exact small text that may render incorrectly.

Patient age: {visit.patient.age_years}
Visit summary: {summary}
Parent education: {parent_education}
Patient-facing education: {patient_education}
Warning signs to imply visually: {warnings}
""".strip()


def _image_bytes_from_response(response):
    item = response.data[0]
    b64_json = getattr(item, "b64_json", None)
    if b64_json:
        return base64.b64decode(b64_json)
    url = getattr(item, "url", None)
    if not url:
        raise ValueError("OpenAI image response did not include b64_json or url.")
    with urllib.request.urlopen(url, timeout=90) as handle:
        return handle.read()


def generate_comic_for_output(output):
    if not settings.OPENAI_IMAGE_API_KEY:
        raise ValueError("OPENAI_IMAGE_API_KEY is not configured.")

    from openai import OpenAI

    prompt = build_comic_prompt(output)
    client = OpenAI(api_key=settings.OPENAI_IMAGE_API_KEY, base_url=settings.OPENAI_IMAGE_BASE_URL)
    try:
        response = client.images.generate(
            model=settings.OPENAI_IMAGE_MODEL,
            prompt=prompt,
            size="1024x1024",
            quality="low",
            n=1,
        )
    except TypeError:
        response = client.images.generate(
            model=settings.OPENAI_IMAGE_MODEL,
            prompt=prompt,
            size="1024x1024",
            n=1,
        )

    image_bytes = _image_bytes_from_response(response)
    filename = f"visit-{output.visit_id}-comic.png"
    output.comic_image.save(filename, ContentFile(image_bytes), save=False)
    output.comic_prompt = prompt
    output.comic_generated_at = timezone.now()
    output.save(update_fields=["comic_image", "comic_prompt", "comic_generated_at"])
    logger.info("Generated comic for visit %s", output.visit_id)
    return output
