"""
Carga datos de demostración para Dulce Arte:
grupos/roles, insumos, productos con su receta (BOM) y pedidos de ejemplo.

Uso:
    python manage.py seed_demo
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from inventario.models import Insumo, Producto, ProductoInsumo
from pedidos.models import Pedido, DetallePedido
from despacho.models import Despacho


class Command(BaseCommand):
    help = 'Carga datos de demostración (roles, insumos, productos, pedidos).'

    def handle(self, *args, **options):
        # ---- Roles (grupos) ----
        for rol in ['Cajero', 'Cocina', 'Despacho']:
            Group.objects.get_or_create(name=rol)
        self.stdout.write(self.style.SUCCESS('Roles creados: Cajero, Cocina, Despacho'))

        # ---- Insumos ----
        insumos = {
            'Harina':   dict(unidad='g',  stock=20000, stock_minimo=2000, costo_unitario=Decimal('1.5')),
            'Azúcar':   dict(unidad='g',  stock=15000, stock_minimo=1500, costo_unitario=Decimal('1.2')),
            'Huevos':   dict(unidad='un', stock=200,   stock_minimo=24,   costo_unitario=Decimal('200')),
            'Crema':    dict(unidad='ml', stock=10000, stock_minimo=1000, costo_unitario=Decimal('3')),
            'Chocolate':dict(unidad='g',  stock=8000,  stock_minimo=800,  costo_unitario=Decimal('6')),
        }
        objs = {}
        for nombre, data in insumos.items():
            objs[nombre], _ = Insumo.objects.get_or_create(nombre=nombre, defaults=data)
        self.stdout.write(self.style.SUCCESS(f'{len(objs)} insumos cargados'))

        # ---- Productos + receta (BOM) ----
        torta, _ = Producto.objects.get_or_create(
            nombre='Torta de Chocolate',
            defaults=dict(descripcion='Torta clásica de chocolate', precio_base=Decimal('18000')),
        )
        cupcakes, _ = Producto.objects.get_or_create(
            nombre='Cupcakes (docena)',
            defaults=dict(descripcion='12 cupcakes decorados', precio_base=Decimal('9000')),
        )
        receta = [
            (torta, 'Harina', 500), (torta, 'Azúcar', 400), (torta, 'Huevos', 6),
            (torta, 'Crema', 300), (torta, 'Chocolate', 250),
            (cupcakes, 'Harina', 300), (cupcakes, 'Azúcar', 200), (cupcakes, 'Huevos', 4),
        ]
        for prod, insumo_nombre, cant in receta:
            ProductoInsumo.objects.get_or_create(
                producto=prod, insumo=objs[insumo_nombre],
                defaults=dict(cantidad=Decimal(cant)),
            )
        self.stdout.write(self.style.SUCCESS('Productos y recetas (BOM) cargados'))

        # ---- Pedidos de ejemplo ----
        if not Pedido.objects.exists():
            p1 = Pedido.objects.create(
                cliente_nombre='María Pérez', cliente_telefono='+56912345678',
                descripcion_diseno='Torta cumpleaños, tema unicornio, texto "Feliz Cumple Sofía"',
                fecha_entrega=timezone.now() + timedelta(days=2),
                estado=Pedido.RECIBIDO,
            )
            DetallePedido.objects.create(pedido=p1, producto=torta, cantidad=1,
                                         personalizacion='Relleno manjar')
            p1.recalcular_total()

            p2 = Pedido.objects.create(
                cliente_nombre='Juan Soto', cliente_telefono='+56987654321',
                descripcion_diseno='Cupcakes para evento empresa',
                fecha_entrega=timezone.now() + timedelta(days=1),
                estado=Pedido.RECIBIDO,
            )
            DetallePedido.objects.create(pedido=p2, producto=cupcakes, cantidad=2)
            p2.recalcular_total()

            Despacho.objects.create(pedido=p1, direccion='Av. Siempre Viva 742, Santiago')
            self.stdout.write(self.style.SUCCESS('Pedidos y despacho de ejemplo creados'))

        self.stdout.write(self.style.SUCCESS('\n✅ Datos de demostración cargados correctamente.'))
