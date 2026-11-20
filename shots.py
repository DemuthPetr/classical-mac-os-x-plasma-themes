"""Render one demo window per theme for the project page (docs/img/).

Runs Qt off-screen with the Kvantum style, then draws the matching Aurorae frame around it.
Needs the themes installed and Kvantum + python-pyqt6.

    python3 shots.py                 # all themes
    python3 shots.py MacOSX-Tiger    # one theme
"""
import configparser
import os
import subprocess
import sys

THEMES = ["MacOSX-Cheetah", "MacOSX-Puma", "MacOSX-Jaguar", "MacOSX-Panther", "MacOSX-Tiger",
          "Mac4Lin", "SnowLeopard", "MacOSX-Lion", "MacOSX-MountainLion", "MacOSX-Mavericks"]
TITLES = {"Mac4Lin": "Leopard", "SnowLeopard": "Snow Leopard", "MacOSX-MountainLion": "Mountain Lion"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "img")
KVCONF = os.path.expanduser("~/.config/Kvantum/kvantum.kvconfig")
AURORAE = os.path.expanduser("~/.local/share/aurorae/themes")


def render(theme):
    from PyQt6.QtCore import QRectF, Qt
    from PyQt6.QtGui import QColor, QFont, QImage, QPainter
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout, QGroupBox,
                                 QHBoxLayout, QLineEdit, QListWidget, QMainWindow, QProgressBar,
                                 QPushButton, QRadioButton, QSlider, QSplitter, QTabWidget,
                                 QToolBar, QVBoxLayout, QWidget)

    app = QApplication(["shots", "-style", "kvantum"])
    app.setFont(QFont("Lucida Grande", 10))

    win = QMainWindow()
    bar = QToolBar()
    bar.setMovable(False)
    for name in ("Back", "Forward", "View", "Action"):
        bar.addAction(name)
    spacer = QWidget()
    spacer.setSizePolicy(spacer.sizePolicy().horizontalPolicy().Expanding,
                         spacer.sizePolicy().verticalPolicy().Preferred)
    bar.addWidget(spacer)
    search = QLineEdit()
    search.setPlaceholderText("Search")
    search.setFixedWidth(150)
    bar.addWidget(search)
    win.addToolBar(bar)

    side = QListWidget()
    side.addItems(["Macintosh HD", "Network", "Desktop", "Documents", "Applications", "Music",
                   "Pictures", "Movies", "Downloads", "Utilities", "Library", "Public"])
    side.setCurrentRow(2)

    tabs = QTabWidget()
    page = QWidget()
    grid = QGridLayout(page)
    box = QGroupBox("Appearance")
    v = QVBoxLayout(box)
    v.addWidget(QRadioButton("Blue", checked=True))
    v.addWidget(QRadioButton("Graphite"))
    v.addWidget(QCheckBox("Show scroll arrows together", checked=True))
    v.addWidget(QCheckBox("Use smooth scrolling"))
    combo = QComboBox()
    combo.addItems(["Lucida Grande", "Helvetica"])
    v.addWidget(combo)
    grid.addWidget(box, 0, 0, 1, 2)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setValue(60)
    grid.addWidget(slider, 1, 0, 1, 2)
    progress = QProgressBar()
    progress.setValue(60)
    progress.setTextVisible(False)
    grid.addWidget(progress, 2, 0, 1, 2)
    buttons = QHBoxLayout()
    buttons.addStretch()
    buttons.addWidget(QPushButton("Cancel"))
    ok = QPushButton("OK")
    ok.setDefault(True)
    buttons.addWidget(ok)
    grid.addLayout(buttons, 3, 0, 1, 2)
    tabs.addTab(page, "General")
    tabs.addTab(QWidget(), "Advanced")

    split = QSplitter()
    split.addWidget(side)
    split.addWidget(tabs)
    split.setSizes([170, 400])
    win.setCentralWidget(split)
    win.resize(600, 380)
    win.show()
    app.processEvents()
    client = win.grab().toImage()

    # Aurorae frame: 9-patch from decoration.svg, padding is the shadow.
    d = os.path.join(AURORAE, theme)
    rc = configparser.ConfigParser(strict=False)
    rc.optionxform = str
    rc.read(os.path.join(d, theme + "rc"))
    L, G = rc["Layout"], rc["General"]
    n = lambda k: int(L.get(k, 0))
    pl, pr, pt, pb = n("PaddingLeft"), n("PaddingRight"), n("PaddingTop"), n("PaddingBottom")
    left, right, bottom = pl + n("BorderLeft"), pr + n("BorderRight"), pb + n("BorderBottom")
    top = pt + n("TitleEdgeTop") + n("TitleHeight") + n("TitleEdgeBottom")
    W, H = client.width() + left + right, client.height() + top + bottom

    img = QImage(W, H, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    deco = QSvgRenderer(os.path.join(d, "decoration.svg"))
    cw, ch = W - left - right, H - top - bottom
    parts = {"topleft": (0, 0, left, top), "top": (left, 0, cw, top), "topright": (W - right, 0, right, top),
             "left": (0, top, left, ch), "center": (left, top, cw, ch), "right": (W - right, top, right, ch),
             "bottomleft": (0, H - bottom, left, bottom), "bottom": (left, H - bottom, cw, bottom),
             "bottomright": (W - right, H - bottom, right, bottom)}
    for name, r in parts.items():
        if deco.elementExists("decoration-" + name):
            deco.render(p, "decoration-" + name, QRectF(*r))
    p.drawImage(left, top, client)

    bw, bh, sp = n("ButtonWidth"), n("ButtonHeight"), n("ButtonSpacing")
    x, y = pl + n("TitleEdgeLeft"), pt + n("TitleEdgeTop") + n("ButtonMarginTop")
    for b in ("close", "minimize", "maximize"):
        btn = QSvgRenderer(os.path.join(d, b + ".svg"))
        btn.render(p, "active-center", QRectF(x, y, bw, bh))
        x += bw + sp
    p.setPen(QColor(*[int(c) for c in G.get("ActiveTextColor", "0,0,0").split(",")]))
    f = QFont("Lucida Grande", 10)
    f.setBold(True)
    p.setFont(f)
    title = "Mac OS X " + TITLES.get(theme, theme.replace("MacOSX-", ""))
    p.drawText(QRectF(left, pt + n("TitleEdgeTop"), cw, n("TitleHeight")), Qt.AlignmentFlag.AlignCenter, title)
    p.end()
    img.save(os.path.join(OUT, theme + ".png"))


def scene(theme):
    """Window on the theme's own generated wallpaper (Leopard gets Graphite: its Aurora is Apple's)."""
    from PIL import Image
    here = os.path.dirname(os.path.abspath(__file__))
    wall = {"SnowLeopard": "build/wallpapers/SnowLeopardAurora",
            "Mac4Lin": "build/wallpapers/SnowLeopardGraphite"}.get(theme, "build-versions/wallpapers/" + theme)
    bg = Image.open(os.path.join(here, wall, "contents/images/3840x2160.jpg")).convert("RGBA").resize((1120, 630))
    win = Image.open(os.path.join(OUT, theme + ".png"))
    bg.alpha_composite(win, ((bg.width - win.width) // 2, (bg.height - win.height) // 2 + 10))
    bg.convert("RGB").save(os.path.join(OUT, theme + "-scene.jpg"), quality=88)


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--one":
        render(sys.argv[2])
        return
    os.makedirs(OUT, exist_ok=True)
    kv = configparser.ConfigParser(strict=False)
    kv.optionxform = str
    kv.read(KVCONF)
    saved = kv.get("General", "theme", fallback=None)
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", QT_SCALE_FACTOR="1", QT_ENABLE_HIGHDPI_SCALING="0")
    try:
        for theme in sys.argv[1:] or THEMES:
            subprocess.run(["kwriteconfig6", "--file", KVCONF, "--group", "General", "--key", "theme", theme], check=True)
            subprocess.run([sys.executable, __file__, "--one", theme], env=env, check=True)
            scene(theme)
            print("wrote", os.path.join(OUT, theme + ".png"), "and -scene.jpg")
    finally:
        if saved:
            subprocess.run(["kwriteconfig6", "--file", KVCONF, "--group", "General", "--key", "theme", saved])


if __name__ == "__main__":
    main()
