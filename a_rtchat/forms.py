from django.forms import ModelForm
from django import forms
from .models import *

class ChatMessagesCreateForm(ModelForm):
        
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'id': 'chat-body',
                'class': 'form-control',
                'placeholder': 'Type your message here...',
                'rows': 3,
            }),
        }