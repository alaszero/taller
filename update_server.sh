#!/bin/bash
# =============================================================================
# update_server.sh — Actualizar el servidor con un nuevo paquete ZIP
# Uso: bash update_server.sh taller_servidor_20241201_1430.zip
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓ $1${NC}"; }
info() { echo -e "${YELLOW}→ $1${NC}"; }
err()  { echo -e "${RED}✗ $1${NC}"; exit 1; }

APP_DIR="/home/taller/app"
BACKUP_DIR="/home/taller/backups"
ZIP="$1"

# ── Verificar argumento ───────────────────────────────────────────────────────
if [ -z "$ZIP" ]; then
    err "Falta el nombre del archivo ZIP.\nUso: bash update_server.sh taller_servidor_YYYYMMDD_HHMM.zip"
fi

if [ ! -f "$ZIP" ]; then
    err "No se encontró el archivo: $ZIP"
fi

echo ""
echo "========================================"
echo "  Actualizando Servidor Taller"
echo "========================================"
echo ""

# ── 1. Backup de la base de datos ────────────────────────────────────────────
if [ -f "$APP_DIR/taller.db" ]; then
    BACKUP_NAME="taller_$(date +%Y%m%d_%H%M%S).db"
    info "Haciendo backup de la base de datos..."
    mkdir -p "$BACKUP_DIR"
    cp "$APP_DIR/taller.db" "$BACKUP_DIR/$BACKUP_NAME"
    ok "Backup guardado: $BACKUP_DIR/$BACKUP_NAME"
else
    info "No existe taller.db previo (primera instalación)"
fi

# ── 2. Extraer ZIP (sin sobreescribir taller.db) ─────────────────────────────
info "Extrayendo archivos nuevos..."
unzip -o "$ZIP" -d "$APP_DIR" -x "taller.db" > /dev/null
ok "Archivos extraídos"

# ── 3. Actualizar dependencias Python ────────────────────────────────────────
if [ -f "$APP_DIR/requirements.txt" ]; then
    info "Actualizando dependencias Python..."
    "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" --quiet
    ok "Dependencias actualizadas"
fi

# ── 4. Ajustar permisos ───────────────────────────────────────────────────────
chown -R taller:taller "$APP_DIR"
ok "Permisos ajustados"

# ── 5. Reiniciar servicio ─────────────────────────────────────────────────────
info "Reiniciando servicio..."
if systemctl is-active --quiet taller; then
    systemctl restart taller
    sleep 2
    if systemctl is-active --quiet taller; then
        ok "Servicio reiniciado correctamente"
    else
        err "El servicio no pudo iniciarse. Revisa los logs: journalctl -u taller -n 50"
    fi
else
    systemctl start taller
    sleep 2
    ok "Servicio iniciado"
fi

# ── 6. Resumen ────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo -e "${GREEN}  Actualización completada${NC}"
echo "========================================"
echo ""
echo "  App corriendo en: http://localhost:5000"
echo "  Estado del servicio: systemctl status taller"
echo "  Ver logs en vivo:    journalctl -u taller -f"
echo ""

# Limpiar backups viejos (mantener últimos 10)
if [ -d "$BACKUP_DIR" ]; then
    BACKUP_COUNT=$(ls "$BACKUP_DIR"/*.db 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 10 ]; then
        info "Limpiando backups antiguos (conservando los 10 más recientes)..."
        ls -t "$BACKUP_DIR"/*.db | tail -n +11 | xargs rm -f
        ok "Backups limpiados"
    fi
fi
