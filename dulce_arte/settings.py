"""
Django settings for dulce_arte project — EVA3 Backend (Proyecto 3 "Dulce Arte").
Alumno: Cristóbal Barriga · Grupo 3
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga variables desde el archivo .env (si existe)
load_dotenv(BASE_DIR / '.env')

# -------------------------------------------------------------------
# Seguridad / entorno
# -------------------------------------------------------------------
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-dev-key-cambiar-en-produccion',
)

DEBUG = os.getenv('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS se lee como lista separada por comas en el .env
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()
]

# En AWS detrás de Nginx, confiar en el origen https/http de la IP pública
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]


# -------------------------------------------------------------------
# Aplicaciones
# -------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'rest_framework',
    'django_filters',

    # Apps del proyecto
    'usuarios',
    'inventario',
    'pedidos',
    'despacho',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dulce_arte.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'dulce_arte.wsgi.application'


# -------------------------------------------------------------------
# Base de datos
# Usa PostgreSQL cuando hay credenciales en .env (local / AWS).
# Si no hay DB_NAME definido, cae a SQLite para que el proyecto
# arranque en cualquier parte sin configuración previa.
# -------------------------------------------------------------------
if os.getenv('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# -------------------------------------------------------------------
# Validación de contraseñas
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -------------------------------------------------------------------
# Internacionalización
# -------------------------------------------------------------------
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True


# -------------------------------------------------------------------
# Archivos estáticos y media
# -------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -------------------------------------------------------------------
# Autenticación / sesiones
# -------------------------------------------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'kanban'
LOGOUT_REDIRECT_URL = 'login'


# -------------------------------------------------------------------
# Django REST Framework
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    # Autenticación por sesión: la API usa el mismo login que las páginas web.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Por defecto, ningún endpoint es accesible sin iniciar sesión.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}


# -------------------------------------------------------------------
# Endurecimiento de seguridad
# Cabeceras aplicadas siempre (sirven también sobre HTTP); el resto
# se activa solo en producción (DEBUG=False) para no estorbar en local.
# -------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True        # impide que el navegador "adivine" tipos MIME
X_FRAME_OPTIONS = 'DENY'                   # protege contra clickjacking (no permite iframes)
SECURE_REFERRER_POLICY = 'same-origin'     # no filtra URLs internas a sitios externos

if not DEBUG:
    # Las cookies no son legibles por JavaScript (excepto el token CSRF,
    # que el Kanban necesita leer para enviarlo en las peticiones fetch).
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

    # HTTPS: activar SOLO si la instancia tiene certificado TLS.
    # Se controla por variable de entorno para no romper el despliegue
    # HTTP de AWS Academy (sin dominio ni certificado).
    USAR_HTTPS = os.getenv('USAR_HTTPS', 'False') == 'True'
    SESSION_COOKIE_SECURE = USAR_HTTPS     # cookie de sesión solo viaja por HTTPS
    CSRF_COOKIE_SECURE = USAR_HTTPS        # cookie CSRF solo viaja por HTTPS
    SECURE_SSL_REDIRECT = USAR_HTTPS       # redirige todo el tráfico a HTTPS
    if USAR_HTTPS:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        SECURE_HSTS_SECONDS = 31536000     # obliga HTTPS por 1 año (HSTS)
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

    # Impide desplegar en producción con la clave de ejemplo.
    if SECRET_KEY == 'django-insecure-dev-key-cambiar-en-produccion':
        raise RuntimeError(
            'Define una SECRET_KEY real en el archivo .env antes de desplegar (DEBUG=False).'
        )
