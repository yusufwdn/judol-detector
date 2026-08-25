# -*- coding: utf-8 -*-
"""Prepare the Chrome Web Store dashboard capture for use as a thesis figure.

Two changes to the raw capture:

  1. Crop away the empty area below the item row. Roughly 60% of the raw
     grab is blank white space; left in, the figure would occupy a large
     part of a printed page while showing almost nothing.
  2. Blur the publisher email in the top-right corner. The thesis already
     names its author on the cover, so the email adds no evidential value,
     and a bound thesis can end up in a repository that is read far more
     widely than the examination itself.

Everything the figure needs to prove stays untouched: extension name,
version, creation and update dates, and the review status.

Run:  python build_thesis_figure.py
Out:  thesis-ready/dashboard-submit.png
"""
import os

from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw", "6-dashboard-submit.png")
OUT_DIR = os.path.join(HERE, "thesis-ready")

CONTENT = (0, 0, 1919, 310)      # header + item row, without the blank tail
EMAIL = (1500, 12, 1800, 52)     # "Penayang: <alamat surel>"

os.makedirs(OUT_DIR, exist_ok=True)

img = Image.open(SRC).convert("RGB")

patch = img.crop(EMAIL).filter(ImageFilter.GaussianBlur(9))
img.paste(patch, EMAIL[:2])

img = img.crop(CONTENT)
dest = os.path.join(OUT_DIR, "dashboard-submit.png")
img.save(dest, "PNG", optimize=True)

print("tersimpan: %s  (%dx%d)" % (dest, img.width, img.height))
