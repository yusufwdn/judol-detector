# -*- coding: utf-8 -*-
"""Buat salinan proyek yang bersih untuk diserahkan atau di-ZIP.

Repositori kerja memuat sejumlah berkas yang tidak semestinya ikut diserahkan:
kredensial, lingkungan virtual yang berukuran besar, cache, catatan kerja
internal, serta berkas konfigurasi perkakas bantu. Skrip ini menyalin proyek
ke folder terpisah tanpa berkas-berkas tersebut, sehingga folder kerja
tetap utuh dan tidak ada yang perlu dihapus permanen.

Jalankan:  python make_submission_copy.py
Hasil   :  ../svm-judol-spam-submission/
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(os.path.dirname(HERE), "svm-judol-spam-submission")

# Folder yang tidak disertakan, beserta alasannya.
SKIP_DIRS = {
    ".git": "riwayat versi, tidak diperlukan penerima",
    ".claude": "konfigurasi perkakas bantu pengembangan",
    ".docs": "catatan kerja internal (review, revisi, pedoman)",
    ".arsip-dokumentasi-lama": "dokumentasi versi lama",
    "BELAJAR": "catatan belajar pribadi",
    "env": "lingkungan virtual Python, dibuat ulang dari requirements.txt",
    "venv": "lingkungan virtual Python",
    "__pycache__": "cache bytecode Python",
    ".ipynb_checkpoints": "cache Jupyter",
    "dist": "hasil build ekstensi, dibuat ulang bila perlu",
    "node_modules": "dependensi Node, dibuat ulang dari package.json",
}

# Berkas yang tidak disertakan.
SKIP_FILES = {
    ".env": "berisi kredensial (kunci API)",
    "notes": "catatan sementara",
    "repomix.config.json": "konfigurasi perkakas bantu",
    "make_submission_copy.py": "skrip ini sendiri",
}

SKIP_EXT = {".pyc", ".pyo"}


def ignore(folder, names):
    buang = []
    for n in names:
        penuh = os.path.join(folder, n)
        if os.path.isdir(penuh):
            if n in SKIP_DIRS:
                buang.append(n)
        else:
            if n in SKIP_FILES or os.path.splitext(n)[1] in SKIP_EXT:
                buang.append(n)
    return buang


if os.path.exists(DEST):
    shutil.rmtree(DEST)
shutil.copytree(HERE, DEST, ignore=ignore)

# Ringkasan
n_berkas = sum(len(f) for _, _, f in os.walk(DEST))
ukuran = sum(
    os.path.getsize(os.path.join(r, f))
    for r, _, fs in os.walk(DEST) for f in fs
)

print("Salinan bersih dibuat:\n  %s\n" % DEST)
print("  %d berkas, %.1f MB\n" % (n_berkas, ukuran / 1024 / 1024))
print("Tidak disertakan:")
for nama, alasan in sorted({**SKIP_DIRS, **SKIP_FILES}.items()):
    ada = os.path.exists(os.path.join(HERE, nama))
    if ada:
        print("  %-26s %s" % (nama, alasan))

print("\nIsi salinan:")
for n in sorted(os.listdir(DEST)):
    tanda = "/" if os.path.isdir(os.path.join(DEST, n)) else ""
    print("  " + n + tanda)
