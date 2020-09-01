from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "catalog"
urlpatterns = [
    path("catalog/", lambda request: redirect("c/", permanent=True)),
    path("c/", views.home, name="catalog-home"),
]
