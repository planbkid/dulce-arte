"""serializers drf para pedidos."""
from rest_framework import serializers

from .models import Pedido, DetallePedido


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'personalizacion']


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente_nombre', 'cliente_telefono', 'descripcion_diseno',
            'fecha_creacion', 'fecha_entrega', 'estado', 'estado_display',
            'total', 'insumos_descontados', 'detalles',
        ]
