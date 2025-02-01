from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

# Create your models here.

class PrivateChat(models.Model):
    user1 = models.ForeignKey(User, related_name="private_chats_as_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="private_chats_as_user2", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    messages = GenericRelation('GroupMessage')

    @property
    def chat_room_name(self):
        return f"private_{min(self.user1.id, self.user2.id)}_{max(self.user1.id, self.user2.id)}"
    
    def __str__(self):
        return f"Private Chat: {self.user1.username} & {self.user2.username}"

class GroupMessage(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    chat = GenericForeignKey('content_type', 'object_id')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.author.username} : {self.body}'
    
    class Meta:
        ordering = ['-created']
        
class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True)
    # Add GenericRelation to reverse query messages
    messages = GenericRelation('GroupMessage')
    
    def __str__(self):
        return self.group_name