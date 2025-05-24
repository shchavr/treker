from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import get_object_or_404
from .models import Card, Column
from .serializers import CardSerializer, ColumnSerializer
from .permissions import IsProjectMember
from rest_framework.permissions import IsAuthenticated
from projects.models import Project, ProjectMember
from django.db.models import Max


class CardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsProjectMember]

    def list(self, request, project_id=None):
        project = get_object_or_404(Project, id=project_id)
        cards = Card.objects.filter(project=project)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)

    def create(self, request, project_id=None):
        project = get_object_or_404(Project, id=project_id)
        serializer = CardSerializer(data=request.data)

        if serializer.is_valid():
            card = serializer.save(project=project)
            return Response(CardSerializer(card).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        card = get_object_or_404(Card, pk=pk)
        if not ProjectMember.objects.filter(user=request.user, project=card.project).exists():
            return Response({'detail': 'Access denied'}, status=403)
        serializer = CardSerializer(card)
        return Response(serializer.data)


class ColumnViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsProjectMember]

    def create(self, request, card_id=None):
        card = get_object_or_404(Card, id=card_id)

        # Получаем максимальное значение order для этой доски
        max_order = card.columns.aggregate(Max('order'))['order__max'] or 0
        next_order = max_order + 1

        serializer = ColumnSerializer(data=request.data)
        if serializer.is_valid():
            # Устанавливаем card и вычисленный order вручную
            serializer.save(card=card, order=next_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        column = get_object_or_404(Column, id=pk)
        if not ProjectMember.objects.filter(user=request.user, project=column.card.project).exists():
            return Response({'detail': 'Access denied'}, status=403)

        # 🔒 Защита от переименования системной колонки
        new_title = request.data.get('title')
        if column.is_system and new_title and new_title != column.title:
            return Response({'detail': 'Нельзя переименовать системную колонку "Готово"'}, status=400)

        serializer = ColumnSerializer(column, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        column = get_object_or_404(Column, id=pk)
        if not ProjectMember.objects.filter(user=request.user, project=column.card.project).exists():
            return Response({'detail': 'Access denied'}, status=403)

        # 🔒 Защита от удаления системной колонки
        if column.is_system:
            return Response({'detail': 'Нельзя удалить системную колонку "Готово"'}, status=400)

        column.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
def reorder_columns(request):
    for item in request.data:
        column = get_object_or_404(Column, id=item['id'])
        if not ProjectMember.objects.filter(user=request.user, project=column.card.project).exists():
            return Response({'detail': 'Access denied'}, status=403)
        column.order = item['order']
        column.save()
    return Response({'status': 'reordered'})
