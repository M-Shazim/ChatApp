from django.urls import path
from authentication import views

urlpatterns = [
    path("",views.index,name="index_page"),
]