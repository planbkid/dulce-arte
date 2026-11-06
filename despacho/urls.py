"""rutas de despacho."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_despachos, name='lista_despachos'),
    path('nuevo/', views.nuevo_despacho, name='nuevo_despacho'),
    path('<int:pk>/confirmar/', views.confirmar_entrega, name='confirmar_entrega'),
]
