"""
blueprints/proyectos.py — Proyectos, Muebles & Ordenes pages & API.
"""
from flask import Blueprint, jsonify, request, render_template, abort
from core.auth import require_login

bp = Blueprint('proyectos', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


@bp.route("/proyectos")
@require_login(sections=["proyectos"])
def proyectos():
    return render_template("proyectos.html")


@bp.route("/api/proyectos")
@require_login(sections=["proyectos", "avance", "almacen", "herramientas"])
def api_proyectos():
    return jsonify(_data.tlist("PROYECTOS"))


@bp.route("/api/proyectos", methods=["POST"])
@require_login(sections=["proyectos", "avance"])
def api_add_proyecto():
    _data.tinsert("PROYECTOS", request.get_json())
    return jsonify({"ok": True})


@bp.route("/api/proyectos/<pid>", methods=["PUT"])
@require_login(sections=["proyectos", "avance"])
def api_update_proyecto(pid):
    if not _data.tupdate_pk("PROYECTOS", "ID_Proyecto", pid, request.get_json()):
        abort(404, description="Proyecto no encontrado")
    return jsonify({"ok": True})


@bp.route("/api/muebles")
@require_login(sections=["proyectos", "avance", "almacen"])
def api_muebles():
    rows = _data.tlist("MUEBLES")
    proy = request.args.get("proyecto")
    if proy:
        rows = [r for r in rows if r.get("ID_Proyecto") == proy]
    return jsonify(rows)


@bp.route("/api/muebles", methods=["POST"])
@require_login(sections=["proyectos", "avance"])
def api_add_mueble():
    _data.tinsert("MUEBLES", request.get_json())
    return jsonify({"ok": True})


@bp.route("/api/muebles/<mid>", methods=["PUT"])
@require_login(sections=["proyectos", "avance"])
def api_update_mueble(mid):
    if not _data.tupdate_pk("MUEBLES", "ID_Mueble", mid, request.get_json()):
        abort(404, description="Mueble no encontrado")
    return jsonify({"ok": True})


@bp.route("/api/ordenes")
@require_login(sections=["proyectos", "avance"])
def api_ordenes():
    rows = _data.tlist("ORDENES_PRODUCCION")
    mueble = request.args.get("mueble")
    if mueble:
        rows = [r for r in rows if r.get("ID_Mueble") == mueble]
    return jsonify(rows)


@bp.route("/api/ordenes", methods=["POST"])
@require_login(sections=["proyectos", "avance"])
def api_add_orden():
    _data.tinsert("ORDENES_PRODUCCION", request.get_json())
    return jsonify({"ok": True})


@bp.route("/api/ordenes/<oid>", methods=["PUT"])
@require_login(sections=["proyectos", "avance"])
def api_update_orden(oid):
    if not _data.tupdate_pk("ORDENES_PRODUCCION", "ID_OP", oid, request.get_json()):
        abort(404, description="Orden no encontrada")
    return jsonify({"ok": True})
