from django.contrib import admin
from .models import Form, RecommendationLimit, FormAnswer, AnswerScore, SurveyAnswerActionsHub, AnswerAction

# Register your models here.

# admin.site.register(Form)
admin.site.register(RecommendationLimit)
# admin.site.register(FormAnswer)
# admin.site.register(AnswerScore)
admin.site.register(SurveyAnswerActionsHub)
admin.site.register(AnswerAction)
