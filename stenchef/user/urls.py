from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views as user_views


app_name = "user"

urlpatterns = [
    path("user/", lambda request: redirect("u/", permanent=True)),
    path(
        "u/",
        include(
            [
                path("", user_views.home, name="user-home"),
                path("register", user_views.register, name="register"),
                path(
                    "login",
                    auth_views.LoginView.as_view(template_name="user/login.html"),
                    name="login",
                ),
                path(
                    "logout",
                    auth_views.LogoutView.as_view(template_name="user/logout.html"),
                    name="logout",
                ),
            ]
        ),
    ),
]

