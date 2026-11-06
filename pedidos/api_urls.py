"""rutas de la api rest de pedidos."""
from rest_framework.routers import DefaultRouter

from .api import PedidoViewSet

router = DefaultRouter()
router.register('pedidos', PedidoViewSet, basename='pedido')

urlpatterns = router.urls
