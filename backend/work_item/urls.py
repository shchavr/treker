from django.urls import path
from .views import WorkItemViewSet, TagViewSet, WorkItemTypeViewSet

workitem_list = WorkItemViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

workitem_detail = WorkItemViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

history_view = WorkItemViewSet.as_view({
    'get': 'history'
})

urlpatterns = [
    path('boards/<int:board_id>/tasks/', workitem_list),
    path('tasks/<int:pk>/', workitem_detail),
    path('tasks/<int:pk>/move/', WorkItemViewSet.as_view({'patch': 'move'})),
    path('tasks/<int:pk>/assign/', WorkItemViewSet.as_view({'post': 'assign'})),
    path('tasks/<int:pk>/tags/', WorkItemViewSet.as_view({'post': 'tags'})),
    path('tasks/<int:pk>/comments/', WorkItemViewSet.as_view({'post': 'comments', 'get': 'get_comments'})),
    path('tags/', TagViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('tags/<int:pk>/', TagViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    path('task-types/', WorkItemTypeViewSet.as_view({'get': 'list'})),

    path('tasks/<int:pk>/history/', history_view),
]
