from django.contrib import admin
from .models import Container, Containertype, StoredItem


@admin.register(Container)
@admin.register(Containertype)
@admin.register(StoredItem)
class AuthorAdmin(admin.ModelAdmin):
    pass
