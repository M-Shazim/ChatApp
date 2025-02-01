from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from .consumers import ChatConsumer, GroupChatConsumer

# Define WebSocket URL patterns
wsPattern = [
    re_path(r'ws/chat/private/(?P<username1>\w+)/(?P<username2>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/group_chat/(?P<group_name>\w+)/$', GroupChatConsumer.as_asgi()),
]

# Apply AuthMiddlewareStack to WebSocket routes
application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(wsPattern)
    ),
})