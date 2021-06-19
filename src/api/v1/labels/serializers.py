from rest_framework import serializers
from .models import Label
from ..events.models import Event
from ..images.serializers import ImageSerializer
from ..users.models import User


class CreateLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ('label_text', 'color', 'hidden_for_client')

    def create(self, validated_data):
        label = Label.objects.create(**validated_data)
        label.save()
        return label

class LabelSerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    class Meta:
        model = Label
        fields = '__all__'

class LabelEventSerializer(serializers.Serializer):
    event_id = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    label_id = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all())


class LabelUserSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    label_id = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all())

class LabelIdSerializer(serializers.Serializer):
    label_id = serializers.PrimaryKeyRelatedField(queryset=Label.objects.all())

