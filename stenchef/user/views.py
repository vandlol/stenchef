from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm

# from .models import Item


def home(request):
    pass


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, "Account created for {}!".format(username))
            return redirect("warehouse:home")
    else:
        form = UserRegisterForm()
    return render(request, "user/register.html", {"form": form})
