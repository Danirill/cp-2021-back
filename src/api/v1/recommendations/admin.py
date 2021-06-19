from datetime import datetime, timedelta

from django.contrib import admin
from django.http import HttpResponseRedirect

from utils.utils import get_token
from .models import Recommendation, RecommendationDetailed, RecommendationPosition

# Register your models here.
from ..orders.models import Promoaction, Promocode
from ..worksheets.BuyingForms.tasks import send_recommendation, send_promocode

admin.site.register(RecommendationDetailed)
admin.site.register(RecommendationPosition)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    change_form_template = "optional_actions_in_recommendations.html"
    def response_change(self, request, obj):
        if "_send_email" in request.POST:
            if obj.user:
                send_recommendation(obj.user.id, obj.get_link())
                self.message_user(request, "Письмо с рекомендацией отправлено")
            else:
                self.message_user(request, "Письмо с рекомендацией не отправлено - пользователь пустой")
            return HttpResponseRedirect(".")
        if "_send_promocode" in request.POST:
            if obj.user:
                hello_promoaction = Promoaction.objects.get_or_create(name='Vitamins_First_Survey',
                                                                      defaults={
                                                                          "name": "Vitamins_First_Survey",
                                                                          "absolute_discount": 0,
                                                                          "relative_discount": 15,
                                                                          "use_absolute_discount": False
                                                                      })[0]
                promocode_data = {
                    "start_time": datetime.now(),
                    "end_time": datetime.now() + timedelta(days=2),
                    "is_active": True,
                    "token": get_token(4, only_digits=True),
                    "usage_limit": 1,
                    "has_usage_limit": True,
                    "has_time_limit": True,
                    "action": hello_promoaction
                }
                promocode = Promocode.objects.create(**promocode_data)
                send_promocode.apply_async(args=[obj.user.id, promocode.id, obj.get_link()], eta=datetime.now())
                self.message_user(request, "Письмо с промокодом отправлено")
            else:
                self.message_user(request, "Письмо с промокодом не отправлено - пользователь пустой")
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
