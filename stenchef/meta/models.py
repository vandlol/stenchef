from django.db import models


class Color(models.Model):
    color = models.CharField(max_length=16)
    colorname = models.CharField(primary_key=True, max_length=100)
    colorrgb = models.CharField(max_length=6)
    colortype = models.CharField(max_length=16)
    coloryearfrom = models.PositiveIntegerField(default=0, blank=True)
    coloryearto = models.PositiveIntegerField(default=0, blank=True)
    colorcntinv = models.CharField(max_length=10)
    colorcntparts = models.CharField(max_length=10, blank=True)
    colorcntsets = models.CharField(max_length=10, blank=True)
    colorcntwanted = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return(self.colorname)


class Category(models.Model):
    category = models.CharField(primary_key=True, max_length=16)
    categoryname = models.CharField(max_length=100)

    def __str__(self):
        return(self.categoryname)


class Itemtype(models.Model):
    itemtype = models.CharField(primary_key=True, max_length=1)
    itemtypename = models.CharField(max_length=100)

    def __str__(self):
        return(self.itemtypename)


class Code(models.Model):
    code = models.CharField(primary_key=True, max_length=16)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    itemid = models.ForeignKey('catalog.Item', on_delete=models.CASCADE)
    itemtype = models.ForeignKey(Itemtype, on_delete=models.CASCADE)

    def __str__(self):
        return(self.code)


class Condition(models.Model):
    condition = models.CharField(primary_key=True, max_length=1)
    name = models.CharField(max_length=100)

    def __str__(self):
        return(self.name)
