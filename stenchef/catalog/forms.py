from django import forms


class ItemSearchForm(forms.Form):
    search_text = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "..."}),
    )