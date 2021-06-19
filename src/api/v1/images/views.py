from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import ListAPIView
import django_filters.rest_framework as filters
from rest_framework.response import Response
from rest_framework.views import APIView
import random

from WellbeApi import settings
from api.v1.images.models import Image
from api.v1.images.serializers import ImageSerializer
from utils.utils import parse_int

class GetImageById(APIView):
    def get(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
            return Response(ImageSerializer(image, context={'request': request}).data, status.HTTP_200_OK)
        except:
            return Response({}, status.HTTP_404_NOT_FOUND)
class GetImageByUUID(APIView):
    def get(self, request, image_uuid):
        try:
            image = Image.objects.get(uuid=image_uuid)
            return Response(ImageSerializer(image, context={'request': request}).data, status.HTTP_200_OK)
        except:
            return Response({}, status.HTTP_404_NOT_FOUND)
