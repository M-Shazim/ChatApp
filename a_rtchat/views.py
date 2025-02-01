from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import *
from django.db.models import Q

# Create your views here.

def index(request):
    return render(request, "a_rtchat/index.html")

def signin(request):
    if request.method == "POST":
        username_fetched = request.POST["username"]
        pass1_fetched = request.POST["pass1"]

        logging_user = authenticate(username=username_fetched, password=pass1_fetched)

        if logging_user is not None:
            login(request, logging_user) 
                                    
            return redirect("home")  
        else:
            return render(request, "a_rtchat/signin.html", {"error": "Invalid credentials"})
        
    return render(request, "a_rtchat/signin.html")

def signout(request):
    logout(request)
    # messages.success(request, "Logged out successfully! ")
    return redirect("index")

def signup(request):
    if request.method == 'POST':
        username_fetched = request.POST["username"]
        email_fetched = request.POST["email"]
        pass1_fetched = request.POST["pass1"]
        
        new_user = User.objects.create_user(username=username_fetched, email=email_fetched, password=pass1_fetched)
        # new_user.is_active = False
        new_user.save()
        
        return redirect("signin")

    return render(request, "a_rtchat/signup.html")

@login_required
def all_groups(request):
    groups = ChatGroup.objects.all()

    return render(request, "a_rtchat/all_groups.html", {
        "all_groups" : groups
    })
        
@login_required
def group_chat(request, group):
    # Get the ChatGroup instance by its name
    chat_group = get_object_or_404(ChatGroup, group_name=group)
    chat_messages = chat_group.messages.all().order_by('-created')[:30]

    form = ChatMessagesCreateForm()

    if request.method == "POST":
        form = ChatMessagesCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            # Link the message to the current ChatGroup using GenericForeignKey
            message.content_type = ContentType.objects.get_for_model(ChatGroup)
            message.object_id = chat_group.id
            message.save()
            return redirect('group_chat', group=chat_group.group_name)

    return render(request, "a_rtchat/group_chat.html", {
        'chat_messages': chat_messages,
        'group_name': chat_group.group_name,
        'username': request.user.username,
        'form': form,
    })
    
@login_required
def home(request):
    
    users = User.objects.all() 
    
    return render(request, "a_rtchat/home.html", {
        "all_users" : users
    })
    
@login_required
def private_chat(request, username1, username2):
    # Ensure the usernames are sorted, so the order doesn't matter for the chat room
    user1 = get_object_or_404(User, username=username1)
    user2 = get_object_or_404(User, username=username2)

    # Check if this is the logged-in user and switch the order if necessary
    if user1 == request.user:
        other_user = user2
    else:
        other_user = user1

    # Look for an existing private chat or create a new one
    chat = PrivateChat.objects.filter(
        Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
    ).first()

    if not chat:
        chat = PrivateChat.objects.create(user1=user1, user2=user2)

    messages = GroupMessage.objects.filter(
        content_type=ContentType.objects.get_for_model(PrivateChat),
        object_id=chat.id
    ).order_by('-created')

    form = ChatMessagesCreateForm()

    if request.method == "POST":
        form = ChatMessagesCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.content_type = ContentType.objects.get_for_model(PrivateChat)
            message.object_id = chat.id
            message.save()
            return redirect('private_chat', username1=user1.username, username2=user2.username)

    return render(request, "a_rtchat/private_chat.html", {
        'chat': chat,
        'messages': messages,
        'other_user': other_user,
        'form': form,
    })
