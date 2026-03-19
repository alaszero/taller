"""
blueprints/admin.py — Admin page & API (CRUD editor, usuarios, reset, backup, restore,
talleres, switch_taller, audit, sistema alertas).
"""
import os
import io
import json
import shutil
import tempfile
import re
import sys
import importlib
from datetime import datetime
from flask import (Blueprint, jsonify, request, render_template, session,
                   make_response, abort, send_file, Response)
from werkzeug.security import generate_password_hash
from core.auth import require_login
from core.config import (_TABLE_REGISTRY, _RESET_MAP, _PK_MAP,
                         DEFAULT_SECCIONES, VALID_NIVELES)

bp = Blueprint('admin', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════

@bp.route("/admin")
@require_login(sections=["admin"])
def admin_page():
    is_prod = not hasattr(_data, "excel_to_sqlite_mem")
    net_auth = True
    net_lan_ip = "—"
    if not is_prod and hasattr(_data, "CAT"):
        try:
            from blueprints.network_local import get_net_state, get_lan_ip
            net_auth = get_net_state()["auth"]
            net_lan_ip = get_lan_ip()
        except Exception:
            pass
    resp = make_response(render_template("admin.html",
        net_auth=net_auth,
        net_lan_ip=net_lan_ip,
        is_production=is_prod,
    ))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    return resp


@bp.route("/manual")
@require_login(sections=["admin"])
def manual():
    if "generar_manual" in sys.modules:
        mod = importlib.reload(sys.modules["generar_manual"])
    else:
        if _data.BASE_DIR not in sys.path:
            sys.path.insert(0, _data.BASE_DIR)
        mod = importlib.import_module("generar_manual")
    html = mod.build_html()
    if request.args.get("print") == "1":
        html = html.replace(
            "</body>",
            "<script>window.onload=function(){setTimeout(function(){window.print();},600);}</script></body>",
        )
    return Response(html, mimetype="text/html; charset=utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# API — EDITOR CRUDO DE TABLAS
# ══════════════════════════════════════════════════════════════════════════════

@bp.route("/api/admin/tabla/<key>")
@require_login(sections=["admin"])
def api_tabla_get(key):
    if key not in _TABLE_REGISTRY:
        return jsonify({"ok": False, "error": "Tabla no encontrada"}), 404
    t = _TABLE_REGISTRY[key]
    try:
        cols, rows = _data.raw_tabla_get(t["table"])
        return jsonify({"ok": True, "label": t["label"], "columns": cols, "rows": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@bp.route("/api/admin/tabla/<key>/update", methods=["POST"])
@require_login(sections=["admin"])
def api_tabla_update(key):
    if key not in _TABLE_REGISTRY:
        return jsonify({"ok": False, "error": "Tabla no encontrada"}), 404
    data    = request.get_json() or {}
    row_idx = data.get("row_idx")
    col     = data.get("col")
    value   = data.get("value", "")
    if row_idx is None or col is None:
        return jsonify({"ok": False, "error": "Faltan parametros"}), 400
    t = _TABLE_REGISTRY[key]
    try:
        _data.raw_tabla_update(t["table"], int(row_idx), col, value)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@bp.route("/api/admin/tabla/<key>/delete", methods=["POST"])
@require_login(sections=["admin"])
def api_tabla_delete(key):
    if key not in _TABLE_REGISTRY:
        return jsonify({"ok": False, "error": "Tabla no encontrada"}), 404
    data    = request.get_json() or {}
    row_idx = data.get("row_idx")
    if row_idx is None:
        return jsonify({"ok": False, "error": "Falta row_idx"}), 400
    t = _TABLE_REGISTRY[key]
    try:
        _data.raw_tabla_delete(t["table"], int(row_idx))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ══════════════════════════════════════════════════════════════════════════════
# API — GESTION DE USUARIOS
# ══════════════════════════════════════════════════════════════════════════════

@bp.route("/api/admin/usuarios")
@require_login(sections=["admin"])
def api_usuarios_list():
    rows = _data.tlist("USUARIOS")
    # No exponer password_hash
    safe = [{k: v for k, v in r.items() if k != "password_hash"} for r in rows]
    return jsonify(safe)


@bp.route("/api/admin/usuarios", methods=["POST"])
@require_login(sections=["admin"])
def api_usuarios_create():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    nivel    = (data.get("nivel") or "").strip()
    nombre   = (data.get("nombre") or "").strip()

    secciones = (data.get("secciones") or "").strip()

    if not username or not password or nivel not in VALID_NIVELES:
        return jsonify({"ok": False, "error": "Datos invalidos"}), 400

    # Si no se enviaron secciones, usar defaults del nivel
    if not secciones:
        secciones = DEFAULT_SECCIONES.get(nivel, "almacen,herramientas")

    existing = _data.tfiltered_dict("USUARIOS", {"username": username})
    if existing:
        return jsonify({"ok": False, "error": "El usuario ya existe"}), 409

    _data.tinsert("USUARIOS", {
        "username":      username,
        "password_hash": generate_password_hash(password),
        "nivel":         nivel,
        "nombre":        nombre,
        "activo":        "1",
        "secciones":     secciones,
    })
    return jsonify({"ok": True})


@bp.route("/api/admin/usuarios/<username>", methods=["PUT"])
@require_login(sections=["admin"])
def api_usuarios_update(username):
    data     = request.get_json() or {}
    to_update = {}

    if "nivel" in data:
        if data["nivel"] not in VALID_NIVELES:
            return jsonify({"ok": False, "error": "Nivel invalido"}), 400
        to_update["nivel"] = data["nivel"]
    if "nombre" in data:
        to_update["nombre"] = data["nombre"]
    if "activo" in data:
        to_update["activo"] = "1" if data["activo"] else "0"
    if "password" in data and data["password"]:
        to_update["password_hash"] = generate_password_hash(data["password"])
    if "secciones" in data:
        to_update["secciones"] = data["secciones"]

    if not to_update:
        return jsonify({"ok": False, "error": "Sin cambios"}), 400

    if not _data.tupdate_pk("USUARIOS", "username", username, to_update):
        return jsonify({"ok": False, "error": "Usuario no encontrado"}), 404
    return jsonify({"ok": True})


@bp.route("/api/admin/usuarios/<username>", methods=["DELETE"])
@require_login(sections=["admin"])
def api_usuarios_delete(username):
    # No permitir que el superusuario se elimine a si mismo
    if username == session.get("username"):
        return jsonify({"ok": False, "error": "No puedes eliminar tu propio usuario"}), 400
    rows = _data.tfiltered_dict("USUARIOS", {"username": username})
    if not rows:
        return jsonify({"ok": False, "error": "Usuario no encontrado"}), 404
    _data.tdelete_rowid("USUARIOS", rows[0]["_idx"])
    return jsonify({"ok": True})


# ══════════════════════════════════════════════════════════════════════════════
# API — RESET / BACKUP / RESTORE
# ══════════════════════════════════════════════════════════════════════════════

@bp.route("/api/admin/reset", methods=["POST"])
@require_login(sections=["admin"])
def api_admin_reset():
    data    = request.get_json() or {}
    target  = data.get("target", "")
    confirm = data.get("confirm", "")
    if confirm != "BORRAR":
        return jsonify({"ok": False, "error": "Confirmacion invalida"}), 400
    if target == "all":
        for tbl in _RESET_MAP.values():
            _data.tclear(tbl)
        return jsonify({"ok": True})
    if target in _RESET_MAP:
        _data.tclear(_RESET_MAP[target])
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Target desconocido"}), 400


@bp.route("/api/admin/backup")
@require_login(sections=["admin"])
def api_admin_backup():
    """Descarga un respaldo completo de los datos."""
    return _data.create_backup()


@bp.route("/api/admin/restore", methods=["POST"])
@require_login(sections=["admin"])
def api_admin_restore():
    """Restaura datos desde un archivo de backup subido."""
    if "backup" not in request.files:
        return jsonify({"ok": False, "error": "No se recibio archivo"}), 400
    return _data.restore_backup(request.files["backup"])


@bp.route("/api/admin/export_deploy")
@require_login(sections=["admin"])
def api_export_deploy():
    """Genera ZIP para deploy en servidor (solo disponible con backend Excel)."""
    if not hasattr(_data, "excel_to_sqlite_mem"):
        return jsonify({"ok": False, "error": "No disponible en este modo"}), 404
    import io
    import zipfile
    from core.helpers import _read_version, _increment_version
    try:
        db_bytes = _data.excel_to_sqlite_mem()
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error al migrar datos: {str(e)}"}), 500
    new_version = _increment_version()
    now_str = datetime.now().strftime("%Y%m%d_%H%M")
    mem = io.BytesIO()
    files_to_include = {
        "app.py":              os.path.join(_data.BASE_DIR, "app_web.py"),
        "db.py":               os.path.join(_data.BASE_DIR, "db.py"),
        "taller.service":      os.path.join(_data.BASE_DIR, "taller.service"),
        "setup_ubuntu.sh":     os.path.join(_data.BASE_DIR, "setup_ubuntu.sh"),
        "update_server.sh":    os.path.join(_data.BASE_DIR, "update_server.sh"),
        "instalar_actualizador.sh": os.path.join(_data.BASE_DIR, "instalar_actualizador.sh"),
        "requirements.txt":    os.path.join(_data.BASE_DIR, "requirements_web.txt"),
        "generar_manual.py":   os.path.join(_data.BASE_DIR, "generar_manual.py"),
        "README_SERVIDOR.md":  os.path.join(_data.BASE_DIR, "README_SERVIDOR.md"),
        "VERSION":             os.path.join(_data.BASE_DIR, "VERSION"),
    }
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for dest, src in files_to_include.items():
            if os.path.isfile(src):
                zf.write(src, dest)
        zf.writestr("taller.db", db_bytes)
        # Templates (incluyendo partials)
        tpl_dir = os.path.join(_data.BASE_DIR, "templates")
        if os.path.isdir(tpl_dir):
            for root, dirs, files in os.walk(tpl_dir):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    arcname = os.path.relpath(fpath, _data.BASE_DIR).replace("\\", "/")
                    zf.write(fpath, arcname)
        # Static
        for sub in ("css", "js"):
            sub_dir = os.path.join(_data.BASE_DIR, "static", sub)
            if os.path.isdir(sub_dir):
                for fname in os.listdir(sub_dir):
                    fpath = os.path.join(sub_dir, fname)
                    if os.path.isfile(fpath):
                        zf.write(fpath, f"static/{sub}/{fname}")
        # Core, data, blueprints modules
        for mod_dir in ("core", "data", "blueprints"):
            src_dir = os.path.join(_data.BASE_DIR, mod_dir)
            if os.path.isdir(src_dir):
                for fname in os.listdir(src_dir):
                    if fname.endswith(".py"):
                        fpath = os.path.join(src_dir, fname)
                        zf.write(fpath, f"{mod_dir}/{fname}")
    mem.seek(0)
    return send_file(
        mem,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"taller_servidor_v{new_version}_{now_str}.zip",
    )


# ══════════════════════════════════════════════════════════════════════════════
# API — TALLERES (solo nivel yekflow)
# ══════════════════════════════════════════════════════════════════════════════

@bp.route("/api/talleres", methods=["GET"])
@require_login(roles=["yekflow"])
def api_talleres_get():
    return jsonify(_data.tlist("TALLERES"))


@bp.route("/api/talleres", methods=["POST"])
@require_login(roles=["yekflow"])
def api_talleres_create():
    data = request.get_json() or {}
    taller_id  = (data.get("id") or "").strip().lower().replace(" ", "_")
    nombre     = (data.get("nombre") or "").strip()
    if not taller_id or not nombre:
        return jsonify({"ok": False, "error": "id y nombre son requeridos"}), 400
    existing = _data.tfiltered_dict("TALLERES", {"id": taller_id})
    if existing:
        return jsonify({"ok": False, "error": "Ya existe un taller con ese id"}), 409
    _data.tinsert("TALLERES", {"id": taller_id, "nombre": nombre})
    return jsonify({"ok": True, "id": taller_id})


@bp.route("/api/talleres/<taller_id>", methods=["PUT"])
@require_login(roles=["yekflow"])
def api_talleres_update(taller_id):
    data = request.get_json() or {}
    rows = _data.tfiltered_dict("TALLERES", {"id": taller_id})
    if not rows:
        return jsonify({"ok": False, "error": "Taller no encontrado"}), 404
    allowed = {k: v for k, v in data.items() if k in ("nombre", "activo")}
    if not allowed:
        return jsonify({"ok": False, "error": "Sin campos validos para actualizar"}), 400
    _data.tupdate_pk("TALLERES", "id", taller_id, allowed)
    return jsonify({"ok": True})


@bp.route("/api/talleres/<taller_id>", methods=["DELETE"])
@require_login(roles=["yekflow"])
def api_talleres_delete(taller_id):
    if taller_id == "rober_lang":
        return jsonify({"ok": False, "error": "No se puede desactivar el taller principal"}), 403
    rows = _data.tfiltered_dict("TALLERES", {"id": taller_id})
    if not rows:
        return jsonify({"ok": False, "error": "Taller no encontrado"}), 404
    _data.tupdate_pk("TALLERES", "id", taller_id, {"activo": 0})
    return jsonify({"ok": True})


@bp.route("/api/switch_taller", methods=["POST"])
@require_login(roles=["yekflow"])
def api_switch_taller():
    """Permite a yekflow cambiar el contexto de taller activo (o '__all__' para vista global)."""
    data = request.get_json() or {}
    taller_id = (data.get("taller_id") or "").strip()
    if not taller_id:
        return jsonify({"ok": False, "error": "taller_id requerido"}), 400
    if taller_id != "__all__":
        rows = _data.tfiltered_dict("TALLERES", {"id": taller_id})
        if not rows:
            return jsonify({"ok": False, "error": "Taller no encontrado"}), 404
    session["taller_id"] = taller_id
    return jsonify({"ok": True, "taller_id": taller_id})


# ══════════════════════════════════════════════════════════════════════════════
# API — AUDIT LOG
# ══════════════════════════════════════════════════════════════════════════════

@bp.route("/api/audit")
@require_login(roles=["yekflow", "superusuario"])
def api_audit():
    """Devuelve entradas del AUDIT_LOG con filtros opcionales via query params."""
    nivel = session.get("nivel")
    taller_filter = request.args.get("taller")
    if nivel != "yekflow":
        taller_filter = session.get("taller_id", "rober_lang")
    filters = {
        "taller":  taller_filter,
        "tabla":   request.args.get("tabla"),
        "usuario": request.args.get("usuario"),
        "desde":   request.args.get("desde"),
        "hasta":   request.args.get("hasta"),
        "limit":   min(int(request.args.get("limit", 200)), 1000),
    }
    return jsonify(_data.audit_query(filters))


# ══════════════════════════════════════════════════════════════════════════════
# API — ALERTAS DEL SISTEMA
# ══════════════════════════════════════════════════════════════════════════════

@bp.route("/api/sistema/alertas")
@require_login()
def api_sistema_alertas():
    """Devuelve alertas no leidas de la tabla ALERTAS del taller activo."""
    tid  = session.get("taller_id", "rober_lang")
    solo_no_leidas = request.args.get("todas") != "1"
    return jsonify(_data.alertas_query(tid, solo_no_leidas))


@bp.route("/api/sistema/alertas/<int:aid>/leer", methods=["POST"])
@require_login()
def api_sistema_alerta_leer(aid):
    """Marca una alerta como leida."""
    _data.alerta_marcar_leida(aid)
    return jsonify({"ok": True})


@bp.route("/api/sistema/alertas/leer_todas", methods=["POST"])
@require_login()
def api_sistema_alertas_leer_todas():
    """Marca todas las alertas del taller activo como leidas."""
    tid = session.get("taller_id", "rober_lang")
    _data.alertas_marcar_todas_leidas(tid)
    return jsonify({"ok": True})
