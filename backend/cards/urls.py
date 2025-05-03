from django.urls import path
from .views import NoteListCreateView

urlpatterns = [

    path('project/<int:project_id>/notes/', NoteListCreateView.as_view(), name='project-notes'),
]
