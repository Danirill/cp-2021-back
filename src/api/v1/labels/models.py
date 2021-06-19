import uuid as uuid
from django.db import models
from ..colors.models import Color
from ..images.models import Image


class Label(models.Model):
    label_text = models.CharField(max_length=50, null=False)
    color = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, blank=True)
    hidden_for_client = models.BooleanField(default=True)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)
    uuid = models.UUIDField(auto_created=True, editable=True, default=uuid.uuid4, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Label: {self.label_text}'
