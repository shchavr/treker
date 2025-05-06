from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from projects.models import Project  

User = get_user_model()

class Note(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:30]

class Column(models.Model):
    card = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='columns')  # если Note = Card
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField()
    limit_work_item = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['position']

    def __str__(self):
        return self.name