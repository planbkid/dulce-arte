"""control de acceso por roles (grupos: cajero, cocina, despacho)."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def tiene_rol(user, *roles):
    """true si es superusuario o pertenece a alguno de los roles."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


def rol_requerido(*roles):
    """decorador: exige sesion iniciada y uno de los roles dados."""
    def decorator(view):
        @wraps(view)
        @login_required
        def _wrapped(request, *args, **kwargs):
            # sin el rol -> 403; sin sesion login_required ya redirige
            if not tiene_rol(request.user, *roles):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return _wrapped
    return decorator
