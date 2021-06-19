import uuid as uuid
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.safestring import mark_safe




class Image(models.Model):
    image = models.FileField(blank=True, null=True, validators=[FileExtensionValidator(['pdf', 'jpg', 'svg', 'png', 'gif', 'webp'])])
    uuid = models.UUIDField(auto_created=True, editable=True, default=uuid.uuid4, null=True)

    @property
    def thumbnail_preview(self):
        if self.image:
            return mark_safe('<img src="{}" width="300" height="300" />'.format(self.image.url))
        return ""

    def __str__(self):
        return f'{self.image.name}'
