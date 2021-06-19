import uuid as uuid

from django.conf import settings
from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType

from ..products.models import Product
from ..users.models import User
from ..labels.models import Label
from ..worksheets.BuyingForms.models import AnswerAction


class Recommendation(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="recommendation_user")
    main_products = models.ManyToManyField(Product, blank=True, related_name="main_products")
    optional_products = models.ManyToManyField(Product, blank=True, related_name="optional_products")
    labels = models.ManyToManyField(Label, blank=True)
    uuid = models.UUIDField(auto_created=True, editable=True, default=uuid.uuid4, null=True)
    info = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'Recommendation: {self.id}, user: {self.user.name}'

    def get_link(self):
        return f"{settings.FRONTEND_URL}/recommendation/?id={self.uuid}"

    def get_detail_string(self):
        str = ""

        if self.user:
            str += f"User: {self.user.name} id:{self.user.id}\n"
        else:
            str += f"Empty user \n"

        str += "============\n"
        if self.main_products:

            str += "Products: "
            for product in self.main_products.all():
                str += f"{product.product_name}, "
            str += "\n"

        str += "============\n"

        if self.uuid:
            str += f"UUID: {self.uuid}\n"

        str += "============\n"
        str += f"Created: {self.created_at}\n"
        str += "============\n"
        if self.info:
            str += "info:\n"
            for key, value in self.info.items():
                str += f"{key}: {value}\n"
            str += "\n"
        return str

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

class RecommendationPosition(models.Model):
    product = models.ForeignKey(Product, blank=True, on_delete=models.CASCADE)
    actions = models.ManyToManyField(AnswerAction, blank=True)

    def __str__(self):
        return f'Recommendation: {self.id}, product: {self.product}'

class RecommendationDetailed(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="recommendation_detailed_user")
    main_positions = models.ManyToManyField(RecommendationPosition, blank=True, related_name="main_positions")
    optional_positions = models.ManyToManyField(RecommendationPosition, blank=True, related_name="optional_positions")
    labels = models.ManyToManyField(Label, blank=True)
    data = models.JSONField(null=True, blank=True)
    uuid = models.UUIDField(auto_created=True, editable=True, default=uuid.uuid4, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'Recommendation: {self.id}, main_positions: {self.main_positions}'

    def get_link(self):
        return f"{settings.FRONTEND_URL}/detailed_recommendation?id={self.uuid}"
