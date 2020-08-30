from django.contrib import admin
from .models import Item, SetContent


@admin.register(Item)
@admin.register(SetContent)
class AuthorAdmin(admin.ModelAdmin):
    pass
