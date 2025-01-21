import json 
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatGroup, GroupMessage

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_name = "room_public_chat" 
        
        # self.group_name = f"room_{self.scope['url_route']['kwargs']['group_name']}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        await self.accept()
        
        
    async def disconnect(self, code):
        
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        
        self.close(code)