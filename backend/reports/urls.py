from django.urls import path
from .views import CreatedResolvedGraphView

urlpatterns = [
    path('created-vs-resolved/', CreatedResolvedGraphView.as_view(), name='created-vs-resolved'),
]
