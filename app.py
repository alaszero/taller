"""
app.py — Backend Flask para el Sistema de Gestion de Taller de Carpinteria (local/Excel)
Ejecutar: python app.py
URL: http://localhost:5000
"""
import os
import sys
from datetime import timedelta

from flask import Flask

from core.config import SESSION_TIMEOUT_MINUTES
from core import auth
from core.helpers import _read_version
from data import excel_backend as data
from blueprints import (
    shared_api, empleados, herramientas, avance,
    proyectos, almacen, dashboard, admin, network_local,
)

app = Flask(__name__)
app.config["JSON_ENSURE_ASCII"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "taller-secret-2024-xK9m")
app.permanent_session_lifetime = timedelta(minutes=SESSION_TIMEOUT_MINUTES)

# ── Inicializar backend de datos y autenticación ─────────────────────────────
data.init_app(app)
auth.init_app(app, data.get_db)

# ── Registrar blueprints ─────────────────────────────────────────────────────
_blueprints = [
    shared_api, empleados, herramientas, avance,
    proyectos, almacen, dashboard, admin, network_local,
]
for bp_mod in _blueprints:
    bp_mod.init_data(data)
    app.register_blueprint(bp_mod.bp)


# ── Banner & servidor ────────────────────────────────────────────────────────

def _print_banner():
    G  = "\033[92m"
    DG = "\033[32m"
    B  = "\033[1m"
    R  = "\033[0m"
    ver = _read_version()
    if os.name == "nt":
        os.system("")
    print(f"""{G}
  ╔═══════════════════════════════════════════════════╗
  ║                                                   ║
  ║   ██╗   ██╗███████╗██╗  ██╗███████╗██╗      ██╗  ║
  ║   ╚██╗ ██╔╝██╔════╝██║ ██╔╝██╔════╝██║     ██╔╝  ║
  ║    ╚████╔╝ █████╗  █████╔╝ █████╗  ██║    ██╔╝   ║
  ║     ╚██╔╝  ██╔══╝  ██╔═██╗ ██╔══╝  ██║   ██╔╝    ║
  ║      ██║   ███████╗██║  ██╗██║     ███████╔╝      ║
  ║      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝      ║
  ║                                                   ║
  ║   {DG}Sistema de Gestión de Taller{G}                  ║
  ║   {DG}By Barrón{G}                                     ║
  ║                                                   ║
  ╚═══════════════════════════════════════════════════╝{R}

  {B}{G}▸{R} Servidor:  {G}http://0.0.0.0:5000{R}
  {B}{G}▸{R} Versión:   {G}v{ver}{R}
  {B}{G}▸{R} Estado:    {G}[ONLINE]{R}
  {B}{G}▸{R} Detener:   {DG}Ctrl+C{R}
""")


if __name__ == "__main__":
    import logging
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s",
                        datefmt="%H:%M:%S")
    try:
        _print_banner()
    except Exception:
        print("[Taller] Servidor iniciando en http://localhost:5000")
    app.run(host="0.0.0.0", debug=False, port=5000)
