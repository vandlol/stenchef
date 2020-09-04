from django import forms
from .models import Container, Containertype, StoredItem


class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = [
            "name",
            "containertype",
            "parent",
            "description",
        ]


class ContainerTypeForm(forms.ModelForm):
    class Meta:
        model = Containertype
        fields = "__all__"
        widgets = {"name": forms.TextInput(attrs={"class": "text-red-500"})}


class StoreItemForm(forms.ModelForm):
    class Meta:
        model = StoredItem
        exclude = ["storeid", "owner"]
