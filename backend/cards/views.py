from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Note, Column
from .serializers import NoteSerializer
from projects.models import Project
from .serializers import ColumnSerializer



class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_project(self):
        try:
            return Project.objects.get(id=self.kwargs['project_id'])
        except Project.DoesNotExist:
            raise PermissionDenied("Проект не найден.")

    def get_queryset(self):
        project = self.get_project()
        if not project.members.filter(user=self.request.user).exists():
            raise PermissionDenied("Вы не участник этого проекта.")
        return Note.objects.filter(project=project).order_by('-created_at')

    def perform_create(self, serializer):
        project = self.get_project()
        if not project.members.filter(user=self.request.user).exists():
            raise PermissionDenied("Вы не участник этого проекта.")
        serializer.save(author=self.request.user, project=project)


class ColumnCreateListView(generics.ListCreateAPIView):
    serializer_class = ColumnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        card_id = self.kwargs['card_id']
        card = Note.objects.get(pk=card_id)
        if card.author != self.request.user:
            raise PermissionDenied("Вы не владелец карточки.")
        return Column.objects.filter(card=card)

    def perform_create(self, serializer):
        card = Note.objects.get(pk=self.kwargs['card_id'])
        if card.author != self.request.user:
            raise PermissionDenied("Вы не владелец карточки.")
        serializer.save(card=card)

class ColumnUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        column = super().get_object()
        if column.card.author != self.request.user:
            raise PermissionDenied("Вы не владелец карточки.")
        return column




class CardListByProjectView(generics.ListAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise PermissionDenied("Проект не найден.")
        
        if not project.members.filter(user=self.request.user).exists():
            raise PermissionDenied("Вы не участник этого проекта.")
        
        return Note.objects.filter(project=project)
