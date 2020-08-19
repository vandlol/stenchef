import uuid
from django.db import models


class Item(models.Model):
    itemid = models.CharField(primary_key=True, max_length=16)
    category = models.ForeignKey('meta.Category', on_delete=models.CASCADE)
    itemdimx = models.PositiveIntegerField(default=0)
    itemdimy = models.PositiveIntegerField(default=0)
    itemdimz = models.PositiveIntegerField(default=0)
    itemweight = models.PositiveIntegerField(default=0)
    itemname = models.CharField(max_length=100)
    itemtype = models.ForeignKey('meta.Itemtype', on_delete=models.CASCADE)
    itemyear = models.PositiveIntegerField(default=0)

    def __str__(self):
        return(self.itemid)


class ItemIdentifier(models.Model):
    itemuuid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    itemcolor = models.ForeignKey('meta.Color', on_delete=models.CASCADE)
    itemid = models.ForeignKey(Item, on_delete=models.CASCADE)
    condition = models.ForeignKey('meta.Condition', on_delete=models.CASCADE)

    def __str__(self):
        return(str(self.itemid))
