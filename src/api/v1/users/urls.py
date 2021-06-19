from django.urls import path
from .views import CheckEmail, RegistrateUser, ConfirmEmail, UserView, UserInfoView, \
    ResetPassword, RequestResetPassword, RequestConfirmationEmail, LogoutView, TableView, ExpertsView, \
    AutoRegistrateUser
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/sign_up/check_email/', CheckEmail.as_view()),
    path('auth/sign_up/me/', RegistrateUser.as_view()),
    path('auth/sign_up/auto/', AutoRegistrateUser.as_view()),
    path('auth/sign_up/confirm_email/<str:token>', ConfirmEmail.as_view()),
    path('auth/sign_up/confirm_email/', RequestConfirmationEmail.as_view()),
    path('auth/sign_in/', TokenObtainPairView.as_view()),
    path('auth/reset_password', RequestResetPassword.as_view()),
    path('auth/reset_password/<str:reset_token>', ResetPassword.as_view()),
    path('auth/sign_in/refresh', TokenRefreshView.as_view()),
    path('auth/me', UserView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('info/<int:user_id>', UserInfoView.as_view()),
    path('info/table', TableView.as_view()),
    path('<int:user_id>/experts', ExpertsView.as_view()),
]



