from rest_framework import generics, permissions
from .models import Note
from .serializers import NoteSerializer

class NoteListCreateView(generics.ListCreateAPIView):
    queryset = Note.objects.all().order_by('-created_at')
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
