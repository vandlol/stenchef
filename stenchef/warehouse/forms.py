from django import forms
from .models import Container, Containertype


class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = [
            "name",
            "containertype",
            "dimx",
            "dimy",
            "dimz",
            "containeremptyweight",
            "parent",
            "description",
        ]


class ContainerTypeForm(forms.ModelForm):
    class Meta:
        model = Containertype
        fields = "__all__"

