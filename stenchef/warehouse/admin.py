from django.contrib import admin
from .models import (
    Container,
    Containertype,
    BLInventoryItem,
    Purchase,
    Order,
    OrderItem,
)


@admin.register(Container)
@admin.register(Containertype)
@admin.register(BLInventoryItem)
@admin.register(Purchase)
@admin.register(Order)
@admin.register(OrderItem)
class AuthorAdmin(admin.ModelAdmin):
    pass
