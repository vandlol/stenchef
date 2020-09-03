from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "catalog"
urlpatterns = [
    path("c/", views.home, name="catalog-home"),
]
