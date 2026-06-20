#!/usr/bin/env bash
set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Installing Haptic Overlay...${NC}"

# ── Check uv ────────────────────────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
    echo -e "${RED}Error: uv is not installed.${NC}"
    echo "Install it with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# ── Install package ──────────────────────────────────────────────────────────
echo "Building and installing package..."
uv tool install --reinstall .

# ── Check /dev/input permissions ────────────────────────────────────────────
if ! groups | grep -qw input; then
    echo -e "${YELLOW}"
    echo "  Warning: you are not in the 'input' group."
    echo "  Without it the overlay cannot read your mouse buttons."
    echo "  Fix it with (then log out and back in):"
    echo "    sudo usermod -aG input \$USER"
    echo -e "${NC}"
fi

# ── XDG autostart ───────────────────────────────────────────────────────────
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_DIR/haptic-overlay.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Haptic Overlay
Comment=Radial menu overlay triggered by haptic device input
Exec=haptic-overlay
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF

echo -e "${GREEN}"
echo "  Installation complete!"
echo ""
echo "  Start now : haptic-overlay"
echo "  Settings  : haptic-overlay-settings"
echo "  Config    : ~/.config/haptic-overlay/config.json"
echo "  Autostart : enabled (takes effect on next login)"
echo ""
echo "  To uninstall: ./uninstall.sh"
echo -e "${NC}"