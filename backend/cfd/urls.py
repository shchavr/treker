from django.urls import path
from .views import CFDView

urlpatterns = [
    path('', CFDView.as_view(), name='cfd-chart'),
]
