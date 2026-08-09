# 12 — Referensi Lengkap Folder `src/`

> Untuk saat kamu membuka sebuah berkas di `src/` dan tidak tahu harus mulai baca dari mana.

Dokumen ini adalah **kamus**, bukan bacaan berurutan. Cari nama berkas atau nama fungsinya, baca bagiannya, tutup lagi.

---

# Sebelum mulai: tiga hal yang bikin kode ini terasa membingungkan

Kamu bukan tidak bisa baca kode — kamu Software Engineer. Yang bikin bingung itu tiga hal spesifik, dan semuanya bisa dibereskan dalam 10 menit.

## 1. Jangan baca dari baris 1

Berkas-berkas di sini panjang (200–480 baris), tapi **60% isinya komentar penjelasan**, bukan kode. Kalau kamu baca dari atas, kamu akan menghabiskan 5 menit di komentar sebelum sampai ke kode pertama.

**Cara baca yang benar untuk berkas apa pun di `src/`:**

```
1. Lompat ke paling bawah  →  cari  if __name__ == "__main__":
2. Dari situ lihat main()  →  itu daftar urutan kerjanya
3. Baru buka fungsi yang kamu butuh
```

`main()` di proyek ini selalu ditulis sebagai daftar langkah. Itu peta isi berkasnya.

## 2. Semua berkas di sini bentuknya sama persis

Begitu kamu hafal polanya, semua berkas jadi mudah:

```python
"""                          ← 1. Docstring modul: kenapa berkas ini ada
berkas.py
=========
...
"""

import ...                   ← 2. Impor

BASE_DIR = ...               ← 3. Konstanta (HURUF BESAR SEMUA)
TFIDF_PARAMS = dict(...)         semua tuas pengaturan ada di sini

def fungsi_satu(...):        ← 4. Fungsi-fungsi, urut sesuai pemakaian
def fungsi_dua(...):
def main():                  ← 5. main() = urutan kerjanya

if __name__ == "__main__":   ← 6. Titik masuk
    main()
```

🎯 **Konstanta HURUF BESAR di bagian 3 adalah panel kendalinya.** Kalau kamu mau mengubah perilaku sebuah berkas, 90% kemungkinan tuasnya ada di sana — tidak perlu menyentuh fungsinya.

## 3. Sepuluh idiom Python/sklearn yang menghambat orang dari dunia JavaScript

| Yang kamu lihat | Artinya | Padanan di JS/Node |
|---|---|---|
| `if __name__ == "__main__":` | "jalankan ini hanya kalau berkas dieksekusi langsung, bukan saat di-`import`" | `if (require.main === module)` |
| `def f(x: str) -> list:` | Type hint. **Tidak dipaksakan Python** — cuma dokumentasi | Mirip TypeScript, tapi tanpa pengecekan |
| `X_train, X_test, y_train, y_test = split(...)` | Satu fungsi mengembalikan 4 nilai sekaligus | Destructuring array |
| `TFIDF_PARAMS = dict(a=1, b=2)` lalu `Tfidf(**TFIDF_PARAMS)` | `**` membongkar dict jadi argumen bernama | Spread `{...obj}` |
| `[clean(t) for t in texts]` | List comprehension | `texts.map(clean)` |
| `f"nilai: {x:.4f}"` | Template string + format 4 desimal | `` `nilai: ${x.toFixed(4)}` `` |
| `@app.get("/health")` | Dekorator — mendaftarkan fungsi di bawahnya sebagai rute | `app.get("/health", fn)` |
| `class PredictRequest(BaseModel)` | Skema validasi Pydantic | DTO / Zod schema |
| `_normalize_leet` (awalan `_`) | Konvensi "internal, jangan dipakai dari luar" | Tidak ada padanan resmi |
| `X` dan `y` | Konvensi ML: `X` = masukan (fitur), `y` = jawaban (label) | — |

### Empat metode sklearn yang muncul di mana-mana

Ini yang paling penting dipahami. Seluruh scikit-learn cuma punya empat kata kerja:

| Metode | Artinya | Analogi |
|---|---|---|
| `.fit(X, y)` | **Belajar** dari data | Murid belajar dari soal + kunci jawaban |
| `.transform(X)` | **Ubah bentuk** data pakai apa yang sudah dipelajari | Menerjemahkan teks ke angka |
| `.fit_transform(X)` | Dua-duanya sekaligus | Belajar sambil menerjemahkan |
| `.predict(X)` | **Tebak** jawaban untuk data baru | Murid mengerjakan ujian |

Dan `Pipeline([("tfidf", ...), ("svm", ...)])` cuma merangkai keduanya, supaya `.fit()` sekali otomatis memanggil `.fit()` di keduanya secara berurutan.

**Analogi SE:** Pipeline itu *middleware chain*. `pipeline.predict(teks)` = teks masuk ke middleware TF-IDF, keluar jadi vektor, masuk ke middleware SVM, keluar jadi label.

---

# Triase: berkas mana yang penting

Ada **10 berkas** di `src/`. Kamu **tidak perlu** paham semuanya sama dalam.

| Berkas | Baris | Status | Perlu dipahami? |
|---|---|---|---|
| `preprocessing.py` | 367 | 🔴 **INTI** | **Ya, sedalam mungkin** — ini judul skripsimu |
| `train.py` | 476 | 🔴 **INTI** | **Ya** — sumber semua angka |
| `server.py` | 478 | 🔴 **INTI** | **Ya** — sistem yang berjalan |
| `prepare_dataset.py` | 358 | 🟠 Penting | Cukup paham alurnya |
| `evaluate_hard_set.py` | 195 | 🟡 Eksperimen | Cukup tahu hasil & ranjaunya |
| `evaluate_hybrid_ablation.py` | 162 | 🟡 Eksperimen | Cukup tahu hasilnya |
| `experiment_stemming.py` | 486 | 🟡 Eksperimen | Cukup tahu hasilnya |
| `compare_baselines.py` | 207 | 🟡 Eksperimen | Cukup tahu hasilnya |
| `experiment_features.py` | 288 | ⚪ Opsional | Tidak masuk skripsi |
| `inspect_features.py` | 205 | ⚪ Opsional | Berguna, tapi tidak wajib |

💡 **Untuk enam berkas 🟡 dan ⚪ itu, kamu cukup tahu: apa yang dijawab, dan apa hasilnya.** Isi kodenya tidak akan ditanya — yang ditanya kesimpulannya.

---
---

# 🔴 `preprocessing.py` (367 baris)

> Membersihkan dan menormalkan teks komentar. **Berkas terpenting di seluruh proyek.**

Dipanggil **identik** saat pelatihan (`train.py`) dan saat inferensi (`server.py`). Itu yang mencegah *training-serving skew*.

## Konstanta

| Baris | Nama | Isinya |
|---|---|---|
| 101 | `_JUDOL_EXCLUDE_PREFIXES` | Kata yang **dikecualikan** dari pola brand: `level`, `rank`, `episode`, `part`, `chapter`, `season`… |
| 107 | `JUDOL_BRAND_PATTERN` | Regex nama situs judi: `[a-z]{2,}` + akhiran `4d`, `88`, `99`, `77`, `138`, `303`… |
| 123 | `STOPWORDS_ID` | Kata umum Indonesia yang dibuang: `yang`, `dan`, `di`, `ke`, `dari`… |
| 148 | `HOMOGLYPH_MAP` | Peta Cyrillic→Latin: `а`→`a`, `е`→`e`, `о`→`o`, `р`→`p`… |

🔍 **`_JUDOL_EXCLUDE_PREFIXES` itu detail cerdas yang layak disebut saat sidang.** Tanpa itu, komentar normal seperti *"level 99"*, *"episode 88"*, atau *"part 4d"* akan ikut diubah jadi `judolbrand` — dan model belajar dari data yang salah. Pengecualian ini mencegahnya.

## Fungsi

### `clean_text(text: str) -> str` 📍 **baris 182** ⭐

Satu-satunya fungsi yang benar-benar perlu kamu kuasai di berkas ini.

Menjalankan tujuh tahap berurutan:

| Baris | Tahap | Contoh |
|---|---|---|
| 201 | Buang karakter tak terlihat | zero-width space, BOM |
| 217 | Normalisasi NFKC | `𝑅𝒪𝑀𝒜𝟦𝒟` → `ROMA4D` |
| 226 | Buang tanda diakritik | `P͟U͟L͟A͟U͟W͟I͟N` → `PULAUWIN` |
| 239 | Buka pembungkus kurung | `[P][U][L][A][U]` → `PULAU` |
| 251 | Petakan homoglyph | Cyrillic `а` → Latin `a` |
| 257 | Emoji jadi kata | 🎰 → `slot_machine` |
| 268 | Huruf kecil | |
| 271 | Normalisasi leet | `H0KI` → `HOKI` |
| 294 | Satukan nama brand | semua nama situs → `judolbrand` |
| 299 | Buang URL/angka/simbol | sisakan a–z dan spasi |
| 306 | Rapikan + buang stopword | buang token 1 huruf |

⚠️ **Urutannya tidak boleh ditukar.** Contoh: tahap 294 (satukan brand) harus **setelah** 268 (huruf kecil) supaya regex-nya cukup satu bentuk, dan harus **sebelum** 299 (buang angka) — kalau angkanya sudah dibuang duluan, `ROMA4D` jadi `ROMAD` dan polanya tidak cocok lagi.

Kalau ditanya "kenapa urutannya begitu?", jawaban di atas itu jawabannya.

### `_normalize_leet(m)` 📍 baris 288
Fungsi kecil di dalam `clean_text`. Mengganti `0`→`o` dan `1`→`i` di dalam kata yang bercampur huruf-angka. Awalan `_` menandakan ini internal.

### `preprocess_batch(texts) -> list` 📍 baris 316
Cuma menjalankan `clean_text()` ke seluruh isi daftar. Isinya satu baris list comprehension.

## Cara mencobanya
```bash
python src/preprocessing.py
```
Berkas ini punya blok uji mandiri berisi 10 kasus. Menampilkan teks asli dan hasil bersihnya berdampingan.

---
---

# 🔴 `train.py` (476 baris)

> Melatih model dan menyimpannya. **Sumber seluruh angka di skripsimu.**

## Konstanta

| Baris | Nama | Isinya |
|---|---|---|
| 52 | `DATA_PATH` | `data/comments.csv` |
| 53 | `MODEL_PATH` | `model/svm_model.joblib` |
| 54 | `REPORTS_DIR` | `reports/` |
| **63** | **`TFIDF_PARAMS`** | `max_features=10000, ngram_range=(1,2), min_df=2, sublinear_tf=True` |

## Baca `main()` dulu 📍 baris 444

`main()` memanggil fungsi-fungsi ini berurutan. Ini peta isi berkasnya:

| Urutan | Fungsi | Baris | Tugasnya |
|---|---|---|---|
| 1 | `load_data(path)` | 71 | Baca CSV, validasi, kembalikan `(X, y)` |
| 2 | `preprocess_data(texts)` | 95 | Jalankan `clean_text()` ke semua teks |
| 3 | `run_cross_validation(X, y)` | 105 | Validasi silang 5-fold pada **seluruh** data |
| 4 | `split_data(X, y)` | 184 | Bagi 80:20 berstrata |
| 5 | `find_best_hyperparams(X_train, y_train)` | 208 | GridSearchCV cari C terbaik |
| 6 | `build_and_train_pipeline(...)` | 321 | Latih model final |
| 7 | `evaluate_model(...)` | 386 | Hitung metrik, cetak, simpan grafik |
| 8 | `save_model(pipeline, path)` | 436 | `joblib.dump()` ke berkas |

Plus tiga fungsi pembuat grafik yang dipanggil dari dalam:
- `save_cv_fold_plot(scores, dir)` 📍 141 → `reports/cv_5fold_scores.png`
- `save_gridsearch_plot(grid, dir)` 📍 275 → `reports/gridsearch_c_sweep.png`
- `save_confusion_matrix_plot(...)` 📍 349 → `reports/confusion_matrix_svm.png`

## Fungsi yang menghasilkan angka skripsimu

### `run_cross_validation(X, y)` 📍 baris 105
```python
scores = cross_val_score(pipeline, X, y, cv=5, scoring="f1_macro", n_jobs=-1)  # baris 128
```
→ menghasilkan **0,9741 ± 0,0030**

💡 Perhatikan 📍 baris 126: pipeline di sini memakai `SVC(...)` **tanpa** `probability=True`. Beda dengan pipeline final. Alasannya kalibrasi probabilitas butuh CV internal tambahan, dan di sini kita cuma butuh skor F1 — jadi dimatikan agar hemat waktu. Menyebut detail ini menunjukkan kamu benar-benar membaca kodenya.

### `split_data(X, y)` 📍 baris 184
```python
train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)   # baris 197
```
→ menghasilkan **5.352 latih / 1.338 uji**

### `find_best_hyperparams(X_train, y_train)` 📍 baris 208
```python
param_grid = {"svm__C": [0.01, 0.1, 1, 10, 100]}   # baris 233
grid_search.fit(X_train, y_train)                   # baris 253  ← X_train, BUKAN X
```
→ menghasilkan **C = 1**

🎯 `X_train` di baris 253 itu **pencegahan kebocoran data**. Kalau pakai `X` (seluruh data), pencarian C akan "mengintip" data uji dan angka akhirnya jadi tidak sah.

### `evaluate_model(pipeline, X_test, y_test)` 📍 baris 386
```python
y_pred   = pipeline.predict(X_test)                     # baris 403
acc      = accuracy_score(y_test, y_pred)               # baris 409  → 0,9753
f1_macro = f1_score(y_test, y_pred, average="macro")    # baris 410  → 0,9726
cm       = confusion_matrix(y_test, y_pred)             # baris 418  → 863/9/24/442
```

📌 **Empat baris ini adalah asal dari hampir semua angka di BAB IV-mu.** Kalau cuma sempat hafal satu lokasi kode, hafal `train.py:409`.

---
---

# 🔴 `server.py` (478 baris)

> Menyajikan model sebagai REST API. Ini yang berjalan di VPS.

## Konstanta

| Baris | Nama | Isinya |
|---|---|---|
| 83 | `MODEL_PATH` | `model/svm_model.joblib` |
| 92 | `REPORT_TOKEN` | Token untuk endpoint `/report` (dari env, ada nilai bawaan) |
| **192** | **`ENABLE_HYBRID_RULES`** | **`False`** |
| 194 | `HARD_SPAM_SIGNALS` | `gacor`, `scatter`, `jackpot`, `maxwin`, `togel`, `toto`, `rtp`… |

🎯 **`ENABLE_HYBRID_RULES = False` itu penting.** Kode aturan hibrida masih ada di berkas ini, tapi **dimatikan** — persis sesuai temuan ablasi bahwa aturan itu menurunkan akurasi 7,32 poin.

❓ **Kalau penguji melihat `HARD_SPAM_SIGNALS` dan bertanya "jadi Anda pakai kata kunci juga?"**
> "Kode itu ada, Pak, tapi tidak aktif — bisa dilihat di baris 192, `ENABLE_HYBRID_RULES` bernilai `False`. Itu sisa dari eksperimen ablasi yang saya laporkan di BAB IV. Hasilnya menunjukkan penambahan aturan kata kunci justru menurunkan akurasi 7,32 poin, jadi saya matikan dan sistem berjalan dengan SVM murni."

Itu jawaban yang sangat kuat: kamu tidak cuma tahu kodenya, kamu tahu **kenapa** ia dimatikan.

## Skema validasi (Pydantic)

Kelas-kelas ini cuma pendefinisian bentuk data — padanan DTO/Zod schema.

| Baris | Kelas | Fungsinya |
|---|---|---|
| 120 | `PredictRequest` | `{ text: str }` — divalidasi tidak boleh kosong 📍 125 |
| 133 | `PredictResponse` | `{ label, confidence, is_spam }` |
| 139 | `BatchPredictRequest` | `{ texts: list }` |
| 143 | `BatchPredictResponse` | daftar hasil |
| 247 | `ReportRequest` | `{ text, label }` — label divalidasi 📍 262 |
| 268 | `ReportResponse` | konfirmasi |

## Fungsi & endpoint

| Baris | Nama | Tugasnya |
|---|---|---|
| 97 | `load_model()` | Muat `.joblib` dari disk. Dipanggil **sekali** saat server menyala |
| 110 | `startup_event()` | Dekorator `@app.on_event("startup")` — pemicu `load_model()` |
| 235 | `has_hard_spam_signal(cleaned)` | Cek apakah teks memuat sinyal keras. **Tidak dipakai** karena hibrida mati |
| 279 | `GET /` | Konfirmasi server hidup |
| 288 | `GET /health` | Status model — dipakai ekstensi sebelum mengirim permintaan |
| **297** | **`POST /predict`** | Klasifikasi **satu** komentar |
| **354** | **`POST /predict/batch`** | Klasifikasi **banyak** komentar — **ini yang dipakai ekstensi** |
| 409 | `POST /report` | Tambah komentar ke dataset. Butuh header token |

## Alur `/predict/batch` — yang sebenarnya berjalan

```python
# baris 372
cleaned = clean_text(text)            # ← fungsi yang SAMA dengan train.py

# baris 379
proba = model.predict_proba([cleaned])[0]
```

Dan di 📍 baris 41:
```python
from src.preprocessing import clean_text
```

🎯 **Baris 41 dan 372 adalah bukti tidak ada *training-serving skew*.** Bukan salinan, bukan versi JavaScript — impor dari berkas yang sama.

🔍 **Kenapa model dimuat sekali di `startup`, bukan tiap permintaan?** Memuat `.joblib` butuh waktu. Kalau dilakukan tiap request, tiap prediksi jadi lambat. Dimuat sekali ke memori, dipakai berulang.

## Cara mencobanya
```bash
python src/server.py
# lalu buka http://localhost:8000/docs
```
FastAPI otomatis membuat halaman dokumentasi interaktif. Kamu bisa menguji tiap endpoint dari peramban tanpa menulis kode.

---
---

# 🟠 `prepare_dataset.py` (358 baris)

> Mengubah JSON hasil scraping jadi `data/comments.csv`.

## Konstanta

| Baris | Nama | Isinya |
|---|---|---|
| 30 | `INPUT_SPAM_JSON` | `scraper/final_spam.json` |
| 31 | `INPUT_NON_SPAM_JSON` | `scraper/final_non_spam.json` |
| 32 | `OUTPUT_CSV` | `data/comments.csv` |
| 33 | `MANUAL_OVERRIDES_CSV` | `data/manual_overrides.csv` |
| **50** | **`SPAM_SCORE_THRESHOLD`** | **80** (scraper pakai 30 — ini lapis kedua yang lebih ketat) |

## Fungsi

| Baris | Nama | Tugasnya |
|---|---|---|
| **54** | `load_spam_data(json_path, threshold)` | Saringan **dua tahap** ⭐ |
| 201 | `load_non_spam_data(json_path)` | Muat non-spam, buang yang teksnya kosong |
| 238 | `apply_manual_overrides(spam, non_spam, path)` | Terapkan koreksi label manual |
| 308 | `build_and_save_dataset(spam, non_spam, out)` | Gabung, acak, tulis CSV |
| 333 | `main()` | Urutan 4 langkah di atas |

### Saringan dua tahap di `load_spam_data` ⭐

```python
if score >= threshold:                      # baris 155 — Tahap 1: skor >= 80, langsung masuk
    ...
elif "brand_pattern" in signals and (       # baris 177 — Tahap 2: penyelamatan
        BRAND_RESCUE_PATTERN.search(normalized)     # ALL-CAPS + digit: ROMA4D
        or BRAND_SUFFIX_PATTERN.search(normalized)  # [3+huruf]TOTO|BET|WIN|QQ
):
    ...
```

🔍 **Kenapa Tahap 2 ada?** Spammer yang pakai obfuscation Unicode biasanya juga menghias komentarnya dengan emoji dan simbol. Skornya nyangkut di 60–75 — di bawah 80 — padahal jelas spam. Tahap 2 menyelamatkan mereka, dengan syarat nama brandnya benar-benar terlihat.

🔍 **Kenapa `BRAND_SUFFIX_PATTERN` 📍 baris 128 memakai ALL-CAPS, bukan case-insensitive?** Kalau case-insensitive, kata Indonesia biasa seperti **"ngebet"** dan **"seribet"** ikut kena (keduanya berakhiran `bet`). Ini *trade-off* sadar, bukan kelalaian.

---
---

# 🟡 Empat berkas eksperimen

Untuk keempat berkas ini, **kamu cukup tahu: pertanyaan apa yang dijawab, dan hasilnya apa.** Kodenya tidak akan ditanya.

## `compare_baselines.py` (207 baris)

**Pertanyaan:** apakah SVM benar-benar lebih baik dari algoritma sederhana?

| Baris | Fungsi |
|---|---|
| 54 | `load_and_prepare_data()` — identik dengan `train.py` (`random_state=42`) |
| 78 | `save_confusion_matrix_plot(...)` |
| 108 | `run_comparison(...)` — latih NB & LogReg, bandingkan dengan SVM tersimpan |

**Hasil:** SVM 97,53% · Logistic Regression 97,09% · Multinomial NB 93,95%

🎯 Kuncinya di baris 54: pembagian datanya **sama persis**. Jadi perbandingannya adil, bukan apel dengan jeruk.

## `evaluate_hard_set.py` (195 baris)

**Pertanyaan:** tahan tidak terhadap komentar ambigu yang mirip spam tapi bukan?

| Baris | Fungsi |
|---|---|
| 55 | `HARD_TEST_PATH` → `data/hard_test_set.csv` |
| 59 | `predict_svm(model, text)` |
| 72 | `main()` |

**Hasil:** akurasi **98,52%**, 2 *false positive* dari 135.

⚠️ **RANJAU.** Berkas keluarannya `reports/hard_set_evaluation.txt` juga memuat **F1-macro 0,4963**, yang terlihat seperti model gagal total. Penyebabnya: hard test set **seluruhnya berisi non-spam**. Karena tidak ada satu pun data spam, F1 kelas spam otomatis nol, dan rata-rata makro dari (0,9926 + 0) ≈ 0,4963.

Itulah sebabnya yang dilaporkan di skripsi adalah **accuracy**, bukan F1-macro — dan naskahmu sudah menjelaskan ini dengan benar.

## `evaluate_hybrid_ablation.py` (162 baris)

**Pertanyaan:** apakah menambah aturan kata kunci di atas SVM membantu?

| Baris | Fungsi |
|---|---|
| 48 | `HARD_SPAM_SIGNALS` — daftar kata kunci yang diuji |
| 59 | `has_hard_spam_signal(cleaned)` |
| 63 | `apply_hybrid(svm_label, cleaned)` — mereproduksi logika hibrida `server.py` |
| 73 | `evaluate(name, model, texts, y_true)` |

**Hasil:** aturan hibrida **menurunkan** akurasi **7,32 poin** (data uji) dan **16,30 poin** (hard test set).

**Kenapa?** Aturan kata kunci memaksa komentar yang menyebut sinyal keras jadi spam — termasuk komentar korban dan kritik. *False positive* melonjak.

📌 Inilah alasan `server.py:192` menyetel `ENABLE_HYBRID_RULES = False`.

## `experiment_stemming.py` (486 baris)

**Pertanyaan:** apakah stemming (memotong kata ke bentuk dasar) meningkatkan performa?

| Baris | Fungsi |
|---|---|
| 77 | `stem_text(text)` — stemming Sastrawi |
| 101 | `preprocess_with_stemming(texts)` |
| 135 | `run_experiment(...)` — satu kali latih & evaluasi |
| **219** | `run_cv_comparison(...)` — **perbandingan 5-fold + uji-t** ⭐ |

**Hasil:** p-value **0,3575** → tidak signifikan. Rata-ratanya bahkan sedikit lebih rendah (−0,0006).

🎯 Perhatikan baris 219: pembandingannya pakai **cross-validation + uji statistik**, bukan sekadar satu kali latih. Itu yang membuat kesimpulan "tidak signifikan" punya dasar, bukan kesan belaka.

❓ **Kalau ditanya "kenapa pakai uji-t, tidak cukup lihat selisihnya saja?"**
> "Karena selisih kecil bisa saja cuma kebetulan dari pembagian data tertentu, Pak. Uji-t berpasangan pada kelima fold menjawab apakah selisih itu konsisten atau tidak. p-value 0,3575 jauh di atas 0,05, jadi perbedaannya tidak bisa dibedakan dari kebetulan."

---
---

# ⚪ Dua berkas opsional

## `inspect_features.py` (205 baris)

**Pertanyaan:** kata apa yang paling menentukan keputusan model?

| Baris | Isi |
|---|---|
| 39 | `TOP_N = 25` |
| 42 | `load_model()` |
| **51** | `extract_feature_weights(pipeline)` — ambil nama fitur + koefisien SVM |
| 86 | `print_top_features(df)` |
| 108 | `save_bar_chart(df)` → `reports/top_features.png` |
| 167 | `save_csv(df)` → `reports/feature_weights.csv` |

**Cara kerjanya:** pada SVM kernel **linear**, tiap fitur punya satu koefisien. Positif besar = kuat menandakan spam; negatif besar = kuat menandakan non-spam. Berkas ini cuma memasangkan `vectorizer.get_feature_names_out()` dengan `svm.coef_`.

**Hasil riil dari model sekarang:**

| Fitur penanda spam | Bobot | | Fitur penanda non-spam | Bobot |
|---|---|---|---|---|
| `judolbrand` | **+12,4969** | | `judol` | −1,6697 |
| `pulauwin` | +6,4552 | | `judi` | −1,4846 |
| `nagamastoto` | +3,6410 | | `bang` | −1,3314 |
| `gacorwini` | +3,6066 | | `berhenti` | −0,9340 |
| `maxwin` | +2,6447 | | `bandar` | −0,8121 |

🎯 **Dua hal yang sangat berguna untuk sidang:**

**1.** `judolbrand` berbobot **+12,50**, hampir dua kali fitur terkuat berikutnya. Ini **bukti empiris** bahwa keputusanmu menyatukan nama brand jadi satu token itu benar. Jawaban terkuat untuk *"kenapa nama situs disatukan?"*

**2.** Kata `judol` dan `judi` justru penanda **non-spam**. Kelihatan aneh, tapi masuk akal: yang menulis "judol" secara eksplisit biasanya orang yang **mengkritik** judi online, bukan yang mempromosikannya. Promotor menyamarkan, pengkritik menyebut terang-terangan.

💡 Poin nomor 2 itu temuan yang menarik dan menunjukkan pemahaman mendalam. Simpan untuk sesi tanya jawab.

## `experiment_features.py` (288 baris)

**Pertanyaan:** kombinasi parameter TF-IDF mana yang terbaik?

| Baris | Isi |
|---|---|
| 63 | `CONFIGS` — daftar kombinasi yang diuji |
| 97 | `load_and_preprocess()` |
| 119 | `run_one_config(cfg, ...)` |
| 153 | `save_bar_chart(results)` |
| 200 | `save_csv(results)` → `reports/experiment_features.csv` |
| 232 | `interpret_results(results)` |

Menguji variasi `ngram_range` dan `max_features`. Membenarkan pilihan `(1,2)` dan `10.000` di `train.py:63`. **Tidak masuk skripsi** — tapi kalau ditanya "kenapa ngram (1,2)?", data pendukungnya ada di sini.

---
---

# Peta cepat: buka berkas mana kalau ditanya apa

| Pertanyaan penguji | Buka |
|---|---|
| "Angka 97,53% dari mana?" | `train.py:409` |
| "Bagaimana teks tersamar ditangani?" | `preprocessing.py:182` |
| "Kenapa nama situs disatukan?" | `preprocessing.py:294` + tabel bobot di atas |
| "Kenapa normalisasi di server?" | `server.py:41` dan `server.py:372` |
| "Kenapa C = 1?" | `train.py:233` dan `train.py:253` |
| "Bagaimana mencegah kebocoran data?" | `train.py:253` (`X_train`, bukan `X`) |
| "Bagaimana Anda melabeli data?" | `prepare_dataset.py:155`, `:177`, `:238` |
| "Ini pakai kata kunci juga ya?" | `server.py:192` → `False` |
| "Kenapa tidak pakai stemming?" | `experiment_stemming.py:219` → p = 0,3575 |
| "Apakah SVM benar lebih baik?" | `compare_baselines.py:54` (split sama) |
| "Kata apa yang paling menentukan?" | `inspect_features.py:51` |
| "Bagaimana kalau komentarnya ambigu?" | `evaluate_hard_set.py` → 98,52% |

---

# Lima lokasi kode yang wajib hafal

Kalau waktumu tinggal sedikit, hafal lima ini saja:

| # | Lokasi | Kenapa |
|---|---|---|
| 1 | `train.py:409` | Asal angka 97,53% |
| 2 | `preprocessing.py:182` | Fungsi `clean_text()` — judul skripsimu |
| 3 | `server.py:372` | Bukti tidak ada training-serving skew |
| 4 | `train.py:253` | Bukti tidak ada kebocoran data |
| 5 | `server.py:192` | Bukti hibrida dimatikan atas dasar bukti |

Lima lokasi itu menjawab sekitar 80% pertanyaan teknis yang mungkin muncul.

---

# Kalau masih buntu membaca sebuah berkas

Urutan yang selalu berhasil:

1. **Baca docstring paling atas.** Tiga baris pertama menjawab "kenapa berkas ini ada".
2. **Lompat ke `main()`.** Itu daftar isi berkasnya.
3. **Lihat konstanta HURUF BESAR.** Itu panel kendalinya.
4. **Baru buka satu fungsi** yang kamu butuhkan.
5. **Jangan baca fungsi grafik** (`save_*_plot`). Isinya matplotlib, tidak ada logika penelitian di sana — cuma mengatur warna dan label.

Poin 5 penting: dari 476 baris `train.py`, sekitar 150 baris cuma urusan menggambar grafik. Melewatinya menghemat banyak waktu tanpa kehilangan apa pun.
