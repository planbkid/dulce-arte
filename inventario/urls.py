"""rutas de inventario."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.lista_insumos, name='lista_insumos'),
]
