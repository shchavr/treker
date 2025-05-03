from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class RoleUser(models.Model):
    name = models.CharField(max_length=50)  # admin, manager, developer, user

    def __str__(self):
        return self.name

class RoleProjectMember(models.Model):
    name = models.CharField(max_length=50)  # admin, participant, observer

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
