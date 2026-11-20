#!/usr/bin/env python3
"""Turn the Mac4Lin 1.0 GNOME pack (vendor/Mac4Lin_Install_v1.0.zip) into a Plasma 6 global theme.

Only artwork is used (icons, cursors, sounds, wallpapers, Lucida Grande, Emerald pixmaps).
Nothing from the pack is executed. Output goes to ./build-mac4lin.
"""
import base64
import io
import os
import shutil
import sys
import tarfile
import zipfile
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import palette as P  # noqa: E402
import kvantum_gen  # noqa: E402
import extras_gen as X  # noqa: E402
from aurorae_gen import _shadow  # noqa: E402
from svgkit import clip_poly, path_d, fmt  # noqa: E402

ZIP = os.path.join(HERE, "vendor", "Mac4Lin_Install_v1.0.zip")
OUT = os.path.join(HERE, "build-mac4lin")
PFX = "Mac4Lin_Install_v1.0/"
LNF_ID = "org.mac4lin.desktop"


# ---------------------------------------------------------------- unpacking
def member_tar(zf, path):
    """Open a .tar.gz stored inside the zip, without touching disk."""
    return tarfile.open(fileobj=io.BytesIO(zf.read(PFX + path)), mode="r:gz")


def safe_extract(tf, dest, strip=1):
    """Extract regular files and relative symlinks only, never outside dest."""
    dest = os.path.realpath(dest)
    for m in tf.getmembers():
        parts = m.name.split("/")[strip:]
        if not parts or any(p in ("", "..") for p in parts) or ".svn" in parts or parts[-1].endswith("~"):
            continue
        target = os.path.join(dest, *parts)
        if not os.path.realpath(os.path.dirname(target)).startswith(dest):
            continue
        if m.isdir():
            os.makedirs(target, exist_ok=True)
        elif m.issym():
            resolved = os.path.realpath(os.path.join(os.path.dirname(target), m.linkname))
            if m.linkname.startswith("/") or not resolved.startswith(dest):
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if not os.path.lexists(target):
                os.symlink(m.linkname, target)
        elif m.isfile():
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as f:
                f.write(tf.extractfile(m).read())


def alias(directory, src, *names):
    if not os.path.exists(os.path.join(directory, src)):
        return
    for n in names:
        p = os.path.join(directory, n)
        if not os.path.lexists(p):
            os.symlink(src, p)


# ---------------------------------------------------------------- icons
KDE_APP_ALIASES = {
    "nautilus.png": ["org.kde.dolphin.png", "dolphin.png", "system-file-manager.png"],
    "Terminal.png": ["org.kde.konsole.png", "konsole.png", "utilities-terminal.png", "org.kde.yakuake.png"],
    "gnome-settings.png": ["systemsettings.png", "org.kde.systemsettings.png", "preferences-system.png",
                           "preferences-desktop.png", "configure.png"],
    "text-editor.png": ["org.kde.kate.png", "kate.png", "org.kde.kwrite.png", "kwrite.png"],
    "system-monitor.png": ["org.kde.plasma-systemmonitor.png", "ksysguard.png", "utilities-system-monitor.png"],
    "accessories-calculator.png": ["org.kde.kcalc.png", "kcalc.png"],
    "system-software-installer.png": ["org.kde.discover.png", "plasmadiscover.png"],
    "gnome-web-browser.png": ["web-browser.png", "internet-web-browser.png"],
}
KDE_FOLDER_ALIASES = {
    "Documents.png": ["folder-documents.png"],
    "Downloads.png": ["folder-download.png", "folder-downloads.png"],
    "Music.png": ["folder-music.png", "folder-sound.png"],
    "Pictures.png": ["folder-pictures.png", "folder-image.png"],
    "Videos.png": ["folder-videos.png", "folder-video.png"],
    "Desktop.png": ["folder-desktop.png"],
    "Public.png": ["folder-public.png", "folder-publicshare.png"],
    "Sites.png": ["folder-html.png"],
    "Applications.png": ["folder-development.png"],
    "Library.png": ["folder-templates.png"],
    "Network.png": ["folder-network.png", "folder-remote.png"],
}


def build_icons(zf):
    dest = os.path.join(OUT, "icons/Mac4Lin")
    safe_extract(member_tar(zf, "Icons/Mac4Lin_Icons_v1.0.tar.gz"), dest, strip=1)
    idx = os.path.join(dest, "index.theme")
    with open(idx) as f:
        text = f.read()
    text = text.replace("Name=Mac4Lin_Icons_v1.0", "Name=Mac4Lin").replace("Inherits=gnome", "Inherits=oxygen,breeze,hicolor")
    # KDE only understands "Type=Scalable" (capital S); the pack's lowercase makes every dir exact-128
    # and lets Oxygen win. Also give the scalable dirs an explicit size range.
    text = "\n".join("Type=Scalable\nMinSize=8\nMaxSize=512" if l.strip().lower() == "type=scalable" else l
                     for l in text.splitlines()) + "\n"
    # Same story for contexts: KDE matches them case-sensitively.
    contexts = {c.lower(): c for c in ("Actions", "Animations", "Applications", "Categories", "Devices", "Emblems",
                                         "Emotes", "International", "MimeTypes", "Places", "Status", "Stock")}
    text = "\n".join("Context=" + contexts.get(l.split("=", 1)[1].strip().lower(), l.split("=", 1)[1])
                     if l.startswith("Context=") else l for l in text.splitlines()) + "\n"
    with open(idx, "w") as f:
        f.write(text)
    apps = os.path.join(dest, "scalable/apps")
    for src, names in KDE_APP_ALIASES.items():
        alias(apps, src, *names)
    places = os.path.join(dest, "scalable/places")
    for src, names in KDE_FOLDER_ALIASES.items():
        if os.path.exists(os.path.join(dest, "scalable/folders", src)):
            alias(places, f"../folders/{src}", *names)
    # The pack's start-here is a GNOME foot; drop it so the launcher falls back to a better logo.
    for n in ("start-here.png", "distributor-logo.png", "gnome-main-menu.png", "main-menu.png"):
        p = os.path.join(places, n)
        if os.path.lexists(p):
            os.remove(p)


# ---------------------------------------------------------------- cursors
CURSOR_ALIASES = {
    "left_ptr": ["default", "arrow", "top_left_arrow", "context-menu", "left-arrow"],
    "hand2": ["pointer", "pointing_hand", "e29285e634086352946a0e7090d73106"],
    "hand1": ["grab", "openhand", "grabbing", "closedhand", "dnd-move", "dnd-none"],
    "xterm": ["text", "ibeam", "vertical-text"],
    "watch": ["wait"],
    "left_ptr_watch": ["progress", "half-busy"],
    "question_arrow": ["help", "whats_this", "left_ptr_help"],
    "fleur": ["move", "all-scroll", "size_all"],
    "crossed_circle": ["not-allowed", "no-drop", "forbidden", "circle"],
    "crosshair": ["cell", "cross", "tcross", "color-picker"],
    "copy": ["dnd-copy"],
    "sb_h_double_arrow": ["ew-resize", "col-resize", "e-resize", "w-resize", "size_hor", "split_h",
                          "right_side", "left_side"],
    "sb_v_double_arrow": ["ns-resize", "row-resize", "n-resize", "s-resize", "size_ver", "split_v",
                          "top_side", "bottom_side"],
    "fd_double_arrow": ["nesw-resize", "size_bdiag"],
    "bd_double_arrow": ["nwse-resize", "size_fdiag"],
    "top_left_corner": ["nw-resize"],
    "top_right_corner": ["ne-resize"],
    "bottom_left_corner": ["sw-resize"],
    "bottom_right_corner": ["se-resize"],
}


def build_cursors(zf):
    dest = os.path.join(OUT, "icons/Mac4Lin-Cursors")
    safe_extract(member_tar(zf, "Cursor/Mac4Lin_Cursors_v1.0.tar.gz"), dest, strip=1)
    shutil.rmtree(os.path.join(dest, "source"), ignore_errors=True)
    cur = os.path.join(dest, "cursors")
    for src, names in CURSOR_ALIASES.items():
        alias(cur, src, *names)
    with open(os.path.join(dest, "index.theme"), "w") as f:
        f.write("[Icon Theme]\nName=Mac4Lin\nComment=Mac OS X Leopard cursors from Mac4Lin\nInherits=breeze_cursors\n")


# ---------------------------------------------------------------- sounds
SOUND_NAMES = {
    "Tink.wav": ["bell", "bell-window-system"],
    "Basso.wav": ["dialog-error", "dialog-error-critical"],
    "Funk.wav": ["dialog-warning", "dialog-warning-auth"],
    "Glass.wav": ["dialog-information", "complete", "message"],
    "Pop.wav": ["message-new-instant", "message-highlight"],
    "New Messages.wav": ["message-new-email"],
    "Hardware Connected.wav": ["device-added", "power-plug"],
    "Hardware Disconnected.wav": ["device-removed", "power-unplug"],
    "Trash Empty.wav": ["trash-empty"],
    "Trash Drop Item.wav": ["trash-drop"],
    "System Log In.wav": ["desktop-login", "service-login"],
    "System Log Off.wav": ["desktop-logout", "service-logout"],
    "Print Complete.wav": ["completion-success"],
    "Sosumi.wav": ["completion-fail", "battery-low", "battery-caution"],
    "Hero.wav": ["outcome-success", "theme-demo"],
    "Ping.wav": ["dialog-question"],
    "Purr.wav": ["audio-volume-change"],
}


def build_sounds(zf):
    dest = os.path.join(OUT, "sounds/Mac4Lin")
    raw = os.path.join(dest, "original")
    safe_extract(member_tar(zf, "Sounds/Mac4Lin_Sounds_v1.0.tar.gz"), raw, strip=0)
    stereo = os.path.join(dest, "stereo")
    os.makedirs(stereo, exist_ok=True)
    for src, names in SOUND_NAMES.items():
        if os.path.exists(os.path.join(raw, src)):
            for n in names:
                os.symlink(f"../original/{src}", os.path.join(stereo, f"{n}.wav"))
    with open(os.path.join(dest, "index.theme"), "w") as f:
        f.write("[Sound Theme]\nName=Mac4Lin\nComment=Mac OS X system sounds from Mac4Lin\n"
                "Inherits=ocean,freedesktop\nDirectories=stereo\n\n[stereo]\nOutputProfile=stereo\n")


# ---------------------------------------------------------------- fonts / wallpapers
def build_fonts(zf):
    tf = member_tar(zf, "Fonts/fonts.tar.gz")
    dest = os.path.join(OUT, "fonts/Mac4Lin")
    os.makedirs(dest, exist_ok=True)
    for m in tf.getmembers():
        base = os.path.basename(m.name)
        if m.isfile() and base.startswith("Lucida Grande"):
            with open(os.path.join(dest, base), "wb") as f:
                f.write(tf.extractfile(m).read())


WALLS = {"Mac4LinAurora": ("Mac4Lin Aurora", "Wallpapers/Mac4Lin_Wallpaper1.jpg"),
         "Mac4LinGrass": ("Mac4Lin Grass", "Wallpapers/Mac4Lin_Wallpaper2.jpg")}


def build_wallpapers(zf):
    first = None
    for wid, (name, path) in WALLS.items():
        img = Image.open(io.BytesIO(zf.read(PFX + path))).convert("RGB")
        d = os.path.join(OUT, f"wallpapers/{wid}/contents")
        os.makedirs(os.path.join(d, "images"), exist_ok=True)
        img.save(os.path.join(d, f"images/{img.width}x{img.height}.jpg"), quality=95)
        img.resize((400, 250), Image.LANCZOS).save(os.path.join(d, "screenshot.jpg"), quality=90)
        with open(os.path.join(OUT, f"wallpapers/{wid}/metadata.json"), "w") as f:
            f.write(X.wallpaper_meta(wid, name))
        first = first or img
    return first


# ---------------------------------------------------------------- window decoration from Emerald pixmaps
PAD_T, PAD_B, PAD_L, PAD_R = 14, 28, 22, 22
TITLE_H = 22
BOTTOM_H = 7
CORNER = 6
EMERALD = "Emerald/Mac4Lin_Emerald_Aqua_v1.0.tar.gz"


def rounded(img, radius, corners):
    """Antialiased transparency outside rounded corners ('tl', 'tr', 'bl', 'br')."""
    s = 4
    w, h = img.size
    mask = Image.new("L", (w * s, h * s), 255)
    d = ImageDraw.Draw(mask)
    r = radius * s
    for c in corners:
        x0 = 0 if c[1] == "l" else w * s - 2 * r
        y0 = 0 if c[0] == "t" else h * s - 2 * r
        cx0 = 0 if c[1] == "l" else w * s - r
        cy0 = 0 if c[0] == "t" else h * s - r
        d.rectangle([cx0, cy0, cx0 + r - 1, cy0 + r - 1], fill=0)
        d.ellipse([x0, y0, x0 + 2 * r - 1, y0 + 2 * r - 1], fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)
    out = img.convert("RGBA")
    a = Image.composite(out.getchannel("A"), Image.new("L", (w, h), 0), mask)
    out.putalpha(a)
    return out


def whiten(img, k):
    """Blend colour towards white, keep alpha."""
    img = img.convert("RGBA")
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    out = Image.blend(img, white, k)
    out.putalpha(img.getchannel("A"))
    return out


def data_uri(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def image_tag(uri, x, y, w, h):
    return (f'<image x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" preserveAspectRatio="none" '
            f'xlink:href="{uri}"/>')


def emerald_images(zf):
    tf = member_tar(zf, EMERALD)
    imgs = {}
    for m in tf.getmembers():
        if m.isfile() and m.name.endswith(".png"):
            imgs[os.path.basename(m.name)] = Image.open(io.BytesIO(tf.extractfile(m).read())).convert("RGBA")
    return imgs


def decoration_svg(px, title_bottom):
    tl = rounded(px["pixmaps.active_top_left.png"], CORNER, ["tl"])
    tr = rounded(px["pixmaps.active_top_right.png"], CORNER, ["tr"])
    bl = rounded(px["pixmaps.active_bottom_left.png"], 5, ["bl"])
    br = rounded(px["pixmaps.active_bottom_right.png"], 5, ["br"])
    uris = {k: data_uri(v) for k, v in {
        "tl": tl, "top": px["pixmaps.active_top.png"], "tr": tr, "left": px["pixmaps.active_left.png"],
        "right": px["pixmaps.active_right.png"], "bl": bl, "bottom": px["pixmaps.active_bottom.png"], "br": br}.items()}
    # Emerald reuses the active pixmaps for inactive windows; Leopard washes them out instead.
    faded = {k: data_uri(whiten(Image.open(io.BytesIO(base64.b64decode(v.split(",", 1)[1]))), 0.42))
             for k, v in uris.items()}

    body = []
    defs = []
    L, R = PAD_L + CORNER, PAD_R + CORNER
    T, B = PAD_T + TITLE_H, PAD_B + BOTTOM_H
    W, H = L + 60 + R, T + 60 + B

    def frame(prefix, ox, oy, inactive):
        wx, wy = ox + PAD_L, oy + PAD_T
        ww, wh = W - PAD_L - PAD_R, H - PAD_T - PAD_B
        shadow = _shadow(wx, wy, ww, wh, 0.55 if inactive else 1.0)
        # what each slice shows: (image key, x, y, w, h)
        xs = [ox, ox + L, ox + W - R, ox + W]
        ys = [oy, oy + T, oy + H - B, oy + H]
        cx0, cx1 = wx + CORNER, wx + ww - CORNER
        imgs = {
            "topleft": [("tl", wx, wy, CORNER, TITLE_H)],
            "top": [("top", xs[1], wy, xs[2] - xs[1], TITLE_H)],
            "topright": [("tr", cx1, wy, CORNER, TITLE_H)],
            "left": [("left", wx, ys[1], 1, ys[2] - ys[1])],
            "right": [("right", wx + ww - 1, ys[1], 1, ys[2] - ys[1])],
            "bottomleft": [("bl", wx, wy + wh - BOTTOM_H, CORNER, BOTTOM_H)],
            "bottom": [("bottom", xs[1], wy + wh - BOTTOM_H, xs[2] - xs[1], BOTTOM_H)],
            "bottomright": [("br", cx1, wy + wh - BOTTOM_H, CORNER, BOTTOM_H)],
            "center": [],
        }
        slots = {"topleft": (0, 0), "top": (1, 0), "topright": (2, 0), "left": (0, 1), "center": (1, 1),
                 "right": (2, 1), "bottomleft": (0, 2), "bottom": (1, 2), "bottomright": (2, 2)}
        for name, (i, j) in slots.items():
            x0, y0, x1, y1 = xs[i], ys[j], xs[i + 1], ys[j + 1]
            parts = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#000" fill-opacity="0"/>']
            for poly, paint in shadow:
                d = path_d(clip_poly(poly, x0, y0, x1, y1))
                if d:
                    col, op = paint[:7], int(paint[7:9], 16) / 255
                    parts.append(f'<path d="{d}" fill="{col}" fill-opacity="{fmt(op)}"/>')
            # area under the client: title-bottom colour hides the fractional-scaling seam
            inner = clip_poly([(wx + 1, wy + TITLE_H), (wx + ww - 1, wy + TITLE_H),
                               (wx + ww - 1, wy + wh - BOTTOM_H), (wx + 1, wy + wh - BOTTOM_H)], x0, y0, x1, y1)
            if inner:
                fill = lighten(title_bottom, 0.42) if inactive else title_bottom
                parts.append(f'<path d="{path_d(inner)}" fill="{fill}"/>')
            for key, ix, iy, iw, ih in imgs[name]:
                parts.append(image_tag((faded if inactive else uris)[key], ix, iy, iw, ih))
            pid = f"{prefix}-center" if name == "center" else f"{prefix}-{name}"
            body.append(f'<g id="{pid}">{"".join(parts)}</g>')

    frame("decoration", 10, 10, False)
    frame("decoration-inactive", 10 + W + 20, 10, True)
    for k, (name, inactive) in enumerate((("decoration-maximized", False), ("decoration-maximized-inactive", True))):
        x, y = 10 + k * 80, H + 30
        g = image_tag((faded if inactive else uris)["top"], x, y, 60, TITLE_H)
        body.append(f'<g id="{name}-center">{g}</g>')
    body.append(f'<g id="hint-stretch-borders"><rect x="300" y="{H + 30}" width="4" height="4" fill-opacity="0"/></g>')
    total_w, total_h = 2 * W + 40, H + 70
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}"><defs>{"".join(defs)}</defs>'
            + "\n".join(body) + "</svg>\n")


BTN_W, BTN_H = 20, 22


def button_svg(sprite):
    frames = 6
    fw = sprite.width // frames
    cells = [sprite.crop((i * fw, 0, i * fw + fw, sprite.height)) for i in range(frames)]
    states = [("active", 0), ("hover", 1), ("pressed", 2), ("inactive", 3), ("hover-inactive", 4),
              ("pressed-inactive", 2), ("deactivated", 3), ("deactivated-inactive", 3)]
    body = []
    for k, (name, f) in enumerate(states):
        x, y = 10 + k * (BTN_W + 10), 10
        img = cells[f]
        ix, iy = x + (BTN_W - img.width) / 2, y + (BTN_H - img.height) / 2 + 0.5
        body.append(f'<g id="{name}-center"><rect x="{x}" y="{y}" width="{BTN_W}" height="{BTN_H}" fill-opacity="0"/>'
                    f'{image_tag(data_uri(img), ix, iy, img.width, img.height)}</g>')
    w = 20 + len(states) * (BTN_W + 10)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{BTN_H + 20}" '
            f'viewBox="0 0 {w} {BTN_H + 20}">' + "".join(body) + "</svg>\n")


def build_decoration(zf):
    px = emerald_images(zf)
    top = px["pixmaps.active_top.png"]
    # the title pixmap is drawn 22 px tall; its bottom row is what the toolbar has to continue from
    r = top.getpixel((0, top.height - 1))
    title_bottom = "#{:02X}{:02X}{:02X}".format(*r[:3])
    dest = os.path.join(OUT, "aurorae/themes/Mac4Lin")
    os.makedirs(dest, exist_ok=True)
    with open(os.path.join(dest, "decoration.svg"), "w") as f:
        f.write(decoration_svg(px, title_bottom))
    for ours, theirs in (("close", "buttons.close.png"), ("minimize", "buttons.min.png"),
                         ("maximize", "buttons.max.png"), ("restore", "buttons.max.png")):
        with open(os.path.join(dest, f"{ours}.svg"), "w") as f:
            f.write(button_svg(px[theirs]))
    with open(os.path.join(dest, "Mac4Linrc"), "w") as f:
        f.write(f"""[General]
ActiveTextColor=34,34,34
InactiveTextColor=120,120,120
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=0
ButtonGroupHover=true

[Layout]
BorderLeft=1
BorderRight=1
BorderBottom={BOTTOM_H}
TitleEdgeTop=0
TitleEdgeBottom=0
TitleEdgeLeft=7
TitleEdgeRight=7
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized=0
TitleEdgeLeftMaximized=7
TitleEdgeRightMaximized=7
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight={TITLE_H}
ButtonWidth={BTN_W}
ButtonHeight={BTN_H}
ButtonSpacing=0
ButtonMarginTop=0
ExplicitButtonSpacer=10
PaddingTop={PAD_T}
PaddingBottom={PAD_B}
PaddingLeft={PAD_L}
PaddingRight={PAD_R}
""")
    with open(os.path.join(dest, "metadata.desktop"), "w") as f:
        f.write(aurorae_meta())
    return title_bottom


def aurorae_meta():
    return """[Desktop Entry]
Name=Mac4Lin
Comment=Leopard window frame converted from the Mac4Lin Emerald theme
X-KDE-PluginInfo-Author=Mac4Lin project (artwork), converted for Plasma 6
X-KDE-PluginInfo-Name=Mac4Lin
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-License=GPL
X-KDE-PluginInfo-EnabledByDefault=true
"""


# ---------------------------------------------------------------- Kvantum variant with matching toolbar
def lighten(c, k):
    v = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(x + (255 - x) * k):02X}" for x in v)


def darken(c, k):
    v = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(x * (1 - k)):02X}" for x in v)


def build_kvantum(title_bottom):
    saved = (P.TITLE_BOTTOM, P.TOOLBAR_BOTTOM, P.TOOLBAR_LINE, P.TITLE_INACTIVE_BOTTOM)
    P.TITLE_BOTTOM = title_bottom
    P.TOOLBAR_BOTTOM = darken(title_bottom, 0.17)
    P.TOOLBAR_LINE = "#505050"
    P.TITLE_INACTIVE_BOTTOM = lighten(title_bottom, 0.42)
    try:
        svg = kvantum_gen.build_svg()
    finally:
        P.TITLE_BOTTOM, P.TOOLBAR_BOTTOM, P.TOOLBAR_LINE, P.TITLE_INACTIVE_BOTTOM = saved
    d = os.path.join(OUT, "Kvantum/Mac4Lin")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "Mac4Lin.svg"), "w") as f:
        f.write(svg)
    with open(os.path.join(d, "Mac4Lin.kvconfig"), "w") as f:
        f.write(kvantum_gen.KVCONFIG.replace("comment=Mac OS X 10.6 Snow Leopard Aqua controls",
                                             "comment=Aqua controls matched to the Mac4Lin window frame"))


# ---------------------------------------------------------------- global theme
LNF_META = """{
    "KPackageStructure": "Plasma/LookAndFeel",
    "KPlugin": {
        "Authors": [{"Name": "Mac4Lin artwork, converted for Plasma 6"}],
        "Category": "",
        "Description": "Mac OS X Leopard from the Mac4Lin pack: original icons, cursors, sounds, wallpaper and window frame",
        "Id": "org.mac4lin.desktop",
        "License": "GPL",
        "Name": "Mac4Lin (Leopard)",
        "Version": "1.0"
    },
    "X-Plasma-APIVersion": "2",
    "X-Plasma-MainScript": "defaults"
}
"""


def lnf_defaults():
    return f"""[kdeglobals][KDE]
widgetStyle=kvantum

[kdeglobals][General]
ColorScheme=SnowLeopard

[kdeglobals][Icons]
Theme=Mac4Lin

[plasmarc][Theme]
name=SnowLeopard

[Wallpaper]
Image=Mac4LinAurora

[kcminputrc][Mouse]
cursorTheme=Mac4Lin-Cursors

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae
theme=__aurorae__svg__Mac4Lin

[ksplashrc][KSplash]
Theme={LNF_ID}
"""


def build_lnf(wall, shot):
    base = os.path.join(OUT, f"plasma/look-and-feel/{LNF_ID}")
    for rel, content in (("metadata.json", LNF_META), ("contents/defaults", lnf_defaults()),
                         ("contents/layouts/org.kde.plasma.desktop-layout.js", X.LAYOUT_JS),
                         ("contents/splash/Splash.qml", X.SPLASH_QML)):
        p = os.path.join(base, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content)
    prev = os.path.join(base, "contents/previews")
    os.makedirs(prev, exist_ok=True)
    for name, size in (("preview.png", (640, 400)), ("fullscreenpreview.jpg", (1920, 1200))):
        img = wall.resize(size, Image.LANCZOS).convert("RGBA")
        s = shot.convert("RGBA")
        k = size[0] / 640 * 1.4
        s = s.resize((int(s.width * k), int(s.height * k)), Image.LANCZOS)
        img.alpha_composite(s, (int(size[0] * 0.08), int(size[1] * 0.12)))
        img.convert("RGB").save(os.path.join(prev, name), quality=92)
    Image.new("RGB", (640, 360), (0xCF, 0xCF, 0xCF)).save(os.path.join(prev, "splash.png"))


def main():
    if not os.path.exists(ZIP):
        sys.exit(f"missing {ZIP}\n"
                 "Download Mac4Lin_Install_v1.0.zip from https://sourceforge.net/projects/mac4lin/files/ "
                 "and put it in vendor/.")
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    with zipfile.ZipFile(ZIP) as zf:
        build_icons(zf)
        build_cursors(zf)
        build_sounds(zf)
        build_fonts(zf)
        wall = build_wallpapers(zf)
        title_bottom = build_decoration(zf)
        build_kvantum(title_bottom)
        shot = emerald_images(zf)["theme.screenshot.png"]
        build_lnf(wall, shot)
    print("built into", OUT, "| toolbar continues from", title_bottom)


if __name__ == "__main__":
    main()
