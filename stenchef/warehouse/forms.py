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
        widgets = {
            "parent": autocomplete.ModelSelect2(
                url="warehouse:cauto",
            ),
        }


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


class StoreItemUpdateContainerForm(forms.ModelForm):
    class Meta:
        model = BLInventoryItem
        fields = ["container"]
        widgets = {
            "container": autocomplete.ModelSelect2(url="warehouse:cauto"),
        }
        labels = {"container": ""}


class StoreItemUpdateQuantityForm(forms.ModelForm):
    class Meta:
        model = BLInventoryItem
        fields = ["count"]


class SearchBarForm(forms.ModelForm):
    class Meta:
        model = BLInventoryItem
        fields = ["item_id"]
        widgets = {
            "item_id": autocomplete.ModelSelect2(url="warehouse:iauto"),
        }


# StoreItemUpdateFormSet = forms.modelformset_factory(BLInventoryItem, form=StoreItemUpdateForm)
