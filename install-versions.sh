#!/usr/bin/env bash
# Install the per-version themes (10.0-10.4, 10.7-10.9) into your home directory. Changes no settings.
set -euo pipefail
cd "$(dirname "$0")"
[ -d build-versions ] || python3 versions.py

DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
CONF="${XDG_CONFIG_HOME:-$HOME/.config}"
copy() { mkdir -p "$2"; rm -rf "$2/$(basename "$1")"; cp -a "$1" "$2/"; }

# Icons, cursors, sounds, Lucida Grande and the dock trash launcher come from these two.
[ -d "$DATA/plasma/desktoptheme/SnowLeopard" ] || ./install.sh
if [ ! -d "$DATA/icons/Mac4Lin" ]; then
    if [ -f vendor/Mac4Lin_Install_v1.0.zip ]; then ./install-mac4lin.sh
    else echo "Mac4Lin pack not in vendor/: skipping Leopard icons, cursors, sounds and font."; fi
fi

for d in build-versions/aurorae/themes/*;            do copy "$d" "$DATA/aurorae/themes"; done
for d in build-versions/plasma/desktoptheme/*;       do copy "$d" "$DATA/plasma/desktoptheme"; done
for d in build-versions/plasma/look-and-feel/*;      do copy "$d" "$DATA/plasma/look-and-feel"; done
for d in build-versions/wallpapers/*;                do copy "$d" "$DATA/wallpapers"; done
for d in build-versions/color-schemes/*;             do copy "$d" "$DATA/color-schemes"; done
for d in build-versions/Kvantum/*;                   do copy "$d" "$CONF/Kvantum"; done
echo "Installed:"
ls build-versions/plasma/look-and-feel | sed 's/^/  /'
echo "Switch with ./apply-version.sh <cheetah|puma|jaguar|panther|tiger|leopard|snowleopard|lion|mountainlion|mavericks>"
