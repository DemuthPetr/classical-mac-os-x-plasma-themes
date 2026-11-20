#!/usr/bin/env python3
"""Generate the whole Snow Leopard theme into ./build (nothing is installed here)."""
import os
import shutil
import subprocess
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import palette as P  # noqa: E402
import kvantum_gen  # noqa: E402
import aurorae_gen  # noqa: E402
import plasma_gen  # noqa: E402
import extras_gen as X  # noqa: E402
from svgkit import Sheet, rrect_poly  # noqa: E402

OUT = os.path.join(HERE, "build")


def write(rel, content, mode="w"):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as f:
        f.write(content)
    return path


def preview_overlay(w, h):
    """Mock desktop (menu bar, two windows, dock) used for the theme picker thumbnails."""
    s = Sheet(width=w)
    k = h / 1080
    body = []
    # menu bar
    body.append(f'<rect width="{w}" height="{24 * k}" fill="#F4F4F4" fill-opacity="0.92"/>'
                f'<rect y="{23 * k}" width="{w}" height="{1 * k}" fill="#000" fill-opacity="0.35"/>')
    for i, label in enumerate(["Finder", "File", "Edit", "View", "Go", "Window", "Help"]):
        weight = "bold" if i == 0 else "normal"
        body.append(f'<text x="{(40 + i * 64) * k}" y="{17 * k}" font-family="Lucida Grande,DejaVu Sans" '
                    f'font-size="{13 * k}" font-weight="{weight}" fill="#111">{label}</text>')
    body.append(f'<text x="{w - 120 * k}" y="{17 * k}" font-family="DejaVu Sans" font-size="{13 * k}" fill="#111">Thu 9:41</text>')

    def window(x, y, ww, wh, title, active):
        x, y, ww, wh = x * k, y * k, ww * k, wh * k
        tb = (22 + 50) * k
        out = []
        for e in range(14, 0, -1):
            out.append(f'<rect x="{x - e * k}" y="{y - e * k + 8 * k}" width="{ww + 2 * e * k}" height="{wh + 2 * e * k - 6 * k}" '
                       f'rx="{(5 + e) * k}" fill="#000" fill-opacity="{0.035 if active else 0.02}"/>')
        g = s.lin([(0, P.TITLE_TOP), (0.3, P.TITLE_BOTTOM), (1, P.TOOLBAR_BOTTOM)] if active else
                  [(0, P.TITLE_INACTIVE_TOP), (1, "#D1D1D1")], 0, y, 0, y + tb)
        out.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{wh}" rx="{5 * k}" fill="{P.WINDOW_BG}" stroke="#000" stroke-opacity="0.4"/>')
        out.append(f'<path d="M{x},{y + tb} V{y + 5 * k} Q{x},{y} {x + 5 * k},{y} H{x + ww - 5 * k} Q{x + ww},{y} {x + ww},{y + 5 * k} V{y + tb} Z" fill="{g}"/>')
        out.append(f'<rect x="{x}" y="{y + tb}" width="{ww}" height="{1 * k}" fill="{P.TOOLBAR_LINE}"/>')
        out.append(f'<rect x="{x + 180 * k}" y="{y + tb + 1 * k}" width="{ww - 180 * k}" height="{wh - tb - 1 * k}" fill="#fff"/>')
        out.append(f'<rect x="{x}" y="{y + tb + 1 * k}" width="{180 * k}" height="{wh - tb - 1 * k}" fill="#E0E5EC"/>')
        for r in range(12):
            if r % 2:
                out.append(f'<rect x="{x + 180 * k}" y="{y + tb + (1 + r * 20) * k}" width="{ww - 180 * k}" height="{20 * k}" fill="{P.ALT_BASE}"/>')
        out.append(f'<rect x="{x + 180 * k}" y="{y + tb + 61 * k}" width="{ww - 180 * k}" height="{20 * k}" fill="{P.SELECTION}"/>')
        out.append(f'<text x="{x + ww / 2}" y="{y + 15 * k}" text-anchor="middle" font-family="DejaVu Sans" '
                   f'font-size="{13 * k}" fill="{P.TITLE_TEXT if active else P.TITLE_TEXT_INACTIVE}">{title}</text>')
        for i, cols in enumerate((P.TL_CLOSE, P.TL_MIN, P.TL_MAX) if active else (P.TL_OFF,) * 3):
            out.append(f'<g transform="translate({x + (8 + i * 21) * k},{y}) scale({k})">'
                       f'{aurorae_gen._light(s, 0, 0, cols, None)}</g>')
        # aqua scroller
        sx = x + ww - 15 * k
        out.append(f'<rect x="{sx}" y="{y + tb + 1 * k}" width="{15 * k}" height="{wh - tb - 1 * k}" fill="#E4E4E4"/>')
        jg = s.lin([(0, "#4F81CF"), (0.38, "#C3DDF9"), (0.5, "#9CC5F3"), (0.5, "#76AAEC"), (1, "#6E9CDD")], sx, 0, sx + 15 * k, 0)
        out.append(f'<rect x="{sx + 2 * k}" y="{y + tb + 20 * k}" width="{11 * k}" height="{120 * k}" rx="{5.5 * k}" fill="{jg}" stroke="#3D64A6" stroke-width="{k}"/>')
        return "".join(out)

    body.append(window(380, 300, 760, 500, "Documents", False))
    body.append(window(160, 140, 820, 560, "Macintosh HD", True))

    # dock shelf
    dw, dh = 560 * k, 64 * k
    dx, dy = (w - dw) / 2, h - dh
    top, front = dy + dh * 0.5, dy + dh - 5 * k
    g = s.lin([(0, "#F4F6FA"), (1, "#E4E8F0")], 0, top, 0, front)
    body.append(f'<path d="M{dx + 26 * k},{top} H{dx + dw - 26 * k} L{dx + dw},{front} H{dx} Z" fill="{g}" fill-opacity="0.75" stroke="#fff" stroke-opacity="0.7" stroke-width="{k}"/>')
    body.append(f'<rect x="{dx}" y="{front}" width="{dw}" height="{1.5 * k}" fill="#fff"/><rect x="{dx}" y="{front + 1.5 * k}" width="{dw}" height="{2.5 * k}" fill="#3C404C" fill-opacity="0.7"/>')
    icons = ["#4A90E2", "#E8A33A", "#2E2E2E", "#7FB24C", "#9A9A9A", "#C04A8A", "#5AA0C8"]
    for i, c in enumerate(icons):
        ix = dx + (40 + i * 72) * k
        body.append(f'<rect x="{ix}" y="{dy + 6 * k}" width="{48 * k}" height="{48 * k}" rx="{10 * k}" fill="{c}"/>'
                    f'<rect x="{ix + 4 * k}" y="{dy + 8 * k}" width="{40 * k}" height="{18 * k}" rx="{8 * k}" fill="#fff" fill-opacity="0.35"/>')
        if i in (0, 1, 2):
            body.append(f'<circle cx="{ix + 24 * k}" cy="{front - 2 * k}" r="{2.2 * k}" fill="#D8ECFF"/>')
    defs = "".join(s.defs)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<defs>{defs}</defs>{"".join(body)}</svg>')


def render_preview(wall, path, w, h):
    svg = write(f"_tmp/overlay_{w}.svg", preview_overlay(w, h))
    png = svg[:-4] + ".png"
    subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-o", png, svg], check=True)
    base = wall.resize((w, h), Image.LANCZOS).convert("RGBA")
    base.alpha_composite(Image.open(png).convert("RGBA"))
    base.convert("RGB").save(path, quality=92)


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    # Kvantum
    write("Kvantum/SnowLeopard/SnowLeopard.svg", kvantum_gen.build_svg())
    write("Kvantum/SnowLeopard/SnowLeopard.kvconfig", kvantum_gen.KVCONFIG)

    # Aurorae
    for name, content in aurorae_gen.files().items():
        write(f"aurorae/themes/SnowLeopard/{name}", content)

    # Colours
    scheme = X.colors()
    write("color-schemes/SnowLeopard.colors", scheme)

    # Plasma style
    for name, content in plasma_gen.files(scheme).items():
        write(f"plasma/desktoptheme/SnowLeopard/{name}", content)

    # Wallpapers
    for wid, (name, tint, clouds, ribbon, seed) in X.WALLPAPERS.items():
        wp = os.path.join(OUT, f"wallpapers/{wid}/contents/images/3840x2160.jpg")
        os.makedirs(os.path.dirname(wp), exist_ok=True)
        img = X.wallpaper(wp, seed=seed, tint=tint, cloud_cols=clouds, ribbon_cols=ribbon)
        write(f"wallpapers/{wid}/metadata.json", X.wallpaper_meta(wid, name))
        img.resize((400, 225), Image.LANCZOS).save(os.path.join(OUT, f"wallpapers/{wid}/contents/screenshot.jpg"), quality=90)
        if wid == "SnowLeopardAurora":
            wall = img

    # Global theme
    lnf = f"plasma/look-and-feel/{X.LNF_ID}"
    write(f"{lnf}/metadata.json", X.LNF_META)
    write(f"{lnf}/contents/defaults", X.lnf_defaults())
    write(f"{lnf}/contents/layouts/org.kde.plasma.desktop-layout.js", X.LAYOUT_JS)
    write(f"{lnf}/contents/splash/Splash.qml", X.SPLASH_QML)
    write("applications/snowleopard-trash.desktop", X.TRASH_DESKTOP)
    prev = os.path.join(OUT, lnf, "contents/previews")
    os.makedirs(prev, exist_ok=True)
    render_preview(wall, os.path.join(prev, "preview.png"), 640, 360)
    render_preview(wall, os.path.join(prev, "fullscreenpreview.jpg"), 1920, 1080)
    Image.new("RGB", (640, 360), (0xCF, 0xCF, 0xCF)).save(os.path.join(prev, "splash.png"))
    shutil.rmtree(os.path.join(OUT, "_tmp"))
    print("built into", OUT)


if __name__ == "__main__":
    main()
