# -*- coding: utf-8 -*-
"""Ubah screenshot mentah jadi ukuran persis 1280x800 untuk Chrome Web Store.

Chrome Web Store menolak gambar yang ukurannya tidak persis 1280x800 (atau
640x400). Skrip ini mengambil screenshot apa adanya — ukuran berapa pun,
hasil Win+Shift+S sekalipun — lalu menyusunnya di atas kanvas 1280x800:
gambar diperbesar/diperkecil proporsional (tidak gepeng), diletakkan di
tengah, dan sisa ruangnya diisi warna latar.

CARA PAKAI
----------
1. Simpan screenshot mentah ke folder `mentah/` di sebelah skrip ini.
   Nama bebas, format PNG/JPG. Urutan tampil di toko mengikuti urutan nama,
   jadi awali dengan angka: 1-sebelum-sesudah.png, 2-popup.png, 3-redupkan.png
2. Jalankan:  python buat_ukuran.py
3. Hasil siap unggah ada di folder `siap-unggah/`
"""
import os
import sys

from PIL import Image

W, H = 1280, 800
BG = (24, 24, 27)          # abu gelap netral; ganti ke (255,255,255) kalau mau putih
MARGIN = 24                # jarak minimum gambar ke tepi kanvas

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "mentah")
OUT = os.path.join(HERE, "siap-unggah")


def proses(path, dest):
    img = Image.open(path).convert("RGB")
    ow, oh = img.size

    # skala proporsional agar muat dalam kanvas dikurangi margin
    maxw, maxh = W - MARGIN * 2, H - MARGIN * 2
    skala = min(maxw / ow, maxh / oh)
    nw, nh = max(1, int(ow * skala)), max(1, int(oh * skala))
    img = img.resize((nw, nh), Image.LANCZOS)

    kanvas = Image.new("RGB", (W, H), BG)
    kanvas.paste(img, ((W - nw) // 2, (H - nh) // 2))
    kanvas.save(dest, "PNG", optimize=True)
    return (ow, oh), (nw, nh), skala


def main():
    if not os.path.isdir(SRC):
        os.makedirs(SRC, exist_ok=True)
        print("Folder 'mentah/' baru dibuat. Taruh screenshot di sana lalu "
              "jalankan skrip ini lagi.")
        return 1

    os.makedirs(OUT, exist_ok=True)
    berkas = sorted(
        f for f in os.listdir(SRC)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    )
    if not berkas:
        print("Tidak ada gambar di folder 'mentah/'.")
        return 1

    print("Memproses %d gambar -> 1280x800\n" % len(berkas))
    for f in berkas:
        nama = os.path.splitext(f)[0] + ".png"
        dest = os.path.join(OUT, nama)
        asal, baru, skala = proses(os.path.join(SRC, f), dest)
        catatan = ""
        if skala > 1.6:
            catatan = "  <- screenshot aslinya kecil, hasil bisa buram"
        print("  %-34s %sx%s -> ditempatkan %sx%s%s"
              % (f, asal[0], asal[1], baru[0], baru[1], catatan))

    print("\nSelesai. Berkas siap unggah ada di:\n  %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
