import io
import base64
from datetime import timedelta
from django.utils.timezone import now
from django.http import JsonResponse
import matplotlib.pyplot as plt
from django.db.models import Count
from rest_framework.views import APIView
from work_item.models import WorkItem  # ← важно

class CreatedResolvedGraphView(APIView):
    def get(self, request):
        days = 30
        today = now().date()
        start_date = today - timedelta(days=days)
        date_range = [start_date + timedelta(days=i) for i in range(days + 1)]
        date_labels = [d.strftime('%Y-%m-%d') for d in date_range]

        created_data = (
            WorkItem.objects.filter(created_at__date__gte=start_date)
            .extra({'day': "date(created_at)"})
            .values('day').annotate(count=Count('id'))
        )
        created_map = {str(row['day']): row['count'] for row in created_data}

        resolved_data = (
            WorkItem.objects.filter(done_at__isnull=False, done_at__date__gte=start_date)
            .extra({'day': "date(done_at)"})
            .values('day').annotate(count=Count('id'))
        )
        resolved_map = {str(row['day']): row['count'] for row in resolved_data}

        created_cumulative = []
        resolved_cumulative = []
        total_created = 0
        total_resolved = 0

        for label in date_labels:
            total_created += created_map.get(label, 0)
            total_resolved += resolved_map.get(label, 0)
            created_cumulative.append(total_created)
            resolved_cumulative.append(total_resolved)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(date_labels, created_cumulative, label='Создано', color='green')
        ax.plot(date_labels, resolved_cumulative, label='Решено', color='red')
        ax.fill_between(date_labels, resolved_cumulative, created_cumulative, color='lightgreen', alpha=0.5)
        ax.set_xticks(date_labels[::3])
        ax.set_xticklabels(date_labels[::3], rotation=45)
        ax.set_title('Созданные vs Решенные задачи')
        ax.set_ylabel('Количество')
        ax.legend()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return JsonResponse({'image': image_base64})
