from django.urls import path

from api.v1.worksheets.BuyingForms.CheckUp.views import CheckupBookingFormView
from api.v1.worksheets.BuyingForms.ExpertBooking.views import ExpertBookingFormView
from api.v1.worksheets.BuyingForms.Vitamins.views import VitaminsBookingFormView, NewVitaminsBookingFormView, \
    SurveyGetRecommendations, SurveyGetRecommendationsSimple
from api.v1.worksheets.BuyingForms.views import GetData, BackCallRequest

urlpatterns = [
    path('expert_booking', ExpertBookingFormView.as_view()),
    path('checkup_booking', CheckupBookingFormView.as_view()),
    path('vitamins/new', NewVitaminsBookingFormView.as_view()),
    path('vitamins', VitaminsBookingFormView.as_view()),
    path('all_data', GetData.as_view()),
    path('call_request', BackCallRequest.as_view()),
    path('recommendation', SurveyGetRecommendations.as_view()),
    path('simple_recommendation', SurveyGetRecommendationsSimple.as_view())
]
