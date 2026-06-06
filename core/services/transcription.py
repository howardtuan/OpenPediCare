import logging
from tempfile import NamedTemporaryFile

from django.conf import settings

logger = logging.getLogger(__name__)


def transcribe_audio(uploaded_file):
    """Transcribe a complete audio file when an STT provider is configured."""
    if not settings.OPENAI_API_KEY:
        return ""

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        suffix = "." + (uploaded_file.name.split(".")[-1] if "." in uploaded_file.name else "webm")
        with NamedTemporaryFile(suffix=suffix) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp.flush()
            with open(tmp.name, "rb") as audio:
                result = client.audio.transcriptions.create(
                    model=settings.OPENAI_TRANSCRIBE_MODEL,
                    file=audio,
                    language="zh",
                )
        return getattr(result, "text", "") or ""
    except Exception:
        logger.exception("OpenAI transcription failed.")
        return ""
