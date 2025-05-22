# serializers.py
from rest_framework import serializers
from .models import Project, ProjectMember, RoleProjectMember
from django.contrib.auth import get_user_model
from cards.serializers import CardSerializer

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    class Meta:
        model = Project
        fields = ['id', 'title', 'created_by', 'created_at', 'cards']
        read_only_fields = ['created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        project = super().create(validated_data)
        # Добавляем создателя как участника проекта
        role = RoleProjectMember.objects.get(name='owner')
        ProjectMember.objects.create(user=self.context['request'].user, project=project, role=role)
        return project

class ProjectMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMember
        fields = ['user', 'role']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']
