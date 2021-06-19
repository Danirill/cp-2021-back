from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from api.v1.images.serializers import ImageSerializer
from api.v1.surveys.models import SurveySession, SurveyPage, SurveyPageAttributes, SurveyAnswer, SurveySessionAnswer, \
    SurveySessionAnswerValue
import logging
from utils.JsonTemplates import render_json

logger = logging.getLogger(__name__)

class SurveyAnswerSerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    class Meta:
        model = SurveyAnswer
        fields = '__all__'

class SurveySessionAnswerSerializer(serializers.ModelSerializer):


    class Meta:
        model = SurveySessionAnswer
        fields = '__all__'

class SurveyPageAttributesSerializer(serializers.ModelSerializer):
    answers = SurveyAnswerSerializer(many=True)
    image = ImageSerializer()
    current_step = serializers.SerializerMethodField()
    steps_count = serializers.SerializerMethodField()

    class Meta:
        model = SurveyPageAttributes
        fields = '__all__'

    def get_steps_count(self, attributes):
        if self.context.get('steps_count'):
            return self.context.get('steps_count')
        session_id = self.context.get('session_id')
        session = SurveySession.objects.get(id=session_id)
        return session.get_steps_count()

    def get_current_step(self, attributes):
        if self.context.get('current_step'):
            return self.context.get('current_step')
        session_id = self.context.get('session_id')
        session = SurveySession.objects.get(id=session_id)
        return session.get_current_step()

class SurveyPageSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = SurveyPage
        fields = '__all__'

    def get_attributes(self, page):
        data = SurveyPageAttributesSerializer(page.attributes, context=self.context).data
        session_id = self.context.get('session_id')
        try:
            session = SurveySession.objects.get(id=session_id)
            session_answers = SurveySessionAnswer.objects.filter(survey_session=session)
            ctx = {}
            for answer in session_answers:
                ctx[answer.key] = answer.value.content
            return render_json(data, ctx)
        except Exception as e:
            print(e)
            return {}




    def get_answers(self, page):
        session_id = self.context.get('session_id')
        session = SurveySession.objects.get(id=session_id)
        session_answers = SurveySessionAnswer.objects.filter(survey_session=session)
        return SurveySessionAnswerSerializer(session_answers, many=True, context=self.context).data



class SurveySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySession
        fields = '__all__'

class DetaliztionTimeSerializer(serializers.Serializer):
    from_time = serializers.DateField(allow_null=True, required=False)
    to_time = serializers.DateField(allow_null=True, required=False)

class SurveySessionAnswerValueSerializer(serializers.ModelSerializer):
    content = serializers.CharField(allow_blank=True)

    class Meta:
        model = SurveySessionAnswerValue
        fields = '__all__'


class SurveySessionAnswerSerializer(serializers.ModelSerializer):
    value = SurveySessionAnswerValueSerializer()

    class Meta:
        model = SurveySessionAnswer
        fields = ('key', 'value')


class SurveySessionAnswerWriterSerializer(serializers.Serializer):
    answers = SurveySessionAnswerSerializer(many=True)
    survey_session_id = serializers.PrimaryKeyRelatedField(queryset=SurveySession.objects.all())


class SurveySessionSimpleSerializer(serializers.Serializer):
    survey_session_id = serializers.PrimaryKeyRelatedField(queryset=SurveySession.objects.all())




