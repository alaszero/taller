"""
blueprints/dashboard.py — Dashboard page & API.
"""
from datetime import datetime
from flask import Blueprint, jsonify, render_template
from core.auth import require_login

bp = Blueprint('dashboard', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


@bp.route("/")
@require_login(sections=["dashboard"])
def dashboard():
    return render_template("dashboard.html")


@bp.route("/api/dashboard")
@require_login(sections=["proyectos", "avance"])
def api_dashboard():
    stock   = _data.calcular_stock()
    alertas = [s for s in stock if s["Alerta"]]

    prestamos      = _data.tlist("MOV_HERRA")
    herr_prestadas = sum(1 for p in prestamos if p.get("FechaDevolucion", "") == "")

    proyectos_list = _data.tlist("PROYECTOS")
    muebles_list   = _data.tlist("MUEBLES")
    ordenes_list   = _data.tlist("ORDENES_PRODUCCION")
    proy_activos   = sum(1 for p in proyectos_list if p.get("Estado") == "En proceso")

    avance_list = _data.tlist("REG_AVANCE")
    hoy_str     = datetime.now().strftime("%Y-%m-%d")
    reg_hoy     = sum(1 for a in avance_list if a.get("Fecha") == hoy_str)
    ops_con_avance = {a["ID_OP"] for a in avance_list}

    mat_map  = {m["Codigo_mat"]: m.get("Descripci\u00f3n", "") for m in _data.tlist("MATERIALES")}
    movs     = _data.tlist("MOV_ALMACEN")
    ultimos  = movs[-8:][::-1]
    for mv in ultimos:
        mv["Descripcion_mat"] = mat_map.get(str(mv.get("Codigo_mat", "")),
                                             str(mv.get("Codigo_mat", "")))

    estados_activos = {"En proceso", "Iniciado", "En curso"}
    progreso = []
    for p in proyectos_list:
        if p.get("Estado") not in estados_activos:
            continue
        pid     = str(p["ID_Proyecto"])
        mues    = [m for m in muebles_list if m.get("ID_Proyecto") == pid]
        mue_ids = {m["ID_Mueble"] for m in mues}
        ops     = [o for o in ordenes_list if o.get("ID_Mueble") in mue_ids]
        ops_total = len(ops)
        ops_done  = sum(1 for o in ops if o.get("ID_OP", "") in ops_con_avance)
        progreso.append({
            "ID_Proyecto":   pid,
            "Nombre":        str(p.get("Nombre_Obra", pid)),
            "Estado":        str(p.get("Estado", "")),
            "muebles":       int(len(mues)),
            "ops_total":     int(ops_total),
            "ops_iniciadas": int(ops_done),
            "pct":           int(round(ops_done / ops_total * 100)) if ops_total > 0 else 0,
        })

    return jsonify({
        "alertas_stock":          len(alertas),
        "herramientas_prestadas": int(herr_prestadas),
        "proyectos_activos":      int(proy_activos),
        "registros_hoy":          int(reg_hoy),
        "alertas_detalle":        alertas,
        "ultimos_movimientos":    ultimos,
        "progreso_proyectos":     progreso,
    })
