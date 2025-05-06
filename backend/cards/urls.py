from django.urls import path
from .views import NoteListCreateView
from .views import ColumnCreateListView, ColumnUpdateDeleteView
from .views import CardListByProjectView

urlpatterns = [
    path('project/<int:project_id>/notes/', NoteListCreateView.as_view(), name='project-notes'),
    path('project/<int:project_id>/cards/', CardListByProjectView.as_view(), name='project-cards'),
    path('cards/<int:card_id>/columns/', ColumnCreateListView.as_view(), name='column-list-create'),
    path('columns/<int:pk>/', ColumnUpdateDeleteView.as_view(), name='column-detail'),
]
