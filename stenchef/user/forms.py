from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.utils.translation import ugettext_lazy as _


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white rounded border border-gray-400 focus:outline-none focus:border-teal-500 text-base px-4 py-2 mb-4",
                "placeholder": "E-Mail",
                "id": "email",
            }
        )
    )
    # username = forms.CharField(
    #    widget=forms.TextInput(
    #        attrs={
    #            "class": "bg-white rounded border border-gray-400 focus:outline-none #focus:border-teal-500 text-base px-4 py-2 mb-4",
    #            "placeholder": "Login",
    #            "id": "username",
    #            "label": "penis",
    #        },
    #    )
    # )
    username = forms.RegexField(
        label=_("Login"),
        max_length=30,
        regex=r"^[\w.@+-]+$",
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and " "@/./+/-/_ only."
        ),
        error_messages={
            "invalid": _(
                "This value may contain only letters, numbers and "
                "@/./+/-/_ characters."
            )
        },
        widget=forms.TextInput(
            attrs={
                "class": "bg-white rounded border border-gray-400 focus:outline-none #focus:border-teal-500 text-base px-4 py-2 mb-4",
                "required": "true",
                "placeholder": "Login",
            }
        ),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "bg-white rounded border border-gray-400 focus:outline-none focus:border-teal-500 text-base px-4 py-2 mb-4",
                "placeholder": "Password",
                "id": "password1",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "bg-white rounded border border-gray-400 focus:outline-none focus:border-teal-500 text-base px-4 py-2 mb-4",
                "placeholder": "Confirm Password",
                "id": "password2",
            }
        )
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "bg-white rounded border border-gray-400 focus:outline-none focus:border-teal-500 text-base px-4 py-2 mb-4",
                "placeholder": "Login",
                "id": "username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "bg-white rounded border border-gray-400 focus:outline-none focus:border-teal-500 text-base px-4 py-2 mb-4",
                "placeholder": "Password",
                "id": "password",
            }
        )
    )

