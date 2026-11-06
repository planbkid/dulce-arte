"""api rest (drf) de pedidos - usada por el tablero kanban asincrono."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from usuarios.roles import tiene_rol
from .models import Pedido, StockInsuficiente
from .serializers import PedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    """crud de pedidos por api + accion para avanzar el estado en el kanban."""
    queryset = Pedido.objects.all().order_by('fecha_entrega')
    serializer_class = PedidoSerializer
    filterset_fields = ['estado']

    @action(detail=True, methods=['post'])
    def mover_estado(self, request, pk=None):
        """cambia el estado del pedido en el kanban (solo rol cocina).

        al pasar a 'en preparacion' descuenta los insumos segun la bom.
        """
        if not tiene_rol(request.user, 'Cocina'):
            return Response(
                {'error': 'No tienes permiso para mover pedidos (rol Cocina requerido).'},
                status=403,
            )

        pedido = self.get_object()
        nuevo = request.data.get('estado')

        # valida que el estado recibido sea uno de los definidos
        if nuevo not in dict(Pedido.ESTADOS):
            return Response({'error': 'Estado inválido.'}, status=400)

        # regla de negocio: descontar inventario al iniciar la preparacion
        if nuevo == Pedido.PREPARACION and not pedido.insumos_descontados:
            try:
                pedido.descontar_insumos()
            except StockInsuficiente as e:
                return Response({'error': str(e)}, status=400)

        pedido.estado = nuevo
        pedido.save(update_fields=['estado'])
        return Response({
            'ok': True,
            'estado': pedido.estado,
            'estado_display': pedido.get_estado_display(),
        })
