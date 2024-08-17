from django.db import models


class Item(models.Model):
    title = models.TextField()
    price = models.FloatField()
