"""
core/auth.py — Authentication & authorization module.

Extracted from app_web.py.  Provides:
  - require_login   decorator
  - auth_bp         Blueprint (login / logout routes)
  - init_app()      wiring helper
"""

from functools import wraps
from datetime import datetime, timedelta

from flask import (
    Blueprint, session, request, redirect, url_for,
    jsonify, abort, render_template, render_template_string,
)
from werkzeug.security import check_password_hash

import db as _db
from core.config import SECTION_ROUTES, DEFAULT_SECCIONES, SESSION_TIMEOUT_MINUTES
from core.helpers import _read_version

# ── Module-level DB accessor (set by init_app) ──────────────────────────────
_get_db = None


# ═══════════════════════════════════════════════════════════════════════════════
# DECORATOR
# ═══════════════════════════════════════════════════════════════════════════════

def require_login(roles=None, sections=None):
    """Decorator de control de acceso.
       sections=['almacen'] → usuario debe tener 'almacen' en sus secciones.
       roles=['superusuario'] → fallback legacy por nivel.
       nivel 'yekflow' siempre tiene acceso total (bypass completo)."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "username" not in session or not session.get("secciones"):
                # Sesión inexistente o corrupta → limpiar y redirigir a login
                session.clear()
                if request.path.startswith("/api/"):
                    return jsonify({"ok": False, "error": "No autenticado"}), 401
                return redirect(url_for("auth.login_page"))
            # yekflow: acceso total, sin restricción de secciones ni roles
            if session.get("nivel") == "yekflow":
                return f(*args, **kwargs)
            if sections:
                user_secciones = session.get("secciones", [])
                if not any(s in user_secciones for s in sections):
                    if request.path.startswith("/api/"):
                        return jsonify({"ok": False, "error": "Sin permisos"}), 403
                    abort(403)
            elif roles and session.get("nivel") not in roles:
                if request.path.startswith("/api/"):
                    return jsonify({"ok": False, "error": "Sin permisos"}), 403
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT PROCESSOR FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def make_inject_user(get_db_func):
    """Return a context-processor function that injects user/session info."""
    def inject_user():
        version = _read_version()
        if "username" in session:
            taller_id = session.get("taller_id", "rober_lang")
            taller_nombre = ""
            if taller_id != "__all__":
                try:
                    conn = get_db_func()
                    rows = _db.table_to_list_filtered(conn, "TALLERES", {"id": taller_id})
                    taller_nombre = rows[0]["nombre"] if rows else taller_id
                except Exception:
                    taller_nombre = taller_id
            return {
                "current_user": {
                    "username":  session["username"],
                    "nivel":     session["nivel"],
                    "nombre":    session["nombre"],
                    "secciones": session.get("secciones", []),
                },
                "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,
                "system_version":          version,
                "current_taller_id":       taller_id,
                "current_taller_nombre":   taller_nombre,
            }
        return {
            "current_user": None,
            "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,
            "system_version": version,
            "current_taller_id": None,
            "current_taller_nombre": "",
        }
    return inject_user


# ═══════════════════════════════════════════════════════════════════════════════
# BEFORE-REQUEST & ERROR HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

def refresh_session():
    """Sliding window: cada petición renueva el timeout de la sesión."""
    session.modified = True


def forbidden(e):
    """Página amigable para acceso denegado."""
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Acceso denegado"}), 403
    return render_template_string('''
    {% extends "base.html" %}
    {% block titulo %}Acceso Denegado{% endblock %}
    {% block contenido %}
    <div class="text-center py-5">
      <i class="bi bi-shield-x" style="font-size:64px;color:#dc3545;"></i>
      <h3 class="mt-3">Acceso Denegado</h3>
      <p class="text-muted">No tienes permiso para acceder a esta sección.</p>
      <a href="/" class="btn btn-primary mt-2"><i class="bi bi-house me-1"></i>Ir al inicio</a>
      <a href="/logout" class="btn btn-outline-secondary mt-2 ms-2"><i class="bi bi-box-arrow-right me-1"></i>Cerrar sesión</a>
    </div>
    {% endblock %}
    '''), 403


def not_found(e):
    """Página amigable para recurso no encontrado."""
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Recurso no encontrado"}), 404
    return render_template_string('''
    {% extends "base.html" %}
    {% block titulo %}No Encontrado{% endblock %}
    {% block contenido %}
    <div class="text-center py-5">
      <i class="bi bi-question-circle" style="font-size:64px;color:#f59e0b;"></i>
      <h3 class="mt-3">Página no encontrada</h3>
      <p class="text-muted">La página que buscas no existe o fue movida.</p>
      <a href="/" class="btn btn-primary mt-2"><i class="bi bi-house me-1"></i>Ir al inicio</a>
    </div>
    {% endblock %}
    '''), 404


def internal_error(e):
    """Página amigable para errores internos del servidor."""
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500
    return render_template_string('''
    {% extends "base.html" %}
    {% block titulo %}Error del Servidor{% endblock %}
    {% block contenido %}
    <div class="text-center py-5">
      <i class="bi bi-exclamation-triangle" style="font-size:64px;color:#dc3545;"></i>
      <h3 class="mt-3">Error del Servidor</h3>
      <p class="text-muted">Ocurrió un error inesperado. Intenta de nuevo o contacta al administrador.</p>
      <a href="/" class="btn btn-primary mt-2"><i class="bi bi-house me-1"></i>Ir al inicio</a>
    </div>
    {% endblock %}
    '''), 500


# ═══════════════════════════════════════════════════════════════════════════════
# BLUEPRINT — LOGIN / LOGOUT
# ═══════════════════════════════════════════════════════════════════════════════

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["GET"])
def login_page():
    if "username" in session:
        secciones = session.get("secciones", [])
        redirect_order = ["dashboard", "almacen", "proyectos", "herramientas",
                          "avance", "empleados", "implementacion", "admin"]
        first = next((s for s in redirect_order if s in secciones), "almacen")
        return redirect(SECTION_ROUTES.get(first, "/almacen"))
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login_post():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    conn  = _get_db()
    ip    = request.remote_addr or "unknown"

    # ── Control de intentos fallidos (max 5 en 10 minutos por IP) ────────────
    try:
        _cutoff = (datetime.utcnow() - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        _attempt_count = conn.execute(
            "SELECT COUNT(*) FROM LOGIN_ATTEMPTS WHERE ip=? AND ts > ?", (ip, _cutoff)
        ).fetchone()[0]
        if _attempt_count >= 5:
            return render_template("login.html",
                                   error="Demasiados intentos fallidos. Espera 10 minutos.",
                                   username=username)
    except Exception:
        pass

    rows  = _db.table_to_list_filtered(conn, "USUARIOS", {"username": username})
    user  = rows[0] if rows else None

    if not user or user.get("activo", "1") != "1" or \
       not check_password_hash(user.get("password_hash", ""), password):
        try:
            conn.execute("INSERT INTO LOGIN_ATTEMPTS(ip,username) VALUES(?,?)", (ip, username))
            conn.commit()
        except Exception:
            pass
        return render_template("login.html",
                               error="Usuario o contraseña incorrectos.",
                               username=username)

    # Calcular secciones (backward compatible: si no tiene, usa default del nivel)
    user_secciones = user.get("secciones", "")
    if not user_secciones:
        user_secciones = DEFAULT_SECCIONES.get(user["nivel"], "almacen,herramientas")
    # '*' = acceso total → expandir a todas las secciones
    if user_secciones.strip() == "*":
        user_secciones = DEFAULT_SECCIONES.get("yekflow",
            "dashboard,almacen,herramientas,proyectos,avance,empleados,implementacion,admin")
    secciones_list = [s.strip() for s in user_secciones.split(",") if s.strip()]

    # Login exitoso → limpiar intentos de esta IP
    try:
        conn.execute("DELETE FROM LOGIN_ATTEMPTS WHERE ip=?", (ip,))
        conn.commit()
    except Exception:
        pass

    session.permanent = True
    session["username"]  = user["username"]
    session["nivel"]     = user["nivel"]
    session["nombre"]    = user["nombre"]
    session["secciones"] = secciones_list
    # Contexto multi-taller: yekflow ve todo; los demás ven su propio taller
    if user["nivel"] == "yekflow":
        session["taller_id"] = "__all__"
    else:
        session["taller_id"] = user.get("taller_id") or "rober_lang"

    redirect_order = ["dashboard", "almacen", "proyectos", "herramientas",
                      "avance", "empleados", "implementacion", "admin"]
    first = next((s for s in redirect_order if s in secciones_list), "almacen")
    next_url = request.args.get("next") or SECTION_ROUTES.get(first, "/almacen")
    return redirect(next_url)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login_page"))


# ═══════════════════════════════════════════════════════════════════════════════
# APP WIRING
# ═══════════════════════════════════════════════════════════════════════════════

def init_app(app, get_db_func):
    """Register auth blueprint, context processor, before-request & error handler."""
    global _get_db
    _get_db = get_db_func

    app.register_blueprint(auth_bp)
    app.context_processor(make_inject_user(get_db_func))
    app.before_request(refresh_session)
    app.errorhandler(403)(forbidden)
    app.errorhandler(404)(not_found)
    app.errorhandler(500)(internal_error)
