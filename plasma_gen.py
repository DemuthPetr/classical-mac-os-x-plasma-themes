"""Plasma style: translucent white menu bar on top, Leopard glass-shelf dock at the bottom."""
import json
from svgkit import Sheet, rrect_poly
import palette as P

MENUBAR_H = 24
DOCK_H = 64
SHELF_SLANT = 26


def _hints(s, prefix, top, right, bottom, left):
    for side, (w, h) in (("top", (4, top)), ("bottom", (4, bottom)), ("left", (left, 4)), ("right", (right, 4))):
        x, y = s.place(max(w, 1), max(h, 1))
        s.raw(f"{prefix}hint-{side}-margin", (x, y, x + w, y + h), "")


def _menubar_shapes(s, x, y, w, h):
    kind = P.STYLE.get("menubar", "translucent")
    if kind == "pinstripe":
        # 10.0-10.2: opaque white with a faint grey line every fourth row
        out = [(rrect_poly(x, y, w, h, 0), "#FBFBFB")]
        out += [(rrect_poly(x, y + r, w, 1, 0), "#E9E9E9") for r in range(1, h - 1, 4)]
        return out + [(rrect_poly(x, y + h - 1, w, 1, 0), "#5E5E5E")]
    if kind == "gloss":
        # 10.3-10.4: solid glossy white
        return [(rrect_poly(x, y, w, h, 0), s.lin([(0, "#FFFFFF"), (0.5, "#F7F7F7"), (1, "#E9E9E9")], 0, y, 0, y + h)),
                (rrect_poly(x, y + h - 1, w, 1, 0), "#7A7A7A")]
    if kind == "lion":
        return [(rrect_poly(x, y, w, h, 0), s.lin([(0, "#F4F4F4"), (1, "#D6D6D6")], 0, y, 0, y + h)),
                (rrect_poly(x, y, w, 1, 0), "#FFFFFFD0"),
                (rrect_poly(x, y + h - 1, w, 1, 0), "#8A8A8A")]
    if kind == "mavericks":
        return [(rrect_poly(x, y, w, h, 0), s.lin([(0, "#FAFAFACC"), (1, "#E6E6E6B8")], 0, y, 0, y + h)),
                (rrect_poly(x, y + h - 1, w, 1, 0), "#0000004D")]
    return [
        (rrect_poly(x, y, w, h, 0), s.lin([(0, "#FCFCFCE6"), (1, "#E2E2E2DC")], 0, y, 0, y + h)),
        (rrect_poly(x, y, w, 1, 0), "#FFFFFFC0"),
        (rrect_poly(x, y + h - 1, w, 1, 0), "#00000066"),
    ]


def _menubar(s, prefix):
    w, h = 60, MENUBAR_H
    x, y = s.place(w, h)
    shapes = _menubar_shapes(s, x, y, w, h)
    s.ninepatch(prefix.rstrip("-") or "center", x, y, w, h, 1, shapes, frame=False,
                interior_name=f"{prefix}center")
    # frame pieces with explicit names (prefix-top etc.)
    xs, ys = [x, x + 1, x + w - 1, x + w], [y, y + 1, y + h - 1, y + h]
    for (i, j), name in {(0, 0): "topleft", (1, 0): "top", (2, 0): "topright", (0, 1): "left", (2, 1): "right",
                         (0, 2): "bottomleft", (1, 2): "bottom", (2, 2): "bottomright"}.items():
        s.group(f"{prefix}{name}", (xs[i], ys[j], xs[i + 1], ys[j + 1]), shapes)
    _hints(s, prefix, 1, 6, 2, 6)


def _dock(s, prefix):
    w, h, side = 400, DOCK_H, 30
    x, y = s.place(w, h)
    shelf_top = y + h * 0.5
    front = y + h - 5
    sl = SHELF_SLANT
    trap = [(x + sl, shelf_top), (x + w - sl, shelf_top), (x + w - 1, front), (x + 1, front)]
    kind = P.STYLE.get("dock", "shelf")
    top_rows = 1
    if kind in ("flat", "flat-pinstripe"):
        # 10.0-10.4: a flat translucent slab with rounded top corners
        r = 10
        top_rows = r + 2
        shapes = [(rrect_poly(x, y + 1, w, h - 1, r, corners=(1, 1, 0, 0)), "#00000059"),
                  (rrect_poly(x + 1, y + 2, w - 2, h - 2, r - 1, corners=(1, 1, 0, 0)), "#FFFFFFD8"),
                  (rrect_poly(x + 2, y + 3, w - 4, h - 3, r - 2, corners=(1, 1, 0, 0)),
                   s.lin([(0, "#F4F4F4C0"), (1, "#E2E2E2B0")], 0, y, 0, y + h))]
        if kind == "flat-pinstripe":
            shapes += [(rrect_poly(x + 2, y + 3 + k, w - 4, 1, 0), "#9A9A9A30") for k in range(r, h - 3, 4)]
    elif kind == "mavericks":
        # 10.9: shallow frosted-glass shelf without the bright lip
        top = y + h * 0.42
        sl = 14
        shapes = [([(x + sl, top), (x + w - sl, top), (x + w - 1, y + h), (x + 1, y + h)],
                   s.lin([(0, "#9A9DA4C8"), (1, "#D8DADED8")], 0, top, 0, y + h)),
                  ([(x + sl, top), (x + w - sl, top), (x + w - sl + 0.5, top + 1), (x + sl - 0.5, top + 1)],
                   "#FFFFFFB0"),
                  ([(x + sl, top), (x + sl + 1, top), (x + 2, y + h), (x + 1, y + h)], "#FFFFFF80"),
                  ([(x + w - sl - 1, top), (x + w - sl, top), (x + w - 1, y + h), (x + w - 2, y + h)], "#FFFFFF80")]
    else:
        shapes = None
    shapes = shapes or [
        (trap, s.lin([(0, "#F4F6FA70"), (0.6, "#E4E8F0A8"), (1, "#F2F4F8D0")], 0, shelf_top, 0, front)),
        ([(x + sl, shelf_top), (x + w - sl, shelf_top), (x + w - sl + 0.6, shelf_top + 1),
          (x + sl - 0.6, shelf_top + 1)], "#FFFFFFA0"),
        # slanted rims
        ([(x + sl, shelf_top), (x + sl + 1.2, shelf_top), (x + 2.2, front), (x + 1, front)], "#FFFFFFB0"),
        ([(x + w - sl - 1.2, shelf_top), (x + w - sl, shelf_top), (x + w - 1, front), (x + w - 2.2, front)],
         "#FFFFFFB0"),
        # bright front lip and its dark thickness
        (rrect_poly(x + 1, front, w - 2, 1.5, 0), "#FFFFFFF2"),
        (rrect_poly(x + 1, front + 1.5, w - 2, 2.5, 0), "#3C404CB0"),
        (rrect_poly(x + 2, front + 4, w - 4, 1, 0), "#00000040"),
    ]
    xs, ys = [x, x + side, x + w - side, x + w], [y, y + top_rows, y + h - 1, y + h]
    for (i, j), name in {(1, 1): "center", (0, 0): "topleft", (1, 0): "top", (2, 0): "topright", (0, 1): "left",
                         (2, 1): "right", (0, 2): "bottomleft", (1, 2): "bottom", (2, 2): "bottomright"}.items():
        s.group(f"{prefix}{name}", (xs[i], ys[j], xs[i + 1], ys[j + 1]), shapes)
    _hints(s, prefix, 4 if kind.startswith("flat") else 2, 14, 7, 14)
    # Plasma derives the panel's input region from its mask. Without an explicit opaque mask the
    # see-through upper half of the dock would ignore clicks on the icons standing on the shelf.
    mask = [(rrect_poly(x, y, w, h, 0), "#000000")]
    for mp in (f"mask-{prefix}", f"{prefix}mask-"):
        for (i, j), name in {(1, 1): "center", (0, 0): "topleft", (1, 0): "top", (2, 0): "topright",
                             (0, 1): "left", (2, 1): "right", (0, 2): "bottomleft", (1, 2): "bottom",
                             (2, 2): "bottomright"}.items():
            s.group(f"{mp}{name}", (xs[i], ys[j], xs[i + 1], ys[j + 1]), mask)


def panel_background():
    s = Sheet(width=1200)
    for p in ("", "north-", "west-", "east-"):
        _menubar(s, p)
    _dock(s, "south-")
    x, y = s.place(4, 4)
    s.raw("hint-stretch-borders", (x, y, x + 4, y + 4), "")
    return s.to_svg()


def _popup(s, prefix, fill, radius=5, border="#00000040", shadow=True):
    m = 6
    w = h = 60
    x, y = s.place(w + 40, h + 40)
    x, y = x + 20, y + 20
    shapes = [(rrect_poly(x, y, w, h, radius), border), (rrect_poly(x + 1, y + 1, w - 2, h - 2, radius - 1), fill)]
    s.ninepatch(prefix.rstrip("-") if prefix else "frame", x, y, w, h, m, shapes, interior_name=f"{prefix}center",
                frame=False)
    xs, ys = [x, x + m, x + w - m, x + w], [y, y + m, y + h - m, y + h]
    for (i, j), name in {(0, 0): "topleft", (1, 0): "top", (2, 0): "topright", (0, 1): "left", (2, 1): "right",
                         (0, 2): "bottomleft", (1, 2): "bottom", (2, 2): "bottomright"}.items():
        s.group(f"{prefix}{name}", (xs[i], ys[j], xs[i + 1], ys[j + 1]), shapes)
    if shadow:
        d = 18
        sx, sy, sw, sh = x - d, y - d, w + 2 * d, h + 2 * d
        layers = []
        for k in range(14):
            e = 14 - k
            layers.append((rrect_poly(x - e, y - e + 5, w + 2 * e, h + 2 * e - 3, radius + e), "#00000009"))
        xs, ys = [sx, sx + d, sx + sw - d, sx + sw], [sy, sy + d, sy + sh - d, sy + sh]
        for (i, j), name in {(0, 0): "topleft", (1, 0): "top", (2, 0): "topright", (0, 1): "left",
                             (2, 1): "right", (0, 2): "bottomleft", (1, 2): "bottom",
                             (2, 2): "bottomright"}.items():
            s.group(f"{prefix}shadow-{name}", (xs[i], ys[j], xs[i + 1], ys[j + 1]), layers)


def dialog_background(fill="#FFFFFFF2"):
    s = Sheet(width=600)
    _popup(s, "", fill)
    x, y = s.place(4, 4)
    s.raw("hint-stretch-borders", (x, y, x + 4, y + 4), "")
    return s.to_svg()


def tasks():
    s = Sheet(width=900)
    w = h = 56
    side, bot = 22, 9

    def frame(prefix, dot, glow, hover):
        x, y = s.place(w, h)
        shapes = []
        if hover:
            shapes.append((rrect_poly(x + 2, y + 2, w - 4, h - 6, 8), "#FFFFFF2A"))
        if dot and P.STYLE.get("indicator") == "triangle":
            # 10.0-10.4: a small black triangle under running apps
            cx = x + w / 2
            col = "#E07000" if prefix == "attention" else "#000000D0"
            shapes.append(([(cx - 4, y + h - 1), (cx + 4, y + h - 1), (cx, y + h - 5)], col))
        elif dot:
            cx, cy = x + w / 2, y + h - 4.5
            shapes.append((rrect_poly(cx - 5, cy - 2.5, 10, 5, 2.5), glow))
            shapes.append((rrect_poly(cx - 2.2, cy - 2.2, 4.4, 4.4, 2.2), dot))
        xs, ys = [x, x + side, x + w - side, x + w], [y, y + 2, y + h - bot, y + h]
        for (i, j), name in {(1, 1): "center", (0, 0): "topleft", (1, 0): "top", (2, 0): "topright",
                             (0, 1): "left", (2, 1): "right", (0, 2): "bottomleft", (1, 2): "bottom",
                             (2, 2): "bottomright"}.items():
            s.group(f"{prefix}-{name}", (xs[i], ys[j], xs[i + 1], ys[j + 1]), shapes)
        # contents margins: keep icons big and close together despite the wide corner slices
        _hints(s, f"{prefix}-", 1, 3, 6, 3)

    frame("normal", "#D8ECFF", "#7FB8FF60", False)
    frame("focus", "#FFFFFF", "#9FD0FFA0", False)
    frame("hover", "#E8F4FF", "#9FD0FF70", True)
    frame("minimized", "#C8D8E8", "#7FB8FF40", False)
    frame("attention", "#FFB040", "#FF8A0080", False)
    x, y = s.place(4, 4)
    s.raw("hint-stretch-borders", (x, y, x + 4, y + 4), "")
    return s.to_svg()


METADATA = json.dumps({
    "KPlugin": {
        "Authors": [{"Name": "Snow Leopard Plasma"}],
        "Category": "",
        "Description": "Mac OS X 10.6 Snow Leopard: translucent menu bar and glass dock shelf",
        "EnabledByDefault": True,
        "Id": "SnowLeopard",
        "License": "GPL",
        "Name": "Snow Leopard",
        "Version": "1.0",
    },
    "X-Plasma-API": "5.0",
}, indent=4)

# Blur and contrast follow the panel mask, which for the dock is the whole rectangle; keep them off
# so the space around the shelf stays clear.
PLASMARC = """[ContrastEffect]
enabled=false

[BlurBehindEffect]
enabled=false

[AdaptiveTransparency]
enabled=false
"""


def files(colors_text):
    dialog = dialog_background()
    return {
        "metadata.json": METADATA,
        "plasmarc": PLASMARC,
        "colors": colors_text,
        "widgets/panel-background.svg": panel_background(),
        "widgets/tasks.svg": tasks(),
        "widgets/tooltip.svg": dialog_background("#FFFFFFF5"),
        "widgets/background.svg": dialog_background("#F4F4F4E8"),
        "dialogs/background.svg": dialog,
    }
