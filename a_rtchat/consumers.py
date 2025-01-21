import json 
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatGroup, GroupMessage
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.group_name = "room_public_chat" 
        # self.group_name = f"room_{self.scope['url_route']['kwargs']['group_name']}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
        
    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        self.close(code)
        
    
    async def receive(self, text_data):
        data_json = json.loads(text_data)
        print(data_json)
        
        event = {
            "type" : "send_message",
            "message" : data_json,
        }
        
        await self.channel_layer.group_send(self.group_name, event)
        
    async def send_message(self, event):
        data = event["message"]
        
        await self.create_message(data = data)
        print("sender here is: ")
        print(data["sender"])
        response = {
            "sender" : data["sender"],
            "message" : data["message"],
            "room_name": data["room_name"],
            
        }
        
        await self.send(text_data=json.dumps({
            "message":response
            }))
        
    
    @database_sync_to_async
    def create_message(self, data):
        get_room = ChatGroup.objects.get(group_name = data["room_name"])
        sender_user = User.objects.get(username=data["sender"])
        
        if not GroupMessage.objects.filter(body = data["message"], author = sender_user).exists():
            new_message = GroupMessage.objects.create(
                                                        group = get_room,
                                                        body = data["message"],
                                                        author = sender_user
                                                    )
            