#!/usr/bin/env bash
# Switch to one Mac OS X version look. Keeps your panels unless --reset-layout is given.
#   ./apply-version.sh tiger
#   ./apply-version.sh mavericks --reset-layout
set -euo pipefail
cd "$(dirname "$0")"
key="${1:-}"
layout=""
[ "${2:-}" = "--reset-layout" ] && layout="--resetLayout"

case "$key" in
    leopard)      lnf=org.mac4lin.desktop;     kv=Mac4Lin ;;
    snowleopard)  lnf=org.snowleopard.desktop; kv=SnowLeopard ;;
    cheetah|puma|jaguar|panther|tiger|lion|mavericks)
                  lnf="org.macosx.$key.desktop"; kv="MacOSX-${key^}" ;;
    mountainlion) lnf=org.macosx.mountainlion.desktop; kv=MacOSX-MountainLion ;;
    *) echo "usage: $0 <cheetah|puma|jaguar|panther|tiger|leopard|snowleopard|lion|mountainlion|mavericks> [--reset-layout]"; exit 1 ;;
esac

plasma-apply-lookandfeel -a "$lnf" $layout

kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnLeft "XIA"
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key ButtonsOnRight ""
kwriteconfig6 --file "$HOME/.config/Kvantum/kvantum.kvconfig" --group General --key theme "$kv"

# Every release up to Mavericks used Lucida Grande and the classic system sounds.
if fc-list | grep -qi "Lucida Grande"; then
    size=$(kreadconfig6 --file kdeglobals --group General --key font | cut -d, -f2)
    size=${size:-10}
    for k in font menuFont toolBarFont; do
        kwriteconfig6 --file kdeglobals --group General --key "$k" "Lucida Grande,$size,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
    done
    kwriteconfig6 --file kdeglobals --group WM --key activeFont "Lucida Grande,$size,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"
fi
[ -d "$HOME/.local/share/sounds/Mac4Lin" ] && kwriteconfig6 --file kdeglobals --group Sounds --key Theme Mac4Lin

# Wallpaper: the global theme only sets it together with a layout reset, so set it directly.
wall=$(kreadconfig6 --file "$HOME/.local/share/plasma/look-and-feel/$lnf/contents/defaults" --group Wallpaper --key Image)
if [ -n "$wall" ]; then
    qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
desktops().forEach(function(d){ d.wallpaperPlugin='org.kde.image';
  d.currentConfigGroup=['Wallpaper','org.kde.image','General'];
  d.writeConfig('Image','file://' + userDataPath('data','wallpapers') + '/$wall'); });" >/dev/null || true
fi

rm -f "$HOME/.cache/icon-cache.kcache"
qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
echo "Applied $key. Restart running apps (and plasmashell for dock icons) to see everything."
