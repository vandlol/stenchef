from django.contrib import admin
from .models import Item, ItemIdentifier


@admin.register(Item)
@admin.register(ItemIdentifier)
class AuthorAdmin(admin.ModelAdmin):
    pass
