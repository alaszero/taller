"""
blueprints/avance.py — Avance page & API (including dashboard resumen).
"""
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template, session
from core.auth import require_login

bp = Blueprint('avance', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


@bp.route("/avance")
@require_login(sections=["avance"])
def avance():
    return render_template("avance.html")


@bp.route("/avance/resumen")
@require_login(sections=["avance"])
def avance_resumen():
    return render_template("avance_dashboard.html")


@bp.route("/api/avance")
@require_login(sections=["proyectos", "avance"])
def api_avance():
    rows = _data.tlist("REG_AVANCE")
    if request.args.get("op"):
        rows = [r for r in rows if r.get("ID_OP") == request.args["op"]]
    if request.args.get("empleado"):
        rows = [r for r in rows if r.get("EmpleadoID") == request.args["empleado"]]
    return jsonify(rows)


@bp.route("/api/avance", methods=["POST"])
@require_login(sections=["proyectos", "avance"])
def api_add_avance():
    data = request.get_json()
    if not data.get("Fecha"):
        data["Fecha"] = datetime.now().strftime("%Y-%m-%d")
    _data.tinsert("REG_AVANCE", data)
    return jsonify({"ok": True})


@bp.route("/api/dashboard/resumen")
@require_login()
def api_dashboard_resumen():
    """Endpoint unificado con cache de 5 minutos. Evalua alertas antes de responder."""
    conn = _data.get_db()
    tid  = session.get("taller_id", "rober_lang")

    # Evaluar alertas (ligero, sin threads)
    _data._evaluar_alertas(conn, tid)

    # Verificar cache (< 5 minutos)
    try:
        cache_row = conn.execute(
            "SELECT data, ts FROM DASHBOARD_CACHE WHERE taller_id=?", (tid,)
        ).fetchone()
        if cache_row:
            cache_ts  = datetime.strptime(cache_row["ts"], "%Y-%m-%d %H:%M:%S")
            cache_age = (datetime.utcnow() - cache_ts).total_seconds()
            if cache_age < 300:
                return jsonify(json.loads(cache_row["data"]))
    except Exception:
        pass

    # Calcular metricas
    stock            = _data.calcular_stock()
    stock_critico    = sum(1 for s in stock if s["Alerta"])
    prestamos        = _data.tlist("MOV_HERRA")
    herr_prestadas   = sum(1 for p in prestamos if p.get("FechaDevolucion", "") == "")
    proyectos_list   = _data.tlist("PROYECTOS")
    proy_activos     = sum(1 for p in proyectos_list
                          if p.get("Estado") in ("En proceso", "Iniciado", "En curso"))
    avance_list      = _data.tlist("REG_AVANCE")
    hoy_str          = datetime.now().strftime("%Y-%m-%d")
    registros_hoy    = sum(1 for a in avance_list if a.get("Fecha", "") == hoy_str)

    tid_alertas = None if tid == "__all__" else tid
    if tid_alertas:
        alertas_activas = conn.execute(
            "SELECT COUNT(*) FROM ALERTAS WHERE taller_id=? AND leida=0", (tid_alertas,)
        ).fetchone()[0]
    else:
        alertas_activas = conn.execute(
            "SELECT COUNT(*) FROM ALERTAS WHERE leida=0"
        ).fetchone()[0]

    data = {
        "stock_critico":          int(stock_critico),
        "herramientas_prestadas": int(herr_prestadas),
        "proyectos_activos":      int(proy_activos),
        "registros_hoy":          int(registros_hoy),
        "alertas_activas":        int(alertas_activas),
    }

    # Guardar en cache
    try:
        ts_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT OR REPLACE INTO DASHBOARD_CACHE(taller_id,data,ts) VALUES(?,?,?)",
            (tid, json.dumps(data), ts_str)
        )
        conn.commit()
    except Exception:
        pass

    return jsonify(data)
