from django.shortcuts import render
from django.views.generic import CreateView, ListView, TemplateView
from .forms import ContainerForm, ContainerTypeForm
from .models import Container, Containertype
from django.contrib.auth.mixins import LoginRequiredMixin
from pprint import pprint as pp
from django_currentuser.middleware import get_current_authenticated_user


class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, "warehouse/container.html", context=None)


# Add this view
class AboutPageView(TemplateView):
    template_name = "warehouse/about.html"


class ContainerCreateView(LoginRequiredMixin, CreateView):
    model = Container
    form_class = ContainerForm
    success_url = "/w"
    template_name = "warehouse/container_create.html"


class ContainerListView(LoginRequiredMixin, ListView):
    model = Container
    form_class = ContainerForm
    context_object_name = "containers"
    template_name = "warehouse/container_list.html"

    def get_queryset(self):
        containers = Container.objects.filter(
            owner=get_current_authenticated_user().id
        ).all()

        return containers


class ContainerTypeCreateView(LoginRequiredMixin, CreateView):
    model = Containertype
    form_class = ContainerTypeForm
    success_url = "/w"
    template_name = "warehouse/container_type_create.html"
