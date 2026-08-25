# Checklist Publikasi Chrome Web Store — Judol Spam Detector

**Disiapkan:** 2026-08-23 · **Target:** submit hari ini/besok (deadline revisi ~1 minggu)
**Paket siap unggah:** `dist/judol-spam-detector-v1.0.0.zip` (24 KB)

---

## Blocker yang ditemukan & sudah diperbaiki

| # | Masalah | Dampak kalau dibiarkan | Status |
|---|---|---|---|
| B1 | `icon16.png` & `icon48.png` sebenarnya file 128×128 hasil copy — ukuran tidak sesuai | Ikon buram/gepeng di toolbar; indikasi kualitas rendah saat review | ✅ Diperbaiki — ikon 16/48/128 asli sudah di-generate |
| B2 | Ikon berupa **kotak merah polos** (442 byte, tanpa desain) | Berisiko dinilai low-quality; buruk juga untuk screenshot Bab IV | ✅ Diperbaiki — ikon baru: gelembung komentar + rambu larangan |
| B3 | `manifest.json` memuat field `"key"` (untuk ID tetap saat dev) | **Google mewajibkan `key` dihapus sebelum unggah**; bisa menyebabkan konflik ID | ✅ Dihapus otomatis di build `dist/store` (file dev tetap utuh) |
| B4 | Belum ada halaman kebijakan privasi | **Wajib** karena ekstensi mengirim teks komentar ke server; tanpa ini pasti ditolak | ✅ Dibuat — `deploy/privacy-policy.html` |
| B5 | Permission `activeTab` dideklarasikan tapi **tidak terpakai** | Permission tak terpakai = penyebab penolakan paling umum | ✅ Dihapus — diverifikasi `popup.js` hanya memakai `tab.id` (baris 71, 93, 113), tidak pernah `tab.url`/`tab.title`, sehingga `activeTab` memang tidak dibutuhkan |

**Verifikasi B5:** `chrome.tabs.query()` tetap mengembalikan `tab.id` tanpa permission apa pun
(yang disembunyikan hanya `url`, `title`, `favIconUrl`), dan `chrome.tabs.sendMessage()` cukup
mengandalkan content script yang sudah ter-inject lewat `content_scripts` + host permission YouTube.
Jadi popup tetap berfungsi normal. **Tetap tes manual sekali** lewat "Load unpacked" sebelum submit.

### Perlu keputusan (belum gua ubah)

| # | Temuan | Rekomendasi |
|---|---|---|
| B6 | `REPORT_TOKEN` ter-hardcode di `content.js:34`. | Aman secara fungsional: `DEV_MODE = false` (`content.js:51`), jadi tombol "Bukan spam?" tidak pernah muncul di produksi dan `/report` tak terpanggil. Tapi token telanjang di kode publik bisa dipertanyakan. Saran: hapus baris token + fungsi `reportFalsePositive` dari build store saja. Prioritas rendah — jangan sampai menunda submit. |

---

## Verifikasi yang sudah dilakukan

```
$ curl https://api-svm.cupsky.my.id/health
HTTP 200 in 0.178s
{"status":"ok","model_loaded":true}
```

Backend produksi **hidup**. `src/server.py` dicek: `/predict` dan `/predict/batch`
**tidak menulis ke disk** — hanya `/report` yang menulis CSV, dan itu tidak
terjangkau dari produksi. Jadi klaim "tidak menyimpan data" di kebijakan privasi
**akurat dan bisa dipertanggungjawabkan**.

---

## Langkah submit

### 0. Sebelum mulai
- [ ] Siapkan akun Google (pakai yang permanen — akun ini jadi pemilik ekstensi)
- [ ] Siapkan kartu buat bayar **USD 5** (sekali seumur hidup, tidak berulang)

### 1. Hosting kebijakan privasi (lakukan pertama — URL-nya dibutuhkan di form)

Disajikan langsung oleh FastAPI lewat route `/privacy` di `src/server.py`.
**Tidak perlu mengubah Nginx** — aplikasi sudah ter-proxy di `location /`.

```bash
# di laptop
git push origin main

# di server
ssh deploy@IP_VPS
cd /home/deploy/svm-judol-spam && git pull origin main
sudo systemctl restart judol-api
curl -I https://api-svm.cupsky.my.id/privacy    # harus 200
```

Langkah rincinya (termasuk jalur `scp` bila server bukan git clone) ada di
[`PANDUAN_LANGKAH_STORE.md`](PANDUAN_LANGKAH_STORE.md) Langkah 1.

**URL kebijakan privasi:** `https://api-svm.cupsky.my.id/privacy`

✅ **SELESAI & TERVERIFIKASI LIVE — 23 Agustus 2026**

```
GET /privacy   -> HTTP 200 | text/html; charset=utf-8 | 5.286 bytes | 95 ms
GET /health    -> {"status":"ok","model_loaded":true}
POST /predict  -> "𝙎𝙇𝙊𝙏 gacor hari ini cuan terus min WD lancar"
                  -> {"label":"spam","confidence":0.992}
POST /predict  -> "videonya bagus banget bang, sangat membantu penjelasannya"
                  -> {"label":"non_spam","confidence":0.9994}
```

Judul halaman, tanggal berlaku, dan email kontak terkonfirmasi tampil.
Restart layanan tidak mengganggu fungsi klasifikasi.

### 2. Daftar developer account
- Buka https://chrome.google.com/webstore/devconsole
- Bayar biaya pendaftaran USD 5
- Lengkapi **Account settings**: nama publisher, email kontak, lalu **verifikasi email**
  (ekstensi tidak bisa dipublikasikan sebelum email terverifikasi — sering terlewat)

### 3. Unggah paket
- Klik **Add new item** → unggah `dist/judol-spam-detector-v1.0.0.zip`

### 4. Isi Store listing

**Name**
```
Judol Spam Detector
```

**Summary** (maks 132 karakter)
```
Deteksi dan sembunyikan komentar spam promosi judi online di YouTube secara otomatis menggunakan machine learning.
```

**Description**
```
Judol Spam Detector menyembunyikan komentar spam promosi judi online di kolom komentar YouTube secara otomatis, langsung saat halaman dibuka.

CARA KERJA
Ekstensi ini menggunakan model machine learning Support Vector Machine (SVM) yang dilatih pada ribuan komentar spam judi online berbahasa Indonesia. Sebelum diklasifikasikan, setiap komentar dinormalisasi terlebih dahulu dengan teknik String Normalization untuk membongkar penyamaran teks yang biasa dipakai spammer.

MENGATASI PENYAMARAN TEKS
Filter berbasis kata kunci biasa mudah dikelabui. Ekstensi ini menangani:
• Karakter Unicode dekoratif (𝙎𝙇𝙊𝙏, 𝕊𝑳𝕆𝑻)
• Penyisipan tanda baca di tengah kata (J.u.d.i)
• Substitusi huruf dengan angka atau leet speak (5L0T, s1tus)
• Karakter mirip dari blok Unicode lain (homoglyph)

FITUR
• Berjalan otomatis di halaman video, livestream, dan Shorts
• Ambang keyakinan yang bisa diatur sendiri (50%–95%, bawaan 75%)
• Dua mode: "Redupkan" (komentar diburamkan, bisa diklik untuk dilihat) atau "Hilangkan" (disembunyikan sepenuhnya)
• Penghitung komentar yang tersaring di setiap tab
• Ringan — pemrosesan dilakukan di server, tidak membebani peramban

PRIVASI
Ekstensi hanya mengirimkan teks komentar untuk diklasifikasikan. Teks diproses di memori dan tidak disimpan. Tidak ada pengumpulan identitas, akun, maupun riwayat penelusuran. Tidak ada iklan dan tidak ada pelacak.

Ekstensi ini dikembangkan sebagai bagian dari penelitian skripsi Teknik Informatika, Institut Teknologi dan Bisnis Swadharma.
```

**Category:** `Productivity`
**Language:** `Bahasa Indonesia`

### 5. Aset grafis yang harus dibuat

| Aset | Ukuran | Wajib? | Cara bikin |
|---|---|---|---|
| Store icon | 128×128 | ✅ Wajib | Pakai `extension/icons/icon128.png` (sudah siap) |
| Screenshot | **1280×800** atau 640×400 | ✅ Wajib min. 1 | Lihat panduan di bawah |
| Small promo tile | 440×280 | Opsional | Lewati saja kalau mepet |

**Panduan screenshot (bikin 3, sekalian buat naskah):**
1. **Sebelum/sesudah** — buka video YouTube dengan banyak spam judol, screenshot kolom komentar saat ekstensi mati lalu saat menyala
2. **Popup** — tampilkan popup dengan slider ambang keyakinan dan penghitung yang jalan
3. **Mode redupkan** — komentar yang diredupkan beserta badge-nya

> Set browser ke 1280×800 biar ukurannya pas tanpa perlu di-crop.
> Screenshot ini **dipakai dua kali**: buat store listing dan buat bukti di naskah revisi.

### 6. Tab "Praktik privasi" — WAJIB, dan tombol Publikasikan terkunci sampai selesai

> Kalau muncul daftar galat *"Tidak dapat publikasikan"*, **semuanya berasal dari tab ini.**
> Formulir tidak memberi tahu di awal bahwa tab ini wajib. Isi kelimanya, lalu **Simpan Draf**.

| Pesan galat | Kolom yang harus diisi |
|---|---|
| Perlu deskripsi satu tujuan | Single purpose / Deskripsi satu tujuan |
| Perlu justifikasi untuk storage | Justifikasi izin `storage` |
| Perlu justifikasi untuk penggunaan izin host | Justifikasi host permission |
| Perlu justifikasi untuk penggunaan kode jarak jauh | Pilihan **kode jarak jauh** (radio button) |
| Harus menyatakan penggunaan data mematuhi Kebijakan | 3 kotak centang sertifikasi di bagian bawah |

#### Kode jarak jauh — pilih "TIDAK"

Pilih: **"Tidak, saya tidak menggunakan kode jarak jauh"**
(*No, I am not using remote code*)

Kalau pilihan ini dipilih, kolom justifikasi tidak perlu diisi dan galatnya hilang.

**Jangan salah pilih "Ya".** Yang dimaksud Google dengan *kode jarak jauh* adalah
JavaScript atau WebAssembly yang **diunduh dari luar paket ekstensi lalu dieksekusi** —
misalnya `eval()` atas string dari server, `new Function()`, `importScripts()`, atau
menyisipkan `<script src="...">`. Memanggil API dan menerima JSON **bukan** kode jarak jauh;
itu data jarak jauh, dan tidak termasuk kategori ini.

Sudah diverifikasi pada `dist/store/`: tidak ada `eval`, `new Function`, `importScripts`,
injeksi elemen `<script>`, `content_security_policy` yang dilonggarkan, maupun
`web_accessible_resources`. Seluruh `fetch` (`/health`, `/predict`, `/predict/batch`)
hanya menerima JSON. Jadi jawaban "Tidak" akurat dan bisa dipertanggungjawabkan.

> Menjawab "Ya" tanpa perlu akan memindahkan ekstensi ke jalur peninjauan yang jauh
> lebih ketat dan lama — hal terakhir yang Anda butuhkan dengan tenggat satu minggu.

#### Rincian isian tiap kolom

**Single purpose description**
```
Ekstensi ini memiliki satu tujuan tunggal: mendeteksi dan menyembunyikan komentar spam promosi judi online pada halaman YouTube.
```

**Justifikasi permission** — isi apa adanya:

| Permission | Justifikasi |
|---|---|
| `storage` | `Menyimpan preferensi pengguna (ambang keyakinan dan mode penyembunyian) secara lokal di perangkat agar pengaturan bertahan antar sesi.` |
| Host permission `www.youtube.com` | `Membaca teks komentar pada halaman YouTube untuk diklasifikasikan, dan menyembunyikan komentar yang terdeteksi sebagai spam judi online.` |
| Host permission `api-svm.cupsky.my.id` | `Mengirim teks komentar ke server klasifikasi milik pengembang dan menerima hasil prediksi berupa label dan nilai keyakinan.` |

> Cuma satu permission + dua host permission. Makin sedikit, makin cepat lolos review.

**Kalau kolom host permission cuma SATU** (dashboard sering menggabungkannya), tempel ini:

```
Ekstensi memerlukan akses ke www.youtube.com untuk membaca teks komentar pada halaman video dan menyembunyikan komentar yang terdeteksi sebagai spam promosi judi online. Akses ke api-svm.cupsky.my.id diperlukan untuk mengirim teks komentar tersebut ke server klasifikasi milik pengembang dan menerima hasil prediksi berupa label dan nilai keyakinan. Kedua akses ini merupakan inti dari fungsi tunggal ekstensi dan tidak digunakan untuk tujuan lain.
```

**Data usage — centang:**
- [x] **Website content** — teks komentar dikirim untuk diklasifikasikan

**Jangan** centang: personally identifiable information, health, financial, authentication,
personal communications, location, web history, user activity.

> Catatan: "Website content" **wajib** dicentang. Jangan digampangkan — kalau Google
> mendeteksi ada pengiriman data tapi tidak dideklarasikan, penolakannya jauh lebih lama diurus.

**Tiga sertifikasi wajib (centang semua):**
- [x] Tidak menjual/mengalihkan data ke pihak ketiga di luar kegunaan utama
- [x] Tidak memakai/mengalihkan data untuk tujuan yang tidak terkait kegunaan utama
- [x] Tidak memakai/mengalihkan data untuk menentukan kelayakan kredit atau pinjaman

**Privacy policy URL:** `https://api-svm.cupsky.my.id/privacy`

### 7. Distribution
- **Visibility:** Public
- **Distribution:** All regions (atau Indonesia saja — sama saja untuk keperluan skripsi)

### 8. Submit
- Klik **Submit for review**
- 📸 **Screenshot dashboard setelah submit** — harus terlihat status "Pending review",
  **Item ID**, dan tanggal submit. Ini bukti utama untuk penguji kalau approval belum turun.
- Catat Item ID di sini: `________________________`
- Catat tanggal & jam submit: `________________________`

---

## Rencana antisipasi deadline

Waktu review Google **tidak bisa diprediksi** (1 hari – 3 minggu). Naskah revisi
karena itu ditulis supaya **valid di dua skenario**:

| Skenario | Yang ditulis di naskah |
|---|---|
| Sudah approved sebelum deadline | Cantumkan URL store + tanggal publikasi + screenshot halaman toko |
| Masih "Pending review" | Cantumkan Item ID + tanggal submit + screenshot dashboard, dengan kalimat bahwa ekstensi telah diajukan dan sedang menunggu peninjauan |

Dua-duanya sama-sama membuktikan poin ke Dosen 2: sistem **tidak berhenti di localhost**.
Backend sudah publik dan hidup, dan distribusi ekstensi sudah diproses.

---

## Yang gua kerjakan setelah ini

Revisi naskah R1–R7 langsung di `1-AKTIF/[DRAFT] 221232017.docx` (mode: edit langsung
+ backup ke `2-RIWAYAT/backup/`). Penomoran sub-bab dan Daftar Isi otomatis — lu tinggal
buka Word lalu `Ctrl+A` → `F9` → "Update entire table".
