from django.contrib import admin
from .models import Color, Category, Itemtype, Code, Condition


@admin.register(Color)
@admin.register(Category)
@admin.register(Itemtype)
@admin.register(Code)
@admin.register(Condition)
class AuthorAdmin(admin.ModelAdmin):
    pass
