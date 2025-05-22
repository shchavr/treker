from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import RoleProjectMember

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    default_roles = ["owner", "editor", "viewer"]
    for role_name in default_roles:
        RoleProjectMember.objects.get_or_create(name=role_name)
