from django.contrib import admin
from .models import (
    Container,
    Containertype,
    StoredItem,
    MOC,
    MOCContent,
    BLInventoryItem,
)


@admin.register(Container)
@admin.register(Containertype)
@admin.register(StoredItem)
@admin.register(MOC)
@admin.register(MOCContent)
@admin.register(BLInventoryItem)
class AuthorAdmin(admin.ModelAdmin):
    pass
