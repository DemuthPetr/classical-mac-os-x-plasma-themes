"""Original procedural wallpapers in the mood of each Mac OS X era (no Apple artwork)."""
import math
import random
from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H = 1280, 720


def _gradient(top, bottom, w=W, h=H):
    img = Image.new("RGB", (1, h))
    for yy in range(h):
        t = yy / (h - 1)
        img.putpixel((0, yy), tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    return img.resize((w, h))


def _screen(base, layer, opacity):
    return Image.blend(base, ImageChops.screen(base, layer), opacity)


def _multiply(base, layer, opacity):
    return Image.blend(base, ImageChops.multiply(base, layer), opacity)


def _layer(draw_cb, blur, mode="RGB", bg=(0, 0, 0)):
    lay = Image.new(mode, (W, H), bg)
    draw_cb(ImageDraw.Draw(lay))
    return lay.filter(ImageFilter.GaussianBlur(blur)) if blur else lay


def _finish(img, path, size, stars=0, seed=0):
    img = img.resize(size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.0))
    if stars:
        rnd = random.Random(seed)
        d = ImageDraw.Draw(img)
        for _ in range(stars):
            x, y = rnd.uniform(0, size[0]), rnd.uniform(0, size[1])
            v = int(rnd.uniform(110, 255))
            r = rnd.choice([0.6, 0.8, 1.0, 1.0, 1.5, 2.2])
            d.ellipse([x - r, y - r, x + r, y + r], fill=(v, v, min(255, v + 25)))
    img.save(path, quality=93)
    return img


def aqua(path, top, bottom, swoosh, seed, lines=0, size=(3840, 2160)):
    """Early Aqua: deep blue with large soft light swooshes (10.0-10.4 mood)."""
    rnd = random.Random(seed)
    img = _gradient(top, bottom)

    def big(d):
        for _ in range(5):
            cx, cy = rnd.uniform(-0.2, 0.6) * W, rnd.uniform(0.2, 1.2) * H
            rx, ry = rnd.uniform(0.5, 1.0) * W, rnd.uniform(0.35, 0.7) * H
            d.arc([cx - rx, cy - ry, cx + rx, cy + ry], rnd.uniform(180, 250), rnd.uniform(300, 360),
                  fill=swoosh, width=int(rnd.uniform(60, 140)))
    img = _screen(img, _layer(big, 45), 0.55)

    def soft(d):
        for _ in range(3):
            cx, cy = rnd.uniform(0.3, 1.1) * W, rnd.uniform(-0.3, 0.4) * H
            r = rnd.uniform(0.3, 0.6) * W
            d.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6], fill=tuple(int(c * 0.6) for c in swoosh))
    img = _screen(img, _layer(soft, 120), 0.5)

    def shade(d):
        for _ in range(3):
            cx, cy = rnd.uniform(0.0, 1.0) * W, rnd.uniform(0.5, 1.2) * H
            r = rnd.uniform(0.3, 0.5) * W
            d.ellipse([cx - r, cy - r * 0.5, cx + r, cy + r * 0.5], fill=(70, 80, 110))
    img = _multiply(img, _layer(shade, 110, bg=(255, 255, 255)), 0.45)

    if lines:
        def thin(d):
            for _ in range(lines):
                cx, cy = rnd.uniform(-0.3, 1.3) * W, rnd.uniform(0.6, 1.8) * H
                rx, ry = rnd.uniform(0.6, 1.4) * W, rnd.uniform(0.5, 1.2) * H
                d.arc([cx - rx, cy - ry, cx + rx, cy + ry], 180, 360, fill=(235, 245, 255), width=3)
        img = _screen(img, _layer(thin, 2.5), 0.55)
    return _finish(img, path, size)


def galaxy(path, base_top, base_bottom, arm, core, seed, tilt=-0.45, size=(3840, 2160)):
    """Lion / Mountain Lion mood: a tilted spiral galaxy in deep space."""
    rnd = random.Random(seed)
    img = _gradient(base_top, base_bottom)
    cx, cy = W * 0.5, H * 0.52
    ca, sa = math.cos(tilt), math.sin(tilt)

    def rot(px, py):
        return cx + px * ca - py * sa, cy + px * sa + py * ca

    def disc(d):
        for k in range(26, 0, -1):
            rx, ry = W * 0.03 * k, W * 0.0075 * k
            pts = [rot(rx * math.cos(t / 40 * 2 * math.pi), ry * math.sin(t / 40 * 2 * math.pi)) for t in range(40)]
            f = 1 - k / 27
            d.polygon(pts, fill=tuple(int(c * (0.25 + 0.75 * f)) for c in arm))
    img = _screen(img, _layer(disc, 30), 0.85)

    def dust(d):
        for _ in range(3200):
            t = rnd.uniform(0, 2 * math.pi)
            r = abs(rnd.gauss(0, 0.33)) * W * 0.75
            arm_off = math.sin(2 * t + r / (W * 0.08)) * 0.25
            px, py = r * math.cos(t), r * 0.24 * math.sin(t + arm_off)
            x, y = rot(px, py)
            s = rnd.uniform(0.6, 2.2)
            v = rnd.uniform(0.35, 1)
            d.ellipse([x - s, y - s, x + s, y + s], fill=tuple(int(c * v) for c in arm))
    img = _screen(img, _layer(dust, 2), 0.7)

    def lanes(d):
        # thin dark dust lanes following the disc, not blobs
        for k in range(5):
            r = (0.12 + k * 0.07) * W
            pts = [rot(r * math.cos(t / 60 * 2 * math.pi), r * 0.23 * math.sin(t / 60 * 2 * math.pi))
                   for t in range(18 + k * 3, 42 + k * 3)]
            d.line(pts, fill=(120, 110, 120), width=int(6 + k * 2), joint="curve")
    img = _multiply(img, _layer(lanes, 9, bg=(255, 255, 255)), 0.35)

    def centre(d):
        for k in range(12, 0, -1):
            r = k * 9
            f = 1 - k / 13
            x0, y0 = rot(0, 0)
            d.ellipse([x0 - r * 1.9, y0 - r * 0.7, x0 + r * 1.9, y0 + r * 0.7],
                      fill=tuple(int(c * (0.3 + 0.7 * f)) for c in core))
    img = _screen(img, _layer(centre, 22), 0.95)
    return _finish(img, path, size, stars=1800, seed=seed)


def wave(path, seed, size=(3840, 2160)):
    """Mavericks mood: a large teal ocean wave curling from the left."""
    rnd = random.Random(seed)
    img = _gradient((10, 120, 150), (20, 70, 140))

    def band(d, col, width, amp, phase, y0):
        pts = []
        for i in range(0, 161):
            x = i / 160 * W
            y = y0 + amp * math.sin(x / W * 3.0 + phase) - (W - x) * 0.25 * math.exp(-x / (W * 0.35))
            pts.append((x, y))
        d.line(pts, fill=col, width=width, joint="curve")

    def greens(d):
        for k in range(14):
            band(d, rnd.choice([(40, 190, 150), (20, 160, 170), (60, 200, 180)]), rnd.randint(40, 90),
                 rnd.uniform(30, 70), rnd.uniform(0, 3), H * (0.05 + k * 0.07))
    img = _screen(img, _layer(greens, 30), 0.55)

    def troughs(d):
        for k in range(10):
            band(d, (40, 60, 100), rnd.randint(30, 70), rnd.uniform(30, 60), rnd.uniform(0, 3), H * (0.1 + k * 0.09))
    img = _multiply(img, _layer(troughs, 25, bg=(255, 255, 255)), 0.5)

    def foam(d):
        for _ in range(160):
            k = rnd.randint(0, 13)
            x = rnd.uniform(0, W)
            y = H * (0.05 + k * 0.07) + rnd.gauss(0, 12) - (W - x) * 0.25 * math.exp(-x / (W * 0.35))
            ln = rnd.uniform(10, 50)
            d.line([(x, y), (x + ln, y + ln * 0.15)], fill=(220, 245, 245), width=1)
    img = _screen(img, _layer(foam, 3), 0.45)
    return _finish(img, path, size)
