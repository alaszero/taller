"""
core/helpers.py — Funciones utilitarias compartidas.
Extraídas de app_web.py para reutilización en módulos.
"""
import os


def safe_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return 0.0


_VERSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "VERSION")


def _read_version():
    try:
        with open(_VERSION_FILE) as f:
            return f.read().strip()
    except Exception:
        return "2.0.0"


def _increment_version():
    """Incrementa el patch de la versión (2.0.0 → 2.0.1) y devuelve la nueva."""
    ver = _read_version()
    parts = ver.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
    except ValueError:
        parts.append("1")
    new_ver = ".".join(parts)
    try:
        with open(_VERSION_FILE, "w") as f:
            f.write(new_ver + "\n")
    except Exception:
        pass
    return new_ver
