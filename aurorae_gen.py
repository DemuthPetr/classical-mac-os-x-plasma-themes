"""Aurorae window decoration: unified grey title bar, traffic lights, soft Mac shadow."""
from svgkit import Sheet, rrect_poly, fmt
import palette as P

PAD_T, PAD_B, PAD_L, PAD_R = 14, 28, 22, 22
TITLE_H = 22
RADIUS = 5
BTN_W, BTN_H = 20, 22


def _shadow(x, y, w, h, strength):
    """Stacked translucent rounded rects approximate a Gaussian drop shadow."""
    out = []
    n = 20
    for k in range(n):
        e = n - k
        a = int(round(255 * strength * (0.25 + 0.75 * k / n) / n * 2.2))
        out.append((rrect_poly(x - e, y - e + 7, w + 2 * e, h + 2 * e - 4, RADIUS + e), f"#000000{min(a, 255):02X}"))
    # tight contact shadow
    out.append((rrect_poly(x - 1, y, w + 2, h + 2, RADIUS + 1), f"#000000{int(70 * strength):02X}"))
    return out


def _frame(s, prefix, x, y, active):
    L, R = PAD_L + RADIUS + 1, PAD_R + RADIUS + 1
    T, B = PAD_T + TITLE_H, PAD_B + RADIUS + 1
    W, H = L + 60 + R, T + 60 + B
    wx, wy, ww, wh = x + PAD_L, y + PAD_T, W - PAD_L - PAD_R, H - PAD_T - PAD_B
    top, bot = (P.TITLE_TOP, P.TITLE_BOTTOM) if active else (P.TITLE_INACTIVE_TOP, P.TITLE_INACTIVE_BOTTOM)
    shapes = _shadow(wx, wy, ww, wh, 1.0 if active else 0.55)
    tile = P.STYLE.get("title_tile")
    if tile:
        # pinstripes / brushed metal: the rounded corners get the texture's average colour,
        # the straight part the texture itself (uniform along x, so stretching is harmless)
        uri, _tw, _th, avg = tile
        bot = avg
        title = [(rrect_poly(wx + 1, wy + 1, ww - 2, TITLE_H - 1, RADIUS - 1, corners=(1, 1, 0, 0)), avg),
                 (None, {"image": uri, "rect": (wx + RADIUS, wy + 1, wx + ww - RADIUS, wy + TITLE_H)})]
        if not active:
            title.append((rrect_poly(wx + 1, wy + 1, ww - 2, TITLE_H - 1, RADIUS - 1, corners=(1, 1, 0, 0)),
                          "#FFFFFF66"))
    else:
        title = [(rrect_poly(wx + 1, wy + 1, ww - 2, TITLE_H - 1, RADIUS - 1, corners=(1, 1, 0, 0)),
                  s.lin([(0, top), (1, bot)], 0, wy + 1, 0, wy + TITLE_H))]
    shapes += [
        (rrect_poly(wx, wy, ww, wh, RADIUS, corners=(1, 1, 0, 0)), "#00000070" if active else "#00000045"),
        # Hidden under the client, except for the half-pixel row fractional scaling leaves below the
        # title: painting it in the title's bottom colour keeps title and toolbar seamless.
        (rrect_poly(wx + 1, wy + 1, ww - 2, wh - 2, RADIUS - 1, corners=(1, 1, 0, 0)), bot),
        *title,
        (rrect_poly(wx + RADIUS, wy + 1, ww - 2 * RADIUS, 1, 0), "#FFFFFFB0"),
    ]
    s.ninepatch(prefix, x, y, W, H, (T, R, B, L), shapes, interior_name=f"{prefix}-center")
    return W, H


def decoration_svg():
    s = Sheet(width=900)
    x, y = s.place(200, 200)
    _frame(s, "decoration", x, y, True)
    x, y = s.place(200, 200)
    _frame(s, "decoration-inactive", x, y, False)
    for name, (top, bot) in (("decoration-maximized", (P.TITLE_TOP, P.TITLE_BOTTOM)),
                             ("decoration-maximized-inactive", (P.TITLE_INACTIVE_TOP, P.TITLE_INACTIVE_BOTTOM))):
        x, y = s.place(60, TITLE_H)
        tile = P.STYLE.get("title_tile")
        fill = ((None, {"image": tile[0], "rect": (x, y, x + 60, y + TITLE_H)}) if tile else
                (rrect_poly(x, y, 60, TITLE_H, 0), s.lin([(0, top), (1, bot)], 0, y, 0, y + TITLE_H)))
        s.group(f"{name}-center", (x, y, x + 60, y + TITLE_H), [
            fill,
            (rrect_poly(x, y, 60, 1, 0), "#FFFFFFB0")])
    # tell KSvg to stretch rather than tile the borders
    x, y = s.place(4, 4)
    s.raw("hint-stretch-borders", (x, y, x + 4, y + 4), "")
    return s.to_svg()


def _light(s, x, y, colors, glyph):
    rim, base_top, base_bot, glow, gcol = colors
    cx, cy, r = x + BTN_W / 2, y + BTN_H / 2 + 0.5, 6.8
    rimg = s.lin([(0, rim), (1, base_top)], 0, cy - r, 0, cy + r)
    body = s.rad([(0, glow), (0.45, base_bot), (1, base_top)], cx, cy + r * 0.85, r * 1.35, sx=1.0, sy=0.9)
    gloss = s.lin([(0, "#FFFFFFF0"), (1, "#FFFFFF10")], 0, cy - r + 1, 0, cy)
    svg = (f'<circle cx="{fmt(cx)}" cy="{fmt(cy + 0.6)}" r="{fmt(r + 0.4)}" fill="#FFFFFF" fill-opacity="0.55"/>'
           f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}" fill="{rimg}"/>'
           f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r - 0.9)}" fill="{body}"/>'
           f'<ellipse cx="{fmt(cx)}" cy="{fmt(cy - r * 0.45)}" rx="{fmt(r * 0.62)}" ry="{fmt(r * 0.4)}" fill="{gloss}"/>')
    if glyph:
        g = 2.6
        if glyph == "close":
            d = f"M{fmt(cx - g)},{fmt(cy - g)} L{fmt(cx + g)},{fmt(cy + g)} M{fmt(cx + g)},{fmt(cy - g)} L{fmt(cx - g)},{fmt(cy + g)}"
        elif glyph == "min":
            d = f"M{fmt(cx - g - 0.6)},{fmt(cy)} L{fmt(cx + g + 0.6)},{fmt(cy)}"
        else:
            d = f"M{fmt(cx - g - 0.4)},{fmt(cy)} L{fmt(cx + g + 0.4)},{fmt(cy)} M{fmt(cx)},{fmt(cy - g - 0.4)} L{fmt(cx)},{fmt(cy + g + 0.4)}"
        svg += f'<path d="{d}" stroke="{gcol}" stroke-opacity="0.85" stroke-width="1.6" stroke-linecap="round"/>'
    return svg


def _darker(colors):
    rim, a, b, glow, g = colors

    def dk(c):
        v = [max(0, int(int(c[i:i + 2], 16) * 0.78)) for i in (1, 3, 5)]
        return "#" + "".join(f"{q:02X}" for q in v)
    return rim, dk(a), dk(b), dk(glow), g


def button_svg(colors, glyph):
    s = Sheet(width=400)
    states = [
        ("active", colors, None), ("hover", colors, glyph), ("pressed", _darker(colors), glyph),
        ("inactive", P.TL_OFF, None), ("hover-inactive", colors, glyph),
        ("pressed-inactive", _darker(colors), glyph),
        ("deactivated", P.TL_OFF, None), ("deactivated-inactive", P.TL_OFF, None),
    ]
    for name, cols, g in states:
        x, y = s.place(BTN_W, BTN_H)
        s.raw(f"{name}-center", (x, y, x + BTN_W, y + BTN_H), _light(s, x, y, cols, g))
    return s.to_svg()


RC = f"""[General]
ActiveTextColor={",".join(str(int(P.TITLE_TEXT[i:i + 2], 16)) for i in (1, 3, 5))}
InactiveTextColor={",".join(str(int(P.TITLE_TEXT_INACTIVE[i:i + 2], 16)) for i in (1, 3, 5))}
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=0
ButtonGroupHover=true

[Layout]
BorderLeft=1
BorderRight=1
BorderBottom=1
TitleEdgeTop=0
TitleEdgeBottom=0
TitleEdgeLeft=8
TitleEdgeRight=8
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized=0
TitleEdgeLeftMaximized=8
TitleEdgeRightMaximized=8
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight={TITLE_H}
ButtonWidth={BTN_W}
ButtonHeight={BTN_H}
ButtonSpacing=1
ButtonMarginTop=0
ButtonMarginTopMaximized=0
ExplicitButtonSpacer=10
PaddingTop={PAD_T}
PaddingBottom={PAD_B}
PaddingLeft={PAD_L}
PaddingRight={PAD_R}
"""

METADATA = """[Desktop Entry]
Name=Snow Leopard
Comment=Mac OS X 10.6 style unified title bar with traffic-light buttons
X-KDE-PluginInfo-Author=Snow Leopard Plasma
X-KDE-PluginInfo-Name=SnowLeopard
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-License=GPL
X-KDE-PluginInfo-Category=
X-KDE-PluginInfo-Depends=
X-KDE-PluginInfo-EnabledByDefault=true
"""


def files():
    return {
        "decoration.svg": decoration_svg(),
        "close.svg": button_svg(P.TL_CLOSE, "close"),
        "minimize.svg": button_svg(P.TL_MIN, "min"),
        "maximize.svg": button_svg(P.TL_MAX, "max"),
        "restore.svg": button_svg(P.TL_MAX, "max"),
        "SnowLeopardrc": RC,
        "metadata.desktop": METADATA,
    }
