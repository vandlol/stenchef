from django.shortcuts import render
from django.http import HttpResponse
from .models import Container, StoredItem
from pprint import pprint as pp


def home(request):
    context = {"containers": Container.objects.all()}
    # for c in Container.objects.all():
    #     for o in StoredItem.objects.filter(container=c):
    #         print(o)
    # return HttpResponse(context, content_type="application/json")
    return render(request, "warehouse/container.html", context)


def about(request):
    return render(request, "warehouse/about.html")
