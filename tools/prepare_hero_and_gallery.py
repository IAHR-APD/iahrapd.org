# -*- coding: utf-8 -*-
"""Rebuild the home-page hero slides and the wide gallery crops.

Hero slides stay in natural colour and are only lightly darkened, so the rivers
are clearly readable behind the headline. Legibility comes from a gradient
drawn in CSS over the left of the image, not from flattening the photograph.
"""
import glob
import json
import os

from PIL import Image, ImageEnhance, ImageOps

ARCHIVE = "E:/Work/09_IAHR-APD"
GALLARY = os.path.join(ARCHIVE, "04_Website", "gallary")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")
os.makedirs(os.path.join(ASSETS, "hero"), exist_ok=True)


def save(im, rel, **kw):
    path = os.path.join(ASSETS, rel)
    im.save(path, **kw)
    print("  %-40s %5d KB" % (rel, os.path.getsize(path) // 1024))


# ---------------------------------------------------------------- hero slides
# (file, caption, horizontal crop centre)
SLIDES = [
    ("Mekong River (Southeast Asia).jpg", "Mekong River", "Southeast Asia", 0.45),
    ("Cheonggyecheon (R. O. Korea).jpg", "Cheonggyecheon", "Seoul, Republic of Korea", 0.50),
    ("Kushiro Wetland (Japan).jpg", "Kushiro Wetland", "Hokkaido, Japan", 0.45),
    ("Syr Darya (Central Asia).jpg", "Syr Darya", "Central Asia", 0.50),
    ("Wular Lake (India).jpg", "Wular Lake", "India", 0.50),
    ("Great Barrier Reef (Australia).jpg", "Great Barrier Reef", "Australia", 0.50),
]

W, H = 1800, 760          # wide banner crop
slides = []
for i, (fn, place, region, cx) in enumerate(SLIDES, start=1):
    im = ImageOps.exif_transpose(Image.open(os.path.join(GALLARY, fn)).convert("RGB"))
    w, h = im.size
    ar = W / H
    cw = int(h * ar)
    if cw > w:
        cw, ch = w, int(w / ar)
    else:
        ch = h
    left = int((w - cw) * cx)
    top = int((h - ch) * 0.35)
    im = im.crop((left, top, left + cw, top + ch)).resize((W, H), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Color(im).enhance(0.92)
    im = ImageEnhance.Brightness(im).enhance(0.86)     # gentle, not a black-out
    name = "hero/slide-%d.jpg" % i
    save(im, name, quality=76, optimize=True, progressive=True)
    slides.append({"image": "/assets/" + name, "place": place, "region": region})

with open(os.path.join(HERE, "content", "hero.json"), "w", encoding="utf-8") as f:
    json.dump({"interval_seconds": 7, "slides": slides}, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("  content/hero.json")

# ---------------------------------------------------------------- gallery, 16:9
GW, GH = 1600, 900
TW, TH = 720, 405
for full in sorted(glob.glob(os.path.join(ASSETS, "gallery", "*.jpg"))):
    if full.endswith("-thumb.jpg"):
        continue
    key = os.path.splitext(os.path.basename(full))[0]
    src = Image.open(full).convert("RGB")
    w, h = src.size
    ar = GW / GH
    cw = int(h * ar)
    if cw > w:
        cw, ch = w, int(w / ar)
    else:
        ch = h
    im = src.crop(((w - cw) // 2, int((h - ch) * 0.45), (w - cw) // 2 + cw, int((h - ch) * 0.45) + ch))
    im = im.resize((GW, GH), Image.LANCZOS)
    save(im, "gallery/%s.jpg" % key, quality=76, optimize=True, progressive=True)
    save(im.resize((TW, TH), Image.LANCZOS), "gallery/%s-thumb.jpg" % key,
         quality=74, optimize=True, progressive=True)

print("\ndone")
