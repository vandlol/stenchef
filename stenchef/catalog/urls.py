from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "catalog"
urlpatterns = [
    path("c/", views.home, name="home"),
]


item = [
    path("list/", views.ItemListView.as_view(), name="ilist",),
    path("detail/<str:pk>", views.ItemDetailView.as_view(), name="idetail"),
    path("autocomplete/", views.ItemAutocomplete.as_view(), name="iauto",),
]

urlpatterns = [
    path("", lambda request: redirect("w/", permanent=True)),
    path(
        "c/",
        include([path("", views.home, name="home"), path("item/", include(item)),]),
    ),
]
