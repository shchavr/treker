from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, accept_invite

router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

urlpatterns = [
    path('invite/accept/', accept_invite, name='accept-invite'),
    path('', include(router.urls)),
]