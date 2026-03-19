"""
blueprints/empleados.py — Empleados page & API.
"""
from flask import Blueprint, jsonify, request, render_template
from core.auth import require_login

bp = Blueprint('empleados', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


@bp.route("/empleados")
@require_login(sections=["empleados"])
def empleados():
    return render_template("empleados.html")


@bp.route("/api/empleados")
@require_login(sections=["empleados", "proyectos", "avance", "almacen", "herramientas"])
def api_empleados():
    return jsonify(_data.tlist("EMPLEADOS"))


@bp.route("/api/empleados", methods=["POST"])
@require_login(sections=["empleados"])
def api_add_empleado():
    _data.tinsert("EMPLEADOS", request.get_json())
    return jsonify({"ok": True})
