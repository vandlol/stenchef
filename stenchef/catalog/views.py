from django.shortcuts import render
from .models import Item
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
)
from django.core.paginator import Paginator
from dal import autocomplete
from pprint import pprint as pp


def home(request):
    context = {"items": Item.objects.all()}  # pylint: disable=no-member
    return render(request, "warehouse/catalog.html", context)


class ItemAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Item.objects.all()  # pylint: disable=no-member
        if self.q:
            qs = qs.filter(itemid__istartswith=self.q)
        return qs


class ItemListView(ListView):
    model = Item
    context_object_name = "items"
    template_name = "catalog/item_list.html"
    paginate_by = 200

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            object_list = self.model.objects.filter(  # pylint: disable=no-member
                itemid__icontains=query
            )
        else:
            object_list = self.model.objects.all()  # pylint: disable=no-member
        return object_list.order_by("itemuid")


class ItemDetailView(DetailView):
    model = Item
    template_name = "catalog/item_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item"] = self.get_object()
        context[
            "link"
        ] = "https://www.bricklink.com/v2/catalog/catalogitem.page?{}={}".format(
            context["item"].itemtype_id, context["item"].itemid
        )
        return context
