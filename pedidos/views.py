"""Vistas (páginas HTML) de pedidos: tablero Kanban y alta de pedidos."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from usuarios.roles import rol_requerido
from .forms import PedidoForm, DetallePedidoFormSet
from .models import Pedido


@login_required
def kanban(request):
    """Muestra el tablero Kanban con los pedidos agrupados por estado de cocina."""
    columnas = [
        {'clave': valor, 'titulo': etiqueta,
         'pedidos': Pedido.objects.filter(estado=valor)}
        for valor, etiqueta in Pedido.ESTADOS
    ]
    return render(request, 'pedidos/kanban.html', {
        'columnas': columnas,
        'estados': Pedido.ESTADOS,
    })


@login_required
def lista_pedidos(request):
    """Listado tabular de todos los pedidos."""
    return render(request, 'pedidos/lista.html', {'pedidos': Pedido.objects.all()})


@rol_requerido('Cajero')
def nuevo_pedido(request):
    """Alta de un pedido personalizado con sus líneas de producto (cotización).

    Solo el rol Cajero (o un superusuario) puede registrar pedidos.
    """
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        formset = DetallePedidoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            # Guarda el pedido junto a sus detalles y recalcula el total.
            pedido = form.save(commit=False)
            pedido.creado_por = request.user
            pedido.save()
            formset.instance = pedido
            formset.save()
            pedido.recalcular_total()
            messages.success(request, f'Pedido #{pedido.id} creado correctamente.')
            return redirect('kanban')
    else:
        form = PedidoForm()
        formset = DetallePedidoFormSet()
    return render(request, 'pedidos/nuevo.html', {'form': form, 'formset': formset})
