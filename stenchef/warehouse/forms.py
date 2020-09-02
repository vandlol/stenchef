from django import forms
from easy_select2 import select2_modelform_meta
from .models import Container, Containertype


class ContainerForm(forms.ModelForm):
    Meta = select2_modelform_meta(Container)


class ContainerTypeForm(forms.ModelForm):
    Meta = select2_modelform_meta(Containertype)
