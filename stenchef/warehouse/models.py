import uuid
import random
import string
from django.db import models
from django.utils import timezone
import django.contrib.auth.models as dmodels
from django_currentuser.middleware import get_current_authenticated_user

# TODO add default config, also make db and editable
id_length = 4


class Containertype(models.Model):
    typeid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        dmodels.User, default=get_current_authenticated_user, on_delete=models.CASCADE)

    def __str__(self):
        return(self.name)


class Container(models.Model):
    containerid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    containertype = models.ForeignKey(Containertype, on_delete=models.CASCADE)
    slug = models.SlugField(default=''.join([random.choice(
        string.ascii_letters.upper() + string.digits) for n in range(id_length)]))
    dimx = models.PositiveIntegerField(default=0)
    dimy = models.PositiveIntegerField(default=0)
    dimz = models.PositiveIntegerField(default=0)
    containeremptyweight = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        dmodels.User, on_delete=models.CASCADE, default=get_current_authenticated_user)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, default=None)
    description = models.TextField(blank=True)
    # TODO
    # content = models.ForeignKey(Part)
    # constraints = TODO

    def __str__(self):
        return(self.name)


class StoredItem(models.Model):
    storedid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    itemid = models.ForeignKey(
        'catalog.ItemIdentifier', on_delete=models.CASCADE)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)
    owner = models.ForeignKey(
        dmodels.User, on_delete=models.CASCADE, default=get_current_authenticated_user)
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return(str(self.storedid))
