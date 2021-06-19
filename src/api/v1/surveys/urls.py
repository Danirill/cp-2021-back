from django.urls import path
# from .views import
from api.v1.surveys.views import SurveyController, TestView, SurveySessionBackView, \
    SurveySessionDefaultBackView, SurveySessionCurrentView, SurveySessionNextView, SurveySessionDefaultSaveBackView, \
    SurveyGetDetalization, SurveysDetalization

urlpatterns = [
    path('survey/test', TestView.as_view()),
    path('survey/<uuid:uuid>/detalization', SurveysDetalization.as_view()),
    path('survey/<uuid:uuid>', SurveyController.as_view()),
    path('session/<int:session_id>/next', SurveySessionNextView.as_view()),
    path('session/<int:session_id>/return', SurveySessionDefaultBackView.as_view()),
    path('session/<int:session_id>/return_with_save', SurveySessionDefaultSaveBackView.as_view()),
    path('session/<int:session_id>/detalization', SurveyGetDetalization.as_view()),
    path('session/<int:session_id>/current', SurveySessionCurrentView.as_view()),
]
