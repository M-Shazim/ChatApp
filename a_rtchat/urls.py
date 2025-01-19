from django.urls import path
from a_rtchat import views

urlpatterns = [
    path("",views.index,name="index"),
    path("signin",views.signin,name="signin"),
    path("signup",views.signup,name="signup"),
    path("signout",views.signout,name="signout"),
    path("home",views.home,name="home"),
    
]