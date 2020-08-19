from django.shortcuts import render
from .models import Item


def home(request):
    context = {"containers": Item.objects.all()}
    return render(request, 'warehouse/catalog.html', context)
