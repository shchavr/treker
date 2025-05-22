from rest_framework.permissions import BasePermission
from projects.models import ProjectMember


class IsProjectMember(BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_id')
        board_id = view.kwargs.get('board_id')

        if project_id:
            return ProjectMember.objects.filter(user=request.user, project_id=project_id).exists()
        if board_id:
            from .models import Card
            try:
                card = Card.objects.get(id=board_id)
                return ProjectMember.objects.filter(user=request.user, project=card.project).exists()
            except Card.DoesNotExist:
                return False

        return True

    def has_object_permission(self, request, view, obj):
        return ProjectMember.objects.filter(user=request.user, project=obj.project).exists()