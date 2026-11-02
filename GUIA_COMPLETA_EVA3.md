# 🍰 GUÍA COMPLETA — EVA 3 Backend · Proyecto 3 "Dulce Arte"

**Alumno:** Cristóbal Barriga · **Grupo 3** · Django/DRF + PostgreSQL + AWS EC2
**Stack recomendado:** Django Templates (HTML/CSS/JS) + algunos endpoints DRF para el Kanban.

> Orden de trabajo: Fase 0 → 1 → 2 → 3 (aseguran BD + Admin + CRUD) → 4 (seguridad/front) → 5 (docs) → 6 (AWS).
> Cada vez que uses IA, copia el prompt en `prompts_ia.md` (ver Fase 5).

---

## ✅ Checklist general (rúbrica = 5 criterios, 20 pts c/u)

- [ ] **C1** PostgreSQL conectado + migraciones aplicadas (en local y en EC2)
- [ ] **C2** Django Admin con TODOS los modelos + `list_display`, filtros y búsqueda
- [ ] **C3** CRUD + las 4 reglas de negocio (pedidos, Kanban, BOM/inventario, despacho+firma)
- [ ] **C4** Login/sesiones/permisos por rol + `prompts_ia.md`
- [ ] **C5** Desplegado y público en AWS EC2 + defensa en vivo
- [ ] Repo público con `README.md` (incluye IP pública) y `prompts_ia.md`

---

# FASE 0 — Entorno local

```bash
cd ~/Documentos/backend/eva3

# entorno virtual
python3 -m venv env
source env/bin/activate

# dependencias
pip install django djangorestframework psycopg2-binary python-dotenv pillow django-filter gunicorn
pip freeze > requirements.txt

# crear proyecto (el punto final = en la carpeta actual)
django-admin startproject dulce_arte .

# crear apps
python manage.py startapp usuarios
python manage.py startapp inventario
python manage.py startapp pedidos
python manage.py startapp despacho
```

Crea el archivo **`.gitignore`**:

```gitignore
env/
__pycache__/
*.pyc
*.sqlite3
.env
media/
staticfiles/
```

Inicia Git:

```bash
git init
git add .
git commit -m "Fase 0: estructura inicial del proyecto Dulce Arte"
```

---

# FASE 1 — PostgreSQL (Criterio 1)

### 1.1 Instalar y crear la base (local, Fedora)

```bash
sudo dnf install postgresql postgresql-server -y
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql

# entrar como usuario postgres
sudo -u postgres psql
```

Dentro de `psql`:

```sql
CREATE DATABASE dulcearte_db;
CREATE USER dulce_user WITH PASSWORD 'TuClaveSegura123';
ALTER ROLE dulce_user SET client_encoding TO 'utf8';
ALTER ROLE dulce_user SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE dulcearte_db TO dulce_user;
\c dulcearte_db
GRANT ALL ON SCHEMA public TO dulce_user;
\q
```

### 1.2 Archivo `.env` (en la raíz, junto a manage.py)

```env
SECRET_KEY=pon-aqui-una-clave-larga-y-aleatoria
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=dulcearte_db
DB_USER=dulce_user
DB_PASSWORD=TuClaveSegura123
DB_HOST=localhost
DB_PORT=5432
```

Crea también `.env.example` (igual pero sin claves reales) para subirlo al repo.

### 1.3 Editar `dulce_arte/settings.py`

Al inicio del archivo:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-inseguro')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
```

`INSTALLED_APPS` — agrega al final:

```python
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

    # apps propias
    'usuarios',
    'inventario',
    'pedidos',
    'despacho',
]
```

Base de datos (reemplaza el bloque `DATABASES`):

```python
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
```

Templates (en el bloque `TEMPLATES`, campo `'DIRS'`):

```python
'DIRS': [BASE_DIR / 'templates'],
```

Al final del `settings.py`:

```python
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'kanban'
LOGOUT_REDIRECT_URL = 'login'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
```

### 1.4 Probar conexión

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Si entra a `http://127.0.0.1:8000/admin/` → **Criterio 1 funcionando en local.** ✔️

---

# FASE 2 — Modelos del dominio (Criterio 3, parte 1)

### 2.1 `inventario/models.py`

```python
from django.db import models


class Insumo(models.Model):
    UNIDADES = [
        ('g', 'Gramos'), ('kg', 'Kilogramos'),
        ('ml', 'Mililitros'), ('l', 'Litros'), ('un', 'Unidades'),
    ]
    nombre = models.CharField(max_length=120, unique=True)
    unidad = models.CharField(max_length=2, choices=UNIDADES, default='un')
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.nombre} ({self.stock} {self.unidad})"

    @property
    def bajo_stock(self):
        return self.stock <= self.stock_minimo


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class ProductoInsumo(models.Model):
    """Lista de Materiales (BOM): qué insumos y cuánto usa cada producto."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='receta')
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('producto', 'insumo')
        verbose_name = 'Insumo de la receta'
        verbose_name_plural = 'Receta (BOM)'

    def __str__(self):
        return f"{self.producto}: {self.cantidad} {self.insumo.unidad} de {self.insumo.nombre}"
```

### 2.2 `pedidos/models.py`

```python
from collections import defaultdict
from django.conf import settings
from django.db import models, transaction
from inventario.models import Producto, Insumo


class StockInsuficiente(Exception):
    pass


class Pedido(models.Model):
    RECIBIDO = 'RECIBIDO'
    PREPARACION = 'PREPARACION'
    HORNEADO = 'HORNEADO'
    CALIDAD = 'CALIDAD'
    LISTO = 'LISTO'
    ESTADOS = [
        (RECIBIDO, 'Recibido'),
        (PREPARACION, 'En Preparación'),
        (HORNEADO, 'Horneado/Decorado'),
        (CALIDAD, 'Control de Calidad'),
        (LISTO, 'Listo'),
    ]

    cliente_nombre = models.CharField(max_length=120)
    cliente_telefono = models.CharField(max_length=30, blank=True)
    descripcion_diseno = models.TextField('Diseño / personalización', blank=True)
    imagen_referencia = models.ImageField(upload_to='disenos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default=RECIBIDO)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insumos_descontados = models.BooleanField(default=False)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente_nombre}"

    def recalcular_total(self):
        self.total = sum(d.subtotal() for d in self.detalles.all())
        self.save(update_fields=['total'])

    def descontar_insumos(self):
        """Descuenta del inventario según la BOM. Se llama al pasar a 'En Preparación'."""
        if self.insumos_descontados:
            return
        requerimientos = defaultdict(float)
        for det in self.detalles.select_related('producto'):
            for item in det.producto.receta.all():
                requerimientos[item.insumo_id] += float(item.cantidad) * det.cantidad

        with transaction.atomic():
            # validar stock
            for insumo_id, cant in requerimientos.items():
                insumo = Insumo.objects.select_for_update().get(pk=insumo_id)
                if float(insumo.stock) < cant:
                    raise StockInsuficiente(
                        f"Stock insuficiente de {insumo.nombre} "
                        f"(necesita {cant}, hay {insumo.stock})"
                    )
            # descontar
            for insumo_id, cant in requerimientos.items():
                insumo = Insumo.objects.select_for_update().get(pk=insumo_id)
                insumo.stock = float(insumo.stock) - cant
                insumo.save()
            self.insumos_descontados = True
            self.save(update_fields=['insumos_descontados'])


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    personalizacion = models.CharField(max_length=255, blank=True)

    def subtotal(self):
        return self.producto.precio_base * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.producto}"
```

### 2.3 `despacho/models.py`

```python
from django.conf import settings
from django.db import models
from pedidos.models import Pedido


class Despacho(models.Model):
    PENDIENTE = 'PENDIENTE'
    EN_RUTA = 'EN_RUTA'
    ENTREGADO = 'ENTREGADO'
    ESTADOS = [
        (PENDIENTE, 'Pendiente'),
        (EN_RUTA, 'En ruta'),
        (ENTREGADO, 'Entregado'),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='despacho')
    repartidor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    direccion = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    firma = models.ImageField('Firma digital / comprobante', upload_to='firmas/', blank=True, null=True)
    fecha_entrega_real = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Despacho Pedido #{self.pedido_id} - {self.get_estado_display()}"
```

> **Nota sobre roles (Criterio 4):** no uses modelo de usuario personalizado (es riesgoso a mitad de proyecto). Usa los **Grupos** de Django: crearás los grupos `Cajero`, `Cocina`, `Despacho` desde el Admin (Fase 3) y validarás permisos con decoradores (Fase 4).

### 2.4 Migrar

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# FASE 3 — Django Admin personalizado (Criterio 2)

### 3.1 `inventario/admin.py`

```python
from django.contrib import admin
from .models import Insumo, Producto, ProductoInsumo


@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad', 'stock', 'stock_minimo', 'bajo_stock')
    list_filter = ('unidad',)
    search_fields = ('nombre',)


class ProductoInsumoInline(admin.TabularInline):
    model = ProductoInsumo
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_base', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
    inlines = [ProductoInsumoInline]
```

### 3.2 `pedidos/admin.py`

```python
from django.contrib import admin
from .models import Pedido, DetallePedido


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'estado', 'fecha_entrega', 'total', 'insumos_descontados')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('cliente_nombre', 'cliente_telefono')
    inlines = [DetallePedidoInline]
    readonly_fields = ('fecha_creacion', 'total')
```

### 3.3 `despacho/admin.py`

```python
from django.contrib import admin
from .models import Despacho


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'repartidor', 'estado', 'direccion', 'fecha_entrega_real')
    list_filter = ('estado',)
    search_fields = ('pedido__cliente_nombre', 'direccion')
```

Entra a `/admin/`, verifica que aparezcan **todos** los modelos. Crea los **Grupos** `Cajero`, `Cocina`, `Despacho` en *Authentication and Authorization → Groups* y asígnales permisos. → **Criterio 2 listo.** ✔️

```bash
git add . && git commit -m "Fases 2-3: modelos + Django Admin personalizado"
```

---

# FASE 4 — Vistas, Kanban, Frontend y Seguridad (Criterios 3 y 4)

### 4.1 Endpoint DRF para mover tarjetas del Kanban

`pedidos/serializers.py`:

```python
from rest_framework import serializers
from .models import Pedido, DetallePedido


class DetallePedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'personalizacion']


class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = '__all__'
```

`pedidos/api.py`:

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pedido, StockInsuficiente
from .serializers import PedidoSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('fecha_entrega')
    serializer_class = PedidoSerializer
    filterset_fields = ['estado']

    @action(detail=True, methods=['post'])
    def mover_estado(self, request, pk=None):
        pedido = self.get_object()
        nuevo = request.data.get('estado')
        if nuevo not in dict(Pedido.ESTADOS):
            return Response({'error': 'Estado inválido'}, status=400)
        # Al pasar a preparación, descontar inventario (BOM)
        if nuevo == Pedido.PREPARACION and not pedido.insumos_descontados:
            try:
                pedido.descontar_insumos()
            except StockInsuficiente as e:
                return Response({'error': str(e)}, status=400)
        pedido.estado = nuevo
        pedido.save(update_fields=['estado'])
        return Response({'ok': True, 'estado': pedido.estado})
```

`pedidos/api_urls.py`:

```python
from rest_framework.routers import DefaultRouter
from .api import PedidoViewSet

router = DefaultRouter()
router.register('pedidos', PedidoViewSet)
urlpatterns = router.urls
```

### 4.2 Vistas de páginas (templates)

`pedidos/views.py`:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Pedido


@login_required
def kanban(request):
    columnas = []
    for valor, etiqueta in Pedido.ESTADOS:
        columnas.append({
            'clave': valor,
            'titulo': etiqueta,
            'pedidos': Pedido.objects.filter(estado=valor).order_by('fecha_entrega'),
        })
    return render(request, 'pedidos/kanban.html', {'columnas': columnas})
```

> El **CRUD de pedidos** puedes resolverlo rápido con `CreateView/UpdateView/DeleteView/ListView` de Django (genéricos) o, más simple aún, hacerlo desde el **Django Admin** (que ya cuenta como CRUD válido). Para subir nota, agrega al menos un formulario propio de "Nuevo Pedido" con `ModelForm`.

`pedidos/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.kanban, name='kanban'),
]
```

### 4.3 URLs del proyecto — `dulce_arte/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('pedidos.urls')),
    path('despacho/', include('despacho.urls')),
    path('api/', include('pedidos.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4.4 Templates

`templates/base.html`:

```html
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dulce Arte{% block titulo %}{% endblock %}</title>
  <style>
    body{font-family:system-ui,Arial,sans-serif;margin:0;background:#faf6f2;color:#3a2b24}
    header{background:#8d5524;color:#fff;padding:12px 20px;display:flex;justify-content:space-between;align-items:center}
    header a{color:#fff;margin-left:12px;text-decoration:none}
    main{padding:20px;max-width:1200px;margin:0 auto}
    .board{display:flex;gap:12px;overflow-x:auto}
    .col{background:#fff;border-radius:10px;padding:10px;min-width:220px;flex:1}
    .col h3{margin:0 0 8px;font-size:14px;text-align:center;background:#f0e2d5;padding:6px;border-radius:6px}
    .card{background:#fff;border:1px solid #e3d3c5;border-radius:8px;padding:8px;margin-bottom:8px;box-shadow:0 1px 2px rgba(0,0,0,.06)}
    button{cursor:pointer;border:0;background:#8d5524;color:#fff;border-radius:6px;padding:4px 8px;font-size:12px}
  </style>
</head>
<body>
  <header>
    <strong>🍰 Dulce Arte</strong>
    <nav>
      <a href="{% url 'kanban' %}">Kanban</a>
      <a href="/admin/">Admin</a>
      <a href="{% url 'logout' %}">Salir</a>
    </nav>
  </header>
  <main>{% block contenido %}{% endblock %}</main>
</body>
</html>
```

`templates/login.html`:

```html
{% extends 'base.html' %}
{% block contenido %}
<h2>Iniciar sesión</h2>
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Entrar</button>
</form>
{% endblock %}
```

`templates/pedidos/kanban.html` (el tablero con `fetch` al endpoint DRF):

```html
{% extends 'base.html' %}
{% block contenido %}
<h2>Tablero de Cocina</h2>
<div class="board">
  {% for col in columnas %}
  <div class="col">
    <h3>{{ col.titulo }}</h3>
    {% for p in col.pedidos %}
      <div class="card">
        <strong>#{{ p.id }}</strong> {{ p.cliente_nombre }}<br>
        <small>Entrega: {{ p.fecha_entrega|date:"d/m H:i" }}</small><br>
        <select onchange="mover({{ p.id }}, this.value)">
          {% for val, lbl in p.ESTADOS %}
            <option value="{{ val }}" {% if val == p.estado %}selected{% endif %}>{{ lbl }}</option>
          {% endfor %}
        </select>
      </div>
    {% empty %}<small>Sin pedidos</small>{% endfor %}
  </div>
  {% endfor %}
</div>

<script>
function getCookie(name){
  const v = document.cookie.match('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}
async function mover(id, estado){
  const r = await fetch(`/api/pedidos/${id}/mover_estado/`, {
    method:'POST',
    headers:{'Content-Type':'application/json','X-CSRFToken':getCookie('csrftoken')},
    body: JSON.stringify({estado})
  });
  const data = await r.json();
  if(!r.ok){ alert(data.error || 'Error'); location.reload(); }
  else { location.reload(); }
}
</script>
{% endblock %}
```

### 4.5 Despacho con firma (Criterio 3, parte 4)

`despacho/forms.py`:

```python
from django import forms
from .models import Despacho

class ConfirmarEntregaForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ['firma']  # sube imagen de firma/comprobante
```

`despacho/views.py`:

```python
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Despacho
from .forms import ConfirmarEntregaForm


@login_required
def lista_despachos(request):
    despachos = Despacho.objects.select_related('pedido').all()
    return render(request, 'despacho/lista.html', {'despachos': despachos})


@login_required
def confirmar_entrega(request, pk):
    desp = get_object_or_404(Despacho, pk=pk)
    if request.method == 'POST':
        form = ConfirmarEntregaForm(request.POST, request.FILES, instance=desp)
        if form.is_valid():
            desp = form.save(commit=False)
            desp.estado = Despacho.ENTREGADO
            desp.fecha_entrega_real = timezone.now()
            desp.save()
            return redirect('lista_despachos')
    else:
        form = ConfirmarEntregaForm(instance=desp)
    return render(request, 'despacho/confirmar.html', {'form': form, 'desp': desp})
```

`despacho/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_despachos, name='lista_despachos'),
    path('<int:pk>/confirmar/', views.confirmar_entrega, name='confirmar_entrega'),
]
```

> Crea `templates/despacho/lista.html` y `templates/despacho/confirmar.html` con un `<form method="post" enctype="multipart/form-data">` (el `enctype` es obligatorio para subir la firma).

### 4.6 Seguridad / permisos por rol (Criterio 4)

- Todas las vistas ya llevan `@login_required`.
- Para restringir por rol, usa `@permission_required` o revisa el grupo. Ejemplo (solo Cocina mueve el Kanban):

```python
from django.contrib.auth.decorators import user_passes_test

def es_cocina(u):
    return u.is_superuser or u.groups.filter(name='Cocina').exists()

# @user_passes_test(es_cocina)  ->  ponlo sobre la vista que corresponda
```

```bash
git add . && git commit -m "Fase 4: Kanban, despacho con firma, templates y seguridad"
```

---

# FASE 5 — Documentación (parte del Criterio 4)

### `prompts_ia.md` (OBLIGATORIO)

```markdown
# Registro de uso de IA — Dulce Arte (EVA3)
Alumno: Cristóbal Barriga

## Prompt 1
**Consulta:** "Dame la receta completa para el proyecto 3 de backend (Dulce Arte) en Django/DRF + PostgreSQL + AWS."
**Apoyo recibido:** Estructura de apps, modelos (Insumo, Producto, BOM, Pedido, Despacho), lógica de descuento de inventario y pasos de despliegue en EC2.
**Qué adapté yo:** [completa con lo que modificaste].

## Prompt 2
...
```

### `README.md`

```markdown
# Dulce Arte — Sistema de Trazabilidad y Pedidos (EVA3 Backend)
Alumno: Cristóbal Barriga · Grupo 3

## 🌐 Aplicación desplegada
http://<IP_PUBLICA_EC2>/        <-- completar al final de la Fase 6

## Tecnologías
Django, Django REST Framework, PostgreSQL, AWS EC2.

## Instalación local
1. `python3 -m venv env && source env/bin/activate`
2. `pip install -r requirements.txt`
3. Copiar `.env.example` a `.env` y completar credenciales de PostgreSQL.
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. `python manage.py runserver`

## Funcionalidades
- Pedidos personalizados con diseño y fecha de entrega
- Tablero Kanban de cocina (5 estados)
- Descuento automático de inventario vía Lista de Materiales (BOM)
- Despacho con confirmación por firma digital
```

---

# FASE 6 — Despliegue en AWS EC2 (Criterio 5)

> Hazlo **con 2-3 días de margen**, no el último día. Vale 20 puntos.

### 6.1 Lanzar la instancia (AWS Academy)

1. Entra a **AWS Academy → Learner Lab → Start Lab** (espera el círculo verde) → **AWS**.
2. **EC2 → Launch Instance**: Ubuntu Server 22.04, tipo `t2.micro`.
3. **Key pair:** crea una y descarga el `.pem`.
4. **Security Group — Inbound rules:** abre
   - SSH (22) desde tu IP
   - HTTP (80) desde 0.0.0.0/0
   - (opcional) Custom TCP 8000 para pruebas
5. Lanza y copia la **IP pública / DNS**.

### 6.2 Conectarte

```bash
chmod 400 tu-clave.pem
ssh -i tu-clave.pem ubuntu@<IP_PUBLICA>
```

### 6.3 Preparar el servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx git -y
```

### 6.4 PostgreSQL en el servidor

```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE dulcearte_db;
CREATE USER dulce_user WITH PASSWORD 'TuClaveSegura123';
GRANT ALL PRIVILEGES ON DATABASE dulcearte_db TO dulce_user;
\c dulcearte_db
GRANT ALL ON SCHEMA public TO dulce_user;
\q
```

### 6.5 Clonar y configurar el proyecto

```bash
git clone https://github.com/<tu-usuario>/dulce-arte.git
cd dulce-arte
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Crea el `.env` en el servidor (nano `.env`), con:
```env
DEBUG=False
ALLOWED_HOSTS=<IP_PUBLICA>,localhost,127.0.0.1
SECRET_KEY=...
DB_NAME=dulcearte_db
DB_USER=dulce_user
DB_PASSWORD=TuClaveSegura123
DB_HOST=localhost
DB_PORT=5432
```

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 6.6 Gunicorn (servidor de aplicación)

Prueba:
```bash
gunicorn --bind 0.0.0.0:8000 dulce_arte.wsgi
```

Servicio systemd — `sudo nano /etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=gunicorn daemon Dulce Arte
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/dulce-arte
ExecStart=/home/ubuntu/dulce-arte/env/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/dulce-arte/gunicorn.sock dulce_arte.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
```

### 6.7 Nginx (servidor web)

`sudo nano /etc/nginx/sites-available/dulce_arte`:

```nginx
server {
    listen 80;
    server_name <IP_PUBLICA>;

    location /static/ {
        alias /home/ubuntu/dulce-arte/staticfiles/;
    }
    location /media/ {
        alias /home/ubuntu/dulce-arte/media/;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/dulce-arte/gunicorn.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/dulce_arte /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
# permisos para que nginx lea la carpeta
sudo chmod 755 /home/ubuntu
```

Abre `http://<IP_PUBLICA>/` en el navegador. Si carga → **Criterio 5 listo.** ✔️
Pega esa IP en el `README.md`, haz commit y push.

---

# ✅ Antes de entregar

- [ ] Repo **público** en GitHub con todo el código
- [ ] `README.md` con la **IP pública real** funcionando
- [ ] `prompts_ia.md` completo
- [ ] App accesible por IP en AWS (pruébala desde el celular con datos móviles)
- [ ] Django Admin con todos los modelos
- [ ] Las 4 funcionalidades demostrables en vivo (pedido → Kanban → descuento de stock → despacho con firma)
- [ ] Subir el **link del repo al AAI**
- [ ] Estudiar para la **prueba de 20 preguntas** (40% de EVA3)

---

### Problemas típicos (y dónde consultarme)
- `psycopg2` no conecta → revisa `.env` y que PostgreSQL esté corriendo.
- `DisallowedHost` → agrega la IP a `ALLOWED_HOSTS`.
- Static no carga en EC2 → `collectstatic` + permisos de carpeta + bloque `location /static/`.
- 502 Bad Gateway → `sudo systemctl status gunicorn` para ver el error.
- AWS Academy se "apaga" → la IP pública **cambia** cada vez que reinicias el Lab; actualiza `ALLOWED_HOSTS` y el README.

**Cuando te trabes en cualquier fase, dime la fase y el error exacto y lo resolvemos.** 🍰
```
