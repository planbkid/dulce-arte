"""Django Admin personalizado — inventario."""
from django.contrib import admin

from .models import Insumo, Producto, ProductoInsumo


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad', 'stock', 'stock_minimo', 'bajo_stock')
    list_filter = ('unidad',)
    search_fields = ('nombre',)
    list_editable = ('stock', 'stock_minimo')

    @admin.display(boolean=True, description='¿Bajo stock?')
    def bajo_stock(self, obj):
        return obj.bajo_stock


class ProductoInsumoInline(admin.TabularInline):
    """Permite definir la receta (BOM) directamente al editar el producto."""
    model = ProductoInsumo
    extra = 1
    autocomplete_fields = ('insumo',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    inlines = [ProductoInsumoInline]
