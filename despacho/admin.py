"""Django Admin personalizado — despacho."""
from django.contrib import admin

from .models import Despacho


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'repartidor', 'estado', 'direccion', 'fecha_entrega_real')
    list_filter = ('estado',)
    search_fields = ('pedido__cliente_nombre', 'direccion')
    autocomplete_fields = ('pedido', 'repartidor')
