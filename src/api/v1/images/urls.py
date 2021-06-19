from django.urls import path
from .views import GetImageById, GetImageByUUID

urlpatterns = [
    path('images/<uuid:image_uuid>', GetImageByUUID.as_view()),
    path('images/<int:image_id>', GetImageById.as_view()),
]
