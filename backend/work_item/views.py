from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.db.models import Q

from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import WorkItem, Tag, Comment, WorkItemType, Column, WorkItemHistory, Attachment
from cards.models import Card, Column
from .serializers import (
    WorkItemSerializer,
    CommentSerializer,
    TagSerializer,
    WorkItemTypeSerializer,
    WorkItemHistorySerializer, AttachmentSerializer
)

class WorkItemViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    permission_classes = [IsAuthenticated]
    queryset = WorkItem.objects.all()
    serializer_class = WorkItemSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['title', 'priority', 'type', 'created_at', 'due_date']
    ordering = ['created_at']

    @extend_schema(parameters=[OpenApiParameter("board_id", int, OpenApiParameter.PATH)],
                   responses=WorkItemSerializer(many=True))
    def list(self, request, board_id=None):
        queryset = self.filter_queryset(self.get_queryset().filter(board_id=board_id))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=WorkItemSerializer,
                   responses=WorkItemSerializer,
                   parameters=[OpenApiParameter("board_id", int, OpenApiParameter.PATH)])
    def create(self, request, board_id=None):
        card = get_object_or_404(Card, id=board_id)
        project = card.project

        data = request.data.copy()
        data['board'] = board_id
        data['project'] = project.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(responses=WorkItemSerializer)
    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(request=WorkItemSerializer, responses=WorkItemSerializer)
    def update(self, request, pk=None):
        instance = self.get_object()
        old_column = instance.column

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            updated_instance = serializer.save()
            if 'column' in request.data and updated_instance.column != old_column:
                WorkItemHistory.objects.create(
                    work_item=updated_instance,
                    from_column=old_column,
                    to_column=updated_instance.column,
                    moved_by=request.user
                )
            return Response(self.get_serializer(updated_instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=None)
    def destroy(self, request, pk=None):
        instance = self.get_object()
        instance.delete()
        return Response(status=204)

    @extend_schema(request={'type': 'object', 'properties': {'column_id': {'type': 'integer'}}})
    @action(detail=True, methods=['patch'])
    def move(self, request, pk=None):
        task = self.get_object()
        column_id = request.data.get('column_id')
        if not column_id:
            return Response({'error': 'column_id is required'}, status=400)

        from_column = task.column
        to_column = get_object_or_404(Column, pk=column_id)

        if from_column == to_column:
            return Response({'status': 'already in this column'})

        task.column = to_column
        task.save()

        WorkItemHistory.objects.create(
            work_item=task,
            from_column=from_column,
            to_column=to_column,
            moved_by=request.user
        )

        return Response({'status': 'moved', 'new_column': column_id})

    @extend_schema(request={'type': 'object', 'properties': {'user_id': {'type': 'integer'}}})
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        task = self.get_object()
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
        task.performer_id = user_id
        task.save()
        return Response({'status': 'assigned', 'performer': user_id})

    @extend_schema(request={'type': 'object', 'properties': {'tag_ids': {'type': 'array', 'items': {'type': 'integer'}}}})
    @action(detail=True, methods=['post'])
    def tags(self, request, pk=None):
        task = self.get_object()
        tag_ids = request.data.get('tag_ids', [])
        task.tags.set(tag_ids)
        return Response({'status': 'tags updated'})

    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    @action(detail=True, methods=['post'])
    def comments(self, request, pk=None):
        task = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(work_item=task, user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(responses=CommentSerializer(many=True))
    @action(detail=True, methods=['get'])
    def get_comments(self, request, pk=None):
        task = self.get_object()
        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        item = self.get_object()
        history = item.history.all().order_by('-moved_at')
        serializer = WorkItemHistorySerializer(history, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_tasks(request, board_id):
    queryset = WorkItem.objects.filter(board_id=board_id)

    # Фильтры
    title = request.GET.get('title')
    task_type = request.GET.get('type')
    due_date = request.GET.get('due_date')
    priority = request.GET.get('priority')
    creator = request.GET.get('creator')
    tag = request.GET.get('tag')  # 💡 это и есть "метка"

    if title:
        queryset = queryset.filter(title__icontains=title)

    if task_type:
        queryset = queryset.filter(type_id=task_type)

    if due_date:
        queryset = queryset.filter(due_date=due_date)

    if priority:
        queryset = queryset.filter(priority=priority)

    if creator:
        queryset = queryset.filter(creator_id=creator)

    if tag:
        queryset = queryset.filter(tags__name__icontains=tag).distinct()

    serializer = WorkItemSerializer(queryset, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_tasks(request):
    query = request.GET.get('q', '')
    queryset = WorkItem.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    serializer = WorkItemSerializer(queryset, many=True)
    return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


class WorkItemTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkItemType.objects.all()
    serializer_class = WorkItemTypeSerializer
    permission_classes = [IsAuthenticated]

class AttachmentViewSet(viewsets.ModelViewSet):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
