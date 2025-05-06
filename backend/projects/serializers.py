from rest_framework import serializers
from .models import Project, ProjectMember
from .models import ProjectMember, RoleProjectMember

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        project = Project.objects.create(created_by=user, **validated_data)
        ProjectMember.objects.create(user=user, project=project)  
        return project

class ProjectMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    role_name = serializers.ReadOnlyField(source='role.name')

    class Meta:
        model = ProjectMember
        fields = ['user_email', 'role_name']