from django.urls import path, include
from django.shortcuts import redirect
from . import views

app_name = "warehouse"

containertype = [
    path("create/", views.ContainerTypeCreateView.as_view(), name="ctcreate",),
    path("delete/<uuid:pk>", views.ContainerTypeDeleteView.as_view(), name="ctdelete"),
    path("edit/<uuid:pk>", views.ContainerTypeUpdateView.as_view(), name="ctedit"),
    path("list/", views.ContainerTypeListView.as_view(), name="ctlist",),
]

container = [
    path("create/", views.ContainerCreateView.as_view(), name="ccreate",),
    path("delete/<uuid:pk>", views.ContainerDeleteView.as_view(), name="cdelete"),
    path("edit/<uuid:pk>", views.ContainerUpdateView.as_view(), name="cedit"),
    path("list/", views.ContainerListView.as_view(), name="clist",),
]

urlpatterns = [
    path("", lambda request: redirect("w/", permanent=True)),
    path(
        "w/",
        include(
            [
                path("", views.HomePageView.as_view(), name="home"),
                path("about/", views.AboutPageView.as_view(), name="about"),
                path("container/type/", include(containertype)),
                path("container/", include(container)),
                # path("categories/", views.categories, name="categories"),
            ]
        ),
    ),
]
