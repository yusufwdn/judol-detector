# Judol Spam Detector — Dokumentasi Lengkap

> Proyek machine learning untuk mendeteksi dan menyembunyikan komentar spam promosi judi online di YouTube/Instagram menggunakan algoritma **SVM (Support Vector Machine)**.

> **Dokumen lain yang berkaitan:**
> - [JOURNEY.md](JOURNEY.md) — cerita & alasan kenapa proyek ini dibangun dengan urutan dan keputusan seperti ini (cocok dibaca duluan kalau kamu masih bingung "kenapa begini")
> - [PENJELASAN_TEKNIS.md](PENJELASAN_TEKNIS.md) — pendalaman teknis tiap komponen + kumpulan pertanyaan yang mungkin muncul saat sidang
>
> README ini fokus ke **cara setup & menjalankan** proyek.

---

## Daftar Isi

1. [Gambaran Besar Proyek](#1-gambaran-besar-proyek)
2. [Setup dari Awal](#2-setup-dari-awal)
3. [Struktur Proyek](#3-struktur-proyek)
4. [Cara Menjalankan](#4-cara-menjalankan)
5. [Teknologi & Library yang Dipakai](#5-teknologi--library-yang-dipakai)
6. [Penjelasan Konsep Machine Learning](#6-penjelasan-konsep-machine-learning)
7. [Training-Serving Consistency](#7-training-serving-consistency)
8. [Penjelasan Setiap File](#8-penjelasan-setiap-file)
9. [Cara Kerja Sistem Secara Keseluruhan](#9-cara-kerja-sistem-secara-keseluruhan)
10. [Cara Meningkatkan Akurasi Model](#10-cara-meningkatkan-akurasi-model)
11. [FAQ — Pertanyaan yang Mungkin Muncul](#11-faq--pertanyaan-yang-mungkin-muncul)

---

## 1. Gambaran Besar Proyek

### Masalah yang diselesaikan

Komentar spam promosi judi online sangat marak di platform seperti YouTube dan Instagram. Memblokir secara manual tidak efisien. Proyek ini membangun sebuah sistem otomatis yang:

1. **Mendeteksi** komentar spam menggunakan model AI yang sudah dilatih
2. **Menyembunyikan** komentar tersebut langsung dari halaman browser secara real-time

### Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────┐
│                     BROWSER (Chrome)                    │
│                                                         │
│  YouTube / Instagram          Extension (content.js)    │
│  ┌─────────────────┐    scan  ┌───────────────────┐     │
│  │ Komentar muncul │ ──────►  │ Baca teks komentar│     │
│  │ saat scroll     │          │ Kirim ke API       │     │
│  └─────────────────┘          └────────┬──────────┘     │
│                                        │ HTTP POST       │
└────────────────────────────────────────┼────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────┐
│              SERVER PYTHON (localhost:8000)              │
│                                                         │
│  FastAPI  ──►  Preprocessing  ──►  Model SVM            │
│                                         │               │
│                              {"label": "spam",          │
│                               "confidence": 0.97}       │
└─────────────────────────────────────────────────────────┘
```

Alurnya sederhana:
- Extension membaca komentar dari halaman
- Dikirim ke server Python via HTTP
- Server memproses dan menjawab: ini spam atau bukan?
- Extension menyembunyikan komentar yang terdeteksi spam

---

## 2. Setup dari Awal

### Prasyarat

Pastikan software berikut sudah terinstal di komputer:

| Software | Versi Minimum | Cara Cek |
|----------|---------------|----------|
| Python   | 3.10+         | `python --version` |
| pip      | 23+           | `pip --version` |
| Google Chrome | Terbaru  | — |

### Langkah 1 — Clone / Download Proyek

Jika menggunakan Git:
```bash
git clone <url-repo>
cd svm-judol-spam
```

Jika download manual, extract ZIP-nya lalu buka terminal di folder tersebut.

### Langkah 2 — (Opsional tapi Direkomendasikan) Buat Virtual Environment

Virtual environment adalah "ruang terisolasi" khusus untuk proyek ini. Tujuannya agar library yang diinstal tidak bercampur dengan proyek Python lain di komputer.

```bash
# Buat virtual environment (satu kali saja)
python -m venv env
```

Aktifkan virtual environment sesuai terminal yang dipakai:

| Terminal | Perintah Aktivasi |
|----------|-------------------|
| Windows — PowerShell | `.\env\Scripts\Activate.ps1` |
| Windows — Command Prompt | `env\Scripts\activate.bat` |
| Windows — Git Bash | `source env/Scripts/activate` |
| Mac / Linux — bash / zsh | `source env/bin/activate` |

Setelah aktif, terminal akan menampilkan `(env)` di awal baris. Selalu aktifkan ini sebelum menjalankan proyek.

> **PowerShell — Execution Policy Error?**
> Jika muncul error *"running scripts is disabled on this system"*, jalankan perintah berikut **sekali** di PowerShell (sebagai Administrator), lalu coba aktifkan lagi:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### Langkah 3 — Install Semua Library

```bash
pip install -r requirements.txt
```

Perintah ini membaca file `requirements.txt` dan menginstal semua library yang dibutuhkan secara otomatis. Proses ini membutuhkan koneksi internet dan mungkin memakan waktu 1–3 menit.

### Langkah 4 — Siapkan Dataset

```bash
python src/prepare_dataset.py
```

Skrip ini membaca data scraping dari `scraper/final_spam.json`, memfilter komentar spam menggunakan **two-pass filter** (lihat penjelasan di bawah), lalu menggabungkannya dengan contoh komentar non-spam untuk membentuk dataset di `data/comments.csv`.

Output yang diharapkan (angka aktual dari dataset proyek ini saat ini — Versi 11, lihat [DATASET_LOG.md](DATASET_LOG.md)):
```
[1/4] Loading spam data (threshold >= 80)...
  Total entries in JSON        : 2324
  Passed primary threshold     : 138
  Rescued via brand regex      : 1947
  Skipped (low score / noisy)  : 239
    -> brand_pattern false pos.: 152
  Total spam collected         : 2085

[2/4] Loading non-spam data...
  Total entries in JSON : 4156
  Loaded                : 4156

[3/4] Applying manual overrides (data/manual_overrides.csv)...
  Loaded 349 manual overrides:
    FP dihapus dari spam      : 7
    Entry ditambah ke non_spam: 82
    Entry ditambah ke spam    : 193

[4/4] Merging, shuffling, and saving dataset...
  Spam samples    : 2332
  Non-spam samples: 4177
  Total           : 6509
  Saved to: data/comments.csv
```

> **Kenapa "two-pass filter", bukan threshold tunggal?** Sistem scraping menghitung `spam_score` (0–100) berdasarkan sinyal heuristik (brand name, link kontak, kata kunci tersamarkan, dll.). Kalau kita hanya ambil yang skornya **≥ 80** (Pass 1), hasilnya cuma ~138 entri — terlalu sedikit untuk training.
>
> Maka ditambahkan **Pass 2**: untuk entri berskor rendah yang mengandung sinyal `brand_pattern`, dicek apakah `normalized_text`-nya mengandung pola brand judi yang jelas (huruf kapital + angka seperti `WIFI4D`, atau suffix khas seperti `*TOTO`/`*BET`/`*WIN`/`*QQ`). Kalau cocok, entri itu "diselamatkan" sebagai spam asli.
>
> Hasil akhir tahap ini: **2085 spam** (138 dari Pass 1 + 1947 dari rescue), lalu di tahap [3/4] ditambah/dikurangi lagi oleh `manual_overrides.csv` (lihat [Bagian 4](#4-cara-menjalankan)) sampai jadi **2332 spam** final — termasuk 61 entri yang awalnya salah ter-scrape sebagai non-spam (spam tersamar pakai Unicode dekoratif/leet speak yang lolos heuristik scraper, lihat [DATASET_LOG.md Versi 11](DATASET_LOG.md#versi-11--2026-06-30)) dan direlabel manual ke spam. Penjelasan lengkap + contoh kasus nyata ("kesambet" yang awalnya ke-flag salah) ada di [PENJELASAN_TEKNIS.md bagian 5](PENJELASAN_TEKNIS.md#5-solusi-two-pass-filter-di-prepare_datasetpy).

### Langkah 5 — Training Model

```bash
python src/train.py
```

Ini adalah langkah terpenting. Skrip ini akan:
- Membaca dataset dari `data/comments.csv`
- Membersihkan dan memproses teks
- Melatih model SVM
- Mengevaluasi akurasi
- Menyimpan model ke `model/svm_model.joblib`

### Langkah 6 — Jalankan Server API

```bash
python src/server.py
```

Server akan berjalan di `http://localhost:8000`. Buka URL tersebut di browser untuk memastikan server aktif. Halaman dokumentasi API interaktif tersedia di `http://localhost:8000/docs`.

### Langkah 7 — Pasang Extension Chrome

1. Buka browser Chrome
2. Ketik `chrome://extensions` di address bar
3. Aktifkan **Developer Mode** (toggle di pojok kanan atas)
4. Klik tombol **"Load unpacked"**
5. Pilih folder `extension/` di dalam proyek ini
6. Extension akan muncul di toolbar Chrome

> **Catatan:** Server Python **harus berjalan** agar extension berfungsi. Jalankan server dulu sebelum membuka YouTube/Instagram.

---

## 3. Struktur Proyek

```
svm-judol-spam/
│
├── data/
│   ├── comments.csv           ← Dataset berlabel final (dibuat oleh prepare_dataset.py)
│   ├── manual_overrides.csv   ← Koreksi label manual, persisten lintas rebuild (lihat Bagian 4)
│   ├── hard_test_set.csv      ← 141 komentar ambigu, dipakai evaluate_hard_set.py
│   └── skipped_entries.json   ← Audit entri yang ke-skip oleh two-pass filter
│
├── scraper/
│   ├── index.js               ← YouTube Data API v3 scraper (Node.js)
│   ├── filter.js              ← Agregasi hasil scraping per label
│   ├── final_spam.json        ← Agregasi komentar spam (output filter.js)
│   ├── final_non_spam.json    ← Agregasi komentar non-spam (output filter.js)
│   └── result/                ← Output mentah per-run scraping
│
├── src/
│   ├── prepare_dataset.py     ← Konversi JSON scraping → comments.csv (two-pass filter + overrides)
│   ├── preprocessing.py       ← Pipeline 7+3 lapisan pembersih teks
│   ├── train.py                ← Script training model SVM (k-fold CV + GridSearchCV)
│   ├── server.py              ← REST API server (FastAPI) + hybrid rules
│   ├── compare_baselines.py   ← Perbandingan SVM vs Naive Bayes vs Logistic Regression
│   ├── evaluate_hard_set.py   ← Evaluasi model di hard_test_set.csv
│   ├── experiment_stemming.py ← Eksperimen Sastrawi stemming
│   ├── experiment_features.py ← Eksperimen ngram_range & max_features
│   └── inspect_features.py    ← Inspeksi fitur TF-IDF berbobot tertinggi
│
├── model/
│   ├── svm_model.joblib       ← Model produksi saat ini (dibuat otomatis)
│   └── versions/              ← Arsip biner tiap versi model historis (lihat versions/INDEX.md)
│
├── extension/
│   ├── manifest.json          ← Konfigurasi Chrome extension (Manifest v3)
│   ├── content.js             ← Script yang berjalan di halaman web
│   ├── popup.html             ← Tampilan UI popup extension
│   ├── popup.js               ← Logic popup
│   └── icons/                 ← Ikon extension
│
├── reports/                   ← Output evaluasi: confusion matrix, top features, hasil eksperimen
├── notebooks/                 ← (opsional, kosong) tempat eksplorasi Jupyter kalau dibutuhkan
├── requirements.txt           ← Daftar library Python yang dibutuhkan
├── DATASET_LOG.md             ← Log riwayat versi dataset (8 versi tercatat)
├── JOURNEY.md                 ← Cerita kronologis pengembangan proyek
├── PENJELASAN_TEKNIS.md       ← Pendalaman teknis + Q&A sidang
├── TODO.md                    ← Roadmap pengembangan per fase
└── README.md                  ← File ini
```

### Penjelasan Singkat Setiap Folder

| Folder/File | Peran |
|------------|-------|
| `data/` | Dataset berlabel + file pendukung (overrides, hard test set). Semakin banyak dan beragam datanya, semakin baik model |
| `src/` | Inti dari sistem: preprocessing, training, evaluasi, dan serving model |
| `model/` | Hasil dari proses training. File `.joblib` berisi "otak" yang sudah dilatih |
| `extension/` | Kode browser extension yang berinteraksi langsung dengan halaman web |
| `reports/` | Hasil evaluasi (confusion matrix, top features, eksperimen) — referensi untuk sidang |
| `notebooks/` | (Opsional, belum dibuat) tempat bereksperimen interaktif pakai Jupyter Notebook, kalau dibutuhkan nanti |

---

## 4. Cara Menjalankan

### Menambah data ke dataset

Ada empat cara menambah data, tergantung kasusnya:

| Kasus | File yang diubah | Keterangan |
|-------|-----------------|------------|
| Koreksi label (spam → non_spam atau sebaliknya) | `data/manual_overrides.csv` | **Cara paling aman.** Berlaku di setiap rebuild. |
| Data spam baru dari YouTube (banyak) | Scraper → `scraper/final_spam.json` | Jalankan scraper dulu, lalu sync ke sini. |
| Data non-spam baru dari YouTube (banyak) | Scraper → `scraper/final_non_spam.json` | Sama seperti spam, mode `non_spam`. |
| Satu komentar langsung | `data/manual_overrides.csv` | Jangan hanya edit `comments.csv` — file itu ter-overwrite saat rebuild. |

**Jangan edit `data/comments.csv` secara langsung** kecuali kamu langsung ikuti dengan menambahkan entri yang sama ke `manual_overrides.csv`. File `comments.csv` digenerate ulang setiap `prepare_dataset.py` dijalankan — koreksi yang hanya ada di sana akan hilang.

#### Alur lengkap: koreksi label manual

Edit `data/manual_overrides.csv` langsung:
```csv
text,label
"teks komentar yang mau dikoreksi",non_spam
```

Lalu rebuild dan retrain:
```bash
python src/prepare_dataset.py
python src/train.py
```

#### Alur lengkap: data spam/non-spam baru dari scraper

```bash
# Di folder scraper-judol-yt-comment:
node scraper/index.js <VIDEO_ID>                    # spam (default)
node scraper/index.js <VIDEO_ID> video non_spam     # non-spam

# Setelah semua video selesai:
node scraper/filter.js
# → hasilnya: final_spam.json dan final_non_spam.json

# Copy ke folder ini:
# scraper/final_spam.json dan scraper/final_non_spam.json

# Rebuild dataset dan retrain:
python src/prepare_dataset.py
python src/train.py
```

### Training ulang model (setelah menambah data baru)

```bash
# Langkah 1: Perbarui dataset dari data scraping terbaru
python src/prepare_dataset.py

# Langkah 2: Latih ulang model
python src/train.py
```

### Menjalankan server API

```bash
python src/server.py
```

### Test API secara manual (tanpa extension)

Menggunakan PowerShell:
```powershell
# Test komentar spam
Invoke-RestMethod -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text": "Daftar sekarang bonus 100% slot gacor!"}'

# Test komentar biasa
Invoke-RestMethod -Uri "http://localhost:8000/predict" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"text": "Mantap tutorialnya, langsung berhasil dipraktekkan!"}'
```

Atau bisa juga lewat halaman `http://localhost:8000/docs` yang menyediakan UI interaktif untuk mencoba semua endpoint API.

---

## 5. Teknologi & Library yang Dipakai

### Bahasa Pemrograman

| Bahasa | Dipakai di mana | Alasan |
|--------|----------------|--------|
| Python | Backend, training, API | Ekosistem ML terlengkap, sintaks mudah dibaca |
| JavaScript | Browser extension | Satu-satunya bahasa yang bisa berjalan di browser |

### Library Python

#### `scikit-learn` — Inti dari Machine Learning

Library ML paling populer untuk Python. Berisi implementasi SVM, TF-IDF, train-test split, dan semua fungsi evaluasi yang digunakan.

**Kenapa bukan TensorFlow/PyTorch?**
TensorFlow dan PyTorch adalah library untuk *Deep Learning* (neural networks). Untuk klasifikasi teks dengan dataset berukuran ratusan hingga ribuan data, SVM dari scikit-learn jauh lebih:
- Cepat untuk dilatih (hitungan detik, bukan jam)
- Mudah dipahami dan dijelaskan
- Tidak butuh GPU mahal
- Performanya sudah sangat baik untuk tugas ini

#### `pandas` — Manipulasi Data

Digunakan untuk membaca file CSV dan mengolah dataset dalam bentuk tabel (DataFrame). Analoginya seperti Microsoft Excel versi Python.

#### `numpy` — Operasi Numerik

Library dasar untuk komputasi numerik. Hampir semua library ML bergantung pada numpy di balik layar.

#### `FastAPI` — Framework Web API

Digunakan untuk membuat REST API yang menjadi jembatan antara model Python dan extension JavaScript.

**Kenapa FastAPI, bukan Flask?**

| Aspek | FastAPI | Flask |
|-------|---------|-------|
| Kecepatan | Sangat cepat (async) | Lebih lambat (sync) |
| Validasi data | Otomatis via Pydantic | Manual |
| Dokumentasi API | Otomatis tersedia di `/docs` | Harus dibuat sendiri |
| Kemudahan belajar | Sedikit lebih steep | Lebih sederhana |

Untuk proyek ini, FastAPI dipilih karena validasi otomatis dan dokumentasi gratis sangat membantu.

#### `uvicorn` — ASGI Server

Server yang menjalankan aplikasi FastAPI. Analoginya seperti "mesin" yang menggerakkan API. FastAPI butuh uvicorn untuk bisa menerima request dari luar.

#### `pydantic` — Validasi Data

Memastikan data yang masuk ke API sudah dalam format yang benar sebelum diproses. Misalnya, memastikan field `text` tidak boleh kosong dan tidak boleh lebih dari 5000 karakter.

#### `joblib` — Simpan & Load Model

Digunakan untuk menyimpan model yang sudah dilatih ke file (`.joblib`) dan memuatnya kembali. Tanpa ini, setiap kali server dinyalakan, model harus dilatih ulang dari awal — yang jelas tidak efisien.

---

## 6. Penjelasan Konsep Machine Learning

Bagian ini menjelaskan konsep-konsep yang mungkin asing bagi pemula.

### Apa itu Machine Learning?

Machine Learning adalah cara membuat program komputer yang bisa "belajar" dari data tanpa harus diprogram secara eksplisit untuk setiap aturan.

Contoh analogi: Daripada kita tulis aturan manual seperti *"kalau ada kata 'daftar' dan 'bonus' maka itu spam"*, kita kasih ribuan contoh komentar spam dan bukan spam, lalu biarkan algoritma sendiri yang mencari polanya.

### Apa itu Klasifikasi?

Klasifikasi adalah tugas mengelompokkan data ke dalam kategori. Dalam proyek ini, kategorinya ada dua: `spam` dan `bukan_spam`. Karena hanya dua kelas, ini disebut **binary classification**.

### Kenapa SVM?

**SVM (Support Vector Machine)** adalah algoritma yang mencari "garis pemisah" terbaik antara dua kelompok data.

Bayangkan kamu punya titik-titik merah (spam) dan titik-titik biru (bukan spam) yang tersebar di kertas. SVM mencari garis yang memisahkan keduanya dengan **jarak (margin) paling lebar** ke titik terdekat di masing-masing kelompok.

```
    Spam          │        Bukan Spam
      ●            │                ○
    ●   ●          │ margin     ○      ○
          ●        │◄──────►○
              ●    │    ○          ○
```

"Titik-titik yang paling dekat ke garis pemisah" itulah yang disebut **Support Vectors** — inilah asal nama algoritmanya.

**Kenapa SVM bagus untuk teks?**
- Data teks biasanya berdimensi sangat tinggi (ribuan kata = ribuan dimensi)
- SVM terbukti bekerja sangat baik di dimensi tinggi
- Efisien secara komputasi
- Performa sangat kompetitif untuk klasifikasi teks

### Apa itu TF-IDF?

Model SVM bekerja dengan angka, bukan kata. TF-IDF adalah cara mengubah teks menjadi vektor angka.

**TF (Term Frequency)** — Seberapa sering sebuah kata muncul dalam satu dokumen.

**IDF (Inverse Document Frequency)** — Seberapa *langka* kata tersebut di seluruh dataset. Kata yang ada di semua dokumen (seperti "yang", "dan") mendapat bobot rendah.

**TF-IDF = TF × IDF** — Kata yang sering muncul di satu dokumen DAN langka di dokumen lain mendapat bobot tinggi. Itulah kata yang benar-benar "khas" untuk dokumen tersebut.

Contoh:
- Kata `"bonus"` → sering di komentar spam, jarang di komentar biasa → bobot tinggi
- Kata `"yang"` → ada di semua komentar → bobot sangat rendah

### Apa itu N-gram?

N-gram adalah cara mempertimbangkan kombinasi kata, bukan hanya kata tunggal.

- **Unigram (1-gram):** `"daftar"`, `"sekarang"`, `"bonus"` (kata satu-satu)
- **Bigram (2-gram):** `"daftar sekarang"`, `"sekarang bonus"` (pasangan kata)

Kenapa penting? Karena `"tidak spam"` dan `"spam"` punya makna yang sangat berbeda, tapi kalau hanya lihat kata satu-satu, kata `"spam"` akan tetap dianggap sama.

Dalam proyek ini dipakai `ngram_range=(1, 2)` — artinya pakai unigram DAN bigram.

### Apa itu Train-Test Split?

Sebelum melatih model, dataset dibagi menjadi dua bagian:

- **Training set (80%)** — Data yang digunakan untuk melatih model
- **Test set (20%)** — Data yang "disembunyikan" dan baru digunakan setelah training selesai untuk mengukur performa

Analoginya: bayangkan belajar untuk ujian. Training set itu latihan soal, test set itu soal ujian asli. Kalau kamu cuma latihan dengan soal yang sama persis dengan ujian, nilaimu mungkin bagus tapi tidak mencerminkan kemampuan sebenarnya.

### Apa itu Pipeline?

Pipeline adalah cara menggabungkan beberapa langkah pemrosesan menjadi satu objek yang bisa dipanggil sekaligus.

Dalam proyek ini, pipeline terdiri dari:
```
Input teks → TF-IDF Vectorizer → SVM Classifier → Output label
```

Manfaat Pipeline:
1. Mencegah **data leakage** — TF-IDF hanya "belajar" dari data training, bukan test
2. Satu perintah `.fit()` untuk melatih semua tahap sekaligus
3. Satu perintah `.predict()` untuk prediksi end-to-end

### Cara Membaca Hasil Evaluasi

Setelah training, akan tampil laporan seperti ini (angka aktual dari dataset Versi 11, 6509 baris, split 80/20 stratified → test set 1302 sampel):

```
              precision    recall  f1-score   support

    non_spam       0.97      0.99      0.98       836
        spam       0.98      0.94      0.96       466

    accuracy                           0.97      1302
```

Akurasi train-test split: **97.39%** (F1-macro 0.9713). Angka ini jauh dari 100% justru karena dataset sudah jauh lebih beragam (data non-spam nyata, bukan sintetis) dibanding versi awal proyek.

> **Apakah angka ini cukup meyakinkan?** Selain train-test split, model juga dievaluasi dengan **5-fold cross-validation** (mean F1 97.30% ± 0.27%) dan **hard test set** berisi 135 komentar ambigu yang sengaja sulit (accuracy 97.04%). Detail lengkap metodologi evaluasi, riwayat tiap iterasi (termasuk insiden kontaminasi data spam tersamar yang ditemukan dan diperbaiki di Versi 11), dan kenapa angka tidak 100% itu justru tanda dataset yang lebih jujur, ada di [PENJELASAN_TEKNIS.md bagian 15](PENJELASAN_TEKNIS.md#15-pertanyaan-yang-mungkin-muncul-saat-sidang) dan [DATASET_LOG.md](DATASET_LOG.md).

**Precision** — Dari semua yang diprediksi "spam", berapa persen yang benar-benar spam?

$$\text{Precision} = \frac{\text{True Positive}}{\text{True Positive} + \text{False Positive}}$$

**Recall** — Dari semua komentar spam yang ada, berapa persen yang berhasil terdeteksi?

$$\text{Recall} = \frac{\text{True Positive}}{\text{True Positive} + \text{False Negative}}$$

**F1-Score** — Rata-rata harmonis antara precision dan recall. Ini metrik utama karena menyeimbangkan keduanya.

$$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

**Confusion Matrix** — Tabel yang menunjukkan detail kesalahan model:

```
                  Prediksi: bukan_spam   Prediksi: spam
Aktual: bukan_spam       17 (TN ✓)          1 (FP ✗)
Aktual: spam              0 (FN ✗)         15 (TP ✓)
```

- **TN (True Negative):** Model benar menebak "bukan spam"
- **TP (True Positive):** Model benar menebak "spam"
- **FP (False Positive):** Komentar biasa salah ditandai spam *(false alarm)*
- **FN (False Negative):** Komentar spam lolos tidak terdeteksi *(berbahaya!)*

Dalam konteks spam detection, **FN lebih berbahaya** dari FP. Lebih baik terlalu banyak yang tersembunyi daripada spam lolos.

---

## 7. Training-Serving Consistency

### Masalah yang diselesaikan

Salah satu jebakan paling umum dalam deployment model machine learning adalah **training-serving skew**: model yang dilatih pada data yang sudah dinormalisasi, lalu menerima data mentah (atau berbeda caranya) saat produksi. Hasilnya: model tampak akurat di evaluasi, tapi buruk di dunia nyata.

Proyek ini dirancang khusus untuk menghindari masalah ini.

---

### Kenapa preprocessing dilakukan di Python, bukan di JavaScript extension?

Pertanyaan ini penting secara arsitektur.

Secara teknis, browser extension bisa melakukan normalisasi teks sebelum mengirimkannya ke server. Tapi ada alasan kuat mengapa itu tidak dilakukan di sini:

**1. JavaScript dan Python menangani Unicode secara berbeda**

Meskipun keduanya mendukung Unicode, implementasi regex, normalisasi unicode (NFKC), dan penanganan karakter eksotis bisa menghasilkan output yang berbeda secara halus antara JavaScript dan Python. Perbedaan sekecil apapun dalam input akan mengubah representasi TF-IDF yang diterima model, yang berdampak langsung pada akurasi prediksi.

**2. Prinsip satu sumber kebenaran**

Fungsi `clean_text()` di `src/preprocessing.py` adalah satu-satunya definisi "cara membersihkan teks" di seluruh sistem. Ia dipanggil identik di dua tempat:

```
Training  : raw text → clean_text() → TF-IDF → SVM belajar dari ini
Inference : raw text → clean_text() → TF-IDF → SVM memprediksi ini
```

Karena transformasinya identik di kedua jalur, model selalu menerima input dalam format yang persis sama dengan yang ia pernah lihat saat training.

**3. Kenapa `original_text`, bukan `normalized_text`?**

Data scraping menyimpan dua versi teks: `original_text` (teks asli dari YouTube API) dan `normalized_text` (sudah diproses oleh scraper menggunakan NFKC normalize).

Dataset training menggunakan `original_text`. Alasannya:

- Saat extension mendeteksi komentar di halaman YouTube, ia membaca teks langsung dari DOM — yaitu teks **mentah** sebelum normalisasi apapun.
- Jika training menggunakan `normalized_text`, maka model belajar dari teks yang sudah berbeda format dibanding apa yang akan ia terima saat produksi.
- Ini akan menciptakan training-serving skew meskipun normalisasinya sendiri sudah benar.

Dengan menggunakan `original_text` untuk training dan membiarkan `clean_text()` melakukan semua normalisasi, kita memastikan pipeline identik dari ujung ke ujung.

---

### Diagram alur kedua jalur

```
TRAINING
────────────────────────────────────────────────────────────
original_text (dari JSON)
    │
    ▼
clean_text()  [src/preprocessing.py]
    │
    ▼
TF-IDF vectorization
    │
    ▼
SVM fit  →  model disimpan ke model/svm_model.joblib

INFERENCE (produksi)
────────────────────────────────────────────────────────────
Teks komentar mentah dari DOM YouTube
    │
    ▼ (dikirim via HTTP POST, tanpa modifikasi apapun di JS)
clean_text()  [src/preprocessing.py]  ← FUNGSI YANG SAMA PERSIS
    │
    ▼
TF-IDF transform  (menggunakan vocabulary dari training)
    │
    ▼
SVM predict  →  {"label": "spam", "confidence": 0.94}
```

---

### Implikasi untuk pengembangan ke depan

Jika kamu menambahkan langkah normalisasi baru ke `clean_text()`, model **harus dilatih ulang**. Mengubah preprocessing tanpa melatih ulang model akan menciptakan skew karena model sudah mempelajari pola dari representasi teks yang lama.

Urutan yang benar selalu:
1. Update `src/preprocessing.py`
2. Jalankan `python src/prepare_dataset.py`
3. Jalankan `python src/train.py`

---

## 8. Penjelasan Setiap File

### `data/comments.csv`

Dataset berlabel yang menjadi "bahan belajar" model. File ini **tidak ada di repo secara default** — dibuat otomatis oleh `src/prepare_dataset.py`. Format (sejak Versi 11):

```
text,label,source
"Daftar sekarang bonus 100%!",spam,abc123XYZvid
"Video ini sangat membantu!",non_spam,def456UVWvid
"Komentar yang dikoreksi manual",non_spam,manual_override
```

Tiga kolom:
- `text` — isi komentar mentah (`original_text` dari data scraping)
- `label` — `spam` atau `non_spam`
- `source` — `video_id` asal komentar (untuk data dari scraper), atau literal `manual_override` (untuk data dari `manual_overrides.csv` / endpoint `/report`)

> **Kenapa ada kolom `source`?** Setiap kali `prepare_dataset.py` dijalankan, `comments.csv` di-regenerate total dari `final_spam.json` + `final_non_spam.json` + `manual_overrides.csv`, lalu **diacak ulang** (`random.shuffle`) — bukan di-append di bagian bawah. Jadi data dari scraping terbaru akan selalu tercampur posisinya dengan data lama, dan urutan baris di file **tidak bisa dipakai** untuk melacak "mana yang baru ditambahkan". Kolom `source` menyelesaikan ini — bisa di-filter (`df[df.source == 'VIDEO_ID']`) kapan saja tanpa perlu shuffle stabil atau balik buka JSON mentah. Ini juga yang dipakai untuk audit kualitas data (lihat insiden kontaminasi di [DATASET_LOG.md Versi 11](DATASET_LOG.md#versi-11--2026-06-30)).
>
> Shuffle sendiri tetap dipertahankan dan **tidak masalah untuk training** — `train_test_split` di `train.py` sudah shuffle ulang dengan `random_state=42` + `stratify=y`, jadi urutan baris di CSV tidak memengaruhi hasil training sama sekali.

> **Semakin banyak dan beragam datanya, semakin baik modelnya.**
> Dataset proyek ini (Versi 11) berisi **6509 baris**: 2332 spam + 4177 non-spam, **keduanya dari data scraping nyata** (non-spam tidak lagi sintetis sejak Versi 2 — lihat [DATASET_LOG.md](DATASET_LOG.md)). Bukan cuma soal jumlah — audit menemukan mayoritas data non-spam sebelumnya bertopik generik (tidak menyinggung judi sama sekali), sehingga kurang membantu model membedakan kritik dari promosi; Versi 10 secara khusus menambah komentar non-spam yang benar-benar membahas topik judi (kritik, cerita pengalaman, edukasi). Versi 11 lalu memperbaiki insiden kualitas data: 61 komentar spam tersamar (Unicode dekoratif/leet speak) yang lolos heuristik scraper direlabel dari non-spam ke spam.
> Untuk hasil yang andal:
> - **Minimum:** 1:1 rasio spam:non-spam, minimal 500 sampel per kelas
> - **Target realistis:** 1.500+ sampel per kelas dengan rasio 1:1 hingga 2:1
> - **Ideal:** Data non-spam juga dari scraping nyata (bukan sintetis) untuk menghindari bias distribusi — **sudah tercapai di Versi 8**

---

### `src/prepare_dataset.py`

Skrip persiapan dataset. Harus dijalankan **sebelum** `train.py` setiap kali data scraping diperbarui.

Cara kerjanya:
1. Baca `scraper/final_spam.json`, filter entri spam dengan **two-pass filter**: ambil yang `spam_score >= 80` (Pass 1), lalu "selamatkan" entri berskor rendah yang terbukti mengandung pola brand judi nyata di `normalized_text` (Pass 2). Lihat [Bagian 2, Langkah 4](#langkah-4--siapkan-dataset) untuk detail & angka aktualnya
2. Baca `scraper/final_non_spam.json` — komentar non-spam nyata hasil scraping (bukan sintetis)
3. Terapkan koreksi dari `data/manual_overrides.csv` (hapus false positive, tambah entry yang lolos filter otomatis) — lihat [Bagian 4](#4-cara-menjalankan)
4. Gabungkan, acak, simpan ke `data/comments.csv`

Menggunakan `original_text` (bukan `normalized_text`) dari JSON. Lihat [Bagian 7](#7-training-serving-consistency) untuk alasannya.

---

### `src/preprocessing.py`

Modul yang bertugas membersihkan teks sebelum diproses model. Pipeline 7 langkah + 3 sub-langkah yang dijalankan secara berurutan:

```
Teks mentah
    ↓ 1.  Hapus karakter zero-width: U+200B, U+FEFF, dll. (tak kasat mata)
    ↓ 2.  NFKC normalization: 𝑅𝒪𝑀𝒜 → ROMA, Ｄａｆｔａｒ → Daftar
    ↓ 2b. Hapus combining diacritical marks: P̲U̲L̲A̲U̲ → PULAU
    ↓ 2c. Buka karakter yang dibungkus kurung: [P][U][L] → PUL
    ↓ 3.  Homoglyph Cyrillic/Greek/Thai: а→a, е→e, о→o (karakter yang mirip huruf Latin)
    ↓ 4.  Demojize emoji: 🎰 → slot_machine, 💰 → money_bag
    ↓ 5.  Lowercase
    ↓ 5b-i. Normalisasi leet speak: h0ki777 → hoki777, s1tus → situs (hanya 0→o, 1→i)
    ↓ 5b. Kanonikalisasi brand judol: keju4d/hobiqq/betawi77 → judolbrand
    ↓ 6.  Hapus URL + karakter non-alfabet
    ↓ 7.  Hapus stopwords + token pendek (≤ 1 karakter)
Teks bersih → siap diproses TF-IDF
```

Contoh nyata:
```
Sebelum: "𝑅𝒪𝑀𝒜4𝒟 🎰 dаftаr sekarang bonus 100%!"
Sesudah: "judolbrand slot_machine daftar sekarang bonus"
```

**Kenapa pipeline berlapis, bukan cukup lowercase dan hapus simbol?**

Spammer sengaja menyamarkan teks agar lolos filter kata kunci sederhana: huruf Unicode dekoratif (𝑹𝑶𝑴𝑨), karakter Cyrillic yang identik secara visual dengan huruf Latin (а vs a), karakter dibungkus tanda baca per huruf ([P][U][L]), leet speak (h0ki777), dan emoji sebagai pengganti kata. Pipeline ini secara eksplisit membongkar setiap teknik penyamaran tersebut sebelum teks dianalisis oleh model. Step 5b juga mengonversi pola brand judol (nama + suffix angka/QQ) ke token universal `judolbrand` agar model bisa generalisasi ke brand baru yang belum pernah dilihat — detail lengkap ada di komentar `JUDOL_BRAND_PATTERN` di `src/preprocessing.py`.

**Fungsi penting:**
- `clean_text(text)` — Proses satu string, kembalikan string bersih. Dipakai di training DAN inference.
- `preprocess_batch(texts)` — Terapkan `clean_text()` ke seluruh list/Series sekaligus.

**Apa itu stopwords?**

Stopwords adalah kata-kata yang sangat umum dan tidak memberikan informasi berguna untuk klasifikasi. Contohnya: `"yang"`, `"dan"`, `"di"`, `"ke"`, `"dari"`. Kata-kata ini ada di hampir setiap komentar, jadi tidak membantu model membedakan spam dari bukan spam.

---

### `src/train.py`

Script utama untuk melatih model. Menjalankan 5 tahap secara berurutan:

```
[1/5] Load dataset        → baca CSV, validasi kolom
[2/5] Preprocessing       → bersihkan semua teks
[3/5] Split data          → 80% train, 20% test
[4/5] Training SVM        → latih Pipeline (TF-IDF + SVM)
[5/5] Evaluasi            → cetak akurasi, precision, recall, F1
       ↓
  Simpan model ke model/svm_model.joblib
```

Parameter SVM yang dipakai:
- `kernel='linear'` — Fungsi pemisah berbentuk garis lurus. Terbaik untuk data teks
- `C=1.0` — Parameter regularisasi. Nilai kecil = model lebih "longgar" (generalisasi lebih baik), nilai besar = model lebih "ketat" (bisa overfitting)
- `class_weight='balanced'` — Otomatis menyesuaikan bobot jika jumlah spam dan bukan spam tidak seimbang
- `probability=True` — Mengaktifkan kemampuan model untuk mengeluarkan skor keyakinan (0–1), bukan hanya label

---

### `src/server.py`

REST API yang menjadi jembatan antara model Python dan extension JavaScript. Dibangun menggunakan FastAPI.

**Endpoints yang tersedia:**

| Method | URL | Fungsi |
|--------|-----|--------|
| GET | `/` | Health check, cek apakah server aktif |
| GET | `/health` | Cek status model apakah sudah dimuat |
| POST | `/predict` | Prediksi satu komentar |
| POST | `/predict/batch` | Prediksi banyak komentar sekaligus (maks. 50) |

**Contoh request & response untuk `/predict`:**

Request:
```json
{
  "text": "Daftar sekarang bonus 100% slot gacor!"
}
```

Response:
```json
{
  "label": "spam",
  "confidence": 0.9721,
  "is_spam": true
}
```

**Apa itu CORS?**

CORS (Cross-Origin Resource Sharing) adalah mekanisme keamanan browser yang mencegah halaman web membuat request ke domain yang berbeda tanpa izin eksplisit. Karena extension kita mengirim request dari `chrome-extension://...` ke `http://localhost:8000`, browser akan memblokir ini secara default. Mengaktifkan CORS di server adalah cara memberitahu browser bahwa request dari extension diizinkan.

**Hybrid Rules — eksperimen yang dicoba, diukur, lalu dimatikan**

`server.py` masih menyimpan kode `HARD_SPAM_SIGNALS` dan `has_hard_spam_signal()` — sisa dari eksperimen menambahkan lapisan rule-based di atas prediksi SVM. Idenya saat itu masuk akal: cegah false positive (SVM bilang spam tapi teks tidak punya kata judi pasti → override ke `non_spam`) dan cegah false negative (SVM bilang non_spam tapi teks punya kata judi pasti → override ke `spam`).

**Tapi setelah diukur dengan ablation study** (`src/evaluate_hybrid_ablation.py`, hasil tersimpan di `reports/hybrid_ablation.txt`), hybrid rule ini terbukti **menurunkan akurasi** dibanding SVM murni, di kedua dataset evaluasi:

| Dataset | SVM murni | SVM + Hybrid | Delta |
|---|---|---|---|
| Train-test split (1027 sampel) | 97.57% | 91.33% | **-6.23%** |
| Hard test set (141 sampel) | 92.91% | 80.14% | **-12.77%** |

Breakdown per-rule: Rule A (spam→non_spam) salah 62 dari 66 kali nyala di test set normal — kebanyakan spam asli memang tidak memuat kata persis dari daftar sinyal keras. Rule B (non_spam→spam) salah **100% dari 27 kali nyala** di kedua dataset — sering salah konteks pada komentar yang mengkritik judol (memuat kata "toto"/"togel" tapi bukan promosi).

**Kesimpulan:** begitu model dilatih ulang dengan dataset yang lebih besar (Versi 8, 5132 baris), SVM sendiri sudah lebih baik dari override kata-kunci manual yang dikalibrasi untuk model versi lama. Hybrid rule sekarang **dinonaktifkan** lewat flag `ENABLE_HYBRID_RULES = False` di `src/server.py` — kodenya sengaja tidak dihapus, supaya tetap jadi bukti proses eksperimen dan bisa diaktifkan ulang + diuji lagi kalau pola spam baru di masa depan menunjukkan kebutuhan berbeda.

---

### `extension/manifest.json`

File konfigurasi yang mendeskripsikan extension ke Chrome. Berisi informasi seperti nama, versi, izin yang dibutuhkan, dan halaman mana yang diizinkan diakses.

Izin penting yang diminta:
- `storage` — Menyimpan statistik (jumlah spam yang disembunyikan)
- `activeTab` — Mengakses tab yang sedang aktif
- `host_permissions` untuk `localhost:8000` — Mengizinkan komunikasi ke server lokal

---

### `extension/content.js`

Script yang di-inject Chrome ke dalam halaman YouTube/Instagram. Ini adalah "mata" dari extension.

Cara kerjanya:

```
1. Cek apakah server API aktif
        ↓
2. Scan semua elemen komentar yang ada di halaman
        ↓
3. Kumpulkan teks komentar yang belum pernah diproses
        ↓
4. Kirim ke API (batch request, maks. 50 sekaligus)
        ↓
5. Terima hasil prediksi
        ↓
6. Kalau confidence ≥ 75%  →  Sembunyikan komentar
        ↓
7. Pantau perubahan DOM (komentar baru saat scroll)
   → Ulangi dari langkah 2
```

**Apa itu MutationObserver?**

YouTube dan Instagram tidak memuat semua komentar sekaligus — komentar muncul secara bertahap saat pengguna scroll ke bawah. MutationObserver adalah API JavaScript yang "mengawasi" perubahan pada halaman. Setiap kali ada elemen baru ditambahkan ke halaman (termasuk komentar baru), observer ini memicu scan ulang.

**Apa itu WeakSet?**

`processedComments` menggunakan `WeakSet` untuk menyimpan referensi elemen komentar yang sudah pernah diproses. Ini mencegah komentar yang sama dikirim ke API dua kali. Menggunakan `WeakSet` (bukan `Set` biasa) karena WeakSet tidak mencegah garbage collection — ketika elemen HTML dihapus dari DOM, memorinya bisa dibebaskan secara otomatis.

---

### `extension/popup.html` dan `popup.js`

Antarmuka visual yang muncul saat pengguna mengklik ikon extension di toolbar Chrome. Menampilkan:
- Status server (aktif/tidak)
- Jumlah komentar spam yang disembunyikan (`hiddenCount`)
- Jumlah komentar yang sudah dipindai (`scannedCount`)
- Slider confidence threshold (default 75%) — mengubah nilainya langsung tersimpan ke `chrome.storage.local` dan dipakai `content.js` setelah halaman di-reload

---

## 9. Cara Kerja Sistem Secara Keseluruhan

Berikut alur lengkap dari awal hingga akhir, setiap kali pengguna membuka YouTube:

```
Pengguna buka YouTube
        │
        ▼
Chrome load content.js ke halaman
        │
        ▼
content.js cek ke localhost:8000/health
        │
   ┌────┴────┐
 Server    Server
 offline    online
   │           │
   ▼           ▼
 Extension  Mulai scan
 tidak      komentar
 aktif
        │
        ▼
Kumpulkan teks semua komentar yang terlihat
        │
        ▼
Kirim POST ke /predict/batch (maks. 50 sekaligus)
        │
        ▼
Server terima teks → clean_text() → model.predict()
        │
        ▼
Server kirim balik array hasil prediksi
        │
        ▼
Extension loop hasil:
  confidence ≥ 0.75 dan is_spam = true?
    ├── Ya  → Beri efek opacity 15%, tambah badge merah "⚠ Spam XX%"
    └── Tidak → Biarkan komentar tampil normal
        │
        ▼
MutationObserver pantau scroll/load komentar baru
        │
        ▼ (saat komentar baru muncul)
Ulangi proses scan untuk komentar yang belum diproses
```

---

## 10. Cara Meningkatkan Akurasi Model

### 1. Tambah lebih banyak data

Ini cara paling efektif. Untuk melatih ulang model dengan data baru:

```bash
# Langkah 1: Siapkan dataset (baca JSON scraping, generate non-spam)
python src/prepare_dataset.py

# Langkah 2: Latih ulang model
python src/train.py
```

**Panduan rasio data:**

| Kondisi | Rasio Spam:Non-Spam | Keterangan |
|---------|---------------------|-----------|
| Minimum | 1:1, ≥ 500 per kelas | Model bisa belajar tapi rentan overfit |
| Layak | 1:1 hingga 2:1, ≥ 1.500 per kelas | Performa produksi yang wajar |
| Ideal | 1:1, ≥ 3.000 per kelas, data non-spam nyata | Performa terbaik, false positive rendah |

> **Data non-spam sudah dari scraping nyata** (sejak Versi 2 di [DATASET_LOG.md](DATASET_LOG.md)), bukan template sintetis lagi. Untuk menambah lebih banyak, scrape video baru dengan `node scraper/index.js <VIDEO_ID> video non_spam` lalu jalankan `node scraper/filter.js` untuk update `scraper/final_non_spam.json`.

> **Penting:** Setiap kali `src/preprocessing.py` diubah, model wajib dilatih ulang. Lihat [Bagian 7 — Training-Serving Consistency](#7-training-serving-consistency) untuk penjelasan lengkapnya.

### 2. Coba nilai C yang berbeda

Di `src/train.py`, ubah nilai `C` pada bagian SVM:

```python
# C kecil (0.1): lebih generalis, mungkin kurang akurat di training tapi lebih baik di data baru
# C besar (10.0): lebih presisi di training, tapi bisa overfit
"svm", SVC(C=0.1, ...)   # coba ini
"svm", SVC(C=10.0, ...)  # atau ini
```

### 3. Tambah stopwords domain-spesifik

Tambahkan kata-kata netral yang sering muncul di komentar YouTube tetapi tidak relevan untuk klasifikasi spam:

```python
# Di src/preprocessing.py
STOPWORDS_ID.update({"kak", "bang", "subscribe", "like", "video", "nonton"})
```

### 4. Gunakan Sastrawi untuk stemming

Stemming adalah proses mengubah kata ke bentuk dasarnya. Misalnya: "mendaftar", "daftar", "pendaftaran" → semuanya jadi "daftar". Ini meningkatkan kemampuan model mengenali variasi kata.

```bash
pip install PySastrawi
```

```python
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

factory = StemmerFactory()
stemmer = factory.createStemmer()

# Di clean_text(), tambahkan setelah langkah stopwords:
text = stemmer.stem(text)
```

---

## 11. FAQ — Pertanyaan yang Mungkin Muncul

**Q: Kenapa harus ada server Python? Kenapa model tidak langsung dijalankan di extension?**

Browser extension hanya bisa menjalankan JavaScript. Scikit-learn adalah library Python dan tidak bisa dijalankan di JavaScript secara native. Solusinya adalah membuat server Python yang menjalankan model, lalu extension berkomunikasi dengan server tersebut via HTTP.

Alternatif lain yang lebih canggih adalah mengkonversi model ke format ONNX atau menggunakan TensorFlow.js, tapi itu jauh lebih kompleks dan tidak sebanding untuk skala proyek skripsi.

---

**Q: Apa itu file `.joblib`? Kenapa tidak pakai `.pkl` (pickle)?**

Keduanya adalah format serialisasi Python (cara menyimpan objek Python ke file). `joblib` lebih efisien dari `pickle` untuk menyimpan array numpy besar seperti yang ada di dalam model scikit-learn, sehingga file lebih kecil dan proses load/save lebih cepat.

---

**Q: Akurasi 97.39% di test set biasa, tapi kenapa hard test set juga 97.04%? Kok deketan?**

Karena dataset sudah cukup beragam dan bersih sehingga gap antara kasus "mudah" dan "ambigu" mengecil — itu justru indikator kualitas data yang baik, bukan kebetulan. Riwayat selisih ini dari waktu ke waktu: 80.14% (hybrid rules masih aktif) → 92.91% (hybrid dimatikan) → 97.04% (error analysis & data augmentation tertarget) → sempat naik ke 97.78% setelah scraping tambahan, **lalu turun lagi ke 97.04%** setelah ditemukan dan diperbaiki insiden kontaminasi data (61 komentar spam yang salah label non-spam, lihat [DATASET_LOG.md Versi 11](DATASET_LOG.md#versi-11--2026-06-30)). Penurunan terakhir itu disengaja — angka sebelumnya sebagian berasal dari model menghafal label yang salah.

Jalankan `python src/evaluate_hard_set.py` untuk melihat detail kegagalan yang tersisa. Riwayat lengkap tiap iterasi ada di [DATASET_LOG.md Versi 8-11](DATASET_LOG.md) dan [PENJELASAN_TEKNIS.md §33-34](PENJELASAN_TEKNIS.md).

---

**Q: Confidence threshold 75% itu dapat dari mana?**

Angka ini adalah keputusan desain, bukan hasil kalkulasi ilmiah. Artinya: model hanya akan menyembunyikan komentar jika yakin ≥ 75% bahwa itu spam. Default-nya ada di `extension/content.js`:

```javascript
let confidenceThreshold = 0.75; // fallback kalau belum ada nilai tersimpan di chrome.storage
```

Nilai ini **bisa diubah pengguna langsung dari slider di popup extension** (`extension/popup.html`/`popup.js`) tanpa edit kode — perubahannya disimpan ke `chrome.storage.local` dan baru berlaku penuh setelah halaman di-reload.
- Nilai lebih tinggi (0.90) → lebih sedikit false alarm, tapi lebih banyak spam yang lolos
- Nilai lebih rendah (0.60) → lebih banyak spam terdeteksi, tapi lebih banyak false alarm

---

**Q: Apa bedanya `precision` dan `recall`? Mana yang lebih penting?**

Tergantung konteks:

- **Precision tinggi penting** jika false alarm sangat mahal. Contoh: sistem medis yang salah diagnosis orang sehat sebagai sakit.
- **Recall tinggi penting** jika melewatkan kasus positif sangat berbahaya. Contoh: detektor spam ini — lebih baik terlalu banyak disembunyikan daripada spam berbahaya lolos.

Untuk proyek ini, **recall** untuk kelas `spam` adalah prioritas utama.

---

**Q: Bisa tidak modelnya dipakai tanpa server, langsung di-embed ke extension?**

Secara teknis bisa dengan menggunakan ONNX Runtime Web, tapi prosesnya sangat kompleks dan di luar scope skripsi. Pendekatan server lokal yang digunakan di sini adalah cara yang paling pragmatis dan mudah dipahami.

---

*Dokumentasi ini ditulis untuk mendampingi pengerjaan skripsi deteksi spam komentar judi online menggunakan SVM.*
