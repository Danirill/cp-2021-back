from datetime import datetime

import pytz
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from itertools import chain

from WellbeApi import settings
from api.v1.external_api.sms import send_sms_message
from api.v1.external_api.telegrambot import send_message, send_message_html
from api.v1.payments.models import Payment
from api.v1.payments.serializers import PaymentSerializer
from api.v1.products.models import Product
from api.v1.worksheets.BuyingForms.CheckUp.serializers import CheckupBookingFormSerializer
from api.v1.worksheets.BuyingForms.Vitamins.serializers import VitaminsFormSerializer
from api.v1.worksheets.BuyingForms.serializers import FormSerializer
from utils.utils import get_user


class CheckupBookingFormView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = FormSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        form_ser = CheckupBookingFormSerializer(data=ser.validated_data['jsondata'])
        form_ser.is_valid(raise_exception=True)

        user = get_user(request)
        products = Product.objects.filter(uuid=uuid)

        if not products:
            return Response({
                "msg": f"Product with uuid {uuid} does not exists"
            }, status.HTTP_400_BAD_REQUEST)

        product = products[0]
        user = get_user(request)

        payment_data = {
            'is_closed': False,
            'info': ser.validated_data['jsondata'],
            'user': user
        }

        payment = Payment.objects.create(**payment_data)
        payment.products.add(product)
        payment.save()

        if not settings.DEBUG:
            if user.phone:
                send_sms_message(user.phone, f'Ваш счет: {settings.FRONTEND_URL}/pay?token={payment.uuid}')

        payment_link = f"https://{request.META['HTTP_HOST']}{payment.get_admin_url()}"
        send_message(f"Заказ на чекап {payment.id} `{payment_link}`")
        return Response(PaymentSerializer(payment, context={"request": request}).data, status.HTTP_200_OK)






