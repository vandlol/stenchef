import uuid
import random
import string
from django.db import models
from django.utils import timezone
import django.contrib.auth.models as dmodels
from django_currentuser.middleware import get_current_authenticated_user
from .fields import IntegerRangeField
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify


class Containertype(models.Model):
    typeid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        dmodels.User,
        default=get_current_authenticated_user,
        on_delete=models.CASCADE,
        editable=False,
    )

    def __str__(self):
        return self.name


class Container(models.Model):
    containerid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    containertype = models.ForeignKey(Containertype, on_delete=models.CASCADE,)
    slug = models.SlugField(editable=False)
    dimx = models.PositiveIntegerField(default=0)
    dimy = models.PositiveIntegerField(default=0)
    dimz = models.PositiveIntegerField(default=0)
    containeremptyweight = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now, editable=False)
    owner = models.ForeignKey(
        dmodels.User,
        on_delete=models.CASCADE,
        default=get_current_authenticated_user,
        editable=False,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        default=None,
        related_name="children",
    )
    description = models.TextField(blank=True)
    # constraints = TODO

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Container, self).save(*args, **kwargs)


class StoredItem(models.Model):
    storedid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    itemid = models.ForeignKey("catalog.Item", on_delete=models.CASCADE)
    color = models.ForeignKey("meta.Color", on_delete=models.CASCADE)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        dmodels.User,
        on_delete=models.CASCADE,
        default=get_current_authenticated_user,
        editable=False,
    )
    condition = models.ForeignKey("meta.Condition", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.storedid)


class MOC(models.Model):
    mocid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    date_added = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        dmodels.User,
        on_delete=models.CASCADE,
        default=get_current_authenticated_user,
        editable=False,
    )
    description = models.TextField(blank=True)
    pictures = models.ImageField(upload_to="moc_pics", blank=True, default=None)
    instruction = models.FileField(
        upload_to="instructions/", max_length=254, blank=True, default=None
    )
    private = models.BooleanField(default=True)


class MOCContent(models.Model):
    contentid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    itemid = models.ForeignKey(
        "catalog.Item", on_delete=models.CASCADE, limit_choices_to={"itemtype": "P"}
    )
    owner = models.ForeignKey(
        dmodels.User,
        on_delete=models.CASCADE,
        default=get_current_authenticated_user,
        editable=False,
    )
    color = models.ForeignKey("meta.Color", on_delete=models.CASCADE)
    mocid = models.ForeignKey(MOC, on_delete=models.CASCADE)
    condition = models.ForeignKey("meta.Condition", on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.contentid)


class BLInventoryItem(models.Model):
    blinvid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inventory_id = models.PositiveIntegerField(default=None, blank=True)
    item_id = models.ForeignKey("catalog.Item", on_delete=models.CASCADE)
    color = models.ForeignKey("meta.Color", on_delete=models.CASCADE, default="0")
    count = models.PositiveIntegerField(default=1)
    condition = models.ForeignKey(
        "meta.Condition",
        on_delete=models.CASCADE,
        default="N",
        limit_choices_to={"subcondition": False},
    )
    completeness = models.ForeignKey(
        "meta.Condition",
        on_delete=models.CASCADE,
        default=None,
        related_name="+",
        limit_choices_to={"subcondition": True},
        blank=True,
    )
    unit_price = models.DecimalField(default=1.0000, max_digits=20, decimal_places=4)
    parent_id = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, default=None
    )
    description = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    bulk = models.PositiveIntegerField(default=1, blank=True)
    is_retain = models.BooleanField(default=False)
    is_stock_room = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    sale_rate = IntegerRangeField(min_value=-1000, max_value=99, default=0)
    models.DecimalField(default=1.0000, max_digits=20, decimal_places=4)
    tier_quantity1 = models.PositiveIntegerField(default=0)
    tier_price1 = models.DecimalField(default=1.0000, max_digits=20, decimal_places=4)
    tier_quantity2 = models.PositiveIntegerField(default=0)
    tier_price2 = models.DecimalField(default=1.0000, max_digits=20, decimal_places=4)
    tier_quantity3 = models.PositiveIntegerField(default=0)
    tier_price3 = models.DecimalField(default=1.0000, max_digits=20, decimal_places=4)
    owner = models.ForeignKey(
        dmodels.User,
        on_delete=models.CASCADE,
        default=get_current_authenticated_user,
        editable=False,
    )


class Purchase(models.Model):
    purchaseid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_id = models.ForeignKey(
        "catalog.Item", on_delete=models.CASCADE, blank=True, default=None
    )
    name = models.CharField(max_length=256, blank=True, default=None)
    count = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(default=1.0000, max_digits=20, decimal_places=4)
    container = models.ForeignKey(
        Container, on_delete=models.CASCADE, blank=True, default=None
    )
    seller = models.CharField(max_length=256, blank=True, default=None)
    url = models.URLField(max_length=1000, blank=True, default=None)
    invoice = models.FileField(
        upload_to="invoice/", max_length=254, blank=True, default=None
    )
    owner = models.ForeignKey(
        dmodels.User,
        on_delete=models.CASCADE,
        default=get_current_authenticated_user,
        editable=False,
    )

    def clean(self):
        if self.name == None and self.item_id is None:
            raise ValidationError("Field name or item are required.")
