"""
core/config.py — Constantes de configuración compartidas.
Extraídas de app_web.py para reutilización en módulos.
"""
import os

SESSION_TIMEOUT_MINUTES = int(os.environ.get("SESSION_TIMEOUT", "30"))

# ── Permisos modulares por sección ────────────────────────────────────────────
DEFAULT_SECCIONES = {
    "yekflow":       "dashboard,almacen,herramientas,proyectos,avance,empleados,implementacion,admin",
    "superusuario":  "dashboard,almacen,herramientas,proyectos,avance,empleados,implementacion,admin",
    "administrador": "dashboard,almacen,herramientas,proyectos,avance,empleados",
    "supervisor":    "proyectos,avance",
    "almacen":       "almacen,herramientas",
}
SECTION_ROUTES = {
    "dashboard": "/", "almacen": "/almacen", "herramientas": "/herramientas",
    "proyectos": "/proyectos", "avance": "/avance", "empleados": "/empleados",
    "implementacion": "/implementacion", "admin": "/admin",
}
VALID_NIVELES = tuple(DEFAULT_SECCIONES.keys())

# ── Multi-taller: tablas que NO se filtran por taller ─────────────────────────
_CROSS_TALLER_TABLES = {"USUARIOS", "TALLERES", "AUDIT_LOG"}

# ── PK de cada tabla (para audit snapshot) ────────────────────────────────────
_PK_MAP = {
    "MATERIALES":        "Codigo_mat",
    "HERRAMIENTAS":      "ID_Herramienta",
    "EMPLEADOS":         "EmpleadoID",
    "UBICACIONES":       "ID_Ubic",
    "PROVEEDORES":       "ProveedorID",
    "PROYECTOS":         "ID_Proyecto",
    "MUEBLES":           "ID_Mueble",
    "ORDENES_PRODUCCION":"ID_OP",
    "ETAPAS":            "Etapa",
    "MOV_ALMACEN":       "_idx",
    "MOV_HERRA":         "_idx",
    "LOTES":             "LoteID",
    "REG_AVANCE":        "_idx",
    "USUARIOS":          "username",
    "TALLERES":          "id",
}

# ── Registro de tablas para editor CRUD de admin ──────────────────────────────
_TABLE_REGISTRY = {
    "movimientos":  {"table": "MOV_ALMACEN",        "label": "Movimientos de Almacén"},
    "prestamos":    {"table": "MOV_HERRA",           "label": "Préstamos de Herramientas"},
    "avance":       {"table": "REG_AVANCE",          "label": "Registro de Avance"},
    "lotes":        {"table": "LOTES",               "label": "Lotes de Material"},
    "materiales":   {"table": "MATERIALES",          "label": "Materiales"},
    "herramientas": {"table": "HERRAMIENTAS",        "label": "Herramientas"},
    "empleados":    {"table": "EMPLEADOS",           "label": "Empleados"},
    "ubicaciones":  {"table": "UBICACIONES",         "label": "Ubicaciones de Almacén"},
    "proveedores":  {"table": "PROVEEDORES",         "label": "Proveedores"},
    "proyectos":    {"table": "PROYECTOS",           "label": "Proyectos"},
    "muebles":      {"table": "MUEBLES",             "label": "Muebles"},
    "ordenes":      {"table": "ORDENES_PRODUCCION",  "label": "Órdenes de Producción"},
    "etapas":       {"table": "ETAPAS",              "label": "Etapas de Producción"},
}

# ── Mapeo para reset de tablas ────────────────────────────────────────────────
_RESET_MAP = {
    "movimientos":  "MOV_ALMACEN",
    "prestamos":    "MOV_HERRA",
    "avance":       "REG_AVANCE",
    "lotes":        "LOTES",
    "materiales":   "MATERIALES",
    "herramientas": "HERRAMIENTAS",
    "empleados":    "EMPLEADOS",
    "ubicaciones":  "UBICACIONES",
    "proveedores":  "PROVEEDORES",
    "proyectos":    "PROYECTOS",
    "muebles":      "MUEBLES",
    "ordenes":      "ORDENES_PRODUCCION",
    "etapas":       "ETAPAS",
}
