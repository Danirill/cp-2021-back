from django.urls import path
from .views import Recommendations, RecommendationsDetailed

urlpatterns = [
    path('<uuid:uuid>', Recommendations.as_view()),
    path('detailed_recommendation/<uuid:uuid>', RecommendationsDetailed.as_view()),
]



