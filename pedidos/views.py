"""Vistas (templates) de pedidos: tablero Kanban y alta de pedidos."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import PedidoForm, DetallePedidoFormSet
from .models import Pedido


@login_required
def kanban(request):
    """Tablero Kanban de cocina con los pedidos agrupados por estado."""
    columnas = []
    for valor, etiqueta in Pedido.ESTADOS:
        columnas.append({
            'clave': valor,
            'titulo': etiqueta,
            'pedidos': Pedido.objects.filter(estado=valor),
        })
    return render(request, 'pedidos/kanban.html', {
        'columnas': columnas,
        'estados': Pedido.ESTADOS,
    })


@login_required
def lista_pedidos(request):
    pedidos = Pedido.objects.all()
    return render(request, 'pedidos/lista.html', {'pedidos': pedidos})


@login_required
def nuevo_pedido(request):
    """Alta de pedido personalizado con sus líneas de producto (cotización)."""
    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        formset = DetallePedidoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
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
