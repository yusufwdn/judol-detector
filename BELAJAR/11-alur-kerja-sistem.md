# 11 — Alur Kerja Sistem, Berurutan dari Awal sampai Akhir

> Dokumen lain menjelaskan **per berkas**. Dokumen ini menjelaskan **per alur** — mengikuti satu potong data dari saat ia diambil sampai jadi angka di skripsimu.

Bedanya dengan dokumen lain:

| Dokumen | Sudut pandang |
|---|---|
| `02-bedah-kode.md` | Per berkas: "apa isi `train.py`?" |
| `03-angka-ke-kode.md` | Per angka: "97,53% dari baris mana?" |
| **`11` (ini)** | **Per alur: "apa yang terjadi, urut, dari mentah sampai hasil?"** |

**Semua angka di dokumen ini diambil langsung dari model terlatih** (`model/svm_model.joblib`) dengan menjalankan kodenya, bukan dikarang.

---

## Enam alur yang ada di sistem ini

```
ALUR 1  Pengumpulan data      scraper/index.js          → final_spam.json
ALUR 2  Penyiapan dataset     src/prepare_dataset.py    → data/comments.csv
ALUR 3  Prapemrosesan         src/preprocessing.py      → teks bersih
ALUR 4  Pelatihan model       src/train.py              → model/svm_model.joblib
ALUR 5  Inferensi runtime     extension/ + src/server.py → komentar disembunyikan
ALUR 6  Eksperimen tambahan   src/evaluate_*.py, dll    → reports/
```

Alur 1–4 adalah **build-time** — dijalankan sekali oleh kamu. Alur 5 adalah **runtime** — berjalan tiap kali pengguna membuka YouTube. Alur 6 berdiri sendiri, tidak memengaruhi sistem.

⚠️ Alur 1 dan 2 **tidak perlu dijalankan lagi**. Datanya sudah ada. Menjalankan ulang justru membuat angka skripsimu berubah.

---

---

# ALUR 1 — Pengumpulan Data

📍 `scraper/index.js` (550 baris) · dijalankan dengan `node index.js <VIDEO_ID>`

## Yang terjadi, urut

```
1. Baca VIDEO_ID dari argumen           📍 baris 15
2. Panggil YouTube Data API v3          📍 baris 348–349
3. Untuk tiap komentar → hitung skor    📍 baris 138  analyzeSpamScore()
4. Simpan kalau lolos syarat            📍 baris 388
5. Ambil halaman berikutnya             📍 baris 407  nextPageToken
6. Tulis hasil ke JSON                  📍 baris 311  saveResults()
```

## Langkah 2 — Panggilan API

```js
// scraper/index.js:348
`https://www.googleapis.com/youtube/v3/commentThreads` +
`?part=snippet&videoId=${VIDEO_ID}&key=${API_KEY}&maxResults=100`
```

🎯 **Ini bukti "bukan web scraping".** Endpoint `commentThreads` adalah API resmi Google. Tidak ada satu pun baris yang mengunduh HTML halaman YouTube lalu mengurainya.

Kalau penguji menantang soal ini, **buka baris ini di layar.** Satu baris kode mengalahkan penjelasan lima menit.

## Langkah 3 — Skoring heuristik ⭐

📍 baris 138, fungsi `analyzeSpamScore()`

Ini **bukan machine learning**. Ini aturan manual berbobot, tugasnya cuma satu: menyaring kandidat spam supaya kamu tidak perlu membaca 20.000 komentar satu per satu.

Sistem bobot berlapis:

| Lapis | Sinyal | Bobot | Baris |
|---|---|---|---|
| **Primer** | `brand_pattern` — nama + angka khas (`88`, `777`, `4d`, `toto`, `bet`, `win`, `qq`) | **+40** | 155 |
| **Primer** | `contact_link` — `wa.me`, nomor HP, `bit.ly`, "link di bio" | **+40** | 164 |
| **Primer** | `soft_brand_testimonial` — nama+angka **dan** kalimat endorse | **+35** | 236 |
| Sekunder | `obfuscated_keyword` — `g a c o r`, `m@xw!n`, `z3u5` | +30 | 183 |
| Sekunder | `plain_keyword` — `depo`, `wd`, `slot`, `rungkad` *(hanya kalau obfuscated tidak aktif)* | +20 | 192 |
| Sekunder | `high_symbol_ratio` — simbol > 15% dari total karakter | +20 | 201 |
| Tersier | `emoji_spam` — 2+ emoji berurutan | +15 | 211 |
| Tersier | `excessive_caps` — kapital > 50% | +10 | 221 |

Skor dibatasi maksimum 100 📍 baris 248.

### Contoh perhitungan

Komentar: `🎰💰 GACOR PARAH!! daftar MAXWIN88 wa.me/628123456789`

| Sinyal | Cek | Bobot |
|---|---|---|
| `brand_pattern` | `MAXWIN88` cocok `[a-z]{3,}(88\|...)` | +40 |
| `contact_link` | `wa.me` cocok | +40 |
| `plain_keyword` | `daftar`/`gacor` — tapi obfuscated tidak aktif, jadi ini yang kena | +20 |
| `emoji_spam` | 🎰💰 berurutan | +15 |
| `excessive_caps` | GACOR PARAH → >50% kapital | +10 |
| | **Total** | **125 → dibatasi 100** |

## Langkah 4 — Syarat penyimpanan

📍 baris 388

```js
analysis.score >= SPAM_SCORE_THRESHOLD &&   // >= 30, baris 53
analysis.hasPrimarySignal                    // wajib ada sinyal primer
```

🔍 **Kenapa `hasPrimarySignal` wajib?** Tanpa itu, komentar normal yang kebetulan pakai banyak emoji (+15) dan huruf kapital (+10) bisa lolos hanya dari sinyal tersier. Syarat sinyal primer memaksa harus ada **nama brand atau link**, bukan sekadar gaya menulis yang ramai.

❓ **Kalau ditanya "kenapa ambangnya 30?"**
> "30 itu sengaja saya set rendah, Pak, karena tahap ini tugasnya menjaring lebar — biar tidak ada spam yang terlewat. Penyaringan ketatnya justru di tahap berikutnya, `prepare_dataset.py`, dengan ambang 80. Jadi ada dua lapis: jaring lebar dulu, baru disaring ketat."

---

---

# ALUR 2 — Penyiapan Dataset

📍 `src/prepare_dataset.py` (357 baris) · `python src/prepare_dataset.py`

Masukan: `scraper/final_spam.json` + `final_non_spam.json` → Keluaran: `data/comments.csv`

## Yang terjadi, urut

```
1. Muat spam JSON, saring dua tahap    📍 baris 54   load_spam_data()
2. Muat non-spam JSON                  📍 baris 201  load_non_spam_data()
3. Terapkan koreksi manual             📍 baris 238  apply_manual_overrides()
4. Gabung, acak, tulis CSV             📍 baris 308  build_and_save_dataset()
```

## Langkah 1 — Penyaringan dua tahap ⭐

Ambang di sini **80**, jauh lebih ketat dari scraper 📍 baris 50.

### Tahap 1 — lolos ambang utama 📍 baris 155
```python
if score >= threshold:      # >= 80
    spam_entries.append(...)
```
Skor ≥ 80 berarti minimal dua sinyal primer aktif. Keyakinan tinggi, langsung masuk.

### Tahap 2 — penyelamatan brand 📍 baris 177
```python
elif "brand_pattern" in signals and (
    BRAND_RESCUE_PATTERN.search(normalized)      # ALL-CAPS + digit: ROMA4D, WIFI4D
    or BRAND_SUFFIX_PATTERN.search(normalized)   # [3+huruf]TOTO|BET|WIN|QQ
):
```

🔍 **Kenapa tahap ini ada?** Spammer yang pakai obfuscation Unicode (`𝑅𝒪𝑀𝒜𝟦𝒟`) biasanya juga menghias komentarnya dengan emoji dan simbol. Akibatnya skornya nyangkut di 60–75 — **di bawah 80**, padahal jelas spam. Tahap 2 menyelamatkan mereka, dengan syarat nama brand betul-betul terlihat di teks yang sudah dinormalisasi.

🔍 **Kenapa polanya ALL-CAPS, bukan case-insensitive?** 📍 baris 128

Ini pilihan yang menarik dan layak diceritakan:

> `BRAND_SUFFIX_PATTERN = re.compile(r'\b[A-Z]{3,}(?:TOTO|BET|WIN|QQ)\b')`

Kalau case-insensitive, kata Indonesia biasa seperti **"ngebet"** dan **"seribet"** ikut kena (keduanya berakhir `bet`). Dengan memaksa ALL-CAPS, `NGEBET` yang ditulis huruf besar memang bisa lolos — tapi itu jarang, sementara `ngebet` lowercase yang umum jadi aman.

Ini **trade-off sadar**, bukan kelalaian. Kalau ditanya, jawab begitu.

## Langkah 3 — Koreksi manual 📍 baris 238

Berkas `data/manual_overrides.csv` dibaca tiap kali skrip dijalankan. Dua jenis koreksi:
- label `non_spam` → buang dari kumpulan spam (memperbaiki *false positive* heuristik)
- label `spam` → tambahkan ke kumpulan spam (menyelamatkan yang terlewat)

🎯 **Ini yang membuat pelabelanmu bisa disebut "manual", bukan murni otomatis.** Heuristik hanya menjaring; keputusan akhir tetap ada padamu, dan tercatat dalam berkas yang bisa diperiksa.

❓ **Kalau ditanya "bagaimana Anda memastikan labelnya benar?"**
> "Ada dua lapis, Pak. Heuristik menjaring kandidat berdasarkan skor, lalu saya periksa manual dan koreksinya saya catat di `manual_overrides.csv`. Berkas itu ikut dibaca ulang setiap dataset dibangun, jadi koreksinya tidak hilang dan prosesnya bisa diulang orang lain."

## Hasil akhir

```
data/comments.csv  →  6.690 baris  (2.332 spam · 4.358 non-spam)
```

---

---

# ALUR 3 — Prapemrosesan ⭐

📍 `src/preprocessing.py` · fungsi `clean_text()` **baris 182**

🎯 **Berkas ini yang paling penting di seluruh proyek**, karena judul skripsimu memuat "String Normalization" — dan inilah wujudnya.

⭐ Fungsi ini dipanggil **identik** saat pelatihan dan saat inferensi. Itu yang mencegah *training-serving skew*.

## Tujuh tahap, dengan baris persisnya

| # | Tahap | Baris | Yang dilakukan |
|---|---|---|---|
| 1 | Buang karakter tak terlihat | 201 | zero-width space, BOM, soft hyphen |
| 2 | Normalisasi NFKC | 217 | `𝑅𝒪𝑀𝒜𝟦𝒟` → `ROMA4D` |
| 2b | Buang tanda diakritik | 226 | `P͟U͟L͟A͟U͟W͟I͟N` → `PULAUWIN` |
| 2c | Buka pembungkus kurung | 239 | `[P][U][L][A][U]` → `PULAU` |
| 3 | Petakan homoglyph | 251 | Cyrillic `а` → Latin `a` |
| 4 | Emoji jadi kata | 257 | 🎰 → `slot_machine` |
| 5 | Huruf kecil | 268 | |
| 5b-i | Normalisasi leet speak | 271 | `H0KI` → `HOKI`, `s1tus` → `situs` |
| 5b | Satukan nama brand | 294 | semua nama situs → `judolbrand` |
| 6 | Buang URL, angka, simbol | 299 | sisakan huruf a–z dan spasi |
| 7 | Rapikan, buang stopword | 306 | buang token 1 huruf |

## Telusuri satu teks melalui ketujuh tahap

Masukan:
```
𝑅𝒪𝑀𝒜𝟦𝒟 daftar sekarang bonus gede 🎰💰 dijamin gacor maxwin
```

| Setelah tahap | Hasilnya |
|---|---|
| 2 (NFKC) | `ROMA4D daftar sekarang bonus gede 🎰💰 dijamin gacor maxwin` |
| 4 (demojize) | `ROMA4D daftar sekarang bonus gede :slot_machine::money_bag: dijamin ...` |
| 5 (lowercase) | `roma4d daftar sekarang bonus gede slot_machine money_bag ...` |
| 5b-i (leet) | `romaad`? **tidak** — `4` tidak dipetakan, hanya `0→o` dan `1→i` |
| 5b (brand) | `judolbrand daftar sekarang bonus gede slot machine money bag ...` |
| 7 (akhir) | **`judolbrand daftar sekarang bonus gede slot machine money bag dijamin gacor maxwin`** |

✅ Keluaran ini **diverifikasi dengan menjalankan kodenya**, bukan diperkirakan.

## Dua keputusan yang paling sering ditanya

### Kenapa nama brand disatukan jadi `judolbrand`? 📍 baris 294

Kalau tidak, tiap nama situs baru (`ROMA4D`, `PULAUWIN`, `NAGAMASTOTO`, …) jadi fitur terpisah. Model harus melihat contoh tiap nama untuk mengenalinya — dan nama baru muncul tiap minggu.

Dengan menyatukannya jadi satu token, model belajar **satu pola** yang berlaku untuk nama yang belum pernah ia lihat sekalipun.

📊 **Buktinya ada di bobot model.** Token `judolbrand` punya bobot **+12,4969** — hampir dua kali lipat fitur terkuat berikutnya (`pulauwin`, +6,4552). Ini fitur paling menentukan di seluruh model.

### Kenapa leet speak hanya `0→o` dan `1→i`? 📍 baris 271

Karena `3→e`, `4→a`, `5→s` terlalu berisiko memutilasi angka yang sah. Komentar "skor 354" akan berubah jadi "skor esa" — merusak data yang tidak bersalah.

⚠️ **Batasan jujur yang layak kamu akui:** aturan ini tetap punya efek samping. Komentar `depo 10rb wd jutaan` berubah jadi `depo iorb wd jutaan` — `10rb` jadi `iorb`. Kalau ditanya soal keterbatasan sistem, ini contoh nyata yang bagus untuk disebut. Menyebut batasan sendiri jauh lebih meyakinkan daripada mengklaim sempurna.

---

---

# ALUR 4 — Pelatihan Model ⭐⭐

📍 `src/train.py` (475 baris) · `python src/train.py`

## Tujuh tahap

```
[1/7] Muat dataset                📍 baris 71
[2/7] Prapemrosesan seluruh teks  📍 baris 95
[3/7] Validasi silang 5-fold      📍 baris 105
[4/7] Bagi data 80:20             📍 baris 184
[5/7] Cari nilai C (GridSearchCV) 📍 baris 208
[6/7] Latih model final           📍 baris 321
[7/7] Evaluasi + simpan           📍 baris 386, 436
```

⚠️ Perhatikan urutannya: **validasi silang dijalankan SEBELUM pembagian data**, pada seluruh 6.690 baris. Sedangkan pencarian C hanya pada 5.352 data latih. Bedanya penting — lihat penjelasan di bawah.

## Tahap 3 — Validasi silang 📍 baris 105

```python
# baris 128
scores = cross_val_score(pipeline, X, y, cv=5, scoring="f1_macro", n_jobs=-1)
```

Data dibagi 5 bagian. Model dilatih 5 kali, tiap kali satu bagian jadi penguji dan empat sisanya jadi pelatih.

**Hasil riil:**
```
Fold: 0,9734 · 0,9700 · 0,9743 · 0,9734 · 0,9793
Rata-rata : 0,9741
Simpangan : 0,0030
```

Simpangan 0,0030 artinya performanya **stabil** — bukan kebetulan dari satu pembagian data yang beruntung.

💡 **Detail halus yang bisa jadi nilai plus:** pipeline pada tahap ini 📍 baris 126 memakai `SVC(...)` **tanpa** `probability=True`, berbeda dari pipeline final 📍 baris 335. Alasannya: kalibrasi probabilitas butuh cross-validation internal tambahan, dan pada tahap ini kita cuma butuh skor F1 — jadi dimatikan supaya hemat waktu. Kalau kamu menyebut ini, penguji tahu kamu benar-benar membaca kodenya.

## Tahap 4 — Pembagian data 📍 baris 197

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

| Parameter | Fungsi |
|---|---|
| `test_size=0.2` | 20% jadi data uji → 6.690 × 0,2 = **1.338** |
| `random_state=42` | pengacakan tetap → hasil bisa direproduksi persis |
| `stratify=y` | proporsi spam:non-spam di kedua bagian dijaga sama |

❓ **Kalau `stratify=y` dihapus?** Pembagian jadi acak murni. Bisa saja data uji kebetulan berisi spam jauh lebih sedikit dari proporsi aslinya, sehingga akurasinya menyesatkan.

## Tahap 5 — Pencarian nilai C 📍 baris 208

```python
param_grid = {"svm__C": [0.01, 0.1, 1, 10, 100]}   # baris 233
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring="f1_macro")
grid_search.fit(X_train, y_train)                   # baris 253  ← HANYA data latih
```

🎯 **`X_train`, bukan `X`.** Ini pencegahan kebocoran data (*data leakage*). Kalau pencarian C melihat data uji, angka akhirnya jadi terlalu optimistis dan tidak sah.

**Hasil: C = 1.**

### Apa arti C?

C mengatur seberapa keras model menghukum kesalahan saat latihan:

| C | Sikap model | Risiko |
|---|---|---|
| 0,01 | Sangat toleran, margin lebar | *underfitting* — terlalu banyak salah |
| **1** | **Seimbang** | **← terpilih** |
| 100 | Sangat galak, margin sempit | *overfitting* — hafal data latih |

**Analogi:** C itu seperti ketegasan guru saat mengoreksi. Terlalu longgar, murid tidak belajar. Terlalu galak, murid cuma menghafal soal latihan dan gagal di ujian sesungguhnya.

## Tahap 6 — Model final 📍 baris 333

```python
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=10000, ngram_range=(1,2),
                              min_df=2, sublinear_tf=True)),
    ("svm",   SVC(kernel="linear", C=best_C, class_weight="balanced",
                  probability=True, random_state=42))
])
pipeline.fit(X_train, y_train)   # baris 344
```

Model terlatih punya **8.342 fitur** dan **2.002 support vector** (1.311 non-spam + 691 spam).

---

## 🧮 PERHITUNGAN DI BALIK LAYAR

Bagian ini menjawab: *"angkanya dari mana?"* — dengan contoh yang benar-benar dihitung dari model.

### Langkah A — Teks jadi angka (TF-IDF)

Rumus yang dipakai scikit-learn:

```
tf(t,d)  = 1 + ln(frekuensi t di d)          ← karena sublinear_tf=True
idf(t)   = ln( (1+n) / (1+df(t)) ) + 1       ← karena smooth_idf=True (bawaan)
w(t,d)   = tf(t,d) × idf(t)
lalu seluruh vektor dokumen dinormalisasi L2
```

⚠️ **Penting dan jujur:** skripsimu menulis rumus baku `IDF = log(N/df)`. scikit-learn memakai versi **ter-smoothing** di atas. Bedanya: penambahan `1` mencegah pembagian nol untuk kata yang tidak pernah muncul, dan `+1` di akhir mencegah bobot nol untuk kata yang muncul di semua dokumen.

❓ **Kalau ditanya soal ini:**
> "Rumus yang saya tulis di skripsi adalah bentuk baku TF-IDF, Pak. Scikit-learn memakai varian ter-smoothing, yaitu `ln((1+n)/(1+df)) + 1`, untuk menghindari pembagian nol. Konsepnya sama — makin sering sebuah kata muncul di banyak dokumen, makin kecil bobotnya."

**Contoh nyata, dihitung dari model:**

Komentar `𝑅𝒪𝑀𝒜𝟦𝒟 daftar sekarang bonus gede 🎰💰 dijamin gacor maxwin`
→ setelah dibersihkan → 15 fitur aktif dari 8.342.

Ambil satu fitur, `judolbrand`:

```
frekuensi          = 1
tf sublinear       = 1 + ln(1)        = 1,0000
idf                                    = 2,4666
bobot mentah       = 1,0000 × 2,4666  = 2,4666
norma L2 dokumen                       = 23,2268
bobot akhir        = 2,4666 / 23,2268 = 0,1062   ✅ cocok dengan sklearn
```

### Langkah B — Angka jadi keputusan (SVM)

```
f(x) = Σ (w_i × x_i) + b
```

`w` = bobot yang dipelajari model per fitur. `x` = nilai TF-IDF. `b` = bias.

**Tabel kontribusi riil untuk komentar di atas:**

| Fitur | TF-IDF | bobot w | kontribusi |
|---|---|---|---|
| `judolbrand` | 0,1062 | **+12,4969** | **+1,3271** |
| `maxwin` | 0,2518 | +2,6447 | +0,6659 |
| `gacor` | 0,2280 | +1,9650 | +0,4480 |
| `bonus` | 0,2508 | +1,3716 | +0,3439 |
| `daftar sekarang` | 0,3289 | +0,5000 | +0,1644 |
| `slot machine` | 0,3136 | +0,5223 | +0,1638 |
| `money` | 0,2364 | +0,6243 | +0,1476 |
| … 8 fitur lain … | | | +0,3724 |
| | | **Σ** | **+3,6331** |
| | | bias `b` | −0,8563 |
| | | **f(x)** | **+2,7768** |

`f(x)` positif → kelas **spam**. Semakin besar, semakin jauh dari batas keputusan, semakin yakin.

💡 Perhatikan `slot` sendirian justru berbobot **−0,3800** (penanda non-spam), sementara bigram `slot machine` berbobot **+0,5223**. Itulah gunanya `ngram_range=(1,2)` — model bisa membedakan kata tunggal dari pasangan kata.

### Langkah C — Keputusan jadi persentase (Platt Scaling)

`f(x)` itu jarak, bukan probabilitas. Diubah lewat sigmoid:

```
P(spam|x) = 1 / (1 + exp( A·f(x) + B ))
```

Model ini menyimpan **A = −5,1547** dan **B = −0,6852**.

**Verifikasi dengan angka riil:**

| Komentar (setelah dibersihkan) | f(x) | P(spam) manual | P(spam) sklearn |
|---|---|---|---|
| `judolbrand daftar sekarang bonus …` | +2,7768 | 1,0000 | 1,0000 |
| `situs penipuan jangan daftar` | −0,1532 | 0,4738 | 0,4738 |
| `depo iorb wd jutaan` | −0,3066 | 0,2900 | 0,2900 |
| `video membantu terima kak` | −0,9680 | 0,0133 | 0,0135 |

✅ Rumusnya benar-benar mereproduksi keluaran sklearn.

🎯 **Baris `situs penipuan jangan daftar` itu emas untuk sidang.** Itu komentar *kritik*, bukan spam. Nilainya 0,4738 — di bawah 0,50, jadi tetap diklasifikasikan non-spam, **dan** jauh di bawah ambang bawaan 0,75 sehingga tidak akan disembunyikan. Ini contoh konkret kenapa ambang batas 0,75 masuk akal.

### Langkah D — Metrik akhir 📍 baris 409–418

```python
acc      = accuracy_score(y_test, y_pred)              # baris 409
f1_macro = f1_score(y_test, y_pred, average="macro")   # baris 410
cm       = confusion_matrix(y_test, y_pred)            # baris 418
```

Dari 1.338 data uji:

```
                 Prediksi
               non-spam  spam
Asli non-spam    863       9      ← 9 false positive
Asli spam         24     442      ← 24 false negative
```

```
Akurasi  = (442 + 863) / 1.338 = 1.305 / 1.338 = 0,9753
Presisi  = 442 / (442 + 9)     = 442 / 451     = 0,9800
Recall   = 442 / (442 + 24)    = 442 / 466     = 0,9485
F1 spam  = 2 × 0,98 × 0,9485 / (0,98 + 0,9485) = 0,9640
F1-macro = rata-rata F1 kedua kelas             = 0,9726
```

---

---

# ALUR 5 — Inferensi Runtime

Ini yang berjalan tiap kali pengguna membuka YouTube.

## Yang terjadi, urut

```
KLIEN — extension/content.js
  1. Halaman dimuat, content script aktif       📍 baris 493  init()
  2. Ambil elemen komentar dari DOM             📍 baris 345  scanComments()
  3. Potong jadi batch 50                       📍 baris 374  BATCH_SIZE
  4. Kirim POST /predict/batch                  📍 baris 153  predictBatch()

SERVER — src/server.py
  5. Terima permintaan                          📍 baris 353
  6. clean_text() tiap teks                     📍 baris 372  ← fungsi yang SAMA
  7. model.predict_proba()                      📍 baris 379
  8. Kembalikan label + skor

KLIEN kembali
  9. Sembunyikan yang lolos ambang              📍 baris 273  hideSpamComment()
 10. Pantau komentar baru saat scroll           📍 baris 484  MutationObserver
```

## Langkah 6 — Titik paling penting di seluruh sistem

```python
# src/server.py:372
cleaned = clean_text(text)
```

```python
# src/server.py:41
from src.preprocessing import clean_text
```

🎯 **Ini fungsi yang persis sama** dengan yang dipakai `train.py` saat pelatihan. Bukan salinan, bukan versi JavaScript — **impor dari berkas yang sama**.

❓ **Kalau ditanya "kenapa normalisasi di server, bukan di ekstensi?"**
> "Supaya tidak ada dua versi logika, Pak. Kalau normalisasi ditulis ulang dalam JavaScript di sisi klien, suatu saat versi Python dan versi JavaScript bisa berbeda — dan model akan menerima masukan dengan format yang tidak sesuai pelatihannya. Itu namanya *training-serving skew*. Dengan mengimpor fungsi yang sama, masalah itu mustahil terjadi."

## Langkah 9 — Dua mode penyembunyian 📍 baris 273

| Mode | Yang dilakukan | Baris |
|---|---|---|
| **Redupkan** | `opacity = 0.15` + badge persentase, bisa diklik untuk memunculkan | 286 |
| **Hilangkan** | `display = "none"`, hilang total | 279 |

🔍 **Kenapa Redupkan jadi bawaan?** Karena model bisa salah. Mode redup membuat kesalahan itu **bisa diperbaiki pengguna** — komentar masih ada, tinggal diklik. Mode hilangkan tidak memberi jalan kembali.

Ini keputusan desain yang berpihak pada korban *false positive*, dan sejalan dengan alasan presisi dijaga lebih tinggi dari recall.

## Langkah 10 — MutationObserver 📍 baris 484

YouTube memuat komentar secara bertahap saat pengguna menggulir. `MutationObserver` memantau perubahan DOM dan memicu pemindaian ulang untuk komentar yang baru muncul.

❓ **Kalau ditanya "bagaimana komentar yang baru muncul saat scroll?"** — jawabannya ini.

---

---

# ALUR 6 — Eksperimen Tambahan

Empat skrip yang berdiri sendiri. **Tidak memengaruhi sistem** — tugasnya membuktikan keputusan desainmu.

| Skrip | Menjawab pertanyaan | Keluaran |
|---|---|---|
| `compare_baselines.py` | Apakah SVM benar lebih baik? | 3 confusion matrix PNG |
| `evaluate_hard_set.py` | Tahan tidak terhadap kasus ambigu? | `reports/hard_set_evaluation.txt` |
| `evaluate_hybrid_ablation.py` | Apakah aturan kata kunci membantu? | `reports/hybrid_ablation.txt` |
| `experiment_stemming.py` | Apakah stemming membantu? | `experiment_stemming.png` + `_cv.png` |
| `experiment_features.py` | Kombinasi parameter TF-IDF terbaik? | `experiment_features.csv` + `.png` |
| `inspect_features.py` | Kata apa yang paling menentukan? | `top_features.png`, `feature_weights.csv` |

## Hasil dan artinya

**`compare_baselines.py`** → SVM 97,53% · LogReg 97,09% · NB 93,95%.
Dijalankan pada pembagian data yang sama persis (`random_state=42`), jadi perbandingannya adil.

**`evaluate_hard_set.py`** → akurasi 98,52%, 2 *false positive* dari 135.

⚠️ **RANJAU.** Berkas keluarannya juga memuat **F1-macro 0,4963**, yang terlihat seperti model gagal total. Penyebabnya: hard test set **seluruhnya berisi non-spam** 📍 `evaluate_hard_set.py:34`. Karena tidak ada satu pun data spam, F1 untuk kelas spam otomatis nol, dan rata-rata makro dari (0,9926 + 0) ≈ 0,4963.

Itulah sebabnya yang dilaporkan di skripsi adalah **accuracy**, bukan F1-macro. Dan naskahmu **sudah menjelaskan ini dengan benar**.

**`evaluate_hybrid_ablation.py`** → menambah aturan kata kunci di atas SVM **menurunkan** akurasi 7,32 poin (data uji) dan 16,30 poin (hard test set).

Kenapa? Aturan kata kunci memaksa komentar yang menyebut sinyal keras jadi spam — termasuk komentar korban dan kritik. *False positive* melonjak.

**`experiment_stemming.py`** → p-value 0,3575 → tidak signifikan.

Uji-t berpasangan pada F1-macro tiap fold. p = 0,3575 jauh di atas 0,05, jadi perbedaannya tidak bisa dibedakan dari kebetulan. Rata-ratanya bahkan sedikit lebih rendah (−0,0006).

🎯 **Dua hasil terakhir itu negatif, dan tetap dilaporkan.** Itu nilai plus akademik — menunjukkan pipeline yang dipakai sudah yang paling sederhana namun efektif, bukan hasil menumpuk teknik tanpa alasan.

---

---

# 🎛️ PANEL KENDALI — Kalau Mau A, Ubah B

Bagian untuk bereksperimen. Tiap baris: apa yang ingin kamu ubah, di mana tuasnya, dan apa akibatnya.

⚠️ **Aturan wajib sebelum bereksperimen:**

```bash
# 1. Amankan model dan dataset sekarang
cp model/svm_model.joblib model/svm_model.joblib.backup
cp data/comments.csv data/comments.csv.backup

# 2. Setelah selesai bereksperimen, kembalikan
cp model/svm_model.joblib.backup model/svm_model.joblib
```

**Jangan bereksperimen dalam 2 hari menjelang sidang.** Kalau model tertimpa, angka di skripsimu tidak lagi cocok.

---

## A. Mengubah perilaku deteksi (tanpa melatih ulang)

Paling aman — cukup ubah lalu muat ulang ekstensi.

| Mau begini | Ubah ini | Akibatnya |
|---|---|---|
| Lebih banyak komentar tersaring | Slider ambang batas di popup → turunkan ke 50% | Lebih banyak spam tertangkap, tapi *false positive* naik |
| Lebih sedikit salah tuduh | Slider → naikkan ke 95% | Lebih aman, tapi lebih banyak spam lolos |
| Ubah rentang slider itu sendiri | `extension/popup.html:355` → `min` / `max` / `step` | Mengubah pilihan yang tersedia bagi pengguna |
| Komentar spam hilang total | Popup → mode **Hilangkan** | `display:none` 📍 `content.js:279` |
| Ubah tingkat keburaman | `content.js:288` → `opacity = "0.15"` | 0 = tak terlihat, 1 = normal |
| Kurangi beban jaringan | `content.js:374` → `BATCH_SIZE` | Naikkan = lebih sedikit request tapi lebih berat per request |
| Lihat log rinci di konsol | `content.js:51` → `DEV_MODE = true` | Menyalakan `devLog()` |
| Pindah server | `content.js:29` `API_BASE` **dan** `manifest.json` `host_permissions` | ⚠️ **harus dua-duanya**, kalau tidak kena CORS |

---

## B. Mengubah cara teks dinormalisasi

📍 Semua di `src/preprocessing.py` · ⚠️ **wajib latih ulang** setelah diubah

| Mau begini | Ubah ini | Akibatnya |
|---|---|---|
| Tambah homoglyph baru | `HOMOGLYPH_MAP` 📍 baris 148 | Karakter tersamar baru ikut dinormalkan |
| Tambah pola nama situs | `JUDOL_BRAND_PATTERN` 📍 baris 107 | Nama brand baru ikut jadi `judolbrand` |
| Tambah/kurangi stopword | `STOPWORDS_ID` 📍 baris 123 | Menambah = kosakata mengecil; hati-hati membuang kata yang ternyata penanda |
| Petakan lebih banyak leet | `_normalize_leet` 📍 baris 288 | `3→e`, `4→a`, `5→s`. ⚠️ Berisiko merusak angka yang sah |
| Pertahankan emoji apa adanya | Hapus Step 4 📍 baris 265 | Emoji hilang di Step 6 → sinyalnya hilang. **Diperkirakan performa turun** |
| Matikan penyatuan brand | Komentari Step 5b 📍 baris 297 | Tiap nama situs jadi fitur sendiri. **Diperkirakan turun tajam** — `judolbrand` adalah fitur terkuat (+12,50) |
| Pakai stemming | Lihat `experiment_stemming.py` | Sudah diuji: **tidak signifikan** (p = 0,3575) |

💡 **Eksperimen paling menarik untuk dicoba:** matikan penyatuan brand (Step 5b), latih ulang, lihat akurasinya turun berapa. Itu membuktikan secara empiris bahwa keputusan desainmu benar — dan jadi jawaban yang sangat kuat kalau ditanya "kenapa nama brand disatukan?".

---

## C. Mengubah ekstraksi fitur

📍 `src/train.py:63` — `TFIDF_PARAMS` · ⚠️ wajib latih ulang

| Parameter | Sekarang | Kalau dinaikkan | Kalau diturunkan |
|---|---|---|---|
| `max_features` | 10.000 | Kosakata lebih kaya, latihan lebih lambat, risiko *overfitting* | Model lebih ringan, bisa kehilangan penanda langka |
| `ngram_range` | (1,2) | (1,3) menangkap frasa 3 kata, fitur meledak | (1,1) hanya kata tunggal — **hilang kemampuan bedakan `slot` dari `slot machine`** |
| `min_df` | 2 | 5 membuang kata langka, kosakata mengecil | 1 memasukkan salah ketik sekali muncul → berisik |
| `sublinear_tf` | `True` | — | `False` membuat kata yang diulang-ulang berbobot berlebihan |

🔍 **Kenapa `min_df=2`?** Kata yang cuma muncul sekali di seluruh dataset hampir pasti salah ketik atau kebetulan. Memasukkannya menambah dimensi tanpa menambah informasi.

📊 Kombinasi ini sudah diuji sistematis di `experiment_features.py`. Hasil lengkapnya di `reports/experiment_features.csv`.

---

## D. Mengubah model

📍 `src/train.py:333` · ⚠️ wajib latih ulang

| Mau begini | Ubah ini | Akibatnya |
|---|---|---|
| Coba kernel lain | `kernel="linear"` → `"rbf"` | Jauh lebih lambat pada 8.342 fitur. **Diperkirakan tidak lebih baik** — data teks TF-IDF sudah terpisah linear |
| Ubah rentang pencarian C | `param_grid` 📍 baris 233 | Rentang lebih rapat = pencarian lebih teliti tapi lebih lama |
| Matikan penyeimbangan kelas | Hapus `class_weight="balanced"` | Model condong ke kelas mayoritas (non-spam). **Recall spam diperkirakan turun** |
| Matikan probabilitas | Hapus `probability=True` | Latihan lebih cepat, **tapi ekstensi rusak** — tidak ada skor keyakinan |
| Ganti proporsi uji | `test_size=0.2` 📍 baris 199 | 0,3 = data uji lebih banyak, data latih lebih sedikit |
| Ubah jumlah fold | `cv=5` 📍 baris 128 | 10 = estimasi lebih halus, dua kali lebih lama |
| **Hilangkan reproduktibilitas** | Hapus `random_state=42` | ⚠️ **Jangan.** Hasilnya berubah tiap dijalankan dan angka skripsimu tidak bisa diverifikasi |

---

## E. Mengubah dataset

⚠️ **Paling berisiko.** Mengubah `data/comments.csv` mengubah **seluruh** angka di skripsimu.

| Mau begini | Ubah ini | Akibatnya |
|---|---|---|
| Longgarkan seleksi spam | `prepare_dataset.py:50` → turunkan dari 80 | Lebih banyak data, tapi label lebih berisik |
| Ketatkan seleksi spam | Naikkan di atas 80 | Label lebih bersih, data lebih sedikit |
| Perbaiki label yang salah | Tambah baris di `data/manual_overrides.csv` | Cara **yang benar** untuk mengoreksi label |
| Jaring lebih lebar saat scraping | `scraper/index.js:53` → turunkan dari 30 | Lebih banyak kandidat, lebih banyak sampah |
| Tambah data baru | `node scraper/index.js <VIDEO_ID>` | ⚠️ Mengubah dataset → **seluruh angka skripsi berubah** |

---

## Alur eksperimen yang aman

```bash
# 1. Amankan
cp model/svm_model.joblib model/svm_model.joblib.backup

# 2. Ubah SATU hal saja (kalau dua, kamu tidak tahu mana yang berpengaruh)

# 3. Latih ulang
python src/train.py

# 4. Catat perubahannya — akurasi & F1-macro naik atau turun?

# 5. Kembalikan
cp model/svm_model.joblib.backup model/svm_model.joblib

# 6. Pastikan angkanya kembali cocok dengan skripsi
python BELAJAR/verifikasi_angka.py
```

Langkah 6 wajib. Jangan pernah menutup sesi eksperimen tanpa memastikan angkanya kembali cocok.

---

# Ringkasan satu halaman

```
KOMENTAR MENTAH
   │
   │  scraper/index.js:138   skor heuristik 0–100, ambang 30 + wajib sinyal primer
   ▼
final_spam.json
   │
   │  prepare_dataset.py:155/177   ambang 80 + penyelamatan brand + koreksi manual
   ▼
data/comments.csv   6.690 baris (2.332 spam / 4.358 non-spam)
   │
   │  preprocessing.py:182   7 tahap → "judolbrand daftar sekarang bonus …"
   ▼
TEKS BERSIH
   │
   │  train.py:333   TF-IDF (8.342 fitur) → SVM linear C=1
   ▼
model/svm_model.joblib
   │
   │  server.py:372   clean_text() yang SAMA → predict_proba()
   ▼
{ label: "spam", confidence: 0.98 }
   │
   │  content.js:273   ambang 0,75 → redupkan / hilangkan
   ▼
KOMENTAR TERSEMBUNYI
```

**Titik yang paling sering ditanya, urut kemungkinannya:**

1. `train.py:409` — dari mana 97,53%
2. `preprocessing.py:294` — kenapa nama brand disatukan
3. `server.py:372` — kenapa normalisasi di server
4. `train.py:253` — kenapa cari C hanya pada data latih
5. `prepare_dataset.py:177` — kenapa ada tahap penyelamatan
