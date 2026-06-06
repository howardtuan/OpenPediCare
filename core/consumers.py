import json
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from core.api import append_audio_chunk_from_base64
from core.models import Profile, TranscriptChunk, Visit


class TranscribeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query = parse_qs(self.scope.get("query_string", b"").decode())
        self.visit_id = (query.get("visit_id") or [""])[0]
        self.user = self.scope.get("user") or AnonymousUser()
        if not self.visit_id or not await self._can_access(self.visit_id):
            await self.close(code=4403)
            return
        await self.accept()
        await self.send_json({"type": "ready", "message": "轉寫通道已連線。"})

    async def receive(self, text_data=None, bytes_data=None):
        try:
            payload = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            await self.send_json({"type": "error", "message": "資料格式錯誤。"})
            return

        event_type = payload.get("type")
        if event_type == "audio":
            chunk = await self._save_audio(payload)
            await self.send_json(
                {
                    "type": "partial",
                    "message": "已收到音訊片段，若設定 STT provider，完成診次時可改用完整音檔轉寫。",
                    "chunk_id": chunk.id if chunk else None,
                }
            )
            return

        if event_type == "transcript":
            text = (payload.get("text") or "").strip()
            transcript = await self._append_text(text)
            await self.send_json({"type": "partial", "text": text, "transcript": transcript})
            return

        if event_type == "transcript_replace":
            text = (payload.get("text") or "").strip()
            transcript = await self._replace_text(text)
            await self.send_json({"type": "transcript_replace", "transcript": transcript})
            return

        await self.send_json({"type": "pong"})

    async def send_json(self, payload):
        await self.send(text_data=json.dumps(payload, ensure_ascii=False))

    @database_sync_to_async
    def _can_access(self, visit_id):
        if not self.user or not self.user.is_authenticated:
            return False
        profile, _ = Profile.objects.get_or_create(user=self.user)
        if profile.role != Profile.ROLE_DOCTOR:
            return False
        return Visit.objects.filter(id=visit_id, doctor=self.user).exists()

    @database_sync_to_async
    def _save_audio(self, payload):
        visit = Visit.objects.get(id=self.visit_id, doctor=self.user)
        return append_audio_chunk_from_base64(visit, payload)

    @database_sync_to_async
    def _append_text(self, text):
        visit = Visit.objects.get(id=self.visit_id, doctor=self.user)
        if text:
            visit.transcript = "\n".join(part for part in [visit.transcript, text] if part)
            visit.save(update_fields=["transcript", "updated_at"])
            TranscriptChunk.objects.create(
                visit=visit,
                sequence=visit.chunks.count() + 1,
                source=TranscriptChunk.SOURCE_MANUAL,
                text=text,
                expires_at=visit.audio_delete_after,
            )
        return visit.transcript

    @database_sync_to_async
    def _replace_text(self, text):
        visit = Visit.objects.get(id=self.visit_id, doctor=self.user)
        visit.transcript = text
        visit.save(update_fields=["transcript", "updated_at"])
        if text:
            TranscriptChunk.objects.create(
                visit=visit,
                sequence=visit.chunks.count() + 1,
                source=TranscriptChunk.SOURCE_MANUAL,
                text=text,
                expires_at=visit.audio_delete_after,
            )
        return visit.transcript
