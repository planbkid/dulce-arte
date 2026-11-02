"""Formularios de despacho."""
from django import forms

from .models import Despacho


class DespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ['pedido', 'repartidor', 'direccion', 'estado']


class ConfirmarEntregaForm(forms.ModelForm):
    """Confirmación de entrega con firma digital / comprobante (imagen)."""
    class Meta:
        model = Despacho
        fields = ['firma']
