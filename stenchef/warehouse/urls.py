from django.urls import path, include, register_converter
from django.shortcuts import redirect
from warehouse import views
from .converts import FloatUrlParameterConverter

register_converter(FloatUrlParameterConverter, "float")
app_name = "warehouse"

order = [
    path(
        "list/",
        views.ListOrdersView.as_view(),
        name="olist",
    ),
    path(
        "item/list/<str:order_id>",
        views.ItemListOrdersView.as_view(),
        name="oilist",
    ),
    path(
        "invoice/create/<str:order_id>", views.CreateInvoice.as_view(), name="oicreate"
    ),
]

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
    path(
        "store/<str:itemuid>/<str:colorid>/<int:quantity>/<str:condition>/<float:price>",
        views.ItemStoreCreateView.as_view(),
        name="istore",
    ),
    path("colorpick/<str:itemuid>", views.AddPartView.as_view(), name="iadd"),
    path("delete/<uuid:pk>", views.ItemStoreDeleteView.as_view(), name="idelete"),
    path(
        "delete/<uuid:pk>/<str:noninteractive>",
        views.ItemStoreDeleteView.as_view(),
        name="idelete",
    ),
    path("delete/<slug:slug>", views.ItemStoreDeleteView.as_view(), name="idelete"),
    path("edit/<uuid:pk>", views.ItemStoreUpdateView.as_view(), name="iedit"),
    path("edit/<slug:slug>", views.ItemStoreUpdateView.as_view(), name="iedit"),
    path(
        "edit/container/<uuid:pk>",
        views.ItemStoreUpdateContainerView.as_view(),
        name="icedit",
    ),
    path(
        "edit/containerwoc/<uuid:pk>",
        views.ItemStoreUpdateContainerFWOCView.as_view(),
        name="icwocedit",
    ),
    path(
        "edit/quantity/<uuid:pk>",
        views.ItemStoreUpdateQuantityView.as_view(),
        name="iqedit",
    ),
    path(
        "edit/quantity/<uuid:pk>/<int:quantity>",
        views.ItemStoreUpdateQuantityView.as_view(),
        name="iqedit",
    ),
    path(
        "edit/price/<uuid:pk>",
        views.ItemStoreUpdatePriceView.as_view(),
        name="ipedit",
    ),
    path("partout/<str:itemid>", views.SetPartoutListView.as_view(), name="spartout"),
    path(
        "list/",
        views.ItemStoreListView.as_view(),
        name="ilist",
    ),
    path(
        "list/woc",
        views.ItemStoreListNoContainerView.as_view(),
        name="iwoclist",
    ),
    path("import/", views.ImportInventory.as_view(), name="iimport"),
    path("export/", views.ExportInventoryFull.as_view(), name="iexport"),
    path("export/<uuid:pk>", views.ExportInventorySingle.as_view(), name="iexport"),
    path(
        "autocomplete/",
        views.StoredItemAutocomplete.as_view(),
        name="iauto",
    ),
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
                path("order/", include(order)),
            ]
        ),
    ),
]
