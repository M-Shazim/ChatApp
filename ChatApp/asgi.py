"""
ASGI config for ChatApp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from a_rtchat.routing import wsPattern
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChatApp.settings')

http_response_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http" : http_response_app,
    "websocket" : AuthMiddlewareStack(
        URLRouter(wsPattern),
        )
})
