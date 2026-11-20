#!/usr/bin/env bash
# Apply the Snow Leopard look. WARNING: --reset-layout replaces your current panels
# with the menu bar + dock layout. Pass --keep-layout to keep your panels.
set -euo pipefail
LAYOUT="--resetLayout"
[ "${1:-}" = "--keep-layout" ] && LAYOUT=""

plasma-apply-lookandfeel -a org.snowleopard.desktop $LAYOUT

# Mac button order: close, minimise, maximise on the left; nothing on the right.
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft "XIA"
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight ""

# Kvantum theme selection (only matters once Kvantum is installed).
kwriteconfig6 --file "$HOME/.config/Kvantum/kvantum.kvconfig" --group General --key theme SnowLeopard

qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
echo "Applied. Restart running apps to pick up the new widget style."
