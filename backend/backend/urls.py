from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularSwaggerView, SpectacularRedocView, SpectacularAPIView

from django.conf import settings
from django.conf.urls.static import static

class SwaggerUIView(SpectacularSwaggerView):
    serve_static = True

class RedocUIView(SpectacularRedocView):
    serve_static = True



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/cards/', include('cards.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),

    # drf-spectacular schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SwaggerUIView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', RedocUIView.as_view(url_name='schema'), name='redoc'),
    path('api/projects/', include('projects.urls')),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
