from django.urls import path
from .views import CardViewSet, ColumnViewSet, reorder_columns

card_list_create = CardViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

card_detail = CardViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',  # 👈 Добавили PATCH
})

column_create = ColumnViewSet.as_view({
    'post': 'create',
})

column_update = ColumnViewSet.as_view({
    'put': 'update',
    'delete': 'destroy',
})

urlpatterns = [
    path('projects/<int:project_id>/cards/', card_list_create),
    path('<int:pk>/', card_detail),
    path('<int:card_id>/columns/', column_create),
    path('columns/<int:pk>/', column_update),
    path('columns/reorder/', reorder_columns),
]
