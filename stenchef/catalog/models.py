import uuid
from django.db import models


class Item(models.Model):
    itemid = models.CharField(primary_key=True, max_length=16)
    category = models.ForeignKey("meta.Category", on_delete=models.CASCADE)
    itemdimx = models.PositiveIntegerField(default=0)
    itemdimy = models.PositiveIntegerField(default=0)
    itemdimz = models.PositiveIntegerField(default=0)
    itemweight = models.PositiveIntegerField(default=0)
    itemname = models.CharField(max_length=100)
    itemtype = models.ForeignKey("meta.Itemtype", on_delete=models.CASCADE)
    itemyear = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.itemid


class SetContent(models.Model):
    contentid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    setid = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        limit_choices_to={"itemtype": "S"},
        related_name="+",
    )
    itemid = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="+")
    color = models.ForeignKey("meta.Color", on_delete=models.CASCADE, default="0")
    count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.contentid)
