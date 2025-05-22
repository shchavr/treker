from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction


from django.contrib.auth import get_user_model

from projects.models import Project, RoleProjectMember, ProjectMember

User = get_user_model()

@receiver(post_save, sender=User)
def create_project_after_user_registration(sender, instance, created, **kwargs):
    if not created:
        return

    with transaction.atomic():

        project = Project.objects.create(
            title="Мой первый проект",
            created_by=instance
        )

        role, _ = RoleProjectMember.objects.get_or_create(name="owner")

        ProjectMember.objects.create(
            user=instance,
            project=project,
            role=role
        )
