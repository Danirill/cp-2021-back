from api.v1.users.serializers import CreateUserSerializer, TokenSerializer
from utils.utils import validate_password, get_token


def create_user_and_tokens(ctx, request):
    temp_data = {
        'name': request.data["name"],
        'email': request.data["email"],
        'password': validate_password(ctx, request.data["password"])
    }
    serializer = CreateUserSerializer(data=temp_data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token_data = {
        'confirmation_token': get_token(),
        'reset_password_token': get_token(),
        'phone_auth_code': get_token(6),
        'user': user.id
    }
    token_serializer = TokenSerializer(data=token_data)
    token_serializer.is_valid(raise_exception=True)
    tokens = token_serializer.save()
    return tokens, user