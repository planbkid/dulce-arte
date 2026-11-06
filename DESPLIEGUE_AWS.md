# ☁️ Despliegue en AWS EC2 — Dulce Arte

Guía paso a paso para dejar la aplicación **pública y funcional** en una instancia EC2
(AWS Academy). Reemplaza `<IP_PUBLICA>` por la IP pública real de tu instancia.

> ⚠️ En AWS Academy, cada vez que reinicias el **Learner Lab** la IP pública **cambia**:
> deberás actualizar `ALLOWED_HOSTS` en el `.env` y la config de Nginx.

---

## 1. Lanzar la instancia
1. AWS Academy → **Start Lab** (espera el punto verde) → **AWS**.
2. **EC2 → Launch Instance**:
   - Nombre: `dulce-arte`
   - AMI: **Ubuntu Server 22.04 LTS**
   - Tipo: `t2.micro`
   - Key pair: crea y descarga el `.pem`
3. **Network settings → Security Group (Inbound rules):**
   - SSH (22) — My IP
   - HTTP (80) — Anywhere 0.0.0.0/0
4. Launch. Copia la **IPv4 pública**.

## 2. Conectarse
```bash
chmod 400 tu-clave.pem
ssh -i tu-clave.pem ubuntu@<IP_PUBLICA>
```

## 3. Instalar dependencias del sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx git
```

## 4. Crear la base de datos PostgreSQL
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

## 5. Clonar y configurar el proyecto
```bash
cd ~
git clone https://github.com/planbkid/dulce-arte.git
cd dulce-arte
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Crear el `.env` (`nano .env`):
```env
SECRET_KEY=una-clave-larga-y-aleatoria-para-produccion
DEBUG=False
ALLOWED_HOSTS=<IP_PUBLICA>,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://<IP_PUBLICA>

DB_NAME=dulcearte_db
DB_USER=dulce_user
DB_PASSWORD=TuClaveSegura123
DB_HOST=localhost
DB_PORT=5432
```

Migrar, datos demo, estáticos y superusuario:
```bash
python manage.py migrate
python manage.py seed_demo          # opcional (datos de ejemplo)
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Prueba rápida (Ctrl+C para salir):
```bash
gunicorn --bind 0.0.0.0:8000 dulce_arte.wsgi
```

## 6. Gunicorn como servicio (systemd)
`sudo nano /etc/systemd/system/gunicorn.service`
```ini
[Unit]
Description=gunicorn daemon Dulce Arte
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/dulce-arte
ExecStart=/home/ubuntu/dulce-arte/env/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/ubuntu/dulce-arte/gunicorn.sock \
          dulce_arte.wsgi:application

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
sudo systemctl status gunicorn   # debe aparecer "active (running)"
```

## 7. Nginx como proxy inverso
`sudo nano /etc/nginx/sites-available/dulce_arte`
```nginx
server {
    listen 80;
    server_name <IP_PUBLICA>;

    client_max_body_size 10M;   # permite subir imágenes (diseño/firma)

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
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo chmod 755 /home/ubuntu          # para que Nginx pueda leer la carpeta
```

## 8. Verificar
Abre en el navegador: **http://\<IP_PUBLICA\>/**
Pruébalo también desde el **celular con datos móviles** (confirma que es público).

Pega la IP en `README.md`, haz commit y push:
```bash
# en tu PC
git add README.md && git commit -m "Agregar IP pública de AWS" && git push
```

---

## 🔧 Si algo falla
| Síntoma | Solución |
|---|---|
| `502 Bad Gateway` | `sudo systemctl status gunicorn` y `sudo journalctl -u gunicorn` |
| `DisallowedHost` | Agrega la IP a `ALLOWED_HOSTS` en `.env` y reinicia gunicorn |
| CSS no carga | `python manage.py collectstatic` + bloque `location /static/` + `chmod 755 /home/ubuntu` |
| No conecta a BD | revisa credenciales en `.env` y `sudo systemctl status postgresql` |
| Tras reiniciar el Lab | IP nueva → actualiza `.env` (ALLOWED_HOSTS/CSRF) y `server_name` en Nginx, reinicia ambos servicios |

Después de cambiar `.env` o la config:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```
