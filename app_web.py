"""
app_web.py — Backend Flask para Hostinger (producción)
Base de datos: SQLite (taller.db)
Sin dependencias de pandas/openpyxl — solo sqlite3 (built-in).

Ejecutar local para pruebas:
    python app_web.py

Hostinger: passenger_wsgi.py importa este módulo.
"""
import os
from datetime import timedelta

from flask import Flask

from core.config import SESSION_TIMEOUT_MINUTES
from core import auth
from data import sqlite_backend as data
from blueprints import (
    shared_api, empleados, herramientas, avance,
    proyectos, almacen, dashboard, admin, network,
)

app = Flask(__name__)
app.config["JSON_ENSURE_ASCII"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "taller-secret-2024-xK9m")
app.permanent_session_lifetime = timedelta(minutes=SESSION_TIMEOUT_MINUTES)

# ── Capa de datos (SQLite) ────────────────────────────────────────────────────
data.init_app(app)

# ── Autenticación ─────────────────────────────────────────────────────────────
auth.init_app(app, data.get_db)

# ── Blueprints ────────────────────────────────────────────────────────────────
_blueprints = [
    shared_api, empleados, herramientas, avance,
    proyectos, almacen, dashboard, admin, network,
]
for bp_mod in _blueprints:
    bp_mod.init_data(data)
    app.register_blueprint(bp_mod.bp)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
