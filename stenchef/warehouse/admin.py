from django.contrib import admin
from .models import (
    Container,
    Containertype,
    StoredItem,
    MOC,
    MOCContent,
    BLInventoryItem,
    Purchase,
)


@admin.register(Container)
@admin.register(Containertype)
@admin.register(StoredItem)
@admin.register(MOC)
@admin.register(MOCContent)
@admin.register(BLInventoryItem)
@admin.register(Purchase)
class AuthorAdmin(admin.ModelAdmin):
    pass
