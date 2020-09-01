from django.shortcuts import render
from django.http import HttpResponse
from .models import Container, StoredItem
from pprint import pprint as pp
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        return render(request, "warehouse/container.html", context=None)


# Add this view
class AboutPageView(TemplateView):
    template_name = "warehouse/about.html"
