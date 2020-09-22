from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "warehouse"

containertype = [
    path(
        "create/",
        views.ContainerTypeCreateView.as_view(),
        name="ctcreate",
    ),
    path("delete/<uuid:pk>", views.ContainerTypeDeleteView.as_view(), name="ctdelete"),
    path(
        "delete/<slug:slug>", views.ContainerTypeDeleteView.as_view(), name="ctdelete"
    ),
    path("edit/<uuid:pk>", views.ContainerTypeUpdateView.as_view(), name="ctedit"),
    path("edit/<slug:slug>", views.ContainerTypeUpdateView.as_view(), name="ctedit"),
    path(
        "list/",
        views.ContainerTypeListView.as_view(),
        name="ctlist",
    ),
]

container = [
    path(
        "create/",
        views.ContainerCreateView.as_view(),
        name="ccreate",
    ),
    path(
        "create/p<uuid:parent>",
        views.ContainerCreateView.as_view(),
        name="ccreate",
    ),
    path(
        "create/t<uuid:type>",
        views.ContainerCreateView.as_view(),
        name="ccreate",
    ),
    path(
        "create/p<uuid:parent>/t<uuid:type>",
        views.ContainerCreateView.as_view(),
        name="ccreate",
    ),
    path(
        "create/t<uuid:type>/p<uuid:parent>",
        views.ContainerCreateView.as_view(),
        name="ccreate",
    ),
    path("delete/<uuid:pk>", views.ContainerDeleteView.as_view(), name="cdelete"),
    path("delete/<slug:slug>", views.ContainerDeleteView.as_view(), name="cdelete"),
    path("detail/<uuid:pk>", views.ContainerDetailView.as_view(), name="cdetail"),
    path("detail/<slug:slug>", views.ContainerDetailView.as_view(), name="cdetail"),
    path("edit/<uuid:pk>", views.ContainerUpdateView.as_view(), name="cedit"),
    path("edit/<slug:slug>", views.ContainerUpdateView.as_view(), name="cedit"),
    path(
        "list/",
        views.ContainerListView.as_view(),
        name="clist",
    ),
    path(
        "autocomplete/",
        views.ContainerAutocomplete.as_view(),
        name="cauto",
    ),
]

item = [
    path(
        "store/",
        views.ItemStoreCreateView.as_view(),
        name="istore",
    ),
    path("delete/<uuid:pk>", views.ContainerDeleteView.as_view(), name="idelete"),
    path("delete/<slug:slug>", views.ContainerDeleteView.as_view(), name="idelete"),
    path("edit/<uuid:pk>", views.ItemStoreUpdateView.as_view(), name="iedit"),
    path("edit/<slug:slug>", views.ItemStoreUpdateView.as_view(), name="iedit"),
    path("partout/<str:itemid>", views.SetPartoutListView.as_view(), name="spartout"),
    path(
        "list/",
        views.ItemStoreListView.as_view(),
        name="ilist",
    ),
    path("import/", views.ImportInventory.as_view(), name="iimport"),
]

urlpatterns = [
    path("", lambda request: redirect("w/", permanent=True)),
    path(
        "w/",
        include(
            [
                path("", views.HomePageView.as_view(), name="home"),
                path("container/type/", include(containertype)),
                path("container/", include(container)),
                path("item/", include(item)),
            ]
        ),
    ),
]
