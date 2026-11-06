"""django admin personalizado - pedidos."""
from django.contrib import admin

from .models import Pedido, DetallePedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    autocomplete_fields = ('producto',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cliente_nombre', 'estado', 'fecha_entrega', 'total', 'insumos_descontados'
    )
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('cliente_nombre', 'cliente_telefono')
    date_hierarchy = 'fecha_entrega'
    inlines = [DetallePedidoInline]
    readonly_fields = ('fecha_creacion', 'total', 'insumos_descontados')

    def save_related(self, request, form, formsets, change):
        # recalcula el total del pedido tras guardar sus detalles
        super().save_related(request, form, formsets, change)
        form.instance.recalcular_total()
