"""
blueprints/network_local.py — Network/tunnel routes for local (app.py) version.
Includes LAN IP detection, Cloudflare tunnel, and auth toggle.
"""
import os
import re as _re
import json
import socket
import subprocess
import threading
from flask import Blueprint, jsonify, request
from core.auth import require_login

bp = Blueprint('network_local', __name__)

_data = None


def init_data(mod):
    global _data
    _data = mod


# ── Estado de red ────────────────────────────────────────────────────────────
_NET_CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "network_config.json"
)


def _load_net_state():
    try:
        with open(_NET_CONFIG_FILE) as f:
            d = json.load(f)
            return {"auth": bool(d.get("auth", True))}
    except Exception:
        return {"auth": True}


def _save_net_state():
    try:
        with open(_NET_CONFIG_FILE, "w") as f:
            json.dump({"auth": _net_state["auth"]}, f)
    except Exception:
        pass


_net_state = _load_net_state()


def _get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_net_state():
    """Devuelve el estado de red actual (para inyectar en admin template)."""
    return _net_state


def get_lan_ip():
    return _get_lan_ip()


# ── Estado del túnel Cloudflare ──────────────────────────────────────────────
_tunnel_state = {"proc": None, "url": None, "log": [], "running": False}
_tunnel_lock  = threading.Lock()


def _capture_tunnel_output(proc):
    url_pattern = _re.compile(r'https://[a-z0-9\-]+\.trycloudflare\.com')
    try:
        for line in iter(proc.stderr.readline, b''):
            decoded = line.decode("utf-8", errors="replace").rstrip()
            with _tunnel_lock:
                _tunnel_state["log"].append(decoded)
                if len(_tunnel_state["log"]) > 200:
                    _tunnel_state["log"] = _tunnel_state["log"][-100:]
                if not _tunnel_state["url"]:
                    m = url_pattern.search(decoded)
                    if m:
                        _tunnel_state["url"] = m.group(0)
    except Exception:
        pass
    with _tunnel_lock:
        _tunnel_state["running"] = False
        if _tunnel_state["proc"] is proc:
            _tunnel_state["proc"] = None


# ── Rutas ────────────────────────────────────────────────────────────────────

@bp.route("/api/admin/network", methods=["GET"])
@require_login(sections=["admin"])
def api_network_get():
    with _tunnel_lock:
        t_running = _tunnel_state["running"]
        t_url     = _tunnel_state["url"]
        t_log     = list(_tunnel_state["log"][-10:])
    return jsonify({
        "ok":     True,
        "auth":   _net_state["auth"],
        "lan_ip": _get_lan_ip(),
        "tunnel": {"running": t_running, "url": t_url, "log": t_log},
    })


@bp.route("/api/admin/network/auth", methods=["POST"])
@require_login(sections=["admin"])
def api_network_auth():
    data = request.get_json(force=True) or {}
    enabled = bool(data.get("enabled", True))
    _net_state["auth"] = enabled
    _save_net_state()
    return jsonify({"ok": True, "auth": _net_state["auth"]})


@bp.route("/api/admin/tunnel/start", methods=["POST"])
@require_login(sections=["admin"])
def api_tunnel_start():
    with _tunnel_lock:
        if _tunnel_state["running"]:
            return jsonify({"ok": False, "error": "El túnel ya está activo"})
        try:
            proc = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            _tunnel_state["proc"]    = proc
            _tunnel_state["url"]     = None
            _tunnel_state["log"]     = []
            _tunnel_state["running"] = True
        except FileNotFoundError:
            return jsonify({"ok": False, "error": "cloudflared no encontrado."})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)})

    t = threading.Thread(target=_capture_tunnel_output, args=(proc,), daemon=True)
    t.start()
    return jsonify({"ok": True, "message": "Túnel iniciado."})


@bp.route("/api/admin/tunnel/stop", methods=["POST"])
@require_login(sections=["admin"])
def api_tunnel_stop():
    with _tunnel_lock:
        proc = _tunnel_state.get("proc")
        if not proc:
            return jsonify({"ok": False, "error": "No hay túnel activo"})
        try:
            proc.terminate()
        except Exception:
            pass
        _tunnel_state["proc"]    = None
        _tunnel_state["url"]     = None
        _tunnel_state["running"] = False
        _tunnel_state["log"].append("— Túnel detenido manualmente —")
    return jsonify({"ok": True})


@bp.route("/api/admin/tunnel/status", methods=["GET"])
@require_login(sections=["admin"])
def api_tunnel_status():
    with _tunnel_lock:
        return jsonify({
            "ok":      True,
            "running": _tunnel_state["running"],
            "url":     _tunnel_state["url"],
            "log":     list(_tunnel_state["log"][-15:]),
        })
