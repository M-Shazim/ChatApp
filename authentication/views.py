from django.shortcuts import render, redirect

# Create your views here.

def index(request):
    ilfaaz = "Hello world"
    return render(request ,"authentication/index.html", {
        "meow" : ilfaaz,
    })