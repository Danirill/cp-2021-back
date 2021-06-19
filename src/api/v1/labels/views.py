from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CreateLabelSerializer
from .serializers import LabelSerializer
from .serializers import LabelEventSerializer, LabelUserSerializer
from ..users.serializers import UserSerializer
from ..events.serializers import EventSerializer
from ..users.models import User
from ..events.models import Event
from .models import Label as LabelModel

class Label(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = CreateLabelSerializer(data=request.data)

        if ser.is_valid(raise_exception=True):
            label = ser.save()
            return Response({
                'details': LabelSerializer(label).data
            },
                status.HTTP_200_OK
            )
        return Response({}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        labels = LabelModel.objects.all()
        return Response({
            'details': LabelSerializer(labels, many=True).data
        },
            status.HTTP_200_OK
        )

class ActionLabels(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, label_id):
        label_ser = LabelSerializer(data=request.data['label_data'], partial=True)
        labels = LabelModel.objects.filter(id=label_id)
        if labels:
            label = labels[0]
            if label_ser.is_valid(raise_exception=True):
                updated_label_ser = LabelSerializer(label, data=request.data['label_data'], partial=True)
                if updated_label_ser.is_valid(raise_exception=True):
                    updated_label = updated_label_ser.save()
                    return Response({
                        'status': status.HTTP_200_OK,
                        'details': LabelSerializer(updated_label).data
                    })
        else:
            return Response({
                'details': 'This label_id is broken or doesn`t exists'
            },
                status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, label_id):
        labels = LabelModel.objects.filter(id=label_id)
        if labels:
            label = labels[0]
            label.delete()
            return Response({
                'status': status.HTTP_200_OK,
                'details': LabelSerializer(label).data
            })
        else:
            return Response({
                'details': 'This label_id is broken or doesn`t exists'
            },
                status.HTTP_400_BAD_REQUEST
            )

    def get(self, request, label_id):
        labels = LabelModel.objects.filter(id=label_id)
        if labels:
            label = labels[0]
            return Response({
                'details': LabelSerializer(label).data
            },
                status.HTTP_200_OK
            )
        else:
            return Response({
                'details': 'This label_id is broken or doesn`t exists'
            },
                status.HTTP_400_BAD_REQUEST
            )

class ActionLabelEvents(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        label_event_ser = LabelEventSerializer(data=request.data)
        if label_event_ser.is_valid(raise_exception=True):
            label = label_event_ser.validated_data['label_id']
            event = label_event_ser.validated_data['event_id']
            event.labels.add(label)
            event.save()
            return Response({
                'details': EventSerializer(event).data
            },
                status.HTTP_200_OK
            )
        return Response({}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        label_event_ser = LabelEventSerializer(data=request.data)
        if label_event_ser.is_valid(raise_exception=True):
            label = label_event_ser.validated_data['label_id']
            event = label_event_ser.validated_data['event_id']
            event.labels.remove(label)
            event.save()
            return Response({
                'details': EventSerializer(event).data
            },
                status.HTTP_200_OK
            )

        return Response({

        },
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class ActionLabelUsers(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        label_event_ser = LabelUserSerializer(data=request.data)
        if label_event_ser.is_valid(raise_exception=True):
            label = label_event_ser.validated_data['label_id']
            user = label_event_ser.validated_data['user_id']
            user.labels.add(label)
            user.save()
            return Response({
                'details': UserSerializer(user).data
            },
                status.HTTP_200_OK
            )
        return Response({}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        label_event_ser = LabelUserSerializer(data=request.data)
        if label_event_ser.is_valid(raise_exception=True):
            label = label_event_ser.validated_data['label_id']
            user = label_event_ser.validated_data['user_id']
            user.labels.remove(label)
            user.save()
            return Response({
                'details': UserSerializer(user).data
            },
                status.HTTP_200_OK
            )
        return Response({

        },
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

