"""Control de acceso por roles (grupos de Django: Cajero, Cocina, Despacho)."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def tiene_rol(user, *roles):
    """Retorna True si el usuario es superusuario o pertenece a alguno de los roles dados."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


def rol_requerido(*roles):
    """Decorador de vista: exige sesión iniciada y uno de los roles indicados.

    Sin sesión -> redirige al login. Con sesión pero sin el rol -> 403.
    """
    def decorator(view):
        @wraps(view)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if not tiene_rol(request.user, *roles):
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return _wrapped
    return decorator
