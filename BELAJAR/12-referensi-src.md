# 12 — Referensi Lengkap Folder `src/`

> Kamus fungsi, **lengkap dengan potongan kodenya**. Dibuat supaya bisa dibaca tuntas dari ponsel tanpa perlu membuka berkas sumbernya.

Ini kamus, bukan bacaan berurutan. Cari nama berkas atau fungsinya, baca bagiannya, tutup lagi.

Semua potongan kode di bawah **disalin persis dari berkas aslinya**, dengan nomor baris apa adanya. Komentar panjang di kode aslinya sengaja dipotong — penjelasannya sudah ditulis di prosa.

---

# Sebelum mulai: tiga hal yang bikin kode ini terasa membingungkan

Kamu bukan tidak bisa baca kode — kamu Software Engineer. Yang bikin bingung cuma tiga hal, dan semuanya bisa dibereskan dalam 10 menit.

## 1. Jangan baca dari baris 1

Berkas di sini panjang (200–480 baris), tapi **sekitar 60% isinya komentar penjelasan**, bukan kode. Kalau kamu baca dari atas, kamu habis 5 menit di komentar sebelum sampai kode pertama.

**Cara baca yang benar untuk berkas apa pun di `src/`:**

```
1. Lompat ke paling bawah  →  cari  if __name__ == "__main__":
2. Dari situ lihat main()  →  itu daftar urutan kerjanya
3. Baru buka fungsi yang kamu butuhkan
```

## 2. Semua berkas di sini bentuknya sama persis

```python
"""                          ← 1. Docstring: kenapa berkas ini ada
berkas.py
"""
import ...                   ← 2. Impor

BASE_DIR = ...               ← 3. KONSTANTA (huruf besar semua)
TFIDF_PARAMS = dict(...)         ini panel kendalinya

def fungsi_satu(...):        ← 4. Fungsi, urut sesuai pemakaian
def main():                  ← 5. main() = urutan kerjanya

if __name__ == "__main__":   ← 6. Titik masuk
    main()
```

🎯 **Konstanta huruf besar di bagian 3 adalah panel kendalinya.** Mau mengubah perilaku sebuah berkas? 90% kemungkinan tuasnya ada di sana — tidak perlu menyentuh fungsinya.

## 3. Sepuluh idiom Python yang menghambat orang dari dunia JavaScript

| Yang kamu lihat | Artinya | Padanan JS |
|---|---|---|
| `if __name__ == "__main__":` | jalankan hanya kalau dieksekusi langsung | `if (require.main === module)` |
| `def f(x: str) -> list:` | type hint, **tidak dipaksakan** Python | mirip TS tanpa pengecekan |
| `a, b, c, d = split(...)` | satu fungsi kembalikan 4 nilai | destructuring array |
| `Tfidf(**PARAMS)` | `**` bongkar dict jadi argumen | spread `{...obj}` |
| `[clean(t) for t in texts]` | list comprehension | `texts.map(clean)` |
| `f"nilai: {x:.4f}"` | template string + 4 desimal | `` `${x.toFixed(4)}` `` |
| `@app.get("/health")` | dekorator: daftarkan fungsi sebagai rute | `app.get("/health", fn)` |
| `class Req(BaseModel)` | skema validasi Pydantic | DTO / Zod schema |
| `_normalize_leet` | awalan `_` = internal, konvensi saja | — |
| `X` dan `y` | konvensi ML: `X` masukan, `y` jawaban | — |

### Empat metode sklearn yang muncul di mana-mana

Seluruh scikit-learn cuma punya empat kata kerja:

| Metode | Artinya | Analogi |
|---|---|---|
| `.fit(X, y)` | **belajar** dari data | murid belajar dari soal + kunci |
| `.transform(X)` | **ubah bentuk** pakai yang sudah dipelajari | menerjemahkan teks ke angka |
| `.fit_transform(X)` | dua-duanya sekaligus | belajar sambil menerjemahkan |
| `.predict(X)` | **tebak** untuk data baru | murid mengerjakan ujian |

**Analogi SE untuk `Pipeline`:** itu *middleware chain*. `pipeline.predict(teks)` → teks masuk middleware TF-IDF, keluar jadi vektor → masuk middleware SVM, keluar jadi label.

---

# Triase: berkas mana yang penting

| Berkas | Baris | Status | Perlu dipahami? |
|---|---|---|---|
| `preprocessing.py` | 367 | 🔴 **INTI** | **Ya, sedalam mungkin** — ini judul skripsimu |
| `train.py` | 476 | 🔴 **INTI** | **Ya** — sumber semua angka |
| `server.py` | 478 | 🔴 **INTI** | **Ya** — sistem yang berjalan |
| `prepare_dataset.py` | 358 | 🟠 Penting | cukup alurnya |
| `evaluate_hard_set.py` | 195 | 🟡 Eksperimen | cukup hasil & ranjaunya |
| `evaluate_hybrid_ablation.py` | 162 | 🟡 Eksperimen | cukup hasilnya |
| `experiment_stemming.py` | 486 | 🟡 Eksperimen | cukup hasilnya |
| `compare_baselines.py` | 207 | 🟡 Eksperimen | cukup hasilnya |
| `experiment_features.py` | 288 | ⚪ Opsional | tidak masuk skripsi |
| `inspect_features.py` | 205 | ⚪ Opsional | berguna, tidak wajib |

💡 Untuk enam berkas 🟡 dan ⚪, kamu cukup tahu **apa yang dijawab dan apa hasilnya**. Kodenya tidak akan ditanya.

---
---

# 🔴 `preprocessing.py` (367 baris)

> Membersihkan dan menormalkan teks komentar. **Berkas terpenting di seluruh proyek.**

Dipanggil **identik** saat pelatihan (`train.py`) dan inferensi (`server.py`). Itu yang mencegah *training-serving skew*.

## Konstanta

### Pola nama situs judi 📍 baris 101–109

```python
_JUDOL_EXCLUDE_PREFIXES = (
    "level", "rank", "stage", "episode", "part", "seri", "versi",
    "chapter", "season", "round", "wave", "fase", "lv",
)
_EXCL = "|".join(_JUDOL_EXCLUDE_PREFIXES)

JUDOL_BRAND_PATTERN = re.compile(
    rf'\b(?!(?:{_EXCL})\d)[a-z]{{2,}}(?:4d|3d|2d|88|99|77|69|138|388|303|777|888|qq)\b'
)
```

🔍 **`_JUDOL_EXCLUDE_PREFIXES` itu detail cerdas yang layak disebut saat sidang.** Bagian `(?!(?:level|rank|...)\d)` adalah *negative lookahead* — artinya "cocokkan pola brand, **kecuali** kalau diawali kata-kata ini".

Tanpa itu, komentar normal seperti *"level 99"*, *"episode 88"*, atau *"part 4d"* ikut diubah jadi `judolbrand`, dan model belajar dari data yang salah.

### Peta homoglyph 📍 baris 148–160

```python
HOMOGLYPH_MAP = str.maketrans({
    # Cyrillic → Latin
    "а": "a",  # а → a
    "е": "e",  # е → e
    "о": "o",  # о → o
    "р": "p",  # р → p  (mirip 'p', bukan 'r')
    "с": "c",  # с → c
    "х": "x",  # х → x
    "і": "i",  # і → i  (Ukrainian)
    ...
})
```

🔍 **Kenapa ini perlu, padahal sudah ada NFKC?** NFKC cuma menormalkan **dalam blok Unicode yang sama**. Ia tidak bisa memetakan Cyrillic `а` ke Latin `a` karena keduanya dianggap aksara berbeda. Peta ini menutup celah itu.

| Baris | Konstanta lain | Isinya |
|---|---|---|
| 123 | `STOPWORDS_ID` | `yang`, `dan`, `di`, `ke`, plus varian informal: `gua`, `gue`, `kalo`, `udah`, `tp`, `dgn` |

## `clean_text(text: str) -> str` 📍 baris 182 ⭐

Satu-satunya fungsi yang benar-benar perlu kamu kuasai di berkas ini.

**Penjaga di awal** 📍 baris 198:
```python
if not isinstance(text, str) or not text.strip():
    return ""
```

### Tahap 1 — Buang karakter tak terlihat 📍 baris 205

```python
zero_width_chars = (
    "​"  # Zero-width space
    "‌"  # Zero-width non-joiner
    "‍"  # Zero-width joiner
    "﻿"  # Byte order mark (BOM)
    "­"  # Soft hyphen
    "‎"  # Left-to-right mark
    "‏"  # Right-to-left mark
)
for char in zero_width_chars:
    text = text.replace(char, "")
```

Karakter ini **tak terlihat di editor mana pun**, tapi memecah tokenisasi. `d​a​f​t​a​r` dengan zero-width space di antaranya akan jadi 6 token terpisah.

### Tahap 2 — Normalisasi NFKC 📍 baris 224

```python
text = unicodedata.normalize("NFKC", text)
```

Satu baris ini menangani sebagian besar trik font spammer:
`𝑅𝒪𝑀𝒜𝟦𝒟` → `ROMA4D` · `Ｄａｆｔａｒ` → `Daftar` · `🅓🅐🅕🅣🅐🅡` → `DAFTAR`

### Tahap 2b — Buang tanda diakritik 📍 baris 237

```python
text = "".join(c for c in text if unicodedata.category(c) != "Mn")
```

`"Mn"` = *Mark, Nonspacing*. Menangkap semua garis bawah/aksen gabungan.

⚠️ **Tanpa baris ini sistemnya rusak parah.** `P͟U͟L͟A͟U͟W͟I͟N` → tiap `͟` diganti spasi oleh Tahap 6 → tiap huruf jadi token sendiri → semua dibuang karena panjangnya 1 → **string kosong** → salah diklasifikasi non-spam.

### Tahap 2c — Buka pembungkus kurung 📍 baris 249

```python
text = re.sub(r"[\[(\{]\s*(\w)\s*[\])\}]", r"\1", text)
```

`[P][U][L][A][U]` → `PULAU`. Regex-nya hanya membuka kurung yang membungkus **tepat satu** karakter, jadi kalimat normal dalam kurung — misal `(lihat di sini)` — tidak terpengaruh.

### Tahap 3 — Homoglyph 📍 baris 255

```python
text = text.translate(HOMOGLYPH_MAP)
```

### Tahap 4 — Emoji jadi kata 📍 baris 265

```python
text = emoji.demojize(text, language="en")
text = re.sub(r":([a-zA-Z0-9_]+):", r" \1 ", text)
```

🎰 → `:slot_machine:` → `slot_machine`. **Emoji tidak dibuang** — diubah jadi kata supaya sinyalnya tetap terpakai.

### Tahap 5 — Huruf kecil 📍 baris 269

```python
text = text.lower()
```

### Tahap 5b-i — Normalisasi leet 📍 baris 288

```python
def _normalize_leet(m):
    word = m.group(0)
    word = word.replace("0", "o").replace("1", "i")
    return word
text = re.sub(r'\b[a-z0-9]*[0-9][a-z0-9]*\b', _normalize_leet, text)
```

`H0KI777` → `HOKI777` · `s1tus` → `situs` · `d3p0s1t` → `depos it`

🔍 **Kenapa hanya `0→o` dan `1→i`?** `3→e`, `4→a`, `5→s` terlalu berisiko memutilasi angka yang sah — "skor 354" akan jadi "skor esa".

⚠️ **Batasan jujur yang layak diakui:** aturan ini tetap punya efek samping. `depo 10rb wd jutaan` berubah jadi `depo iorb wd jutaan`. Kalau ditanya keterbatasan sistem, ini contoh nyata yang bagus.

### Tahap 5b — Satukan nama brand 📍 baris 297 ⭐

```python
text = JUDOL_BRAND_PATTERN.sub("judolbrand", text)
```

**Satu baris ini adalah fitur paling menentukan di seluruh model.** Semua nama situs (`ROMA4D`, `PULAUWIN`, `NAGAMASTOTO`, …) jadi satu token `judolbrand`, yang bobotnya **+12,4969** — hampir dua kali fitur terkuat berikutnya.

Tanpa ini, tiap nama situs baru jadi fitur terpisah dan model harus melihat contohnya dulu untuk mengenalinya. Dengan ini, model belajar **satu pola** yang berlaku untuk nama yang belum pernah ia lihat.

### Tahap 6 — Buang URL, angka, simbol 📍 baris 303

```python
text = re.sub(r"http\S+|www\.\S+", " ", text)
text = re.sub(r"[^a-z\s]", " ", text)
```

### Tahap 7 — Rapikan + buang stopword 📍 baris 307

```python
text = re.sub(r"\s+", " ", text).strip()
tokens = [
    word for word in text.split()
    if word not in STOPWORDS_ID and len(word) > 1
]
return " ".join(tokens)
```

## ⚠️ Urutan tahapnya tidak boleh ditukar

Ini pertanyaan yang mungkin muncul, dan jawabannya konkret:

| Aturan | Kenapa |
|---|---|
| Tahap 5b **setelah** Tahap 5 | regex brand ditulis huruf kecil semua, jadi teksnya harus sudah lowercase |
| Tahap 5b **sebelum** Tahap 6 | kalau angka sudah dibuang duluan, `roma4d` jadi `romad` dan polanya tidak cocok |
| Tahap 2b **sebelum** Tahap 6 | kalau tidak, diakritik jadi spasi dan tiap huruf jadi token tunggal lalu terbuang |
| Tahap 5b-i **sebelum** Tahap 5b | supaya brand yang pakai leet (`h0ki777`) ikut terdeteksi polanya |

## `preprocess_batch(texts) -> list` 📍 baris 316

```python
return [clean_text(t) for t in texts]
```

## Cara mencobanya
```bash
python src/preprocessing.py
```
Berkas ini punya blok uji mandiri berisi 10 kasus — menampilkan teks asli dan hasil bersihnya berdampingan.

---
---

# 🔴 `train.py` (476 baris)

> Melatih model dan menyimpannya. **Sumber seluruh angka di skripsimu.**

## Panel kendali 📍 baris 63

```python
TFIDF_PARAMS = dict(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True,
)
```

| Parameter | Artinya |
|---|---|
| `max_features=10000` | ambil 10.000 kata/bigram paling sering saja |
| `ngram_range=(1,2)` | pakai kata tunggal **dan** pasangan kata |
| `min_df=2` | abaikan yang cuma muncul di 1 dokumen (kemungkinan salah ketik) |
| `sublinear_tf=True` | pakai `1 + log(tf)`, bukan `tf` mentah |

🔍 **Kenapa `ngram_range=(1,2)` penting?** Buktinya ada di bobot model: kata `slot` sendirian berbobot **−0,3800** (penanda non-spam), tapi bigram `slot machine` berbobot **+0,5223**. Tanpa bigram, model kehilangan kemampuan membedakan keduanya.

## Peta isi: baca `main()` 📍 baris 444

| Urutan | Fungsi | Baris | Tugasnya |
|---|---|---|---|
| 1 | `load_data(path)` | 71 | baca CSV, validasi, kembalikan `(X, y)` |
| 2 | `preprocess_data(texts)` | 95 | jalankan `clean_text()` ke semua teks |
| 3 | `run_cross_validation(X, y)` | 105 | validasi silang pada **seluruh** data |
| 4 | `split_data(X, y)` | 184 | bagi 80:20 berstrata |
| 5 | `find_best_hyperparams(...)` | 208 | GridSearchCV cari C |
| 6 | `build_and_train_pipeline(...)` | 321 | latih model final |
| 7 | `evaluate_model(...)` | 386 | hitung metrik, cetak, simpan grafik |
| 8 | `save_model(pipeline, path)` | 436 | tulis ke berkas |

Plus tiga pembuat grafik: `save_cv_fold_plot` 📍141, `save_gridsearch_plot` 📍275, `save_confusion_matrix_plot` 📍349.

💡 **Lewati ketiganya.** Isinya matplotlib mengatur warna dan label — nol logika penelitian. Sekitar 150 dari 476 baris berkas ini cuma urusan menggambar.

## `run_cross_validation(X, y)` 📍 baris 105

```python
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
    ("svm", SVC(kernel="linear", class_weight="balanced", random_state=42))
])

scores = cross_val_score(pipeline, X, y, cv=5, scoring="f1_macro", n_jobs=-1)

print(f"\n    Fold scores (F1-macro): {[f'{s:.4f}' for s in scores]}")
print(f"    Mean  : {scores.mean():.4f}")
print(f"    Std   : {scores.std():.4f}")
```

→ menghasilkan **0,9741 ± 0,0030**

💡 **Detail halus yang bisa jadi nilai plus.** Perhatikan `SVC(...)` di sini **tidak punya** `probability=True`, berbeda dari pipeline final di baris 335. Alasannya: kalibrasi probabilitas butuh cross-validation internal tambahan, dan di tahap ini kita cuma butuh skor F1 — jadi dimatikan supaya hemat waktu. Menyebut ini menunjukkan kamu benar-benar membaca kodenya.

## `split_data(X, y)` 📍 baris 184

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)
```

→ menghasilkan **5.352 latih / 1.338 uji**

| Parameter | Fungsinya |
|---|---|
| `test_size=0.2` | 6.690 × 0,2 = 1.338 |
| `random_state=42` | pengacakan tetap → hasil bisa direproduksi persis |
| `stratify=y` | proporsi spam:non-spam dijaga sama di kedua bagian |

## `find_best_hyperparams(X_train, y_train)` 📍 baris 208

```python
param_grid = {"svm__C": [0.01, 0.1, 1, 10, 100]}

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
    ("svm", SVC(
        kernel="linear",
        class_weight="balanced",
        probability=True,
        random_state=42
    ))
])

grid_search = GridSearchCV(
    pipeline, param_grid, cv=5,
    scoring="f1_macro", n_jobs=-1, verbose=0,
)
grid_search.fit(X_train, y_train)     # ← X_train, BUKAN X

best_C = grid_search.best_params_["svm__C"]
```

→ menghasilkan **C = 1**

🎯 **`X_train` di baris 253 itu pencegahan kebocoran data.** Kalau pakai `X` (seluruh data), pencarian C akan "mengintip" data uji dan angka akhirnya jadi tidak sah.

🔍 **`"svm__C"` dengan dua garis bawah** itu cara sklearn menunjuk parameter di dalam langkah pipeline bernama `"svm"`. Bacanya: *"parameter `C` milik langkah `svm`"*.

## `build_and_train_pipeline(...)` 📍 baris 321

```python
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
    ("svm", SVC(
        C=best_C,
        kernel="linear",
        class_weight="balanced",
        probability=True,
        random_state=42
    ))
])

pipeline.fit(X_train, y_train)
return pipeline
```

Model hasilnya punya **8.342 fitur** dan **2.002 support vector** (1.311 non-spam + 691 spam).

| Parameter | Kenapa |
|---|---|
| `kernel="linear"` | data teks TF-IDF berdimensi tinggi dan sudah terpisah linear |
| `class_weight="balanced"` | menangani ketidakseimbangan 2.332 vs 4.358 tanpa membuang data |
| `probability=True` | menyalakan Platt Scaling — **wajib**, ekstensi butuh skor keyakinan |
| `random_state=42` | hasil bisa direproduksi |

## `evaluate_model(...)` 📍 baris 386 ⭐

```python
y_pred = pipeline.predict(X_test)

acc = accuracy_score(y_test, y_pred)                    # → 0,9753
f1_macro = f1_score(y_test, y_pred, average="macro")    # → 0,9726

print(f"\nOverall Accuracy : {acc:.2%}")
print(f"F1-score (macro) : {f1_macro:.4f}")
print(classification_report(y_test, y_pred))

labels = ["non_spam", "spam"]
cm = confusion_matrix(y_test, y_pred, labels=labels)    # → 863/9/24/442
```

📌 **Baris 409, 410, dan 418 adalah asal hampir semua angka di BAB IV-mu.** Kalau cuma sempat hafal satu lokasi kode, hafal `train.py:409`.

```
              Prediksi non_spam   Prediksi spam
Aktual non_spam       863               9        ← 9 false positive
Aktual spam            24             442        ← 24 false negative
```

## `save_model(pipeline, path)` 📍 baris 436

```python
def save_model(pipeline: Pipeline, path: str) -> None:
    """Serialize the trained pipeline to disk using joblib."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(pipeline, path)
```

🔍 **Yang disimpan adalah seluruh Pipeline**, bukan cuma modelnya. Artinya TF-IDF yang sudah "hafal" kosakata ikut tersimpan. Kalau cuma SVM yang disimpan, saat inferensi kosakatanya berbeda dan seluruh vektornya salah.

---
---

# 🔴 `server.py` (478 baris)

> Menyajikan model sebagai REST API. Ini yang berjalan di VPS.

## Baris terpenting di seluruh berkas 📍 baris 41

```python
from src.preprocessing import clean_text
```

🎯 **Ini bukti tidak ada *training-serving skew*.** Bukan salinan, bukan versi JavaScript — impor dari berkas yang sama dengan yang dipakai `train.py`.

## `load_model()` 📍 baris 97

```python
def load_model():
    """Load the serialized Pipeline from disk. Called once at server startup."""
    global model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}\n"
            f"Run training first: python src/train.py"
        )
    model = joblib.load(MODEL_PATH)
```

Dipanggil dari `startup_event()` 📍 baris 110 lewat dekorator `@app.on_event("startup")`.

🔍 **Kenapa dimuat sekali di startup, bukan tiap permintaan?** Memuat `.joblib` butuh waktu. Kalau dilakukan tiap request, tiap prediksi jadi lambat. Dimuat sekali ke memori, dipakai berulang.

## Aturan hibrida — dimatikan 📍 baris 192

```python
ENABLE_HYBRID_RULES = False

HARD_SPAM_SIGNALS = {
    "gacor",      # slot dengan RTP tinggi — sangat spesifik ke promosi
    "scatter",    # simbol bonus di mesin slot
    "jackpot",
    "maxwin",
    "togel",
    ...
}
```

🎯 **Ini pertanyaan jebakan yang bisa kamu balik jadi jawaban kuat.**

❓ **Kalau penguji melihat `HARD_SPAM_SIGNALS` dan bertanya "jadi Anda pakai kata kunci juga?"**
> "Kode itu ada, Pak, tapi tidak aktif — bisa dilihat di baris 192, `ENABLE_HYBRID_RULES` bernilai `False`. Itu sisa dari eksperimen ablasi yang saya laporkan di BAB IV. Hasilnya menunjukkan penambahan aturan kata kunci justru menurunkan akurasi 7,32 poin, jadi saya matikan dan sistem berjalan dengan SVM murni."

Kamu tidak cuma tahu kodenya — kamu tahu **kenapa** ia dimatikan.

## Skema validasi (Pydantic)

| Baris | Kelas | Isinya |
|---|---|---|
| 120 | `PredictRequest` | `{ text: str }`, divalidasi tidak boleh kosong 📍125 |
| 133 | `PredictResponse` | `{ label, confidence, is_spam }` |
| 139 | `BatchPredictRequest` | `{ texts: list }` |
| 143 | `BatchPredictResponse` | daftar hasil |
| 247 | `ReportRequest` | `{ text, label }`, label divalidasi 📍262 |

## Endpoint

| Baris | Endpoint | Tugasnya |
|---|---|---|
| 279 | `GET /` | konfirmasi server hidup |
| 288 | `GET /health` | status model — dipakai ekstensi sebelum kirim permintaan |
| 297 | `POST /predict` | klasifikasi **satu** komentar |
| **354** | **`POST /predict/batch`** | klasifikasi banyak — **ini yang dipakai ekstensi** |
| 409 | `POST /report` | tambah komentar ke dataset, butuh header token |

### `GET /health` 📍 baris 287

```python
@app.get("/health")
def health():
    return {
        "status": "ok" if model is not None else "model_not_loaded",
        "model_loaded": model is not None
    }
```

### `POST /predict` — inti alurnya 📍 baris 313

```python
cleaned = clean_text(request.text)

if not cleaned:
    # Teks jadi kosong setelah dibersihkan (misal masukan emoji semua)
    return PredictResponse(label="non_spam", confidence=0.5, is_spam=False)

label = model.predict([cleaned])[0]

proba = model.predict_proba([cleaned])[0]
classes = model.classes_
label_idx = list(classes).index(label)
confidence = float(proba[label_idx])
```

🔍 **Penanganan `if not cleaned`** itu penting. Komentar yang isinya cuma emoji atau simbol bisa jadi string kosong setelah dibersihkan. Tanpa penjaga ini, model dipanggil dengan masukan kosong dan hasilnya tidak bisa diandalkan. Dikembalikan `confidence=0.5` — artinya "benar-benar tidak tahu".

### `POST /predict/batch` 📍 baris 365

```python
if len(request.texts) > 50:
    raise HTTPException(status_code=400,
                        detail="Maximum 50 texts per request")

results = []
for text in request.texts:
    cleaned = clean_text(text)

    if not cleaned:
        results.append(PredictResponse(label="non_spam",
                                       confidence=0.5, is_spam=False))
        continue

    label = model.predict([cleaned])[0]
    proba = model.predict_proba([cleaned])[0]
    ...
```

📌 Batas **50** di baris 367 harus cocok dengan `BATCH_SIZE = 50` di `content.js:374`. Kalau salah satu diubah tanpa yang lain, permintaan ditolak dengan galat 400.

## Cara mencobanya
```bash
python src/server.py
# lalu buka http://localhost:8000/docs
```
FastAPI otomatis membuat halaman dokumentasi interaktif — bisa menguji tiap endpoint dari peramban tanpa menulis kode.

---
---

# 🟠 `prepare_dataset.py` (358 baris)

> Mengubah JSON hasil pengumpulan jadi `data/comments.csv`.

## Panel kendali 📍 baris 50

```python
# Trade-off: raising this value  = cleaner data, fewer samples.
#            lowering this value = more samples, more label noise.
SPAM_SCORE_THRESHOLD = 80
```

⚠️ Perhatikan: **80**, sementara scraper memakai **30**. Ini lapis kedua yang jauh lebih ketat.

❓ **Kalau ditanya "kenapa dua ambang berbeda?"**
> "Ada dua lapis, Pak. Scraper pakai ambang 30 supaya menjaring lebar — tidak ada spam yang terlewat. Penyaringan ketatnya di `prepare_dataset.py` dengan ambang 80, yang mensyaratkan minimal satu sinyal primer plus sinyal pendukung. Jaring lebar dulu, baru disaring ketat."

## Saringan dua tahap 📍 baris 143 ⭐

```python
for entry in raw_data:
    score      = entry.get("spam_score", 0)
    text       = entry.get("original_text", "").strip()
    normalized = entry.get("normalized_text", "").strip()
    signals    = entry.get("active_signals", [])

    if not text:
        skipped_low_score += 1
        continue

    # Tahap 1: ambang utama — keyakinan tinggi, selalu masuk
    if score >= threshold:
        spam_entries.append({"text": text, "label": "spam", ...})
```

```python
    # Tahap 2: selamatkan yang di bawah ambang tapi nama brandnya jelas
    elif "brand_pattern" in signals and (
        BRAND_RESCUE_PATTERN.search(normalized)     # ALL-CAPS + digit: ROMA4D
        or BRAND_SUFFIX_PATTERN.search(normalized)  # [3+huruf]TOTO|BET|WIN|QQ
    ):
        spam_entries.append({"text": text, "label": "spam", ...})
        rescued += 1

    else:
        # Bisa jadi false positive seperti "kesambet" (brand_pattern kena "bet"),
        # soft brand (Miya88 — huruf campur, tidak cocok regex ALL-CAPS),
        # atau memang sinyalnya lemah. Dilewati.
        skipped_low_score += 1
```

🔍 **Kenapa Tahap 2 ada?** Spammer yang pakai obfuscation Unicode biasanya juga menghias komentarnya dengan emoji dan simbol. Skornya nyangkut di 60–75 — di bawah 80 — padahal jelas spam. Tahap 2 menyelamatkan mereka, dengan syarat nama brandnya benar-benar terlihat di teks yang sudah dinormalisasi.

🔍 **Kenapa polanya ALL-CAPS?** 📍 baris 128

```python
BRAND_SUFFIX_PATTERN = re.compile(r'\b[A-Z]{3,}(?:TOTO|BET|WIN|QQ)\b')
```

Kalau case-insensitive, kata Indonesia biasa seperti **"ngebet"** dan **"seribet"** ikut kena — keduanya berakhiran `bet`. Dengan memaksa huruf besar semua, `ngebet` lowercase yang umum jadi aman.

Ini **trade-off sadar**, bukan kelalaian. Kalau ditanya, jawab begitu.

## Fungsi lain

| Baris | Nama | Tugasnya |
|---|---|---|
| 201 | `load_non_spam_data(path)` | muat non-spam, buang yang teksnya kosong |
| 238 | `apply_manual_overrides(...)` | terapkan koreksi label dari `manual_overrides.csv` |
| 308 | `build_and_save_dataset(...)` | gabung, acak, tulis CSV |

🎯 **`apply_manual_overrides` yang membuat pelabelanmu bisa disebut "manual", bukan murni otomatis.** Heuristik hanya menjaring; keputusan akhir tetap padamu, tercatat dalam berkas yang bisa diperiksa dan dibaca ulang tiap dataset dibangun.

---
---

# 🟡 Empat berkas eksperimen

Untuk keempat berkas ini, **cukup tahu pertanyaan yang dijawab dan hasilnya.** Kodenya tidak akan ditanya.

## `compare_baselines.py` (207 baris)

**Pertanyaan:** apakah SVM benar-benar lebih baik dari algoritma sederhana?

| Baris | Fungsi |
|---|---|
| 54 | `load_and_prepare_data()` — identik `train.py`, `random_state=42` |
| 108 | `run_comparison(...)` — latih NB & LogReg, bandingkan dengan SVM tersimpan |

**Hasil:** SVM 97,53% · Logistic Regression 97,09% · Multinomial NB 93,95%

🎯 Kuncinya di baris 54: pembagian datanya **sama persis**, jadi perbandingannya adil.

## `evaluate_hard_set.py` (195 baris)

**Pertanyaan:** tahan tidak terhadap komentar ambigu yang mirip spam tapi bukan?

**Hasil:** akurasi **98,52%**, 2 *false positive* dari 135.

⚠️ **RANJAU.** Berkas keluarannya `reports/hard_set_evaluation.txt` juga memuat **F1-macro 0,4963**, yang terlihat seperti model gagal total.

Penyebabnya: hard test set **seluruhnya berisi non-spam**. Karena tidak ada satu pun data spam, F1 kelas spam otomatis nol, dan rata-rata makro dari (0,9926 + 0) ≈ 0,4963.

Itulah sebabnya yang dilaporkan di skripsi **accuracy**, bukan F1-macro — dan naskahmu sudah menjelaskan ini dengan benar.

## `evaluate_hybrid_ablation.py` (162 baris)

**Pertanyaan:** apakah menambah aturan kata kunci di atas SVM membantu?

| Baris | Fungsi |
|---|---|
| 59 | `has_hard_spam_signal(cleaned)` |
| 63 | `apply_hybrid(svm_label, cleaned)` — mereproduksi logika hibrida `server.py` |

**Hasil:** aturan hibrida **menurunkan** akurasi **7,32 poin** (data uji) dan **16,30 poin** (hard test set).

**Kenapa?** Aturan kata kunci memaksa komentar yang menyebut sinyal keras jadi spam — termasuk komentar korban dan kritik. *False positive* melonjak.

📌 Inilah alasan `server.py:192` menyetel `ENABLE_HYBRID_RULES = False`.

## `experiment_stemming.py` (486 baris)

**Pertanyaan:** apakah stemming meningkatkan performa?

| Baris | Fungsi |
|---|---|
| 77 | `stem_text(text)` — stemming Sastrawi |
| 135 | `run_experiment(...)` — satu kali latih & evaluasi |
| **219** | `run_cv_comparison(...)` — **perbandingan 5-fold + uji-t** ⭐ |

**Hasil:** p-value **0,3575** → tidak signifikan. Rata-ratanya bahkan sedikit lebih rendah (−0,0006).

❓ **Kalau ditanya "kenapa pakai uji-t, tidak cukup lihat selisihnya?"**
> "Karena selisih kecil bisa saja cuma kebetulan dari pembagian data tertentu, Pak. Uji-t berpasangan pada kelima fold menjawab apakah selisih itu konsisten. p-value 0,3575 jauh di atas 0,05, jadi perbedaannya tidak bisa dibedakan dari kebetulan."

---
---

# ⚪ Dua berkas opsional

## `inspect_features.py` (205 baris)

**Pertanyaan:** kata apa yang paling menentukan keputusan model?

### `extract_feature_weights(pipeline)` 📍 baris 51

```python
tfidf = pipeline.named_steps["tfidf"]
svm = pipeline.named_steps["svm"]

feature_names = tfidf.get_feature_names_out()

# coef_ adalah sparse matrix scipy dengan shape (1, n_features).
# Harus .toarray() untuk konversi ke numpy 2D, lalu .ravel() ke 1D.
weights = svm.coef_.toarray().ravel()

df = pd.DataFrame({
    "feature": feature_names,
    "weight": weights,
}).sort_values("weight", ascending=False).reset_index(drop=True)
```

**Cara kerjanya:** pada SVM kernel **linear**, tiap fitur punya satu koefisien. Positif besar = kuat menandakan spam; negatif besar = kuat menandakan non-spam. Berkas ini cuma memasangkan nama fitur dengan koefisiennya.

⚠️ Ini **hanya bisa dilakukan pada kernel linear.** Kalau kamu ganti ke RBF, `coef_` tidak ada dan berkas ini gagal — karena RBF tidak punya bobot per fitur yang bisa dibaca langsung. Ini salah satu alasan praktis memilih kernel linear: **modelnya bisa dijelaskan.**

**Hasil riil dari model sekarang:**

| Penanda spam | Bobot | | Penanda non-spam | Bobot |
|---|---|---|---|---|
| `judolbrand` | **+12,4969** | | `judol` | −1,6697 |
| `pulauwin` | +6,4552 | | `judi` | −1,4846 |
| `nagamastoto` | +3,6410 | | `bang` | −1,3314 |
| `gacorwini` | +3,6066 | | `berhenti` | −0,9340 |
| `maxwin` | +2,6447 | | `bandar` | −0,8121 |

🎯 **Dua hal yang sangat berguna untuk sidang:**

**1.** `judolbrand` berbobot **+12,50**, hampir dua kali fitur terkuat berikutnya. Ini **bukti empiris** bahwa keputusanmu menyatukan nama brand itu benar — jawaban terkuat untuk *"kenapa nama situs disatukan?"*

**2.** Kata `judol` dan `judi` justru penanda **non-spam**. Kelihatan aneh tapi masuk akal: yang menulis "judol" terang-terangan biasanya orang yang **mengkritik**, bukan yang mempromosikan. Promotor menyamarkan, pengkritik menyebut blak-blakan.

💡 Poin nomor 2 menunjukkan pemahaman mendalam. Simpan untuk sesi tanya jawab.

## `experiment_features.py` (288 baris)

**Pertanyaan:** kombinasi parameter TF-IDF mana yang terbaik?

| Baris | Isi |
|---|---|
| 63 | `CONFIGS` — daftar kombinasi yang diuji |
| 119 | `run_one_config(cfg, ...)` |
| 200 | `save_csv(results)` → `reports/experiment_features.csv` |

Menguji variasi `ngram_range` dan `max_features`. Membenarkan pilihan `(1,2)` dan `10.000`. **Tidak masuk skripsi** — tapi kalau ditanya "kenapa ngram (1,2)?", data pendukungnya ada di sini.

---
---

# Bonus: dua berkas di luar `src/`

## `scraper/index.js` — panggilan API 📍 baris 347

```js
const baseUrl =
  `https://www.googleapis.com/youtube/v3/commentThreads` +
  `?part=snippet&videoId=${VIDEO_ID}&key=${API_KEY}&maxResults=100`;
```

🎯 **Ini bukti "bukan web scraping".** Endpoint `commentThreads` adalah API resmi Google. Tidak ada satu pun baris yang mengunduh HTML halaman YouTube lalu mengurainya.

Kalau penguji menantang soal ini — **buka baris ini di layar.** Satu baris kode mengalahkan penjelasan lima menit.

### Skoring heuristik 📍 baris 149

```js
// [+40] Pola brand judol: nama + angka khas
const brandPattern =
  /[a-z]{3,}(88|99|77|69|138|388|777|888|4d|toto|bet|win|qq)\b/i;
if (brandPattern.test(lowerText)) {
  score += 40;
  activeSignals.push("brand_pattern");
}

// [+40] Link atau nomor kontak
const contactPattern =
  /(wa\.me|08[0-9]{8,11}|\+62[0-9]{9,12}|bit\.ly|s\.id|link\s?di|cek\s?profil|kunjungi|situs)/;
if (contactPattern.test(lowerText)) {
  score += 40;
  activeSignals.push("contact_link");
}
```

### Syarat penyimpanan 📍 baris 240 & 387

```js
const hasPrimarySignal =
  activeSignals.includes("brand_pattern") ||
  activeSignals.includes("contact_link") ||
  activeSignals.includes("soft_brand_testimonial");

return { score: Math.min(score, 100), normalizedText,
         activeSignals, hasPrimarySignal };
```

```js
if (
  analysis.score >= SPAM_SCORE_THRESHOLD &&   // >= 30
  analysis.hasPrimarySignal                    // wajib ada sinyal primer
) {
  spamResults.push({ ... });
}
```

🔍 **Kenapa `hasPrimarySignal` wajib?** Tanpa itu, komentar normal yang kebetulan pakai banyak emoji (+15) dan huruf kapital (+10) bisa lolos hanya dari sinyal tersier. Syarat ini memaksa harus ada **nama brand atau link**, bukan sekadar gaya menulis yang ramai.

## `extension/content.js` — sisi klien

### Alamat server 📍 baris 29

```js
const API_BASE = "https://api-svm.cupsky.my.id";
const API_URL = `${API_BASE}/predict`;
const BATCH_API_URL = `${API_BASE}/predict/batch`;
```

⚠️ Kalau mengubah `API_BASE`, **wajib** ubah juga `host_permissions` di `manifest.json`. Kalau tidak, permintaannya diblokir Chrome.

### Pemindaian per batch 📍 baris 374

```js
const BATCH_SIZE = 50;
for (let i = 0; i < toProcess.length; i += BATCH_SIZE) {
  const batch = toProcess.slice(i, i + BATCH_SIZE);
  const texts = batch.map((item) => item.text);

  const results = await predictBatch(texts);
  if (!results) continue;

  results.forEach((result, idx) => {
    if (result.is_spam && result.confidence >= confidenceThreshold) {
      hideSpamComment(batch[idx].element, result.confidence, batch[idx].text);
    }
  });
}
```

📌 **Dua syarat harus terpenuhi** sebelum komentar disembunyikan: labelnya spam **dan** keyakinannya melewati ambang batas. Model bisa saja bilang "spam" dengan keyakinan 0,60 — dan itu tidak akan disembunyikan kalau ambangnya 0,75.

### Dua mode penyembunyian 📍 baris 273

```js
function hideSpamComment(element, confidence, originalText) {
  element.dataset.judolDetected = "spam";
  element.dataset.judolConfidence = confidence.toFixed(2);
  element.dataset.judolText = originalText;

  if (hideMode === "remove") {
    element.style.display = "none";
    hiddenCount++;
    return;
  }

  element.style.transition = "opacity 0.3s ease, max-height 0.5s ease";
  element.style.opacity = "0.15";
  element.style.border = "1px solid #ff4444";
  ...
}
```

🔍 **Kenapa Redupkan jadi bawaan?** Karena model bisa salah. Mode redup membuat kesalahan itu **bisa diperbaiki pengguna** — komentar masih ada, tinggal diklik badge-nya. Mode hilangkan tidak memberi jalan kembali.

Ini keputusan desain yang berpihak pada korban *false positive*, sejalan dengan alasan presisi (0,98) dijaga lebih tinggi dari recall (0,9485).

### Pemantau komentar baru 📍 baris 484

```js
let scanTimeout = null;

const observer = new MutationObserver(() => {
  clearTimeout(scanTimeout);
  scanTimeout = setTimeout(scanComments, 1000);
});
```

🔍 **Pola `clearTimeout` + `setTimeout` itu *debounce*.** YouTube mengubah DOM puluhan kali per detik saat menggulir. Tanpa debounce, `scanComments()` terpanggil puluhan kali dan membanjiri server. Dengan ini, pemindaian baru berjalan setelah DOM tenang selama 1 detik.

❓ Kalau ditanya *"bagaimana komentar yang baru muncul saat scroll?"* — jawabannya ini.

---
---

# Peta cepat: buka apa kalau ditanya apa

| Pertanyaan penguji | Lokasi |
|---|---|
| "Angka 97,53% dari mana?" | `train.py:409` |
| "Bagaimana teks tersamar ditangani?" | `preprocessing.py:182` |
| "Kenapa nama situs disatukan?" | `preprocessing.py:297` + bobot +12,50 |
| "Kenapa normalisasi di server?" | `server.py:41` dan `server.py:372` |
| "Kenapa C = 1?" | `train.py:233` dan `train.py:253` |
| "Bagaimana mencegah kebocoran data?" | `train.py:253` (`X_train`, bukan `X`) |
| "Bagaimana Anda melabeli data?" | `prepare_dataset.py:155`, `:177`, `:238` |
| "Ini pakai kata kunci juga ya?" | `server.py:192` → `False` |
| "Kenapa tidak pakai stemming?" | `experiment_stemming.py:219` → p = 0,3575 |
| "Apakah SVM benar lebih baik?" | `compare_baselines.py:54` (split sama) |
| "Kata apa yang paling menentukan?" | `inspect_features.py:51` |
| "Kalau komentarnya ambigu?" | `evaluate_hard_set.py` → 98,52% |
| "Ini web scraping bukan?" | `scraper/index.js:347` |
| "Komentar baru saat scroll?" | `content.js:484` |

---

# Lima lokasi kode yang wajib hafal

| # | Lokasi | Kenapa |
|---|---|---|
| 1 | `train.py:409` | asal angka 97,53% |
| 2 | `preprocessing.py:182` | `clean_text()` — judul skripsimu |
| 3 | `server.py:372` | bukti tidak ada training-serving skew |
| 4 | `train.py:253` | bukti tidak ada kebocoran data |
| 5 | `server.py:192` | bukti hibrida dimatikan atas dasar bukti |

Lima itu menjawab sekitar 80% pertanyaan teknis yang mungkin muncul.

---

# Kalau masih buntu membaca sebuah berkas

1. **Baca docstring paling atas.** Tiga baris pertama menjawab "kenapa berkas ini ada".
2. **Lompat ke `main()`.** Itu daftar isi berkasnya.
3. **Lihat konstanta huruf besar.** Itu panel kendalinya.
4. **Baru buka satu fungsi** yang kamu butuhkan.
5. **Jangan baca fungsi grafik** (`save_*_plot`). Isinya matplotlib mengatur warna dan label — nol logika penelitian.

Poin 5 penting: dari 476 baris `train.py`, sekitar 150 baris cuma urusan menggambar grafik. Melewatinya menghemat banyak waktu tanpa kehilangan apa pun.
