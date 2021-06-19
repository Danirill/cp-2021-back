
import collections.abc
import csv
import json
import sys
import os
import re
import types
from string import Template

from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from api.v1.external_api import telegrambot
from WellbeApi import settings
from utils.JsonTemplates import render_json
from utils.utils import get_token, string_is_equal, parse_int
from .models import Survey, SurveySession, SurveyPage, SurveySessionAnswerValue, SurveySessionAnswer, SurveyPageJump, \
    SurveyPageAttributes, SurveyAnswer
from .serializers import SurveySessionSerializer, SurveyPageSerializer, SurveySessionAnswerSerializer, \
    SurveySessionAnswerWriterSerializer, SurveySessionSimpleSerializer, DetaliztionTimeSerializer
from ..external_api.sms import send_sms_message
from ..external_api.telegrambot import send_message
from ..users.models import User, UserToken
from ..users.serializers import CreateUserSerializer, TokenSerializer, UserSerializer




class TestView(APIView):

    def post(self, request):
        from api.v1.external_api.sendpulse import send_test
        send_test()
        return Response({}, status=status.HTTP_200_OK)

class SurveyController(APIView):

    def get(self, request, uuid):
        survey = None
        try:
            survey = Survey.objects.get(uuid=uuid)
        except Survey.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        new_session_data = {
            "survey": survey,
            "user": None,
            "current_page": survey.start_survey_page
        }
        survey_session = SurveySession.objects.create(**new_session_data)
        return Response(SurveySessionSerializer(survey_session).data, status=status.HTTP_200_OK)

class SurveySessionNextView(APIView):

    def post(self, request, session_id):
        request.data['survey_session_id'] = session_id
        ser = SurveySessionAnswerWriterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        session = ser.validated_data['survey_session_id']
        for answer in ser.validated_data['answers']:
            answer_value = SurveySessionAnswerValue.objects.create(**answer['value'])
            SurveySessionAnswer.objects.filter(survey_session=session, key=answer['key']).delete()
            answer_instance = SurveySessionAnswer.objects.create(survey_session=session,
                                                                 key=answer['key'],
                                                                 value=answer_value)

        if session.current_page:
            next_page = session.current_page.get_next_page(SurveySessionAnswer.objects.filter(survey_session=session))
            SurveyPageJump.objects.filter(session=session,
                                          initial=session.current_page).delete()
            SurveyPageJump.objects.create(session=session,
                                          initial=session.current_page,
                                          target=next_page)
            session.current_page = next_page
            session.save()
        current_step, steps_count = session.get_steps_info()
        return Response({
            "is_null": session.current_page is None,
            "page": SurveyPageSerializer(session.current_page, context={
                                                                'request': request,
                                                                'session_id': session_id,
                                                                'current_step': current_step,
                                                                'steps_count': steps_count
            }
                                         ).data
        })

class SurveySessionBackView(APIView):
    def get(self, request, session_id, page_id):
        if SurveySession.objects.filter(id=session_id).exists():
            session = SurveySession.objects.get(id=session_id)
            if SurveyPage.objects.filter(id=page_id).exists():
                page = SurveyPage.objects.get(id=page_id)
                if SurveyPageJump.objects.filter(session=session, target=page).exists():
                    jump = SurveyPageJump.objects.filter(session=session, target=page)[0]
                    session.current_page = jump.initial
                    session.save()
                    current_step, steps_count = session.get_steps_info()
                    return Response({
                        "is_null": session.current_page is None,
                        "page": SurveyPageSerializer(session.current_page, context={
                            'request': request,
                            'session_id': session_id,
                            'current_step': current_step,
                            'steps_count': steps_count
                        }
                                                     ).data
                    })
        return Response({}, status=status.HTTP_404_NOT_FOUND)

class SurveySessionDefaultBackView(APIView):
    def get(self, request, session_id):
        data = {
            "survey_session_id": session_id
        }
        ser = SurveySessionSimpleSerializer(data=data)
        ser.is_valid(raise_exception=True)
        session = ser.validated_data['survey_session_id']
        page = session.current_page
        if SurveyPageJump.objects.filter(session=session, target=page).exists():
            jump = SurveyPageJump.objects.filter(session=session, target=page)[0]
            session.current_page = jump.initial
            session.save()

        current_step, steps_count = session.get_steps_info()
        return Response({
            "is_null": session.current_page is None,
            "page": SurveyPageSerializer(session.current_page, context={
                                                                'request': request,
                                                                'session_id': session_id,
                                                                'current_step': current_step,
                                                                'steps_count': steps_count
                                                                }
                                         ).data
        })

class SurveySessionDefaultSaveBackView(APIView):
    def post(self, request, session_id):
        request.data["survey_session_id"] = session_id
        ser = SurveySessionAnswerWriterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        session = ser.validated_data['survey_session_id']
        page = session.current_page

        for answer in ser.validated_data['answers']:
            answer_value = SurveySessionAnswerValue.objects.create(**answer['value'])
            SurveySessionAnswer.objects.filter(survey_session=session, key=answer['key']).delete()
            answer_instance = SurveySessionAnswer.objects.create(survey_session=session,
                                                                 key=answer['key'],
                                                                 value=answer_value)

        if SurveyPageJump.objects.filter(session=session, target=page).exists():
            jump = SurveyPageJump.objects.filter(session=session, target=page)[0]
            session.current_page = jump.initial
            session.save()

        current_step, steps_count = session.get_steps_info()

        return Response({
            "is_null": session.current_page is None,
            "page": SurveyPageSerializer(session.current_page, context={
                'request': request,
                'session_id': session_id,
                'current_step': current_step,
                'steps_count': steps_count
            }
                                         ).data
        })



class SurveySessionCurrentView(APIView):
    def get(self, request, session_id):
        data = {
            "survey_session_id": session_id
        }
        ser = SurveySessionSimpleSerializer(data=data)
        ser.is_valid(raise_exception=True)
        session = ser.validated_data['survey_session_id']
        current_step, steps_count = session.get_steps_info()
        return Response({
            "is_null": session.current_page is None,
            "page": SurveyPageSerializer(session.current_page, context={
                'request': request,
                'session_id': session_id,
                'current_step': current_step,
                'steps_count': steps_count
            }
                                         ).data
        })

class SurveyGetDetalization(APIView):

    def get(self, request, session_id):
        data = {
            "survey_session_id": session_id
        }
        ser = SurveySessionSimpleSerializer(data=data)
        ser.is_valid(raise_exception=True)
        session = ser.validated_data['survey_session_id']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="forms_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['key', 'value'])
        answers = SurveySessionAnswer.objects.filter(survey_session=session)
        for e in answers:
            try:
                writer.writerow([e.key, e.value.content])
            except TypeError:
                print('oops')

        return response

class SurveysDetalization(APIView):

    def get(self, request, uuid):
        survey = None
        try:
            survey = Survey.objects.get(uuid=uuid)
        except Survey.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        ser = DetaliztionTimeSerializer(data={
            "from_time": request.query_params.get('from_time'),
            "to_time": request.query_params.get('to_time')
        })
        ser.is_valid(raise_exception=True)
        from_time = ser.validated_data['from_time']
        to_time = ser.validated_data['to_time']
        all_keys = SurveySessionAnswer.objects.values_list('key', flat=True).distinct()
        sessions = SurveySession.objects.all()

        if from_time:
            sessions = sessions.filter(Q(created_at__gte=from_time))

        if to_time:
            sessions = sessions.filter(Q(created_at__lte=to_time))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="forms_report.csv"'
        writer = csv.writer(response)
        writer.writerow(all_keys)
        default_data = {key: "null" for key in all_keys}
        for session in sessions:
            default_data_copy = dict(default_data)
            answers = SurveySessionAnswer.objects.filter(survey_session=session)
            for answer in answers:
                default_data_copy[answer.key] = answer.value.content
            writer.writerow(default_data_copy.values())
        return response
