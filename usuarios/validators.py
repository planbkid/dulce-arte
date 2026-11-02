"""Validaciones de archivos subidos (imágenes de diseño y firmas)."""
from django.core.exceptions import ValidationError

# Tamaño máximo permitido para una imagen subida (5 MB).
MAX_IMAGEN_MB = 5


def validar_imagen(archivo):
    """Rechaza imágenes demasiado grandes para evitar abuso de almacenamiento."""
    if archivo and archivo.size > MAX_IMAGEN_MB * 1024 * 1024:
        raise ValidationError(f'La imagen no puede superar los {MAX_IMAGEN_MB} MB.')
    return archivo
