"""Rutas (templates) de pedidos."""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.kanban, name='kanban'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/nuevo/', views.nuevo_pedido, name='nuevo_pedido'),
]
