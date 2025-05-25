from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import WorkItem, Tag, Comment, WorkItemType
from cards.models import Card, Column
from .serializers import WorkItemSerializer, CommentSerializer, TagSerializer, WorkItemTypeSerializer
from .serializers import WorkItemSerializer, WorkItemHistorySerializer  # если используешь history endpoint
from .models import Column, WorkItemHistory

class WorkItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[OpenApiParameter("board_id", int, OpenApiParameter.PATH)],
        responses=WorkItemSerializer(many=True)
    )
    def list(self, request, board_id=None):
        items = WorkItem.objects.filter(board_id=board_id)
        serializer = WorkItemSerializer(items, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=WorkItemSerializer,
        responses=WorkItemSerializer,
        parameters=[OpenApiParameter("board_id", int, OpenApiParameter.PATH)]
    )
    def create(self, request, board_id=None):
        card = get_object_or_404(Card, id=board_id)
        project = card.project

        data = request.data.copy()
        data['board'] = board_id
        data['project'] = project.id

        serializer = WorkItemSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(responses=WorkItemSerializer)
    def retrieve(self, request, pk=None):
        task = get_object_or_404(WorkItem, pk=pk)
        serializer = WorkItemSerializer(task)
        return Response(serializer.data)

    @extend_schema(request=WorkItemSerializer, responses=WorkItemSerializer)
    def update(self, request, pk=None):
        task = get_object_or_404(WorkItem, pk=pk)
        serializer = WorkItemSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    @extend_schema(responses=None)
    def destroy(self, request, pk=None):
        task = get_object_or_404(WorkItem, pk=pk)
        task.delete()
        return Response(status=204)

    @extend_schema(
        request={'type': 'object', 'properties': {'column_id': {'type': 'integer'}}}
    )

    @action(detail=True, methods=['patch'])
    def move(self, request, pk=None):
        task = get_object_or_404(WorkItem, pk=pk)
        column_id = request.data.get('column_id')
        if not column_id:
            return Response({'error': 'column_id is required'}, status=400)

        from_column = task.column
        to_column = get_object_or_404(Column, pk=column_id)

        if from_column == to_column:
            return Response({'status': 'already in this column'})

        task.column = to_column
        task.save()

        # Создание записи в истории
        WorkItemHistory.objects.create(
            work_item=task,
            from_column=from_column,
            to_column=to_column,
            moved_by=request.user
        )

        return Response({'status': 'moved', 'new_column': column_id})


    @extend_schema(
        request={'type': 'object', 'properties': {'user_id': {'type': 'integer'}}}
    )
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        task = get_object_or_404(WorkItem, pk=pk)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)
        task.performer_id = user_id
        task.save()
        return Response({'status': 'assigned', 'performer': user_id})

    @extend_schema(
        request={'type': 'object', 'properties': {'tag_ids': {'type': 'array', 'items': {'type': 'integer'}}}}
    )
    @action(detail=True, methods=['post'])
    def tags(self, request, pk=None):
        task = get_object_or_404(WorkItem, pk=pk)
        tag_ids = request.data.get('tag_ids', [])
        task.tags.set(tag_ids)
        return Response({'status': 'tags updated'})

    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    @action(detail=True, methods=['post'])
    def comments(self, request, pk=None):
        task = get_object_or_404(WorkItem, pk=pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(work_item=task, user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @extend_schema(responses=CommentSerializer(many=True))
    @action(detail=True, methods=['get'])
    def get_comments(self, request, pk=None):
        task = get_object_or_404(WorkItem, pk=pk)
        comments = task.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    

    # work_item/views.py

    def update(self, request, pk=None):
        instance = get_object_or_404(WorkItem, id=pk)
        old_column = instance.column

        serializer = WorkItemSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            updated_instance = serializer.save()
            if 'column' in request.data and updated_instance.column != old_column:
                WorkItemHistory.objects.create(
                    work_item=updated_instance,
                    from_column=old_column,
                    to_column=updated_instance.column
                )
            return Response(WorkItemSerializer(updated_instance).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        item = get_object_or_404(WorkItem, pk=pk)
        history = item.history.all().order_by('-moved_at')
        serializer = WorkItemHistorySerializer(history, many=True)
        return Response(serializer.data)

    



class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

class WorkItemTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkItemType.objects.all()
    serializer_class = WorkItemTypeSerializer
    permission_classes = [IsAuthenticated]


