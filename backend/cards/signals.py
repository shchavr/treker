from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from projects.models import Project
from .models import Card, Column

@receiver(post_save, sender=Project)
def create_card_and_columns_for_project(sender, instance, created, **kwargs):
    if not created:
        return

    with transaction.atomic():
        # Создаём первую доску
        card = Card.objects.create(
            project=instance,
            title="Первая доска"
        )

        # Создаём три стандартные колонки
        Column.objects.create(card=card, title='Выполняется', order=1)
        Column.objects.create(card=card, title='В проверке', order=2)
        Column.objects.create(card=card, title='Готово', order=3, is_system=True)
