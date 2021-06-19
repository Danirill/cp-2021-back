import string
from datetime import datetime, timedelta
from itertools import chain
from random import choice

import translit as translit
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db.models import Q

from api.v1.timetable.models import TimeTable
from api.v1.users.serializers import UserSerializer
from api.v1.users.models import User
from api.v1.labels.models import Label
from django.utils.translation import gettext_lazy as _


def get_broken_label_ids(label_id_array):
    err_label_arr = []
    for label_id in label_id_array:
        events = Label.objects.filter(id=label_id)
        if len(events) == 0:
            err_label_arr.append(label_id)
    return err_label_arr



def validate_password(self, value: str) -> str:
    """
    Hash value passed by user.
    :param value: password of a user
    :return: a hashed version of the password
    """
    return make_password(value)


def get_token(length=15, only_digits=False):
    rand_str = lambda n: ''.join([choice(string.ascii_lowercase) for i in range(n)])
    if only_digits:
        rand_str = lambda n: ''.join([choice(string.digits) for i in range(n)])
    set_id = rand_str(length)
    return set_id

def get_user(request):
    user_id = UserSerializer(request.user).data['id']
    user = User.objects.get(id=user_id)
    return user


def get_user_by_id(user_id):
    user = User.objects.get(id=user_id)
    return user


def get_broken_user_ids(user_id_array):
    err_user_arr = []
    for user_id in user_id_array:
        tags = User.objects.filter(id=user_id)
        if len(tags) == 0:
            err_user_arr.append(user_id)
    return err_user_arr


def get_closest_event(event_set):
    closest = event_set.filter(start_time__gte=datetime.now()).order_by("start_time").first()
    return closest


def get_closest_to_dt_from_two_eventsets(event_set_a, event_set_b, dt):
    event_a = event_set_a.filter(start_time__gte=dt).order_by("start_time").first()
    event_b = event_set_b.filter(start_time__gte=dt).order_by("start_time").first()

    if event_a and event_b:
        return event_a if abs(event_a.start_time - dt) < abs(event_b.start_time - dt) else event_b
    else:
        return event_a or event_b

def parse_int(s, base=10, val=None):
    try:
        a = int(s, base)
        return a
    except:
        return val

def parse_bool(s, val=False):
    try:
        if s.lower() in ['true', '1', 't', 'y', 'yes']:
            return True
        if s.lower() in ['false', '0', 'n', 'no']:
            return False
    except:
        return val

def get_events_by_date(date, user):
    # Get all events in date, linked to this user
    events_slaves = user.event_slaves.filter(Q(start_time__date=date))
    events_master = user.event_master.filter(Q(start_time__date=date))
    result_list = list(set(list(chain(events_slaves, events_master))))
    return result_list

def time_to_tz_naive(t, tz_in, tz_out):
    return tz_in.localize(datetime.combine(datetime.today(), t)).astimezone(tz_out).time()

def string_is_equal(string1, string2):
    import hashlib
    print("HASH")
    hash1 = int(hashlib.sha256(string1.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    hash2 = int(hashlib.sha256(string2.encode('utf-8')).hexdigest(), 16) % 10 ** 8
    print(hash1)
    print(hash2)
    return hash1 == hash2

class PromocodeTokenNotValid(Exception):

    pass

def my_translit(text):

    text = text.strip()
    try:
        text = translit(text, reversed=True)
    except:
        print('Translit false')
    text = "".join(e for e in text if e.isalnum())
    return text

def validate_positive(value):
    if value < 0:
        raise ValidationError(
            _('%(value)s is not an even number'),
            params={'value': value},
        )

