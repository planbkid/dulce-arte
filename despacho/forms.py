"""Formularios de despacho."""
from django import forms

from usuarios.validators import validar_imagen
from .models import Despacho


class DespachoForm(forms.ModelForm):
    """Creación de una ruta de despacho asociada a un pedido."""
    class Meta:
        model = Despacho
        fields = ['pedido', 'repartidor', 'direccion', 'estado']


class ConfirmarEntregaForm(forms.ModelForm):
    """Confirmación de entrega adjuntando la firma digital / comprobante."""
    class Meta:
        model = Despacho
        fields = ['firma']

    def clean_firma(self):
        # Valida el tamaño de la imagen de firma subida.
        return validar_imagen(self.cleaned_data.get('firma'))
