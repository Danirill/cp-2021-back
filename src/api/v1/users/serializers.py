from .models import User, UserToken
from rest_framework import serializers
from ..labels.serializers import LabelSerializer
from django.utils.text import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': _('Token is invalid or expired')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True}, }

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        user.save()
        # AuthToken.objects.create(user)
        return user

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name')

class UserIdSerializer(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

class UserSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'name', 'labels', 'coach', 'is_confirmed',
            'role', 'last_name', 'whatsapp_phone','experts','telegram_tag', 'birthday', 'phone')


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserToken
        fields = ('id', 'confirmation_token', 'reset_password_token', 'user', 'phone_auth_code')

    def create(self, validated_data):
        token = UserToken.objects.create(**validated_data)
        token.save()
        return token


class EmailConfSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserCreationSerializer(serializers.Serializer):
    # Check request for values

    email = serializers.EmailField(required=True)
    name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class UserAutoCreationSerializer(serializers.Serializer):
    # Check request for values
    email = serializers.EmailField(required=True)


class TableRowSerialiser(serializers.Serializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_name = serializers.CharField()
    user_registration_date = serializers.DateTimeField()
    user_phone = serializers.CharField()
    coach_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    coach_name = serializers.CharField()

class UserInfoSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    phone = serializers.CharField(max_length=12, required=False)
    whatsapp_phone = serializers.CharField(max_length=12, required=False)
    telegram_tag = serializers.CharField(max_length=300, required=False)
    birthday = serializers.DateField(required=False)
    last_name = serializers.CharField(required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('email', 'user_id', 'phone', 'whatsapp_phone', 'telegram_tag', 'birthday', 'last_name', 'name')

class UserExpertsSerializerInput(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    experts = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()))

    class Meta:
        model = User
        fields = ('id', 'experts')

class UserExpertsSerializerOutput(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    experts = UserSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'experts')