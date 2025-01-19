from django.forms import ModelForm
from django import forms
from .models import *

class ChatMessagesCreateForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        