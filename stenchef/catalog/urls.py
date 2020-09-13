from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "catalog"
urlpatterns = [
    path("c/", views.home, name="home"),
]


item = [
    # path("store/", views.ItemStoreCreateView.as_view(), name="istore",),
    # path("delete/<uuid:pk>", views.ContainerDeleteView.as_view(), name="idelete"),
    # path("delete/<slug:slug>", views.ContainerDeleteView.as_view(), name="idelete"),
    # path("delete/<str:name>", views.ContainerDeleteView.as_view(), name="idelete"),
    # path("edit/<uuid:pk>", views.ContainerUpdateView.as_view(), name="iedit"),
    # path("edit/<slug:slug>", views.ContainerUpdateView.as_view(), name="iedit"),
    # path("edit/<str:name>", views.ContainerUpdateView.as_view(), name="iedit"),
    # # path("pick/<uuid:pk>/<int:", views.ContainerDeleteView.as_view(), name="idelete"),
    # path("list/", views.ContainerListView.as_view(), name="ilist",),
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
