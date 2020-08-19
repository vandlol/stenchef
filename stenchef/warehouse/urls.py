from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='warehouse-home'),
    path('about/', views.about, name='warehouse-about'),
]
