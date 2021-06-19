from rest_framework import serializers

from api.v1.experts.models import ExpertProfile
from api.v1.labels.models import Label
from api.v1.users.models import User


class CheckupBookingFormSerializer(serializers.Serializer):
    product_uuid = serializers.UUIDField(required=True, allow_null=False)
    email = serializers.EmailField(required=True, allow_null=True)
    name = serializers.CharField(required=True, allow_null=True)
    selected_time = serializers.DateTimeField(required=True, allow_null=True)
    jsondata = serializers.JSONField(required=True, allow_null=True)

