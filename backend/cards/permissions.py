from rest_framework.permissions import BasePermission
from projects.models import ProjectMember, Project
from .models import Card, Column  # добавили Column

class IsProjectMember(BasePermission):
    """
    Доступ разрешён, если пользователь:
    - является участником проекта (ProjectMember)
    - или он создал проект (Project.created_by)
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        project_id = view.kwargs.get('project_id')
        board_id = (
                view.kwargs.get('board_id')
                or view.kwargs.get('card_id')
                or view.kwargs.get('pk')
        )

        if project_id:
            return self._is_member_or_owner(request.user, project_id)

        if board_id:
            # Пытаемся сначала найти Card
            try:
                card = Card.objects.select_related('project').get(id=board_id)
                return self._is_member_or_owner(request.user, card.project.id)
            except Card.DoesNotExist:
                pass  # пробуем ниже колонку

            # Если не нашли карточку — пробуем Column
            try:
                column = Column.objects.select_related('card__project').get(id=board_id)
                return self._is_member_or_owner(request.user, column.card.project.id)
            except Column.DoesNotExist:
                return False

        return False

    def has_object_permission(self, request, view, obj):
        return self._is_member_or_owner(request.user, obj.project.id)

    def _is_member_or_owner(self, user, project_id):
        is_member = ProjectMember.objects.filter(user_id=user.id, project_id=project_id).exists()
        is_owner = Project.objects.filter(id=project_id, created_by_id=user.id).exists()
        return is_member or is_owner
