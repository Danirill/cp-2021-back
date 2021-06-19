from django.http import HttpResponse
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import csv

from api.v1.external_api.telegrambot import send_message
from api.v1.worksheets.BuyingForms.models import Form
from api.v1.worksheets.BuyingForms.serializers import CallRequestSerializer
from utils.utils import get_user


class GetData(APIView):

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="forms_report.csv"'

        writer = csv.writer(response)
        forms = Form.objects.all()
        writer.writerow(['age','city','drug','name','height','weight','operations','specialists'])
        for e in forms:
            jsondata = e.jsondata
            if not 'jsondata' in jsondata:
                continue
            try:
                jsondata = jsondata['jsondata']
                age = ""
                if 'age' in jsondata:
                    age = jsondata['age']
                city = ""
                if 'city' in jsondata:
                    city = jsondata['city']
                drug = ""
                if 'drug' in jsondata:
                    drug = jsondata['drug']
                name = ""
                if 'name' in jsondata:
                    name = jsondata['name']
                height = ""
                if 'height' in jsondata:
                    height = jsondata['height']
                weight = ""
                if 'weight' in jsondata:
                    weight = jsondata['weight']
                operations = ""
                if 'operations' in jsondata:
                    operations = jsondata['operations']
                specialists = ""
                if 'specialists' in jsondata:
                    specialists = jsondata['specialists']
                writer.writerow([age, city, drug, name, height, weight, operations, specialists])
            except TypeError:
                print('oops')

        return response

class BackCallRequest(APIView):

    def post(self, request):
        ser = CallRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        phone = ser.validated_data['phone'].replace("-", "").replace("(", "").replace(")", "").replace(" ", "").replace("+", "")
        name = ser.validated_data['name'].replace("-", "").replace("(", "").replace(")", "").replace(" ", "").replace("+", "")

        str = f"{name} с номером {phone} ожидает звонка"
        send_message(str)
        return Response({}, status.HTTP_200_OK)

