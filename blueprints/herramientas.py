"""
blueprints/herramientas.py — Herramientas page & API (including prestamos).
"""
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template, abort
from core.auth import require_login

bp = Blueprint('herramientas', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


@bp.route("/herramientas")
@require_login(sections=["herramientas"])
def herramientas():
    return render_template("herramientas.html")


@bp.route("/api/herramientas")
@require_login()
def api_herramientas():
    herrs = _data.tlist("HERRAMIENTAS")
    movs  = _data.tlist("MOV_HERRA")
    activos = {m["ID_Herramienta"] for m in movs if m.get("FechaDevolucion", "") == ""}
    for h in herrs:
        h["Estado"] = "Prestada" if h["ID_Herramienta"] in activos else "Disponible"
    return jsonify(herrs)


@bp.route("/api/herramientas", methods=["POST"])
@require_login(roles=["superusuario", "administrador"])
def api_add_herramienta():
    _data.tinsert("HERRAMIENTAS", request.get_json())
    return jsonify({"ok": True})


@bp.route("/api/prestamos")
@require_login()
def api_prestamos():
    rows = _data.tlist("MOV_HERRA")
    if request.args.get("activos") == "1":
        rows = [r for r in rows if r.get("FechaDevolucion", "") == ""]
    return jsonify(rows)


@bp.route("/api/prestamos", methods=["POST"])
@require_login()
def api_add_prestamo():
    raw   = request.get_json()
    now   = datetime.now()
    items = raw if isinstance(raw, list) else [raw]
    for item in items:
        if not item.get("FechaSalida"):
            item["FechaSalida"] = now.strftime("%Y-%m-%d")
        item["Hora"] = now.strftime("%H:%M")
        _data.tinsert("MOV_HERRA", item)
    ids_afectados = {str(it.get("ID_Herramienta", "")) for it in items if it.get("ID_Herramienta")}
    for id_h in ids_afectados:
        _data._sync_herramienta_estado(id_h)
    return jsonify({"ok": True})


@bp.route("/api/prestamos/<id_prestamo>/devolucion", methods=["POST"])
@require_login()
def api_devolucion(id_prestamo):
    fecha = request.get_json().get("fecha", datetime.now().strftime("%Y-%m-%d"))
    rows  = _data.tfiltered_dict("MOV_HERRA", {"ID_Prestamo": id_prestamo})
    if not rows:
        abort(404, "Prestamo no encontrado")
    row = rows[0]
    id_herramienta = row.get("ID_Herramienta", "")
    # Usar tupdate_pk (backend-agnostic) en vez de raw_tabla_update que requiere _idx
    _data.tupdate_pk("MOV_HERRA", "ID_Prestamo", id_prestamo, {
        "FechaDevolucion": fecha
    })
    _data._sync_herramienta_estado(id_herramienta)
    return jsonify({"ok": True})
