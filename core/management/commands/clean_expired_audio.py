from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import TranscriptChunk


class Command(BaseCommand):
    help = "Delete audio chunks after the configured 72-hour retention window."

    def handle(self, *args, **options):
        expired = TranscriptChunk.objects.filter(expires_at__lte=timezone.now())
        deleted_files = 0
        for chunk in expired:
            if chunk.audio_file:
                chunk.audio_file.delete(save=False)
                deleted_files += 1
        count, _ = expired.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} chunks and {deleted_files} audio files."))
