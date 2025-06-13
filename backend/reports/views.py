import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io
import base64
from datetime import timedelta
from django.utils.timezone import now
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db import models
from django.db.models.functions import TruncDate

from work_item.models import WorkItem, WorkItemHistory
from cards.models import Column

class CreatedResolvedGraphView(APIView):
    def get(self, request):
        # Количество дней назад
        days = 30
        today = now().date()
        start_date = today - timedelta(days=days)
        date_range = [start_date + timedelta(days=i) for i in range(days + 1)]
        date_labels = [d.strftime('%Y-%m-%d') for d in date_range]

        # Получаем project_id из параметров
        project_id = request.query_params.get('project_id')
        if not project_id:
            return JsonResponse({'error': 'project_id обязателен'}, status=400)

        # Получаем done_column_id из параметров или ищем по названию
        done_column_id = request.query_params.get('done_column_id')
        if done_column_id:
            try:
                done_column_id = int(done_column_id)
            except ValueError:
                return JsonResponse({'error': 'done_column_id должен быть числом'}, status=400)
        else:
            done_column = Column.objects.filter(title__icontains='готово').first()
            if not done_column:
                return JsonResponse({'error': 'Колонка "Готово" не найдена'}, status=400)
            done_column_id = done_column.id

        # Подсчёт созданных задач по дням
        created_data = (
            WorkItem.objects.filter(
                created_at__date__gte=start_date,
                project_id=project_id
            )
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=models.Count('id'))
        )
        created_map = {str(row['day']): row['count'] for row in created_data}

        # Подсчёт решённых задач по дням (по to_column_id)
        resolved_data = (
            WorkItemHistory.objects.filter(
                to_column_id=done_column_id,
                moved_at__date__gte=start_date,
                work_item__project_id=project_id
            )
            .annotate(day=TruncDate('moved_at'))
            .values('day')
            .annotate(count=models.Count('id'))
        )
        resolved_map = {str(row['day']): row['count'] for row in resolved_data}

        # Подсчёт накопленных значений
        created_total = 0
        resolved_total = 0
        created_cumulative = []
        resolved_cumulative = []

        for label in date_labels:
            created_total += created_map.get(label, 0)
            resolved_total += resolved_map.get(label, 0)
            created_cumulative.append(created_total)
            resolved_cumulative.append(resolved_total)

        # Построение графика
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(date_labels, created_cumulative, color='red', marker='o', label='Создано')
        ax.plot(date_labels, resolved_cumulative, color='green', marker='o', label='Решено')

        ax.fill_between(
            date_labels,
            resolved_cumulative,
            created_cumulative,
            where=[c > r for c, r in zip(created_cumulative, resolved_cumulative)],
            interpolate=True,
            color='lightgreen',
            alpha=0.5
        )

        ax.set_xticks(date_labels[::3])
        ax.set_xticklabels(date_labels[::3], rotation=45)
        ax.set_title(f'Накопление задач (проект ID: {project_id})')
        ax.set_ylabel('Количество задач')
        ax.set_yticks(range(0, max(created_total, resolved_total) + 2))
        ax.legend()
        plt.tight_layout()

        # Преобразуем график в base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return JsonResponse({'image': image_base64})
