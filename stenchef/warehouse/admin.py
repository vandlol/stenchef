from django.contrib import admin
from .models import (
    Container,
    Containertype,
    BLInventoryItem,
    Purchase,
)


@admin.register(Container)
@admin.register(Containertype)
@admin.register(BLInventoryItem)
@admin.register(Purchase)
class AuthorAdmin(admin.ModelAdmin):
    pass
