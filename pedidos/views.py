"""vistas (paginas html) de pedidos: tablero kanban y alta de pedidos."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from usuarios.roles import rol_requerido
from .forms import PedidoForm, DetallePedidoFormSet
from .models import Pedido


@login_required
def kanban(request):
    """tablero kanban con los pedidos agrupados por estado de cocina."""
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
    """listado tabular de todos los pedidos."""
    return render(request, 'pedidos/lista.html', {'pedidos': Pedido.objects.all()})


@rol_requerido('Cajero')
def nuevo_pedido(request):
    """alta de un pedido personalizado con sus lineas (solo rol cajero)."""
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        formset = DetallePedidoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            # guarda el pedido con sus detalles y recalcula el total
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
