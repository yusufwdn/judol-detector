# Dokumentasi

Dokumentasi Judol Spam Detector. Untuk gambaran singkat proyek, lihat
[README di akar repositori](../README.md).

## Memulai

| Dokumen | Isi |
|---|---|
| [instalasi.md](instalasi.md) | Menyiapkan environment, menjalankan server, memasang ekstensi, melatih ulang model |
| [arsitektur.md](arsitektur.md) | Bagaimana ketiga komponen terhubung dan kenapa dipisah begitu |

## Data dan model

| Dokumen | Isi |
|---|---|
| [dataset.md](dataset.md) | Sumber data, proses penyaringan dua tahap, dan pelabelan |
| [riwayat-dataset.md](riwayat-dataset.md) | Catatan perubahan dataset dan model dari versi ke versi |
| [preprocessing.md](preprocessing.md) | Tujuh tahap normalisasi teks dan alasan tiap tahapnya |
| [model.md](model.md) | TF-IDF, SVM, pemilihan hyperparameter |
| [evaluasi.md](evaluasi.md) | Metrik, cross-validation, perbandingan baseline, pengujian kasus ambigu |
| [eksperimen.md](eksperimen.md) | Tiga studi yang dijalankan, termasuk dua yang hasilnya negatif |

## Sistem

| Dokumen | Isi |
|---|---|
| [api.md](api.md) | Referensi endpoint REST |
| [extension.md](extension.md) | Cara kerja ekstensi Chrome |
| [deployment.md](deployment.md) | Menjalankan di VPS dengan systemd, Nginx, dan HTTPS |
| [diagram.md](diagram.md) | Katalog berkas diagram |

## Lain-lain

| Dokumen | Isi |
|---|---|
| [roadmap.md](roadmap.md) | Fitur yang sudah selesai dan yang masih terbuka |

## Keputusan teknis

Ringkasan alasan di balik pilihan utama. Uraian lengkapnya ada di dokumen yang
ditunjuk.

| Pilihan | Alasan singkat | Detail |
|---|---|---|
| SVM, bukan Naive Bayes | Naive Bayes mengasumsikan antar fitur saling bebas, padahal kata penciri spam judol justru muncul berkelompok. Selisihnya 3,58 poin. | [model.md](model.md) |
| SVM, bukan Logistic Regression | Selisihnya tipis, 0,44 poin. SVM dipilih karena unggul konsisten di semua metrik dan menjadi fokus penelitian. | [evaluasi.md](evaluasi.md) |
| SVM, bukan deep learning | Kebutuhan latensi rendah, ukuran data relatif kecil, dan terbukti bahwa menambah kompleksitas justru menurunkan performa. | [eksperimen.md](eksperimen.md) |
| TF-IDF, bukan word embedding | Spam dikenali dari kata penciri yang spesifik, bukan kemiripan makna. Bobot fiturnya juga bisa ditelusuri. | [model.md](model.md) |
| Kernel linear | Data teks berdimensi tinggi umumnya sudah terpisah secara linear, dan kernel linear jauh lebih cepat. | [model.md](model.md) |
| Normalisasi di Python, bukan JavaScript | Mencegah selisih perlakuan Unicode antara pelatihan dan prediksi. | [arsitektur.md](arsitektur.md) |
| YouTube Data API v3, bukan scraping HTML | Sesuai ketentuan layanan, formatnya terstruktur, dan tidak rusak saat tampilan berubah. | [dataset.md](dataset.md) |
| FastAPI, bukan Flask atau Django | Validasi masukan otomatis lewat Pydantic, dan dokumentasi interaktif tersedia tanpa konfigurasi. | [api.md](api.md) |
| joblib, bukan pickle | Lebih efisien untuk objek berisi array numerik besar, dan dianjurkan scikit-learn. | [model.md](model.md) |
