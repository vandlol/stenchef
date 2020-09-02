from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import CreateView
from .forms import ContainerForm, ContainerTypeForm
from .models import Container, Containertype


class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, "warehouse/container.html", context=None)


# Add this view
class AboutPageView(TemplateView):
    template_name = "warehouse/about.html"


class ContainerCreateView(CreateView):
    model = Container
    form_class = ContainerForm
    success_url = "/w"
    template_name = "warehouse/container_create.html"


class ContainerTypeCreateView(CreateView):
    model = Containertype
    form_class = ContainerTypeForm
    success_url = "/w"
    template_name = "warehouse/container_create.html"
