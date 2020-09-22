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
from rgbfield.fields import RGBColorField


class Containertype(models.Model):
    typeid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Give your Containertype a Name. 100 Characters maximum.",
    )
    owner = models.ForeignKey(
        dmodels.User,
        default=get_current_authenticated_user,
        on_delete=models.CASCADE,
        editable=False,
    )
    dimx = models.PositiveIntegerField(
        default=0,
        help_text="Size of your Container in X Dimension. Will be ignored if set to 0.",
    )
    dimy = models.PositiveIntegerField(
        default=0,
        help_text="Size of your Container in X Dimension. Will be ignored if set to 0.",
    )
    dimz = models.PositiveIntegerField(
        default=0,
        help_text="Size of your Container in X Dimension. Will be ignored if set to 0.",
    )
    containeremptyweight = models.PositiveIntegerField(
        default=0,
        help_text="Weight of your Container if empty. Will be ignored if set to 0.",
    )
    hierarchy_order_number = IntegerRangeField(
        min_value=-99999,
        max_value=99999,
        default=0,
        help_text="Hierarchy works like this: Containers can also fit into Containers with a bigger number. Keep gaps between numbers. Containers of equal numbers will not fit in each other (except 0). (Min -99999, Max 99999) Will be ignored if set to 0.",
    )
    description = models.TextField(
        blank=True,
        help_text="Write something helpful about this Type of Container",
    )
    color = models.CharField(
        max_length=7,
        default="#fff",
        help_text="Every Container you Create from this type will be colored like this. https://www.w3schools.com/colors/colors_picker.asp Pick a Color and Copy the #Value.",
    )
    prefix = models.CharField(
        max_length=4,
        blank=True,
        help_text="If you create a Container ...FIXME",
    )

    def __str__(self):
        return self.name


class Container(models.Model):
    containerid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100, help_text="Give your Container a Name. 100 Characters maximum."
    )
    containertype = models.ForeignKey(
        Containertype,
        on_delete=models.CASCADE,
    )
    slug = models.SlugField(editable=False)
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


class BLInventoryItem(models.Model):
    storedid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    container = models.ForeignKey(Container, on_delete=models.CASCADE, blank=True)
    owner = models.ForeignKey(
        dmodels.User,
        on_delete=models.CASCADE,
        default=get_current_authenticated_user,
        editable=False,
    )
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
    description = models.TextField(blank=True)
    bulk = models.PositiveIntegerField(default=1, blank=True)
    is_retain = models.BooleanField(default=False)
    is_stock_room = models.BooleanField(default=False)
    sale_rate = IntegerRangeField(min_value=-1000, max_value=99, default=0)
    tier_quantity1 = models.PositiveIntegerField(default=0)
    tier_price1 = models.DecimalField(default=0.0000, max_digits=20, decimal_places=4)
    tier_quantity2 = models.PositiveIntegerField(default=0)
    tier_price2 = models.DecimalField(default=0.0000, max_digits=20, decimal_places=4)
    tier_quantity3 = models.PositiveIntegerField(default=0)
    tier_price3 = models.DecimalField(default=0.0000, max_digits=20, decimal_places=4)

    def __str__(self):
        return str(self.item_id_id)  # pylint: disable=no-member


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
