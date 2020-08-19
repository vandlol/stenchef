from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='user-home'),
    path('register', views.register, name='user-register')
]
