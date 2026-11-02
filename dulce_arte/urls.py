"""URLs principales del proyecto Dulce Arte."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación (sesiones)
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Páginas (templates)
    path('', include('pedidos.urls')),
    path('inventario/', include('inventario.urls')),
    path('despacho/', include('despacho.urls')),

    # API REST (DRF) para el Kanban asíncrono
    path('api/', include('pedidos.api_urls')),
]

# Servir archivos media (imágenes de diseño y firmas) en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
