"""Color scheme, wallpaper, splash screen and global-theme (look-and-feel) package."""
import json
import math
import random
from PIL import Image, ImageDraw, ImageFilter
import palette as P


def rgb(c):
    return ",".join(str(int(c[i:i + 2], 16)) for i in (1, 3, 5))


def colors(name="Snow Leopard"):
    def sec(title, bg, alt, fg, inactive="#6E6E6E", hover=P.FOCUS, focus=P.FOCUS):
        return f"""[{title}]
BackgroundAlternate={rgb(alt)}
BackgroundNormal={rgb(bg)}
DecorationFocus={rgb(focus)}
DecorationHover={rgb(hover)}
ForegroundActive=0,87,174
ForegroundInactive={rgb(inactive)}
ForegroundLink={rgb(P.LINK)}
ForegroundNegative=191,3,3
ForegroundNeutral=176,128,0
ForegroundNormal={rgb(fg)}
ForegroundPositive=0,110,40
ForegroundVisited={rgb(P.LINK_VISITED)}
"""
    return f"""[ColorEffects:Disabled]
Color=56,56,56
ColorAmount=0
ColorEffect=0
ContrastAmount=0.55
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

{sec("Colors:Button", P.BUTTON_BG, "#E4E4E4", P.TEXT)}
{sec("Colors:Complementary", "#2E2E2E", "#3A3A3A", "#F0F0F0", "#A0A0A0")}
{sec("Colors:Header", "#D6D6D6", "#CFCFCF", P.TEXT)}
{sec("Colors:Header][Inactive", "#ECECEC", "#E4E4E4", "#606060")}
{sec("Colors:Selection", P.SELECTION, "#2E64C0", P.SELECTION_TEXT, "#DDE8FA")}
{sec("Colors:Tooltip", P.TOOLTIP_BG, "#F7F7B8", P.TEXT)}
{sec("Colors:View", P.BASE, P.ALT_BASE, P.TEXT)}
{sec("Colors:Window", P.WINDOW_BG, "#E4E4E4", P.TEXT)}
[General]
ColorScheme=SnowLeopard
Name={name}
accentActiveTitlebar=false
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground={rgb(P.TITLE_BOTTOM)}
activeBlend={rgb(P.TITLE_TOP)}
activeForeground={rgb(P.TITLE_TEXT)}
inactiveBackground={rgb(P.TITLE_INACTIVE_BOTTOM)}
inactiveBlend={rgb(P.TITLE_INACTIVE_TOP)}
inactiveForeground={rgb(P.TITLE_TEXT_INACTIVE)}
"""


WALLPAPERS = {
    # id: (name, background tint (r, g, b) weights, cloud colours, ribbon colours wide/mid/core, seed)
    "SnowLeopardAurora": ("Snow Leopard Aurora", (1.0, 1.0, 1.0),
                          [(150, 50, 190), (110, 40, 170), (190, 60, 170), (70, 60, 190), (40, 80, 200)],
                          ((120, 70, 220), (230, 140, 255), (255, 230, 255)), 106),
    "SnowLeopardGalaxy": ("Snow Leopard Galaxy", (0.35, 0.8, 1.25),
                          [(40, 70, 190), (30, 110, 200), (70, 50, 170), (20, 60, 150), (60, 140, 220)],
                          ((60, 110, 230), (140, 200, 255), (235, 248, 255)), 105),
    "SnowLeopardGraphite": ("Snow Leopard Graphite", (0.75, 0.8, 0.95),
                            [(90, 95, 110), (70, 75, 90), (110, 115, 130), (60, 70, 95), (100, 110, 140)],
                            ((120, 130, 160), (200, 210, 230), (250, 252, 255)), 104),
}


def wallpaper(path, size=(3840, 2160), seed=106, tint=(1.0, 1.0, 1.0), cloud_cols=None, ribbon_cols=None):
    """An original 'aurora in deep space' picture in the spirit of the 10.6 default wallpaper."""
    rnd = random.Random(seed)
    W, H = 1280, 720
    img = Image.new("RGB", (W, H))
    px = img.load()
    for yy in range(H):
        for xx in range(W):
            t = yy / H
            d = math.hypot((xx - W * 0.62) / W, (yy - H * 0.42) / H)
            r = int(14 + 40 * (1 - t) * 0.5 + 30 * max(0, 0.6 - d))
            g = int(8 + 10 * (1 - t) * 0.5 + 12 * max(0, 0.6 - d))
            b = int(38 + 70 * (1 - t) * 0.6 + 70 * max(0, 0.6 - d))
            px[xx, yy] = (min(255, int(r * tint[0])), min(255, int(g * tint[1])), min(255, int(b * tint[2])))

    def glow(layer_cb, blur, opacity):
        nonlocal img
        lay = Image.new("RGB", (W, H), (0, 0, 0))
        layer_cb(ImageDraw.Draw(lay))
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
        img = _screen(img, lay, opacity)

    # large purple / magenta clouds
    def clouds(d):
        for _ in range(26):
            cx, cy = rnd.uniform(0.1, 1.0) * W, rnd.uniform(0.0, 0.85) * H
            rx, ry = rnd.uniform(80, 260), rnd.uniform(50, 160)
            col = rnd.choice(cloud_cols)
            d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
    glow(clouds, 90, 0.55)

    # the bright aurora ribbon sweeping from lower left to upper right
    def ribbon(d, width, col, jitter):
        pts = []
        for i in range(0, 241):
            u = i / 240
            x = -0.05 * W + u * 1.15 * W
            y = H * (0.88 - 0.62 * u + 0.16 * math.sin(u * 3.4 + 0.6)) + rnd.uniform(-jitter, jitter)
            pts.append((x, y))
        d.line(pts, fill=col, width=width, joint="curve")
    wide, mid, core = ribbon_cols
    glow(lambda d: ribbon(d, 120, wide, 0), 60, 0.65)
    glow(lambda d: ribbon(d, 46, mid, 2), 22, 0.75)
    glow(lambda d: ribbon(d, 12, core, 1), 6, 0.9)

    # fine streaks around the ribbon
    def streaks(d):
        for _ in range(140):
            u = rnd.random()
            x = -0.05 * W + u * 1.15 * W
            y = H * (0.88 - 0.62 * u + 0.16 * math.sin(u * 3.4 + 0.6)) + rnd.gauss(0, 40)
            ang = -0.65 + rnd.gauss(0, 0.12)
            ln = rnd.uniform(30, 160)
            d.line([(x, y), (x + ln * math.cos(ang), y + ln * math.sin(ang))],
                   fill=rnd.choice([mid, core, (255, 255, 255)]), width=1)
    glow(streaks, 2, 0.6)

    img = img.resize(size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
    d = ImageDraw.Draw(img)
    for _ in range(1400):
        x, y = rnd.uniform(0, size[0]), rnd.uniform(0, size[1])
        v = int(rnd.uniform(120, 255))
        r = rnd.choice([0.6, 0.8, 1.0, 1.0, 1.4, 2.0])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(v, v, min(255, v + 20)))
    img.save(path, quality=93)
    return img


def _screen(base, top, opacity):
    from PIL import ImageChops
    scr = ImageChops.screen(base, top)
    return Image.blend(base, scr, opacity)


def wallpaper_meta(wid, name):
    return json.dumps({"KPlugin": {"Authors": [{"Name": "Snow Leopard Plasma"}], "Id": wid,
                                   "License": "CC0-1.0", "Name": name}}, indent=4)

LNF_ID = "org.snowleopard.desktop"

LNF_META = json.dumps({
    "KPackageStructure": "Plasma/LookAndFeel",
    "KPlugin": {
        "Authors": [{"Name": "Snow Leopard Plasma"}],
        "Category": "",
        "Description": "Mac OS X 10.6 Snow Leopard: unified grey windows, Aqua controls, menu bar and glass dock",
        "Id": LNF_ID,
        "License": "GPL",
        "Name": "Snow Leopard",
        "Version": "1.0",
    },
    "X-Plasma-APIVersion": "2",
    "X-Plasma-MainScript": "defaults",
}, indent=4)


def lnf_defaults(widget_style="kvantum"):
    return f"""[kdeglobals][KDE]
widgetStyle={widget_style}

[kdeglobals][General]
ColorScheme=SnowLeopard

[kdeglobals][Icons]
Theme=oxygen

[plasmarc][Theme]
name=SnowLeopard

[Wallpaper]
Image=SnowLeopardAurora

[kcminputrc][Mouse]
cursorTheme=Oxygen_Black

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae
theme=__aurorae__svg__SnowLeopard

[ksplashrc][KSplash]
Theme={LNF_ID}
"""


LAYOUT_JS = """// Snow Leopard layout: menu bar on top, centred glass dock at the bottom.
var menubar = new Panel;
menubar.location = "top";
menubar.height = 24;
menubar.hiding = "none";
menubar.floating = false;
var launcher = menubar.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "start-here");
menubar.addWidget("org.kde.plasma.appmenu");
menubar.addWidget("org.kde.plasma.panelspacer");
menubar.addWidget("org.kde.plasma.systemtray");
var clock = menubar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", true);
clock.writeConfig("dateDisplayFormat", "BesideTime");
clock.writeConfig("dateFormat", "custom");
clock.writeConfig("customDateFormat", "ddd");

var dock = new Panel;
dock.location = "bottom";
dock.height = 64;
dock.hiding = "none";
dock.floating = false;
dock.alignment = "center";
dock.lengthMode = "fit";
var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", "applications:org.kde.dolphin.desktop,preferred://browser,applications:org.kde.konsole.desktop,applications:org.kde.kate.desktop,applications:systemsettings.desktop");
tasks.writeConfig("separateLaunchers", false);
tasks.writeConfig("indicateAudioStreams", false);

// Trash sits at the far right, outside the task list, like on the Mac.
var trash = dock.addWidget("org.kde.plasma.icon");
trash.currentConfigGroup = ["General"];
trash.writeConfig("url", "file://" + userDataPath("data", "applications") + "/snowleopard-trash.desktop");

var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = "org.kde.image";
}
"""

# Dock launcher for the trash: the stock trash widget forces a flat symbolic icon in panels.
TRASH_DESKTOP = """[Desktop Entry]
Type=Application
Name=Trash
Name[cs]=Koš
Icon=user-trash
Exec=dolphin trash:/
NoDisplay=true
"""

SPLASH_QML = """import QtQuick

Rectangle {
    id: root
    color: "#CFCFCF"
    property int stage

    Item {
        id: spinner
        width: 34
        height: 34
        anchors.centerIn: parent
        anchors.verticalCenterOffset: 90
        opacity: root.stage >= 1 ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 400 } }

        property int phase: 0
        Timer {
            interval: 80; running: true; repeat: true
            onTriggered: spinner.phase = (spinner.phase + 1) % 12
        }
        Repeater {
            model: 12
            Rectangle {
                width: 3; height: 9; radius: 1.5
                color: "#3C3C3C"
                x: spinner.width / 2 - width / 2
                y: 0
                opacity: 0.15 + 0.85 * (((index - spinner.phase + 12) % 12) / 11)
                transform: Rotation { origin.x: 1.5; origin.y: spinner.height / 2; angle: index * 30 }
            }
        }
    }
}
"""
