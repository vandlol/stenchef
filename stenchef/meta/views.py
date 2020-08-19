from django.shortcuts import render
from .models import Color


def home(request):
    context = {"containers": Color.objects.all()}
    return render(request, 'warehouse/catalog.html', context)
