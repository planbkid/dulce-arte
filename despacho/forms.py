"""formularios de despacho."""
from django import forms

from usuarios.validators import validar_imagen
from .models import Despacho


class DespachoForm(forms.ModelForm):
    """creacion de una ruta de despacho asociada a un pedido."""
    class Meta:
        model = Despacho
        fields = ['pedido', 'repartidor', 'direccion', 'estado']


class ConfirmarEntregaForm(forms.ModelForm):
    """confirmacion de entrega adjuntando la firma / comprobante."""
    class Meta:
        model = Despacho
        fields = ['firma']

    def clean_firma(self):
        # valida el tamaño de la imagen de firma
        return validar_imagen(self.cleaned_data.get('firma'))
