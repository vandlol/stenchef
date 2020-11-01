from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    ListView,
    TemplateView,
    DeleteView,
    UpdateView,
    DetailView,
    View,
    FormView,
)
from extra_views import ModelFormSetView
from django import forms
from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic.edit import ModelFormMixin, FormMixin
from .forms import (
    ContainerForm,
    ContainerTypeForm,
    StoreItemForm,
    StoreItemUpdateContainerForm,
    StoreItemUpdateQuantityForm,
    SearchBarForm,
)
from .models import Container, Containertype, BLInventoryItem
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from pprint import pprint as pp
from django_currentuser.middleware import get_current_authenticated_user
from catalog.models import Item
from meta.models import Color, Condition
from user.models import Setting
from dal import autocomplete
from warehouse.bricklink_integration import (
    part_out_set,
    bl_auth,
    import_inventory,
    add_quantity,
    update_container,
    update_price,
    export_inventory_full,
    export_inventory_single,
    query_price,
    known_colors,
    orders_query,
    order_query,
    generate_picklist,
)
from warehouse.lexoffice_integration import create_invoice


class HomePageView(TemplateView):
    def query_data(self):
        _query = {"containers": Container.objects.all()}  # pylint: disable=no-member
        return _query

    def get(self, request, **kwargs):
        return render(request, "warehouse/container.html", context=self.query_data())


class ContainerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Container.objects.filter(  # pylint: disable=no-member
            owner=get_current_authenticated_user().id
        ).all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class StoredItemAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = BLInventoryItem.objects.filter(  # pylint: disable=no-member
            owner=get_current_authenticated_user().id
        ).all()
        if self.q:
            qs = qs.filter(item_id_id__itemuid__icontains=self.q)
        return qs

    def get_result_label(self, item):
        return "{}-{}-{}".format(
            item.item_id.itemuid,
            item.color.colorname.replace(" ", "_"),
            item.condition.name,
        )


class ContainerCreateView(LoginRequiredMixin, CreateView):
    model = Container
    form_class = ContainerForm
    success_url = "/w/container/list"
    template_name = "warehouse/form_create.html"
    title = "Container"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        if self.kwargs:
            if self.kwargs.get("parent") and self.kwargs.get("type"):
                context["form"] = ContainerForm(
                    initial={
                        "parent": self.kwargs["parent"],
                        "containertype": self.kwargs["type"],
                    }
                )
            if self.kwargs.get("parent"):
                context["form"] = ContainerForm(
                    initial={"parent": self.kwargs["parent"]}
                )
            if self.kwargs.get("type"):
                context["form"] = ContainerForm(
                    initial={"containertype": self.kwargs["type"]}
                )

        return context


class ContainerListView(LoginRequiredMixin, ListView):
    model = Container
    context_object_name = "containers"
    template_name = "warehouse/container_list.html"
    paginate_by = 50
    ordering = ["name"]

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = Container.objects.filter(  # pylint: disable=no-member
                name__icontains=query,
                owner=get_current_authenticated_user().id,
            ).all()
        else:
            object_list = Container.objects.filter(  # pylint: disable=no-member
                owner=get_current_authenticated_user().id
            ).all()
        return object_list.order_by("name")


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
    template_name = "warehouse/stored_item_create.html"
    title = "Stored Item"

    def form_valid(self, form):

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        if (
            self.kwargs.get("itemuid")
            and self.kwargs.get("colorid")
            and self.kwargs.get("quantity")
            and self.kwargs.get("condition")
            and self.kwargs.get("price")
        ):
            context["form"] = StoreItemForm(
                initial={
                    "item_id": self.kwargs["itemuid"],
                    "color": self.kwargs["colorid"],
                    "condition": self.kwargs["condition"],
                    "count": self.kwargs["quantity"],
                    "unit_price": self.kwargs["price"],
                }
            )
        return context

    def get_success_url(self):
        pk = self.kwargs["itemuid"]
        return reverse("warehouse:iadd", kwargs={"itemuid": pk})


class ItemStoreDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BLInventoryItem
    success_url = "/w/item/list"
    template_name = "warehouse/confirm_delete.html"
    title = "Stored Item"

    def test_func(self):
        containertype = self.get_object()
        if self.request.user == containertype.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ItemStoreUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BLInventoryItem
    template_name = "warehouse/form_edit.html"
    title = "Stored Item"
    success_url = "/w/item/list/"
    fields = [
        "inventory_id",
        "color",
        "condition",
        "count",
        "completeness",
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


class ItemStoreUpdateContainerView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BLInventoryItem
    template_name = "warehouse/form_edit.html"
    title = "Container"
    success_url = "/w/item/list"
    form_class = StoreItemUpdateContainerForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        item = self.get_object()
        inventory_id = item.inventory_id
        containerid = self.request.POST["container"]
        update_container(
            get_current_authenticated_user().id,
            inventory_id,
            containerid,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        redirect_url = super().form_valid(form)
        return redirect_url

    def test_func(self):
        stored_item = self.get_object()
        if self.request.user == stored_item.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ItemStoreUpdateContainerFWOCView(
    LoginRequiredMixin, UserPassesTestMixin, UpdateView
):
    model = BLInventoryItem
    template_name = "warehouse/form_edit.html"
    title = "FWOC"
    success_url = "/w/item/list/woc"
    form_class = StoreItemUpdateContainerForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        item = self.get_object()
        inventory_id = item.inventory_id
        containerid = self.request.POST["container"]
        update_container(
            get_current_authenticated_user().id,
            inventory_id,
            containerid,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        redirect_url = super().form_valid(form)
        return redirect_url

    def test_func(self):
        stored_item = self.get_object()
        if self.request.user == stored_item.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        return context


class ItemStoreUpdateQuantityView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "warehouse/stored_item_add_quantity_form.html"
    success_url = "warehouse/close_window.html"
    model = BLInventoryItem
    form_class = StoreItemUpdateContainerForm
    title = "Stored Item"

    def post(self, request, **kwargs):
        item = BLInventoryItem.objects.filter(  # pylint: disable=no-member
            storedid=self.kwargs["pk"], owner=get_current_authenticated_user().id
        ).first()
        quantity = int(request.POST["add_item"])
        itemid = item.item_id_id
        color_id = item.color_id
        condition = item.condition_id
        add_quantity(
            get_current_authenticated_user().id,
            itemid,
            color_id,
            condition,
            quantity,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        item.count = item.count + quantity
        item.save()
        return render(request, "warehouse/close_window.html")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        redirect_url = super().form_valid(form)
        return redirect_url

    def test_func(self):
        stored_item = self.get_object()
        if self.request.user == stored_item.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        if self.kwargs.get("quantity"):
            context["quantity"] = self.kwargs["quantity"]
        return context


class ItemStoreUpdatePriceView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = "warehouse/stored_item_change_price_form.html"
    success_url = "warehouse/close_window.html"
    model = BLInventoryItem
    form_class = StoreItemUpdateContainerForm
    title = "Stored Item"

    def post(self, request, **kwargs):
        item = BLInventoryItem.objects.filter(  # pylint: disable=no-member
            storedid=self.kwargs["pk"], owner=get_current_authenticated_user().id
        ).first()
        price = float(request.POST["change_price"])
        itemid = item.item_id_id
        color_id = item.color_id
        condition = item.condition_id
        update_price(
            get_current_authenticated_user().id,
            itemid,
            color_id,
            condition,
            price,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        item.unit_price = price
        item.save()
        return render(request, "warehouse/close_window.html")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        redirect_url = super().form_valid(form)
        return redirect_url

    def test_func(self):
        stored_item = self.get_object()
        if self.request.user == stored_item.owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # get the default context data
        context["title"] = self.title
        item = BLInventoryItem.objects.filter(  # pylint: disable=no-member
            storedid=self.kwargs["pk"], owner=get_current_authenticated_user().id
        ).first()
        context["price_curr"] = float(item.unit_price)
        context["price_prop"] = float(
            query_price(
                item.item_id.itemtype_id,
                item.item_id.itemid,
                item.color_id,
                item.condition_id,
                auth=bl_auth(
                    Setting.objects.filter(  # pylint: disable=no-member
                        owner=get_current_authenticated_user().id
                    ).first()
                ),
            )
        )
        return context


class ItemStoreListView(LoginRequiredMixin, ListView):
    model = BLInventoryItem
    context_object_name = "items"
    template_name = "warehouse/stored_item_list.html"
    paginate_by = 50

    def get_queryset(self):
        query = self.request.GET.get("item_id")
        if query:
            object_list = BLInventoryItem.objects.filter(  # pylint: disable=no-member
                storedid=query,
                owner=get_current_authenticated_user().id,
            ).all()
        else:
            object_list = BLInventoryItem.objects.filter(  # pylint: disable=no-member
                owner=get_current_authenticated_user().id
            ).all()
        return object_list

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["form"] = SearchBarForm()
        return context


class ItemStoreListNoContainerView(LoginRequiredMixin, ListView):
    model = BLInventoryItem
    context_object_name = "items"
    template_name = "warehouse/stored_item_list.html"
    paginate_by = 50
    title = "FWOC"

    def get_queryset(self):
        query = self.request.GET.get("item_id")
        if query:
            object_list = BLInventoryItem.objects.filter(  # pylint: disable=no-member
                storedid=query,
                container=None,
                owner=get_current_authenticated_user().id,
            ).all()
        else:
            object_list = BLInventoryItem.objects.filter(  # pylint: disable=no-member
                owner=get_current_authenticated_user().id,
                container=None,
            ).all()
        return object_list


class AddPartView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        if not self.kwargs:
            return
        if not self.kwargs.get("itemuid"):
            return
        itemtype, itemid = self.kwargs["itemuid"].split("_")

        if self.request.GET.get("color"):
            c = Color.objects.filter(  # pylint: disable=no-member
                colorname=self.request.GET["color"]
            ).first()

            condition = Condition.objects.filter(  # pylint: disable=no-member
                name=self.request.GET["condition"]
            ).first()

            found = BLInventoryItem.objects.filter(  # pylint: disable=no-member
                item_id=self.kwargs["itemuid"],
                color=c.color,
                condition=condition.condition,
                owner=get_current_authenticated_user().id,
            ).first()

            if found:
                return redirect("/w/item/edit/quantity/{}".format(found.storedid))
            price_prop = float(
                query_price(
                    itemtype,
                    itemid,
                    c.color,
                    condition.condition,
                    auth=bl_auth(
                        Setting.objects.filter(  # pylint: disable=no-member
                            owner=get_current_authenticated_user().id
                        ).first()
                    ),
                )
            )
            return redirect(
                "/w/item/store/{}/{}/1/{}/{}".format(
                    self.kwargs["itemuid"], c.color, condition.condition, price_prop
                )
            )

        context = dict()
        context["itemuid"] = self.kwargs["itemuid"]
        context["colors"] = known_colors(
            itemtype,
            itemid,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        return render(request, "warehouse/add_item.html", context)


class SetPartoutListView(LoginRequiredMixin, ListView):
    template_name = "warehouse/partout_item_list.html"
    context_object_name = "items"

    def get_queryset(self, **kwargs):
        if not self.kwargs:
            return
        if not self.kwargs.get("itemid"):
            return
        if self.request.GET.get("multi"):
            multi = self.request.GET["multi"]
        else:
            multi = 1
        setid = self.kwargs["itemid"]
        if "-" in setid:
            setid, subsetid = setid.split("-")
        else:
            subsetid = 1
        items = part_out_set(
            setid,
            get_current_authenticated_user().id,
            subset=subsetid,
            multi=multi,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        return items


class ImportInventory(LoginRequiredMixin, View):
    def get(self, request):
        import_inventory(  # pylint: disable=no-member
            get_current_authenticated_user().id,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        return redirect("/w/item/list/")


class ExportInventoryFull(LoginRequiredMixin, View):
    def get(self, request):
        import_inventory(  # pylint: disable=no-member
            get_current_authenticated_user().id,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        export_inventory_full(
            get_current_authenticated_user().id,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        import_inventory(  # pylint: disable=no-member
            get_current_authenticated_user().id,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        return redirect("/w/item/list/")


class ExportInventorySingle(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        export_inventory_single(
            get_current_authenticated_user().id,
            self.kwargs["pk"],
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        return redirect("/w/item/list/")


class ListOrdersView(LoginRequiredMixin, View):
    def get(self, request):
        orders = orders_query(
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        for order in orders:
            order["disp_cost"]["shipping"] = "{:.2f}".format(
                float(order["disp_cost"]["grand_total"])
                - float(order["disp_cost"]["subtotal"])
            )
        context = dict()
        context["orders"] = orders
        return render(request, "warehouse/order_list.html", context)


class ItemListOrdersView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        order_id = self.kwargs["order_id"]
        pick = generate_picklist(
            order_id,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        context = dict()
        context["order_id"] = order_id
        context["items"] = list()
        for elem in pick:
            for item in elem:
                i = item
                found = BLInventoryItem.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id,
                    inventory_id=item["inventory_id"],
                ).first()
                if found:
                    i["type_short"] = found.item_id.itemtype.itemtype
                    i["container"] = found.container.name
                    i["storage_count"] = found.count
                    i["storedid"] = str(found.storedid)
                    i["noninteractive"] = "y"
                    i["remaining_count"] = found.count - i["quantity"]
                    i["show_delete"] = "y"
                else:
                    i["type_short"] = None
                    i["container"] = None
                    i["storage_count"] = 0
                    i["storedid"] = None
                    i["noninteractive"] = "n"
                    i["remaining_count"] = 0
                    i["show_delete"] = "n"
                context["items"].append(i)
        return render(request, "warehouse/order_item_list.html", context)


class CreateInvoice(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        order_id = self.kwargs["order_id"]
        ordered_items = generate_picklist(
            order_id,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        order_details = order_query(
            order_id,
            auth=bl_auth(
                Setting.objects.filter(  # pylint: disable=no-member
                    owner=get_current_authenticated_user().id
                ).first()
            ),
        )
        create_invoice(order_details, ordered_items)
        return redirect("/w/order/item/list/{}".format(order_id))
