"""
passenger_wsgi.py — Punto de entrada WSGI para Hostinger (Phusion Passenger)

Cómo funciona:
  Hostinger detecta este archivo automáticamente cuando creas una aplicación
  Python en hPanel. Phusion Passenger importa `application` desde aquí.

Instrucciones:
  1. Sube todos los archivos al directorio raíz de tu app en Hostinger.
  2. En hPanel → Sitios Web → nombre del sitio → Python App:
       - App Root:   /home/TU_USUARIO/domains/TU_DOMINIO/public_html
       - App URL:    /
       - App entry:  passenger_wsgi.py
       - Python:     3.10 (o superior)
  3. Instala dependencias desde la terminal SSH:
       pip install -r requirements.txt
  4. Establece variables de entorno (opcional, ver abajo).
  5. Reinicia la app desde hPanel.

Variables de entorno opcionales (config → .htaccess o hPanel):
  TALLER_USER   — usuario de acceso (defecto: admin)
  TALLER_PASS   — contraseña de acceso (defecto: taller2024)
  TALLER_DB     — ruta absoluta al archivo taller.db
                  (defecto: mismo directorio que app.py)
  SECRET_KEY    — clave secreta de Flask (genera una aleatoria si no se define)
"""
import sys
import os

# Agrega el directorio de la app al path de Python
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app_web import app as application  # noqa: F401
