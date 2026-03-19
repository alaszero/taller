# Sistema de Taller — Guía de despliegue en Hostinger Business

## Requisito: Plan Hostinger Business o superior

El plan **Premium** de Hostinger **no incluye** soporte para aplicaciones Python.
Debes estar en el plan **Business** (o superior) para continuar.

Para actualizar: hPanel → **Mi cuenta** → **Actualizar plan** → Business.

---

## Contenido del paquete

| Archivo | Descripción |
|---------|-------------|
| `app.py` | Aplicación Flask (versión producción, usa SQLite) |
| `db.py` | Capa de acceso a datos SQLite |
| `passenger_wsgi.py` | Punto de entrada WSGI para Hostinger |
| `.htaccess` | Configuración Apache + Passenger |
| `requirements.txt` | Dependencias Python (`flask` únicamente) |
| `taller.db` | Base de datos SQLite con tus datos actuales |
| `templates/` | Plantillas HTML de la interfaz |
| `static/` | CSS y JavaScript |
| `generar_manual.py` | Generador del manual de usuario |

---

## Pasos de instalación

### Paso 1 — Subir los archivos

1. En **hPanel** → **Administrador de Archivos** (o usa FileZilla por FTP).
2. Navega a `domains/TU_DOMINIO/public_html/`.
3. **Sube todos los archivos del ZIP** manteniendo la estructura de carpetas.
   - `app.py`, `db.py`, `passenger_wsgi.py`, `.htaccess`, `requirements.txt`, `taller.db`
   - Carpetas: `templates/`, `static/`

> ⚠️ **No uses la herramienta de Migración** — es solo para WordPress/PHP.
> Usa el Administrador de Archivos o FTP directamente.

---

### Paso 2 — Crear la aplicación Python

1. En **hPanel** → **Sitios Web** → selecciona tu dominio.
2. Busca **Python** (puede estar en "Avanzado" o directamente en el menú).
3. Haz clic en **Configurar** o **Crear aplicación Python**.
4. Completa los campos:

| Campo | Valor |
|-------|-------|
| **Python version** | `3.10` o superior |
| **App root** | `/home/TU_USUARIO/domains/TU_DOMINIO/public_html` |
| **App URL** | `/` |
| **Startup file** | `passenger_wsgi.py` |

5. Haz clic en **Crear** y espera que termine.

---

### Paso 3 — Instalar Flask

Desde la **Terminal SSH** de Hostinger o el terminal integrado en hPanel:

```bash
cd ~/domains/TU_DOMINIO/public_html
pip install flask
```

> Si `pip` no funciona directamente, usa: `python -m pip install flask`

---

### Paso 4 — Configurar la clave de sesión (importante)

En **hPanel → Python App → Variables de entorno**, agrega:

```
SECRET_KEY = una_cadena_larga_y_aleatoria_aqui_minimo_32_caracteres
TALLER_DB  = /home/TU_USUARIO/domains/TU_DOMINIO/public_html/taller.db
```

> `SECRET_KEY` protege las sesiones de usuario. Usa cualquier cadena larga y aleatoria.
> Si no la defines, el sistema igual funciona pero las sesiones se invalidan al reiniciar.

---

### Paso 5 — Reiniciar e iniciar sesión

1. En **hPanel → Python App** → botón **Restart**.
2. Abre tu dominio en el navegador.
3. Verás la pantalla de **inicio de sesión**.

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `taller2024`

---

## Primeros pasos tras el despliegue

### Cambiar la contraseña del administrador

1. Inicia sesión con `admin` / `taller2024`
2. Ve a **Administración** → sección **Gestión de Usuarios**
3. Haz clic en el botón ✏️ junto al usuario `admin`
4. Introduce una nueva contraseña y guarda

### Crear usuarios adicionales

En la misma sección **Gestión de Usuarios** → **Nuevo Usuario**:

| Nivel | Acceso |
|-------|--------|
| `superusuario` | Todo el sistema + Administración |
| `administrador` | Todo excepto Admin e Implementación |
| `usuario` | Solo Almacén y Herramientas |

---

## Seguridad

### Ruta de la base de datos

Por defecto, `taller.db` se guarda en `public_html`. Para mayor seguridad,
puedes moverla fuera del directorio público:

```
TALLER_DB = /home/TU_USUARIO/private/taller.db
```

El `.htaccess` ya bloquea el acceso directo a archivos `.db`, pero una ubicación
privada es protección adicional.

---

## Backup y restauración

En **Administración → Backup y Restauración**:

- **Descargar backup:** descarga `taller.db` completo (incluye usuarios).
- **Restaurar backup:** sube un archivo `.db` previamente descargado.

También puedes descargar `taller.db` manualmente desde el Administrador de Archivos.

---

## Actualización del sistema

1. Descarga un backup desde Admin → Backup **antes de cualquier cambio**.
2. Genera un nuevo ZIP desde Admin → Exportar para Hostinger.
3. Sube los nuevos archivos (sobrescribe todo **excepto `taller.db`**).
4. Reinicia la app desde hPanel → Python App → Restart.

---

## Solución de problemas

| Problema | Solución |
|----------|----------|
| No aparece opción Python en hPanel | Debes tener plan **Business** o superior |
| Error 500 al cargar | Ejecuta `pip install flask` por SSH |
| Pantalla en blanco sin login | Verifica que `passenger_wsgi.py` está en `public_html` |
| Archivos estáticos no cargan | Verifica que la carpeta `static/` se subió correctamente |
| DB no encontrada | Confirma que `taller.db` se subió y la ruta en `TALLER_DB` es correcta |
| App no inicia | Revisa los logs en hPanel → Python App → View logs |
| Sesión expira al reiniciar | Define `SECRET_KEY` fija en variables de entorno |

---

*Sistema de Taller de Carpintería — v2.0 (Producción SQLite + Auth por sesión)*
