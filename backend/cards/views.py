from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Note
from .serializers import NoteSerializer
from projects.models import Project 


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
