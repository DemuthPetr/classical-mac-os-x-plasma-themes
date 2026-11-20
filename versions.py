#!/usr/bin/env python3
"""Build a Plasma 6 global theme for each Mac OS X release from 10.0 Cheetah to 10.9 Mavericks.

Leopard (10.5) is the Mac4Lin theme and Snow Leopard (10.6) the original theme of this project;
this script adds the other eight. Colours were sampled from period screenshots; every texture and
wallpaper is generated here. Icons, cursors, sounds and Lucida Grande come from the Mac4Lin install.

    python3 versions.py            # all versions
    python3 versions.py tiger lion # just these
"""
import base64
import copy
import io
import os
import random
import shutil
import sys

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import palette as P  # noqa: E402
import kvantum_gen  # noqa: E402
import aurorae_gen  # noqa: E402
import plasma_gen  # noqa: E402
import extras_gen as X  # noqa: E402
import wallpapers_gen as WP  # noqa: E402
import build as SL  # noqa: E402

OUT = os.path.join(HERE, "build-versions")

# ---------------------------------------------------------------- textures


def _uri(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _avg(img):
    small = img.convert("RGB").resize((1, 1), Image.BOX)
    return "#{:02X}{:02X}{:02X}".format(*small.getpixel((0, 0)))


def pinstripe(rows, w, h):
    """Horizontal pinstripes repeating the grey levels in `rows`."""
    img = Image.new("RGB", (w, h))
    for yy in range(h):
        v = rows[yy % len(rows)]
        for xx in range(w):
            img.putpixel((xx, yy), (v, v, v))
    return img


def brushed(base, spread, w, h, seed, highlight=0):
    """Brushed aluminium: per-row brightness plus fine noise smeared horizontally (seamless in x)."""
    rnd = random.Random(seed)
    img = Image.new("L", (w * 3, h))
    px = img.load()
    rows = [rnd.gauss(0, spread) for _ in range(h)]
    for yy in range(h):
        for xx in range(w):
            v = base + rows[yy] + rnd.gauss(0, spread * 0.8)
            if highlight:
                v += highlight * max(0.0, 1 - yy / (h * 0.35))
            v = max(0, min(255, int(v)))
            for k in range(3):
                px[xx + k * w, yy] = v
    img = img.filter(ImageFilter.BoxBlur(0)).resize((w * 3 // 6, h), Image.BOX).resize((w * 3, h), Image.BILINEAR)
    return img.crop((w, 0, 2 * w, h)).convert("RGB")


def tile(img):
    return (_uri(img), img.width, img.height, _avg(img))


# ---------------------------------------------------------------- per-version specs

AQUA_EARLY_SEL = dict(LIST_SEL=[(0, "#5E98EE"), (1, "#2F6CD6")], LIST_SEL_TOP="#4F87DE",
                      MENU_SEL=[(0, "#5B8FF2"), (1, "#1E5FDB")], MENU_SEL_TOP="#4E7FE6", SELECTION="#3A74D8")
LION_BUTTONS = dict(
    WHITE_GLOSS=("#A8A8A8", "#8C8C8C", [(0, "#FFFFFF"), (1, "#F0F0F0")]),
    WHITE_HOVER=("#999999", "#7E7E7E", [(0, "#FFFFFF"), (1, "#F4F4F4")]),
    BLUE_GLOSS=("#4F7CC0", "#3460A6", [(0, "#A9CDF6"), (0.5, "#7DB3F0"), (1, "#5D9BEA")]),
    BLUE_PRESSED=("#3D669F", "#274C85", [(0, "#8BB4E8"), (1, "#4C86D8")]),
)

VERSIONS = {
    "cheetah": dict(
        name="Mac OS X 10.0 Cheetah", version="10.0",
        pal=dict(WINDOW_BG="#EEEEEE", TITLE_TEXT="#1A1A1A", TITLE_TEXT_INACTIVE="#7F7F7F",
                 TOOLBAR_LINE="#9C9C9C", TITLE_BOTTOM="#EBEBEB", TITLE_INACTIVE_BOTTOM="#F3F3F3",
                 **AQUA_EARLY_SEL),
        title=("pinstripe", [252, 243, 232, 242]), window=("pinstripe", [246, 238, 233, 238]),
        style=dict(toolbar="textured", scroll="jelly", menubar="pinstripe", dock="flat-pinstripe",
                   indicator="triangle"),
        wall=("aqua", dict(top=(22, 64, 160), bottom=(84, 136, 225), swoosh=(170, 200, 255), seed=100)),
    ),
    "puma": dict(
        name="Mac OS X 10.1 Puma", version="10.1",
        pal=dict(WINDOW_BG="#EFEFEF", TITLE_TEXT="#1A1A1A", TITLE_TEXT_INACTIVE="#7F7F7F",
                 TOOLBAR_LINE="#A0A0A0", TITLE_BOTTOM="#EDEDED", TITLE_INACTIVE_BOTTOM="#F4F4F4",
                 **AQUA_EARLY_SEL),
        title=("pinstripe", [252, 245, 236, 245]), window=("pinstripe", [247, 240, 235, 240]),
        style=dict(toolbar="textured", scroll="jelly", menubar="pinstripe", dock="flat-pinstripe",
                   indicator="triangle"),
        wall=("aqua", dict(top=(26, 70, 170), bottom=(96, 146, 232), swoosh=(180, 210, 255), seed=101)),
    ),
    "jaguar": dict(
        name="Mac OS X 10.2 Jaguar", version="10.2",
        pal=dict(WINDOW_BG="#F1F1F1", TITLE_TEXT="#1E1E1E", TITLE_TEXT_INACTIVE="#858585",
                 TOOLBAR_LINE="#A6A6A6", TITLE_BOTTOM="#EFEFEF", TITLE_INACTIVE_BOTTOM="#F5F5F5",
                 **AQUA_EARLY_SEL),
        title=("pinstripe", [251, 247, 239, 246]), window=("pinstripe", [248, 243, 238, 243]),
        style=dict(toolbar="textured", scroll="jelly", menubar="pinstripe", dock="flat-pinstripe",
                   indicator="triangle"),
        wall=("aqua", dict(top=(24, 70, 168), bottom=(64, 120, 210), swoosh=(150, 190, 250), seed=102, lines=7)),
    ),
    "panther": dict(
        name="Mac OS X 10.3 Panther", version="10.3",
        pal=dict(WINDOW_BG="#D4D4D4", TITLE_TEXT="#1C1C1C", TITLE_TEXT_INACTIVE="#6E6E6E",
                 TOOLBAR_LINE="#00000040", TITLE_BOTTOM="#D4D4D4", TITLE_INACTIVE_BOTTOM="#DEDEDE",
                 **AQUA_EARLY_SEL),
        title=("metal", dict(base=212, spread=5, highlight=22)), window=("metal", dict(base=212, spread=5)),
        style=dict(toolbar="textured", scroll="jelly", menubar="gloss", dock="flat", indicator="triangle"),
        wall=("aqua", dict(top=(30, 80, 180), bottom=(70, 125, 215), swoosh=(160, 205, 255), seed=103, lines=4)),
    ),
    "tiger": dict(
        name="Mac OS X 10.4 Tiger", version="10.4",
        pal=dict(WINDOW_BG="#D0D0D0", TITLE_TEXT="#1C1C1C", TITLE_TEXT_INACTIVE="#6E6E6E",
                 TOOLBAR_LINE="#00000038", TITLE_BOTTOM="#CFCFCF", TITLE_INACTIVE_BOTTOM="#DADADA",
                 **AQUA_EARLY_SEL),
        title=("metal", dict(base=208, spread=3.5, highlight=26)), window=("metal", dict(base=208, spread=3.5)),
        style=dict(toolbar="textured", scroll="jelly", menubar="gloss", dock="flat", indicator="triangle"),
        wall=("aqua", dict(top=(40, 96, 196), bottom=(110, 160, 230), swoosh=(190, 220, 255), seed=104)),
    ),
    "lion": dict(
        name="Mac OS X 10.7 Lion", version="10.7",
        pal=dict(TITLE_TOP="#E8E8E8", TITLE_BOTTOM="#D0D0D0", TOOLBAR_BOTTOM="#ABABAB", TOOLBAR_LINE="#5E5E5E",
                 TITLE_INACTIVE_TOP="#F5F5F5", TITLE_INACTIVE_BOTTOM="#E6E6E6", **LION_BUTTONS),
        style=dict(toolbar="unified", scroll="overlay", menubar="lion", dock="shelf", indicator="glow"),
        wall=("galaxy", dict(base_top=(14, 18, 40), base_bottom=(30, 40, 80), arm=(150, 160, 230),
                             core=(255, 228, 190), seed=107, tilt=-0.42)),
    ),
    "mountainlion": dict(
        name="OS X 10.8 Mountain Lion", version="10.8",
        pal=dict(TITLE_TOP="#EAEAEA", TITLE_BOTTOM="#D2D2D2", TOOLBAR_BOTTOM="#AEAEAE", TOOLBAR_LINE="#626262",
                 TITLE_INACTIVE_TOP="#F6F6F6", TITLE_INACTIVE_BOTTOM="#E8E8E8", **LION_BUTTONS),
        style=dict(toolbar="unified", scroll="overlay", menubar="lion", dock="shelf", indicator="glow"),
        wall=("galaxy", dict(base_top=(8, 22, 38), base_bottom=(24, 54, 80), arm=(120, 175, 215),
                             core=(255, 238, 205), seed=108, tilt=-0.62)),
    ),
    "mavericks": dict(
        name="OS X 10.9 Mavericks", version="10.9",
        pal=dict(TITLE_TOP="#ECECEC", TITLE_BOTTOM="#D6D6D6", TOOLBAR_BOTTOM="#B5B5B5", TOOLBAR_LINE="#6B6B6B",
                 TITLE_INACTIVE_TOP="#F6F6F6", TITLE_INACTIVE_BOTTOM="#EAEAEA", **LION_BUTTONS),
        style=dict(toolbar="unified", scroll="overlay", menubar="mavericks", dock="mavericks", indicator="glow"),
        wall=("wave", dict(seed=109)),
    ),
}


def key_name(key):
    return "MacOSX-" + key.capitalize().replace("lion", "Lion")


# ---------------------------------------------------------------- build one version

def _textures(spec):
    out = {}
    for which, size in (("title", (8, aurorae_gen.TITLE_H - 1)), ("window", (256, 256))):
        kind = spec.get(which)
        if not kind:
            continue
        if kind[0] == "pinstripe":
            w = 8 if which == "window" else size[0]
            h = len(kind[1]) * (1 if which == "window" else 1)
            img = pinstripe(kind[1], w, size[1] if which == "title" else h)
        else:
            p = kind[1]
            img = brushed(p["base"], p["spread"], 256, size[1], seed=len(which), highlight=p.get("highlight", 0))
        out[which] = tile(img)
    return out


def write(rel, content, mode="w"):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode) as f:
        f.write(content)
    return path


def build_version(key):
    spec = VERSIONS[key]
    tid = key_name(key)
    lnf = f"org.macosx.{key}.desktop"
    saved_pal = {k: copy.deepcopy(getattr(P, k)) for k in spec["pal"]}
    saved_style = dict(P.STYLE)
    try:
        for k, v in spec["pal"].items():
            setattr(P, k, v)
        tex = _textures(spec)
        P.STYLE.clear()
        P.STYLE.update(spec["style"])
        if "title" in tex:
            P.STYLE["title_tile"] = tex["title"]
        if "window" in tex:
            P.STYLE["window_tile"] = tex["window"]
            P.WINDOW_BG = tex["window"][3]

        # Kvantum
        cfg = kvantum_gen.KVCONFIG.replace("comment=Mac OS X 10.6 Snow Leopard Aqua controls",
                                           f"comment={spec['name']} Aqua controls")
        if spec["style"].get("scroll") == "overlay":
            cfg = cfg.replace("scroll_width=15", "scroll_width=11").replace(
                "transient_scrollbar=false", "transient_scrollbar=true\ntransient_groove=false")
        if "window" in tex:
            tw, th = tex["window"][1], tex["window"][2]
            cfg = cfg.replace("[Window]\ninterior=false\nframe=false",
                              f"[Window]\ninterior=true\ninterior.element=window\nframe=false\n"
                              f"interior.x.patternsize={tw}\ninterior.y.patternsize={th}")
            cfg = cfg.replace("[Toolbar]\ninherits=PanelButtonCommand\nframe=true\ninterior=true",
                              "[Toolbar]\ninherits=PanelButtonCommand\nframe=true\ninterior=true\n"
                              f"interior.x.patternsize={tw}\ninterior.y.patternsize={th}")
        cfg = cfg.replace("window.color=#EDEDED", f"window.color={P.WINDOW_BG}")
        write(f"Kvantum/{tid}/{tid}.svg", kvantum_gen.build_svg())
        write(f"Kvantum/{tid}/{tid}.kvconfig", cfg)

        # Window decoration
        for name, content in aurorae_gen.files().items():
            if name == "SnowLeopardrc":
                name = f"{tid}rc"
                content = (content.replace("ActiveTextColor=43,43,43", "ActiveTextColor=" + X.rgb(P.TITLE_TEXT))
                           .replace("InactiveTextColor=142,142,142", "InactiveTextColor=" + X.rgb(P.TITLE_TEXT_INACTIVE)))
            if name == "metadata.desktop":
                content = content.replace("Name=Snow Leopard", f"Name={spec['name']}").replace(
                    "X-KDE-PluginInfo-Name=SnowLeopard", f"X-KDE-PluginInfo-Name={tid}")
            write(f"aurorae/themes/{tid}/{name}", content)

        # Colours + Plasma style
        scheme = X.colors(spec["name"]).replace("ColorScheme=SnowLeopard", f"ColorScheme={tid}")
        if "window" in tex:
            # toolbars and headers that fill themselves should blend into the texture
            scheme = scheme.replace("BackgroundNormal=214,214,214", "BackgroundNormal=" + X.rgb(P.WINDOW_BG))
        write(f"color-schemes/{tid}.colors", scheme)
        for name, content in plasma_gen.files(scheme).items():
            if name == "metadata.json":
                content = content.replace('"Id": "SnowLeopard"', f'"Id": "{tid}"').replace(
                    '"Name": "Snow Leopard"', f'"Name": "{spec["name"]}"')
            write(f"plasma/desktoptheme/{tid}/{name}", content)

        # Wallpaper
        wp = os.path.join(OUT, f"wallpapers/{tid}/contents/images/3840x2160.jpg")
        os.makedirs(os.path.dirname(wp), exist_ok=True)
        kind, args = spec["wall"]
        wall = getattr(WP, kind)(wp, **args)
        write(f"wallpapers/{tid}/metadata.json", X.wallpaper_meta(tid, spec["name"]))
        wall.resize((400, 225), Image.LANCZOS).save(os.path.join(OUT, f"wallpapers/{tid}/contents/screenshot.jpg"))

        # Global theme
        base = f"plasma/look-and-feel/{lnf}"
        meta = X.LNF_META.replace(X.LNF_ID, lnf).replace('"Name": "Snow Leopard"', f'"Name": "{spec["name"]}"')
        meta = meta.replace("Mac OS X 10.6 Snow Leopard: unified grey windows, Aqua controls, menu bar and glass dock",
                            f"{spec['name']}: window frame, Aqua controls, menu bar, dock and wallpaper")
        write(f"{base}/metadata.json", meta)
        defaults = (X.lnf_defaults().replace("ColorScheme=SnowLeopard", f"ColorScheme={tid}")
                    .replace("Theme=oxygen", "Theme=Mac4Lin").replace("name=SnowLeopard", f"name={tid}")
                    .replace("Image=SnowLeopardAurora", f"Image={tid}")
                    .replace("cursorTheme=Oxygen_Black", "cursorTheme=Mac4Lin-Cursors")
                    .replace("__aurorae__svg__SnowLeopard", f"__aurorae__svg__{tid}")
                    .replace(f"Theme={X.LNF_ID}", f"Theme={lnf}"))
        write(f"{base}/contents/defaults", defaults)
        write(f"{base}/contents/layouts/org.kde.plasma.desktop-layout.js", X.LAYOUT_JS)
        write(f"{base}/contents/splash/Splash.qml", X.SPLASH_QML)
        prev = os.path.join(OUT, base, "contents/previews")
        os.makedirs(prev, exist_ok=True)
        SL.OUT = os.path.join(OUT, "_tmp_" + key)
        SL.render_preview(wall, os.path.join(prev, "preview.png"), 640, 360)
        SL.render_preview(wall, os.path.join(prev, "fullscreenpreview.jpg"), 1920, 1080)
        shutil.rmtree(SL.OUT, ignore_errors=True)
        Image.new("RGB", (640, 360), (0xCF, 0xCF, 0xCF)).save(os.path.join(prev, "splash.png"))
    finally:
        for k, v in saved_pal.items():
            setattr(P, k, v)
        P.STYLE.clear()
        P.STYLE.update(saved_style)
        P.WINDOW_BG = "#EDEDED"
    print("built", spec["name"], "->", tid)


def main(keys):
    keys = keys or list(VERSIONS)
    if not sys.argv[1:] and os.path.isdir(OUT):
        shutil.rmtree(OUT)
    for k in keys:
        build_version(k)


if __name__ == "__main__":
    main(sys.argv[1:])
