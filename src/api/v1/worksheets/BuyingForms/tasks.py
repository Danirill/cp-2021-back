from datetime import datetime, timedelta

from babel.dates import get_timezone, format_datetime
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from transliterate import translit

from WellbeApi.celery import app
from api.v1.external_api.sms import send_sms_message
from api.v1.external_api.telegrambot import send_message_html
from api.v1.orders.models import Promocode, Promoaction
from api.v1.users.models import User
from utils.utils import my_translit, get_token
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(ignore_result=True)
def send_recommendation(user_id, recommendation_link):
    user = None

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    user_name_translitted = my_translit(user.name)

    if user.email:
        logger.info('SEND EMAIL')
        ctx = {
            'name': user.name,
            'recommendation_link': recommendation_link + f"&utm_source=recommendation&utm_medium=mail&utm_content={user_name_translitted}&utm_term=rec"
        }

        message = get_template('recommendation_mail_new.html').render(ctx)
        msg = EmailMessage(
            'Рекомендация от Wellbe',
            message,
            'dzykin3@gmail.com',
            [user.email],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    if user.phone:
        try:
            recommendation_link_sms = recommendation_link + f"&utm_source=recommendation&utm_medium=sms&utm_content={user_name_translitted}&utm_term=rec"
            send_sms_message(user.phone, f"Подобранные витамины: {recommendation_link_sms}")
        except Exception:
            print("SMS EXCEPTION IN RECOMMENDATION")

@app.task(ignore_result=True)
def send_promocode(user_id, promocode_id, recommendation_link):
    logger.info('SEND Promocode')
    user = None
    promocode = None
    try:
        user = User.objects.get(pk=user_id)
        promocode = Promocode.objects.get(pk=promocode_id)
    except User.DoesNotExist or Promocode.DoesNotExist:
        return

    end_time = format_datetime(promocode.end_time, "EEE dd.MM HH:mm", tzinfo=get_timezone('Europe/Moscow'), locale='ru')
    remind_time = promocode.end_time - timedelta(hours=2)
    user_name_translitted = my_translit(user.name)
    promoaction_detail = promocode.action.get_discount_str()
    promocode_token = promocode.token

    if user.email:
        ctx = {
            'name': user.name,
            'recommendation_link': recommendation_link + f"&utm_source=recommendation&utm_medium=mail&utm_content={user_name_translitted}&utm_term=15_promo_kod",
            'promocode_finish_date': end_time,
            'promoaction_detail': promoaction_detail,
            'promocode': promocode_token
        }

        message = get_template('recommendation_mail_24hrs_promocode.html').render(ctx)
        msg = EmailMessage(
            'Промокод от Wellbe',
            message,
            'dzykin3@gmail.com',
            [user.email],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    if user.phone:
        try:
            recommendation_link_sms = recommendation_link + f"&utm_source=recommendation&utm_medium=sms&utm_content={user_name_translitted}&utm_term=15_promo_kod"
            send_sms_message(user.phone, f"Wellbe. Дарим скидку {promoaction_detail} по промокоду {promocode_token}"
                                         f" в течении 24 часов. Перейти к рекомендациям {recommendation_link_sms}")
        except Exception:
            print("SMS EXCEPTION IN PROMOSEND")

    send_promocode_remind.apply_async(args=[user.id, promocode.id, recommendation_link], eta=remind_time)

@app.task(ignore_result=True)
def send_promocode_remind(user_id, promocode_id, recommendation_link):
    logger.info('REMIND TRY')
    user = None
    promocode = None
    try:
        user = User.objects.get(pk=user_id)
        promocode = Promocode.objects.get(pk=promocode_id)
    except User.DoesNotExist or Promocode.DoesNotExist:
        return

    end_time = format_datetime(promocode.end_time, "EEE dd.MM HH:mm", tzinfo=get_timezone('Europe/Moscow'), locale='ru')
    user_name_translitted = my_translit(user.name)
    promoaction_detail = promocode.action.get_discount_str()
    promocode_token = promocode.token

    if user.email:
        ctx = {
            'name': user.name,
            'recommendation_link': recommendation_link + f"&utm_source=recommendation&utm_medium=sms&utm_content={user_name_translitted}&utm_term=15_promo_kod_napominanie",
            'promocode_finish_date': end_time,
            'promoaction_detail': promoaction_detail,
            'promocode': promocode_token
        }

        message = get_template('recommendation_mail_46hrs_promocode.html').render(ctx)
        msg = EmailMessage(
            'Промокод от Wellbe',
            message,
            'dzykin3@gmail.com',
            [user.email],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    if user.phone:
        recommendation_link_sms = recommendation_link + f"&utm_source=recommendation&utm_medium=sms&utm_content={user_name_translitted}&utm_term=15_promo_kod_napominanie"
        try:
            send_sms_message(user.phone, f"Wellbe. Напоминаем, что промокод {promocode_token} со скидкой в {promoaction_detail}"
                                         f" истекает {end_time} (время московское) Перейти к рекомендациям {recommendation_link_sms}")
        except Exception:
            print("SMS EXCEPTION IN REMIND")
