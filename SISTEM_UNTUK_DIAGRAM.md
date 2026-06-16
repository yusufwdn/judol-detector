# Penjelasan Sistem: Deteksi Komentar Spam Judi Online (Judol)

> **Tujuan file ini:** Memberikan penjelasan lengkap arsitektur sistem kepada AI (Gemini) agar dapat membuat diagram yang akurat sesuai sistem yang benar-benar dibangun.

---

## 1. Gambaran Umum Sistem

Sistem ini adalah **detektor komentar spam promosi judi online** yang bekerja secara otomatis di YouTube dan Instagram. Sistem terdiri dari tiga komponen utama:

| Komponen | Teknologi | Fungsi |
|---|---|---|
| **Model ML** | Python, scikit-learn (SVM) | Mengklasifikasikan teks komentar: spam atau bukan |
| **API Server** | Python, FastAPI | Jembatan antara browser extension dan model ML |
| **Browser Extension** | JavaScript, Manifest V3 | Mendeteksi komentar di halaman web dan menyembunyikan spam |

Ketiga komponen ini berjalan di komputer pengguna secara lokal (localhost). Tidak ada server eksternal.

---

## 2. Arsitektur Sistem (Gambaran Besar)

```
[YouTube / Instagram]
        |
        | (pengguna membuka halaman)
        v
[Chrome Extension - content.js]
  - Membaca elemen komentar di DOM
  - Mengambil teks mentah (raw text)
  - Mengirim ke API server via HTTP POST
        |
        | HTTP POST localhost:8000/predict/batch
        | Body: { "texts": ["komentar1", "komentar2", ...] }
        v
[FastAPI Server - server.py]
  - Menerima request
  - Menjalankan preprocessing (clean_text)
  - Menjalankan prediksi SVM
  - Mengembalikan hasil JSON
        |
        | Response: { "label": "spam", "confidence": 0.94, "is_spam": true }
        v
[Chrome Extension - content.js]
  - Jika is_spam == true DAN confidence >= 0.75:
    → Sembunyikan komentar (opacity 15%, tambahkan badge merah "Spam 94%")
  - Jika tidak:
    → Biarkan komentar tetap tampil
```

---

## 3. Fase Pengembangan Sistem

Sistem dikembangkan dalam dua fase besar yang terpisah:

### Fase A: Training (Offline / Satu Kali)

Dilakukan sekali di komputer developer untuk menghasilkan file model `svm_model.joblib`.

```
[scraper/final_result.json]  →  [prepare_dataset.py]  →  [data/comments.csv]
                                                                   |
                                                                   v
                                                          [train.py]
                                                          - Preprocessing teks
                                                          - Split data (80/20)
                                                          - Latih TF-IDF + SVM
                                                          - Evaluasi model
                                                          - Simpan model
                                                                   |
                                                                   v
                                                      [model/svm_model.joblib]
```

### Fase B: Inferensi (Online / Real-time)

Terjadi setiap kali pengguna membuka YouTube atau Instagram.

```
[Komentar di halaman web]
        |
        v
[Extension kirim ke API]
        |
        v
[Server: clean_text()]       ← fungsi yang SAMA dengan saat training
        |
        v
[Model SVM: predict()]       ← baca model dari svm_model.joblib
        |
        v
[Kembalikan label + confidence]
        |
        v
[Extension: sembunyikan jika spam]
```

---

## 4. Komponen Detail: Pembuatan Dataset (`prepare_dataset.py`)

Dataset dibuat dari dua sumber:

### Sumber 1: Data Spam (dari scraper)
- **Input:** `scraper/final_result.json` — 2.318 entri komentar hasil scraping YouTube
- **Metode filter: Two-Pass Filter**

```
[2.318 komentar dari JSON]
        |
        ├── Pass 1: spam_score >= 80
        │   Hasil: 137 komentar (komentar dengan skor spam tinggi)
        │
        └── Pass 2: Brand Regex Rescue
            Pola: \b[A-Z]{2,}\d+[A-Z0-9]*\b pada teks ternormalisasi
            (menangkap nama situs judi: ROMA4D, BET88, dll.)
            Hasil: 962 komentar tambahan yang diselamatkan

Total spam terkumpul: 1.099 komentar
```

### Sumber 2: Data Non-Spam (sintetis)
- **700 komentar** dibuat secara programatik dari template komentar wajar di YouTube (pujian, pertanyaan, diskusi, dsb.)
- Dibuat sintetis karena komentar non-spam tidak tersedia dari scraper

### Hasil Dataset Akhir
| Label | Jumlah |
|---|---|
| spam | 1.099 |
| non_spam | 700 |
| **Total** | **1.799** |

Disimpan ke: `data/comments.csv` (kolom: `text`, `label`)

---

## 5. Komponen Detail: Preprocessing Teks (`preprocessing.py`)

Setiap teks komentar melewati **7 tahap pembersihan** secara berurutan melalui fungsi `clean_text()`.

**Penting:** Fungsi ini digunakan **identik** saat training dan saat inferensi untuk memastikan konsistensi.

```
[Teks Mentah]
      |
      v
[Step 1] Hapus karakter zero-width (invisible)
         → karakter U+200B, U+200C, U+200D, U+FEFF, dll.
         → Contoh: "d​a​f​t​a​r" → "daftar"
      |
      v
[Step 2] NFKC Unicode Normalization
         → Ubah font dekoratif ke ASCII biasa
         → Contoh: "𝑅𝒪𝑀𝒜𝟦𝒟" → "ROMA4D"
         → Contoh: "Ｄａｆｔａｒ" → "Daftar"
      |
      v
[Step 3] Homoglyph Fix (Cyrillic/Greek → Latin)
         → NFKC tidak bisa lintas script
         → Contoh: "dаftаr" (Cyrillic а) → "daftar" (Latin a)
      |
      v
[Step 4] Emoji Demojize
         → Ubah emoji ke token teks deskriptif
         → Contoh: 🎰 → "slot_machine"
         → Contoh: 💰 → "money_bag"
      |
      v
[Step 5] Lowercase
         → "Daftar" → "daftar"
      |
      v
[Step 6] Hapus URL dan karakter non-alfabet
         → Hapus http://, www., tanda baca, angka, simbol
      |
      v
[Step 7] Hapus stopwords Bahasa Indonesia + token pendek
         → Hapus: yang, dan, di, ke, dari, gua, dll. (80+ kata)
         → Hapus token dengan panjang <= 1 karakter
      |
      v
[Teks Bersih - siap untuk TF-IDF]
```

---

## 6. Komponen Detail: Training Model (`train.py`)

### Pipeline Scikit-learn

Model dibangun sebagai satu Pipeline berisi dua tahap:

```
[Teks Bersih]
      |
      v
[Stage 1: TF-IDF Vectorizer]
  Parameter:
  - max_features = 10.000 (ambil 10.000 fitur terpenting)
  - ngram_range  = (1, 2) (unigram + bigram)
  - min_df       = 2 (abaikan kata yang muncul < 2 dokumen)
  - sublinear_tf = True (gunakan log(TF) untuk redamkan frekuensi tinggi)
      |
      | Output: vektor numerik sparse [0.0, 0.03, 0.12, 0.0, ...]
      v
[Stage 2: SVM Classifier]
  Parameter:
  - kernel        = 'linear' (terbaik untuk data teks berdimensi tinggi)
  - C             = 1.0 (regularisasi sedang)
  - class_weight  = 'balanced' (kompensasi ketidakseimbangan kelas)
  - probability   = True (aktifkan skor kepercayaan via Platt Scaling)
  - random_state  = 42
      |
      v
[Label: "spam" / "non_spam" + Confidence Score 0.0-1.0]
```

### Pembagian Data Training/Testing

```
[1.799 baris dataset]
        |
        | train_test_split(test_size=0.2, random_state=42, stratify=y)
        |
        ├── Training Set: 1.439 sampel (80%)  → digunakan untuk melatih model
        └── Test Set    :   360 sampel (20%)  → digunakan untuk evaluasi saja
```

### Proses Training (5 langkah berurutan)

```
[1/5] Load dataset dari data/comments.csv
[2/5] Preprocessing semua teks via preprocess_batch()
[3/5] Split data 80/20 (stratified)
[4/5] Fit Pipeline (TF-IDF → SVM) pada training set
[5/5] Evaluasi pada test set → cetak classification report
      Simpan model ke model/svm_model.joblib
```

---

## 7. Komponen Detail: API Server (`server.py`)

### Teknologi
- **Framework:** FastAPI (Python)
- **Runtime:** Uvicorn (ASGI server)
- **Alamat:** `http://localhost:8000`
- **CORS:** Diizinkan dari semua origin (`*`) — karena browser extension perlu akses

### Endpoint API

| Method | Path | Fungsi |
|---|---|---|
| GET | `/` | Cek server aktif |
| GET | `/health` | Cek apakah model sudah ter-load |
| POST | `/predict` | Klasifikasi satu komentar |
| POST | `/predict/batch` | Klasifikasi banyak komentar sekaligus (maks. 50) |

### Alur Request `/predict/batch` (yang digunakan extension)

```
[Extension kirim POST /predict/batch]
Body: { "texts": ["komentar A", "komentar B", ...] }
        |
        v
[Pydantic validasi input]
  - texts harus array of string
  - Maks. 50 item
        |
        v
[Loop setiap teks:]
  1. clean_text(teks)           → teks bersih
  2. model.predict([bersih])    → "spam" atau "non_spam"
  3. model.predict_proba([...]) → probabilitas [non_spam_prob, spam_prob]
  4. Ambil confidence sesuai label yang diprediksi
        |
        v
[Kembalikan JSON]
{
  "results": [
    { "label": "spam", "confidence": 0.94, "is_spam": true },
    { "label": "non_spam", "confidence": 0.87, "is_spam": false },
    ...
  ]
}
```

### Model Loading

- Model di-load **sekali saat server startup** dari `model/svm_model.joblib`
- Tidak di-load ulang setiap request (terlalu lambat)
- Endpoint `/health` mengembalikan `model_loaded: true/false`

---

## 8. Komponen Detail: Chrome Extension

### File-file Extension

| File | Fungsi |
|---|---|
| `manifest.json` | Konfigurasi extension (permission, target URL, dll.) |
| `content.js` | Script utama yang diinjeksi ke halaman YouTube/Instagram |
| `popup.html` | UI popup saat klik ikon extension di toolbar |
| `popup.js` | Logic popup (tampilkan jumlah spam tersembunyi) |

### Cara Kerja `content.js`

```
[Halaman YouTube/Instagram dibuka]
        |
        v
[init()] → checkServerHealth()
  - GET http://localhost:8000/health
  - Jika server tidak aktif → extension tidak jalan (diam)
  - Jika server aktif → lanjut
        |
        v
[scanComments()] — scan awal
  - Cari elemen komentar di DOM:
    - YouTube: ytd-comment-thread-renderer > #content-text
    - Instagram: ul._a9ym li > span._aacl
  - Ambil teks komentar
  - Tandai elemen di WeakSet (processedComments) agar tidak diproses 2x
  - Kirim batch ke /predict/batch (maks. 50 per request)
        |
        v
[MutationObserver aktif]
  - Memantau perubahan DOM (komentar baru muncul saat scroll)
  - Debounce 1 detik setelah DOM berubah
  - Panggil scanComments() lagi untuk komentar baru
        |
        v
[Untuk setiap hasil prediksi:]
  if (is_spam == true AND confidence >= 0.75):
    → hideSpamComment(element, confidence)
       - opacity: 15%
       - border merah
       - tambahkan badge "Spam XX%"
       - badge bisa diklik untuk reveal komentar
  else:
    → biarkan komentar tampil normal
```

### Target Platform & Selector CSS

| Platform | Container Selector | Teks Selector |
|---|---|---|
| YouTube | `ytd-comment-thread-renderer` | `#content-text` |
| Instagram | `ul._a9ym li` | `span._aacl` |

### Permission (manifest.json)

```json
{
  "permissions": ["storage", "activeTab"],
  "host_permissions": [
    "http://localhost:8000/*",
    "https://www.youtube.com/*",
    "https://www.instagram.com/*"
  ]
}
```

---

## 9. Keputusan Arsitektur Penting

### 9.1 Preprocessing hanya di Python, bukan di JavaScript

**Masalah:** Extension berjalan di JavaScript, server di Python. Jika preprocessing dilakukan di JS, ada risiko perbedaan hasil karena perbedaan cara kedua bahasa menangani Unicode dan regex.

**Solusi:** Extension hanya mengirim teks mentah. Semua normalisasi terjadi di `clean_text()` di Python — fungsi yang **sama persis** dengan yang digunakan saat training.

### 9.2 Pipeline scikit-learn (bukan langkah terpisah)

**Masalah:** Jika TF-IDF di-fit pada seluruh dataset sebelum split, informasi test set bocor ke training → evaluasi tidak jujur (data leakage).

**Solusi:** TF-IDF dan SVM dibungkus dalam `sklearn.Pipeline`. Pipeline hanya di-fit pada training set. Saat transform test set, TF-IDF sudah dalam keadaan fitted (tidak belajar lagi dari test set).

### 9.3 Two-Pass Filter untuk dataset spam

**Masalah:** Filter tunggal `spam_score >= 80` hanya menghasilkan 137 data spam — terlalu sedikit.

**Solusi:** Pass 2 menambahkan regex khusus untuk mendeteksi nama situs judi (pola `\b[A-Z]{2,}\d+[A-Z0-9]*\b` seperti ROMA4D, BET88) pada teks yang sudah dinormalisasi. Menghasilkan 962 data tambahan → total 1.099 spam.

### 9.4 Confidence threshold 0.75

Extension hanya menyembunyikan komentar jika `confidence >= 0.75` (75%). Ini trade-off antara:
- **Terlalu rendah** → banyak komentar normal ikut tersembunyi (false positive tinggi)
- **Terlalu tinggi** → banyak spam lolos (false negative tinggi)

---

## 10. Struktur Folder Proyek

```
svm-judol-spam/
├── data/
│   └── comments.csv          # Dataset final (1.799 baris: text, label)
│
├── extension/
│   ├── manifest.json         # Konfigurasi Chrome Extension (Manifest V3)
│   ├── content.js            # Script utama yang diinjeksi ke halaman
│   ├── popup.html            # UI popup extension
│   ├── popup.js              # Logic popup
│   └── icons/                # Ikon extension (16px, 48px, 128px)
│
├── model/
│   └── svm_model.joblib      # Model terlatih (TF-IDF + SVM Pipeline)
│
├── scraper/
│   ├── index.js              # Scraper YouTube (Node.js)
│   └── final_result.json     # Hasil scraping mentah (2.318 komentar)
│
├── src/
│   ├── prepare_dataset.py    # Buat dataset dari JSON scraper
│   ├── preprocessing.py      # Fungsi clean_text() — 7 tahap normalisasi
│   ├── train.py              # Training pipeline TF-IDF + SVM
│   └── server.py             # FastAPI server — endpoint /predict
│
└── requirements.txt          # Dependensi Python
```

---

## 11. Alur Data End-to-End (Lengkap)

```
[FASE PERSIAPAN - dilakukan sekali]

1. Scraping
   scraper/index.js (Node.js)
   → YouTube comment scraping
   → Output: scraper/final_result.json (2.318 entri)

2. Pembuatan Dataset
   src/prepare_dataset.py
   → Two-pass filter dari JSON
   → Generate 700 non-spam sintetis
   → Output: data/comments.csv (1.799 baris)

3. Training
   src/train.py
   → Load comments.csv
   → Preprocessing via preprocess_batch()
   → Split 80/20 (stratified)
   → Fit Pipeline(TF-IDF, SVM) pada 1.439 training samples
   → Evaluasi pada 360 test samples
   → Output: model/svm_model.joblib


[FASE PRODUKSI - terjadi setiap saat]

4. Server Aktif
   src/server.py (FastAPI)
   → Load svm_model.joblib saat startup
   → Dengarkan di http://localhost:8000

5. Pengguna Buka YouTube/Instagram
   extension/content.js
   → Cek kesehatan server (/health)
   → Scan komentar di DOM
   → Kirim batch teks ke /predict/batch

6. Server Proses Request
   → clean_text() setiap komentar
   → model.predict() + model.predict_proba()
   → Return JSON {label, confidence, is_spam}

7. Extension Terapkan Hasil
   → Jika spam AND confidence >= 0.75: sembunyikan komentar
   → MutationObserver pantau komentar baru (infinite scroll)
   → Ulangi langkah 5-7 untuk komentar baru
```

---

## 12. Teknologi yang Digunakan

| Kategori | Teknologi | Versi / Keterangan |
|---|---|---|
| Bahasa (ML/Server) | Python | 3.10+ |
| ML Framework | scikit-learn | Pipeline, SVC, TfidfVectorizer |
| API Framework | FastAPI + Uvicorn | REST API, ASGI |
| Validasi Input | Pydantic v2 | field_validator |
| Serialisasi Model | joblib | Simpan/load Pipeline |
| Data Processing | pandas | Load CSV, value_counts |
| Text Processing | unicodedata, emoji, re | NFKC, demojize, regex |
| Browser Extension | JavaScript | Manifest V3, MutationObserver |
| Scraper | Node.js | Scraping komentar YouTube |
| Platform Target | YouTube, Instagram | Deteksi via hostname + CSS selector |
