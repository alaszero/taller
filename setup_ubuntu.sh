#!/bin/bash
# =============================================================================
# setup_ubuntu.sh — Instalación inicial del Servidor Taller (Ubuntu)
# Ejecutar UNA SOLA VEZ como root o con sudo
# Uso: sudo bash setup_ubuntu.sh
# =============================================================================

set -e  # Detener si hay cualquier error

# ── Colores para mensajes ────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sin color

ok()   { echo -e "${GREEN}✓ $1${NC}"; }
info() { echo -e "${YELLOW}→ $1${NC}"; }
err()  { echo -e "${RED}✗ $1${NC}"; exit 1; }

# ── Verificar que se ejecuta como root ──────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    err "Ejecuta este script con sudo: sudo bash setup_ubuntu.sh"
fi

echo ""
echo "=============================================="
echo "  Instalación del Servidor Taller Carpintería"
echo "=============================================="
echo ""

# ── 1. Actualizar sistema e instalar dependencias ────────────────────────────
info "Actualizando sistema..."
apt-get update -qq
apt-get install -y python3 python3-venv python3-pip unzip curl wget -qq
ok "Python y dependencias instalados"

# ── 2. Crear usuario del sistema 'taller' ────────────────────────────────────
info "Creando usuario del sistema 'taller'..."
if id "taller" &>/dev/null; then
    ok "Usuario 'taller' ya existe"
else
    useradd -r -m -d /home/taller -s /bin/bash taller
    ok "Usuario 'taller' creado"
fi

# ── 3. Crear estructura de directorios ───────────────────────────────────────
info "Creando directorios..."
mkdir -p /home/taller/app
mkdir -p /home/taller/backups
chown -R taller:taller /home/taller
ok "Directorios creados"

# ── 4. Crear entorno virtual Python ─────────────────────────────────────────
info "Creando entorno virtual Python..."
if [ ! -d "/home/taller/app/venv" ]; then
    sudo -u taller python3 -m venv /home/taller/app/venv
    ok "Entorno virtual creado"
else
    ok "Entorno virtual ya existe"
fi

# ── 5. Instalar Flask en el entorno virtual ───────────────────────────────────
info "Instalando Flask..."
sudo -u taller /home/taller/app/venv/bin/pip install flask --quiet
ok "Flask instalado"

# ── 6. Instalar cloudflared ───────────────────────────────────────────────────
info "Instalando cloudflared..."
if command -v cloudflared &>/dev/null; then
    ok "cloudflared ya está instalado"
else
    # Detectar arquitectura
    ARCH=$(dpkg --print-architecture)
    if [ "$ARCH" = "amd64" ]; then
        CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
    elif [ "$ARCH" = "arm64" ]; then
        CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb"
    else
        CF_URL="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb"
    fi
    wget -q "$CF_URL" -O /tmp/cloudflared.deb
    dpkg -i /tmp/cloudflared.deb
    rm /tmp/cloudflared.deb
    ok "cloudflared instalado"
fi

# ── 7. Instalar servicio systemd para la app ─────────────────────────────────
info "Instalando servicio taller.service..."
if [ -f "./taller.service" ]; then
    cp ./taller.service /etc/systemd/system/taller.service
    systemctl daemon-reload
    systemctl enable taller
    ok "Servicio taller instalado y habilitado para inicio automático"
else
    echo ""
    echo -e "${YELLOW}AVISO: No se encontró taller.service en el directorio actual."
    echo -e "Cópialo manualmente a /etc/systemd/system/taller.service${NC}"
fi

# ── 8. Permisos del directorio de backups ─────────────────────────────────────
chown -R taller:taller /home/taller/backups
chmod 750 /home/taller/backups
ok "Permisos configurados"

# ── 9. Resumen final ──────────────────────────────────────────────────────────
echo ""
echo "=============================================="
echo -e "${GREEN}  Instalación completada${NC}"
echo "=============================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "  1. Copia los archivos de la app al servidor:"
echo "     bash update_server.sh taller_servidor_YYYYMMDD.zip"
echo ""
echo "  2. Edita la clave secreta en el servicio:"
echo "     nano /etc/systemd/system/taller.service"
echo "     → Cambia SECRET_KEY por una clave segura aleatoria"
echo "     systemctl daemon-reload && systemctl restart taller"
echo ""
echo "  3. Configura Cloudflare Tunnel (ver README_SERVIDOR.md):"
echo "     cloudflared tunnel login"
echo "     cloudflared tunnel create taller"
echo "     cloudflared tunnel route dns taller tudominio.com"
echo "     cloudflared service install"
echo ""
echo "  4. Verifica que la app está corriendo:"
echo "     systemctl status taller"
echo "     curl http://localhost:5000"
echo ""
