from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from api.v1.labels.models import Label


class Video(models.Model):
    video_url = models.URLField(null=True, blank=True)
    video_file = models.FileField(null=True, blank=True)
    text = models.CharField(null=True, blank=True, max_length=500)
    labels = models.ManyToManyField(Label, related_name='video_labels', blank=True)

    def __str__(self):
        return f"{self.text}"
