"""Kvantum widget style: Aqua controls (glossy buttons, jelly scrollers, blue selections)."""
from svgkit import Sheet, rrect_poly, ellipse_poly, fmt
import palette as P


def capsule(s, x, y, w, h, r, gloss, horizontal=False, glow=True):
    """Aqua control body: white glow below, gradient border, glossy body."""
    btop, bbot, body = gloss
    shapes = []
    hh = h - 1 if glow else h
    if glow:
        shapes.append((rrect_poly(x, y + 1, w, h - 1, r), "#FFFFFF99"))
    if horizontal:
        border = s.lin([(0, btop), (1, bbot)], x, y, x + w, y)
        fill = s.lin(body, x + 1, y, x + w - 1, y)
    else:
        border = s.lin([(0, btop), (1, bbot)], x, y, x, y + hh)
        fill = s.lin(body, x, y + 1, x, y + hh - 1)
    shapes.append((rrect_poly(x, y, w, hh, r), border))
    shapes.append((rrect_poly(x + 1, y + 1, w - 2, hh - 2, max(0, r - 1)), fill))
    return shapes


def element(s, name, w, h, m, draw, **kw):
    x, y = s.place(w, h)
    s.ninepatch(name, x, y, w, h, m, draw(s, x, y, w, h), **kw)


def _unified_toolbar(s):
    element(s, "toolbar-normal", 40, 40, (0, 0, 1, 0), lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 0), s.lin([(0, P.TITLE_BOTTOM), (1, P.TOOLBAR_BOTTOM)], x, y, x, y + h - 1)),
        (rrect_poly(x, y + h - 1, w, 1, 0), P.TOOLBAR_LINE)])
    element(s, "toolbar-normal-inactive", 40, 40, (0, 0, 1, 0), lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 0), s.lin([(0, P.TITLE_INACTIVE_BOTTOM), (1, "#D1D1D1")], x, y, x, y + h - 1)),
        (rrect_poly(x, y + h - 1, w, 1, 0), "#8F8F8F")])


def build_svg():
    s = Sheet(width=1600)

    # ---- push buttons (PanelButtonCommand) and combo boxes
    states = {"normal": P.WHITE_GLOSS, "focused": P.WHITE_HOVER, "pressed": P.BLUE_PRESSED,
              "toggled": P.BLUE_GLOSS, "disabled": P.DISABLED_GLOSS}
    for st, g in states.items():
        element(s, f"button-{st}", 60, 26, 6, lambda s, x, y, w, h, g=g: capsule(s, x, y, w, h, 5, g))
    # default button indicator: pulsing blue in real Aqua, static here
    element(s, "button-default", 60, 26, 6, lambda s, x, y, w, h: capsule(s, x, y, w, h, 5, P.BLUE_GLOSS))

    # ---- the blue end of pop-up buttons
    for st, g in {"normal": P.BLUE_GLOSS, "focused": P.BLUE_GLOSS, "pressed": P.BLUE_PRESSED,
                  "toggled": P.BLUE_PRESSED, "disabled": P.DISABLED_GLOSS}.items():
        element(s, f"dropdown-{st}", 40, 26, 6, lambda s, x, y, w, h, g=g: capsule(s, x, y, w, h, 5, g))

    # ---- tool buttons: flat until touched, like toolbar items on the Mac
    def tool(fill_top, fill_bot, border):
        def d(s, x, y, w, h):
            return [(rrect_poly(x, y, w, h, 4), border),
                    (rrect_poly(x + 1, y + 1, w - 2, h - 2, 3), s.lin([(0, fill_top), (1, fill_bot)], x, y, x, y + h))]
        return d
    element(s, "tbutton-focused", 40, 26, 5, tool("#FFFFFF55", "#FFFFFF22", "#00000022"))
    element(s, "tbutton-pressed", 40, 26, 5, tool("#00000040", "#00000020", "#00000055"))
    element(s, "tbutton-toggled", 40, 26, 5, tool("#00000030", "#00000018", "#00000048"))

    # ---- segmented tabs
    for st, g in {"normal": P.WHITE_GLOSS, "focused": P.WHITE_HOVER, "pressed": P.BLUE_PRESSED,
                  "toggled": P.BLUE_GLOSS, "disabled": P.DISABLED_GLOSS}.items():
        element(s, f"tab-{st}", 60, 24, 5, lambda s, x, y, w, h, g=g: capsule(s, x, y, w, h, 4, g))
    element(s, "tabframe-normal", 60, 40, 5, lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 5), "#00000030"),
        (rrect_poly(x + 1, y + 1, w - 2, h - 2, 4), "#E3E3E3"),
        (rrect_poly(x + 1, y + 1, w - 2, 2, 0), "#D6D6D6")])

    # ---- line edits (square, inset, Aqua focus ring)
    def lineedit(focused):
        def d(s, x, y, w, h):
            sh = []
            if focused:
                sh += [(rrect_poly(x, y, w, h, 4), "#7AA7E5B0"),
                       (rrect_poly(x + 1, y + 1, w - 2, h - 2, 3), "#8DB6ECE0")]
            sh += [(rrect_poly(x + 2, y + 2, w - 4, h - 4, 0),
                    "#5F8AC8" if focused else s.lin([(0, "#8A8A8A"), (1, "#BDBDBD")], x, y + 2, x, y + h - 2)),
                   (rrect_poly(x + 3, y + 3, w - 6, h - 6, 0), "#E2E2E2"),
                   (rrect_poly(x + 3, y + 4, w - 6, h - 7, 0), P.BASE)]
            return sh
        return d
    element(s, "lineedit-normal", 60, 26, 4, lineedit(False))
    element(s, "lineedit-focused", 60, 26, 4, lineedit(True))
    element(s, "lineedit-disabled", 60, 26, 4, lambda s, x, y, w, h: [
        (rrect_poly(x + 2, y + 2, w - 4, h - 4, 0), "#C9C9C9"),
        (rrect_poly(x + 3, y + 3, w - 6, h - 6, 0), "#F7F7F7")])

    # ---- generic frames, group boxes, docks
    element(s, "common-normal", 40, 40, 1, lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 0), "#A5A5A5"), (rrect_poly(x + 1, y + 1, w - 2, h - 2, 0), "#00000000")],
        interior=False)
    element(s, "group-normal", 50, 50, 6, lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 5), "#0000002C"), (rrect_poly(x + 1, y + 1, w - 2, h - 2, 4), "#F3F3F3"),
        (rrect_poly(x + 1, y + 1, w - 2, h - 2, 4), "#0000000A")])
    element(s, "dock-normal", 40, 24, 2, lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 0), "#A5A5A5"),
        (rrect_poly(x + 1, y + 1, w - 2, h - 2, 0), s.lin([(0, "#F4F4F4"), (1, "#DADADA")], x, y, x, y + h))])

    # ---- check boxes and radio buttons (16 px, full elements)
    def check_body(g, round_):
        def d(s, x, y, w, h):
            r = 8 if round_ else 3
            return capsule(s, x, y, w, h, r, g, glow=False)
        return d

    check_states = {"normal": P.WHITE_GLOSS, "focused": P.WHITE_HOVER, "pressed": P.BLUE_PRESSED,
                    "disabled": P.DISABLED_GLOSS}
    for kind, round_ in (("checkbox", False), ("radio", True)):
        for st, g in check_states.items():
            x, y = s.place(16, 16)
            s.group(f"{kind}-{st}", (x, y, x + 16, y + 16), check_body(g, round_)(s, x, y, 16, 16))
        for mark in ("checked", "tristate") if kind == "checkbox" else ("checked",):
            for st, g in {"normal": P.BLUE_GLOSS, "focused": P.BLUE_GLOSS, "pressed": P.BLUE_PRESSED,
                          "disabled": P.DISABLED_GLOSS}.items():
                x, y = s.place(16, 16)
                body = check_body(g, round_)(s, x, y, 16, 16)
                col = "#9A9A9A" if st == "disabled" else "#111111"
                if kind == "radio":
                    body.append((ellipse_poly(x + 8, y + 8, 3, 3, 24), col))
                    s.group(f"radio-{mark}-{st}", (x, y, x + 16, y + 16), body)
                    continue
                s.group(f"_tmp", (x, y, x + 16, y + 16), body)
                inner = s.body.pop()[len('<g id="_tmp">'):-len("</g>")]
                if mark == "checked":
                    glyph = (f'<path d="M{fmt(x + 3.5)},{fmt(y + 8.2)} L{fmt(x + 6.8)},{fmt(y + 11.6)} '
                             f'L{fmt(x + 13)},{fmt(y + 3.2)}" fill="none" stroke="{col}" stroke-width="2.1" '
                             f'stroke-linecap="round" stroke-linejoin="round"/>')
                else:
                    glyph = f'<rect x="{x + 4}" y="{y + 7}" width="8" height="2.2" rx="1" fill="{col}"/>'
                s.raw(f"checkbox-{mark}-{st}", (x, y, x + 16, y + 16), inner + glyph)
    # check marks for checkable menu / view items
    for mark in ("checked", "tristate"):
        for st, col in (("normal", "#111111"), ("focused", "#FFFFFF"), ("pressed", "#FFFFFF"),
                        ("toggled", "#FFFFFF"), ("disabled", "#9A9A9A")):
            x, y = s.place(16, 16)
            if mark == "checked":
                g = (f'<path d="M{fmt(x + 3.5)},{fmt(y + 8.2)} L{fmt(x + 6.8)},{fmt(y + 11.6)} L{fmt(x + 13)},{fmt(y + 3.2)}" '
                     f'fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
            else:
                g = f'<rect x="{x + 4}" y="{y + 7}" width="8" height="2" rx="1" fill="{col}"/>'
            s.raw(f"item-checkbox-{mark}-{st}", (x, y, x + 16, y + 16), g)

    # ---- scrollbars (drawn vertical; Kvantum rotates them for horizontal bars)
    def groove(s, x, y, w, h):
        return [(rrect_poly(x, y, w, h, 0), s.lin([(0, "#C6C6C6"), (0.2, "#DCDCDC"), (0.55, "#F2F2F2"),
                                                    (0.85, "#ECECEC"), (1, "#D2D2D2")], x, y, x + w, y)),
                (rrect_poly(x + 2, y + 2, w - 4, h - 4, (w - 4) / 2),
                 s.lin([(0, "#B4B4B4"), (0.5, "#CDCDCD"), (1, "#C4C4C4")], x, y, x + w, y)),
                (rrect_poly(x + 3, y + 3, w - 6, h - 6, (w - 6) / 2),
                 s.lin([(0, "#D8D8D8"), (0.5, "#EDEDED"), (1, "#E2E2E2")], x, y, x + w, y))]
    if P.STYLE.get("scroll") == "overlay":
        # Lion and later: no track, thin dark thumb
        def groove(s, x, y, w, h):
            return [(rrect_poly(x, y, w, h, 0), "#FFFFFF00")]
    element(s, "scrollbargroove-normal", 15, 60, (8, 0, 8, 0), groove)
    element(s, "scrollbargroove-disabled", 15, 60, (8, 0, 8, 0), groove)

    jelly_blue = ("#3D64A6", "#466FB4", [(0, "#4F81CF"), (0.12, "#7BA8E7"), (0.38, "#C3DDF9"), (0.5, "#9CC5F3"),
                                         (0.5, "#76AAEC"), (0.85, "#A9D3FB"), (1, "#6E9CDD")])
    jelly_hover = ("#33599A", "#3D66AA", [(0, "#4677C7"), (0.12, "#719FE1"), (0.38, "#B8D5F6"), (0.5, "#90BCF0"),
                                          (0.5, "#6AA0E8"), (0.85, "#9CCAF9"), (1, "#6593D6")])
    jelly_press = ("#2A4E8C", "#2F5594", [(0, "#3C6AB8"), (0.12, "#5F8FD6"), (0.38, "#9EC2EE"), (0.5, "#759FE0"),
                                          (0.5, "#5389DA"), (0.85, "#7FB2EE"), (1, "#5584CB")])
    jelly_graphite = ("#6F6F6F", "#787878", [(0, "#8C8C8C"), (0.12, "#AFAFAF"), (0.38, "#E2E2E2"), (0.5, "#C8C8C8"),
                                             (0.5, "#B2B2B2"), (0.85, "#D4D4D4"), (1, "#A2A2A2")])

    def jelly(g):
        if P.STYLE.get("scroll") == "overlay":
            tone = {"#3D64A6": "#00000078", "#33599A": "#00000090", "#2A4E8C": "#000000A8"}.get(g[0], "#00000060")
            return lambda s, x, y, w, h: [(rrect_poly(x + 4, y + 1, w - 7, h - 2, (w - 7) / 2), tone)]
        return lambda s, x, y, w, h: capsule(s, x + 2, y + 1, w - 4, h - 2, (w - 4) / 2, g, horizontal=True, glow=False)
    for st, g in (("normal", jelly_blue), ("focused", jelly_hover), ("pressed", jelly_press),
                  ("normal-inactive", jelly_graphite), ("focused-inactive", jelly_graphite),
                  ("disabled", jelly_graphite)):
        element(s, f"scrollbarslider-{st}", 15, 60, (8, 0, 8, 0), jelly(g))

    # ---- sliders: thin inset track, blue fill, glossy knob
    def track(fill):
        def d(s, x, y, w, h):
            return [(rrect_poly(x, y, w, h, 2.5), "#7E7E7E"),
                    (rrect_poly(x + 1, y + 1, w - 2, h - 2, 1.5), s.lin(fill, x, y, x, y + h))]
        return d
    element(s, "slider-normal", 40, 5, (2, 3, 2, 3), track([(0, "#9E9E9E"), (1, "#E4E4E4")]))
    element(s, "slider-disabled", 40, 5, (2, 3, 2, 3), track([(0, "#CFCFCF"), (1, "#EEEEEE")]))
    element(s, "slider-toggled", 40, 5, (2, 3, 2, 3), track([(0, "#3E6DB8"), (1, "#8DBDF1")]))
    for st, g in (("normal", P.WHITE_GLOSS), ("focused", P.WHITE_HOVER), ("pressed", P.BLUE_GLOSS),
                  ("disabled", P.DISABLED_GLOSS)):
        x, y = s.place(18, 18)
        knob = [(ellipse_poly(x + 9, y + 9.6, 8.6, 8.4), "#00000030")]
        knob += capsule(s, x + 1, y + 1, 16, 16, 8, g, glow=False)
        knob.append((ellipse_poly(x + 9, y + 5.2, 5.2, 2.6), "#FFFFFF90"))
        s.group(f"slidercursor-{st}", (x, y, x + 18, y + 18), knob)

    # ---- progress bars: capsule groove + tiled blue barber-pole
    def pgroove(s, x, y, w, h):
        return capsule(s, x, y, w, h, 7, ("#8D8D8D", "#9F9F9F",
                                          [(0, "#F6F6F6"), (0.5, "#E8E8E8"), (0.5, "#DADADA"), (1, "#F2F2F2")]),
                       glow=False)
    element(s, "progress-normal", 40, 14, (3, 7, 3, 7), pgroove)
    element(s, "progress-disabled", 40, 14, (3, 7, 3, 7), pgroove)

    def ppattern(gloss, stripe):
        def d(s, x, y, w, h):
            sh = capsule(s, x, y, w, h, 7, gloss, glow=False)
            for k in range(-2, 4):
                sx = x + 7 + k * 16
                sh.append(([(sx, y + h), (sx + 8, y + h), (sx + 16, y), (sx + 8, y)], stripe))
            sh.append((rrect_poly(x + 1, y + 1, w - 2, (h - 2) / 2, 0), "#FFFFFF30"))
            return sh
        return d
    # template: 7px caps + 16px tile + 7px caps, 3 + 8 + 3 high
    blue_bar = ("#3B62A3", "#2E5394", [(0, "#A9C9F1"), (0.5, "#6C9FE6"), (0.5, "#3F7FDB"), (1, "#8BC1FA")])
    element(s, "progress-pattern-normal", 30, 14, (3, 7, 3, 7), ppattern(blue_bar, "#FFFFFF38"))
    element(s, "progress-pattern-focused", 30, 14, (3, 7, 3, 7), ppattern(blue_bar, "#FFFFFF38"))
    element(s, "progress-pattern-disabled", 30, 14, (3, 7, 3, 7), ppattern(P.GRAPHITE_GLOSS, "#FFFFFF30"))
    element(s, "progress-pattern-normal-inactive", 30, 14, (3, 7, 3, 7), ppattern(P.GRAPHITE_GLOSS, "#FFFFFF30"))

    # ---- menus
    element(s, "menu-normal", 40, 40, 4, lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 4), "#00000038"),
        (rrect_poly(x + 1, y + 1, w - 2, h - 2, 3), "#FFFFFFF2")])
    sh_depth = 6
    def shadow(s, x, y, w, h):
        out = []
        for i in range(sh_depth):
            a = int(14 + i * 5)
            out.append((rrect_poly(x + i, y + i + 1, w - 2 * i, h - 2 * i - 1, sh_depth - i + 3), f"#000000{a:02X}"))
        return out
    element(s, "menu-shadow", 40, 40, sh_depth, shadow, interior=False)
    element(s, "tooltip-shadow", 40, 40, sh_depth, shadow, interior=False)

    def blue_band(stops, top):
        def d(s, x, y, w, h):
            return [(rrect_poly(x, y, w, h, 0), s.lin(stops, x, y, x, y + h)),
                    (rrect_poly(x, y, w, 1, 0), top)]
        return d
    for st in ("focused", "pressed", "toggled"):
        element(s, f"menuitem-{st}", 40, 20, 2, blue_band(P.MENU_SEL, P.MENU_SEL_TOP))
        element(s, f"menubaritem-{st}", 40, 20, 2, blue_band(P.MENU_SEL, P.MENU_SEL_TOP))
    element(s, "menubar-normal", 40, 22, (0, 0, 1, 0), lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 0), s.lin([(0, "#FAFAFA"), (1, "#D6D6D6")], x, y, x, y + h)),
        (rrect_poly(x, y + h - 1, w, 1, 0), "#8E8E8E")])

    # ---- unified toolbar (continues the window title gradient)
    if P.STYLE.get("toolbar") == "textured":
        # pinstripe / brushed-metal windows: the window texture shows through, only a dividing line
        # KDE toolbars fill themselves with a flat colour, so the toolbar carries the texture as a
        # tiled interior (same tile as the window) plus a dividing line as its bottom frame.
        tex = P.STYLE.get("window_tile")
        for nm in ("toolbar-normal", "toolbar-normal-inactive"):
            element(s, nm, 40, 40, (0, 0, 1, 0), lambda s, x, y, w, h: [
                (rrect_poly(x, y + h - 1, w, 1, 0), P.TOOLBAR_LINE)], interior=not tex)
            if tex:
                uri, tw, th, _avg = tex
                x, y = s.place(tw, th)
                s.raw(nm, (x, y, x + tw, y + th),
                      f'<image x="{x}" y="{y}" width="{tw}" height="{th}" preserveAspectRatio="none" xlink:href="{uri}"/>')
    else:
        _unified_toolbar(s)

    # ---- item views
    for st, stops, top in (("pressed", P.LIST_SEL, P.LIST_SEL_TOP), ("toggled", P.LIST_SEL, P.LIST_SEL_TOP),
                           ("pressed-inactive", P.LIST_SEL_INACTIVE, "#B5B5B5"),
                           ("toggled-inactive", P.LIST_SEL_INACTIVE, "#B5B5B5")):
        element(s, f"itemview-{st}", 40, 20, 1, blue_band(stops, top))
    element(s, "itemview-focused", 40, 20, 1, lambda s, x, y, w, h: [(rrect_poly(x, y, w, h, 0), "#3875D71C")])

    # ---- list headers
    for st, stops in (("normal", [(0, "#FFFFFF"), (0.5, "#F5F5F5"), (0.5, "#EAEAEA"), (1, "#F7F7F7")]),
                      ("focused", [(0, "#FFFFFF"), (0.5, "#F8F8F8"), (0.5, "#EFEFEF"), (1, "#FAFAFA")]),
                      ("pressed", [(0, "#C9DDF6"), (0.5, "#AFCBF0"), (0.5, "#97BDEB"), (1, "#C4DEFA")]),
                      ("toggled", [(0, "#DCEBFB"), (0.5, "#C5DCF7"), (0.5, "#ADD0F5"), (1, "#D7ECFF")])):
        element(s, f"header-{st}", 40, 18, (0, 1, 1, 0), lambda s, x, y, w, h, stops=stops: [
            (rrect_poly(x, y, w, h, 0), s.lin(stops, x, y, x, y + h)),
            (rrect_poly(x + w - 1, y + 2, 1, h - 4, 0), "#BEBEBE"),
            (rrect_poly(x, y + h - 1, w, 1, 0), "#A0A0A0")])

    # ---- tooltips (Mac OS X pale yellow)
    element(s, "tooltip-normal", 30, 30, 2, lambda s, x, y, w, h: [
        (rrect_poly(x, y, w, h, 0), "#00000050"), (rrect_poly(x + 1, y + 1, w - 2, h - 2, 0), P.TOOLTIP_BG)])

    # ---- arrows / disclosure triangles / spin steppers
    colors = {"normal": "#4D4D4D", "focused": "#1E1E1E", "pressed": "#000000", "toggled": "#FFFFFF",
              "disabled": "#ABABAB"}
    tri = {"down": [(1, 2.5), (9, 2.5), (5, 8)], "up": [(1, 7.5), (9, 7.5), (5, 2)],
           "right": [(2.5, 1), (2.5, 9), (8, 5)], "left": [(7.5, 1), (7.5, 9), (2, 5)]}
    for prefix in ("arrow", "flat-arrow"):
        for d, pts in tri.items():
            for st, c in colors.items():
                x, y = s.place(10, 10)
                s.group(f"{prefix}-{d}-{st}", (x, y, x + 10, y + 10), [([(x + a, y + b) for a, b in pts], c)])
    for sign, d in (("plus", "up"), ("minus", "down")):
        for st, c in colors.items():
            x, y = s.place(10, 10)
            s.group(f"arrow-{sign}-{st}", (x, y, x + 10, y + 10), [([(x + a, y + b) for a, b in tri[d]], c)])

    # ---- tab close buttons
    for st, circle, glyph in (("normal", None, "#6E6E6E"), ("focused", "#9C9C9C", "#FFFFFF"),
                              ("pressed", "#6C6C6C", "#FFFFFF"), ("toggled", None, "#3A3A3A"),
                              ("disabled", None, "#BDBDBD")):
        x, y = s.place(16, 16)
        inner = f'<circle cx="{x + 8}" cy="{y + 8}" r="7" fill="{circle}"/>' if circle else ""
        inner += (f'<path d="M{x + 5},{y + 5} L{x + 11},{y + 11} M{x + 11},{y + 5} L{x + 5},{y + 11}" '
                  f'stroke="{glyph}" stroke-width="1.8" stroke-linecap="round"/>')
        s.raw(f"tab-close-{st}", (x, y, x + 16, y + 16), inner)

    # ---- grips
    for name, size in (("splitter-grip-normal", 8), ("splitter-grip-focused", 8), ("splitter-grip-pressed", 8)):
        x, y = s.place(size, size)
        s.raw(name, (x, y, x + size, y + size),
              f'<circle cx="{x + 4}" cy="{y + 4}" r="2.2" fill="#8A8A8A"/><circle cx="{x + 4}" cy="{y + 3.5}" r="1" fill="#FFFFFF" fill-opacity="0.6"/>')
    x, y = s.place(12, 12)
    s.raw("resize-grip-normal", (x, y, x + 12, y + 12), "".join(
        f'<path d="M{x + 12 - k},{y + 12} L{x + 12},{y + 12 - k}" stroke="#8C8C8C" stroke-width="1"/>'
        f'<path d="M{x + 12 - k + 1},{y + 12} L{x + 12},{y + 12 - k + 1}" stroke="#FFFFFF" stroke-width="1"/>'
        for k in (4, 8, 12)))
    tile = P.STYLE.get("window_tile")
    if tile:
        uri, tw, th, _avg = tile
        for nm in ("window-normal", "window-normal-inactive"):
            x, y = s.place(tw, th)
            s.raw(nm, (x, y, x + tw, y + th),
                  f'<image x="{x}" y="{y}" width="{tw}" height="{th}" preserveAspectRatio="none" xlink:href="{uri}"/>')
    return s.to_svg()


KVCONFIG = f"""[%General]
author=Built for Snow Leopard Plasma
comment=Mac OS X 10.6 Snow Leopard Aqua controls
x11drag=menubar_and_primary_toolbar
alt_mnemonic=true
left_tabs=false
attach_active_tab=false
embedded_tabs=false
center_doc_tabs=false
center_normal_tabs=true
mirror_doc_tabs=false
joined_inactive_tabs=true
group_toolbar_buttons=false
spread_progressbar=true
composite=true
menu_shadow_depth=6
tooltip_shadow_depth=6
menu_separator_height=10
spread_menuitems=true
scroll_width=15
scroll_arrows=false
scroll_min_extent=36
transient_scrollbar=false
slider_width=5
slider_handle_width=18
slider_handle_length=18
check_size=16
textless_progressbar=false
progressbar_thickness=14
menubar_mouse_tracking=true
toolbutton_style=0
click_behavior=0
translucent_windows=false
blurring=false
popup_blurring=true
vertical_spin_indicators=true
spin_button_width=16
fill_rubberband=true
merge_menubar_with_toolbar=true
small_icon_size=16
large_icon_size=32
button_icon_size=16
toolbar_icon_size=24
combo_as_lineedit=false
combo_menu=true
combo_focus_rect=false
hide_combo_checkboxes=true
inline_spin_indicators=true
inline_spin_separator=false
animate_states=false
no_inactiveness=false
dialog_button_layout=3
layout_spacing=6
layout_margin=12
submenu_overlap=0
submenu_delay=150
tree_branch_line=false
button_contents_shift=false
respect_DE=true
scrollable_menu=true
contrast=1.00
intensity=1.00
saturation=1.00
reduce_window_opacity=0
reduce_menu_opacity=0

[GeneralColors]
window.color={P.WINDOW_BG}
base.color={P.BASE}
alt.base.color={P.ALT_BASE}
button.color={P.BUTTON_BG}
light.color=#FFFFFF
mid.light.color=#E2E2E2
dark.color=#A0A0A0
mid.color=#C8C8C8
shadow.color=#00000040
highlight.color={P.SELECTION}
inactive.highlight.color=#C4C4C4
tooltip.base.color={P.TOOLTIP_BG}
text.color=#000000
window.text.color=#000000
button.text.color=#000000
disabled.text.color=#0000006A
tooltip.text.color=#000000
highlight.text.color=#FFFFFF
inactive.highlight.text.color=#000000
link.color={P.LINK}
link.visited.color={P.LINK_VISITED}
progress.indicator.text.color=#000000
progress.inactive.indicator.text.color=#000000

[Hacks]
transparent_ktitle_label=true
transparent_dolphin_view=false
transparent_pcmanfm_sidepane=false
blur_translucent=true
transparent_menutitle=true
respect_darkness=true
force_size_grip=false
iconless_pushbutton=true
iconless_menu=false
transparent_arrow_button=true
single_top_toolbar=true
no_selection_tint=true
centered_forms=false
kinetic_scrolling=false
middle_click_scroll=false
normal_default_pushbutton=false
tint_on_mouseover=0
disabled_icon_opacity=60
lxqtmainmenu_iconsize=16

[PanelButtonCommand]
frame=true
frame.element=button
frame.top=6
frame.bottom=6
frame.left=6
frame.right=6
interior=true
interior.element=button
indicator.size=9
indicator.element=arrow
text.normal.color=#000000
text.focus.color=#000000
text.press.color=#000000
text.toggle.color=#000000
text.shadow=0
text.margin=1
text.iconspacing=4
text.margin.top=1
text.margin.bottom=1
text.margin.left=8
text.margin.right=8
min_width=+0.4font
min_height=+0.2font
frame.expansion=0

[PanelButtonTool]
inherits=PanelButtonCommand
frame.element=tbutton
interior.element=tbutton
frame.top=5
frame.bottom=5
frame.left=5
frame.right=5
text.margin.left=3
text.margin.right=3
min_width=0
min_height=0

[ToolbarButton]
inherits=PanelButtonTool

[DropDownButton]
inherits=PanelButtonCommand
frame.element=dropdown
interior.element=dropdown
indicator.element=arrow
indicator.size=8
text.normal.color=#FFFFFF

[IndicatorSpinBox]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.element=arrow
indicator.size=8

[RadioButton]
inherits=PanelButtonCommand
frame=false
interior.element=radio
text.margin.left=2
text.margin.right=2

[CheckBox]
inherits=PanelButtonCommand
frame=false
interior.element=checkbox
text.margin.left=2
text.margin.right=2

[Focus]
inherits=PanelButtonCommand
frame=false
interior=false

[GenericFrame]
inherits=PanelButtonCommand
frame=true
interior=false
frame.element=common
interior.element=common
frame.top=1
frame.bottom=1
frame.left=1
frame.right=1

[LineEdit]
inherits=PanelButtonCommand
frame.element=lineedit
interior.element=lineedit
frame.top=4
frame.bottom=4
frame.left=4
frame.right=4
text.margin.left=2
text.margin.right=2
min_height=+0.2font

[ToolbarLineEdit]
inherits=LineEdit

[ComboBox]
inherits=PanelButtonCommand
text.margin.left=8
text.margin.right=4

[ToolboxTab]
inherits=PanelButtonCommand

[Tab]
inherits=PanelButtonCommand
frame.element=tab
interior.element=tab
frame.top=5
frame.bottom=5
frame.left=5
frame.right=5
indicator.element=tab
indicator.size=16
text.margin.left=10
text.margin.right=10
text.margin.top=1
text.margin.bottom=1
focusFrame=false
min_width=+1font
min_height=+0.2font

[TabFrame]
inherits=PanelButtonCommand
frame.element=tabframe
interior.element=tabframe
frame.top=5
frame.bottom=5
frame.left=5
frame.right=5

[TabBarFrame]
inherits=GenericFrame
frame=false
interior=false

[TreeExpander]
inherits=PanelButtonCommand
frame=false
interior=false
indicator.size=10
indicator.element=arrow

[HeaderSection]
inherits=PanelButtonCommand
frame.element=header
interior.element=header
frame.top=0
frame.bottom=1
frame.left=0
frame.right=1
text.margin.left=4
text.margin.right=4
text.margin.top=1
text.margin.bottom=1
indicator.element=arrow
indicator.size=8
text.toggle.color=#000000
min_height=+0.1font

[SizeGrip]
indicator.element=resize-grip

[Toolbar]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=toolbar
interior.element=toolbar
frame.top=0
frame.bottom=1
frame.left=0
frame.right=0
indicator.element=toolbar
indicator.size=5
text.margin=0
text.normal.color=#000000

[Slider]
inherits=PanelButtonCommand
frame.element=slider
interior.element=slider
frame.top=2
frame.bottom=2
frame.left=3
frame.right=3
focusFrame=false

[SliderCursor]
inherits=PanelButtonCommand
frame=false
interior.element=slidercursor

[Progressbar]
inherits=PanelButtonCommand
frame.element=progress
interior.element=progress
frame.top=3
frame.bottom=3
frame.left=7
frame.right=7
text.margin=0
text.bold=false
text.normal.color=#000000
text.focus.color=#000000
frame.expansion=0

[ProgressbarContents]
inherits=PanelButtonCommand
frame=true
frame.element=progress-pattern
interior.element=progress-pattern
frame.top=3
frame.bottom=3
frame.left=7
frame.right=7
interior.x.patternsize=16
interior.y.patternsize=8
frame.expansion=0

[ItemView]
inherits=PanelButtonCommand
frame.element=itemview
interior.element=itemview
frame.top=1
frame.bottom=1
frame.left=1
frame.right=1
text.margin.top=1
text.margin.bottom=1
text.margin.left=3
text.margin.right=3
text.normal.color=#000000
text.focus.color=#000000
text.press.color=#FFFFFF
text.toggle.color=#FFFFFF
min_width=+0.3font
min_height=+0.3font
frame.expansion=0

[Splitter]
interior=false
frame=false
indicator.element=splitter-grip
indicator.size=8

[Scrollbar]
inherits=PanelButtonCommand
indicator.element=arrow
indicator.size=8

[ScrollbarGroove]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=scrollbargroove
interior.element=scrollbargroove
frame.top=8
frame.bottom=8
frame.left=0
frame.right=0

[ScrollbarSlider]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=scrollbarslider
interior.element=scrollbarslider
frame.top=8
frame.bottom=8
frame.left=0
frame.right=0
indicator.element=none

[MenuItem]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=menuitem
interior.element=menuitem
indicator.element=arrow
indicator.size=8
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
text.margin.top=1
text.margin.bottom=1
text.margin.left=6
text.margin.right=6
text.normal.color=#000000
text.focus.color=#FFFFFF
text.press.color=#FFFFFF
text.toggle.color=#FFFFFF
min_height=+0.4font

[MenuBar]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=menubar
interior.element=menubar
frame.top=0
frame.bottom=1
frame.left=0
frame.right=0

[MenuBarItem]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=menubaritem
interior.element=menubaritem
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
text.margin.left=6
text.margin.right=6
text.margin.top=1
text.margin.bottom=1
text.normal.color=#000000
text.focus.color=#000000
text.press.color=#FFFFFF
text.toggle.color=#FFFFFF

[TitleBar]
inherits=PanelButtonCommand
frame=false
interior=false
text.normal.color={P.TITLE_TEXT_INACTIVE}
text.focus.color={P.TITLE_TEXT}

[ComboBoxFrame]
inherits=GenericFrame

[Menu]
inherits=PanelButtonCommand
frame=true
interior=true
frame.element=menu
interior.element=menu
frame.top=4
frame.bottom=4
frame.left=1
frame.right=1
text.normal.color=#000000

[GroupBox]
inherits=GenericFrame
frame=true
interior=true
frame.element=group
interior.element=group
frame.top=6
frame.bottom=6
frame.left=6
frame.right=6
text.normal.color=#000000
text.bold=false

[ToolTip]
inherits=GenericFrame
frame=true
interior=true
frame.element=tooltip
interior.element=tooltip
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2
text.margin=1
text.normal.color=#000000

[StatusBar]
inherits=GenericFrame
frame=false
interior=false

[Window]
interior=false
frame=false

[Dock]
inherits=PanelButtonCommand
frame.element=dock
interior.element=dock
frame.top=2
frame.bottom=2
frame.left=2
frame.right=2

[DockTitle]
inherits=PanelButtonCommand
frame=false
interior=false
text.bold=true
"""
