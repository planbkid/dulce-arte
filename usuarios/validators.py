"""validaciones de archivos subidos (imagenes de diseño y firmas)."""
from django.core.exceptions import ValidationError

# tamaño maximo permitido por imagen (5 mb)
MAX_IMAGEN_MB = 5


def validar_imagen(archivo):
    """rechaza imagenes demasiado grandes para evitar abuso de almacenamiento."""
    if archivo and archivo.size > MAX_IMAGEN_MB * 1024 * 1024:
        raise ValidationError(f'La imagen no puede superar los {MAX_IMAGEN_MB} MB.')
    return archivo
