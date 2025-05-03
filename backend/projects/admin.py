from django.contrib import admin
from .models import Project, ProjectMember, RoleUser, RoleProjectMember

admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(RoleUser)
admin.site.register(RoleProjectMember)
