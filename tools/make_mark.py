# -*- coding: utf-8 -*-
"""Generate the Division's own square mark and the site icons.

The mark is typographic on purpose. The parent association's logo is a
wireframe globe in a blue box; at avatar size a second globe would be
indistinguishable from it, so the Division's mark names both bodies instead and
shares only the brand blue and the white line work.

    python tools/make_mark.py

Needs Pillow and a heavy grotesque. Arial Black is used when present; the
generated PNGs are committed, so this only needs re-running if the mark changes.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(HERE, "assets", "logo")
STATIC = os.path.join(HERE, "static")
os.makedirs(LOGO, exist_ok=True)

S, SS = 1000, 4
W = S * SS
BLUE = (0, 128, 192)
WHITE = (255, 255, 255)

FONTS = ["C:/Windows/Fonts/ariblk.ttf", "/Library/Fonts/Arial Black.ttf",
         "/usr/share/fonts/truetype/msttcorefonts/Arial_Black.ttf"]
FONT_PATH = next((f for f in FONTS if os.path.exists(f)), None)
if not FONT_PATH:
    raise SystemExit("No heavy grotesque found. Install Arial Black or edit FONTS.")


def font(px):
    return ImageFont.truetype(FONT_PATH, int(px))


def widths(d, text, f):
    return [d.textbbox((0, 0), ch, font=f)[2] - d.textbbox((0, 0), ch, font=f)[0] for ch in text]


def tracked_width(d, text, f, tracking):
    w = widths(d, text, f)
    return sum(w) + tracking * (len(text) - 1)


def draw_tracked(d, text, f, y, tracking, canvas_w, colour=WHITE):
    total = tracked_width(d, text, f, tracking)
    x = (canvas_w - total) / 2
    for ch, cw in zip(text, widths(d, text, f)):
        box = d.textbbox((0, 0), ch, font=f)
        d.text((x - box[0], y), ch, font=f, fill=colour)
        x += cw + tracking


def fit_tracking(d, text, f, target_w):
    if len(text) < 2:
        return 0
    return max(0, (target_w - tracked_width(d, text, f, 0)) / (len(text) - 1))


def wave(d, cx, cy, width, amp, w, colour=WHITE):
    pts = [(cx - width / 2 + width * (i / 160.0),
            cy - math.sin(i / 160.0 * 2 * math.pi) * amp) for i in range(161)]
    d.line(pts, fill=colour, width=int(w), joint="curve")


def full_mark(size):
    """IAHR over a wave over APD."""
    w = size * SS
    img = Image.new("RGB", (w, w), BLUE)
    d = ImageDraw.Draw(img)
    f_top, f_bot = font(w * 0.225), font(w * 0.335)
    bottom = tracked_width(d, "APD", f_bot, 0)
    draw_tracked(d, "IAHR", f_top, int(w * 0.185), fit_tracking(d, "IAHR", f_top, bottom), w)
    wave(d, w / 2, w * 0.500, bottom, w * 0.030, w * 0.022)
    draw_tracked(d, "APD", f_bot, int(w * 0.560), 0, w)
    return img.resize((size, size), Image.LANCZOS)


def small_mark(size):
    """Below about 40 px the two lines collapse, so the icon drops to APD alone."""
    w = size * SS
    img = Image.new("RGB", (w, w), BLUE)
    d = ImageDraw.Draw(img)
    f = font(w * 0.40)
    box = d.textbbox((0, 0), "APD", font=f)
    d.text(((w - (box[2] - box[0])) / 2 - box[0], (w - (box[3] - box[1])) / 2 - box[1]),
           "APD", font=f, fill=WHITE)
    return img.resize((size, size), Image.LANCZOS)


mark = full_mark(S)
mark.save(os.path.join(LOGO, "apd-mark.png"))
print("  assets/logo/apd-mark.png            1000 x 1000")

mark.resize((180, 180), Image.LANCZOS).save(os.path.join(STATIC, "apple-touch-icon.png"))
print("  static/apple-touch-icon.png          180 x 180")

# A multi-size .ico: the plain APD at the sizes where the stacked mark turns to mud.
frames = [small_mark(16), small_mark(32), full_mark(48), full_mark(64),
          full_mark(128), full_mark(256)]
frames[-1].save(os.path.join(STATIC, "favicon.ico"), format="ICO",
                sizes=[(f.width, f.height) for f in frames], append_images=frames[:-1])
print("  static/favicon.ico                   16, 32, 48, 64, 128, 256")
print("\ndone")
