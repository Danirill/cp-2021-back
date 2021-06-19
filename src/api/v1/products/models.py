from datetime import datetime

import uuid
from django.db import models

# Create your models here.
from django.db import models

from utils.utils import get_token

from ..images.models import Image
from ..labels.models import Label

class ProductCategory(models.Model):
    product_category_name = models.CharField(max_length=1500, null=False)

    def __str__(self):
        return f'ProductCategory name: {self.product_category_name}'


class Product(models.Model):
    product_name = models.CharField(max_length=1000)
    product_internal_name = models.CharField(max_length=1000, default="Unknown")
    description_instruction = models.TextField(null=True, blank=True)
    description_format = models.TextField(null=True, blank=True)
    description_mini = models.TextField(null=True, blank=True)
    description_large = models.TextField(null=True, blank=True)
    code = models.IntegerField(null=True, blank=True)
    labels = models.ManyToManyField(Label, blank=True)
    images = models.ManyToManyField(Image, blank=True)
    price = models.IntegerField(null=True, blank=True)
    uuid = models.UUIDField(auto_created=True, editable=True, default=uuid.uuid4, null=True)
    product_categories = models.ManyToManyField(ProductCategory, blank=True)
    related_products = models.ManyToManyField('self', blank=True)


    def __str__(self):
        return f'Product name: {self.product_internal_name}, price: {self.price} \n связанные продукты: {self.related_products}'


class ProductCombinations(models.Model):

    product = models.ForeignKey(Product, unique=True, on_delete=models.CASCADE,
                                related_name="product_combination_product")
    positive_combinations = models.ManyToManyField(Product, blank=True,
                                                   related_name="positive_combinations")
    negative_combinations = models.ManyToManyField(Product, blank=True,
                                                   related_name="negative_combinations")

    def __str__(self):
        return f'{self.product}'

