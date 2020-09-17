from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    TemplateView,
    DeleteView,
    UpdateView,
    DetailView,
)
from .forms import ContainerForm, ContainerTypeForm, StoreItemForm
from .models import Container, Containertype, BLInventoryItem
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from pprint import pprint as pp
from django_currentuser.middleware import get_current_authenticated_user
from catalog.models import Item


class HomePageView(TemplateView):
    def query_data(self):
        _query = {"containers": Container.objects.all()}  # pylint: disable=no-member
        return _query

    def get(self, request, **kwargs):
        return render(request, "warehouse/container.html", context=self.query_data())


class ContainerCreateView(LoginRequiredMixin, CreateView):
    model = Container
    form_class = ContainerForm
    success_url = "/w"
    template_name = "warehouse/form_create.html"
    title = "Container"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        if self.kwargs:
            if self.kwargs.get("parent"):
                context["form"] = ContainerForm(
                    initial={"parent": self.kwargs["parent"]}
                )

        return context


class ContainerListView(LoginRequiredMixin, ListView):
    model = Container
    context_object_name = "containers"
    template_name = "warehouse/container_list.html"
    paginate_by = 50
    ordering = ["name"]

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
    fields = ["name", "containertype", "parent", "description"]
    template_name = "warehouse/form_edit.html"
    title = "Container"
    success_url = "/"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        container = self.get_object()
        if self.request.user == container.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ContainerDetailView(LoginRequiredMixin, DetailView):
    model = Container
    success_url = "/w"
    template_name = "warehouse/container_detail.html"

    def test_func(self):
        container = self.get_object()
        if self.request.user == container.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["container"] = self.get_object()
        context["items"] = BLInventoryItem.objects.filter(  # pylint: disable=no-member
            container__pk=context["container"].containerid
        )
        context["children"] = context["container"].children.all()
        parents = list()
        if hasattr(context["container"], "parent"):
            cparent = context["container"].parent
            parents.insert(0, context["container"].parent.name)
            while True:
                if not hasattr(cparent, "parent"):
                    break
                cparent = cparent.parent
                parents.insert(0, cparent.name)
            context["parents"] = parents
        return context


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
    title = "Containertype"

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
    fields = [
        "name",
        "dimx",
        "dimy",
        "dimz",
        "containeremptyweight",
        "hierarchy_order_number",
        "description",
    ]
    template_name = "warehouse/form_edit.html"
    title = "Containertype"
    success_url = "/"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        containertype = self.get_object()
        if self.request.user == containertype.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ContainerTypeListView(LoginRequiredMixin, ListView):
    model = Containertype
    context_object_name = "containers"
    template_name = "warehouse/containertype_list.html"

    def get_queryset(self):
        containertypes = Containertype.objects.filter(  # pylint: disable=no-member
            owner=get_current_authenticated_user().id
        ).all()

        return containertypes


class ItemStoreCreateView(LoginRequiredMixin, CreateView):
    model = BLInventoryItem
    form_class = StoreItemForm
    success_url = "/w"
    template_name = "warehouse/stored_item_create.html"
    title = "Stored Item"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ItemStoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BLInventoryItem
    template_name = "warehouse/form_edit.html"
    title = "Stored Item"
    success_url = "/w"
    fields = [
        "container",
        "inventory_id",
        "color",
        "count",
        "condition",
        "completeness",
        "unit_price",
        "description",
        "bulk",
        "is_retain",
        "is_stock_room",
        "sale_rate",
        "tier_quantity1",
        "tier_price1",
        "tier_quantity2",
        "tier_price2",
        "tier_quantity3",
        "tier_price3",
    ]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        stored_item = self.get_object()
        if self.request.user == stored_item.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ItemStoreListView(LoginRequiredMixin, ListView):
    model = BLInventoryItem
    context_object_name = "items"
    template_name = "warehouse/stored_items_list.html"
    paginate_by = 50
    ordering = ["item_id"]

    def get_queryset(self):
        containers = Container.objects.filter(  # pylint: disable=no-member
            owner=get_current_authenticated_user().id
        ).all()

        return containers
