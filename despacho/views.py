"""Vistas (páginas HTML) de despacho: rutas y confirmación con firma digital."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from usuarios.roles import rol_requerido
from .forms import DespachoForm, ConfirmarEntregaForm
from .models import Despacho


@login_required
def lista_despachos(request):
    """Listado de despachos con su estado y firma asociada."""
    despachos = Despacho.objects.select_related('pedido', 'repartidor').all()
    return render(request, 'despacho/lista.html', {'despachos': despachos})


@rol_requerido('Cajero', 'Despacho')
def nuevo_despacho(request):
    """Crea una ruta de despacho para un pedido."""
    if request.method == 'POST':
        form = DespachoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Despacho creado.')
            return redirect('lista_despachos')
    else:
        form = DespachoForm()
    return render(request, 'despacho/nuevo.html', {'form': form})


@rol_requerido('Despacho')
def confirmar_entrega(request, pk):
    """Sube la firma digital / comprobante y marca el despacho como entregado.

    Solo el rol Despacho (o superusuario) puede confirmar entregas.
    """
    desp = get_object_or_404(Despacho, pk=pk)
    if request.method == 'POST':
        form = ConfirmarEntregaForm(request.POST, request.FILES, instance=desp)
        if form.is_valid():
            # Registra firma, estado, fecha real y repartidor que confirma.
            desp = form.save(commit=False)
            desp.estado = Despacho.ENTREGADO
            desp.fecha_entrega_real = timezone.now()
            if not desp.repartidor:
                desp.repartidor = request.user
            desp.save()
            messages.success(request, f'Entrega del pedido #{desp.pedido_id} confirmada.')
            return redirect('lista_despachos')
    else:
        form = ConfirmarEntregaForm(instance=desp)
    return render(request, 'despacho/confirmar.html', {'form': form, 'desp': desp})
