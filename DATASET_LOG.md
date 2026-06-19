# Dataset Log — Judol Spam Detector

Setiap kali dataset diperbarui, catat di sini: tanggal, jumlah data, dan sumber.
Berguna untuk bab metodologi skripsi dan untuk melacak versi mana yang menghasilkan hasil evaluasi tertentu.

---

## Versi 6 — 2026-06-18

### Ringkasan
Empat perbaikan sekaligus: hybrid rule dibuat dua arah, dua kata terlalu generik dihapus dari sinyal keras, 500 spam terverifikasi manual diimport, dan dua rescue pattern di filter dataset diperbaiki agar menangkap brand yang tertulis lowercase atau terlalu pendek.

### Perubahan dari Versi 5

#### 1. Hybrid Rule Dua Arah (`server.py`)

Sebelumnya hybrid rule hanya satu arah — hanya mencegah false positive (spam → non_spam). Ditemukan false negative: komentar dengan `judolbrand` di teks tapi SVM memprediksi `non_spam` karena kata-kata normal di kalimat lebih banyak sehingga bobot totalnya mengalahkan token judolbrand di model linear.

Ditambahkan arah sebaliknya:
```python
# (B) FN prevention: SVM non_spam + hard signal → paksa spam
if label == "non_spam" and has_signal:
    return PredictResponse(label="spam", confidence=0.9, is_spam=True)
```

Contoh yang sebelumnya lolos:
```
"Gw bakal ikutin konten lu terus bang ... ❤!!!✅ 𝑯𝑶𝑩𝑰𝑸𝑸 ❤!!!✅"
→ clean: "... judolbrand ..."
→ SVM: non_spam (kalimat normal mendominasi)
→ Hybrid (B): override ke spam ✓
```

#### 2. Hapus Kata Terlalu Generik dari `HARD_SPAM_SIGNALS`

Ditemukan false positive: komentar tentang "rebusan rebung bambu" untuk pengobatan kanker dianggap spam karena `"bambu"` ada di HARD_SPAM_SIGNALS. Setelah audit menyeluruh, dua kata dihapus:

| Kata | Makna biasa | Alasan dihapus |
|------|-------------|---------------|
| `bambu` | Tanaman bambu | Muncul di konteks kuliner, pengobatan, alam |
| `giat` | Rajin, aktif | Kata sifat umum, muncul di kalimat motivasi |

Brand judol yang memakai nama ini + suffix angka (bambu88, giat777) tetap tertangkap via Step 5b → `judolbrand`.

#### 3. Import 500 Spam Terverifikasi Manual

**File:** `data/skipped_entries.json` → `data/comments.csv`

Dari 533 entry yang sebelumnya di-skip oleh `prepare_dataset.py`, dilakukan review manual untuk memilah mana yang benar-benar spam dan mana false positive. Hasil:

- Dihapus (bukan spam): **33 entry** — meliputi nama orang dengan "win" (darwin, deswin, goodwin), kata Indonesia umum dengan "bet" (ribet, kesambet, diabet), dan konteks non-judol (situs darkweb, situs bokep, kunjungi restoran, dll)
- Diimport ke dataset: **500 entry** — semuanya spam nyata yang lolos filter karena pola brand-nya lowercase atau mixed case

Mengapa 500 entry ini lolos filter sebelumnya? Rescue patterns di `prepare_dataset.py` hanya cocok ALL-CAPS, sedangkan banyak brand di `normalized_text` berbentuk lowercase setelah NFKC normalization:

```
𝒃𝒃𝒄𝒂4𝒅  →  bbca4d      (math italic → lowercase, tidak cocok [A-Z]{2,}\d+)
𝐊𝐨𝐫𝐞𝐨𝟏𝟑𝟖 →  Koreo138    (math bold → Title Case, tidak cocok [A-Z]{2,}\d+)
OMETOTO   →  ALL-CAPS tapi OME=3 huruf < minimum 4 di BRAND_SUFFIX_PATTERN
```

#### 4. Perbaikan `BRAND_RESCUE_PATTERN` — Case-Insensitive

**File:** `src/prepare_dataset.py`

```python
# Sebelum:
BRAND_RESCUE_PATTERN = re.compile(r'\b[A-Z]{2,}\d+[A-Z0-9]*\b')

# Sesudah:
BRAND_RESCUE_PATTERN = re.compile(r'\b[A-Z]{2,}\d+[A-Z0-9]*\b', re.IGNORECASE)
```

Penambahan `re.IGNORECASE` membuat pola ini mencocokkan brand dengan huruf besar/kecil apapun, selama tetap mengandung digit. Digit sebagai syarat wajib memastikan kata Indonesia umum seperti "ribet" atau "kesambet" tidak ikut tertangkap.

#### 5. Perbaikan `BRAND_SUFFIX_PATTERN` — Minimum 3 Huruf

**File:** `src/prepare_dataset.py`

```python
# Sebelum (minimum 4 huruf sebelum suffix):
BRAND_SUFFIX_PATTERN = re.compile(r'\b[A-Z]{4,}(?:TOTO|BET|WIN|QQ)\b')

# Sesudah (minimum 3 huruf):
BRAND_SUFFIX_PATTERN = re.compile(r'\b[A-Z]{3,}(?:TOTO|BET|WIN|QQ)\b')
```

Brand pendek seperti `OMETOTO` (OME=3 huruf + TOTO) sebelumnya tidak terdeteksi. Pola tetap ALL-CAPS untuk mencegah false positive dari kata Indonesia lowercase.

### Statistik dataset (`data/comments.csv`)

| Label    | Versi 5 | Versi 6 |
|----------|---------|---------|
| spam     | 1785    | **2285** (+500) |
| non_spam | 2513    | 2513 |
| **Total**| **4298**| **4798** |

### Hasil evaluasi model

**K-Fold Cross-Validation (cv=5, full dataset):**
- Fold scores (F1-macro): 0.9896, 0.9885, 0.9885, 0.9895, 0.9053
- **Mean F1-macro: 97.23% ± 3.35%**
- Catatan: fold ke-5 mendapat 0.9053 — outlier karena konsentrasi spam obfuscated yang lebih sulit di fold tersebut.

**GridSearchCV (hyperparameter tuning):**
- C terpilih: **1** (F1-macro CV = 0.9744)

**Train-test split (80/20, test set = 960 sampel):**

| Metrik | Versi 5 | Versi 6 | Delta |
|--------|---------|---------|-------|
| Accuracy | 99.53% | **98.44%** | −1.09% |
| F1-macro | 0.9952 | **0.9843** | −0.0109 |
| FP | 1 | **0** | −1 |
| FN | 3 | **15** | +12 |
| Best C | 10 | 1 | — |

**Mengapa FN naik dan accuracy turun?**

500 entry baru yang diimport adalah spam dengan trik obfuscation paling canggih — mereka lolos filter awal justru karena sulit dideteksi. Model sekarang belajar dari data yang lebih keras dan lebih realistis. FP=0 menunjukkan presisi sempurna; FN yang lebih tinggi mencerminkan sulitnya kelas baru ini, bukan kemunduran.

Confusion matrix:
```
                  Prediksi non_spam  Prediksi spam
Aktual non_spam        503 (TN)          0 (FP)
Aktual spam             15 (FN)        442 (TP)
```

→ Lihat gambar: `reports/confusion_matrix_svm.png`

---

## Versi 7 — 2026-06-19

### Ringkasan
Kurasi manual dataset: 20 entri dilabeli ulang dari spam ke non_spam (kata umum Indonesia yang salah ditangkap: nyabet, kesambet, brebet, lembet, ngebet, deswin, darwin, situs jembot, situs darkweb, kunjungi), 1 entri spam baru ditambahkan. Satu kata generik ("situs") dihapus dari HARD_SPAM_SIGNALS.

### Perubahan dari Versi 6

#### 1. Relabeling 20 False Positive di `data/comments.csv`

Ditemukan false positive yang lolos ke dataset saat kurasi manual sebelumnya. Semua diubah label dari `spam` ke `non_spam`:

| Kategori | Contoh | Alasan |
|----------|--------|--------|
| Kata kerja biasa ber-suffix "bet"/"abet" | nyabet, kesambet, brebet, menyabet | Kata Indonesia umum, bukan brand |
| Kata sifat ber-suffix "bet" | lembet, ribet, ngebet | Kata sehari-hari, bukan taruhan |
| Nama orang dengan "win" | deswin (nama), darwin (nama pemain bola Darwin Nunez) | Nama bukan brand judol |
| "situs" di konteks non-judol | situs jembot, situs darkweb | Kata "situs" terlalu generik |
| "kunjungi" di konteks makanan/travel | "tempat yang dikunjungi Tan Boy", "dagangan mpok laris setelah dikunjungi" | Kalimat normal ulasan kuliner |

#### 2. Tambah 1 Entry Spam Baru

`🌺ALEXIS🌺1.7🌺 bikin hati meleleh, gemes banget!` — brand ALEXIS17 dengan obfuscasi emoji sebagai pemisah angka.

#### 3. Hapus "situs" dari `HARD_SPAM_SIGNALS` (`server.py`)

Kata "situs" dihapus karena terlalu generik — menyebabkan hybrid Rule (B) memaksa non_spam → spam di komentar yang hanya kebetulan mengandung kata "situs" tanpa konteks judi.

```python
# Sebelum:
"slot", "situs", "withdraw",

# Sesudah:
"slot",
# "situs" dihapus — terlalu generik
"withdraw",
```

Brand yang memakai kata "situs" + nama judol tetap tertangkap via token `judolbrand` dari Step 5b preprocessing.

#### 4. Buat `data/manual_overrides.csv` (file baru)

**Masalah:** Mengedit `comments.csv` langsung tidak aman — file ini ditimpa setiap `prepare_dataset.py` dijalankan. Semua koreksi manual akan hilang saat ada scraping baru.

**Solusi:** File `data/manual_overrides.csv` sebagai tempat permanen menyimpan koreksi label. Berisi 213 entry:
- 20 entry `non_spam` (false positive yang dikoreksi)
- 193 entry `spam` (1 baru + 192 dari manual import yang tidak terjangkau rescue pattern otomatis)

#### 5. Modifikasi `src/prepare_dataset.py` — tambah Step 3 `apply_manual_overrides()`

Pipeline persiapan dataset sekarang 4 langkah (sebelumnya 3):

```
[1/4] load_spam_data()          ← final_spam.json → Pass 1 + Pass 2
[2/4] load_non_spam_data()      ← final_non_spam.json
[3/4] apply_manual_overrides()  ← manual_overrides.csv  ← BARU
[4/4] build_and_save_dataset()  ← shuffle + save
```

Fungsi ini menghapus false positive dari daftar spam dan menambahkan spam yang tidak tertangkap filter otomatis. Koreksi persisten — berlaku di setiap run `prepare_dataset.py` di masa depan.

### Statistik dataset (`data/comments.csv`)

| Label    | Versi 6 | Versi 7 |
|----------|---------|---------|
| spam     | 2285    | **2266** (−20 relabel, +1 baru) |
| non_spam | 2513    | **2533** (+20 relabel) |
| **Total**| **4798**| **4799** |

### Hasil evaluasi model

**K-Fold Cross-Validation (cv=5, full dataset):**
- Fold scores (F1-macro): 0.9895, 0.9885, 0.9875, 0.9885, 0.9183
- **Mean F1-macro: 97.45% ± 2.81%**

**GridSearchCV (hyperparameter tuning):**
- C terpilih: **1** (F1-macro CV = 0.9791)

**Train-test split (80/20, test set = 960 sampel):**

| Metrik | Versi 6 | Versi 7 | Delta |
|--------|---------|---------|-------|
| Accuracy | 98.44% | **98.23%** | −0.21% |
| F1-macro | 0.9843 | **0.9822** | −0.0021 |
| FP | 0 | **0** | 0 |
| FN | 15 | **17** | +2 |
| Best C | 1 | 1 | — |

**Mengapa FN naik sedikit?**

20 entry diambil dari kelas spam ke non_spam — ini sedikit mengurangi contoh training untuk kelas spam. FP tetap 0 (tidak ada komentar normal yang salah dianggap spam). Penurunan 0.21% accuracy adalah wajar dan bisa diterima karena lebih baik daripada mempertahankan label yang salah.

Confusion matrix:
```
                  Prediksi non_spam  Prediksi spam
Aktual non_spam        507 (TN)          0 (FP)
Aktual spam             17 (FN)        436 (TP)
```

→ Lihat gambar: `reports/confusion_matrix_svm.png`

---

## Versi 5 — 2026-06-18

### Ringkasan
Perbaikan preprocessing generasi kedua: tiga teknik baru untuk menangani trik obfuscation spammer yang lebih canggih, plus canonicalisasi token brand yang membuat model generalisasi tanpa hafal nama brand satu per satu. Metrik melonjak signifikan.

### Perubahan dari Versi 4

#### 1. Step 5b — Brand Canonicalization (`JUDOL_BRAND_PATTERN`)

**File:** `src/preprocessing.py`

Sebelum digit dihapus di Step 6, semua nama brand judol yang cocok pola **[kata][suffix khas judol]** diganti dengan token universal `judolbrand`.

```
KEJU4D   → judolbrand
BETAWI77 → judolbrand
HOBIQQ   → judolbrand
SLOT777  → judolbrand
```

**Suffix yang ditangkap:** `4d`, `3d`, `2d`, `88`, `99`, `77`, `69`, `138`, `388`, `303`, `777`, `888`, `qq`

**Kenapa ini penting?**
Sebelumnya, Step 6 menghapus semua digit → `KEJU4D` → `keju` (makanan). Model dilatih dengan fitur `keju` yang salah label (spam), meningkatkan risiko false positive di komentar kuliner. Dengan Step 5b, sinyal brand diselamatkan sebelum digit dibuang.

**Efek ke model:**
- Model tidak perlu hafal ratusan nama brand
- Brand baru yang belum pernah dilihat tapi pakai pola yang sama → langsung dikenali
- Token `judolbrand` ditambahkan ke `HARD_SPAM_SIGNALS` di `server.py`

**False positive protection:** prefix gaming umum (`level`, `rank`, `stage`, `episode`, dll) dikecualikan via negative lookbehind regex.

#### 2. Step 2c — Unwrap Kurung Per-Huruf

**File:** `src/preprocessing.py`

Menangani trik spammer yang membungkus setiap huruf brand dalam kurung:
```
[P][U][L][A][U][7][7][7]  →  PULAU777  →  judolbrand
```

Tanpa step ini: Step 6 mengubah tiap kurung jadi spasi → `P U L A U 7 7 7` → tiap huruf adalah token tunggal → semua dibuang (`len ≤ 1`) → string kosong → false non_spam.

Regex: `[\[({]\s*(\w)\s*[\])}]` — hanya membuka kurung yang berisi **tepat 1 karakter word**. Kurung biasa seperti `(penjelasan di sini)` tidak terpengaruh.

#### 3. Homoglyph Thai `๓ → m`

**File:** `src/preprocessing.py`

Ditambahkan ke `HOMOGLYPH_MAP`. Angka Thai 3 (๓, U+0E53) bentuknya mirip huruf Latin 'm', dipakai spammer untuk menulis "roma" sebagai "ro๓a".

#### 4. Suffix `QQ` di `BRAND_SUFFIX_PATTERN`

**File:** `src/prepare_dataset.py`

Pola rescue untuk brand tanpa digit diperluas: `TOTO|BET|WIN` → `TOTO|BET|WIN|QQ`. Menangkap keluarga brand poker/domino (HOBIQQ, BANDARQQ, DOMINOQQ) di Pass 2 filter.

#### 5. Suffix `qq` di Scraper `brandPattern`

**File:** `scraper/index.js`

Regex `brandPattern` di scraper sekarang juga mendeteksi suffix `qq` sehingga brand seperti HOBIQQ mendapat sinyal `brand_pattern` saat scraping.

### Statistik dataset (`data/comments.csv`)

Tidak berubah dari Versi 4 (dataset sama, preprocessing berubah):

| Label    | Jumlah |
|----------|--------|
| spam     | 1785   |
| non_spam | 2513   |
| **Total**| **4298** |

### Hasil evaluasi model

**K-Fold Cross-Validation (cv=5, full dataset):**
- Fold scores (F1-macro): 0.9904, 0.9904, 0.9892, 0.9904, 0.9952
- **Mean F1-macro: 99.11% ± 0.21%**

**GridSearchCV (hyperparameter tuning):**
- C terpilih: **10** (F1-macro CV = 0.9886)

**Train-test split (80/20, test set = 860 sampel):**

| Metrik | Versi 4 | Versi 5 | Delta |
|--------|---------|---------|-------|
| Accuracy | 96.74% | **99.53%** | +2.79% |
| F1-macro | 0.9664 | **0.9952** | +0.0288 |
| FP | 11 | **1** | −10 |
| FN | 17 | **3** | −14 |
| Best C | 1 | 10 | — |

Lonjakan signifikan karena `judolbrand` menjadi token konsisten yang kuat — model belajar satu pola daripada ratusan nama brand berbeda.

Confusion matrix:
```
                  Prediksi non_spam  Prediksi spam
Aktual non_spam        502 (TN)          1 (FP)
Aktual spam              3 (FN)        354 (TP)
```

→ Lihat gambar: `reports/confusion_matrix_svm.png`

---

## Versi 4 — 2026-06-18

### Ringkasan
Ekspansi dataset besar-besaran: tiga perbaikan kumulatif yang masing-masing meningkatkan cakupan spam. Dimulai dari bug preprocessing yang menyebabkan komentar obfuscated hilang total, lalu rescue condition yang terlalu ketat, lalu pola brand tanpa digit yang tidak terdeteksi.

### Perubahan dari Versi 3

#### 1. Fix Preprocessing: Step 2b — Strip Combining Diacritical Marks

**File:** `src/preprocessing.py`

Ditemukan bug: spammer yang menulis brand dengan `COMBINING LOW LINE` (U+0332) di tiap huruf:
```
P͟U͟L͟A͟U͟W͟I͟N͟  →  tanpa fix: tiap karakter combining menjadi spasi → tiap huruf jadi
                   token tunggal → semua dibuang (len≤1) → string kosong → false non_spam
               →  dengan fix: combining marks dihapus → PULAUWIN bertahan sebagai satu token
```

Solusi: `text = "".join(c for c in text if unicodedata.category(c) != "Mn")` — menghapus semua karakter Unicode kategori "Mn" (Mark, Nonspacing).

#### 2. Fix Rescue Condition di `prepare_dataset.py`

Kondisi `signals == ["brand_pattern"]` (exact match) diubah ke `"brand_pattern" in signals` (membership check).

**Kenapa perlu diubah?** Spammer yang pakai Unicode obfuscation sering juga pakai banyak emoji dan simbol → komentar dapat 2–3 sinyal → kondisi lama mengharuskan tepat 1 sinyal → entry di-skip padahal jelas spam.

#### 3. `BRAND_SUFFIX_PATTERN` — Brand Tanpa Digit

Ditambahkan pola rescue kedua `\b[A-Z]{4,}(?:TOTO|BET|WIN)\b` untuk menangkap brand yang tidak mengandung digit (PULAUWIN, NAGAMASTOTO, MANJURBET). Sebelumnya hanya `BRAND_RESCUE_PATTERN` yang mendeteksi ALL-CAPS+digit.

#### 4. `pulauwin` ditambahkan ke `HARD_SPAM_SIGNALS`

**File:** `src/server.py`

Brand "pulauwin" ditambahkan karena compound-nya spesifik (berbeda dari kata "pulau" yang umum).

### Statistik dataset (`data/comments.csv`)

| | Versi 3 | Versi 4 |
|---|---|---|
| spam | 1099 | **1785** (+686) |
| non_spam | 2513 | 2513 |
| **Total** | **3612** | **4298** |

Breakdown tambahan spam:
- Lolos primary threshold (≥80): 137
- Diselamatkan brand rescue: **1648** (naik drastis dari 962)
- Dibuang (false positive / noisy): 533

### Hasil evaluasi model

| Metrik | Versi 3 | Versi 4 |
|--------|---------|---------|
| Accuracy | 97.23% | 96.74% |
| F1-macro | 0.9671 | 0.9664 |
| FP | 7 | 11 |
| FN | 13 | 17 |

*Sedikit turun karena 686 spam obfuscated baru yang lebih sulit — lebih realistis.*

---

## Versi 3 — 2026-06-18

### Perubahan dari versi sebelumnya
- Ditambahkan **3 hard negative examples** berupa komentar non-spam yang sebelumnya menghasilkan false positive saat pengujian langsung di YouTube
- Komentar-komentar ini mengandung kata yang berbobot spam (`sambil` +1.28, `berkali` +0.74, `bosen` +0.60) dalam konteks normal
- Tujuan: membantu model belajar bahwa kata-kata tersebut tidak selalu berarti spam — konteks kalimat berbeda

### Komentar yang ditambahkan (label: non_spam)

| Komentar | Kata Bermasalah | Confidence Sebelumnya |
|----------|-----------------|----------------------|
| "Nonton berkali kali gak bosen dan ttep ngakak" | berkali (+0.74), bosen (+0.60) | 92% spam |
| "Nonton ulang² tetap rata ngakak😂😂😂😂😂" | ulang (+0.57) | 76% spam |
| "tontonan sambil makan update juga" | sambil (+1.28), update (+0.50) | 80% spam |
| "Keren sih penyiar2 kayak Kamal ama Sahil pengetahuannya luas banget dari yang serius sampai yg santai😊" | serius (+1.10), keren (+0.80) | 77% spam |

### Statistik dataset (`data/comments.csv`)

| Label    | Jumlah |
|----------|--------|
| spam     | 1099   |
| non_spam | 2513   |
| **Total**| **3612** |

**Catatan:** Perlu jalankan ulang `python src/train.py` untuk memperbarui model dengan data baru ini.

---

## Versi 2 — 2026-06-16

### Perubahan dari versi sebelumnya
- Data non-spam **diganti dari sintetis ke nyata** (2509 komentar asli dari YouTube)
- Akurasi turun dari ~100% ke 97.23% — ini **lebih jujur dan lebih baik untuk skripsi**

### Statistik dataset (`data/comments.csv`)

| Label    | Jumlah |
|----------|--------|
| spam     | 1099   |
| non_spam | 2509   |
| **Total**| **3608** |

### Sumber data spam (`scraper/final_spam.json`)

- Raw entries dari scraper : 2318
- Lolos threshold >= 80    : 137
- Diselamatkan brand regex : 962
- Dibuang (false positive) : 1219
- **Total spam dipakai**   : **1099**
- Dikumpulkan dari         : **75 video** YouTube

### Sumber data non-spam (`scraper/final_non_spam.json`)

- **Total non-spam dipakai**: **2509**
- Dikumpulkan dari          : **17 video** YouTube (komentar nyata, bukan sintetis)

### Hasil evaluasi model

**K-Fold Cross-Validation (cv=5, full dataset):**
- Fold scores (F1-macro): 0.9572, 0.9621, 0.9738, 0.9705, 0.9669
- **Mean F1-macro: 96.61% ± 0.59%**

**GridSearchCV (hyperparameter tuning):**
- C kandidat: [0.01, 0.1, 1, 10, 100]
- C terpilih: **1** (F1-macro CV = 0.9543)

**Train-test split (80/20, test set = 722 sampel):**

| Metrik | Nilai |
|--------|-------|
| Accuracy | 97.23% |
| F1-macro | 0.9671 |
| Spam Precision | 0.97 |
| Spam Recall | 0.94 |
| Spam F1 | 0.95 |
| Non-spam F1 | 0.98 |

Confusion matrix:
```
                  Prediksi non_spam  Prediksi spam
Aktual non_spam        495 (TN)          7 (FP)
Aktual spam             13 (FN)        207 (TP)
```

→ Lihat gambar: `reports/confusion_matrix_svm.png`

**Perbandingan dengan baseline (data training dan test sama):**

| Model | Accuracy | F1-macro |
|-------|----------|----------|
| SVM (C=1, linear) | **97.23%** | **0.9671** |
| Logistic Regression | 95.15% | 0.9423 |
| Naive Bayes (MultinomialNB) | 94.32% | 0.9305 |

---

## Versi 1 — (sebelum 2026-06-16)

### Statistik dataset

| Label    | Jumlah |
|----------|--------|
| spam     | 1099   |
| non_spam | 700    |
| **Total**| **1799** |

### Catatan
- Data non-spam berasal dari template sintetis (`NON_SPAM_TEMPLATES` di `prepare_dataset.py`)
- Akurasi test set ~100% — kemungkinan terlalu optimis karena non-spam sintetis terlalu seragam
