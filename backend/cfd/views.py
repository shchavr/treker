import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io
import base64
from datetime import timedelta
from django.utils.timezone import now
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db.models.functions import TruncDate
from django.db import models

from work_item.models import WorkItem
from cards.models import Column


class CFDView(APIView):
    def get(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return JsonResponse({'error': 'project_id обязателен'}, status=400)

        days = 30
        today = now().date()
        start_date = today - timedelta(days=days)
        date_range = [start_date + timedelta(days=i) for i in range(days + 1)]
        date_labels = [d.strftime('%Y-%m-%d') for d in date_range]

        # Все колонки проекта
        columns = Column.objects.filter(card__project_id=project_id).order_by('order')

        # Подготовим данные: {column_title: [0, 0, 1, 2, ...]}
        column_series = {col.title: [0] * len(date_labels) for col in columns}

        # Получаем задачи проекта
        tasks = WorkItem.objects.filter(project_id=project_id)

        for task in tasks:
            created = task.created_at.date()
            col_title = task.column.title

            for i, day in enumerate(date_range):
                if day >= created:
                    column_series[col_title][i] += 1

        # Построение графика
        fig, ax = plt.subplots(figsize=(10, 6))
        bottom = [0] * len(date_labels)

        for title, counts in column_series.items():
            ax.fill_between(date_labels, bottom, [b + c for b, c in zip(bottom, counts)], label=title)
            bottom = [b + c for b, c in zip(bottom, counts)]

        ax.set_xticks(date_labels[::3])
        ax.set_xticklabels(date_labels[::3], rotation=45)
        ax.set_title(f'Cumulative Flow Diagram (проект ID: {project_id})')
        ax.set_ylabel('Количество задач')
        ax.legend()
        plt.tight_layout()

        # Возвращаем изображение
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return JsonResponse({'image': image_base64})
