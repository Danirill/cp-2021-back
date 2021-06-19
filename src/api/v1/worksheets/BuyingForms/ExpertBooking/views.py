from datetime import datetime

import pytz
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from itertools import chain

from api.v1.experts.serializers import ProfileSerializer
from api.v1.external_api.sms import send_sms_message
from api.v1.external_api.telegrambot import send_message
from api.v1.labels.serializers import LabelSerializer
from api.v1.payments.models import Payment
from api.v1.payments.serializers import PaymentSerializer
from api.v1.worksheets.BuyingForms.models import Form
from .serializers import ExpertBookingFormSerializer
from ..serializers import FormSerializer

def expert_payment_to_str(payment_data):
    payment_info = payment_data['info']
    name = ''
    phone = ''
    labels_info = ''
    selected_time = ''
    spec = ''
    optional_info = ""

    fields_arr = ["message", "age", "weight", "height", "gender", "email", "date"]

    if payment_info['jsondata']:
        for keyword in fields_arr:
            if keyword in payment_info['jsondata'].keys():
                optional_info += "\n" + keyword + ":  " + str(payment_info['jsondata'][keyword])
    if payment_info['labels']:
        for label in payment_info['labels']:
            labels_info += str(label['label_text']) + ", "
    if payment_info['selected_time']:
        selected_time = f"{payment_info['selected_time']}"
    if payment_info['expert_profile']:
        spec = f"{payment_info['expert_profile']['fnp']}"
    if payment_info['phone']:
        phone = payment_info['phone']
    if payment_info['name']:
        name = payment_info['name']

    return f"{payment_data['id']} \n {labels_info} \n {phone} \n {name} \n {selected_time} \n {spec} \n {optional_info}"


class ExpertBookingFormView(APIView):
    def post(self, request):
        ser = FormSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        form = ser.save(**ser.validated_data)


        form_ser = ExpertBookingFormSerializer(data=ser.validated_data['jsondata'])
        form_ser.is_valid(raise_exception=True)
        if form_ser.validated_data['expert_profile'] and form_ser.validated_data['selected_time']:

            ser.validated_data['jsondata']['expert_profile'] = \
                ProfileSerializer(form_ser.validated_data['expert_profile'], context={'request': request}).data

            ser.validated_data['jsondata']['labels'] = \
                LabelSerializer(form_ser.validated_data['labels'], many=True, context={'request': request}).data

            products = form_ser.validated_data['expert_profile'].products.filter(product_category__id=1)
            if products:
                payment_data = {
                    'is_closed': False,
                    'info': ser.validated_data['jsondata'],
                    'user': None
                }
                payment = Payment.objects.create(**payment_data)
                payment.products.add(products[0])
                payment.save()
                text = expert_payment_to_str(PaymentSerializer(payment).data)

                form.text_representation = text
                send_message(text)
                form.save()
                return Response(PaymentSerializer(payment, context={"request": request}).data, status.HTTP_200_OK)
        return Response({}, status.HTTP_200_OK)

