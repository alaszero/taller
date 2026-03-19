"""
blueprints/shared_api.py — Shared API endpoints (next_code, etapas).
"""
import re as _re
from flask import Blueprint, jsonify, request, render_template
from core.auth import require_login

bp = Blueprint('shared_api', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


@bp.route("/implementacion")
@require_login(sections=["implementacion"])
def implementacion():
    return render_template("implementacion.html")


@bp.route("/api/next_code")
@require_login()
def api_next_code():
    prefix = request.args.get("prefix", "").upper()
    mapping = {
        "MAT":  ("MATERIALES",         "Codigo_mat"),
        "HER":  ("HERRAMIENTAS",       "ID_Herramienta"),
        "EMP":  ("EMPLEADOS",          "EmpleadoID"),
        "PROV": ("PROVEEDORES",        "ProveedorID"),
        "PROY": ("PROYECTOS",          "ID_Proyecto"),
        "MUE":  ("MUEBLES",            "ID_Mueble"),
        "UB":   ("UBICACIONES",        "ID_Ubic"),
        "OP":   ("ORDENES_PRODUCCION", "ID_OP"),
    }
    if prefix not in mapping:
        return jsonify({"error": f"Prefijo '{prefix}' no reconocido"}), 400

    table, col = mapping[prefix]
    rows = _data.tlist(table)
    pattern = _re.compile(rf"^{_re.escape(prefix)}(\d+)$", _re.IGNORECASE)
    nums, pad = [], 3
    for row in rows:
        val = str(row.get(col, "")).strip()
        m = pattern.match(val)
        if m:
            nums.append(int(m.group(1)))
            pad = max(pad, len(val) - len(prefix))
    next_num = max(nums) + 1 if nums else 1
    return jsonify({"code": f"{prefix}{str(next_num).zfill(pad)}"})


@bp.route("/api/etapas")
@require_login(sections=["proyectos", "avance"])
def api_etapas():
    return jsonify(_data.tlist("ETAPAS"))
