"""
blueprints/network.py — Network/tunnel stub routes (no-op in production).
"""
from flask import Blueprint, jsonify

bp = Blueprint('network', __name__)

# Module-level data accessor (set by init_data)
_data = None


def init_data(mod):
    global _data
    _data = mod


@bp.route("/api/admin/network", methods=["GET"])
@bp.route("/api/admin/network/auth", methods=["POST"])
@bp.route("/api/admin/tunnel/start", methods=["POST"])
@bp.route("/api/admin/tunnel/stop", methods=["POST"])
@bp.route("/api/admin/tunnel/status", methods=["GET"])
def api_no_disponible():
    return jsonify({"ok": False, "error": "No disponible en produccion"}), 404
