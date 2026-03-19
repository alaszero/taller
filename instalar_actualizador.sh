#!/bin/bash
# =============================================================================
# instalar_actualizador.sh — Instala el script de actualización en el servidor
# Ejecutar UNA SOLA VEZ en el servidor Ubuntu.
# Uso: sudo bash instalar_actualizador.sh
# =============================================================================
set -e

DEST="/usr/local/bin/actualizar-taller"

cat > "$DEST" << 'SCRIPT'
#!/bin/bash
# =============================================================================
# actualizar-taller — Actualizar el sistema Yekflow con un ZIP nuevo
# Uso: sudo actualizar-taller /ruta/al/archivo.zip
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

# ── Verificar argumento ─────────────────────────────────────────────────────
if [ -z "$ZIP" ]; then
    echo ""
    echo "Uso: sudo actualizar-taller /ruta/al/archivo.zip"
    echo ""
    echo "Ejemplo:"
    echo "  sudo actualizar-taller /home/serv-bar/Documentos/YekflowExports/taller_servidor_20260317_1430.zip"
    echo ""
    exit 1
fi

if [ ! -f "$ZIP" ]; then
    err "No se encontró el archivo: $ZIP"
fi

echo ""
echo "========================================"
echo "  Actualizando Yekflow"
echo "========================================"
echo "  Archivo: $(basename $ZIP)"
echo ""

# ── 1. Backup de la base de datos ──────────────────────────────────────────
if [ -f "$APP_DIR/taller.db" ]; then
    BACKUP_NAME="taller_$(date +%Y%m%d_%H%M%S).db"
    info "Haciendo backup de la base de datos..."
    mkdir -p "$BACKUP_DIR"
    cp "$APP_DIR/taller.db" "$BACKUP_DIR/$BACKUP_NAME"
    ok "Backup guardado: $BACKUP_DIR/$BACKUP_NAME"
else
    info "No existe taller.db previo (primera instalación)"
fi

# ── 2. Extraer ZIP (sin sobreescribir taller.db) ─────────────────────────
info "Extrayendo archivos nuevos..."
unzip -o "$ZIP" -d "$APP_DIR" -x "taller.db" > /dev/null
ok "Archivos extraídos en $APP_DIR"

# ── 3. Actualizar dependencias Python ────────────────────────────────────
if [ -f "$APP_DIR/requirements.txt" ]; then
    info "Actualizando dependencias Python..."
    "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" --quiet 2>/dev/null || true
    ok "Dependencias actualizadas"
fi

# ── 4. Ajustar permisos ─────────────────────────────────────────────────
chown -R taller:taller "$APP_DIR"
ok "Permisos ajustados"

# ── 5. Reiniciar servicio ────────────────────────────────────────────────
info "Reiniciando servicio..."
if systemctl is-active --quiet taller; then
    systemctl restart taller
    sleep 2
    if systemctl is-active --quiet taller; then
        ok "Servicio reiniciado correctamente"
    else
        err "El servicio no pudo iniciarse. Revisa: journalctl -u taller -n 50"
    fi
else
    systemctl start taller
    sleep 2
    ok "Servicio iniciado"
fi

# ── 6. Resumen ───────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo -e "${GREEN}  Actualización completada${NC}"
echo "========================================"
echo ""
echo "  Web:    https://yekflow.com"
echo "  Estado: systemctl status taller"
echo "  Logs:   journalctl -u taller -f"
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
SCRIPT

chmod +x "$DEST"
echo "✓ Comando 'actualizar-taller' instalado en $DEST"
echo ""
echo "Ahora puedes actualizar desde cualquier carpeta con:"
echo "  sudo actualizar-taller /ruta/al/archivo.zip"
echo ""
