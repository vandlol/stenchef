from django import forms
from .models import Container, Containertype, BLInventoryItem
from catalog.models import Item
from dal import autocomplete
from pprint import pprint as pp


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
        model = BLInventoryItem
        exclude = ["inventory_id"]
        widgets = {
            "item_id": autocomplete.ModelSelect2(
                url="catalog:iauto",
            ),
            "container": autocomplete.ModelSelect2(
                url="warehouse:cauto",
            ),
        }


class StoreItemContainerForm(forms.ModelForm):
    class Meta:
        model = BLInventoryItem
        fields = ["container"]
        widgets = {
            "container": autocomplete.ModelSelect2(
                url="warehouse:cauto",
            ),
        }