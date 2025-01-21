from django.urls import path
from .consumers import ChatConsumer

wsPattern = [
    path("ws/messages/public_chat/", ChatConsumer.as_asgi())
]