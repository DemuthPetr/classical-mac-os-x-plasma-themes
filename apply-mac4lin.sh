#!/usr/bin/env bash
# Apply the Mac4Lin (Leopard) theme. Keeps your panels unless you pass --reset-layout.
set -euo pipefail
LAYOUT=""
[ "${1:-}" = "--reset-layout" ] && LAYOUT="--resetLayout"

plasma-apply-lookandfeel -a org.mac4lin.desktop $LAYOUT

kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft "XIA"
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight ""
kwriteconfig6 --file "$HOME/.config/Kvantum/kvantum.kvconfig" --group General --key theme Mac4Lin
kwriteconfig6 --file kdeglobals --group Sounds --key Theme Mac4Lin

# Lucida Grande everywhere, keeping your current point size.
size=$(kreadconfig6 --file kdeglobals --group General --key font | cut -d, -f2)
size=${size:-10}
for key in font menuFont toolBarFont; do
    kwriteconfig6 --file kdeglobals --group General --key "$key" "Lucida Grande,$size,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
done
kwriteconfig6 --file kdeglobals --group General --key smallestReadableFont "Lucida Grande,$((size - 2)),-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
kwriteconfig6 --file kdeglobals --group WM --key activeFont "Lucida Grande,$size,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"

qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
echo "Applied. Restart running apps to pick up the new widget style and font."
