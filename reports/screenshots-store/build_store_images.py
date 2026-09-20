# -*- coding: utf-8 -*-
"""Build the Chrome Web Store screenshots (1280x800) from the raw captures.

The raw captures are full-screen 1919x1038 grabs. Uploading them as-is has
two problems:

  1. About a third of each frame is YouTube's "recommended videos" sidebar.
     It carries other people's faces and channel names into a public store
     listing, and it steals space from the part that demonstrates the
     extension.
  2. Fitting 1919px into a 1280px canvas shrinks everything to ~64%, pushing
     the comment text and the "Spam 100%" badges close to unreadable.

So instead of scaling the raw frames down, each output is composed from two
crops taken out of them: the comment column on the left, and the extension
popup lifted out and placed on the right. Nothing from the sidebar survives,
and both halves get to sit at a larger effective scale than the whole frame
would have allowed.

Run:  python build_store_images.py
Out:  store-ready/*.png  (each exactly 1280x800)
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 800
BG = (18, 18, 20)
MARGIN = 20

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "store-ready")

# Regions inside the 1919x1038 raw captures.
COMMENTS = (0, 105, 1352, 1038)      # the comment column, minus YouTube's header
POPUP = (1398, 42, 1683, 602)        # the extension popup, minus the strip of
                                     # sidebar thumbnail showing under its edge


def font(size, bold=True):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype("C:/Windows/Fonts/" + name, size)
    except OSError:
        return ImageFont.load_default()


def crop(name, box):
    return Image.open(os.path.join(RAW, name)).convert("RGB").crop(box)


def fit(img, box_w, box_h, max_scale=None):
    s = min(box_w / img.width, box_h / img.height)
    if max_scale:
        s = min(s, max_scale)
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))),
                      Image.LANCZOS)


def save(im, name):
    im.save(os.path.join(OUT, name), "PNG", optimize=True)
    print("  %-34s %dx%d" % (name, im.width, im.height))


def compose(source, out_name):
    """Comment column on the left, extension popup on the right."""
    c = Image.new("RGB", (W, H), BG)

    # Popup first, it sets how much width is left for the comments.
    # Capped at 1.15x so the upscale never turns mushy.
    popup = fit(crop(source, POPUP), 340, H - MARGIN * 2, max_scale=1.15)
    px = W - MARGIN - popup.width
    c.paste(popup, (px, (H - popup.height) // 2))

    comments = fit(crop(source, COMMENTS),
                   px - MARGIN * 2, H - MARGIN * 2)
    c.paste(comments, (MARGIN, (H - comments.height) // 2))

    save(c, out_name)


os.makedirs(OUT, exist_ok=True)
for stale in ("_popup_check.png",):
    p = os.path.join(OUT, stale)
    if os.path.exists(p):
        os.remove(p)

print("Building store screenshots...\n")

# 1. Dim mode, the strongest single image. Shows the control panel and the
#    result of that control in one frame, so it needs no caption to be read.
compose("4-dim-mode.png", "1-detection-in-action.png")

# 2. Before / after, stacked rather than side by side.
#    Side by side forces each full-height column down to ~45% scale, which
#    leaves the comment text too small to read and a third of the canvas
#    empty. Stacking lets each half keep the full 1280px width, so a short
#    horizontal band of comments survives at ~80% instead.
#
#    Each band is chosen to contain the same two spam comments in both
#    captures. They cannot be identical crops: the two raws come from
#    separate page loads and YouTube reorders comments between them.
BANDS = {
    "1-before.png": (0, 620, 1352, 1038),
    "2-after.png": (0, 560, 1352, 978),
}
c = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(c)
label_h = 34
row_h = (H - MARGIN * 3 - label_h * 2) // 2
for i, (fname, label, colour) in enumerate([
    ("1-before.png", "SEBELUM", (229, 115, 115)),
    ("2-after.png", "SESUDAH", (129, 199, 132)),
]):
    img = fit(crop(fname, BANDS[fname]), W - MARGIN * 2, row_h)
    top = MARGIN + i * (label_h + row_h + MARGIN)
    d.text((MARGIN + 4, top + label_h // 2), label,
           font=font(24), fill=colour, anchor="lm")
    c.paste(img, ((W - img.width) // 2, top + label_h))
save(c, "2-before-after.png")

# 3. Hide mode, same framing as image 1 so the pair reads as one set.
compose("5-hide-mode.png", "3-hide-mode.png")

print("\nDone. Upload the files in store-ready/ in filename order.")
