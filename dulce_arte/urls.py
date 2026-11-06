"""urls principales del proyecto dulce arte."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # autenticacion por sesion
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # paginas (templates)
    path('', include('pedidos.urls')),
    path('inventario/', include('inventario.urls')),
    path('despacho/', include('despacho.urls')),

    # api rest (drf) para el kanban asincrono
    path('api/', include('pedidos.api_urls')),
]

# sirve archivos media (imagenes de diseño y firmas) en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
