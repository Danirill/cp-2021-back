from django.contrib import admin
from .models import Label

# Register your models here.

class LabelAdmin(admin.ModelAdmin):
    list_display = ('id','info')

    def info(self, obj):
        return str(obj)

    info.short_description = 'info'
    info.allow_tags = True

admin.site.register(Label, LabelAdmin)