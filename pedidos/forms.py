"""Formularios de pedidos."""
from django import forms
from django.forms import inlineformset_factory

from .models import Pedido, DetallePedido


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'cliente_nombre', 'cliente_telefono', 'descripcion_diseno',
            'imagen_referencia', 'fecha_entrega',
        ]
        widgets = {
            'fecha_entrega': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'descripcion_diseno': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_entrega'].input_formats = ['%Y-%m-%dT%H:%M']


# Formset para capturar las líneas (productos) del pedido en el mismo formulario
DetallePedidoFormSet = inlineformset_factory(
    Pedido,
    DetallePedido,
    fields=['producto', 'cantidad', 'personalizacion'],
    extra=3,
    can_delete=True,
)
