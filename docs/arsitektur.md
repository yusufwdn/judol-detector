# Arsitektur Sistem

Proyek ini bukan satu program besar, melainkan tiga aplikasi terpisah yang
dirangkai menjadi satu alur. Memahami pemisahan ini lebih dulu membuat sisa
dokumentasi jauh lebih mudah diikuti.

## Dua fase yang berbeda

| Fase | Komponen | Kapan berjalan |
|---|---|---|
| Build-time | Scraper, penyiapan dataset, pelatihan | Manual, sesekali |
| Runtime | Server API, ekstensi Chrome | Terus-menerus |

Hasil dari fase build-time adalah satu berkas artefak, `model/svm_model.joblib`.
Fase runtime hanya memuat berkas itu dan menerapkannya. Server tidak belajar
apa pun saat berjalan, sehingga prediksi selesai dalam hitungan milidetik
meskipun pelatihannya memakan waktu menit.

```
BUILD-TIME (manual, sesekali)

  YouTube Data API v3
        |
        v
  scraper/index.js              ambil komentar, beri skor heuristik awal
  scraper/filter.js             gabungkan hasil banyak video
        |
        v  scraper/final_spam.json, scraper/final_non_spam.json
        |
  src/prepare_dataset.py        saring dua tahap, terapkan koreksi manual
        |
        v  data/comments.csv  (6.690 baris)
        |
  src/train.py                  latih dan evaluasi
        |     |
        |     +-- src/preprocessing.py   normalisasi teks
        |     +-- TF-IDF                 teks menjadi vektor numerik
        |     +-- SVM                    vektor menjadi keputusan
        v
  model/svm_model.joblib        artefak hasil akhir


RUNTIME (berjalan terus)

  src/server.py                 FastAPI
        |  /predict          satu komentar
        |  /predict/batch    maksimal 50 komentar sekaligus
        |  /health           status server dan model
        |  /report           koreksi label, butuh token
        ^
        |  HTTP POST berisi teks mentah
        |
  extension/content.js          disuntikkan ke halaman YouTube
        |
        v
  Komentar spam diredupkan atau disembunyikan
```

## Kenapa normalisasi dilakukan di Python

Ekstensi mengirim teks komentar apa adanya. Secara teknis pembersihan teks bisa
saja dilakukan di JavaScript sebelum dikirim, sehingga beban server berkurang.
Pendekatan itu sengaja tidak dipakai.

Alasannya, pembersihan harus identik antara saat pelatihan dan saat prediksi.
Jika versi JavaScript berbeda sedikit saja dari versi Python, misalnya dalam
cara keduanya menangani karakter Unicode dekoratif, maka model menerima masukan
yang bentuknya tidak sama dengan yang dipelajarinya. Akurasi turun tanpa gejala
yang jelas dan penyebabnya sulit dilacak. Masalah ini dikenal sebagai
*training-serving skew*.

Solusinya menaruh seluruh normalisasi di satu tempat, yaitu
[`src/preprocessing.py`](../src/preprocessing.py), dan memakai modul yang sama
untuk pelatihan maupun prediksi.

```
Pelatihan : teks mentah -> clean_text() -> TF-IDF -> SVM belajar
Prediksi  : teks mentah -> clean_text() -> TF-IDF -> SVM menebak
```

Konsekuensinya, setiap kali `preprocessing.py` diubah, dataset harus disiapkan
ulang dan model dilatih ulang. Kalau tidak, model produksi masih memakai kamus
fitur dari aturan normalisasi yang lama.

## Kenapa bahasanya berbeda-beda

| Bagian | Bahasa | Alasan |
|---|---|---|
| Pelatihan dan prediksi | Python | Ekosistem scikit-learn, pandas, dan numpy tidak punya padanan sepadan di tempat lain |
| Pengumpulan data | Node.js | Tugasnya murni memanggil REST API dan mengolah JSON |
| Ekstensi | JavaScript | Satu-satunya yang dijalankan peramban |

Ketiganya terhubung lewat berkas dan HTTP, sehingga perbedaan bahasa tidak
menimbulkan kopling yang merepotkan.

## Isi kode inti

| Berkas | Peran |
|---|---|
| [`scraper/index.js`](../scraper/index.js) | Mengambil komentar dari YouTube API dan memberi skor heuristik |
| [`scraper/filter.js`](../scraper/filter.js) | Menggabungkan hasil banyak video menjadi berkas agregat |
| [`src/prepare_dataset.py`](../src/prepare_dataset.py) | Menyaring hasil scraper menjadi dataset berlabel |
| [`src/preprocessing.py`](../src/preprocessing.py) | Normalisasi teks tujuh tahap, dipakai pelatihan dan prediksi |
| [`src/train.py`](../src/train.py) | Melatih model, mengevaluasi, menyimpan artefak |
| [`src/server.py`](../src/server.py) | REST API |
| [`extension/content.js`](../extension/content.js) | Membaca komentar dari DOM dan menyembunyikan yang spam |
| [`extension/popup.js`](../extension/popup.js) | Panel pengaturan ekstensi |

Ditambah lima skrip eksperimen yang tidak ikut berjalan saat runtime, tetapi
menghasilkan angka yang dilaporkan di [evaluasi.md](evaluasi.md) dan
[eksperimen.md](eksperimen.md):

| Berkas | Menghasilkan |
|---|---|
| [`src/compare_baselines.py`](../src/compare_baselines.py) | Perbandingan SVM, Logistic Regression, dan Naive Bayes |
| [`src/evaluate_hard_set.py`](../src/evaluate_hard_set.py) | Pengujian pada 135 kasus ambigu |
| [`src/evaluate_hybrid_ablation.py`](../src/evaluate_hybrid_ablation.py) | Pengaruh aturan heuristik tambahan |
| [`src/experiment_stemming.py`](../src/experiment_stemming.py) | Pengaruh stemming Sastrawi |
| [`src/experiment_features.py`](../src/experiment_features.py) | Perbandingan konfigurasi n-gram dan `max_features` |

## Penyaringan di sisi klien

Ekstensi hanya mengubah tampilan di peramban pengguna. Tidak ada data milik
YouTube yang diubah, dan tidak ada permintaan tambahan ke server YouTube.
Pendekatan ini memang satu-satunya yang tersedia bagi pihak ketiga, tetapi
punya keuntungan yang layak disebut: setiap pengguna bisa menentukan sendiri
seberapa ketat ambang deteksinya.
