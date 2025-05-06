from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectMembersListView,
    AddProjectMemberView,
    ChangeMemberRoleView,
    RemoveProjectMemberView,
)

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:project_id>/members/', ProjectMembersListView.as_view(), name='project-members'),
    path('<int:project_id>/members/add/', AddProjectMemberView.as_view(), name='add-member'),
    path('<int:project_id>/members/<int:user_id>/role/', ChangeMemberRoleView.as_view(), name='change-member-role'),
    path('<int:project_id>/members/<int:user_id>/', RemoveProjectMemberView.as_view(), name='remove-member'),
]
