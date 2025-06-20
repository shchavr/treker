from rest_framework import serializers

from accounts.serializers import CustomUserSerializer
from .models import WorkItem, Comment, Tag, WorkItemType, WorkItemHistory, Attachment


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'name', 'uploaded_at', 'uploaded_by']
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']


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
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True,
        source='tags'
    )
    attachments = AttachmentSerializer(many=True, read_only=True)
    attachment_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Attachment.objects.all(),
        write_only=True,
        source='attachments'
    )

    class Meta:
        model = WorkItem
        fields = '__all__'
        read_only_fields = ['id', 'creator', 'created_at']

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        validated_data['type'] = WorkItemType.objects.get(id=1)
        return super().create(validated_data)

# work_item/serializers.py

class WorkItemHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkItemHistory
        fields = ['id', 'work_item', 'from_column', 'to_column', 'moved_at', 'moved_by']