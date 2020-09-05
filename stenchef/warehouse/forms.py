from django import forms
from .models import Container, Containertype, StoredItem
from catalog.models import Item
from dal import autocomplete


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
        fields = "__all__"
        widgets = {
            "itemid": autocomplete.ModelSelect2(
                url="warehouse:iauto",
                attrs={
                    # Set some placeholder
                    "data-placeholder": "Autocomplete ...",
                    # Only trigger autocompletion after 3 characters have been typed
                    "data-minimum-input-length": 2,
                },
            )
        }

