from rest_framework import serializers
from .models import Note
from .models import Column

class NoteSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')  
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Note
        fields = ['id', 'author', 'project', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'project', 'created_at']

class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ['id', 'card', 'name', 'position', 'limit_work_item']
        read_only_fields = ['id', 'card'] 
