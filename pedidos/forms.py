"""formularios de pedidos."""
from django import forms
from django.forms import inlineformset_factory

from usuarios.validators import validar_imagen
from .models import Pedido, DetallePedido


class PedidoForm(forms.ModelForm):
    """datos del cliente, diseño personalizado y fecha de entrega."""
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
        # el input datetime-local envia el formato 'yyyy-mm-ddThh:mm'
        self.fields['fecha_entrega'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_imagen_referencia(self):
        # valida el tamaño de la imagen de referencia
        return validar_imagen(self.cleaned_data.get('imagen_referencia'))


# formset para capturar las lineas (productos) del pedido en el mismo form
DetallePedidoFormSet = inlineformset_factory(
    Pedido,
    DetallePedido,
    fields=['producto', 'cantidad', 'personalizacion'],
    extra=3,
    can_delete=True,
)
