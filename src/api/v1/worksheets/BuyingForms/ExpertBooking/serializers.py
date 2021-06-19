from rest_framework import serializers

from api.v1.experts.models import ExpertProfile
from api.v1.labels.models import Label
from api.v1.worksheets.BuyingForms.models import Form


class ExpertBookingFormSerializer(serializers.Serializer):
    expert_profile = serializers.PrimaryKeyRelatedField(queryset=ExpertProfile.objects.all(),
                                                        required=True,
                                                        allow_null=True)
    labels = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=Label.objects.all()),
                                   required=True,
                                   allow_null=True)
    phone = serializers.CharField(required=True, allow_null=True)
    email = serializers.EmailField(required=True, allow_null=True)
    name = serializers.CharField(required=True, allow_null=True)
    selected_time = serializers.DateTimeField(required=True, allow_null=True)
    jsondata = serializers.JSONField(required=True, allow_null=True)

