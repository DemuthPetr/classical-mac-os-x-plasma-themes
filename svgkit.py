"""Tiny helpers for generating 9-slice SVG theme sheets (Kvantum, Aurorae, Plasma).

Every slice is emitted as its own <g id=...> whose bounding box is pinned by an
invisible rect, so the renderers (QtSvg / KSvg) see exactly the slot geometry.
Shapes are pre-clipped to the slot with polygon clipping, so no clip-path is needed.
"""
import math

_gid = [0]


def _uid(prefix):
    _gid[0] += 1
    return f"{prefix}{_gid[0]}"


def fmt(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def rrect_poly(x, y, w, h, r, seg=10, corners=(1, 1, 1, 1)):
    """Rounded rect polygon. corners = (tl, tr, br, bl) flags."""
    r = max(0.0, min(r, w / 2, h / 2))
    pts = []
    spec = [
        (x + w - r, y + r, -90, corners[1]),
        (x + w - r, y + h - r, 0, corners[2]),
        (x + r, y + h - r, 90, corners[3]),
        (x + r, y + r, 180, corners[0]),
    ]
    sq = [(x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    for (cx, cy, a0, on), corner in zip(spec, sq):
        if on and r > 0:
            for i in range(seg + 1):
                a = math.radians(a0 + 90 * i / seg)
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        else:
            pts.append(corner)
    return pts


def ellipse_poly(cx, cy, rx, ry, seg=48):
    return [(cx + rx * math.cos(2 * math.pi * i / seg), cy + ry * math.sin(2 * math.pi * i / seg)) for i in range(seg)]


def clip_poly(poly, x0, y0, x1, y1):
    """Sutherland-Hodgman clip of a polygon against an axis aligned rect."""
    def clip(pts, inside, inter):
        out = []
        n = len(pts)
        for i in range(n):
            cur, prev = pts[i], pts[i - 1]
            ci, pi = inside(cur), inside(prev)
            if ci:
                if not pi:
                    out.append(inter(prev, cur))
                out.append(cur)
            elif pi:
                out.append(inter(prev, cur))
        return out

    def ix(xc):
        return lambda a, b: (xc, a[1] + (b[1] - a[1]) * (xc - a[0]) / (b[0] - a[0]))

    def iy(yc):
        return lambda a, b: (a[0] + (b[0] - a[0]) * (yc - a[1]) / (b[1] - a[1]), yc)

    p = poly
    for inside, inter in (
        (lambda q: q[0] >= x0, ix(x0)),
        (lambda q: q[0] <= x1, ix(x1)),
        (lambda q: q[1] >= y0, iy(y0)),
        (lambda q: q[1] <= y1, iy(y1)),
    ):
        if not p:
            break
        p = clip(p, inside, inter)
    return p


def path_d(pts):
    if len(pts) < 3:
        return ""
    return "M" + " L".join(f"{fmt(a)},{fmt(b)}" for a, b in pts) + " Z"


class Sheet:
    """An SVG document with gradient defs, slices and a simple row packer."""

    def __init__(self, width=2000):
        self.defs = []
        self.body = []
        self.width = width
        self.cx = 10
        self.cy = 10
        self.row_h = 0

    # ---- layout
    def place(self, w, h, gap=12):
        if self.cx + w > self.width - 10:
            self.cx = 10
            self.cy += self.row_h + gap
            self.row_h = 0
        x, y = self.cx, self.cy
        self.cx += w + gap
        self.row_h = max(self.row_h, h)
        return x, y

    # ---- paints
    def lin(self, stops, x1, y1, x2, y2):
        gid = _uid("lg")
        s = "".join(_stop(o, c) for o, c in stops)
        self.defs.append(
            f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{fmt(x1)}" y1="{fmt(y1)}" '
            f'x2="{fmt(x2)}" y2="{fmt(y2)}">{s}</linearGradient>')
        return f"url(#{gid})"

    def rad(self, stops, cx, cy, r, fx=None, fy=None, sx=1.0, sy=1.0):
        gid = _uid("rg")
        s = "".join(_stop(o, c) for o, c in stops)
        tr = ""
        if sx != 1.0 or sy != 1.0:
            tr = f' gradientTransform="translate({fmt(cx)},{fmt(cy)}) scale({fmt(sx)},{fmt(sy)}) translate({fmt(-cx)},{fmt(-cy)})"'
        fxa = f' fx="{fmt(fx)}" fy="{fmt(fy)}"' if fx is not None else ""
        self.defs.append(
            f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r)}"{fxa}{tr}>{s}</radialGradient>')
        return f"url(#{gid})"

    # ---- raw output
    def group(self, gid, slot, shapes):
        """slot = (x0, y0, x1, y1); shapes = list of (polygon, paint)."""
        x0, y0, x1, y1 = slot
        out = [f'<g id="{gid}"><rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}" fill="#000000" fill-opacity="0"/>']
        for poly, paint in shapes:
            if isinstance(paint, dict):
                # {"image": data-uri, "rect": (x0, y0, x1, y1)}: the image is fitted to the part of
                # rect inside this slot (textures here are uniform along the stretched axis).
                rx0, ry0, rx1, ry1 = paint["rect"]
                ix0, iy0, ix1, iy1 = max(rx0, x0), max(ry0, y0), min(rx1, x1), min(ry1, y1)
                if ix1 > ix0 and iy1 > iy0:
                    out.append(f'<image x="{fmt(ix0)}" y="{fmt(iy0)}" width="{fmt(ix1 - ix0)}" height="{fmt(iy1 - iy0)}" '
                               f'preserveAspectRatio="none" xlink:href="{paint["image"]}"/>')
                continue
            d = path_d(clip_poly(poly, x0, y0, x1, y1))
            if d:
                out.append(_path(d, paint))
        out.append("</g>")
        self.body.append("".join(out))

    def raw(self, gid, slot, inner_svg):
        x0, y0, x1, y1 = slot
        self.body.append(
            f'<g id="{gid}"><rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(x1 - x0)}" height="{fmt(y1 - y0)}" '
            f'fill="#000000" fill-opacity="0"/>{inner_svg}</g>')

    def ninepatch(self, name, x, y, w, h, m, shapes, interior=True, frame=True, interior_name=None):
        """Emit name, name-top, ... from one full drawing. m = (top, right, bottom, left) or int."""
        if isinstance(m, (int, float)):
            m = (m, m, m, m)
        t, r, b, l = m
        xs = [x, x + l, x + w - r, x + w]
        ys = [y, y + t, y + h - b, y + h]
        names = {
            (0, 0): "topleft", (1, 0): "top", (2, 0): "topright",
            (0, 1): "left", (2, 1): "right",
            (0, 2): "bottomleft", (1, 2): "bottom", (2, 2): "bottomright",
        }
        if interior:
            self.group(interior_name or name, (xs[1], ys[1], xs[2], ys[2]), shapes)
        if frame:
            for (i, j), suffix in names.items():
                if xs[i + 1] - xs[i] <= 0 or ys[j + 1] - ys[j] <= 0:
                    continue
                self.group(f"{name}-{suffix}", (xs[i], ys[j], xs[i + 1], ys[j + 1]), shapes)

    def to_svg(self, height=None):
        h = height or (self.cy + self.row_h + 10)
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{self.width}" height="{fmt(h)}" viewBox="0 0 {self.width} {fmt(h)}">\n'
            f'<defs>{"".join(self.defs)}</defs>\n' + "\n".join(self.body) + "\n</svg>\n")


def _stop(o, c):
    col, op = split_color(c)
    return f'<stop offset="{fmt(o)}" stop-color="{col}" stop-opacity="{fmt(op)}"/>'


def split_color(c):
    """'#rrggbbaa' or '#rrggbb' -> ('#rrggbb', alpha)."""
    if c.startswith("#") and len(c) == 9:
        return c[:7], int(c[7:9], 16) / 255
    return c, 1.0


def _path(d, paint):
    if paint.startswith("url("):
        return f'<path d="{d}" fill="{paint}"/>'
    col, op = split_color(paint)
    if op < 1:
        return f'<path d="{d}" fill="{col}" fill-opacity="{fmt(op)}"/>'
    return f'<path d="{d}" fill="{col}"/>'
