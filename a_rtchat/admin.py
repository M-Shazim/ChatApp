from django.contrib import admin
from .models import User, GroupMessage, ChatGroup, PrivateChat
# Register your models here.


admin.site.register(ChatGroup)
admin.site.register(GroupMessage)
admin.site.register(PrivateChat)

