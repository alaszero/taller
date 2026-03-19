# Sistema Yekflow — Guía del Servidor en Casa (Ubuntu + Cloudflare)

## Resumen de la Arquitectura

```
PC 1 — Windows (tu escritorio de trabajo)
        ├── app.py            → versión local (Excel)
        ├── Archivos Excel    → base de datos local
        └── Administración → "Generar paquete del servidor" → ZIP

PC 2 — Ubuntu (servidor dedicado en casa)
        ├── taller.service    → app Flask (app_web.py) en puerto 5000
        ├── cloudflared       → túnel seguro a Cloudflare
        └── taller.db         → base de datos SQLite

Trabajadores (celular/PC desde cualquier lugar)
        ↓ HTTPS  yekflow.com
Cloudflare (gratis — DNS + Tunnel)
        ↓ Túnel seguro (conexión saliente desde casa)
PC 2 — Ubuntu (servidor)
```

### Flujo de datos

- **PC 1 (Windows)**: Aquí desarrollas y pruebas cambios. Los datos locales se manejan con archivos Excel.
- **PC 2 (Ubuntu)**: Corre el servidor web 24/7. Los datos de producción se guardan en `taller.db` (SQLite).
- **Los datos NO se sincronizan automáticamente** entre PC 1 y PC 2. Son bases independientes.

---

## Requisitos Previos

- PC con Ubuntu 22.04 LTS (o 20.04) dedicada como servidor
- Conexión a internet estable
- Cuenta gratuita en [cloudflare.com](https://cloudflare.com)
- Dominio comprado (ej: en Hostinger) con DNS apuntando a Cloudflare
- El ZIP de despliegue generado desde el sistema local (PC 1)

---

## PASO 1 — Instalar Ubuntu en la PC Servidor

Si la PC tiene Windows y quieres instalar Ubuntu junto a él (dual boot) o reemplazarlo:

1. Descarga Ubuntu 22.04 LTS desde: https://ubuntu.com/download/desktop
2. Crea un USB booteable con Rufus (Windows) o Balena Etcher
3. Reinicia la PC desde el USB e instala Ubuntu

**Recomendación**: Durante la instalación, elige "Instalación mínima" para ahorrar recursos.

---

## PASO 2 — Ejecutar el Script de Instalación

Una vez en Ubuntu, abre una terminal:

```bash
# Navegar a donde copiaste los archivos
cd ~/Documentos/YekflowExports

# Ejecutar script de instalación
sudo bash setup_ubuntu.sh
```

El script instalará automáticamente:
- Python 3 + pip + venv
- Flask y dependencias (en entorno virtual `/home/taller/venv/`)
- cloudflared (herramienta de Cloudflare Tunnel)
- El servicio systemd `taller` para inicio automático

### Estructura creada en el servidor

```
/home/taller/
├── app/                  → Archivos de la aplicación
│   ├── app_web.py        → Aplicación Flask principal
│   ├── db.py             → Capa de base de datos
│   ├── taller.db         → Base de datos SQLite
│   ├── templates/        → Plantillas HTML
│   └── static/           → CSS, JS, imágenes
├── venv/                 → Entorno virtual Python
└── backups/              → Backups automáticos de taller.db
```

---

## PASO 3 — Subir los Archivos de la App

### Desde PC 1 (Windows):

1. Abre el sistema local → **Administración** → botón **"Generar paquete del servidor"**
2. Se descarga un ZIP (ej: `taller_servidor_20260317_1430.zip`)
3. Copia el ZIP al servidor Ubuntu (USB, carpeta compartida en red, o SCP)

### En PC 2 (Ubuntu):

```bash
# Ejecutar actualización (funciona desde cualquier carpeta)
sudo actualizar-taller /home/serv-bar/Documentos/YekflowExports/taller_servidor_20260317_1430.zip
```

El comando extrae los archivos, actualiza dependencias y reinicia el servicio.

> **Primera vez?** Si el comando `actualizar-taller` no existe, instálalo:
> ```bash
> cd /home/serv-bar/Documentos/YekflowExports
> unzip -o taller_servidor_20260317_1430.zip instalar_actualizador.sh
> sudo bash instalar_actualizador.sh
> ```
> Después de esto, `actualizar-taller` queda instalado permanentemente.

**Nota**: El script NO sobreescribe `taller.db` para proteger los datos de producción. Si es la primera instalación y no hay base de datos:

```bash
sudo unzip -o taller_servidor_20260317_1430.zip taller.db -d /home/taller/app/
sudo systemctl restart taller
```

---

## PASO 4 — Configurar Cloudflare Tunnel (una sola vez)

### 4a. Crear cuenta Cloudflare gratuita

1. Ve a [cloudflare.com](https://cloudflare.com) y crea una cuenta (gratis)
2. Haz clic en **"Add a Site"** y escribe tu dominio (ej: `yekflow.com`)
3. Elige el plan **Free**
4. Cloudflare te dará **2 nameservers**, algo como:
   - `aria.ns.cloudflare.com`
   - `bob.ns.cloudflare.com`

### 4b. Cambiar DNS en Hostinger

1. Entra a [hpanel.hostinger.com](https://hpanel.hostinger.com)
2. Ve a **Dominios** → selecciona tu dominio → **Nameservers**
3. Cambia los nameservers a los que te dio Cloudflare
4. Espera 5–30 minutos para que propague

### 4c. Crear el túnel en el servidor Ubuntu

```bash
# Iniciar sesión con tu cuenta Cloudflare
cloudflared tunnel login

# Crear el túnel (solo una vez)
cloudflared tunnel create taller

# Crear directorio de configuración
sudo mkdir -p /etc/cloudflared
sudo mkdir -p /root/.cloudflared

# Conectar el dominio al túnel
cloudflared tunnel route dns taller yekflow.com

# Crear archivo de configuración
sudo tee /etc/cloudflared/config.yml > /dev/null <<EOF
tunnel: taller
credentials-file: /root/.cloudflared/<ID_DEL_TUNEL>.json
ingress:
  - hostname: yekflow.com
    service: http://localhost:5000
  - service: http_status:404
EOF

# Instalar cloudflared como servicio automático
sudo cloudflared service install
```

**Nota**: Si al ejecutar `cloudflared tunnel route dns` da error de "DNS record already exists", ve al panel de Cloudflare → DNS y elimina el registro A/CNAME existente para tu dominio. Luego repite el comando.

### 4d. Verificar que funciona

```bash
# Ver estado del túnel
systemctl status cloudflared

# Abrir en el navegador de cualquier dispositivo:
# https://yekflow.com → debe aparecer el login del sistema
```

---

## PASO 5 — Primer Acceso

Abre tu dominio en el navegador. Verás la pantalla de inicio de sesión.

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `taller2024`

### Cambiar contraseña (importante)

1. Inicia sesión con `admin` / `taller2024`
2. Ve a **Administración** → **Gestión de Usuarios**
3. Haz clic en el icono de lápiz junto al usuario `admin`
4. Escribe una nueva contraseña segura → Guardar

---

## Roles y Permisos

### Niveles de usuario

| Nivel | Descripción | Secciones por defecto |
|-------|------------|----------------------|
| `superusuario` | Control total del sistema | Todas (incluyendo Administración) |
| `administrador` | Gestión operativa completa | Dashboard, Almacen, Herramientas, Proyectos, Avance, Empleados |
| `supervisor` | Seguimiento de obras | Proyectos, Avance de Obras |
| `usuario` | Operación básica | Almacen, Herramientas |

### Permisos modulares por sección

Cada usuario tiene un campo `secciones` que define exactamente a qué partes del sistema puede acceder. Al crear un usuario, las secciones se auto-populan según el nivel seleccionado, pero **el administrador puede personalizar las secciones individualmente** usando los checkboxes en el modal de usuario.

Las secciones disponibles son:
- **Dashboard** — Panel principal con KPIs
- **Almacen** — Gestión de materiales e inventario
- **Herramientas** — Control de herramientas
- **Proyectos** — Gestión de proyectos
- **Avance** — Avance de obras y reportes
- **Empleados** — Gestión de personal
- **Implementacion** — Documentación de implementación
- **Admin** — Panel de administración (usuarios, backup, configuración)

### Crear usuarios

En **Administración** → **Gestión de Usuarios** → **Nuevo Usuario**:

1. Ingresa usuario y contraseña
2. Selecciona el nivel (las secciones se auto-populan)
3. Opcionalmente ajusta las secciones manualmente con los checkboxes
4. Guardar

---

## Session Timeout (Expiración de Sesión)

El sistema cierra automáticamente las sesiones inactivas. Por defecto, el timeout es de **30 minutos**.

- A los **2 minutos** antes de expirar, aparece un aviso en pantalla
- El usuario puede hacer clic en "Renovar" para extender la sesión
- Si no hay actividad, se redirige automáticamente al login

### Cambiar el tiempo de timeout

Editar la variable de entorno en el servicio:

```bash
sudo nano /etc/systemd/system/taller.service

# Agregar o modificar:
Environment="SESSION_TIMEOUT=30"
# (valor en minutos, ej: 60 para 1 hora)

sudo systemctl daemon-reload
sudo systemctl restart taller
```

---

## PASO 6 — Configurar Clave Secreta (seguridad)

La `SECRET_KEY` protege las sesiones de usuario. Debes cambiarla:

```bash
sudo nano /etc/systemd/system/taller.service

# Cambia esta línea:
Environment="SECRET_KEY=CAMBIAR_POR_CLAVE_SEGURA_ALEATORIA"
# Por una clave larga y aleatoria, por ejemplo:
Environment="SECRET_KEY=x7k2mP9nQvR4wJ8tF3hL6yA1sD5uE0bC"

# Guardar (Ctrl+O, Enter, Ctrl+X) y recargar
sudo systemctl daemon-reload
sudo systemctl restart taller
```

---

## Flujo de Trabajo para Actualizar el Sistema

### Resumen rapido

```
PC Windows (desarrollo)                    PC Ubuntu (servidor)
─────────────────────                      ────────────────────
1. Modificas el codigo
2. Pruebas en http://127.0.0.1:5000
3. Admin → "Generar paquete servidor"
4. Se descarga un ZIP
5. Copias el ZIP al servidor ────────────► /home/serv-bar/Documentos/YekflowExports/
                                           6. sudo actualizar-taller /ruta/al.zip
                                           7. Listo — yekflow.com actualizado
```

### Paso a paso en el servidor Ubuntu

#### 1. Copiar el ZIP al servidor

Desde tu PC Windows, copia el ZIP generado al servidor. Puedes usar:
- **USB**: Copia el ZIP al USB → conecta al servidor → copia a la carpeta
- **Red local (recomendado)**: Si ambas PCs estan en la misma red, comparte la carpeta o usa SCP:

```bash
# Desde Windows (PowerShell) — enviar ZIP por SCP:
scp taller_servidor_20260317_1430.zip serv-bar@192.168.100.156:/home/serv-bar/Documentos/YekflowExports/
```

#### 2. Ejecutar la actualización en el servidor

Abre una terminal en Ubuntu y ejecuta:

```bash
# Ver que ZIPs hay disponibles
ls -la /home/serv-bar/Documentos/YekflowExports/*.zip

# Ejecutar la actualizacion (cambia el nombre por el ZIP que copiaste)
sudo actualizar-taller /home/serv-bar/Documentos/YekflowExports/taller_servidor_20260317_1430.zip
```

El comando automaticamente:
1. Hace backup de `taller.db` antes de tocar nada
2. Extrae los archivos nuevos (templates, CSS, Python, etc.)
3. **NO sobreescribe `taller.db`** — los datos de produccion se mantienen intactos
4. Actualiza dependencias Python si hay cambios en `requirements.txt`
5. Reinicia el servicio `taller`

#### 3. Verificar que funciono

```bash
# Ver que el servicio esta corriendo
systemctl status taller

# Ver los logs para confirmar que no hay errores
journalctl -u taller -n 20

# Probar localmente
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000
# Debe responder: 302 (redirect a login) o 200
```

Luego abre https://yekflow.com en el navegador y verifica los cambios.

### Importar base de datos al servidor

Si necesitas reemplazar la base de datos del servidor con una nueva (ej: primera instalacion):

```bash
# Detener el servicio
sudo systemctl stop taller

# Hacer backup del actual (si existe)
sudo cp /home/taller/app/taller.db /home/taller/backups/taller_$(date +%Y%m%d_%H%M%S).db

# Copiar la nueva base de datos
sudo cp /home/serv-bar/Documentos/YekflowExports/taller.db /home/taller/app/taller.db

# Ajustar permisos
sudo chown taller:taller /home/taller/app/taller.db

# Reiniciar
sudo systemctl start taller
```

---

## Encender y Apagar el Servidor

### Encender

1. Enciende la PC Ubuntu normalmente
2. Los servicios `taller` y `cloudflared` **se inician automaticamente** (gracias a `systemctl enable`)
3. En 1-2 minutos, `yekflow.com` estara accesible

### Apagar correctamente

```bash
# Opcion 1: Apagar desde terminal
sudo shutdown now

# Opcion 2: Apagar en X minutos (avisa a los usuarios)
sudo shutdown +5 "El servidor se apagara en 5 minutos"

# Opcion 3: Solo detener servicios sin apagar la PC
sudo systemctl stop taller
sudo systemctl stop cloudflared
```

### Reiniciar servicios (sin apagar la PC)

```bash
sudo systemctl restart taller              # Reiniciar solo la app
sudo systemctl restart cloudflared         # Reiniciar solo el tunel
sudo systemctl restart taller cloudflared  # Reiniciar ambos
```

---

## Comandos Utiles del Servidor

### Estado y control

```bash
# ── Ver estado ──
systemctl status taller          # Estado de la app
systemctl status cloudflared     # Estado del tunel Cloudflare

# ── Iniciar / Detener / Reiniciar ──
sudo systemctl start taller      # Iniciar la app
sudo systemctl stop taller       # Detener la app
sudo systemctl restart taller    # Reiniciar la app
```

### Logs y monitoreo en vivo

```bash
# ── Logs de la app (Flask) ──
journalctl -u taller -f                    # Ver trafico y logs EN VIVO (Ctrl+C para salir)
journalctl -u taller -n 50                 # Ultimas 50 lineas de log
journalctl -u taller --since "10 min ago"  # Logs de los ultimos 10 minutos
journalctl -u taller --since today         # Todo lo de hoy

# ── Logs del tunel Cloudflare ──
journalctl -u cloudflared -f               # Trafico del tunel en vivo
journalctl -u cloudflared -n 30            # Ultimas 30 lineas

# ── Logs combinados (app + tunel) ──
journalctl -u taller -u cloudflared -f     # Ambos servicios en vivo
```

### Monitoreo de red y conexiones

```bash
# ── Ver conexiones activas al puerto 5000 ──
ss -tnp | grep :5000                       # Conexiones TCP activas a la app
ss -tnp | grep :5000 | wc -l              # Contar conexiones activas

# ── Ver IP del servidor ──
ip addr show | grep "inet "                # IPs asignadas al servidor
hostname -I                                # IP rapida

# ── Verificar que la app responde ──
curl -s http://localhost:5000              # Probar respuesta local
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:5000  # Solo codigo HTTP

# ── Ver uso de red en tiempo real (requiere instalar) ──
# sudo apt install iftop
sudo iftop -i eth0                         # Trafico de red en vivo (Ctrl+C para salir)

# ── Ver puertos abiertos ──
sudo ss -tlnp                              # Todos los puertos escuchando
```

### Base de datos y backups

```bash
# ── Ver base de datos ──
ls -lh /home/taller/app/taller.db         # Tamano de la BD
ls -lh /home/taller/backups/              # Ver backups disponibles
ls -lt /home/taller/backups/ | head -5    # Los 5 backups mas recientes

# ── Backup manual rapido ──
sudo cp /home/taller/app/taller.db /home/taller/backups/taller_manual_$(date +%Y%m%d_%H%M%S).db
```

### Recursos del sistema

```bash
# ── Ver uso de CPU y memoria ──
htop                                       # Monitor interactivo (Ctrl+C para salir)
free -h                                    # Memoria RAM disponible
df -h /                                    # Espacio en disco

# ── Ver procesos de la app ──
ps aux | grep app_web                      # Proceso Flask corriendo
```

### Referencia rapida (cheat sheet)

| Accion | Comando |
|--------|---------|
| Ver trafico en vivo | `journalctl -u taller -f` |
| Ver errores recientes | `journalctl -u taller -p err -n 20` |
| Estado de la app | `systemctl status taller` |
| Reiniciar app | `sudo systemctl restart taller` |
| Detener app | `sudo systemctl stop taller` |
| Iniciar app | `sudo systemctl start taller` |
| Actualizar app | `sudo actualizar-taller /home/serv-bar/Documentos/YekflowExports/NOMBRE.zip` |
| Ver conexiones | `ss -tnp \| grep :5000` |
| Apagar servidor | `sudo shutdown now` |
| Ver IP | `hostname -I` |
| Backup manual BD | `sudo cp /home/taller/app/taller.db /home/taller/backups/taller_manual_$(date +%Y%m%d_%H%M%S).db` |

---

## Backup y Restauracion

### Backup automatico al actualizar

Cada vez que corres `actualizar-taller`, se hace un backup automatico de `taller.db` en `/home/taller/backups/`.

### Backup manual desde el panel

Entra al sistema web → **Administracion** → **Backup y Restauracion** → **Descargar backup**

### Restaurar un backup

Desde el panel: Admin → Backup → **Restaurar** → sube el archivo `.db`

O desde la terminal:
```bash
sudo systemctl stop taller
sudo cp /home/taller/backups/taller_20260317_143000.db /home/taller/app/taller.db
sudo systemctl start taller
```

---

## Acceso por Red Local (LAN)

Si estas en la misma red que el servidor, puedes acceder directamente sin pasar por Cloudflare:

```
http://192.168.x.x:5000
```

Para encontrar la IP del servidor: `ip addr show` en la terminal de Ubuntu.

---

## Solucion de Problemas

| Problema | Solucion |
|----------|----------|
| No carga el sistema al entrar al dominio | `systemctl status taller` — ver si la app esta corriendo |
| Error 500 | `journalctl -u taller -n 50` — buscar el error en los logs |
| El dominio no abre pero la LAN si | `systemctl status cloudflared` — verificar el tunel |
| Los cambios del ZIP no aparecen | Verificar que se ejecuto `actualizar-taller` y que el servicio se reinicio |
| Login no funciona | Verificar que `taller.db` existe en `/home/taller/app/` |
| La PC se apago y todo se detuvo | Al encender, los servicios se reinician solos (`systemctl enable`) |
| Olvide la contrasena de admin | Ver seccion "Resetear contrasena" abajo |
| Session expira muy rapido | Cambiar `SESSION_TIMEOUT` en taller.service (ver seccion Session Timeout) |
| Pagina vieja aparece en el navegador | Limpiar cache del navegador o abrir en ventana de incognito |

---

## Resetear contrasena admin desde terminal (emergencia)

```bash
cd /home/taller/app
source /home/taller/venv/bin/activate
python3 -c "
import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect('taller.db')
conn.execute(\"UPDATE USUARIOS SET password_hash=? WHERE username='admin'\",
             (generate_password_hash('nueva_contrasena'),))
conn.commit()
conn.close()
print('Contrasena cambiada.')
"
```

---

*Sistema Yekflow — v3.0 | Servidor Ubuntu + Cloudflare Tunnel | yekflow.com*
