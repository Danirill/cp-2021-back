from django.urls import path
from .views import Label, ActionLabels, ActionLabelEvents, ActionLabelUsers

urlpatterns = [
    path('', Label.as_view()),
    path('label/<int:label_id>', ActionLabels.as_view()),
    path('label/actionlabeluser', ActionLabelUsers.as_view()),
    path('label/actionlabelevent', ActionLabelEvents.as_view())
]
