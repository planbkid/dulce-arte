"""modelo de despacho: ruta de entrega con confirmacion por firma digital."""
from django.conf import settings
from django.db import models

from pedidos.models import Pedido


class Despacho(models.Model):
    PENDIENTE = 'PENDIENTE'
    EN_RUTA = 'EN_RUTA'
    ENTREGADO = 'ENTREGADO'
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (EN_RUTA, 'En ruta'),
        (ENTREGADO, 'Entregado'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='despacho')
    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    direccion = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    firma = models.ImageField(
        'Firma digital / comprobante', upload_to='firmas/', blank=True, null=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega_real = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Despacho Pedido #{self.pedido_id} - {self.get_estado_display()}"
