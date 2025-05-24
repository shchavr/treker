from rest_framework import serializers

from accounts.serializers import CustomUserSerializer
from .models import WorkItem, Comment, Tag, WorkItemType

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class WorkItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItemType
        fields = ['id', 'name']

class WorkItemSerializer(serializers.ModelSerializer):
    creator = CustomUserSerializer(read_only=True)
    class Meta:
        model = WorkItem
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'created_at']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        validated_data['type'] = WorkItemType.objects.get(id=1)
        return super().create(validated_data)
