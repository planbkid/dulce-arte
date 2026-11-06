# 🍰 Dulce Arte — Sistema de Trazabilidad y Pedidos

**EVA 3 — Desarrollo Backend** · Alumno: **Cristóbal Barriga** · Grupo 3
Django + Django REST Framework + PostgreSQL + AWS EC2

## 🌐 Aplicación desplegada (AWS EC2)
> **http://3.218.109.138/**

> ⚠️ Instancia de **AWS Academy**: al reiniciar el Lab la IP pública cambia. Si no carga,
> es porque el Lab está detenido o la IP cambió (ver `DESPLIEGUE_AWS.md`).

### 👤 Usuarios y roles (demo)
| Usuario | Rol |
|---|---|
| `admin` | Superusuario (acceso total + Django Admin) |
| `cajero1` | Cajero (registra pedidos y despachos) |
| `cocina1` | Cocina (mueve el tablero Kanban) |
| `despacho1` | Despacho (confirma entregas con firma) |

> 🔑 Las contraseñas se entregan al docente durante la defensa (no se publican por seguridad).

- Panel de administración: **http://3.218.109.138/admin/**

---

## 📋 Descripción
Sistema para la pastelería artesanal **Dulce Arte** que resuelve la falta de coordinación
entre la toma de pedidos personalizados, el inventario de insumos y los tiempos de cocina.

### Funcionalidades (requerimientos del caso)
1. **Cotización y registro de pedidos personalizados** (ingredientes, diseño, fecha/hora de entrega).
2. **Tablero tipo Kanban** del flujo de cocina: `Recibido → En Preparación → Horneado/Decorado → Control de Calidad → Listo`.
3. **Descuento automático de inventario** de insumos mediante **Lista de Materiales (BOM)** al iniciar la preparación.
4. **Gestión de despacho** con confirmación mediante **firma digital / comprobante**.

### Tecnologías
- **Backend:** Django 6.1 + Django REST Framework
- **Base de datos:** PostgreSQL (SQLite como fallback para pruebas locales rápidas)
- **Frontend:** Templates Django (HTML/CSS/JS responsivo) + endpoint DRF asíncrono para el Kanban
- **Seguridad:** autenticación por sesión, login/logout, roles (grupos Cajero, Cocina, Despacho)
- **Despliegue:** AWS EC2 + Gunicorn + Nginx

---

## 🚀 Instalación local

```bash
# 1. Clonar
git clone https://github.com/planbkid/dulce-arte.git
cd dulce-arte

# 2. Entorno virtual
python3 -m venv env
source env/bin/activate        # Windows: env\Scripts\activate

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env           # luego edita .env con tus credenciales
#   (Si dejas DB_NAME vacío en .env, usa SQLite automáticamente.)

# 5. Migraciones
python manage.py migrate

# 6. (Opcional) Datos de demostración
python manage.py seed_demo

# 7. Superusuario
python manage.py createsuperuser

# 8. Levantar
python manage.py runserver
```

Abrir: http://127.0.0.1:8000/ (login) y http://127.0.0.1:8000/admin/

### Usuario de demo (si usaste seed_demo + el superusuario de ejemplo)
- **admin / admin123** (superusuario) — *cámbialo en producción.*

---

## 🗄️ Configurar PostgreSQL (local)

```sql
CREATE DATABASE dulcearte_db;
CREATE USER dulce_user WITH PASSWORD 'TuClaveSegura123';
GRANT ALL PRIVILEGES ON DATABASE dulcearte_db TO dulce_user;
\c dulcearte_db
GRANT ALL ON SCHEMA public TO dulce_user;
```
Luego completa `DB_*` en `.env` y corre `python manage.py migrate`.

---

## ☁️ Despliegue en AWS EC2

Ver la guía detallada paso a paso en **`DESPLIEGUE_AWS.md`**.
Resumen: lanzar instancia Ubuntu → abrir puertos 22 y 80 → instalar PostgreSQL/Python/Nginx →
clonar repo → `.env` con `DEBUG=False` y la IP en `ALLOWED_HOSTS` → `migrate` + `collectstatic` →
Gunicorn (systemd) + Nginx como proxy inverso.

---

## 📁 Estructura del proyecto
```
dulce_arte/      → configuración del proyecto (settings, urls)
usuarios/        → roles y permisos (grupos de Django)
inventario/      → Insumo, Producto, ProductoInsumo (BOM)
pedidos/         → Pedido, DetallePedido, Kanban, API DRF, lógica de descuento BOM
despacho/        → Despacho con firma digital
templates/       → frontend (base, login, kanban, pedidos, inventario, despacho)
```

## 🔐 Seguridad
- **Autenticación por sesión** en todas las vistas y en la API (nada es accesible sin login).
- **Roles (grupos):** **Cajero** registra pedidos/despachos, **Cocina** mueve el Kanban,
  **Despacho** confirma entregas. El superusuario tiene acceso total. Se asignan desde el
  Django Admin. Los grupos los crea `seed_demo`.
- **Endurecimiento de producción** (activo con `DEBUG=False`): cabeceras anti-clickjacking y
  anti-MIME-sniffing, cookies `HttpOnly`/`SameSite`, y bloqueo de arranque si la `SECRET_KEY`
  es la de ejemplo.
- **HTTPS opcional:** pon `USAR_HTTPS=True` en el `.env` solo si la instancia tiene certificado
  TLS (activa cookies seguras, redirección SSL y HSTS).
- **Validación de subidas:** las imágenes (diseño y firma) se limitan a 5 MB.
