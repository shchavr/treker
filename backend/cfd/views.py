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

from work_item.models import WorkItem, WorkItemHistory
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

        # Все колонки проекта (упорядочены)
        columns = Column.objects.filter(card__project_id=project_id).order_by('order')
        column_ids = [col.id for col in columns]
        column_titles = {col.id: col.title for col in columns}

        # Инициализация: {column_title: [0]*len(date_range)}
        column_series = {col.title: [0] * len(date_range) for col in columns}

        # Получаем задачи проекта
        tasks = WorkItem.objects.filter(project_id=project_id).prefetch_related('history')

        for task in tasks:
            created_date = task.created_at.date()
            history = sorted(task.history.all(), key=lambda h: h.moved_at)

            # Определяем начальную колонку
            if history:
                timeline = [(created_date, history[0].from_column_id)]
                for record in history:
                    move_date = record.moved_at.date()
                    timeline.append((move_date, record.to_column_id))
            else:
                timeline = [(created_date, task.column_id)]

            timeline = sorted(timeline, key=lambda t: t[0])
            print(f"Task {task.id} timeline: {timeline}")

            for i, day in enumerate(date_range):
                last_column_id = None
                for moved_date, to_col in timeline:
                    if moved_date <= day:
                        last_column_id = to_col
                    else:
                        break
                if last_column_id and last_column_id in column_titles:
                    column_series[column_titles[last_column_id]][i] += 1

        # DEBUG: выведем итоговое количество задач по колонкам на последнюю дату
        for title, counts in column_series.items():
            print(f"{title}: {counts[-1]} задач на {date_labels[-1]}")

        # Построение графика
        fig, ax = plt.subplots(figsize=(10, 6))
        bottom = [0] * len(date_range)

        for col in columns:
            counts = column_series[col.title]
            ax.fill_between(date_labels, bottom, [b + c for b, c in zip(bottom, counts)], label=col.title)
            bottom = [b + c for b, c in zip(bottom, counts)]

        ax.set_xticks(date_labels[::3])
        ax.set_xticklabels(date_labels[::3], rotation=45)
        ax.set_title(f'Cumulative Flow Diagram (проект ID: {project_id})')
        ax.set_ylabel('Количество задач')
        ax.set_yticks(range(0, max(bottom) + 2))
        ax.legend()
        plt.tight_layout()

        # Возвращаем изображение
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return JsonResponse({'image': image_base64})
