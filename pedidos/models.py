"""modelos de pedidos: pedido personalizado, detalle y logica kanban + bom."""
from collections import defaultdict
from decimal import Decimal

from django.conf import settings
from django.db import models, transaction

from inventario.models import Insumo, Producto


class StockInsuficiente(Exception):
    """se lanza cuando no hay suficiente insumo para preparar un pedido."""
    pass


class Pedido(models.Model):
    # estados del tablero kanban de cocina
    RECIBIDO = 'RECIBIDO'
    PREPARACION = 'PREPARACION'
    HORNEADO = 'HORNEADO'
    CALIDAD = 'CALIDAD'
    LISTO = 'LISTO'
    ESTADOS = [
        (RECIBIDO, 'Recibido'),
        (PREPARACION, 'En Preparación'),
        (HORNEADO, 'Horneado/Decorado'),
        (CALIDAD, 'Control de Calidad'),
        (LISTO, 'Listo'),
    ]

    cliente_nombre = models.CharField(max_length=120)
    cliente_telefono = models.CharField(max_length=30, blank=True)
    descripcion_diseno = models.TextField('Diseño / personalización', blank=True)
    imagen_referencia = models.ImageField(upload_to='disenos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default=RECIBIDO)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insumos_descontados = models.BooleanField(default=False)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ['fecha_entrega']

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente_nombre}"

    def recalcular_total(self):
        """suma los subtotales de los detalles y guarda el total."""
        total = sum((d.subtotal() for d in self.detalles.all()), Decimal('0'))
        self.total = total
        self.save(update_fields=['total'])
        return total

    def descontar_insumos(self):
        """
        descuenta el inventario segun la receta (bom) de cada producto.
        se ejecuta una sola vez, al pasar a 'en preparacion'.
        lanza stockinsuficiente si falta algun insumo.
        """
        if self.insumos_descontados:
            return

        # 1) calcular cuanto se necesita de cada insumo
        requerimientos = defaultdict(Decimal)
        for det in self.detalles.select_related('producto'):
            for item in det.producto.receta.all():
                requerimientos[item.insumo_id] += item.cantidad * det.cantidad

        with transaction.atomic():
            # 2) validar que haya stock suficiente (bloqueando filas)
            for insumo_id, cant in requerimientos.items():
                insumo = Insumo.objects.select_for_update().get(pk=insumo_id)
                if insumo.stock < cant:
                    raise StockInsuficiente(
                        f"Stock insuficiente de '{insumo.nombre}': "
                        f"se necesitan {cant} {insumo.unidad} y hay {insumo.stock}."
                    )
            # 3) descontar
            for insumo_id, cant in requerimientos.items():
                insumo = Insumo.objects.select_for_update().get(pk=insumo_id)
                insumo.stock -= cant
                insumo.save(update_fields=['stock'])

            self.insumos_descontados = True
            self.save(update_fields=['insumos_descontados'])


class DetallePedido(models.Model):
    """linea de un pedido: un producto, su cantidad y personalizacion."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    personalizacion = models.CharField(max_length=255, blank=True)

    def subtotal(self):
        return self.producto.precio_base * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto}"
