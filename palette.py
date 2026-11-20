"""Snow Leopard (Mac OS X 10.6) palette, shared by every generator."""

WINDOW_BG = "#EDEDED"
BASE = "#FFFFFF"
ALT_BASE = "#EDF3FE"
BUTTON_BG = "#F4F4F4"
TEXT = "#000000"
SELECTION = "#3875D7"
SELECTION_TEXT = "#FFFFFF"
LINK = "#0E4CB3"
LINK_VISITED = "#551A8B"
TOOLTIP_BG = "#FFFFC7"
FOCUS = "#6E9BDB"

# Unified title bar + toolbar: one continuous ramp from title top to toolbar bottom.
TITLE_TOP = "#E9E9E9"
TITLE_BOTTOM = "#D3D3D3"   # == toolbar top
TOOLBAR_BOTTOM = "#A9A9A9"
TOOLBAR_LINE = "#565656"
TITLE_INACTIVE_TOP = "#F6F6F6"
TITLE_INACTIVE_BOTTOM = "#E7E7E7"
TITLE_TEXT = "#2B2B2B"
TITLE_TEXT_INACTIVE = "#8E8E8E"

# Aqua control gloss: (border_top, border_bottom, [(offset, color), ...])
WHITE_GLOSS = ("#9C9C9C", "#7A7A7A",
               [(0, "#FFFFFF"), (0.5, "#F3F3F3"), (0.5, "#E6E6E6"), (1, "#FCFCFC")])
WHITE_HOVER = ("#7F7F7F", "#626262",
               [(0, "#FFFFFF"), (0.5, "#F7F7F7"), (0.5, "#EBEBEB"), (1, "#FFFFFF")])
BLUE_GLOSS = ("#5A7DB3", "#34599A",
              [(0, "#DCEBFB"), (0.5, "#A8CCF3"), (0.5, "#82B6EF"), (1, "#CCE7FF")])
BLUE_PRESSED = ("#3F5F94", "#264578",
                [(0, "#B1CCEE"), (0.5, "#7BA6DD"), (0.5, "#568AD2"), (1, "#97C3F4")])
GRAPHITE_GLOSS = ("#858585", "#5E5E5E",
                  [(0, "#E4E4E4"), (0.5, "#C9C9C9"), (0.5, "#B6B6B6"), (1, "#D9D9D9")])
DISABLED_GLOSS = ("#C6C6C6", "#B6B6B6",
                  [(0, "#FDFDFD"), (1, "#F1F1F1")])

# Menu highlight (Snow Leopard blue menu selection)
MENU_SEL = [(0, "#6587F1"), (1, "#2B57E0")]
MENU_SEL_TOP = "#5577E5"
LIST_SEL = [(0, "#6E9DDF"), (1, "#3E73CA")]
LIST_SEL_TOP = "#5B8AD1"
LIST_SEL_INACTIVE = [(0, "#C4C4C4"), (1, "#A9A9A9")]

# Traffic lights: (rim, base_top, base_bottom, glow, glyph)
TL_CLOSE = ("#9B2A22", "#B8271C", "#F2867C", "#FFD3CC", "#4D0000")
TL_MIN = ("#A8781A", "#C88A0E", "#FBD86A", "#FFF2C4", "#5A3A00")
TL_MAX = ("#3F7E25", "#4F9A2B", "#A6E37A", "#E4FFD0", "#0B4400")
TL_OFF = ("#8D8D8D", "#A9A9A9", "#E3E3E3", "#FAFAFA", "#555555")

# Per-version style switches, filled in by versions.py (empty = Snow Leopard look).
#   window_tile: (data-uri, w, h, average colour) texture behind windows (pinstripes, brushed metal)
#   title_tile:  same for the title bar; toolbar: "unified" | "textured"
#   scroll: "jelly" | "overlay"; menubar: "translucent" | "pinstripe" | "gloss" | "lion" | "mavericks"
#   dock: "shelf" | "flat" | "flat-pinstripe" | "mavericks"; indicator: "glow" | "triangle" | "dot"
STYLE = {}
