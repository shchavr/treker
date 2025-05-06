from rest_framework import generics, permissions
from .models import Project
from .serializers import ProjectSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Project, ProjectMember, RoleProjectMember
from accounts.models import User
from .serializers import ProjectMemberSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(members__user=self.request.user)
    

def is_project_admin(project, user):
    return ProjectMember.objects.filter(
        project=project, user=user, role__name='admin'
    ).exists()

class ProjectMembersListView(generics.ListAPIView):
    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project = Project.objects.get(id=self.kwargs['project_id'])
        if not project.members.filter(user=self.request.user).exists():
            raise PermissionDenied("Вы не участник проекта.")
        return ProjectMember.objects.filter(project=project)

class AddProjectMemberView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id):
        project = Project.objects.get(id=project_id)
        if not is_project_admin(project, request.user):
            raise PermissionDenied("Только админ может добавлять участников.")

        email = request.data.get('email')
        role_name = request.data.get('role')

        user = User.objects.get(email=email)
        role = RoleProjectMember.objects.get(name=role_name)

        ProjectMember.objects.create(project=project, user=user, role=role)
        return Response({"detail": "Участник добавлен"}, status=status.HTTP_201_CREATED)

class ChangeMemberRoleView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, project_id, user_id):
        project = Project.objects.get(id=project_id)
        if not is_project_admin(project, request.user):
            raise PermissionDenied("Только админ может менять роли.")

        role_name = request.data.get('role')
        role = RoleProjectMember.objects.get(name=role_name)

        member = ProjectMember.objects.get(project=project, user__id=user_id)
        member.role = role
        member.save()

        return Response({"detail": "Роль изменена"}, status=status.HTTP_200_OK)

class RemoveProjectMemberView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, project_id, user_id):
        project = Project.objects.get(id=project_id)
        if not is_project_admin(project, request.user):
            raise PermissionDenied("Только админ может удалять участников.")

        ProjectMember.objects.get(project=project, user__id=user_id).delete()
        return Response({"detail": "Участник удалён"}, status=status.HTTP_204_NO_CONTENT)
