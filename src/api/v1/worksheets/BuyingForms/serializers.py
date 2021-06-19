from rest_framework import serializers

from api.v1.worksheets.BuyingForms.models import Form, AnswerAction


class FormSerializer(serializers.ModelSerializer):
    jsondata = serializers.JSONField(required=True)
    email = serializers.EmailField(required=False, allow_null=True)

    class Meta:
        model = Form
        fields = '__all__'

    def create(self, validated_data):
        form = Form.objects.create(**validated_data)
        form.save()
        return form

class CallRequestSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)

class AnswerActionSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerAction
        fields = '__all__'