from django.contrib import admin
from .models import (
    Container,
    Containertype,
    StoredItem,
    BLInventoryItem,
    Purchase,
)


@admin.register(Container)
@admin.register(Containertype)
@admin.register(StoredItem)
@admin.register(BLInventoryItem)
@admin.register(Purchase)
class AuthorAdmin(admin.ModelAdmin):
    pass
