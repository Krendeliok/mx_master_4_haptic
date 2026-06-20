#!/usr/bin/env bash
set -euo pipefail

echo "Uninstalling Haptic Overlay..."

if command -v uv &>/dev/null; then
    uv tool uninstall haptic-overlay 2>/dev/null && echo "  Package removed." || echo "  Package was not installed."
else
    echo "  uv not found — skipping package removal."
fi

DESKTOP="$HOME/.config/autostart/haptic-overlay.desktop"
if [[ -f "$DESKTOP" ]]; then
    rm "$DESKTOP"
    echo "  Autostart entry removed."
fi

echo ""
echo "Done. Config is kept at ~/.config/haptic-overlay/ — remove manually if you want a clean slate."