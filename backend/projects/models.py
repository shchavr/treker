from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class RoleProjectMember(models.Model):
    name = models.CharField(max_length=50)  # Например: "owner", "editor", "viewer"

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ProjectMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    role = models.ForeignKey(RoleProjectMember, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('user', 'project')  

    def __str__(self):
        return f"{self.user.email} in {self.project.title}"

import uuid
from django.utils import timezone
from datetime import timedelta

class ProjectInvite(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        return self.created_at < timezone.now() - timedelta(days=3)  # ← ссылка активна 3 дня

    def __str__(self):
        return f"Invite to {self.project.title} by {self.created_by}"
