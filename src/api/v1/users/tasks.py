from WellbeApi.celery import app
from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage


@app.task
def send_confimation_token(email, name, token_link):
    ctx = {
        'name': name,
        'token_link': token_link
    }
    message = get_template('registration_confirmation.html').render(ctx)
    msg = EmailMessage(
        'Confirm registration',
        message,
        'dzykin3@gmail.com',
        [email],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

@app.task
def send_reset_password_token(email, name, token_link):
    ctx = {
        'name': name,
        'token_link': token_link
    }
    message = get_template('reset_password.html').render(ctx)
    msg = EmailMessage(
        'Reset password',
        message,
        'dzykin3@gmail.com',
        [email],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()

@app.task
def send_auto_registrate_info(email, name, password, url):
    ctx = {
        'name': name,
        'password': password,
        'url':url
    }
    message = get_template('auto_registration_info.html').render(ctx)
    msg = EmailMessage(
        'Confirm registration',
        message,
        'dzykin3@gmail.com',
        [email],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()