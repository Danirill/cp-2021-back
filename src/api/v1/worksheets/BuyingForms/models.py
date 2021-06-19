import uuid

from django.db import models

# Create your models here.
from django.db import models
from api.v1.products.models import Product

## DEPRECATED
from api.v1.surveys.models import SurveyCondition
from utils.conditions.models import Condition


class Form(models.Model):

    jsondata = models.JSONField(null=True, blank=True)
    text_representation = models.JSONField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Form {self.text_representation}'


class RecommendationLimit(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, null=True, blank=False)
    main_limit = models.IntegerField(null=False)
    optional_limit = models.IntegerField(null=False)

    def __str__(self):
        return f'{self.product.product_name}, Limit: {self.main_limit}'


## DEPRECATED
class AnswerScore(models.Model):
    recommendation_limit = models.ForeignKey(RecommendationLimit, null=True, on_delete=models.CASCADE)
    score = models.IntegerField(null=False)

    def __str__(self):
        return f'{self.recommendation_limit.product.product_name}, Score: {self.score}'


## DEPRECATED
class FormAnswer(models.Model):
    name = models.TextField(max_length=1000)
    code = models.IntegerField(unique=True)
    answer_scores = models.ManyToManyField(AnswerScore, blank=True)

    def __str__(self):
        return f'{self.name}, code: {self.code}'


class AnswerAction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(null=False)
    title = models.CharField(null=True, blank=True, max_length=1000)
    text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.product.product_name if self.product else ""}, Score: {self.score},' \
               f' Text: {self.text if self.text else "empty"}'


class SurveyAnswerActionsHub(models.Model):
    key = models.CharField(max_length=1000, null=False)
    value = models.TextField(default="empty", null=False)
    answer_actions = models.ManyToManyField(AnswerAction, blank=True)
    condition = models.ForeignKey(Condition, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.key}, value: {self.value}'





