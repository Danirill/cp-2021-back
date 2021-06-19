from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from api.v1.images.serializers import ImageSerializer
from api.v1.products.models import Product, ProductCategory
from utils.utils import validate_positive


class ProductInputSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)


class ProductManyInputSerializer(serializers.Serializer):
    products = serializers.ListSerializer(child=serializers.PrimaryKeyRelatedField(queryset=Product.objects.all()),
                                          required=True)


class ProductUUIDInputSerializer(serializers.Serializer):
    product_uuid = serializers.UUIDField(required=True)


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    count = serializers.IntegerField()


class CartPriceSerializer(serializers.Serializer):
    data = CartItemSerializer(many=True)
    token = serializers.CharField(allow_null=True, required=False)
    month = serializers.IntegerField(default=1, required=False, validators=[
        MaxValueValidator(100),
        MinValueValidator(1)
    ])

class ProductSerializer(serializers.ModelSerializer):
    product_categories = ProductCategorySerializer(many=True)
    images = ImageSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'
