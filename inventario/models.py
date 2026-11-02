"""Modelos de inventario: insumos, productos y la Lista de Materiales (BOM)."""
from django.db import models


class Insumo(models.Model):
    """Materia prima de bodega (harina, azúcar, crema, etc.)."""
    UNIDADES = [
        ('g', 'Gramos'),
        ('kg', 'Kilogramos'),
        ('ml', 'Mililitros'),
        ('l', 'Litros'),
        ('un', 'Unidades'),
    ]
    nombre = models.CharField(max_length=120, unique=True)
    unidad = models.CharField(max_length=2, choices=UNIDADES, default='un')
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.stock} {self.unidad})"

    @property
    def bajo_stock(self):
        """True si el stock llegó al mínimo o menos (para alertas)."""
        return self.stock <= self.stock_minimo


class Producto(models.Model):
    """Producto de pastelería que se vende (torta, postre, etc.)."""
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ProductoInsumo(models.Model):
    """Lista de Materiales (BOM): qué insumos y cuánto consume un producto."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='receta')
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('producto', 'insumo')
        verbose_name = 'Insumo de la receta'
        verbose_name_plural = 'Receta (BOM)'

    def __str__(self):
        return f"{self.producto}: {self.cantidad} {self.insumo.unidad} de {self.insumo.nombre}"
