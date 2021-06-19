from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from WellbeApi import settings
from .user_utils import create_user_and_tokens
from ..users.models import UserToken, User, Role
from .serializers import CreateUserSerializer, TokenSerializer, UserSerializer, EmailConfSerializer, \
    UserCreationSerializer, RefreshTokenSerializer, UserInfoSerializer, UserExpertsSerializerInput, \
    UserExpertsSerializerOutput, UserAutoCreationSerializer
from .tasks import send_confimation_token, send_reset_password_token, send_auto_registrate_info
from utils.utils import get_token, validate_password, get_user, parse_int, parse_bool


class LogoutView(GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args):
        sz = self.get_serializer(data=request.data)
        sz.is_valid(raise_exception=True)
        sz.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Create your views here.
class CheckEmail(APIView):

    def post(self, request):
        ser = EmailConfSerializer(data=request.data)
        if ser.is_valid(raise_exception=True):
            user = get_user_model()
            if user.objects.filter(email=request.data['email']):
                return Response({
                    'details': 'Email is already used'
                }, status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'details': 'Email not already used'
                }, status.HTTP_202_ACCEPTED)
        else:
            return Response({
                'details': 'Email must be in request'
            }, status.HTTP_400_BAD_REQUEST)

class AutoRegistrateUser(APIView):

    def post(self, request):
        ser = UserAutoCreationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        redirect_url = self.request.query_params.get('redirect_url')
        password = get_token(6)
        request.data['name'] = request.data['email']
        request.data['password'] = password
        tokens, user = create_user_and_tokens(self, request)
        user.is_confirmed = True
        user.save()

        if redirect_url:
            send_auto_registrate_info(email=user.email, name=user.name,
                                   url=f'https://{redirect_url}', password=password)
        else:
            send_auto_registrate_info(email=user.email, name=user.name,
                        url=f'{settings.FRONTEND_URL}', password=password)

        return Response({
            'details': 'User successfully created',
            'redirect_url': redirect_url
        }, status.HTTP_201_CREATED)


class RegistrateUser(APIView):

    def post(self, request):
        ser = UserCreationSerializer(data=request.data)
        if ser.is_valid(raise_exception=True):
            redirect_url = self.request.query_params.get('redirect_url')
            tokens, user = create_user_and_tokens(self, request)

            if redirect_url:
                send_confimation_token(email=user.email, name=user.name,
                                       token_link=f'https://{redirect_url}/confirm_email/?token={tokens.confirmation_token}')
            else:
                send_confimation_token(email=user.email, name=user.name,
                            token_link=f'{settings.FRONTEND_URL}/confirm_email/?token={tokens.confirmation_token}')

            return Response({
                'details': 'User successfully created',
                'redirect_url': redirect_url
            }, status.HTTP_201_CREATED)
        else:
            return Response({
                'details': 'Name, email and password must be in request'
            }, status.HTTP_400_BAD_REQUEST)

class UserView(RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = User
    serializer_class = UserSerializer

    def retrieve(self, request):
        if request.user:
            return Response(UserSerializer(request.user).data)
        return super(UserView, self).retrieve(request)


class ExpertsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        users = User.objects.filter(id=user_id)
        if users:
            return Response(UserExpertsSerializerOutput(users[0]).data)

    def post(self, request,user_id):
        request.data['id'] = user_id
        experts_ser = UserExpertsSerializerInput(data=request.data)
        experts_ser.is_valid(raise_exception=True)
        user = experts_ser.validated_data['id']
        user.experts.add(*experts_ser.validated_data['experts'])
        user.save()
        return Response(UserExpertsSerializerOutput(user).data)

    def put(self, request, user_id):
        request.data['id'] = user_id
        experts_ser = UserExpertsSerializerInput(data=request.data)
        experts_ser.is_valid(raise_exception=True)
        user = experts_ser.validated_data['id']
        user.experts.clear()
        user.experts.add(*experts_ser.validated_data['experts'])
        user.save()
        return Response(UserExpertsSerializerOutput(user).data)

    def delete(self, request, user_id):
        request.data['id'] = user_id
        experts_ser = UserExpertsSerializerInput(data=request.data)
        experts_ser.is_valid(raise_exception=True)
        user = experts_ser.validated_data['id']
        user.experts.remove(*experts_ser.validated_data['experts'])
        user.save()
        return Response(UserExpertsSerializerOutput(user).data)


class UserInfoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, user_id):
        users = User.objects.filter(id=user_id)
        if users:
            user = users[0]
            return Response(UserSerializer(user).data)
        else:
            return Response({
                'details': 'This label_id is broken or doesn`t exists'
            },
                status.HTTP_400_BAD_REQUEST
            )

    def patch(self, request, user_id):
        request.data['user_id'] = user_id
        serializer = UserInfoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user_id']
        updated_user_ser = UserInfoSerializer(user, data=request.data, partial=False)
        if updated_user_ser.is_valid(raise_exception=True):
            updated_user = updated_user_ser.save()
            return Response({
                'details': UserSerializer(updated_user).data
            }, status.HTTP_200_OK)

class ConfirmEmail(APIView):

    def get(self, request, token):
        token_model = UserToken.objects.filter(confirmation_token=token)
        if token_model:
            user = token_model[0].user
            user.is_confirmed = True
            user.auth_provider = 'email'
            user.save()
            return Response({
                'details': 'Email confirmed'
            }, status.HTTP_200_OK)
        else:
            return Response({
                'details': 'Bad token'
            }, status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):

    def post(self, request, reset_token):
        if request.data['password']:
            users_tokens = UserToken.objects.filter(reset_password_token=reset_token)
            if users_tokens:
                user_tokens = users_tokens[0]
                user = user_tokens.user
                user.set_password(request.data['password'])
                user.save()
                token_data = {
                    'reset_password_token': get_token(),
                    'user': user.id
                }
                token_serializer = TokenSerializer(data=token_data, partial=True)
                token_serializer.is_valid(raise_exception=True)
                token_serializer.save()
                return Response({}, status.HTTP_200_OK)

        return Response({

        }, status.HTTP_400_BAD_REQUEST)


class RequestResetPassword(APIView):
    def post(self, request):
        if request.data['email']:
            users = User.objects.filter(email=request.data['email'])
            if users:
                user = users[0]
                user_tokens = UserToken.objects.filter(user=user)[0]
                redirect_url = self.request.query_params.get('redirect_url')


                if redirect_url:
                    reset_password_url = f'https://{redirect_url}/create_password/?token={user_tokens.reset_password_token}'
                else:
                    reset_password_url = f'{settings.FRONTEND_URL}/create_password/?token={user_tokens.reset_password_token}'

                send_reset_password_token(user.email, user.name, reset_password_url)
                return Response({

                }, status.HTTP_200_OK)
        return Response({
            'details': 'Bad email'
        }, status.HTTP_400_BAD_REQUEST)


class RequestConfirmationEmail(APIView):
    def post(self, request):
        if request.data['email']:
            users = User.objects.filter(email=request.data['email'])
            if users:
                user = users[0]
                user_tokens = UserToken.objects.filter(user=user)[0]
                redirect_url = self.request.query_params.get('redirect_url')

                if redirect_url:
                    send_confimation_token(email=user.email, name=user.name,
                                           token_link=f'https://{redirect_url}/confirm_email/?token={user_tokens.confirmation_token}')
                else:
                    send_confimation_token(email=user.email, name=user.name,
                                           token_link=f'{settings.FRONTEND_URL}/confirm_email/?token={user_tokens.confirmation_token}')

                return Response({

                }, status.HTTP_200_OK)
        return Response({
            'details': 'Bad email'
        }, status.HTTP_400_BAD_REQUEST)

class TableView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request,):
        user = get_user(request)

        if not user.role.is_couch:
            return Response({"User": "Role must have is_couch:true"
                }, status.HTTP_403_FORBIDDEN)

        page = parse_int(s=self.request.query_params.get('page'), val=1)
        role_id = parse_int(s=self.request.query_params.get('role_id'), val=0)
        limit = parse_int(s=self.request.query_params.get('limit'), val=50)
        only_my_clients = parse_bool(self.request.query_params.get('only_my_clients'), val=True)
        expert_id = parse_int(s=self.request.query_params.get('expert_id'), val=0)
        coach_id = parse_int(s=self.request.query_params.get('coach_id'), val=0)
        query = self.request.query_params.get('q')

        users = User.objects.all()
        if role_id:
            users = users.filter(
                Q(role__id=role_id)
            )

        if only_my_clients:
            users = users.filter(
                Q(coach=user) or
                Q(experts__id=user.id)
            )

        if expert_id:
            users = users.filter(
                Q(experts__id=expert_id)
            )

        if coach_id:
            users = users.filter(
                Q(coach__id=coach_id)
            )

        if query:
            users = users.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query)
            ).distinct()



        paginator = Paginator(users, limit)
        user_set = []

        try:
            rows = paginator.page(page)
        except EmptyPage:
            rows = paginator.page(paginator.num_pages)

        for current_user in rows:
            row = {
                "user_id": current_user.id,
                "user_name":current_user.name,
                "user_email": current_user.email,
                "user_registration_date":current_user.created_at,
                "user_phone":current_user.phone,
                "coach_id": current_user.coach.id if current_user.coach else '',
                "coach_name": current_user.coach.name if current_user.coach else '',
                "role": current_user.role.name_of_role,
                "role_id": current_user.role.id,
                "experts": UserExpertsSerializerOutput(current_user).data['experts']
            }
            user_set.append(row)

        return Response({
            "results": len(users),
            "num_pages": paginator.num_pages,
            "role_id": role_id,
            "page": page,
            "limit": limit,
            "only_my_clients": only_my_clients,
            "q": query,
            "data": user_set
        }, status.HTTP_200_OK)


