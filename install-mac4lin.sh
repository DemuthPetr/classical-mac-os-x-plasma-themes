#!/usr/bin/env bash
# Install the Mac4Lin (Leopard) global theme into your home directory. Changes no settings.
set -euo pipefail
cd "$(dirname "$0")"
[ -d build ] || python3 build.py
[ -d build-mac4lin ] || python3 mac4lin_gen.py

DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONF="${XDG_CONFIG_HOME:-$HOME/.config}"
copy() { mkdir -p "$2"; rm -rf "$2/$(basename "$1")"; cp -a "$1" "$2/"; echo "  $2/$(basename "$1")"; }

# Plasma style, colours and the dock trash launcher are shared with the Snow Leopard theme.
[ -d "$DATA/plasma/desktoptheme/SnowLeopard" ] || ./install.sh

echo "Installing Mac4Lin theme:"
copy build-mac4lin/aurorae/themes/Mac4Lin                    "$DATA/aurorae/themes"
copy build-mac4lin/plasma/look-and-feel/org.mac4lin.desktop  "$DATA/plasma/look-and-feel"
copy build-mac4lin/icons/Mac4Lin                             "$DATA/icons"
copy build-mac4lin/icons/Mac4Lin-Cursors                     "$DATA/icons"
copy build-mac4lin/sounds/Mac4Lin                            "$DATA/sounds"
copy build-mac4lin/fonts/Mac4Lin                             "$DATA/fonts"
for w in build-mac4lin/wallpapers/*; do copy "$w" "$DATA/wallpapers"; done
copy build-mac4lin/Kvantum/Mac4Lin                           "$CONF/Kvantum"

# The pack has no Apple logo; borrow WhiteSur's if it is installed.
if [ -f "$DATA/icons/WhiteSur/places/scalable/start-here.svg" ]; then
    cp "$DATA/icons/WhiteSur/places/scalable/start-here.svg" "$DATA/icons/Mac4Lin/scalable/places/start-here.svg"
elif [ -f "$DATA/icons/WhiteSur/places/24/start-here.svg" ]; then
    cp "$DATA/icons/WhiteSur/places/24/start-here.svg" "$DATA/icons/Mac4Lin/scalable/places/start-here.svg"
fi

fc-cache -f "$DATA/fonts" >/dev/null 2>&1 || true
echo "Done. Pick 'Mac4Lin (Leopard)' in System Settings > Global Theme, or run ./apply-mac4lin.sh"
