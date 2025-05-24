from django.urls import path
from .views import CreatedResolvedGraphView  # и позже CFDView

urlpatterns = [
    path('created-vs-resolved/', CreatedResolvedGraphView.as_view(), name='created-vs-resolved'),
    # path('cfd/', CFDView.as_view(), name='cfd') — добавим позже
]
