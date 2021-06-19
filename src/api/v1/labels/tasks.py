from WellbeApi.celery import app
from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail
