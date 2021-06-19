from django.db.models import Sum

from .models import Recommendation, RecommendationPosition, RecommendationDetailed
from rest_framework import serializers

from ..products.models import Product
from ..products.serializers import ProductSerializer
from ..users.models import User
from ..users.serializers import UserSerializer
from ..labels.serializers import LabelSerializer
from ..worksheets.BuyingForms.serializers import AnswerActionSerializer


class RecommendationSerializer(serializers.ModelSerializer):
    main_products = ProductSerializer(many=True)
    optional_products = ProductSerializer(many=True)
    labels = LabelSerializer(many=True)
    user = UserSerializer()
    sum = serializers.SerializerMethodField()

    class Meta:
        model = Recommendation
        fields = '__all__'

    def get_sum(self, recommendation):
        return recommendation.main_products.aggregate(Sum('price'))['price__sum']

class RecommendationPositionSerializer(serializers.ModelSerializer):
    actions = AnswerActionSerializer(many=True)
    product = ProductSerializer()

    class Meta:
        model = RecommendationPosition
        fields = '__all__'

class RecommendationDetailedSerializer(serializers.ModelSerializer):
    main_positions = RecommendationPositionSerializer(many=True)
    optional_positions = RecommendationPositionSerializer(many=True)
    labels = LabelSerializer(many=True)
    user = UserSerializer()

    class Meta:
        model = RecommendationDetailed
        fields = '__all__'
