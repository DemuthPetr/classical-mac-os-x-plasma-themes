#!/usr/bin/env bash
# Copy the built theme into your home directory. Installs nothing system-wide and changes no settings.
set -euo pipefail
cd "$(dirname "$0")"
[ -d build ] || python3 build.py

DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONF="${XDG_CONFIG_HOME:-$HOME/.config}"

copy() { mkdir -p "$2"; rm -rf "$2/$(basename "$1")"; cp -r "$1" "$2/"; echo "  $2/$(basename "$1")"; }

echo "Installing Snow Leopard theme:"
copy build/aurorae/themes/SnowLeopard                       "$DATA/aurorae/themes"
copy build/plasma/desktoptheme/SnowLeopard                  "$DATA/plasma/desktoptheme"
copy build/plasma/look-and-feel/org.snowleopard.desktop     "$DATA/plasma/look-and-feel"
for w in build/wallpapers/*; do copy "$w" "$DATA/wallpapers"; done
copy build/color-schemes/SnowLeopard.colors                 "$DATA/color-schemes"
copy build/applications/snowleopard-trash.desktop           "$DATA/applications"
copy build/Kvantum/SnowLeopard                              "$CONF/Kvantum"

if ls /usr/lib/qt6/plugins/styles/libkvantum*.so >/dev/null 2>&1; then
    echo "Kvantum found: global theme will use the Aqua widget style."
else
    sed -i 's/^widgetStyle=kvantum$/widgetStyle=Breeze/' \
        "$DATA/plasma/look-and-feel/org.snowleopard.desktop/contents/defaults"
    echo "Kvantum not installed: global theme falls back to Breeze widgets."
    echo "For Aqua buttons/scrollbars: sudo pacman -S kvantum   (official 'extra' repo), then re-run this script."
fi
LNF_DEFAULTS="$DATA/plasma/look-and-feel/org.snowleopard.desktop/contents/defaults"
if [ -d "$DATA/icons/WhiteSur-light" ]; then
    sed -i 's/^Theme=oxygen$/Theme=WhiteSur-light/' "$LNF_DEFAULTS"
    echo "WhiteSur icons found: global theme will use WhiteSur-light."
fi
echo "Done. Pick 'Snow Leopard' in System Settings > Colours & Themes > Global Theme, or run ./apply.sh"
