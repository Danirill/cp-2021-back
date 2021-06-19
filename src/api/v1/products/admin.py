from django.contrib import admin
from .models import Product, ProductCategory, ProductCombinations
# Register your models here.

admin.site.register(Product)

admin.site.register(ProductCategory)
admin.site.register(ProductCombinations)
