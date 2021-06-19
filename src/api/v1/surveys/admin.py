from django.contrib import admin
from .models import SurveyCondition, SurveyAnswer, SurveyPageAttributes, SurveyPage, Survey, SurveySession, \
    SurveyPageJump, SurveySessionAnswerValue, SurveySessionAnswer

# Register your models here.
admin.site.register(SurveyCondition)
admin.site.register(SurveyAnswer)
admin.site.register(SurveyPageAttributes)

class SurveyPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'attributes', 'redirect_to')

admin.site.register(SurveyPage, SurveyPageAdmin)

admin.site.register(Survey)
admin.site.register(SurveySession)
admin.site.register(SurveyPageJump)
admin.site.register(SurveySessionAnswerValue)
admin.site.register(SurveySessionAnswer)
