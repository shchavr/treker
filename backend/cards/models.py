from django.db import models
from projects.models import Project
from django.conf import settings


class Card(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Column(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()