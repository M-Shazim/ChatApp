from django.urls import path
from a_rtchat import views

urlpatterns = [
    path("",views.index,name="index"),
    path("signin",views.signin,name="signin"),
    path("signup",views.signup,name="signup"),
    path("signout",views.signout,name="signout"),
    path("home",views.home,name="home"),
    path("all_groups/",views.all_groups,name="all_groups"),
    path("group_chat/<str:group>/",views.group_chat,name="group_chat"),
    path('chat/private/<str:username1>/<str:username2>/', views.private_chat, name='private_chat'),
]