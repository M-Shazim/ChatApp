import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatGroup, GroupMessage, PrivateChat
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.db.models import Q
import html
from asgiref.sync import sync_to_async

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.contenttypes.models import ContentType
from .models import ChatGroup, GroupMessage

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatGroup, GroupMessage

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        # Capture the two users from the URL
        self.username1 = self.scope['url_route']['kwargs']['username1']
        self.username2 = self.scope['url_route']['kwargs']['username2']
        
        # Get the User objects for the two users
        user1 = await database_sync_to_async(User.objects.get)(username=self.username1)
        user2 = await database_sync_to_async(User.objects.get)(username=self.username2)

        # Look for an existing private chat or create one if it doesn't exist
        self.chat_room = await database_sync_to_async(self.get_or_create_private_chat)(user1, user2)

        # Calculate the room name manually
        self.room_name = f"private_{min(user1.id, user2.id)}_{max(user1.id, user2.id)}"
        
        # Add the current user to the WebSocket room
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()     
        
    async def disconnect(self, code):
        # Leave the WebSocket room
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        self.close(code)
        
    async def receive(self, text_data):
        # Receive the message from WebSocket
        data_json = json.loads(text_data)
        message = data_json['message']
        sender = data_json['sender']
        print("Received data: ", data_json)
        
        # Forward the received message to all connected users in the group
        event = {
            "type": "send_message",
            "message": data_json,
        }
        
        # Send the message to the group
        await self.channel_layer.group_send(self.room_name, event)
        
    async def send_message(self, event):
        # Extract message data
        data = event["message"]
        
        # Save the message in the database
        await self.create_message(data)
        
        # Respond with the message
        response = {
            "sender": data["sender"],
            "message": data["message"],
            "room_name": data["room_name"],
        }
        
        await self.send(text_data=json.dumps({
            "message": response
        }))
    
    @database_sync_to_async
    def create_message(self, data):
        if data["room_name"].startswith("Private Chat:"):
            # Decode HTML entities (e.g., &amp; -> &)
            decoded_room_name = html.unescape(data["room_name"])
            
            # Ensure room name format is correct
            room_name_parts = decoded_room_name.replace("Private Chat: ", "").split(" & ")
            if len(room_name_parts) != 2:
                raise ValueError("Invalid room name format. Expected 'Private Chat: username1 & username2'.")

            # Extract usernames
            user1_username, user2_username = room_name_parts[0], room_name_parts[1]

            # Retrieve user objects
            sender_user = User.objects.get(username=data["sender"])
            user1 = User.objects.get(username=user1_username)
            user2 = User.objects.get(username=user2_username)

            # Retrieve or create the private chat room
            private_chat = PrivateChat.objects.filter(
                Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
            ).first()
            if not private_chat:
                private_chat = PrivateChat.objects.create(user1=user1, user2=user2)

            # Save the message in GroupMessage
            GroupMessage.objects.create(
                content_type=ContentType.objects.get_for_model(PrivateChat),
                object_id=private_chat.id,
                author=sender_user,
                body=data["message"],
            )

    # @database_sync_to_async
    def get_or_create_private_chat(self, user1, user2):
        # Ensure consistent room name: always create a unique room name based on the users
        room_name = f"private_{min(user1.id, user2.id)}_{max(user1.id, user2.id)}"
        
        # Get or create the private chat between the two users
        chat, created = PrivateChat.objects.get_or_create(
            user1=user1,
            user2=user2,
        )
        chat.room_name = room_name
        
        return chat







logger = logging.getLogger(__name__)

class GroupChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """Handles WebSocket connection."""
        logger.debug(f"Scope: {self.scope}")

        # Retrieve user correctly
        self.user = self.scope["user"]  # No need for `await`
        if self.user.is_anonymous:
            logger.warning("Unauthenticated user attempted to connect.")
            await self.close()
            return

        self.group_name = self.scope['url_route']['kwargs']['group_name']
        logger.info(f"Connecting to group: {self.group_name}")

        # Fetch chat group
        self.chat_group = await self.get_chat_group(self.group_name)
        if not self.chat_group:
            logger.error(f"ChatGroup '{self.group_name}' does not exist.")
            await self.close()
            return

        self.room_name = f"group_{self.chat_group.group_name}"
        logger.info(f"Joining room: {self.room_name}")

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        logger.info("WebSocket connection accepted.")

        # Fetch latest messages safely
        try:
            chat_messages = await get_latest_group_messages(self.chat_group.pk)
            for message in chat_messages:
                await self.send(text_data=json.dumps({
                    'message': message.body,
                    'author': message.author.username,
                    'created': message.created.isoformat()
                }))
            logger.info(f"Sent {len(chat_messages)} messages to WebSocket.")
        except Exception as e:
            logger.error(f"Error fetching (from connect) messages: {e}")

    async def disconnect(self, close_code): 
        """Handles WebSocket disconnection."""
        logger.info(f"Disconnecting from room: {self.room_name}")
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        """Handles incoming messages."""
        logger.info(f"Received message: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')

            if self.user.is_anonymous:
                logger.warning("Unauthenticated user attempted to send a message.")
                return

            # Save message asynchronously
            await self.save_group_message(message, self.user)

            # Broadcast message
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'author': self.user.username
                }
            )
            logger.info(f"Message broadcasted in room: {self.room_name}")

        except Exception as e:
            logger.error(f"Error processing received message: {e}")

    async def chat_message(self, event):
        """Sends received message to WebSocket."""
        logger.info(f"Sending message to WebSocket: {event}")
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'author': event['author']
        }))

    ## 🔹 ASYNC ORM QUERIES WRAPPED CORRECTLY ##

    @database_sync_to_async
    def get_chat_group(self, group_name):
        """Fetch the ChatGroup object from the database."""
        try:
            return ChatGroup.objects.get(group_name=group_name)
        except ChatGroup.DoesNotExist:
            return None

    @database_sync_to_async
    def save_group_message(self, message_body, user):
        # Re-fetch the chat group so that it is bound to the sync DB connection:
        chat_group = ChatGroup.objects.get(pk=self.chat_group.pk)
        return GroupMessage.objects.create(
            chat=chat_group,
            author=user,
            body=message_body
        )

@database_sync_to_async
def get_latest_group_messages(chat_group_id):
    # Re-fetch the chat group in the sync context
    chat_group = ChatGroup.objects.get(pk=chat_group_id)
    logger.info(f"Fetching latest messages for group: {chat_group.group_name}")
    return list(chat_group.messages.all().select_related('author').order_by('-created')[:30])