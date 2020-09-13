from django.shortcuts import render
from .models import Item
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
)
from dal import autocomplete


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

    def get_queryset(self):
        items = Item.objects.all()  # pylint: disable=no-member

        return items


class ItemDetailView(DetailView):
    model = Item
    template_name = "catalog/item_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["item"] = self.get_object()

        return context

