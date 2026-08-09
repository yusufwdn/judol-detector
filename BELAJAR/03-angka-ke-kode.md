# 03 — Dari Angka ke Kode

> Setiap angka yang kamu tulis di skripsi, ditelusuri sampai baris kode yang menghasilkannya.

Ini dokumen yang paling sering dibuka saat sidang. Kalau penguji menunjuk satu angka dan bertanya "ini dari mana?", jawabannya ada di sini.

**Semua angka di halaman ini sudah diverifikasi ulang** dengan menjalankan pipeline dari nol pada 1 Agustus 2026 — bukan disalin dari dokumen lama.

---

## Ringkasan cepat

| Angka | Artinya | Sumber |
|---|---|---|
| 6.690 | Total komentar | `data/comments.csv` |
| 2.332 / 4.358 | Spam / non-spam | `data/comments.csv` |
| 5.352 / 1.338 | Data latih / uji | `train.py:197` |
| **97,53%** | Akurasi | `train.py:409` |
| **0,9726** | F1-macro | `train.py:410` |
| 863 / 9 / 24 / 442 | TN / FP / FN / TP | `train.py:418` |
| 0,9741 ± 0,0030 | Cross-validation | `train.py:128` |
| C = 1 | Parameter terbaik | `train.py:255` |
| 97,09% · 93,95% | LogReg · Naive Bayes | `compare_baselines.py:164` |
| 98,52% · 2 FP | Hard test set | `evaluate_hard_set.py:123` |
| −7,32 · −16,30 | Ablasi hibrida | `evaluate_hybrid_ablation.py` |
| p = 0,3575 | Uji stemming | `experiment_stemming.py` |
| 0,75 | Ambang batas | `extension/content.js` |

---

# 1. Angka dataset

## 6.690 komentar · 2.332 spam · 4.358 non-spam

📄 **Di skripsi:** Sub-bab 4.3.4 (Tabel 4.4 Komposisi Dataset), abstrak, dan Sub-bab 3.1
📍 **Di kode:** berkas `data/comments.csv`, dibaca oleh `src/train.py:79`

🔍 **Cara angka ini terbentuk:**

```
scraper/index.js          → ambil komentar mentah dari YouTube Data API v3
        ↓                    (menghasilkan final_spam.json & final_non_spam.json)
src/prepare_dataset.py    → saring & beri label
        ↓
data/comments.csv         → 6.690 baris, kolom: text, label, source
```

Berkas CSV-nya punya tiga kolom. Kolom `source` mencatat asal tiap baris (ID video YouTube, atau `manual_override` kalau labelnya dikoreksi manual) — ini penting kalau penguji menanyakan keterlacakan data.

✅ **Verifikasi sendiri:**
```bash
python -c "import pandas as pd; d=pd.read_csv('data/comments.csv'); print(len(d)); print(d['label'].value_counts())"
```
Keluaran: `6690`, lalu `non_spam 4358`, `spam 2332`.

❓ **Kalau ditanya "kenapa spam lebih sedikit dari non-spam?"**
> "Karena mencerminkan kondisi nyata, Pak — di kolom komentar, spam memang minoritas. Ketimpangan ini ditangani lewat `class_weight='balanced'` pada model dan pemilihan F1-macro sebagai metrik utama, supaya kelas yang lebih sedikit tetap dihitung setara."

---

## 5.352 data latih · 1.338 data uji

📄 **Di skripsi:** Sub-bab 4.10.1
📍 **Di kode:** `src/train.py:197`

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,        # 6.690 x 0,2 = 1.338 data uji
    random_state=42,      # pengacakan tetap -> bisa direproduksi
    stratify=y            # proporsi spam:non-spam dijaga sama
)
```

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)
```

🔍 **Hitungannya:** 6.690 × 20% = 1.338 untuk uji. Sisanya 6.690 − 1.338 = **5.352** untuk latih.

Tiga pengaturan yang perlu kamu bisa jelaskan:
- `test_size=0.2` → 20% disisihkan sebagai data ujian
- `random_state=42` → kunci acakan supaya pembagiannya bisa diulang persis
- `stratify=y` → komposisi spam/non-spam dijaga sama di kedua bagian

❓ **Kalau ditanya "kenapa 80:20, bukan 70:30?"**
> "80:20 adalah proporsi yang paling lazim dipakai, Pak. Dengan 6.690 data, 20% sudah memberi 1.338 sampel uji — cukup besar untuk hasil yang stabil, sambil menyisakan data latih yang memadai. Selain itu evaluasinya tidak hanya bergantung pada satu pembagian ini, karena diperkuat dengan 5-fold cross-validation."

---

# 2. Angka hasil utama

## Akurasi 97,53%

📄 **Di skripsi:** Sub-bab 4.10.1, Tabel 4.10, abstrak
📍 **Di kode:** `src/train.py:409`

```python
y_pred = pipeline.predict(X_test)                       # baris 403

acc = accuracy_score(y_test, y_pred)                    # baris 409  → 0,9753
f1_macro = f1_score(y_test, y_pred, average="macro")    # baris 410  → 0,9726
print(f"\nOverall Accuracy : {acc:.2%}")
```

🔍 **Rumus dan perhitungannya:**

```
Accuracy = (TP + TN) / (TP + TN + FP + FN)
         = (442 + 863) / 1.338
         = 1.305 / 1.338
         = 0,97534
         → 97,53%
```

Artinya: dari 1.338 komentar uji, **1.305 ditebak benar** dan 33 salah.

❓ **Kalau ditanya "97,53% ini dari mana?"**
> "Dari 1.338 data uji, Pak. Model menebak benar 1.305 komentar — yaitu 442 spam yang benar terdeteksi ditambah 863 non-spam yang benar dibiarkan. Dibagi 1.338 hasilnya 0,9753."

---

## Confusion matrix 863 / 9 / 24 / 442

📄 **Di skripsi:** Tabel 4.11, Gambar 4.7
📍 **Di kode:** `src/train.py:418`

```python
labels = ["non_spam", "spam"]                            # baris 417
cm = confusion_matrix(y_test, y_pred, labels=labels)     # baris 418
print(f"{'Aktual non_spam':20} {cm[0][0]:>18} {cm[0][1]:>14}")
print(f"{'Aktual spam':20} {cm[1][0]:>18} {cm[1][1]:>14}")
```

📌 `labels=["non_spam", "spam"]` itu **wajib**. Tanpa itu sklearn mengurutkan kelas sesuai abjad, dan posisi TN/FP/FN/TP di matriksnya bisa tertukar tanpa peringatan.

|  | Ditebak non-spam | Ditebak spam |
|---|---|---|
| **Aslinya non-spam** | **TN = 863** | **FP = 9** |
| **Aslinya spam** | **FN = 24** | **TP = 442** |

Cek konsistensi: 863 + 9 + 24 + 442 = **1.338** ✅ sama dengan jumlah data uji.

🔍 **Cara membacanya untuk sidang:**
- **9 false positive** = 9 komentar normal ikut disembunyikan. Ini yang mengganggu pengguna.
- **24 false negative** = 24 spam lolos. Ini kegagalan tujuan utama.

Perhatikan FN (24) lebih banyak dari FP (9). Artinya model ini **cenderung berhati-hati** — lebih memilih membiarkan spam lolos daripada salah menuduh komentar normal. Itu perilaku yang bisa kamu bela: bagi pengguna, komentar sendiri yang hilang lebih menyebalkan daripada satu spam yang lewat.

❓ **Kalau ditanya "kenapa false negative lebih banyak dari false positive?"**
> "Itu konsekuensi dari mengutamakan pengalaman pengguna, Pak. Model cenderung berhati-hati sebelum menuduh sebuah komentar sebagai spam. Kalau ambang batasnya diturunkan, false negative akan berkurang tapi false positive bertambah. Karena itu ambangnya dibuat dapat diatur pengguna antara 0,50 sampai 0,95."

---

## Precision 0,98 · Recall 0,95 · F1 0,96

📄 **Di skripsi:** Tabel 4.10
📍 **Di kode:** `src/train.py:415` → `classification_report(y_test, y_pred)`

🔍 **Semua untuk kelas spam:**

```
Precision = TP / (TP + FP) = 442 / (442 + 9)  = 442 / 451 = 0,98004 → 0,98
Recall    = TP / (TP + FN) = 442 / (442 + 24) = 442 / 466 = 0,94850 → 0,95
F1        = 2 × (0,98004 × 0,94850) / (0,98004 + 0,94850) = 0,96401 → 0,96
```

⚠️ **Perhatikan:** di skripsi ditulis dua desimal (0,98 dan 0,95). Kalau penguji minta lebih presisi, angka aslinya **0,9800** dan **0,9485**. Keduanya benar — cuma beda pembulatan.

---

## F1-macro 0,9726

📄 **Di skripsi:** Sub-bab 4.10.1, abstrak
📍 **Di kode:** `src/train.py:410` → `f1_score(y_test, y_pred, average="macro")`

🔍 **Cara hitungnya:** F1 kelas spam dan F1 kelas non-spam dirata-rata **biasa** (bukan ditimbang jumlah data).

```
F1 spam      ≈ 0,9640
F1 non-spam  ≈ 0,9812
F1-macro     = (0,9640 + 0,9812) / 2 = 0,9726
```

Dipakai macro, bukan weighted, supaya kelas spam yang jumlahnya lebih sedikit tetap punya bobot setara.

---

## Cross-validation 0,9741 ± 0,0030

📄 **Di skripsi:** Sub-bab 4.10.2, Gambar 4.8
📍 **Di kode:** `src/train.py:128`

```python
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
    ("svm", SVC(kernel="linear", class_weight="balanced", random_state=42))
])

scores = cross_val_score(pipeline, X, y, cv=5,
                         scoring="f1_macro", n_jobs=-1)   # baris 128
print(f"    Mean  : {scores.mean():.4f}")                 # → 0,9741
print(f"    Std   : {scores.std():.4f}")                  # → 0,0030
```

📌 Perhatikan argumennya `X, y` — **seluruh** 6.690 data, bukan `X_train`. Validasi silang memang sengaja dijalankan sebelum pembagian data, karena tujuannya menguji kestabilan model secara umum, bukan mengukur performa akhir.

```python
scores = cross_val_score(pipeline, X, y, cv=5, scoring="f1_macro", n_jobs=-1)
```

🔍 Skor lima putaran: **0,9734 · 0,9700 · 0,9743 · 0,9734 · 0,9793**
Rata-rata **0,9741**, simpangan baku **0,0030**.

⚠️ **Detail yang sering ditanya:** cross-validation ini dijalankan pada **seluruh 6.690 data**, bukan hanya data latih. Alasannya ada di komentar kode baris 109–115: tujuan CV adalah menaksir kemampuan generalisasi, dan makin banyak data yang dilipat, makin stabil taksirannya. Ini terpisah dari pembagian 80:20 yang tujuannya berbeda — memberi rincian per kelas dan confusion matrix.

❓ **Kalau ditanya "kenapa simpangan bakunya penting?"**
> "Karena menunjukkan konsistensi, Pak. Simpangan baku 0,0030 itu sangat kecil — artinya performa model hampir sama di kelima putaran, tidak ada satu putaran yang jauh lebih buruk. Kalau simpangannya besar, itu tanda hasilnya bergantung pada keberuntungan pembagian data."

---

## C = 1

📄 **Di skripsi:** Sub-bab 4.10.3, Gambar 4.9
📍 **Di kode:** `src/train.py:233` (daftar kandidat) dan `:255` (pemenangnya)

```python
param_grid = {"svm__C": [0.01, 0.1, 1, 10, 100]}      # baris 233

grid_search = GridSearchCV(
    pipeline, param_grid, cv=5,
    scoring="f1_macro", n_jobs=-1, verbose=0,
)
grid_search.fit(X_train, y_train)                     # baris 253

best_C = grid_search.best_params_["svm__C"]           # baris 255  → 1
```

🎯 `X_train` di baris 253, **bukan** `X`. Ini pencegahan kebocoran data — kalau pencarian C melihat data uji, angka akhirnya jadi terlalu optimistis dan tidak sah.

```python
param_grid = {"svm__C": [0.01, 0.1, 1, 10, 100]}
...
best_C = grid_search.best_params_["svm__C"]
```

🔍 Lima nilai diuji, masing-masing dengan cross-validation, lalu yang skornya tertinggi dipilih. Pemenangnya **C = 1** dengan F1-macro 0,9728 pada data latih.

⚠️ **Poin penting untuk dibela:** pencarian ini dijalankan **hanya pada data latih** (`X_train`), tidak menyentuh data uji. Kalau data uji ikut dipakai memilih C, artinya data uji sudah bocor mempengaruhi model dan skor akhirnya tidak jujur — istilahnya *data leakage*. Kodenya sudah benar.

❓ **Kalau ditanya "kenapa C = 1, bukan nilai lain?"**
> "Tidak ditentukan manual, Pak. Lima nilai diuji lewat GridSearchCV — 0,01 sampai 100 — masing-masing dievaluasi dengan cross-validation, dan C = 1 memberi skor terbaik. Pencariannya hanya memakai data latih supaya data uji tetap bersih."

---

# 3. Angka pembanding

## Logistic Regression 97,09% · Naive Bayes 93,95%

📄 **Di skripsi:** Sub-bab 4.10.4, Tabel 4.12
📍 **Di kode:** `src/compare_baselines.py:164`

| Algoritma | Akurasi | F1-macro |
|---|---|---|
| **SVM** | **97,53%** | **0,9726** |
| Logistic Regression | 97,09% | 0,9675 |
| Multinomial Naive Bayes | 93,95% | 0,9313 |

⚠️ **Yang membuat perbandingan ini sah:** ketiganya memakai **fitur TF-IDF yang sama persis** dan **pembagian data yang sama**. Yang berbeda cuma algoritma klasifikasinya. Kalau fiturnya beda, perbandingannya tidak adil.

🔍 **Kenapa Naive Bayes paling rendah?** Naive Bayes berasumsi tiap fitur saling bebas — kemunculan kata "slot" dianggap tidak berhubungan dengan kemunculan kata "gacor". Padahal pada spam judol, kata-kata itu justru muncul bersamaan sebagai satu pola. Asumsi yang tidak terpenuhi inilah yang membuat performanya tertinggal.

🔍 **Kenapa Logistic Regression begitu dekat (selisih 0,44 poin)?** Karena keduanya sama-sama pemisah linear. Bedanya di cara menentukan garis: SVM memaksimalkan margin, LogReg memaksimalkan kemungkinan statistik. Pada data yang mudah dipisah, hasilnya memang mirip.

❓ **Kalau ditanya "selisih SVM dan Logistic Regression cuma 0,44%, kenapa tetap pilih SVM?"**
Ini pertanyaan bagus dan jujur. Jawaban yang jujur juga:
> "Betul, selisihnya tipis, Pak. SVM tetap dipilih karena tiga alasan: unggul konsisten di semua metrik, memiliki dasar teoretis margin maksimum yang membuatnya lebih tahan terhadap data baru, dan sesuai dengan judul serta fokus penelitian ini. Tapi saya juga mencatat di skripsi bahwa Logistic Regression merupakan alternatif yang sangat kompetitif untuk kasus ini."

Jangan mengarang keunggulan yang tidak ada. Mengakui selisihnya tipis justru menunjukkan kamu paham datanya.

---

# 4. Angka uji ketahanan

## Hard test set: 135 kasus · 98,52% · 2 FP

📄 **Di skripsi:** Sub-bab 4.10.5
📍 **Di kode:** `src/evaluate_hard_set.py:123`
📄 **Berkas hasil:** `reports/hard_set_evaluation.txt`

🔍 **Apa itu hard test set?** 135 komentar yang **semuanya bukan spam**, tapi sengaja dipilih yang paling membingungkan — komentar korban judol, kritik terhadap judol, atau diskusi yang menyebut nama situs judi.

Contoh nyata dari berkas hasilnya:
> *"Brantas pak, ini situs Judi online yg saya tahu... Udintogel, Zara4d, Playbook88 dll"*

Kalimat itu **melaporkan** situs judi, bukan mempromosikannya. Tapi kata-katanya persis seperti spam. Inilah ujian sesungguhnya.

**Hasilnya:** 133 dari 135 benar → akurasi **98,52%**, dengan **2 false positive** dan **0 false negative**.

---

## ⚠️ RANJAU: F1-macro 0,4963

**Ini bagian terpenting di seluruh dokumen ini. Baca sampai paham.**

Kalau penguji membuka `reports/hard_set_evaluation.txt`, dia akan melihat:

```
Accuracy : 98.52%
F1-macro : 0.4963      ← terlihat seperti model rusak
FP       : 2
FN       : 0
```

Angka 0,4963 itu terlihat seperti model cuma menebak-nebak. **Padahal modelnya baik-baik saja.**

🔍 **Penyebabnya:** hard test set berisi **135 komentar yang semuanya non-spam** — nol contoh spam (lihat `evaluate_hard_set.py:34`).

F1-macro = rata-rata F1 dari kedua kelas:
- F1 kelas non-spam ≈ **0,9926** (sangat baik)
- F1 kelas spam = **0** — bukan karena model gagal, tapi karena **tidak ada spam sama sekali untuk dideteksi**. Tidak ada TP yang mungkin, jadi F1-nya nol secara definisi.

```
F1-macro = (0,9926 + 0) / 2 = 0,4963
```

**Jadi angka itu artefak dari komposisi data uji, bukan indikator performa.** Untuk data yang isinya satu kelas saja, metrik yang bermakna adalah **akurasi** dan **jumlah false positive** — dan itulah yang dilaporkan di skripsi.

❓ **Kalau penguji menunjuk angka 0,4963:**
> "Angka itu memang terlihat rendah, Pak, tapi tidak bermakna dalam konteks ini. Hard test set sengaja disusun berisi 135 komentar yang seluruhnya bukan spam — tidak ada satu pun contoh spam di dalamnya. Karena F1-macro merata-ratakan kedua kelas, dan kelas spam tidak punya data sama sekali, F1 kelas itu otomatis nol lalu menyeret rata-ratanya. Metrik yang tepat untuk pengujian ini adalah akurasi 98,52% dan jumlah false positive yang hanya 2 dari 135. Itulah yang saya laporkan di skripsi."

**Kalau kamu bisa menjawab ini dengan tenang, kamu justru terlihat sangat menguasai.** Yang berbahaya bukan angkanya — tapi kalau kamu ikut kaget melihatnya.

---

## Ablasi hibrida: −7,32 dan −16,30 poin

📄 **Di skripsi:** Sub-bab 4.10.6, Tabel 4.13
📍 **Di kode:** `src/evaluate_hybrid_ablation.py`
📄 **Berkas hasil:** `reports/hybrid_ablation.txt`

| Pengujian | SVM murni | SVM + aturan hibrida | Selisih |
|---|---|---|---|
| Data uji (n=1.338) | 97,53% | 90,21% | **−7,32 poin** |
| Hard test set (n=135) | 98,52% | 82,22% | **−16,30 poin** |

🔍 **Apa yang diuji?** Gagasan awalnya masuk akal: perkuat SVM dengan aturan kata kunci manual — kalau komentar mengandung sinyal spam yang jelas, langsung tandai spam tanpa menunggu keputusan model.

**Hasilnya justru memburuk.** Dan memburuknya paling parah di hard test set — turun 16,30 poin, dengan false positive melonjak dari 2 jadi 24.

**Kenapa?** Karena hard test set berisi komentar yang **menyebut** nama situs judi tanpa mempromosikannya. Aturan kata kunci tidak bisa membedakan "melaporkan situs judi" dari "mempromosikan situs judi" — dia cuma melihat ada kata kuncinya, lalu menuduh. SVM bisa membedakan karena mempertimbangkan seluruh kombinasi kata dalam kalimat, bukan satu kata terpisah.

**Ini temuan yang bagus, bukan kegagalan.** Kamu menguji sebuah hipotesis, hipotesisnya terbantah, dan kamu melaporkannya dengan jujur beserta buktinya. Itu penelitian yang benar.

❓ **Kalau ditanya "kenapa aturan hibrida tidak dipakai?"**
> "Karena diuji dan terbukti merugikan, Pak. Saya menambahkan aturan heuristik di atas SVM, lalu mengukur dampaknya lewat ablation study. Akurasi turun 7,32 poin pada data uji dan 16,30 poin pada hard test set. Penyebabnya, aturan kata kunci tidak bisa membedakan komentar yang melaporkan situs judi dari yang mempromosikannya, sehingga false positive melonjak dari 2 menjadi 24. Karena itu SVM murni yang dipertahankan."

---

## Stemming: p-value 0,3575

📄 **Di skripsi:** Sub-bab 4.10.7, Gambar 4.10
📍 **Di kode:** `src/experiment_stemming.py`

| Fold | Tanpa stemming | Dengan stemming |
|---|---|---|
| 1 | 0,9734 | 0,9726 |
| 2 | 0,9700 | 0,9691 |
| 3 | 0,9743 | 0,9727 |
| 4 | 0,9734 | 0,9718 |
| 5 | 0,9793 | 0,9810 |

🔍 Selisih rata-ratanya **−0,0006** — dengan stemming justru sedikit lebih rendah, tapi selisihnya sangat kecil.

Pertanyaannya: apakah selisih sekecil itu nyata, atau cuma kebetulan? Untuk menjawabnya dipakai **paired t-test**, hasilnya **p = 0,3575**.

Karena p jauh di atas 0,05, kesimpulannya: **belum terbukti ada perbedaan**. Jadi stemming tidak dipakai — menambah beban komputasi tanpa manfaat yang terbukti.

⚠️ **Hati-hati merumuskan kesimpulan.** Yang benar: *"belum terbukti stemming membantu"*. Yang salah: *"terbukti stemming tidak membantu"*. Uji statistik tidak bisa membuktikan ketiadaan efek — dia cuma bisa gagal menemukan bukti adanya efek. Penguji yang teliti akan menghargai ketelitian bahasa ini.

❓ **Kalau ditanya "kenapa tidak pakai stemming? Bukankah itu standar dalam pemrosesan teks?"**
> "Memang lazim, Pak, dan saya sudah mengujinya. Perbandingan berpasangan pada lima fold menghasilkan selisih F1-macro hanya −0,0006 dengan p-value 0,3575. Karena jauh di atas 0,05, perbedaannya belum bisa dianggap signifikan secara statistik. Jadi stemming tidak dipakai karena menambah waktu komputasi tanpa manfaat yang terbukti — dan waktu komputasi itu penting karena sistem ini harus menjawab secara real-time."

---

# 5. Angka sistem

## Ambang batas 0,75 · rentang 50–95%

📄 **Di skripsi:** Sub-bab 4.11
📍 **Di kode:** `extension/content.js` (ambang bawaan), `extension/popup.html` (slider `min=50 max=95`)

🔍 Nilai 0,75 adalah **keputusan produk**, bukan hasil perhitungan. Artinya: komentar baru disembunyikan kalau model yakin minimal 75%.

Jangan mengaku angka ini hasil optimasi kalau memang bukan. Jawaban jujurnya:
> "0,75 dipilih sebagai titik tengah yang wajar antara terlalu agresif dan terlalu longgar, Pak. Karena nilai terbaiknya bergantung pada preferensi masing-masing pengguna — ada yang lebih terganggu oleh spam yang lolos, ada yang lebih terganggu kalau komentarnya ikut tersembunyi — nilainya dibuat dapat diatur sendiri antara 50% sampai 95%."

## Transparansi 15% · batas batch 50

📍 **Di kode:** `extension/content.js` (opacity mode Redupkan), `src/server.py` (validasi `/predict/batch`)

Batas 50 komentar per permintaan itu perlindungan standar API — mencegah satu permintaan raksasa membebani server.

---

# 6. Angka konfigurasi TF-IDF

📄 **Di skripsi:** Sub-bab 4.3
📍 **Di kode:** `src/train.py:63`

```python
TFIDF_PARAMS = dict(
    max_features=10000,   # ambil 10.000 kata/bigram tersering
    ngram_range=(1, 2),   # kata tunggal DAN pasangan kata
    min_df=2,             # abaikan yang cuma muncul di 1 dokumen
    sublinear_tf=True,    # pakai 1 + log(tf), bukan tf mentah
)
```

🔍 **Bukti `ngram_range=(1,2)` berguna:** pada model terlatih, kata `slot` sendirian berbobot **−0,3800** (penanda non-spam), tapi bigram `slot machine` berbobot **+0,5223**. Tanpa bigram, model kehilangan kemampuan membedakan keduanya.

| Pengaturan | Nilai | Alasan singkat |
|---|---|---|
| `max_features` | 10.000 | Batasi kolom, buang ekor panjang yang jarang muncul |
| `ngram_range` | (1, 2) | Kata tunggal **dan** pasangan kata — `link slot` beda makna dari `link` saja |
| `min_df` | 2 | Kata yang cuma muncul sekali di seluruh dataset dibuang (biasanya salah ketik) |
| `sublinear_tf` | True | Pengulangan kata tidak dianggap berlipat ganda |

Penjelasan lengkap tiap pengaturan ada di `01-kamus-ml.md` bagian "Empat pengaturan TF-IDF".

---

# Cara memverifikasi semuanya sendiri

Kalau kamu ingin membuktikan sendiri bahwa angka-angka ini benar (dan ini **sangat disarankan** minimal sekali sebelum sidang), ada skrip verifikasi di `LAB-praktik.md` Sesi 2.

Intinya menjalankan ulang pipeline dari nol dan membandingkan keluarannya dengan yang tertulis di skripsi. Kalau semuanya cocok, kamu bisa berdiri di depan penguji dengan tenang — karena kamu tahu angkanya bukan sekadar salinan.

---

## Selanjutnya

Lanjut ke `06-bank-pertanyaan.md` untuk latihan tanya jawab, atau `04-kenapa-a-bukan-b.md` untuk mendalami justifikasi tiap keputusan teknis.
