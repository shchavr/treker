from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project, ProjectMember, RoleProjectMember, ProjectInvite
from .serializers import ProjectSerializer, ProjectMemberSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(members__user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        project = self.get_object()
        members = ProjectMember.objects.filter(project=project)
        data = [
            {
                "user": UserSerializer(m.user).data,
                "role": m.role.name
            }
            for m in members
        ]
        return Response(data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        project = self.get_object()
        user_id = request.data.get('user_id')
        role_id = request.data.get('role_id')
        user = get_object_or_404(User, id=user_id)
        role = get_object_or_404(RoleProjectMember, id=role_id)
        ProjectMember.objects.create(user=user, project=project, role=role)
        return Response({'status': 'member added'})

    @action(detail=True, methods=['put'], url_path='members/(?P<user_id>[^/.]+)/role')
    def change_role(self, request, pk=None, user_id=None):
        project = self.get_object()
        member = get_object_or_404(ProjectMember, project=project, user_id=user_id)
        role_id = request.data.get('role_id')
        role = get_object_or_404(RoleProjectMember, id=role_id)
        member.role = role
        member.save()
        return Response({'status': 'role updated'})

    @action(detail=True, methods=['delete'], url_path='members/(?P<user_id>[^/.]+)')
    def remove_member(self, request, pk=None, user_id=None):
        project = self.get_object()
        ProjectMember.objects.filter(project=project, user_id=user_id).delete()
        return Response({'status': 'member removed'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def generate_invite(self, request, pk=None):
        project = self.get_object()
        invite = ProjectInvite.objects.create(project=project, created_by=request.user)
        return Response({'token': str(invite.token)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_invite(request):
    token = request.data.get('token')

    try:
        invite = ProjectInvite.objects.get(token=token)
    except ProjectInvite.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

    if invite.is_expired:
        return Response({'error': 'Invite link expired'}, status=status.HTTP_400_BAD_REQUEST)

    already_joined = ProjectMember.objects.filter(project=invite.project, user=request.user).exists()
    if already_joined:
        return Response({'status': 'already_member', 'project_id': invite.project.id})

    default_role = RoleProjectMember.objects.get(name='editor')
    ProjectMember.objects.create(project=invite.project, user=request.user, role=default_role)

    return Response({'status': 'joined', 'project_id': invite.project.id})
