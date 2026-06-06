from django.urls import re_path

from .consumers import TranscribeConsumer


websocket_urlpatterns = [
    re_path(r"^api/visit/transcribe/$", TranscribeConsumer.as_asgi()),
]
