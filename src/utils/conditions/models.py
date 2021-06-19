from django.db import models

class Condition(models.Model):

    class Relations(models.TextChoices):
        EQUALS = '==='
        NOT_EQUALS = '!='
        MORE = '>'
        MORE_OR_EQUAL = '>='
        LESS = '<'
        LESS_OR_EQUAL = '<='

    relation = models.CharField(
        max_length=10,
        choices=Relations.choices,
        default=Relations.EQUALS,
    )

    actions = {
        '===': lambda x, y: x == y,
        '>': lambda x, y: x > y,
        '<': lambda x, y: x < y,
        '>=': lambda x, y: x >= y,
        '<=': lambda x, y: x <= y,
        '!=': lambda x, y: x != y
    }

    def execute(self, value1, value2):
        return self.actions[self.relation](value1, value2)

    def __str__(self):
        return f"{self.relation}"