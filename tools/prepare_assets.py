# -*- coding: utf-8 -*-
"""One-off: pull the source images out of the archive folders into assets/.

Run again only if the source photographs change. Needs Pillow.
"""
import os, glob, shutil
from PIL import Image, ImageOps, ImageStat, ImageFilter, ImageEnhance

ARCHIVE = "E:/Work/09_IAHR-APD"
WEB = os.path.join(ARCHIVE, "04_Website")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")

for sub in ("logo", "hero", "people", "gallery", "uploads"):
    os.makedirs(os.path.join(ASSETS, sub), exist_ok=True)


def save(im, rel, **kw):
    path = os.path.join(ASSETS, rel)
    im.save(path, **kw)
    print("  %-34s %6d KB" % (rel, os.path.getsize(path) // 1024))


# ---------------------------------------------------------------- logos
print("logos")
src = Image.open(os.path.join(WEB, "logo/logonew.png")).convert("RGBA")
logo = src.resize((600, round(600 * src.height / src.width)), Image.LANCZOS)
save(logo, "logo/iahr-apd.png", optimize=True)

# White knockout that keeps the mark's counters open, for dark grounds.
px, out = logo.load(), Image.new("RGBA", logo.size)
op = out.load()
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b, a = px[x, y]
        op[x, y] = (255, 255, 255, int(a * (1.0 - min(r, g, b) / 255.0)))
save(out, "logo/iahr-apd-white.png", optimize=True)

kict = [f for f in glob.glob(os.path.join(WEB, "logo/*")) if f.endswith("_KICT.png")][0]
k = Image.open(kict).convert("RGBA")
k = k.resize((k.width * 2, k.height * 2), Image.LANCZOS)
kw = Image.new("RGBA", k.size, (255, 255, 255, 0))
kw.putalpha(k.getchannel("A"))
save(kw, "logo/kict-white.png", optimize=True)


# ---------------------------------------------------------------- hero montage
print("hero")
TILES = [("Syr Darya (Central Asia).jpg", .50), ("Wular Lake (India).jpg", .50),
         ("Mekong River (Southeast Asia).jpg", .45), ("Cheonggyecheon (R. O. Korea).jpg", .50),
         ("Kushiro Wetland (Japan).jpg", .45), ("Great Barrier Reef (Australia).jpg", .50)]
TW, TH, GAP, TARGET = 340, 620, 3, 96.0
W = len(TILES) * TW + (len(TILES) - 1) * GAP
canvas = Image.new("RGB", (W, TH), (4, 30, 48))
for i, (fn, cx) in enumerate(TILES):
    im = Image.open(os.path.join(WEB, "gallary", fn)).convert("RGB")
    w, h = im.size
    ar = TW / TH
    cw = int(h * ar)
    if cw > w:
        cw, ch = w, int(w / ar)
    else:
        ch = h
    im = im.crop((int((w - cw) * cx), int((h - ch) * .35),
                  int((w - cw) * cx) + cw, int((h - ch) * .35) + ch))
    im = im.resize((TW, TH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
    g = ImageOps.autocontrast(im.convert("L"), cutoff=2)
    g = ImageEnhance.Brightness(g).enhance(min(1.6, TARGET / max(ImageStat.Stat(g).mean[0], 1)))
    g = ImageEnhance.Contrast(g).enhance(0.86)
    canvas.paste(ImageOps.colorize(g, black=(3, 22, 38), white=(150, 196, 226)), (i * (TW + GAP), 0))
grad = Image.linear_gradient("L").resize((W, TH))
canvas = Image.composite(Image.new("RGB", (W, TH), (3, 20, 34)), canvas,
                         grad.point(lambda v: int((v / 255) ** 2.4 * 190)))
save(canvas, "hero/region.jpg", quality=78, optimize=True, progressive=True)


# ---------------------------------------------------------------- portraits
print("portraits")
EC = os.path.join(WEB, "Committee (2025-2026)")
DOWNLOADED = os.path.join(HERE, "tools", "downloaded")
PEOPLE = [
    ("tanaka", EC + "/1.tanaka.png"), ("sannasiraj", EC + "/2.Sannasj.jpg"),
    ("wonkim", EC + "/13.Wonkim.jpg"), ("paik", DOWNLOADED + "/paik.jpg"),
    ("shamseldin", EC + "/4.Shamseldin.png"), ("intan", EC + "/5.Intan.png"),
    ("haoche", EC + "/6.Hao-che.jpg"), ("mingfu", EC + "/7.Mingfu.jpg"),
    ("chunkiat", EC + "/8.ChunKiat.jpg"), ("huuloc", EC + "/9.Huu Loc.png"),
    ("liu", EC + "/10.Liu Yongfeng.jpg"), ("er", EC + "/new_Er.jpg"),
    ("qian", EC + "/new_Qian.jpg"), ("zhu", DOWNLOADED + "/zhu.jpg"),
    ("choi", DOWNLOADED + "/choi.jpg"),
    ("adrian", os.path.join(WEB, "JHER/adrian.jpg")),
]
for key, path in PEOPLE:
    im = ImageOps.exif_transpose(Image.open(path).convert("RGB"))
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, int((h - s) * .12), (w - s) // 2 + s, int((h - s) * .12) + s))
    im = ImageOps.autocontrast(im.resize((420, 420), Image.LANCZOS), cutoff=1)
    im = ImageEnhance.Color(im).enhance(0.96)
    save(im, "people/%s.jpg" % key, quality=82, optimize=True, progressive=True)


# ---------------------------------------------------------------- gallery, full + thumb
print("gallery")
PICKS = [
    ("2026-incheon-01", "02_Executive Committee Meetings/20260700 EC meeting (Incheon, Korea)/Photo", 0),
    ("2026-incheon-02", "02_Executive Committee Meetings/20260700 EC meeting (Incheon, Korea)/Photo", 9),
    ("2026-incheon-03", "02_Executive Committee Meetings/20260700 EC meeting (Incheon, Korea)/Photo", 18),
    ("2026-incheon-04", "02_Executive Committee Meetings/20260700 EC meeting (Incheon, Korea)/Photo", 63),
    ("2026-incheon-05", "02_Executive Committee Meetings/20260700 EC meeting (Incheon, Korea)/Photo", 90),
    ("2026-incheon-06", "02_Executive Committee Meetings/20260700 EC meeting (Incheon, Korea)/Photo", 99),
    ("2025-singapore-01", "02_Executive Committee Meetings/20250630 EC meeting (Singapore, Singapore)/Photos", 4),
    ("2025-singapore-02", "02_Executive Committee Meetings/20250630 EC meeting (Singapore, Singapore)/Photos", 8),
    ("2025-singapore-03", "02_Executive Committee Meetings/20250630 EC meeting (Singapore, Singapore)/Photos", 44),
    ("2019-panama-01", "02_Executive Committee Meetings/20190903 EC meeting (Panamacity, Panama)/Photo", 0),
    ("2019-panama-02", "02_Executive Committee Meetings/20190903 EC meeting (Panamacity, Panama)/Photo", 99),
    ("2018-yogyakarta-01", "03_Regional Congress/21st (2018, Yogyakarta, Indonesia)/Photos-ExCoMeeting/Photos-ExCoMeeting", 1),
    ("2018-yogyakarta-02", "03_Regional Congress/21st (2018, Yogyakarta, Indonesia)/Photos-ExCoMeeting/Photos-ExCoMeeting", 6),
    ("2018-yogyakarta-03", "03_Regional Congress/21st (2018, Yogyakarta, Indonesia)/Photos-TechnicalVisit1/Photos-TechnicalVisit1", 9),
    ("2018-yogyakarta-04", "03_Regional Congress/21st (2018, Yogyakarta, Indonesia)/Photos-TechnicalVisit1/Photos-TechnicalVisit1", 10),
]
for key, rel, idx in PICKS:
    files = sorted(f for f in glob.glob(os.path.join(ARCHIVE, rel, "*"))
                   if f.lower().endswith((".jpg", ".jpeg", ".png")))
    im = ImageOps.exif_transpose(Image.open(files[idx]).convert("RGB"))
    w, h = im.size
    ar = 7 / 5
    cw = int(h * ar)
    if cw > w:
        cw, ch = w, int(w / ar)
    else:
        ch = h
    im = im.crop(((w - cw) // 2, int((h - ch) * .4), (w - cw) // 2 + cw, int((h - ch) * .4) + ch))
    full = ImageOps.autocontrast(im.resize((1540, 1100), Image.LANCZOS), cutoff=1)
    save(full, "gallery/%s.jpg" % key, quality=76, optimize=True, progressive=True)
    save(full.resize((640, 457), Image.LANCZOS), "gallery/%s-thumb.jpg" % key,
         quality=74, optimize=True, progressive=True)

print("\ndone")
