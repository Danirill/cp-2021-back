from datetime import time, datetime

from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.utils import parse_int, get_user
from .models import Recommendation, RecommendationDetailed
from .serializers import RecommendationSerializer, RecommendationDetailedSerializer
from ..external_api import telegrambot
from ..products.models import ProductCombinations
from ..surveys.models import SurveySessionAnswer
from ..surveys.serializers import SurveySessionSimpleSerializer
from ..worksheets.BuyingForms.models import SurveyAnswerActionsHub, RecommendationLimit


class Recommendations(APIView):
    def get(self, request, uuid):
        recommendations = Recommendation.objects.filter(uuid=uuid)
        if recommendations:
            return Response(RecommendationSerializer(recommendations[0], context={"request": request}).data, status.HTTP_200_OK)
        return Response({}, status.HTTP_404_NOT_FOUND)

class RecommendationsDetailed(APIView):
    def get(self, request, uuid):
        recommendations = RecommendationDetailed.objects.filter(uuid=uuid)
        if recommendations:
            return Response(RecommendationDetailedSerializer(recommendations[0], context={"request": request}).data, status.HTTP_200_OK)
        return Response({}, status.HTTP_404_NOT_FOUND)
