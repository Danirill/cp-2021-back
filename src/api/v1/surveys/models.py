import uuid as uuid

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from api.v1.images.models import Image
from api.v1.users.models import User


class SurveyCondition(models.Model):
    key = models.CharField(max_length=1000)
    value = models.CharField(max_length=1000)

    class Relations(models.TextChoices):
        EQUALS = '==='
        NOT_EQUALS = '!='

    relation = models.CharField(
        max_length=10,
        choices=Relations.choices,
        default=Relations.EQUALS,
    )

    actions = {
        '===': lambda x, y: x == y,
        '!=': lambda x, y: x != y
    }

    def execute(self, answers):
        try:
            answer = answers.get(key=self.key)
            result = self.actions[self.relation](answer.value.content, self.value)
            return result
        except SurveySessionAnswer.DoesNotExist:
            return False
        except KeyError:
            return False

    def __str__(self):
        return f"{self.key} {self.relation} {self.value}"


class SurveyAnswer(models.Model):
    key = models.CharField(blank=False, max_length=3000)
    value = models.CharField(blank=True, null=False, default="", max_length=4000)
    text = models.CharField(blank=True, default='', null=False, max_length=4000)
    title = models.CharField(blank=True, default='', null=False, max_length=4000)
    second_hint = models.CharField(blank=True, default='', null=False, max_length=4000)
    hint = models.CharField(blank=True, default='Ваш ответ', null=False, max_length=3000)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.key} : {self.value}"


class SurveyPageAttributes(models.Model):
    name = models.CharField(max_length=300)

    class PageTypes(models.TextChoices):
        PROLOGUE = 'PROLOGUE'
        # EPILOGUE = 'EPILOGUE'
        CHECKBOXES = 'CHECKBOXES'
        RADIOBUTTONS = 'RADIOBUTTONS'
        CHECKBOXES_IMAGE = 'CHECKBOXES_IMAGE'
        RADIOBUTTONS_IMAGE = 'RADIOBUTTONS_IMAGE'
        INPUT_TEXT = 'INPUT_TEXT'
        INPUT_NUMBER = 'INPUT_NUMBER'
        INPUT_PHONE = 'INPUT_PHONE'
        INPUT_EMAIL = 'INPUT_EMAIL'
        PHONE_VERIFICATION = 'PHONE_VERIFICATION'

    type = models.CharField(
        max_length=100,
        choices=PageTypes.choices,
        default=PageTypes.PROLOGUE,
        null=False,
        blank=False
    )
    answers = models.ManyToManyField(SurveyAnswer, blank=False)
    use_answers_counter = models.BooleanField(default=False, blank=False)

    def clean(self):
        if self.minimum_answers_count > self.answers.count().real:
            raise ValidationError(_('minimum_answers_count greater then answers count'))
        if self.maximum_answers_count > self.answers.count().real:
            raise ValidationError(_('maximum_answers_count greater then answers count'))
        if self.maximum_answers_count < self.minimum_answers_count:
            raise ValidationError(_('maximum_answers_count less then minimum_answers_count'))

    minimum_answers_count = models.IntegerField(default=0, blank=False, null=False, validators=[
        MinValueValidator(0)
    ])
    maximum_answers_count = models.IntegerField(default=0, blank=False, null=False, validators=[
        MinValueValidator(0)
    ])
    title = models.CharField(blank=False, max_length=1000)
    description = models.TextField(blank=True)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True)
    render_return_button = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class SurveyPage(models.Model):
    name = models.CharField(max_length=300)
    attributes = models.OneToOneField(SurveyPageAttributes, on_delete=models.PROTECT)
    render_conditions = models.ManyToManyField(SurveyCondition, blank=True)
    redirect_to = models.ForeignKey('self', null=True, on_delete=models.PROTECT, blank=True)

    def check_render(self, survey_session_answers):
        for render_condition in self.render_conditions.all():
            if not render_condition.execute(survey_session_answers):
                return False
        return True

    def get_next_page(self, survey_session_answers):
        if not self.redirect_to:
            return None
        if self.redirect_to.check_render(survey_session_answers):
            return self.redirect_to
        else:
            return self.redirect_to.get_next_page(survey_session_answers)


    def __str__(self):
        return f"{self.name}"


class Survey(models.Model):
    name = models.CharField(max_length=300)
    uuid = models.UUIDField(auto_created=True, default=uuid.uuid4)
    start_survey_page = models.ForeignKey(SurveyPage, null=False, on_delete=models.PROTECT)

    def get_pages(self):
        page_ids = []
        current_page = self.start_survey_page
        while current_page:
            page_ids.append(current_page.id)
            current_page = current_page.redirect_to
        return SurveyPage.objects.filter(id__in=page_ids)

    def __str__(self):
        return f"{self.name}"


class SurveySession(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    current_page = models.ForeignKey(SurveyPage, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def get_current_step(self):
        steps = 1
        current_page = self.survey.start_survey_page
        next_page = current_page.redirect_to
        while current_page != self.current_page and next_page:
            answers = SurveySessionAnswer.objects.filter(survey_session=self)
            if next_page.check_render(answers):
                steps += 1
            current_page = next_page
            next_page = current_page.redirect_to
        return steps

    def get_steps_count(self):
        steps = 1
        STEPS_AFTER_SURVEY = 0
        steps += STEPS_AFTER_SURVEY
        current_page = self.survey.start_survey_page
        next_page = current_page.redirect_to
        while next_page:
            answers = SurveySessionAnswer.objects.filter(survey_session=self)
            if next_page.check_render(answers):
                steps += 1
            current_page = next_page
            next_page = current_page.redirect_to
        return steps

    def get_steps_info(self):
        steps = 1
        current_step = 1
        flag = True
        STEPS_AFTER_SURVEY = 0
        steps += STEPS_AFTER_SURVEY
        current_page = self.survey.start_survey_page
        next_page = current_page.redirect_to
        while next_page:
            answers = SurveySessionAnswer.objects.filter(survey_session=self)
            if current_page == self.current_page:
                flag = False
            if next_page.check_render(answers):
                if flag and current_page != self.current_page:
                    current_step += 1
                steps += 1
            current_page = next_page
            next_page = current_page.redirect_to
        return current_step, steps

    # def get_current_percent(self):
    #     #ToDo: текущий процент заполнения
    #     return

    def __str__(self):
        return f"{self.survey} {self.user.name if self.user else 'Empty user'}"


class SurveyPageJump(models.Model):
    session = models.ForeignKey(SurveySession, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    initial = models.ForeignKey(SurveyPage, on_delete=models.CASCADE, related_name="initial")
    target = models.ForeignKey(SurveyPage, on_delete=models.CASCADE, related_name="target", null=True)

    def __str__(self):
        return f"{self.session}: from {self.initial} to {self.target}"


class SurveySessionAnswerValue(models.Model):
    content = models.TextField(null=True)

    def __str__(self):
        return f"{self.content}"


class SurveySessionAnswer(models.Model):
    survey_session = models.ForeignKey(SurveySession, on_delete=models.CASCADE)
    key = models.CharField(max_length=1000)
    value = models.OneToOneField(SurveySessionAnswerValue, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.key} : {self.value}"
