"""
db.py — Capa de acceso a datos SQLite para el Sistema de Taller
Usado por app_web.py (versión producción para Hostinger).
"""
import sqlite3

# ── Schema ─────────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS MATERIALES (
    Codigo_mat TEXT, Tipo TEXT, "Descripción" TEXT, Unidad TEXT, Stock_min TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS HERRAMIENTAS (
    ID_Herramienta TEXT, Herramienta TEXT, Marca TEXT, Modelo TEXT, Tipo TEXT,
    NS TEXT, Categoria TEXT, "Ubicación_Base" TEXT, Estado TEXT,
    Responsable_Actual TEXT, Fecha_Alta TEXT, Observaciones TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS EMPLEADOS (
    EmpleadoID TEXT, Nombre TEXT, Apellido TEXT, Alias TEXT, Area TEXT,
    Puesto TEXT, Especialidad TEXT, NivelExperiencia TEXT, FechaIngreso TEXT,
    SalarioHora TEXT, CostoHoraReal TEXT, Activo TEXT, SupervisorID TEXT,
    Observaciones TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS UBICACIONES (
    ID_Ubic TEXT, Zona TEXT, "Descripción" TEXT, Tipo TEXT,
    Estante TEXT, Nivel TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS PROVEEDORES (
    ProveedorID TEXT, Nombre TEXT, Telefono TEXT, Email TEXT,
    RFC TEXT, Contacto TEXT, Categoria TEXT, Observaciones TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS PROYECTOS (
    ID_Proyecto TEXT, Cliente TEXT, Nombre_Obra TEXT,
    Inicio TEXT, Fin TEXT, Encargado TEXT, Estado TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS MUEBLES (
    ID_Mueble TEXT, ID_Proyecto TEXT, Mueble TEXT, Cantidad TEXT,
    Tipo TEXT, Area TEXT, "Observación" TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS ORDENES_PRODUCCION (
    ID_OP TEXT, ID_Mueble TEXT, Etapa TEXT, Cantidad TEXT,
    FechaInicioPlaneada TEXT, FechaFinalPlaneada TEXT,
    FechaInicioReal TEXT, FechaFinalReal TEXT, Responsable TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS ETAPAS (
    Etapa TEXT, "Orden" TEXT, Area TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS MOV_ALMACEN (
    Fecha TEXT, Codigo_mat TEXT, Tipo TEXT, Cantidad TEXT, Unidad TEXT,
    ID_Proyecto TEXT, Mueble TEXT, ID_Trab TEXT,
    ID_Ubic_Origen TEXT, ID_Ubic_Destino TEXT, Hora TEXT, Folio TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS MOV_HERRA (
    ID_Prestamo TEXT, FechaSalida TEXT, ID_Herramienta TEXT, Herramienta TEXT,
    Responsable TEXT, Nombre_Responsable TEXT, Proyecto TEXT,
    FechaDevolucion TEXT, Hora TEXT, Folio TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS LOTES (
    LoteID TEXT, MaterialID TEXT, FechaCompra TEXT, FechaCaducidad TEXT,
    CantidadInicial TEXT, CantidadDisponible TEXT, UbicacionID TEXT,
    CostoUnitario TEXT, ProveedorID TEXT, EstadoLote TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS REG_AVANCE (
    Fecha TEXT, ID_OP TEXT, EmpleadoID TEXT,
    Etapa TEXT, Estado TEXT, Horas TEXT, Piezas TEXT,
    taller_id TEXT DEFAULT 'rober_lang'
);
CREATE TABLE IF NOT EXISTS USUARIOS (
    username TEXT UNIQUE, password_hash TEXT, nivel TEXT,
    nombre TEXT, activo TEXT, secciones TEXT
);
CREATE TABLE IF NOT EXISTS TALLERES (
    id        TEXT PRIMARY KEY,
    nombre    TEXT NOT NULL,
    activo    INTEGER DEFAULT 1,
    creado_en TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS AUDIT_LOG (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    taller_id   TEXT,
    usuario     TEXT,
    ip          TEXT,
    accion      TEXT,
    tabla       TEXT,
    registro_id TEXT,
    antes       TEXT,
    despues     TEXT,
    ts          TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS LOGIN_ATTEMPTS (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    ip       TEXT,
    username TEXT,
    ts       TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS DASHBOARD_CACHE (
    taller_id TEXT PRIMARY KEY,
    data      TEXT,
    ts        TEXT
);
CREATE TABLE IF NOT EXISTS ALERT_RULES (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    taller_id  TEXT,
    tipo       TEXT,
    parametros TEXT,
    activa     INTEGER DEFAULT 1,
    creada_en  TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS ALERTAS (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    taller_id TEXT,
    rule_id   INTEGER,
    tipo      TEXT,
    mensaje   TEXT,
    referencia TEXT,
    leida     INTEGER DEFAULT 0,
    ts        TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_audit_ts       ON AUDIT_LOG(ts DESC);
CREATE INDEX IF NOT EXISTS idx_audit_taller   ON AUDIT_LOG(taller_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_attempts_ip    ON LOGIN_ATTEMPTS(ip, ts DESC);
CREATE INDEX IF NOT EXISTS idx_alertas_taller ON ALERTAS(taller_id, leida, ts DESC);
CREATE INDEX IF NOT EXISTS idx_materiales_taller    ON MATERIALES(taller_id);
CREATE INDEX IF NOT EXISTS idx_herramientas_taller  ON HERRAMIENTAS(taller_id);
CREATE INDEX IF NOT EXISTS idx_empleados_taller     ON EMPLEADOS(taller_id);
CREATE INDEX IF NOT EXISTS idx_proyectos_taller     ON PROYECTOS(taller_id);
CREATE INDEX IF NOT EXISTS idx_mov_almacen_taller   ON MOV_ALMACEN(taller_id);
CREATE INDEX IF NOT EXISTS idx_mov_herra_taller     ON MOV_HERRA(taller_id);
"""

# ── Tabla → columnas (caché en memoria) ───────────────────────────────────────
_col_cache: dict = {}


def init_db(db_path: str):
    """Crea todas las tablas si no existen y migra columnas faltantes."""
    conn = sqlite3.connect(db_path)

    # ── Migración: agregar taller_id a tablas existentes que no lo tengan ────
    _tables_with_taller = [
        "MATERIALES", "HERRAMIENTAS", "EMPLEADOS", "UBICACIONES",
        "PROVEEDORES", "PROYECTOS", "MUEBLES", "ORDENES_PRODUCCION",
        "ETAPAS", "MOV_ALMACEN", "MOV_HERRA", "LOTES", "REG_AVANCE",
    ]
    for tbl in _tables_with_taller:
        try:
            cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{tbl}")').fetchall()]
            if cols and "taller_id" not in cols:
                conn.execute(f'ALTER TABLE "{tbl}" ADD COLUMN taller_id TEXT DEFAULT \'rober_lang\'')
        except sqlite3.OperationalError:
            pass  # tabla no existe aún, SCHEMA la creará

    conn.commit()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def get_columns(conn: sqlite3.Connection, table: str) -> list:
    """Devuelve la lista de nombres de columnas de la tabla."""
    key = id(conn.database_path if hasattr(conn, 'database_path') else 0) + hash(table)
    if key not in _col_cache:
        cur = conn.execute(f'PRAGMA table_info("{table}")')
        _col_cache[key] = [row[1] for row in cur.fetchall()]
    return _col_cache[key]


# Limpia la caché (útil en tests)
def clear_col_cache():
    _col_cache.clear()


def _row_to_dict(row, cols) -> dict:
    """Convierte una fila (rowid, col1, col2, ...) a dict con _idx."""
    d = {"_idx": row[0]}
    for i, col in enumerate(cols):
        val = row[i + 1]
        d[col] = str(val) if val is not None else ""
    return d


def table_to_list(conn: sqlite3.Connection, table: str) -> list:
    """Todos los registros de la tabla como lista de dicts. Incluye _idx=rowid."""
    cols = get_columns(conn, table)
    cur = conn.execute(f'SELECT rowid, * FROM "{table}"')
    return [_row_to_dict(r, cols) for r in cur.fetchall()]


def table_to_list_filtered(conn: sqlite3.Connection, table: str,
                            filters: dict) -> list:
    """Registros filtrados. filters = {columna: valor}"""
    cols = get_columns(conn, table)
    conds = [f'"{k}" = ?' for k in filters]
    params = list(filters.values())
    where = f' WHERE {" AND ".join(conds)}' if conds else ""
    cur = conn.execute(f'SELECT rowid, * FROM "{table}"{where}', params)
    return [_row_to_dict(r, cols) for r in cur.fetchall()]


def table_to_list_multi(conn: sqlite3.Connection, table: str,
                         filters: dict = None, not_empty: str = None,
                         last_n: int = None) -> list:
    """Versión extendida con soporte para NOT EMPTY y LIMIT."""
    cols = get_columns(conn, table)
    conds, params = [], []
    if filters:
        for k, v in filters.items():
            conds.append(f'"{k}" = ?')
            params.append(v)
    if not_empty:
        conds.append(f'("{not_empty}" IS NULL OR "{not_empty}" = "")')
    where = f' WHERE {" AND ".join(conds)}' if conds else ""
    order = " ORDER BY rowid" if last_n else ""
    sql = f'SELECT rowid, * FROM "{table}"{where}{order}'
    rows = conn.execute(sql, params).fetchall()
    if last_n:
        rows = rows[-last_n:]
    return [_row_to_dict(r, cols) for r in rows]


def insert_row(conn: sqlite3.Connection, table: str, data: dict):
    """Inserta una fila usando los campos presentes en data."""
    cols = get_columns(conn, table)
    col_names = [f'"{c}"' for c in cols if c in data]
    values = [data[c] for c in cols if c in data]
    if not col_names:
        return
    ph = ",".join("?" for _ in col_names)
    sql = f'INSERT INTO "{table}" ({",".join(col_names)}) VALUES ({ph})'
    conn.execute(sql, values)
    conn.commit()


def update_cell_by_rowid(conn: sqlite3.Connection, table: str,
                          rowid: int, col: str, value: str):
    """Actualiza una celda específica por rowid."""
    conn.execute(f'UPDATE "{table}" SET "{col}" = ? WHERE rowid = ?', (value, rowid))
    conn.commit()


def update_row_by_pk(conn: sqlite3.Connection, table: str,
                     pk_col: str, pk_val: str, data: dict) -> bool:
    """Actualiza una fila completa buscando por columna clave."""
    cols = get_columns(conn, table)
    updates = [f'"{c}" = ?' for c in cols if c in data]
    values = [data[c] for c in cols if c in data]
    if not updates:
        return False
    values.append(pk_val)
    sql = f'UPDATE "{table}" SET {", ".join(updates)} WHERE "{pk_col}" = ?'
    cur = conn.execute(sql, values)
    conn.commit()
    return cur.rowcount > 0


def delete_row_by_rowid(conn: sqlite3.Connection, table: str, rowid: int):
    """Elimina una fila por rowid."""
    conn.execute(f'DELETE FROM "{table}" WHERE rowid = ?', (rowid,))
    conn.commit()


def clear_table(conn: sqlite3.Connection, table: str):
    """Borra todos los registros de la tabla."""
    conn.execute(f'DELETE FROM "{table}"')
    conn.commit()


def tdelete_rowid(conn: sqlite3.Connection, table: str, rowid: int):
    """Elimina una fila por rowid (alias semántico de delete_row_by_rowid)."""
    conn.execute(f'DELETE FROM "{table}" WHERE rowid = ?', (rowid,))
    conn.commit()


def audit_log(conn: sqlite3.Connection, taller_id, usuario, ip,
              accion, tabla, registro_id, antes, despues):
    """Escribe una entrada en AUDIT_LOG. antes/despues deben ser dict o None."""
    import json as _json
    conn.execute(
        """INSERT INTO AUDIT_LOG
           (taller_id, usuario, ip, accion, tabla, registro_id, antes, despues)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            taller_id, usuario, ip, accion, tabla, str(registro_id) if registro_id is not None else None,
            _json.dumps(antes, ensure_ascii=False) if antes is not None else None,
            _json.dumps(despues, ensure_ascii=False) if despues is not None else None,
        ),
    )
    conn.commit()
