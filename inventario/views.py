"""vistas (templates) de inventario."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Insumo, Producto


@login_required
def lista_insumos(request):
    # muestra insumos y productos en una sola pagina
    insumos = Insumo.objects.all()
    return render(request, 'inventario/insumos.html', {
        'insumos': insumos,
        'productos': Producto.objects.all(),
    })
