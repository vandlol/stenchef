from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    TemplateView,
    DeleteView,
    UpdateView,
)
from .forms import ContainerForm, ContainerTypeForm, StoreItemForm
from .models import Container, Containertype, StoredItem
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from pprint import pprint as pp
from django_currentuser.middleware import get_current_authenticated_user


class HomePageView(TemplateView):
    def query_data(self):
        _query = {"containers": Container.objects.all()}  # pylint: disable=no-member
        print(_query)
        return _query

    def get(self, request, **kwargs):
        return render(request, "warehouse/container.html", context=self.query_data())


class AboutPageView(TemplateView):
    template_name = "warehouse/about.html"


class ContainerCreateView(LoginRequiredMixin, CreateView):
    model = Container
    form_class = ContainerForm
    success_url = "/w"
    template_name = "warehouse/form_create.html"
    title = "Container"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ContainerListView(LoginRequiredMixin, ListView):
    model = Container
    form_class = ContainerForm
    context_object_name = "containers"
    template_name = "warehouse/container_list.html"

    def get_queryset(self):
        containers = Container.objects.filter(  # pylint: disable=no-member
            owner=get_current_authenticated_user().id
        ).all()

        return containers


class ContainerDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Container
    success_url = "/"
    template_name = "warehouse/confirm_delete.html"
    title = "Container"

    def test_func(self):
        container = self.get_object()
        if self.request.user == container.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ContainerUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Container
    fields = ["name", "containertype"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        container = self.get_object()
        if self.request.user == container.owner:
            return True
        return False


class ContainerDetailView(LoginRequiredMixin, CreateView):
    model = Container
    form_class = ContainerForm
    success_url = "/w"
    template_name = "warehouse/container_type_create.html"


class ContainerTypeCreateView(LoginRequiredMixin, CreateView):
    model = Containertype
    form_class = ContainerTypeForm
    success_url = "/w"
    template_name = "warehouse/form_create.html"
    title = "Containertype"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ContainerTypeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Containertype
    success_url = "/"
    template_name = "warehouse/confirm_delete.html"

    def test_func(self):
        containertype = self.get_object()
        if self.request.user == containertype.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ContainerTypeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Containertype
    fields = ["name", "containertype"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        containertype = self.get_object()
        if self.request.user == containertype.owner:
            return True
        return False


class ContainerTypeListView(LoginRequiredMixin, ListView):
    model = Containertype
    form_class = ContainerTypeForm
    context_object_name = "containers"
    template_name = "warehouse/container_list.html"

    def get_queryset(self):
        containertypes = Containertype.objects.filter(  # pylint: disable=no-member
            owner=get_current_authenticated_user().id
        ).all()

        return containertypes


class StoreItemView(LoginRequiredMixin, CreateView):
    model = StoredItem
    form_class = StoreItemForm
    success_url = "/w"
    template_name = "warehouse/container_type_create.html"


class StoredItemDetailView(LoginRequiredMixin, CreateView):
    model = StoredItem
    form_class = StoreItemForm
    success_url = "/w"
    template_name = "warehouse/container_type_create.html"
