# Panduan Screenshot — Chrome Web Store & Naskah Revisi

Alur kerja: **screenshot bebas → simpan ke `raw/` → jalankan skrip → siap unggah.**
Tidak perlu mengatur ukuran secara manual.

```
1. Win+Shift+S  →  seleksi area  →  tempel & simpan ke folder raw/
2. python build_store_images.py
3. hasil 1280x800 ada di folder store-ready/
```

## Dua skrip, beda kegunaan

| Skrip | Kapan dipakai |
|---|---|
| `build_store_images.py` | **Utama.** Menyusun ulang tangkapan layar penuh menjadi tiga gambar toko: memotong sidebar YouTube, mengangkat popup ekstensi, lalu menatanya di kanvas 1280×800. Koordinat potongannya sudah dikunci untuk tangkapan layar 1919×1038. |
| `resize_for_store.py` | **Cadangan.** Sekadar menempatkan gambar apa adanya di kanvas 1280×800 tanpa memotong. Pakai ini kalau menambah gambar baru yang tata letaknya berbeda. |

> Kalau nanti mengambil tangkapan layar ulang dengan resolusi atau tingkat zoom
> berbeda, koordinat di `build_store_images.py` (konstanta `COMMENTS`, `POPUP`,
> dan `BANDS`) perlu disesuaikan.

---

## Persiapan sebelum memotret (5 menit, jangan dilewat)

- [ ] **Buka jendela Chrome baru mode Samaran** (`Ctrl+Shift+N`), lalu izinkan ekstensi
      berjalan di mode Samaran lewat `chrome://extensions` → Details → *Allow in Incognito*.
      Tujuannya: tidak ada foto profil, nama akun, email, atau riwayat yang ikut terpotret.
- [ ] Tutup bookmark bar (`Ctrl+Shift+B`) dan tab-tab lain — tampilan jadi bersih
- [ ] Perbesar tampilan ke **125% atau 150%** (`Ctrl` + `+`). Ini penting: gambar akan
      diperkecil saat ditempatkan di kanvas, jadi teks berukuran normal bisa jadi tidak terbaca
- [ ] Siapkan **satu video** yang kolom komentarnya banyak spam judol, dan **pakai video yang
      sama** untuk semua pengambilan gambar

**Cara menemukan video yang tepat:** buka video Indonesia bertrafik tinggi — musik yang sedang
tren, rekaman siaran langsung, atau konten gaming. Spam judol menumpuk di video semacam itu.
Urutkan komentar berdasarkan **"Terbaru"** (bukan "Teratas") karena spam biasanya baru dan
belum tenggelam oleh komentar populer.

---

## Screenshot 1 — Perbandingan sebelum & sesudah ⭐ paling penting

**Kapan dipotret:** dua kali, pada video dan posisi gulir yang sama.

### Bagian "sebelum"
1. Buka `chrome://extensions` → **matikan** sakelar Judol Spam Detector
2. Kembali ke video → tekan `F5` untuk muat ulang
3. Gulir ke kolom komentar, tunggu komentar termuat
4. Gulir sampai terlihat **beberapa komentar spam judol sekaligus** dalam satu layar
5. 📸 Potret area kolom komentarnya saja (tidak perlu seluruh layar)

### Bagian "sesudah"
1. `chrome://extensions` → **nyalakan** lagi
2. Kembali ke video → `F5`
3. Gulir ke posisi **yang sama** seperti tadi
4. **Tunggu 3–5 detik** — ekstensi memindai secara berkelompok, komentar tidak langsung
   tersaring begitu halaman terbuka
5. 📸 Potret area yang sama

### Menggabungkan
Tidak perlu manual. Simpan kedua tangkapan layar apa adanya sebagai `1-before.png`
dan `2-after.png`, lalu `build_store_images.py` yang menyusunnya jadi satu gambar
bertumpuk lengkap dengan label "SEBELUM"/"SESUDAH".

> Inilah gambar yang paling menjelaskan. Calon pengguna dan penguji sama-sama langsung
> paham hanya dengan melihatnya.

---

## Screenshot 2 — Popup ekstensi

**Kapan dipotret:** setelah ekstensi sempat bekerja, **jangan** langsung setelah halaman dibuka.

1. Buka video, gulir kolom komentar **agak jauh ke bawah** supaya banyak komentar termuat
   dan terpindai (penghitung baru akan menunjukkan angka besar)
2. Tunggu sampai proses pemindaian tenang
3. Klik ikon ekstensi di toolbar
4. 📸 Potret popup **beserta sedikit halaman YouTube di belakangnya** — konteksnya membantu

**Pastikan terlihat dalam satu gambar:**
- [ ] Penghitung komentar tersaring **menunjukkan angka nyata, bukan 0**
- [ ] Slider ambang keyakinan
- [ ] Pilihan mode (Redupkan / Hilangkan)
- [ ] Indikator status server dalam keadaan terhubung

> ⚠️ **DevTools tidak bisa memotret popup.** Popup adalah bagian antarmuka peramban,
> bukan isi halaman, sehingga `Capture screenshot` di DevTools tidak menjangkaunya.
> Gunakan `Win+Shift+S`.

---

## Screenshot 3 — Mode Redupkan dari dekat

**Kapan dipotret:** saat ada komentar yang sedang diredupkan beserta badge-nya.

1. Di popup, pilih mode **"Redupkan"**
2. Muat ulang halaman, tunggu penyaringan selesai
3. Cari satu komentar yang diredupkan dan badge-nya terlihat jelas
4. Perbesar ke **150%** kalau perlu
5. 📸 Potret dari dekat — cukup satu sampai dua komentar saja, tidak usah seluruh kolom

> Gambar ini menjawab pertanyaan "bagaimana kalau sistemnya salah deteksi?" —
> menunjukkan komentar tidak dihapus paksa, pengguna tetap bisa membukanya.

---

## Penamaan berkas

Urutan tampil di halaman toko mengikuti urutan nama berkas, jadi awali dengan angka.
Susunan yang dipakai sekarang:

```
raw/                          (tangkapan layar apa adanya)
  1-before.png                ekstensi mati
  2-after.png                 ekstensi menyala
  3-popup.png                 popup dipotong sendiri
  4-dim-mode.png              popup + komentar diredupkan
  5-hide-mode.png             popup + komentar dihilangkan
  6-dashboard-submit.png      bukti submission (untuk naskah)

store-ready/                  (hasil skrip, siap unggah)
  1-detection-in-action.png
  2-before-after.png
  3-hide-mode.png
```

Nama berkas di `raw/` dirujuk langsung oleh `build_store_images.py`,
jadi jangan diubah tanpa menyesuaikan skripnya.

---

## Simpan yang mentah

**Jangan hapus isi folder `raw/`.** Gambar yang sama dipakai dua kali:

| Keperluan | Versi yang dipakai |
|---|---|
| Halaman Chrome Web Store | `store-ready/` (1280×800) |
| Gambar di naskah revisi (Bab IV) | `raw/` (resolusi asli, lebih tajam saat dicetak) |

Untuk naskah, gambar mentah (folder `raw/`) lebih baik karena tidak ada ruang kosong di sisi kiri-kanan
dan resolusinya penuh.

---

## Sekalian: screenshot bukti submission

Setelah menekan *Submit for review*, potret juga halaman dashboard-nya dan simpan sebagai:

```
raw/6-dashboard-submit.png
```

Harus terlihat: nama ekstensi, **Item ID**, **status**, dan tanggal.
Gambar ini tidak diunggah ke toko — khusus untuk bukti di naskah (revisi R6).
