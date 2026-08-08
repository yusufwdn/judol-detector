# Panduan Belajar Skripsi — 7 Hari Menuju Sidang

Dokumen ini ditulis untuk satu tujuan: **membuat kamu benar-benar menguasai proyek ini sebelum sidang**, bukan sekadar hafal.

Asumsi yang dipakai:

- Latar belakangmu **Software Engineering**, bukan Machine Learning. Jadi konsep seperti *pipeline*, API, dependency, dan serialisasi sudah kamu kuasai — itu tidak akan dijelaskan panjang lebar. Yang dijelaskan pelan-pelan adalah lapisan ML-nya.
- Waktu belajar sekitar **3–4 jam per hari**.
- **Praktik dipisah** dari bacaan. Semua dokumen di bawah bisa dipahami tanpa menjalankan apa pun. Sesi praktik dikumpulkan terpisah di `LAB-praktik.md`, ambil kapan saja kamu punya waktu luang panjang.

---

## Kenapa dokumen ini ditulis ulang

Repositori ini sudah punya dokumentasi lama sebanyak 7.288 baris. Sayangnya sebagian sudah tidak sinkron dengan kondisi terkini:

| Dokumen lama | Masalah |
|---|---|
| `PENJELASAN_TEKNIS.md` | Mencampur angka dataset lama (1.800) dan baru (6.690) dalam satu file |
| `DOKUMENTASI.md` | Terakhir diubah 16 Juni, sebelum model dilatih ulang |
| `JOURNEY.md` | Masih memakai angka dataset 1.800 |

Belajar dari dokumen yang mencampur angka lama dan baru itu berbahaya — kamu bisa menyebut angka yang salah di depan penguji. Semua dokumen lama sudah dipindah ke `.arsip-dokumentasi-lama/`.

**Setiap angka di folder ini diverifikasi ulang dengan menjalankan kodenya**, bukan disalin dari dokumen lama.

---

## Urutan baca

Dokumen disusun berdasarkan **risiko saat sidang**, bukan urutan bab skripsi. Yang paling sering ditanya ada di depan.

| Hari | Dokumen | Fokus | Perkiraan |
|---|---|---|---|
| 1 | `00-peta-sistem.md` | Gambaran utuh sistem dalam satu peta | 45 menit |
| 1 | `01-kamus-ml.md` | Semua istilah ML dengan analogi dunia SE | 2 jam |
| 2 | `02-bedah-kode.md` (bagian data) | Scraper → pelabelan → prapemrosesan | 3 jam |
| 3 | `02-bedah-kode.md` (bagian model) | Pelatihan, TF-IDF, SVM | 3 jam |
| 4 | `03-angka-ke-kode.md` | Tiap angka di skripsi berasal dari mana | 3 jam |
| 5 | `02-bedah-kode.md` (bagian sistem) + `05-instalasi.md` | Server, ekstensi, cara menjalankan | 3 jam |
| 4 | `07-baca-gambar.md` | Cara membaca tiap gambar & asal nilainya | 1,5 jam |
| 6 | `04-kenapa-a-bukan-b.md` | Justifikasi tiap keputusan teknis | 3 jam |
| 7 | `06-bank-pertanyaan.md` | Latihan tanya jawab | 3 jam |
| — | `08-daftar-kesalahan.md` | ⚠️ **Baca sebelum sidang.** Ketidakcocokan yang sudah terlanjur tersubmit + cara menjawabnya | 45 menit |
| — | `09-naskah-presentasi.md` | 🎤 Naskah presentasi 10 menit per slide + anggaran waktu + peta lampiran | latih 3× |

Kapan saja (butuh waktu luang panjang): `LAB-praktik.md` — 3 sesi praktik, masing-masing 1–2 jam.

---

## Cara memakai dokumen ini

**Jangan dibaca seperti novel.** Tiap dokumen punya pola yang sama:

- 🎯 **Intinya** — ringkasan satu paragraf. Kalau cuma sempat baca ini, sudah lumayan.
- 🔍 **Penjelasan** — uraian dengan analogi.
- 📍 **Di kode** — lokasi persis di berkas dan baris berapa.
- 📄 **Di skripsi** — sub-bab mana yang membahas ini.
- ❓ **Kalau ditanya** — kalimat siap pakai untuk menjawab penguji.

Bagian ❓ itu yang paling penting. Kalau waktumu mepet, baca 🎯 dan ❓ saja di seluruh dokumen, lalu perdalam yang terasa paling goyah.

---

## Tiga hal yang paling berisiko

Kalau dari seluruh dokumen ini kamu cuma sempat menguasai tiga hal, pilih ini:

**1. Dari mana angka 97,53% berasal**
Harus bisa menyebut: data uji 1.338 baris, *confusion matrix* 863/9/24/442, dan rumus akurasi. Ini pertanyaan paling pasti muncul.

**2. Kenapa dua hasil negatif tetap dilaporkan**
Aturan hibrida justru **menurunkan** akurasi 7,32 poin, dan *stemming* **tidak signifikan** (p = 0,3575). Menjelaskan kenapa sesuatu tidak dipakai jauh lebih sulit daripada menjelaskan yang dipakai — dan penguji suka menanyakannya.

**3. Kenapa angka F1-macro 0,4963 di berkas hard test set bukan berarti model rusak**
Ini ranjau. Berkas `reports/hard_set_evaluation.txt` memuat angka yang terlihat buruk, padahal penyebabnya adalah komposisi data uji itu sendiri. Penjelasan lengkapnya ada di `03-angka-ke-kode.md`.

---

## Kalau ada yang tidak nyantol

Dokumen ini bukan satu-satunya jalur. Dua hal yang bisa kamu minta kapan saja:

- **Tanya ulang.** Sebutkan bagian mana yang belum masuk, nanti dijelaskan lagi dengan sudut pandang berbeda. Kadang analogi pertama memang tidak cocok untuk semua orang.
- **Simulasi sidang.** Minta diuji seperti penguji sungguhan — dicecar sampai ketahuan bagian mana yang masih bolong. Ini cara tercepat menemukan lubang pemahaman, dan paling efektif dilakukan di hari ke-6 atau ke-7.
