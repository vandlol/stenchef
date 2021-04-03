from django.contrib import admin
from .models import (
    Setting,
)


@admin.register(Setting)
class AuthorAdmin(admin.ModelAdmin):
    pass
