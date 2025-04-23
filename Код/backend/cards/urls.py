from django.urls import path
from .views import NoteListCreateView

urlpatterns = [
    path('', NoteListCreateView.as_view(), name='note-list-create'),
]
