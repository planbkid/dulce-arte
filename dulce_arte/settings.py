"""
settings de django para el proyecto dulce_arte (eva3 backend, proyecto 3).
alumno: cristobal barriga - grupo 3
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# carga variables desde el archivo .env si existe
load_dotenv(BASE_DIR / '.env')

# -------------------------------------------------------------------
# seguridad / entorno
# -------------------------------------------------------------------
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-dev-key-cambiar-en-produccion',
)

DEBUG = os.getenv('DEBUG', 'True') == 'True'

# hosts permitidos, separados por comas en el .env
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()
]

# en aws detras de nginx, confiar en el origen de la ip publica
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()
]


# -------------------------------------------------------------------
# aplicaciones
# -------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # terceros
    'rest_framework',
    'django_filters',

    # apps del proyecto
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
# base de datos
# usa postgresql cuando hay credenciales en el .env (local / aws).
# si no hay db_name definido, cae a sqlite para arrancar sin config.
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
# validacion de contraseñas
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# -------------------------------------------------------------------
# internacionalizacion
# -------------------------------------------------------------------
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True


# -------------------------------------------------------------------
# archivos estaticos y media
# -------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -------------------------------------------------------------------
# autenticacion / sesiones
# -------------------------------------------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'kanban'
LOGOUT_REDIRECT_URL = 'login'


# -------------------------------------------------------------------
# django rest framework
# -------------------------------------------------------------------
REST_FRAMEWORK = {
    # autenticacion por sesion: la api usa el mismo login que las paginas
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    # por defecto ningun endpoint es accesible sin iniciar sesion
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}


# -------------------------------------------------------------------
# endurecimiento de seguridad
# cabeceras siempre activas (sirven sobre http); el resto solo en
# produccion (debug=false) para no estorbar en local.
# -------------------------------------------------------------------
SECURE_CONTENT_TYPE_NOSNIFF = True        # evita que el navegador adivine tipos mime
X_FRAME_OPTIONS = 'DENY'                   # protege contra clickjacking (sin iframes)
SECURE_REFERRER_POLICY = 'same-origin'     # no filtra urls internas a sitios externos

if not DEBUG:
    # cookies no legibles por js (salvo el token csrf, que el kanban
    # necesita leer para enviarlo en las peticiones fetch)
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SAMESITE = 'Lax'

    # https: activar solo si la instancia tiene certificado tls.
    # se controla por variable de entorno para no romper el despliegue
    # http de aws academy (sin dominio ni certificado).
    USAR_HTTPS = os.getenv('USAR_HTTPS', 'False') == 'True'
    SESSION_COOKIE_SECURE = USAR_HTTPS     # cookie de sesion solo por https
    CSRF_COOKIE_SECURE = USAR_HTTPS        # cookie csrf solo por https
    SECURE_SSL_REDIRECT = USAR_HTTPS       # redirige todo el trafico a https
    if USAR_HTTPS:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
        SECURE_HSTS_SECONDS = 31536000     # obliga https por 1 año (hsts)
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

    # impide desplegar en produccion con la clave de ejemplo
    if SECRET_KEY == 'django-insecure-dev-key-cambiar-en-produccion':
        raise RuntimeError(
            'Define una SECRET_KEY real en el archivo .env antes de desplegar (DEBUG=False).'
        )
