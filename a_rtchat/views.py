from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

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
        
        firstName_fetched = request.POST["firstName"]
        lastName_fetched = request.POST["lastName"]
        
        new_user = User.objects.create_user(username=username_fetched, email=email_fetched, password=pass1_fetched)
        new_user.first_name = firstName_fetched
        new_user.last_name = lastName_fetched
        new_user.is_active = False
        new_user.save()
        
        return redirect("signin")

    return render(request, "a_rtchat/signup.html")


    
@login_required
def home(request):
    chat_group = get_object_or_404(ChatGroup, group_name="public_chat")
    chat_messages = chat_group.chat_messages.all()[:30]
    ilfaaz = "Hello world"
    return render(request ,"a_rtchat/home.html", {
        "meow" : ilfaaz,
        'chat_messages' : chat_messages,
    })