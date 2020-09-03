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
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['name'].widget.attrs.update({'class': 'text-red-500'})


#class RawcontainerForm(forms.Form):
#    name = forms.CharField()
#    dimx = forms.NumberInput()
#    dimy = forms.NumberInput()
#    dimz = forms.NumberInput()
#    empty_weight = forms.NumberInput()
#    description = forms.Textarea()
