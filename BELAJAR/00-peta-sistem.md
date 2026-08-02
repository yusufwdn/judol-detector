# 00 — Peta Sistem

> Baca ini duluan. Setelah paham peta ini, semua dokumen lain tinggal mengisi detailnya.

---

## 🎯 Intinya

Proyek ini sebenarnya **tiga aplikasi terpisah** yang dirangkai jadi satu alur, bukan satu program besar:

1. **Pengumpul data** (Node.js) — mengambil komentar dari YouTube, dijalankan sekali-sekali secara manual.
2. **Pelatih model** (Python) — mengubah komentar jadi model yang bisa menebak, dijalankan sekali lalu hasilnya disimpan.
3. **Penyaji** (Python + JavaScript) — server yang melayani permintaan, dan ekstensi peramban yang bertanya ke server itu.

Kalau kamu terbiasa dengan istilah SE: ini seperti **ETL → build → runtime**. Bagian 1 dan 2 itu *build-time* (dijalankan sesekali, hasilnya artefak). Bagian 3 itu *runtime* (jalan terus melayani permintaan).

Kebingungan paling umum adalah menyangka semuanya jalan bersamaan. **Tidak.** Saat demo sidang nanti, yang benar-benar berjalan hanyalah bagian 3.

---

## 🔍 Alur lengkap

```
┌─── BUILD-TIME (dijalankan manual, sesekali) ──────────────────────┐
│                                                                    │
│  YouTube Data API v3                                               │
│         │                                                          │
│         ▼                                                          │
│  scraper/index.js ............... ambil komentar + beri skor awal  │
│         │                                                          │
│         ▼  final_spam.json / final_non_spam.json                   │
│                                                                    │
│  src/prepare_dataset.py ......... saring & beri label akhir        │
│         │                                                          │
│         ▼  data/comments.csv  (6.690 baris)                        │
│                                                                    │
│  src/train.py ................... latih model                      │
│         │        ├── src/preprocessing.py  (bersihkan teks)        │
│         │        ├── TF-IDF                (teks → angka)          │
│         │        └── SVM                   (angka → keputusan)     │
│         ▼                                                          │
│  model/svm_model.joblib ......... ARTEFAK. Ini hasil akhirnya.     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                              │
                              │  dimuat saat server dinyalakan
                              ▼
┌─── RUNTIME (yang jalan saat demo) ────────────────────────────────┐
│                                                                    │
│  src/server.py .................. FastAPI di localhost:8000        │
│         ▲          ├── /predict        satu komentar               │
│         │          ├── /predict/batch  banyak komentar (maks 50)   │
│         │          ├── /health         cek server hidup            │
│         │          └── /report         lapor salah deteksi         │
│         │                                                          │
│         │  HTTP POST (teks mentah)                                 │
│         │                                                          │
│  extension/content.js ........... disuntik ke halaman YouTube      │
│         │                                                          │
│         ▼                                                          │
│  Komentar spam diredupkan / disembunyikan                          │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Kenapa dipecah begini

**Analogi:** bayangkan restoran.

- **Pengumpul data** = belanja bahan ke pasar. Dilakukan sesekali, tidak saat pelanggan datang.
- **Pelatih model** = koki berlatih resep sampai jago, lalu resepnya ditulis di buku. Latihannya lama, tapi cuma sekali.
- **Server** = dapur yang siap memasak begitu ada pesanan, berbekal buku resep tadi.
- **Ekstensi** = pelayan yang menerima pesanan dari meja dan membawanya ke dapur.

`model/svm_model.joblib` itu **buku resepnya**. Server tidak belajar apa-apa saat berjalan — dia cuma membuka buku resep dan menerapkannya. Itu sebabnya prediksi bisa cepat (milidetik), padahal pelatihannya makan waktu menit.

---

## 🔍 Satu keputusan arsitektur yang penting

Perhatikan: **ekstensi mengirim teks mentah**, bukan teks yang sudah dibersihkan.

Padahal secara teknis, pembersihan teks bisa saja dilakukan di JavaScript sebelum dikirim. Kenapa tidak?

**Karena pembersihan harus identik antara saat pelatihan dan saat prediksi.** Kalau pembersihan versi JavaScript beda sedikit saja dari versi Python — misalnya cara keduanya menangani karakter Unicode aneh — maka model menerima masukan yang bentuknya agak berbeda dari yang dipelajarinya. Akibatnya akurasi turun tanpa kelihatan penyebabnya.

Masalah ini punya nama: **training-serving skew**. Solusinya sederhana: seluruh pembersihan dijalankan di satu tempat saja, yaitu `src/preprocessing.py`, dan berkas itu dipakai bersama oleh pelatihan maupun prediksi.

📍 **Di kode:** penjelasan ini ada sebagai komentar di `src/preprocessing.py` baris 16–29.

❓ **Kalau ditanya "kenapa normalisasi tidak di sisi klien saja supaya server lebih ringan?"**
> "Karena harus konsisten antara pelatihan dan prediksi, Pak. Kalau normalisasi dipecah antara JavaScript dan Python, perbedaan kecil dalam penanganan Unicode bisa membuat model menerima masukan yang tidak sama dengan saat dilatih — istilahnya *training-serving skew*. Jadi seluruh normalisasi dijalankan oleh satu berkas Python yang sama, dipakai bersama oleh pelatihan dan prediksi."

---

## 🔍 Isi repositori

Kode intinya **4.481 baris** di 11 berkas. Tidak sebanyak yang dibayangkan.

| Berkas | Baris | Perannya |
|---|---|---|
| `scraper/index.js` | 550 | Ambil komentar dari YouTube API, beri skor heuristik |
| `src/prepare_dataset.py` | 357 | Saring hasil scraper jadi dataset berlabel |
| `src/preprocessing.py` | 366 | **Pembersihan teks 7 tahap** — dipakai pelatihan & prediksi |
| `src/train.py` | 475 | Latih model, evaluasi, simpan artefak |
| `src/server.py` | 458 | REST API pelayan prediksi |
| `extension/content.js` | 540 | Sisi klien: baca komentar, sembunyikan yang spam |
| `extension/popup.js` | 198 | Panel pengaturan ekstensi |

Ditambah lima berkas eksperimen yang tidak ikut jalan di runtime, tapi **menghasilkan angka-angka yang kamu kutip di skripsi**:

| Berkas | Menghasilkan |
|---|---|
| `src/compare_baselines.py` | Perbandingan SVM vs Logistic Regression vs Naive Bayes |
| `src/evaluate_hard_set.py` | Uji ketahanan pada 135 kasus ambigu |
| `src/evaluate_hybrid_ablation.py` | Bukti bahwa aturan hibrida justru merugikan |
| `src/experiment_stemming.py` | Bukti bahwa *stemming* tidak signifikan |
| `src/experiment_features.py` | Perbandingan konfigurasi N-gram |

❓ **Kalau ditanya "mana bagian yang kamu buat sendiri?"**
Jawab jujur dan spesifik tentang peranmu: menentukan masalah, merancang alur, menetapkan aturan bisnis (mana yang dianggap spam), memutuskan eksperimen apa yang perlu dijalankan, dan menafsirkan hasilnya. Itu peran yang sah dan bisa dipertanggungjawabkan. Yang penting kamu **paham setiap keputusan di dalamnya** — dan itulah gunanya seminggu ini.

---

## 📄 Peta ke skripsi

| Bagian sistem | Dibahas di skripsi |
|---|---|
| Alur keseluruhan | Sub-bab 4.4 (Gambar 4.1 & 4.2) |
| Arsitektur komponen | Sub-bab 4.6 (Gambar 4.3) |
| Pembersihan teks | Sub-bab 2.4 (teori) dan 4.3 (penerapan) |
| TF-IDF | Sub-bab 2.5 |
| SVM | Sub-bab 2.6 |
| Hasil pengujian | Sub-bab 4.10 |
| Ekstensi | Sub-bab 2.13 (teori) dan 4.11 (tampilan) |

---

## Selanjutnya

Lanjut ke `01-kamus-ml.md` — semua istilah ML yang muncul di skripsimu, dijelaskan dengan analogi dari dunia software engineering.
