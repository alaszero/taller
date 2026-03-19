"""
data/sqlite_backend.py — Capa de acceso a datos SQLite (taller-aware + audit).
Extraída de app_web.py para reutilización y modularidad.
"""
import os
import sqlite3
from datetime import datetime, timedelta
from flask import g, session, request
from werkzeug.security import generate_password_hash

import db as _db

from core.config import _CROSS_TALLER_TABLES, _PK_MAP, DEFAULT_SECCIONES, SESSION_TIMEOUT_MINUTES
from core.helpers import safe_float

# ── Base de datos ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.environ.get("TALLER_DB", os.path.join(BASE_DIR, "taller.db"))


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
        _db.init_db(DB_PATH)          # no-op si ya existe
        _seed_default_user(g.db)      # crea admin si no hay usuarios
    return g.db


def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _current_taller_id():
    """Devuelve el taller_id de la sesión activa, o None si es vista global (yekflow/__all__)."""
    tid = session.get("taller_id", "rober_lang")
    return None if tid == "__all__" else tid


def _audit(conn, accion, tabla, registro_id, antes=None, despues=None):
    """Escribe entrada en AUDIT_LOG usando el contexto de sesión actual."""
    try:
        _db.audit_log(
            conn,
            taller_id   = session.get("taller_id"),
            usuario     = session.get("username", "sistema"),
            ip          = request.remote_addr,
            accion      = accion,
            tabla       = tabla,
            registro_id = registro_id,
            antes       = antes,
            despues     = despues,
        )
    except Exception:
        pass  # La auditoría nunca debe interrumpir la operación principal


# ── Wrappers de acceso a datos (taller-aware + audit) ─────────────────────────

def tlist(table):
    """Lista todos los registros de la tabla, filtrados por taller activo.
    Incluye también filas con taller_id IS NULL para compatibilidad con datos legacy."""
    conn = get_db()
    tid = _current_taller_id()
    if tid and table not in _CROSS_TALLER_TABLES:
        try:
            cols = _db.get_columns(conn, table)
            if "taller_id" in cols:
                cur = conn.execute(
                    f'SELECT rowid, * FROM "{table}" WHERE "taller_id"=? OR "taller_id" IS NULL OR "taller_id"=\'\'',
                    (tid,)
                )
                return [_db._row_to_dict(r, cols) for r in cur.fetchall()]
        except Exception:
            pass
        return _db.table_to_list_filtered(conn, table, {"taller_id": tid})
    return _db.table_to_list(conn, table)


def tfiltered(table, **kw):
    """Lista registros filtrados por columna=valor, más filtro de taller activo.
    Incluye filas con taller_id NULL (datos legacy) cuando se activa el filtro de taller."""
    conn = get_db()
    tid = _current_taller_id()
    if tid and table not in _CROSS_TALLER_TABLES:
        try:
            cols = _db.get_columns(conn, table)
            if "taller_id" in cols:
                conds = [f'"{k}"=?' for k in kw]
                params = list(kw.values())
                conds.append(f'("taller_id"=? OR "taller_id" IS NULL OR "taller_id"=\'\')')
                params.append(tid)
                where = " AND ".join(conds)
                cur = conn.execute(f'SELECT rowid, * FROM "{table}" WHERE {where}', params)
                return [_db._row_to_dict(r, cols) for r in cur.fetchall()]
        except Exception:
            pass
        kw["taller_id"] = tid
    return _db.table_to_list_filtered(conn, table, kw)


def tinsert(table, data):
    """Inserta una fila inyectando taller_id y registrando en AUDIT_LOG.
    Si no hay taller activo (Vista Global), usa 'rober_lang' por defecto."""
    conn = get_db()
    tid = _current_taller_id()
    # Siempre asignar un taller para tablas de datos (None = Vista Global → usa rober_lang)
    effective_tid = tid if tid else "rober_lang"
    if table not in _CROSS_TALLER_TABLES:
        data = {**data, "taller_id": effective_tid}
    _db.insert_row(conn, table, data)
    # Obtener el rowid del registro recién insertado para el audit
    try:
        new_idx = conn.execute(f'SELECT last_insert_rowid()').fetchone()[0]
    except Exception:
        new_idx = None
    _audit(conn, "INSERT", table, new_idx, antes=None, despues=data)


def tupdate_pk(table, pk_col, pk_val, data):
    """Actualiza una fila por PK con snapshot antes/después en AUDIT_LOG."""
    conn = get_db()
    # Snapshot antes
    try:
        antes_rows = _db.table_to_list_filtered(conn, table, {pk_col: pk_val})
        antes = dict(antes_rows[0]) if antes_rows else None
    except Exception:
        antes = None
    result = _db.update_row_by_pk(conn, table, pk_col, pk_val, data)
    despues = {**antes, **data} if antes else data
    _audit(conn, "UPDATE", table, pk_val, antes=antes, despues=despues)
    return result


def tdelete_rowid(table, rowid):
    """Elimina una fila por rowid con snapshot en AUDIT_LOG."""
    conn = get_db()
    try:
        antes_rows = _db.table_to_list_filtered(conn, table, {"rowid": rowid})
        antes = dict(antes_rows[0]) if antes_rows else None
    except Exception:
        antes = None
    _db.tdelete_rowid(conn, table, rowid)
    _audit(conn, "DELETE", table, rowid, antes=antes, despues=None)


def tclear(table):
    return _db.clear_table(get_db(), table)


def tfiltered_dict(table, filters):
    """Lista registros filtrados por un dict {col: val}. Sin filtro de taller."""
    return _db.table_to_list_filtered(get_db(), table, filters)


# ── Raw table CRUD (para el editor de admin) ─────────────────────────────────

def raw_tabla_get(table_name):
    """Devuelve columnas y filas de una tabla para el editor CRUD."""
    conn = get_db()
    cols = _db.get_columns(conn, table_name)
    rows = _db.table_to_list(conn, table_name)
    return cols, rows


def raw_tabla_update(table_name, row_idx, col, value):
    """Actualiza una celda por rowid en el editor CRUD."""
    _db.update_cell_by_rowid(get_db(), table_name, int(row_idx), col, value)


def raw_tabla_delete(table_name, row_idx):
    """Elimina una fila por rowid en el editor CRUD."""
    _db.delete_row_by_rowid(get_db(), table_name, int(row_idx))


# ── Autenticación por sesión ──────────────────────────────────────────────────

def _seed_default_user(conn):
    """Migraciones idempotentes + usuario admin por defecto si la tabla está vacía."""
    # ── M0_tables: crear tablas nuevas si no existen ─────────────────────────
    # Necesario para Passenger/Hostinger donde __main__ no se ejecuta y
    # init_db() nunca es llamado. Cada sentencia es idempotente (IF NOT EXISTS).
    _new_tables = [
        """CREATE TABLE IF NOT EXISTS TALLERES (
            id TEXT PRIMARY KEY, nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1,
            creado_en TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS AUDIT_LOG (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taller_id TEXT, usuario TEXT, ip TEXT, accion TEXT,
            tabla TEXT, registro_id TEXT, antes TEXT, despues TEXT,
            ts TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS LOGIN_ATTEMPTS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT, username TEXT,
            ts TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS DASHBOARD_CACHE (
            taller_id TEXT PRIMARY KEY, data TEXT, ts TEXT)""",
        """CREATE TABLE IF NOT EXISTS ALERT_RULES (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taller_id TEXT, tipo TEXT, parametros TEXT,
            activa INTEGER DEFAULT 1,
            creada_en TEXT DEFAULT (datetime('now')))""",
        """CREATE TABLE IF NOT EXISTS ALERTAS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taller_id TEXT, rule_id INTEGER, tipo TEXT,
            mensaje TEXT, referencia TEXT, leida INTEGER DEFAULT 0,
            ts TEXT DEFAULT (datetime('now')))""",
    ]
    for _stmt in _new_tables:
        try:
            conn.execute(_stmt)
        except Exception:
            pass
    try:
        conn.commit()
    except Exception:
        pass

    # ── M0 (legacy): columna secciones en USUARIOS ───────────────────────────
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(USUARIOS)").fetchall()]
        if "secciones" not in cols:
            conn.execute("ALTER TABLE USUARIOS ADD COLUMN secciones TEXT DEFAULT ''")
            conn.commit()
            _db.clear_col_cache()
    except Exception:
        pass
    # ── M0b: renombrar nivel "usuario" → "almacen" (legacy) ─────────────────
    try:
        conn.execute("UPDATE USUARIOS SET nivel='almacen' WHERE nivel='usuario'")
        conn.commit()
    except Exception:
        pass
    # ── M0c: asegurar secciones correctas en nivel almacen ───────────────────
    try:
        conn.execute("""UPDATE USUARIOS SET secciones='almacen,herramientas'
                        WHERE nivel='almacen'
                          AND (secciones IS NULL OR secciones=''
                               OR secciones NOT LIKE '%almacen%')""")
        conn.commit()
    except Exception:
        pass
    # ── M0d: eliminar usuarios duplicados ────────────────────────────────────
    try:
        conn.execute("""DELETE FROM USUARIOS WHERE rowid NOT IN
                        (SELECT MIN(rowid) FROM USUARIOS GROUP BY username)""")
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_username ON USUARIOS(username)")
        conn.commit()
    except Exception:
        pass

    # ── M1: seed TALLERES con datos iniciales ────────────────────────────────
    try:
        conn.execute("INSERT OR IGNORE INTO TALLERES(id,nombre) VALUES('rober_lang','Rober Lang')")
        conn.execute("INSERT OR IGNORE INTO TALLERES(id,nombre) VALUES('testing','Testing')")
        conn.commit()
    except Exception:
        pass

    # ── M2: añadir taller_id a todas las tablas de datos ─────────────────────
    _TALLER_TABLES = [
        "MATERIALES", "HERRAMIENTAS", "EMPLEADOS", "UBICACIONES", "PROVEEDORES",
        "PROYECTOS", "MUEBLES", "ORDENES_PRODUCCION", "ETAPAS",
        "MOV_ALMACEN", "MOV_HERRA", "LOTES", "REG_AVANCE",
    ]
    for tabla in _TALLER_TABLES:
        try:
            cols = [r[1] for r in conn.execute(f"PRAGMA table_info({tabla})").fetchall()]
            if "taller_id" not in cols:
                conn.execute(f"ALTER TABLE {tabla} ADD COLUMN taller_id TEXT DEFAULT 'rober_lang'")
                conn.commit()
                _db.clear_col_cache()
        except Exception:
            pass

    # ── M2b: reparar filas sin taller asignado (NULL o vacío → rober_lang) ───
    # Corre siempre pero es O(0) cuando no hay filas sin taller
    for tabla in _TALLER_TABLES:
        try:
            conn.execute(f"""UPDATE {tabla} SET taller_id='rober_lang'
                             WHERE taller_id IS NULL OR taller_id=''""")
        except Exception:
            pass
    try:
        conn.commit()
    except Exception:
        pass

    # ── M3: crear usuario yekflowtotal si no existe ───────────────────────────
    try:
        yf_hash = generate_password_hash("yekflow2025")
        conn.execute(
            """INSERT OR IGNORE INTO USUARIOS(username, password_hash, nivel, nombre, activo, secciones)
               VALUES('yekflowtotal', ?, 'yekflow', 'YekFlow Admin', '1', '*')""",
            (yf_hash,),
        )
        conn.commit()
    except Exception:
        pass

    # ── M4: índices de rendimiento ────────────────────────────────────────────
    try:
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_ts     ON AUDIT_LOG(ts DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_taller ON AUDIT_LOG(taller_id, ts DESC)")
        for t in ["MATERIALES", "MOV_ALMACEN", "EMPLEADOS", "PROYECTOS"]:
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{t.lower()}_taller ON {t}(taller_id)")
        conn.commit()
    except Exception:
        pass

    # ── Seed: usuario admin si no hay ninguno (excepto yekflowtotal) ──────────
    try:
        rows = [r for r in _db.table_to_list(conn, "USUARIOS") if r.get("username") != "yekflowtotal"]
        if not rows:
            _db.insert_row(conn, "USUARIOS", {
                "username":      "admin",
                "password_hash": generate_password_hash("taller2024"),
                "nivel":         "superusuario",
                "nombre":        "Administrador",
                "activo":        "1",
                "secciones":     DEFAULT_SECCIONES["superusuario"],
            })
            conn.commit()
    except Exception:
        pass


def migrate_base_data_to_taller_raw(db_path: str, source_taller_id: str, target_taller_id: str) -> bool:
    """
    Copia datos MAESTROS (no transaccionales) de un taller a otro.
    VERSIÓN SIN CONTEXTO de Flask (para usar en cualquier contexto).

    Copia:
      - MATERIALES, HERRAMIENTAS, EMPLEADOS, UBICACIONES, PROVEEDORES, ETAPAS

    NO copia (datos transaccionales):
      - MOV_ALMACEN, MOV_HERRA, PROYECTOS, MUEBLES, ORDENES_PRODUCCION, REG_AVANCE, LOTES
    """
    _BASE_TABLES = ["MATERIALES", "HERRAMIENTAS", "EMPLEADOS", "UBICACIONES", "PROVEEDORES", "ETAPAS"]

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        for tabla in _BASE_TABLES:
            try:
                # Obtener columnas
                cur = conn.execute(f"PRAGMA table_info({tabla})")
                cols = [row[1] for row in cur.fetchall()]

                # Obtener todos los registros del taller origen
                cur = conn.execute(
                    f'SELECT * FROM "{tabla}" WHERE taller_id = ?',
                    (source_taller_id,)
                )
                rows = cur.fetchall()

                # Insertar con taller_id destino (usar INSERT OR IGNORE para evitar duplicados)
                for row in rows:
                    values = dict(row)
                    values["taller_id"] = target_taller_id

                    col_names = [f'"{c}"' for c in cols if c in values]
                    placeholders = ",".join("?" * len(col_names))
                    sql_vals = [values[c.strip('"')] for c in col_names]

                    sql = f'INSERT OR IGNORE INTO "{tabla}" ({",".join(col_names)}) VALUES ({placeholders})'
                    try:
                        conn.execute(sql, sql_vals)
                    except Exception:
                        pass

                conn.commit()

            except Exception as e:
                print(f"[MIGRATE] Error en {tabla}: {e}")
                pass

        conn.close()
        return True

    except Exception as e:
        print(f"[MIGRATE] Error general: {e}")
        return False


def migrate_base_data_to_taller(source_taller_id: str, target_taller_id: str):
    """
    Copia datos MAESTROS de un taller a otro (versión con contexto de Flask).
    Delegará a la versión raw.
    """
    try:
        db_path = DB_PATH
        return migrate_base_data_to_taller_raw(db_path, source_taller_id, target_taller_id)
    except Exception as e:
        print(f"[MIGRATE] Error: {e}")
        return False


def calcular_stock():
    mats = tlist("MATERIALES")
    movs = tlist("MOV_ALMACEN")

    result = []
    for m in mats:
        cod = m["Codigo_mat"]
        mat_movs = [mv for mv in movs if mv["Codigo_mat"] == cod]
        entradas  = sum(safe_float(mv["Cantidad"]) for mv in mat_movs if mv["Tipo"] == "Entrada")
        salidas   = sum(safe_float(mv["Cantidad"]) for mv in mat_movs if mv["Tipo"] == "Salida")
        stock_actual = entradas - salidas
        stock_min    = safe_float(m.get("Stock_min", 0))
        if stock_actual <= 0:
            nivel = "danger"
        elif stock_actual < stock_min:
            nivel = "warning"
        else:
            nivel = "ok"
        result.append({
            "Codigo_mat":   cod,
            "Descripcion":  m.get("Descripción", ""),
            "Unidad":       m.get("Unidad", ""),
            "Stock_min":    stock_min,
            "Stock_actual": round(float(stock_actual), 2),
            "Alerta":       nivel != "ok",
            "Nivel":        nivel,
        })
    return result


def _evaluar_alertas(conn, taller_id):
    """Evalúa condiciones y genera alertas nuevas sin duplicar las existentes no-leídas."""
    try:
        efectivo = None if taller_id == "__all__" else taller_id

        # ── Stock bajo (solo si tiene stock_min configurado > 0) ────────────
        stock = calcular_stock()
        for s in stock:
            if s["Nivel"] in ("danger", "warning") and s["Stock_min"] > 0:
                ref = f"stock_{s['Codigo_mat']}"
                existe = conn.execute(
                    "SELECT id FROM ALERTAS WHERE taller_id=? AND referencia=? "
                    "AND ts > datetime('now','-24 hours')",
                    (efectivo or "rober_lang", ref)
                ).fetchone()
                if not existe:
                    msg = (f"Stock {'agotado' if s['Nivel']=='danger' else 'bajo'}: "
                           f"{s['Descripcion']} ({s['Stock_actual']} {s['Unidad']})")
                    conn.execute(
                        "INSERT INTO ALERTAS(taller_id,tipo,mensaje,referencia) VALUES(?,?,?,?)",
                        (efectivo or "rober_lang", "stock_bajo", msg, ref)
                    )

        # ── Obras sin avance en los últimos 5 días ─────────────────────────
        avances = tlist("REG_AVANCE")
        proyectos = tlist("PROYECTOS")
        hoy = datetime.utcnow()
        for p in proyectos:
            if p.get("Estado") not in ("En proceso", "Iniciado", "En curso"):
                continue
            pid = str(p.get("ID_Proyecto", ""))
            ultimos_avances = [a for a in avances if str(a.get("ID_OP", "")).startswith(pid)
                               or str(a.get("ID_Proyecto", "")) == pid]
            if ultimos_avances:
                ultima_fecha_str = max(a.get("Fecha", "2000-01-01") for a in ultimos_avances)
                try:
                    ultima_fecha = datetime.strptime(ultima_fecha_str[:10], "%Y-%m-%d")
                    dias = (hoy - ultima_fecha).days
                except Exception:
                    dias = 0
            else:
                dias = 999
            if dias >= 5:
                ref = f"obra_detenida_{pid}"
                existe = conn.execute(
                    "SELECT id FROM ALERTAS WHERE taller_id=? AND referencia=? AND leida=0",
                    (efectivo or "rober_lang", ref)
                ).fetchone()
                if not existe:
                    msg = f"Obra sin avance {dias} días: {p.get('Nombre_Obra', pid)}"
                    conn.execute(
                        "INSERT INTO ALERTAS(taller_id,tipo,mensaje,referencia) VALUES(?,?,?,?)",
                        (efectivo or "rober_lang", "obra_detenida", msg, ref)
                    )
        conn.commit()
    except Exception:
        pass


def _sync_herramienta_estado(id_herramienta: str):
    movs    = tfiltered("MOV_HERRA", ID_Herramienta=id_herramienta)
    activos = [m for m in movs if m.get("FechaDevolucion", "") == ""]
    if activos:
        nuevo_estado = "Prestada"
        responsable  = activos[-1].get("Responsable", "")
    else:
        nuevo_estado = "Disponible"
        responsable  = ""
    tupdate_pk("HERRAMIENTAS", "ID_Herramienta", id_herramienta, {
        "Estado": nuevo_estado,
        "Responsable_Actual": responsable,
    })


# ── Audit / Alertas queries (usadas por admin blueprint) ─────────────────────

def audit_query(filters):
    """Devuelve entradas del AUDIT_LOG según filtros."""
    conn = get_db()
    conds, params = [], []
    if filters.get("taller"):
        conds.append("taller_id = ?");  params.append(filters["taller"])
    if filters.get("tabla"):
        conds.append("tabla = ?");      params.append(filters["tabla"])
    if filters.get("usuario"):
        conds.append("usuario = ?");    params.append(filters["usuario"])
    if filters.get("desde"):
        conds.append("ts >= ?");        params.append(filters["desde"])
    if filters.get("hasta"):
        conds.append("ts <= ?");        params.append(filters["hasta"])
    where = f"WHERE {' AND '.join(conds)}" if conds else ""
    limit = filters.get("limit", 200)
    sql = f"SELECT * FROM AUDIT_LOG {where} ORDER BY ts DESC LIMIT ?"
    params.append(limit)
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def alertas_query(taller_id, solo_no_leidas=True):
    """Devuelve alertas del taller (o todas si __all__)."""
    conn = get_db()
    if taller_id == "__all__":
        cond = "WHERE leida=0" if solo_no_leidas else ""
        rows = conn.execute(f"SELECT * FROM ALERTAS {cond} ORDER BY ts DESC LIMIT 200").fetchall()
    else:
        cond = "AND leida=0" if solo_no_leidas else ""
        rows = conn.execute(
            f"SELECT * FROM ALERTAS WHERE taller_id=? {cond} ORDER BY ts DESC LIMIT 200",
            (taller_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def alerta_marcar_leida(aid):
    conn = get_db()
    conn.execute("UPDATE ALERTAS SET leida=1 WHERE id=?", (aid,))
    conn.commit()


def alertas_marcar_todas_leidas(taller_id):
    conn = get_db()
    if taller_id == "__all__":
        conn.execute("UPDATE ALERTAS SET leida=1")
    else:
        conn.execute("UPDATE ALERTAS SET leida=1 WHERE taller_id=?", (taller_id,))
    conn.commit()


def create_backup():
    """Devuelve el archivo taller.db como descarga."""
    from flask import send_file, abort
    if not os.path.exists(DB_PATH):
        abort(404, "Base de datos no encontrada")
    now_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    return send_file(
        DB_PATH,
        mimetype="application/octet-stream",
        as_attachment=True,
        download_name=f"taller_backup_{now_str}.db",
    )


def restore_backup(uploaded_file):
    """Restaura taller.db desde un archivo subido."""
    from flask import jsonify
    if not (uploaded_file.filename.lower().endswith(".db") or
            uploaded_file.filename.lower().endswith(".sqlite")):
        return jsonify({"ok": False, "error": "El archivo debe ser un .db o .sqlite"}), 400
    try:
        uploaded_file.save(DB_PATH)
        return jsonify({"ok": True, "restored": [uploaded_file.filename]})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


def init_app(app):
    app.teardown_appcontext(close_db)
