# Jurnal Perjalanan Pengembangan — Judol Spam Detector

> Dokumen ini menjawab pertanyaan: **"Kenapa proyek ini dibangun dengan urutan
> dan struktur seperti ini?"** — bukan sekadar "apa isinya", tapi "kenapa
> langkah A diambil sebelum B, dan kenapa bukan C".
>
> Tulisan ini sengaja ditulis seperti **cerita** (per "babak"), karena urutan
> kejadian itu sendiri adalah bagian dari logikanya. Setiap konsep teknis
> dijelaskan dulu dengan analogi sehari-hari, baru kemudian istilah resminya.
>
> **Posisi dokumen ini dibanding dokumen lain:**
> | Dokumen | Isi | Kapan dibaca |
> |---|---|---|
> | [README.md](README.md) | Cara install & menjalankan | Saat setup awal |
> | **JOURNEY.md** (ini) | Cerita & alasan di balik urutan keputusan | Untuk memahami "kenapa begini" |
> | [PENJELASAN_TEKNIS.md](PENJELASAN_TEKNIS.md) | Detail teknis tiap komponen + FAQ sidang | Untuk pendalaman & latihan tanya-jawab |
> | [TODO.md](TODO.md) | Rencana ke depan | Untuk planning lanjutan |
>
> Kalau kamu baru pertama kali baca, urutan paling enak: **JOURNEY.md (ini) →
> PENJELASAN_TEKNIS.md → README.md** (untuk praktik).

---

## Daftar Isi

- [Babak 0 — Mendefinisikan Masalah Sebelum Menulis Kode](#babak-0--mendefinisikan-masalah-sebelum-menulis-kode)
- [Babak 1 — Masalah Telur dan Ayam: Dari Mana Data Berlabel Datang?](#babak-1--masalah-telur-dan-ayam-dari-mana-data-berlabel-datang)
- [Babak 2 — Menyaring "Telur" yang Bagus: Dataset Preparation](#babak-2--menyaring-telur-yang-bagus-dataset-preparation)
- [Babak 3 — Menyamakan "Bahasa": Preprocessing 7 Layer](#babak-3--menyamakan-bahasa-preprocessing-7-layer)
- [Babak 4 — Mengajari Mesin: TF-IDF + SVM](#babak-4--mengajari-mesin-tf-idf--svm)
- [Babak 5 — Menjembatani Python dan Browser: FastAPI Server](#babak-5--menjembatani-python-dan-browser-fastapi-server)
- [Babak 6 — Turun ke Lapangan: Chrome Extension](#babak-6--turun-ke-lapangan-chrome-extension)
- [Babak 7 — Benang Merah: Training-Serving Consistency](#babak-7--benang-merah-training-serving-consistency)
- [Lampiran A — Tabel Keputusan Desain (Decision Log)](#lampiran-a--tabel-keputusan-desain-decision-log)
- [Lampiran B — Peta Mental Keseluruhan Sistem](#lampiran-b--peta-mental-keseluruhan-sistem)

---

## Babak 0 — Mendefinisikan Masalah Sebelum Menulis Kode

Sebelum baris kode pertama ditulis, pertanyaan yang harus dijawab dulu adalah:
**"Masalah konkret apa yang mau diselesaikan, dan kenapa pendekatan
sederhana tidak cukup?"**

Masalahnya: komentar promosi judi online ("judol") di YouTube/Instagram
sering ditulis dengan **penyamaran** — huruf Unicode dekoratif
(`𝑹𝑶𝑴𝑨𝟒𝑫`), karakter mirip-mirip dari alfabet lain (Cyrillic `а` vs Latin
`a`), atau emoji sebagai pengganti kata (`🎰💰`).

**Kenapa tidak pakai filter kata kunci biasa saja** (misal: kalau ada kata
"slot" atau "daftar" → blokir)?

Analoginya begini: bayangkan kamu satpam yang disuruh "tolak semua orang yang
bawa tas merah". Tas merah memang sering dibawa orang yang mencurigakan, tapi
tas merah juga dibawa anak sekolah, ibu-ibu belanja, dll. Kamu akan menolak
banyak orang baik-baik (**false positive**) sambil orang mencurigakan cukup
ganti warna tas (**mudah dihindari**).

Itulah yang terjadi kalau kita filter kata "daftar" — komentar **"daftar isi
episode ini ada di deskripsi"** (normal) ikut diblokir, sementara spammer
cukup menulis `𝒹𝒶𝒻𝓉𝒶𝓇` untuk lolos.

**Keputusan pertama proyek ini:** gunakan **machine learning** — sistem yang
belajar pola dari ribuan contoh, bukan aturan manual yang gampang basi.
Tapi ML butuh **data berlabel** dalam jumlah banyak. Dan di sinilah masalah
besar pertama muncul — dibahas di Babak 1.

---

## Babak 1 — Masalah Telur dan Ayam: Dari Mana Data Berlabel Datang?

Ini adalah **keputusan arsitektur paling awal dan paling sering terlewat**
dijelaskan di proyek-proyek serupa, jadi penting kamu paham betul.

### Masalahnya

Untuk melatih model ML klasifikasi, kita butuh ribuan contoh komentar yang
sudah diberi label `spam` / `non_spam`. Tapi:

- Tidak ada dataset publik siap pakai untuk "komentar judol berbahasa
  Indonesia"
- Memberi label manual ke ribuan komentar satu-per-satu **sangat memakan
  waktu**

Ini adalah **masalah telur dan ayam**: butuh model untuk otomatis memberi
label, tapi butuh data berlabel untuk melatih model.

### Solusi: Heuristik sebagai "Ayam Pertama"

Solusinya ada di `scraper/index.js`, fungsi `analyzeSpamScore()`. Alih-alih
langsung pakai ML, dibuat dulu **sistem skor berbasis aturan** (heuristik) —
mirip seperti "satpam dengan checklist", bukan ML, tapi cukup pintar untuk
menyaring kandidat awal.

Checklist-nya berlapis (lihat [PENJELASAN_TEKNIS.md bagian 3](PENJELASAN_TEKNIS.md#3-sistem-penilaian-spam-spam_score-dan-kelemahannya)
untuk detail tiap sinyal), intinya:

- **Sinyal Primer** (bobot besar, +40): ada pola nama brand judi
  (`MAXWIN88`), atau ada link/kontak (`wa.me/...`)
- **Sinyal Sekunder** (+20–30): kata kunci judi yang disamarkan (`g a c o r`)
  atau polos (`slot`, `depo`)
- **Sinyal Tersier** (+10–15): emoji berjejer, capslock berlebihan

**Analoginya:** ini seperti dokter yang melakukan skrining awal pasien
sebelum pemeriksaan lab lengkap — bukan diagnosis final, tapi cukup untuk
memutuskan "siapa yang perlu diperiksa lebih lanjut".

### Kenapa heuristik ini "cukup baik tapi tidak sempurna" — dan itu OK

Heuristik ini **sengaja dibuat sensitif** (banyak yang lolos saring) daripada
presisi (hanya yang benar-benar yakin). Konsekuensinya: ada false positive,
seperti kasus terkenal di proyek ini — kata **"kesambet"** ke-flag sebagai
spam karena mengandung substring **"bet"** (cocok dengan pola brand seperti
`SBOBET`).

Ini **bukan bug yang harus diperbaiki di scraper**. Kenapa? Karena:

1. Kalau pola `bet` dihapus dari regex, brand asli seperti `SBOBET88`,
   `MAXBET`, `BET138` jadi lolos tanpa terdeteksi — **lebih buruk**.
2. Tugas memisahkan "brand asli" vs "kata biasa yang kebetulan mirip" lebih
   tepat dilakukan di tahap berikutnya, dengan **konteks tambahan** (lihat
   Babak 2).

**Pelajaran penting:** dalam membangun sistem, kadang lebih baik membiarkan
satu komponen "agak kasar" (sensitif tapi tidak presisi), lalu menyaring
dengan komponen lain yang punya informasi lebih lengkap — daripada memaksa
satu komponen menjadi sempurna sendirian.

### Output Babak 1

`scraper/index.js` menghasilkan file-file di `result/`, lalu `filter.js` mengagregasikannya menjadi `final_spam.json` — kumpulan komentar "kandidat spam" (saat ini **2318 entries**), masing-masing menyimpan:

```json
{
  "original_text": "...",      // teks asli dari YouTube, apa adanya
  "normalized_text": "...",    // sudah di-NFKC normalize oleh scraper
  "spam_score": 40,             // hasil skrining heuristik
  "active_signals": ["brand_pattern"]
}
```

Dua field (`original_text` dan `normalized_text`) ini akan jadi krusial di
Babak 2 dan Babak 7.

---

## Babak 2 — Menyaring "Telur" yang Bagus: Dataset Preparation

File: `src/prepare_dataset.py`

### Masalah yang dilanjutkan dari Babak 1

Kita punya 2318 kandidat dengan skor 0–100. Kalau kita ambil semua sebagai
"spam", dataset kita tercemar oleh false positive seperti "kesambet".
Kalau kita hanya ambil yang skornya sangat tinggi (≥80), kita kehilangan
banyak spam asli yang skornya "tertekan" karena hanya memicu satu sinyal.

### Solusi: Two-Pass Filter

Bayangkan kamu sedang menyortir surat masuk ke dua tumpukan: "pasti penting"
dan "buang". Ada satu tumpukan ketiga: "ragu-ragu" — surat yang mencurigakan
tapi belum pasti. Untuk tumpukan ketiga ini, kamu punya **satu trik
tambahan**: lihat **amplopnya** (bukan isinya) — kalau amplopnya pakai
kop surat resmi perusahaan tertentu, kemungkinan besar itu memang dari
perusahaan tersebut, bukan surat nyasar.

Itu persis logika **two-pass filter**:

- **Pass 1 (skor ≥ 80):** "pasti penting" → langsung masuk sebagai spam.
  Hasilnya: 137 entry.
- **Pass 2 (rescue):** untuk entry dengan skor < 80 yang **HANYA** memicu
  sinyal `brand_pattern` — cek "amplopnya": apakah `normalized_text`
  mengandung pola **`[A-Z]{2,}\d+[A-Z0-9]*`** (huruf kapital + angka
  langsung setelahnya, contoh: `WIFI4D`, `ROMA4D`, `SBOBET88`)?

  - Kalau **ya** → ini brand judi asli yang ditulis pakai font Unicode
    dekoratif (setelah di-NFKC jadi huruf kapital + angka) → **selamatkan**,
    masuk sebagai spam. Hasilnya: 962 entry.
  - Kalau **tidak** → kemungkinan besar ini "kesambet"/"ribet" yang lolos
    secara kebetulan → **buang**.

**Kenapa hanya entry dengan SATU sinyal (`brand_pattern` saja) yang di-rescue?**
Karena kita ingin sangat spesifik — kalau ada sinyal lain juga (misal
`emoji_spam` + `brand_pattern`), skor rendahnya mungkin memang representasi
yang valid dari "sinyal lemah gabungan", bukan kasus brand-tersamar yang
butuh rescue.

Total hasil: **1099 spam** (137 + 962), dibanding kalau kita asal pakai
threshold 80 saja (cuma 137 — terlalu sedikit untuk training).

### Bagian kedua: data non-spam (sintetis)

Scraper di proyek ini **dirancang khusus mencari spam** — tidak ada
mekanisme untuk mengumpulkan komentar non-spam. Maka dibuat
`NON_SPAM_TEMPLATES`: ~150 contoh kalimat representatif (tutorial, gaming,
musik, reaksi umum), lalu fungsi `generate_non_spam_data()` mengambil sampel
acak (dengan sedikit variasi filler kalimat) sebanyak 700 kali.

**Ini adalah kompromi, bukan solusi ideal** — sudah ditandai sebagai item
prioritas di [TODO.md Fase 1](TODO.md#fase-1--kualitas-dataset-prioritas-tertinggi).
Kenapa rasio targetnya 2:1 (spam:non-spam) bukan 1:1? Karena di YouTube
nyata, video yang "diserbu" judol biasanya memang punya proporsi spam yang
lebih tinggi dari non-spam — rasio 1:1 yang "terlalu rapi" justru kurang
realistis.

### Kenapa pakai `original_text`, bukan `normalized_text`, untuk dataset final?

Ini pertanyaan yang **sangat mungkin ditanyakan saat sidang**. Jawabannya
berhubungan langsung dengan Babak 6 (extension) dan Babak 7 — jadi untuk
sekarang, ingat saja: **karena saat produksi nanti, extension membaca teks
mentah dari halaman web (persis seperti `original_text`), bukan teks yang
sudah dinormalisasi**. Kalau model dilatih dengan `normalized_text`, ada
risiko model "terbiasa" dengan format yang berbeda dari apa yang akan ia
terima nanti. Detail lengkapnya di Babak 7.

### Output Babak 2

`data/comments.csv` — **1800 baris** (1099 spam + ~700 non-spam), dua kolom:
`text` (mentah) dan `label` (`spam`/`non_spam`).

---

## Babak 3 — Menyamakan "Bahasa": Preprocessing 7 Layer

File: `src/preprocessing.py`, fungsi `clean_text()`

### Kenapa langkah ini perlu, secara intuitif

Bayangkan kamu mengajar anak kecil mengenali kata "KUCING". Kalau kamu
tunjukkan kartu bertuliskan "KUCING", "kucing", "Kucing", "K U C I N G", dan
"kucing 🐱" sebagai **lima kata yang berbeda total**, anak itu butuh 5x lebih
banyak contoh untuk akhirnya paham bahwa kelimanya merujuk ke konsep yang
sama.

Preprocessing adalah proses **menyeragamkan representasi** — supaya variasi
penulisan yang sebenarnya bermakna sama, terlihat sama juga oleh model.

Spammer judol justru **mengeksploitasi keberagaman representasi** ini secara
sengaja. Maka pipeline `clean_text()` punya 7 layer, masing-masing membongkar
satu jenis trik penyamaran. Urutan layer **tidak bisa diacak** — tiap layer
mengasumsikan layer sebelumnya sudah selesai.

Berikut ringkasan tiap layer dengan analoginya (detail regex/kode ada di
[PENJELASAN_TEKNIS.md bagian 7](PENJELASAN_TEKNIS.md#7-pipeline-preprocessing-7-lapisan)):

| # | Layer | Analoginya | Contoh |
|---|---|---|---|
| 1 | Strip zero-width chars | Menghapus **tinta tak kasat mata** yang diselipkan di antara huruf surat | `d​a​f​t​a​r` (ada karakter invisible) → `daftar` |
| 2 | NFKC normalize | Melepas **kostum/font dekoratif**, kembali ke bentuk standar | `𝑹𝑶𝑴𝑨𝟒𝑫` → `ROMA4D` |
| 3 | Homoglyph fix (Cyrillic/Greek) | Mengenali **kembaran identik** dari "negara lain" yang menyamar jadi huruf Latin | `dаftаr` (huruf 'а' Rusia) → `daftar` |
| 4 | Emoji → teks (demojize) | Menerjemahkan **bahasa simbol** jadi kata, bukan dihapus | `🎰` → `slot_machine` |
| 5 | Lowercase | Menyamakan ukuran font ke satu standar | `DAFTAR`/`Daftar`/`daftar` → `daftar` |
| 6 | Hapus URL & non-huruf | Membuang "alamat unik" (URL selalu beda-beda, jadi tidak berguna sebagai pola umum) dan noise simbol | `wa.me/6281234 daftar!!` → `daftar` |
| 7 | Hapus stopwords & token pendek | Membuang kata "basa-basi" yang muncul di hampir semua kalimat (`yang`, `dan`, `di`) | `daftar di sini` → `daftar` |

**Kenapa urutannya seperti ini, bukan acak?**

Contoh kritis: **Layer 5 (lowercase) harus SETELAH Layer 2 (NFKC)**. Kenapa?
Karena Pass 2 di Babak 2 mendeteksi brand dengan pola "huruf KAPITAL + angka"
(`WIFI4D`). Pola ini hanya terlihat **sebelum** lowercase. Kalau urutannya
dibalik, sinyal pembeda itu hilang duluan sebelum sempat dipakai.

(Catatan: deteksi brand di Babak 2 dilakukan terhadap `normalized_text` dari
scraper, bukan di dalam `clean_text()` — tapi prinsip "urutan transformasi
menentukan informasi apa yang masih bisa diekstrak" berlaku sama persis di
kedua tempat.)

### Output Babak 3

Sebuah fungsi `clean_text(text) -> str` yang **deterministik** — input yang
sama selalu menghasilkan output yang sama, di mana pun fungsi ini dipanggil.
Sifat "di mana pun dipanggil sama" inilah yang akan jadi pondasi Babak 7.

---

## Babak 4 — Mengajari Mesin: TF-IDF + SVM

File: `src/train.py`

Sekarang kita punya 1800 kalimat bersih dengan label. Tapi komputer/model
**tidak bisa membaca kalimat** — ia hanya bisa mengolah angka. Babak ini
punya 2 sub-masalah: (1) ubah teks jadi angka, (2) ajarkan model membedakan
pola angka spam vs non-spam.

### Sub-masalah 1: Mengubah Teks Jadi Angka (TF-IDF)

**Analogi:** Bayangkan kamu HRD yang membaca ratusan CV pelamar kerja, mencari
kata-kata yang **membedakan** pelamar yang relevan dari yang tidak.

- Kata seperti **"saya"**, **"pengalaman"**, **"kerja"** muncul di **hampir
  semua** CV → kata ini **tidak membantu** kamu membedakan pelamar.
- Kata seperti **"TensorFlow"** atau **"Adobe Premiere"** hanya muncul di
  beberapa CV, dan kalau muncul **berkali-kali** dalam satu CV, itu sinyal
  kuat bahwa pelamar itu memang ahli di bidang itu.

**TF (Term Frequency)** = "seberapa sering kata ini muncul **dalam CV ini**?"
**IDF (Inverse Document Frequency)** = "seberapa **langka** kata ini di
**seluruh tumpukan CV**?"

**TF-IDF = TF × IDF** → kata mendapat skor tinggi kalau **sering di satu
dokumen TAPI langka secara keseluruhan**. Persis kriteria "kata yang
membedakan".

Untuk proyek ini:
- Kata `"slot_machine"` (hasil demojize dari 🎰) → sering di komentar spam,
  langka di komentar lain → **skor tinggi**, fitur penting
- Kata `"video"` → sering muncul di mana-mana → skor rendah, tidak penting

**Konfigurasi yang dipakai** (`TfidfVectorizer`):
```python
TfidfVectorizer(
    max_features=10000,   # simpan 10.000 "kata kunci" dengan skor tertinggi
    ngram_range=(1, 2),   # hitung kata tunggal DAN pasangan kata berurutan
    min_df=2,             # abaikan kata yang cuma muncul di 1 komentar (kemungkinan typo)
    sublinear_tf=True      # redam dominasi kata yang muncul SANGAT sering
)
```

**Kenapa `ngram_range=(1,2)` (pakai bigram juga)?** Karena makna bisa berubah
total tergantung kata di sebelahnya. `"spam"` sendirian beda makna dengan
`"bukan spam"`. Kalau hanya unigram, kata `"spam"` di kedua kalimat dianggap
identik — padahal konteksnya berlawanan.

### Sub-masalah 2: SVM — Mencari "Garis Pemisah" Terbaik

Sekarang setiap komentar sudah jadi **vektor angka** (titik dalam ruang
berdimensi tinggi — bayangkan 10.000 sumbu, satu sumbu per kata/bigram).
Titik-titik ini ada yang berlabel "spam" dan ada yang "non_spam". Tugas SVM:
cari **batas pemisah** antara dua kelompok titik ini.

**Analogi paling sederhana:** Bayangkan kamu menaruh kelereng merah dan biru
di lantai, lalu kamu mau menaruh **sebatang tongkat lurus** yang memisahkan
keduanya. Ada banyak cara menaruh tongkat agar kedua kelompok terpisah — tapi
SVM mencari **posisi tongkat yang jaraknya paling jauh** ke kelereng terdekat
dari MASING-MASING kelompok.

```
    Spam (●)              Non-Spam (○)
       ●                          ○
     ●   ●     ←─ jarak ─→     ○     ○
           ●  ←────tongkat────►   ○
```

Kenapa "jarak paling jauh" (disebut **margin**) ini penting? Karena kalau
ada kelereng baru yang posisinya **agak meleset** dari kelereng-kelereng
training (data baru di dunia nyata SELALU sedikit berbeda), tongkat dengan
margin lebar masih punya "ruang toleransi" sebelum salah mengklasifikasikan.
Inilah konsep **generalisasi**.

Kelereng-kelereng yang **paling dekat dengan tongkat** (yang menentukan posisi
tongkat) disebut **Support Vectors** — asal nama "Support Vector Machine".

### Kenapa `kernel='linear'` (tongkat lurus, bukan lengkung)?

SVM bisa juga membuat "tongkat" berbentuk lengkung/kurva (kernel non-linear,
misal RBF) untuk kasus di mana data tidak bisa dipisah garis lurus dalam
dimensi rendah. Tapi:

1. Data kita **sudah** berdimensi sangat tinggi (10.000 dimensi dari TF-IDF)
2. Dalam dimensi setinggi itu, data **hampir selalu** sudah bisa dipisahkan
   dengan "garis lurus" (hyperplane linear)
3. Kernel non-linear lebih lambat dan lebih rentan **overfitting** untuk
   data teks

Analogi tambahan: kalau kamu punya 2 keping koin di meja, mungkin susah
memisahkan dengan garis lurus kalau posisinya saling tumpang tindih. Tapi
kalau kamu punya 10.000 keping koin tersebar di ruangan 3D, kemungkinan besar
ada **bidang datar** yang bisa memisahkan dua kelompok warna koin tersebut.
Makin tinggi dimensinya, makin mudah menemukan pemisah linear.

### Parameter `C=1.0` — Toleransi vs Ketegasan

**Analogi:** Bayangkan kamu guru yang membuat aturan kelas berdasarkan
perilaku murid-murid tahun ini.

- **C besar** → kamu guru yang **sangat ketat**, memaksa aturan yang bisa
  membedakan SEMUA murid tahun ini dengan sempurna — termasuk murid yang
  perilakunya "kebetulan aneh" (outlier). Tahun depan, murid baru yang
  perilakunya sedikit beda dari pola tahun ini bisa salah dinilai, karena
  aturanmu terlalu spesifik untuk tahun ini saja (**overfitting**).
- **C kecil** → kamu guru yang **lebih longgar**, rela "salah menilai" satu-dua
  murid aneh tahun ini demi punya aturan yang lebih umum dan tahan lama untuk
  tahun-tahun berikutnya (**generalisasi lebih baik**).

`C=1.0` adalah titik tengah yang jadi titik awal yang wajar — bukan hasil
optimasi (lihat [TODO.md Fase 2](TODO.md#fase-2--evaluasi-model-yang-lebih-jujur)
untuk rencana tuning sistematis dengan `GridSearchCV`).

### `class_weight='balanced'` — Mengoreksi Ketimpangan

Dataset kita: 1099 spam vs 700 non_spam (rasio ~1.6:1). Kalau dibiarkan,
model bisa "malas" dan condong menebak `spam` terus karena secara statistik
itu sering benar. `class_weight='balanced'` memberi "bobot ekstra" pada kelas
yang lebih sedikit (`non_spam`) — analoginya seperti **nilai ujian kelas yang
jumlah siswanya lebih sedikit di-scale up** supaya tetap punya pengaruh
seimbang ke nilai rata-rata sekolah.

### `probability=True` — Skor Keyakinan, Bukan Cuma Ya/Tidak

Tanpa ini, SVM hanya bisa bilang "spam" atau "non_spam" — biner. Tapi
extension butuh **angka keyakinan** (misal 97%) untuk menentukan apakah
cukup yakin untuk menyembunyikan komentar (threshold 75%, lihat Babak 6).

`probability=True` mengaktifkan **Platt Scaling** — sebuah model kecil
tambahan (logistic regression) yang dilatih *di atas* output SVM untuk
mengubah "jarak ke tongkat pemisah" menjadi "probabilitas 0–100%". Analoginya
seperti menambahkan "indikator level baterai" pada alat yang awalnya cuma
punya lampu nyala/mati.

### Pipeline & Kenapa Tidak Boleh Fit TF-IDF Sebelum Split

```python
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(...)),
    ("svm", SVC(...))
])
pipeline.fit(X_train, y_train)
```

Ingat, TF-IDF butuh "melihat seluruh dataset" untuk menghitung IDF (kata mana
yang langka). Kalau TF-IDF di-fit ke **seluruh data** (termasuk yang nanti
jadi test set) **sebelum** displit, maka informasi dari test set sudah
"bocor" ke proses training — disebut **data leakage**.

**Analoginya:** ini seperti siswa yang belajar untuk ujian dengan **sudah
membaca soal ujiannya duluan**. Nilai ujiannya pasti bagus, tapi itu tidak
mencerminkan kemampuan sebenarnya. `Pipeline` memastikan TF-IDF hanya
"belajar kosakata" dari `X_train`, lalu untuk `X_test` hanya **menerapkan**
kosakata yang sudah dipelajari (tanpa belajar ulang).

### Train-Test Split

```python
train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```

- `test_size=0.2` → 80% data untuk belajar, 20% "disembunyikan" untuk ujian
  akhir
- `stratify=y` → memastikan proporsi spam:non_spam di training set dan test
  set **sama** (tidak kebetulan test set isinya 95% spam semua)
- `random_state=42` → angka "kunci acak" yang tetap, supaya kalau script
  dijalankan ulang, hasil split-nya **identik** — penting untuk reproducibility
  (orang lain yang menjalankan kode yang sama akan dapat hasil yang sama
  persis)

### Output Babak 4

`model/svm_model.joblib` — satu file berisi **dua hal sekaligus**: "kamus"
TF-IDF (kosakata + bobot IDF dari training data) DAN "tongkat pemisah" SVM
yang sudah ditemukan posisinya.

---

## Babak 5 — Menjembatani Python dan Browser: FastAPI Server

File: `src/server.py`

### Masalah: Dua Dunia yang Tidak Bisa Bicara Langsung

Model di atas adalah objek Python (`scikit-learn`). Chrome extension hanya
bisa menjalankan JavaScript. **JavaScript tidak bisa langsung memanggil
fungsi Python** — dua bahasa ini berjalan di "dunia" yang sama sekali
terpisah.

**Analogi:** ini seperti dua orang yang masing-masing hanya bisa bahasa
Indonesia dan bahasa Jepang, harus bekerja sama. Solusinya bukan memaksa
salah satu belajar bahasa yang lain dari nol, tapi **menyewa penerjemah** —
sebuah "pihak ketiga" yang dipahami keduanya: dalam kasus ini, **HTTP**
(protokol web universal — keduanya bisa "bicara HTTP").

`server.py` adalah penerjemah ini: program Python yang "mendengarkan" di
`localhost:8000`, menerima request HTTP (yang bisa dikirim JavaScript via
`fetch()`), menjalankan model Python, dan mengirim balik hasil sebagai JSON
(format yang dipahami JavaScript).

### Kenapa FastAPI, bukan Flask (atau bikin server manual)?

Alasan utamanya adalah **validasi otomatis** lewat Pydantic:

```python
class PredictRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Text must not be empty")
        if len(v) > 5000:
            raise ValueError("Text too long (maximum 5000 characters)")
        return v
```

Tanpa ini, kamu harus menulis manual: "cek apakah field `text` ada, cek
apakah string, cek apakah kosong, cek panjangnya..." untuk SETIAP endpoint.
FastAPI + Pydantic melakukan semua ini otomatis berdasarkan **definisi tipe
data** — kamu cukup deklarasikan "bentuk data yang valid", sisanya
ditangani framework. Bonus: dokumentasi API interaktif otomatis muncul di
`/docs` tanpa kerja tambahan.

### Model Dimuat Sekali, Bukan Setiap Request

```python
@app.on_event("startup")
async def startup_event():
    load_model()
```

**Analogi:** Bayangkan kamu kasir yang harus **membuka brankas** setiap kali
ada pelanggan, lalu menutupnya lagi setelah transaksi. Sangat lambat. Lebih
baik brankas dibuka **sekali di awal shift**, lalu kamu cukup ambil dari
laci yang sudah terbuka untuk setiap transaksi berikutnya.

`model` disimpan sebagai variabel global yang diisi **sekali** saat server
pertama kali nyala (`startup_event`). Setiap request `/predict` setelahnya
tinggal memakai model yang sudah ada di memori — jauh lebih cepat daripada
`joblib.load()` ulang setiap kali.

### CORS — Kenapa Perlu "Mengizinkan Tamu Asing"?

Browser punya kebijakan keamanan: halaman dari domain A **tidak boleh**
diam-diam mengirim request ke server domain B (mencegah skrip jahat mencuri
data dari situs lain yang sedang kamu login).

**Analogi:** CORS itu seperti **daftar tamu di resepsionis gedung**. Secara
default, resepsionis (browser) menolak semua tamu dari luar (`chrome-extension://...`)
yang mau masuk ke gedung (`localhost:8000`). `CORSMiddleware` adalah instruksi
ke resepsionis: "tamu dari daftar ini boleh masuk".

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # untuk development; produksi sebaiknya spesifik
    ...
)
```

`allow_origins=["*"]` artinya "semua tamu boleh masuk" — oke untuk
development di laptop sendiri, tapi catatan keamanan di kode menyebutkan:
untuk produksi, sebaiknya dibatasi ke ID extension spesifik saja.

### Endpoint `/predict/batch` — Kenapa Tidak Satu-Satu Saja?

Satu halaman YouTube bisa punya 50–200 komentar terlihat sekaligus. Kalau
extension memanggil `/predict` satu per satu, itu 50–200 **perjalanan
bolak-balik jaringan** (round-trip) — masing-masing punya overhead (buka
koneksi, header HTTP, dll), meskipun semuanya ke `localhost`.

**Analogi:** ini seperti mengantar 50 paket satu-satu naik-turun tangga,
vs mengumpulkan semuanya dalam satu troli dan mengantar sekali jalan.
`/predict/batch` menerima **array teks** dan mengembalikan **array hasil**
dalam satu request — jauh lebih efisien.

### Output Babak 5

Server yang berjalan di `localhost:8000` dengan endpoint `/`, `/health`,
`/predict`, `/predict/batch` — siap menerima request dari extension.

---

## Babak 6 — Turun ke Lapangan: Chrome Extension

File: `extension/` (manifest.json, content.js, popup.html/js)

### Manifest V3 — "KTP" Extension

`manifest.json` adalah file yang memberi tahu Chrome: siapa nama extension
ini, versi berapa, izin apa yang dibutuhkan, dan file mana yang harus
dijalankan di halaman mana.

Izin yang diminta (`host_permissions`):
- `localhost:8000` — supaya boleh `fetch()` ke server kita
- `youtube.com`, `instagram.com` — supaya `content.js` boleh di-inject ke
  halaman ini

### Content Script — "Mata dan Tangan" di Halaman Orang Lain

`content.js` di-inject Chrome ke dalam halaman YouTube. Ia berjalan **di
dalam** halaman (bisa baca/ubah HTML), tapi **terisolasi** dari JavaScript
milik YouTube sendiri (tidak bisa akses variabel internal YouTube) — ini
batasan keamanan browser.

### Masalah: Komentar Dimuat Bertahap (Infinite Scroll)

YouTube tidak memuat semua komentar sekaligus — komentar baru muncul saat
kamu scroll. Kalau `content.js` hanya scan sekali saat halaman dibuka,
komentar yang muncul belakangan tidak akan pernah diperiksa.

**Solusi: `MutationObserver`** — API browser yang "mengawasi" perubahan pada
struktur halaman (DOM). Setiap kali ada elemen baru ditambahkan (misalnya
komentar baru), callback kita dipanggil otomatis.

**Analogi:** ini seperti CCTV yang otomatis memberi notifikasi setiap kali
ada barang baru masuk ke gudang, sehingga kamu tidak perlu mengecek gudang
setiap detik secara manual.

```javascript
const observer = new MutationObserver((mutations) => {
  clearTimeout(scanTimeout);
  scanTimeout = setTimeout(scanComments, 1000);
});
```

**Kenapa ada `clearTimeout` + `setTimeout` (debounce)?** Saat scroll,
DOM bisa berubah puluhan kali per detik (animasi loading, dll). Tanpa
debounce, `scanComments` akan terpanggil puluhan kali per detik — boros.
Debounce = "tunggu sampai tidak ada perubahan selama 1 detik, baru scan
sekali". **Analoginya:** seperti lift yang menunggu beberapa detik sebelum
pintunya menutup, memberi kesempatan orang lain yang masih berlarian masuk,
daripada langsung menutup tiap kali ada 1 orang masuk.

### `WeakSet` — Mencegah Kerja Dua Kali (Tanpa Bocor Memori)

```javascript
let processedComments = new WeakSet();
```

Setiap komentar yang sudah dikirim ke API ditandai di `processedComments`,
supaya tidak dikirim ulang saat `scanComments` jalan lagi.

**Kenapa `WeakSet`, bukan `Set` biasa?** Kalau YouTube menghapus elemen
komentar dari halaman (misal saat kamu pindah video), `Set` biasa akan
**terus menyimpan referensi** ke elemen yang sudah tidak ada itu — memori
tidak pernah dibebaskan, lama-lama menumpuk (**memory leak**). `WeakSet`
menyimpan referensi "lemah" — kalau elemen aslinya sudah dihapus dari
halaman, browser boleh membuang juga catatan di `WeakSet` ini secara
otomatis.

**Analogi:** `Set` biasa seperti mencatat nomor plat semua mobil yang pernah
masuk parkiran di buku permanen (buku makin tebal selamanya). `WeakSet`
seperti karcis parkir — begitu mobilnya keluar, karcisnya otomatis tidak
berlaku lagi dan bisa dibuang.

### Confidence Threshold 0.75 — Keputusan Trade-off, Bukan Hasil Hitungan

```javascript
const CONFIDENCE_THRESHOLD = 0.75;

if (result.is_spam && result.confidence >= CONFIDENCE_THRESHOLD) {
  hideSpamComment(batch[idx].element, result.confidence);
}
```

Kenapa 0.75, bukan 0.5 atau 0.9? Ini **keputusan desain** yang
merepresentasikan trade-off:

- Threshold **rendah** (misal 0.5) → lebih banyak spam tertangkap, tapi
  lebih banyak juga komentar normal yang salah disembunyikan (**false
  positive** naik)
- Threshold **tinggi** (misal 0.9) → nyaris tidak ada false positive, tapi
  banyak spam yang "agak yakin" (confidence 0.8) lolos tanpa disembunyikan
  (**false negative** naik)

0.75 adalah titik tengah yang dipilih sebagai starting point — **bisa dan
sebaiknya disesuaikan** berdasarkan masukan pengguna nyata.

### Kenapa Komentar Di-"redupkan" (opacity 15%), Bukan Dihapus dari Halaman?

```javascript
element.style.opacity = "0.15";
```

1. Kalau elemen **dihapus total** dari DOM, YouTube yang mengelola posisi
   scroll bisa "bingung" (tinggi halaman berubah mendadak, posisi scroll
   meloncat)
2. Memberi kesempatan ke pengguna untuk **mengecek ulang** — kalau itu
   ternyata false positive, klik badge untuk menampilkan lagi. Ini lebih
   aman daripada menghilangkan informasi secara permanen.

**Analogi:** seperti mem-blur foto yang dicurigai tidak pantas di media
sosial, dengan tombol "tampilkan tetap" — bukan menghapus fotonya secara
permanen.

### Output Babak 6

Extension yang berjalan otomatis di YouTube/Instagram, mengirim komentar
mentah ke server, dan memberi efek visual pada komentar yang terdeteksi spam
dengan confidence ≥ 75%.

---

## Babak 7 — Benang Merah: Training-Serving Consistency

Ini adalah **babak yang mengikat semua keputusan sebelumnya menjadi satu
prinsip arsitektur**. Kalau dosen penguji hanya boleh bertanya SATU hal
tentang desain sistem ini, kemungkinan besar ini yang ditanyakan.

### Masalahnya — "Training-Serving Skew"

Model dilatih dengan data yang sudah melewati `clean_text()`. Saat produksi
(extension aktif), model menerima komentar baru dari pengguna nyata. **Kalau
proses pembersihan teks yang diterapkan saat produksi berbeda — sekecil
apapun — dari saat training, model menerima input dalam "bahasa" yang
berbeda dari yang ia pelajari.**

**Analogi:** Bayangkan kamu melatih seekor anjing pelacak untuk mengenali bau
parfum tertentu dari sampel **botol parfum asli**. Lalu saat bertugas di
lapangan, kamu menyemprotkan parfum itu **dicampur sedikit alkohol** sebelum
disodorkan ke anjingnya. Baunya "mirip" tapi tidak identik — anjing yang
terlatih sangat baik sekalipun bisa kebingungan, karena yang ia hadapi di
lapangan tidak persis sama dengan yang ia pelajari.

Inilah **training-serving skew**. Ini salah satu penyebab paling umum model
"bagus di laboratorium, jelek di dunia nyata" — dan seringnya tidak
disadari karena tidak memunculkan error, hanya **penurunan akurasi diam-diam**.

### Solusi yang Diterapkan — "Satu Sumber Kebenaran"

Lihat kembali ke belakang:

- **Babak 2:** dataset training memakai `original_text` (teks mentah,
  belum dinormalisasi)
- **Babak 3:** `clean_text()` adalah **satu-satunya** definisi "cara
  membersihkan teks" di seluruh proyek
- **Babak 5:** server memanggil `clean_text()` yang **persis sama** ke teks
  yang diterima dari extension
- **Babak 6:** extension mengirim teks **mentah, tanpa modifikasi apapun**
  dari JavaScript

Semua keputusan ini, kalau dirangkai, membentuk satu jalur:

```
TRAINING:
original_text → clean_text() → TF-IDF → SVM belajar dari representasi ini

PRODUKSI:
teks mentah dari DOM → (dikirim apa adanya) → clean_text() → TF-IDF → SVM memprediksi dari representasi yang SAMA
```

**Kenapa tidak melakukan SEBAGIAN normalisasi di JavaScript** (misalnya
lowercase saja, sebelum dikirim)? Karena meskipun JavaScript dan Python
sama-sama mendukung Unicode, **implementasi regex dan normalisasi Unicode di
keduanya bisa berbeda secara halus** untuk karakter-karakter eksotis. Selisih
sekecil apapun = representasi TF-IDF yang berbeda = model menerima "bau yang
sudah tercampur alkohol" seperti analogi anjing pelacak di atas.

### Implikasi Praktis — Aturan yang Harus Selalu Diingat

> **Setiap kali `src/preprocessing.py` diubah, model HARUS dilatih ulang.**

Urutan yang benar selalu:
```
1. Update src/preprocessing.py
2. python src/prepare_dataset.py
3. python src/train.py
```

Kalau langkah 2-3 dilewati setelah mengubah `preprocessing.py`, maka saat
produksi, server menjalankan `clean_text()` versi BARU terhadap teks, tapi
model masih "berpikir" dengan kosakata dan pola dari `clean_text()` versi
LAMA. Inilah training-serving skew yang terjadi **karena perubahan kode kita
sendiri** — bukan karena lingkungan eksternal.

---

## Lampiran A — Tabel Keputusan Desain (Decision Log)

Tabel ini merangkum **semua keputusan "A vs B"** dari Babak 0–7 dalam satu
tempat, untuk referensi cepat saat sidang.

| # | Keputusan | Alternatif yang Dipertimbangkan | Kenapa Dipilih | Lokasi Kode |
|---|---|---|---|---|
| 1 | Machine Learning (SVM) | Filter kata kunci manual | Filter statis mudah dihindari (obfuscation) & rawan false positive pada kata yang kebetulan mengandung substring terlarang | `src/train.py` |
| 2 | Heuristic scoring untuk bootstrap data | Label manual ribuan komentar | Heuristik cukup untuk skrining awal; label manual tidak skalabel | `scraper/index.js` → `analyzeSpamScore()` |
| 3 | Two-pass filter (threshold + brand-regex rescue) | Threshold tunggal (≥80 saja) | Threshold tunggal hanya menghasilkan 137 sampel — terlalu sedikit; rescue menambah 962 sampel valid | `src/prepare_dataset.py` → `load_spam_data()` |
| 4 | `original_text` untuk dataset training | `normalized_text` (sudah di-NFKC oleh scraper) | Extension mengirim teks mentah dari DOM (= `original_text`); training harus pakai input dengan "bentuk" yang sama | `src/prepare_dataset.py`, dibahas di Babak 7 |
| 5 | ~~Non-spam sintetis dari template~~ **(dibalik di Versi 2)** | Scraping non-spam asli | Awalnya: tidak ada scraper untuk non-spam, sintetis jadi kompromi pragmatis. **Direvisi di Versi 2** (2026-06-16) — scraper diperluas mendukung mode `video non_spam`, data sintetis diganti data nyata sepenuhnya. Lihat [DATASET_LOG.md Versi 2](DATASET_LOG.md#versi-2--2026-06-16). | `src/prepare_dataset.py` → `load_non_spam_data()` |
| 6 | Preprocessing 7-layer di Python (server) | Sebagian preprocessing di JavaScript (extension) | JS dan Python menangani Unicode/regex secara halus berbeda → training-serving skew | `src/preprocessing.py`, Babak 7 |
| 7 | Demojize emoji (jadi token) | Hapus emoji | Emoji adalah sinyal kuat (🎰, 💰); menghapusnya membuang informasi | `src/preprocessing.py` Layer 4 |
| 8 | TF-IDF dengan `ngram_range=(1,2)` | Unigram saja | Bigram menangkap konteks (`"tidak spam"` vs `"spam"`) | `src/train.py` |
| 9 | SVM `kernel='linear'` | Kernel RBF/non-linear | Data TF-IDF sudah berdimensi sangat tinggi → linear sudah cukup, lebih cepat, tidak overfit | `src/train.py` |
| 10 | `class_weight='balanced'` | Tanpa pembobotan | Dataset tidak seimbang (1.6:1); tanpa ini model bias ke kelas mayoritas | `src/train.py` |
| 11 | `probability=True` (Platt Scaling) | Output biner saja | Extension butuh skor confidence untuk threshold 75% | `src/train.py` |
| 12 | `Pipeline` (TF-IDF + SVM jadi satu) | Fit TF-IDF terpisah sebelum split | Mencegah data leakage (TF-IDF "mengintip" data test) | `src/train.py` |
| 13 | FastAPI server lokal sebagai jembatan | Konversi model ke ONNX/TF.js (jalan di browser) | ONNX/TF.js jauh lebih kompleks, di luar scope skripsi; server lokal pragmatis dan mudah dijelaskan | `src/server.py` |
| 14 | `/predict/batch` endpoint | Hanya `/predict` single, dipanggil berkali-kali | Mengurangi jumlah round-trip jaringan untuk 50-200 komentar per halaman | `src/server.py`, `extension/content.js` |
| 15 | `MutationObserver` + debounce 1 detik | Polling interval tetap (misal cek tiap 1 detik) | Lebih efisien — hanya bereaksi saat DOM benar-benar berubah, bukan terus-menerus | `extension/content.js` |
| 16 | `WeakSet` untuk dedup komentar | `Set` biasa | Mencegah memory leak saat elemen DOM dihapus YouTube | `extension/content.js` |
| 17 | Sembunyikan komentar (opacity 15% + badge) | Hapus elemen dari DOM | Menghindari masalah scroll-position; reversibel jika false positive | `extension/content.js` |
| 18 | Confidence threshold 0.75 | 0.5 atau 0.9 | Titik tengah trade-off precision vs recall; recall lebih diprioritaskan untuk kasus spam | `extension/content.js` |

---

## Lampiran B — Peta Mental Keseluruhan Sistem

Cara mengingat keseluruhan alur secara singkat — bayangkan ini sebagai **garis
produksi (assembly line)**:

```
┌──────────────┐   ┌──────────────────┐   ┌─────────────────┐   ┌──────────────┐
│  1. SCRAPER   │──▶│ 2. DATASET PREP   │──▶│ 3. PREPROCESSING │──▶│ 4. TRAINING  │
│ (Node.js)     │   │ (two-pass filter) │   │ (clean_text)     │   │ (TF-IDF+SVM) │
│ heuristic     │   │ + non-spam        │   │ 7 layer          │   │              │
│ scoring       │   │ sintetis          │   │                  │   │              │
└──────────────┘   └──────────────────┘   └─────────────────┘   └──────┬───────┘
                                                                          │
                                                                  model.joblib
                                                                          │
┌──────────────┐   ┌──────────────────┐   ┌─────────────────┐         │
│ 7. EXTENSION  │◀──│ 6. RESPONSE JSON  │◀──│ 5. FASTAPI       │◀────────┘
│ tampilkan/    │   │ {label,           │   │ SERVER           │
│ sembunyikan   │   │  confidence}      │   │ clean_text() +   │
│ komentar      │   │                   │   │ model.predict()  │
└───────┬───────┘   └──────────────────┘   └─────────────────┘
        │                                            ▲
        │            kirim teks MENTAH               │
        └────────────────────────────────────────────┘
```

**Satu kalimat untuk mengingat semuanya:**
> "Kita ajarkan komputer mengenali pola spam dari ribuan contoh nyata
> (1–2), kita pastikan komputer 'membaca' setiap komentar dengan cara yang
> SAMA PERSIS baik saat belajar maupun saat bertugas (3, 7), lalu kita
> sediakan jembatan (5) agar 'otak' Python ini bisa dipakai oleh 'tangan dan
> mata' di browser (6)."

---

*Dokumen ini melengkapi [README.md](README.md) (cara menjalankan) dan
[PENJELASAN_TEKNIS.md](PENJELASAN_TEKNIS.md) (referensi detail + FAQ sidang).
Kalau ada bagian yang masih membingungkan, tanyakan langsung — sebutkan babak
mana yang belum jelas.*
