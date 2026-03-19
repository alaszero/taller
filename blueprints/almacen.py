"""
blueprints/almacen.py — Almacen page & API (materiales, ubicaciones, proveedores, stock, movimientos, lotes).
"""
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template, abort
from core.auth import require_login
from core.helpers import safe_float

bp = Blueprint('almacen', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


@bp.route("/almacen")
@require_login(sections=["almacen"])
def almacen():
    return render_template("almacen.html")


@bp.route("/api/materiales")
@require_login()
def api_materiales():
    return jsonify(_data.tlist("MATERIALES"))


@bp.route("/api/materiales", methods=["POST"])
@require_login(roles=["superusuario", "administrador"])
def api_add_material():
    _data.tinsert("MATERIALES", request.get_json())
    return jsonify({"ok": True})


@bp.route("/api/materiales/<codigo>", methods=["PUT"])
@require_login(roles=["superusuario", "administrador"])
def api_update_material(codigo):
    if not _data.tupdate_pk("MATERIALES", "Codigo_mat", codigo, request.get_json()):
        abort(404, description="Material no encontrado")
    return jsonify({"ok": True})


@bp.route("/api/ubicaciones")
@require_login()
def api_ubicaciones():
    return jsonify(_data.tlist("UBICACIONES"))


@bp.route("/api/ubicaciones", methods=["POST"])
@require_login(sections=["almacen", "admin"])
def api_add_ubicacion():
    _data.tinsert("UBICACIONES", request.get_json())
    return jsonify({"ok": True})


@bp.route("/api/ubicaciones/<uid>", methods=["PUT"])
@require_login(sections=["almacen", "admin"])
def api_update_ubicacion(uid):
    if not _data.tupdate_pk("UBICACIONES", "ID_Ubic", uid, request.get_json()):
        abort(404, description="Ubicacion no encontrada")
    return jsonify({"ok": True})


@bp.route("/api/proveedores")
@require_login(sections=["almacen", "proyectos", "admin"])
def api_proveedores():
    return jsonify(_data.tlist("PROVEEDORES"))


@bp.route("/api/stock")
@require_login()
def api_stock():
    return jsonify(_data.calcular_stock())


@bp.route("/api/alertas")
@require_login()
def api_alertas():
    return jsonify([s for s in _data.calcular_stock() if s["Alerta"]])


@bp.route("/api/stock_ubicaciones")
@require_login()
def api_stock_ubicaciones():
    mats  = _data.tlist("MATERIALES")
    movs  = _data.tlist("MOV_ALMACEN")
    ubics = _data.tlist("UBICACIONES")

    total_stock = {}
    for mv in movs:
        cod  = str(mv.get("Codigo_mat", "") or "").strip()
        cant = safe_float(mv.get("Cantidad", 0))
        tipo = str(mv.get("Tipo", ""))
        if not cod or cod == "nan":
            continue
        if tipo == "Entrada":
            total_stock[cod] = total_stock.get(cod, 0) + cant
        elif tipo == "Salida":
            total_stock[cod] = total_stock.get(cod, 0) - cant

    stock = {}
    for mv in movs:
        tipo = str(mv.get("Tipo", ""))
        cod  = str(mv.get("Codigo_mat", "") or "").strip()
        cant = safe_float(mv.get("Cantidad", 0))
        orig = str(mv.get("ID_Ubic_Origen",  "") or "").strip()
        dest = str(mv.get("ID_Ubic_Destino", "") or "").strip()
        if not cod or cod == "nan":
            continue
        if tipo == "Entrada" and dest and dest != "nan":
            stock.setdefault(dest, {})[cod] = stock.get(dest, {}).get(cod, 0) + cant
        elif tipo == "Salida" and orig and orig != "nan":
            stock.setdefault(orig, {})[cod] = stock.get(orig, {}).get(cod, 0) - cant
        elif tipo == "Traslado":
            if orig and orig != "nan":
                stock.setdefault(orig, {})[cod] = stock.get(orig, {}).get(cod, 0) - cant
            if dest and dest != "nan":
                stock.setdefault(dest, {})[cod] = stock.get(dest, {}).get(cod, 0) + cant

    mat_map = {m["Codigo_mat"]: m for m in mats}
    assigned = {}
    result = []
    for u in ubics:
        uid = str(u["ID_Ubic"])
        items = []
        for cod, qty in stock.get(uid, {}).items():
            if qty > 0:
                assigned[cod] = assigned.get(cod, 0) + qty
                items.append({
                    "Codigo_mat": cod,
                    "Descripcion": mat_map[cod].get("Descripci\u00f3n", cod) if cod in mat_map else cod,
                    "Unidad":      mat_map[cod].get("Unidad", "")      if cod in mat_map else "",
                    "Cantidad":    round(float(qty), 2),
                })
        items.sort(key=lambda x: x["Codigo_mat"])
        result.append({
            "ID_Ubic":     uid,
            "Descripcion": str(u.get("Descripci\u00f3n", "") or ""),
            "Zona":        str(u.get("Zona",    "") or ""),
            "Estante":     str(u.get("Estante", "") or ""),
            "Nivel":       str(u.get("Nivel",   "") or ""),
            "items":       items,
            "total_items": len(items),
        })

    huerfanos = []
    for cod, total in total_stock.items():
        diferencia = round(total - assigned.get(cod, 0), 4)
        if diferencia > 0 and cod in mat_map:
            huerfanos.append({
                "Codigo_mat":  cod,
                "Descripcion": mat_map[cod].get("Descripci\u00f3n", ""),
                "Unidad":      mat_map[cod].get("Unidad", ""),
                "Cantidad":    round(diferencia, 2),
            })
    if huerfanos:
        huerfanos.sort(key=lambda x: x["Codigo_mat"])
        result.append({
            "ID_Ubic":     "__SIN_UBIC__",
            "Descripcion": "Movimientos sin ubicaci\u00f3n asignada",
            "Zona":        "__SIN_UBIC__",
            "Estante":     "", "Nivel": "",
            "items":       huerfanos,
            "total_items": len(huerfanos),
            "sin_ubic":    True,
        })
    return jsonify(result)


@bp.route("/api/movimientos")
@require_login()
def api_movimientos():
    rows = _data.tlist("MOV_ALMACEN")
    cod  = request.args.get("material")
    proy = request.args.get("proyecto")
    if cod:
        rows = [r for r in rows if r.get("Codigo_mat") == cod]
    if proy:
        rows = [r for r in rows if r.get("ID_Proyecto") == proy]
    return jsonify(rows)


@bp.route("/api/movimientos", methods=["POST"])
@require_login()
def api_add_movimiento():
    raw  = request.get_json()
    now  = datetime.now()
    items = raw if isinstance(raw, list) else [raw]
    movs  = _data.tlist("MOV_ALMACEN")

    for item in items:
        if not item.get("Fecha"):
            item["Fecha"] = now.strftime("%Y-%m-%d")
        item["Hora"] = now.strftime("%H:%M")

        if item.get("Tipo") == "Salida":
            cod      = item.get("Codigo_mat", "")
            mat_movs = [m for m in movs if m["Codigo_mat"] == cod]
            entradas = sum(safe_float(m["Cantidad"]) for m in mat_movs if m["Tipo"] == "Entrada")
            salidas  = sum(safe_float(m["Cantidad"]) for m in mat_movs if m["Tipo"] == "Salida")
            stock    = entradas - salidas
            if float(item.get("Cantidad") or 0) > stock:
                return jsonify({
                    "ok": False,
                    "error": f"Stock insuficiente para {cod}. Disponible: {round(float(stock), 2)}"
                }), 400

        _data.tinsert("MOV_ALMACEN", item)

    return jsonify({"ok": True})


@bp.route("/api/lotes")
@require_login()
def api_lotes():
    return jsonify(_data.tlist("LOTES"))


@bp.route("/api/lotes", methods=["POST"])
@require_login()
def api_add_lote():
    data = request.get_json()
    if not data.get("FechaCompra"):
        data["FechaCompra"] = datetime.now().strftime("%Y-%m-%d")
    _data.tinsert("LOTES", data)
    return jsonify({"ok": True})
