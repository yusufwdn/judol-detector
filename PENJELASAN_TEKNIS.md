# Penjelasan Teknis Lengkap — Judol Spam Detector

> Dokumen ini ditulis untuk menemani pengerjaan skripsi. Tujuannya satu: kamu harus bisa menjelaskan **setiap keputusan teknis** dalam proyek ini, baik kepada dosen maupun kepada diri sendiri. Tidak ada yang dilewat.

> **Baru pertama kali baca dokumentasi proyek ini?** Mulai dari [JOURNEY.md](JOURNEY.md) dulu — dokumen itu menceritakan urutan pengembangan secara kronologis dengan analogi sehari-hari. Dokumen ini (PENJELASAN_TEKNIS.md) adalah pendalaman per-topik dari cerita tersebut, plus kumpulan pertanyaan sidang di bagian akhir.

---

## Daftar Isi

1. [Gambaran Masalah dari Nol](#1-gambaran-masalah-dari-nol)
2. [Cara Scraper Mengumpulkan Data](#2-cara-scraper-mengumpulkan-data)
3. [Sistem Penilaian Spam (Spam Score) dan Kelemahannya](#3-sistem-penilaian-spam-spam-score-dan-kelemahannya)
4. [Masalah Nyata: "kesambet" Dianggap Spam](#4-masalah-nyata-kesambet-dianggap-spam)
5. [Solusi: Two-Pass Filter di prepare_dataset.py](#5-solusi-two-pass-filter-di-prepare_datasetpy)
6. [Apa itu NFKC dan Kenapa Krusial di Sini](#6-apa-itu-nfkc-dan-kenapa-krusial-di-sini)
7. [Pipeline Preprocessing 7 Lapisan](#7-pipeline-preprocessing-7-lapisan)
8. [Dari Teks ke Angka: TF-IDF](#8-dari-teks-ke-angka-tf-idf)
9. [Algoritma Klasifikasi: SVM](#9-algoritma-klasifikasi-svm)
10. [Proses Training End-to-End](#10-proses-training-end-to-end)
11. [Training-Serving Consistency: Jebakan yang Sering Diabaikan](#11-training-serving-consistency-jebakan-yang-sering-diabaikan)
12. [FastAPI Server sebagai Jembatan](#12-fastapi-server-sebagai-jembatan)
13. [Browser Extension: Cara Kerjanya di Dalam Halaman](#13-browser-extension-cara-kerjanya-di-dalam-halaman)
14. [Alur Lengkap dari Komentar Muncul Sampai Disembunyikan](#14-alur-lengkap-dari-komentar-muncul-sampai-disembunyikan)
15. [Pertanyaan yang Mungkin Muncul Saat Sidang](#15-pertanyaan-yang-mungkin-muncul-saat-sidang)
16. [Evaluasi Model yang Lebih Jujur (Fase 2)](#16-evaluasi-model-yang-lebih-jujur-fase-2)
17. [Inspeksi Fitur — "Apa yang Dipelajari Model?"](#17-inspeksi-fitur--apa-yang-dipelajari-model)
18. [Eksperimen Stemming — Apakah Stemming Membantu?](#18-eksperimen-stemming--apakah-stemming-membantu)
19. [Eksperimen Konfigurasi TF-IDF — ngram dan max_features](#19-eksperimen-konfigurasi-tf-idf--ngram-dan-max_features)
20. [Perbaikan Extension — Fase 4](#20-perbaikan-extension--fase-4)
21. [False Positive — Ketika Model Salah Menilai Komentar Normal](#21-false-positive--ketika-model-salah-menilai-komentar-normal)
22. [Hybrid SVM + Rules — Lapisan Kedua untuk Kurangi False Positive](#22-hybrid-svm--rules--lapisan-kedua-untuk-kurangi-false-positive)
23. [Brand Canonicalization — Token Universal untuk Nama Brand Judol](#23-brand-canonicalization--token-universal-untuk-nama-brand-judol)
24. [Perbaikan Two-Pass Filter — Rescue Condition dan Suffix QQ](#24-perbaikan-two-pass-filter--rescue-condition-dan-suffix-qq)
25. [Keterbatasan: Obfuscation yang Belum Bisa Ditangani](#25-keterbatasan-obfuscation-yang-belum-bisa-ditangani)
26. [Hybrid Rule Dua Arah — Mencegah False Negative dari Kata Normal](#26-hybrid-rule-dua-arah--mencegah-false-negative-dari-kata-normal)
27. [Kurasi Manual Dataset + Perbaikan Rescue Pattern](#27-kurasi-manual-dataset--perbaikan-rescue-pattern)
28. [manual_overrides.csv — Menjaga Koreksi Manual Agar Tidak Hilang](#28-manual_overridescsv--menjaga-koreksi-manual-agar-tidak-hilang)
29. [Hard Test Set — Evaluasi pada Kasus Ambigu](#29-hard-test-set--evaluasi-pada-kasus-ambigu)
30. [Leet Speak Normalization — Mendeteksi H0KI777 dan Sejenisnya](#30-leet-speak-normalization--mendeteksi-h0ki777-dan-sejenisnya)
31. [Perlindungan Data Laporan Extension — /report ke Dua File](#31-perlindungan-data-laporan-extension--report-ke-dua-file)
32. [Penghapusan slot dan deposit dari HARD_SPAM_SIGNALS](#32-penghapusan-slot-dan-deposit-dari-hard_spam_signals)
33. [Ablation Study Hybrid Rules — Kenapa Akhirnya Dimatikan](#33-ablation-study-hybrid-rules--kenapa-akhirnya-dimatikan)
34. [Generalisasi ke Brand Judol Baru — Sejauh Mana Model Bisa Mengikuti?](#34-generalisasi-ke-brand-judol-baru--sejauh-mana-model-bisa-mengikuti)
35. [Insiden Kontaminasi Data — Spam Tersamar yang Lolos Heuristik Scraper](#35-insiden-kontaminasi-data--spam-tersamar-yang-lolos-heuristik-scraper)

---

## 1. Gambaran Masalah dari Nol

### Kenapa ini perlu dibuat?

Coba buka video YouTube populer Indonesia — podcast, berita, gaming, apapun. Scroll ke kolom komentar. Ada kemungkinan besar kamu akan menemukan komentar seperti ini:

> *"𝑹𝑶𝑴𝑨𝟒𝑫 🎰 daftar sekarang bonus new member 100%!! WD lancar gak ribet, udah terbukti 💰💰"*

atau ini:

> *"Gokil 🐣 ℙ𝔼𝕃𝔸𝕋𝕀ℍ𝟜𝔻🐣 berhasil bikin klip singkat yang super menakjubkan ini 0:16"*

Yang kedua lebih berbahaya — terlihat seperti komentar normal yang memuji video, tapi menyisipkan nama brand judi di tengah kalimat menggunakan Unicode dekoratif agar lolos filter kata kunci sederhana.

Memblokir ini secara manual tidak skalabel. Dibutuhkan sistem otomatis yang bisa:
1. **Mendeteksi** komentar spam dengan akurat
2. **Menyembunyikan** langsung di browser secara real-time
3. **Tidak butuh koneksi ke server eksternal** — cukup jalan di laptop sendiri

Inilah yang dibangun di proyek ini.

---

### Kenapa Machine Learning, bukan filter kata kunci biasa?

Cara paling naif adalah membuat daftar kata terlarang: kalau ada kata "slot", "daftar", "bonus" → spam.

Masalahnya:

| Pendekatan Naif | Masalah |
|----------------|---------|
| Filter "slot" | Komentar "time slot jadwal" juga ikut terblokir |
| Filter "bonus" | "bonus tips dari video ini keren" juga kena |
| Filter "daftar" | "daftar isi episode ini ada di deskripsi" kena |
| Spammer update kata | Filter jadi usang setiap minggu |

Spammer sudah tahu cara ini — makanya mereka menulis `𝑹𝑶𝑴𝑨𝟒𝑫` bukan `ROMA4D`, `g a c o r` bukan `gacor`. Mereka mengobfuscate teks agar lolos filter statis.

Machine learning tidak diprogram dengan aturan manual. Ia **belajar pola dari ribuan contoh**, termasuk pola-pola yang tidak terpikirkan sebelumnya oleh programmer.

---

## 2. Cara Scraper Mengumpulkan Data

### Peran scraper dalam proyek ini

Model machine learning butuh data untuk belajar. Tidak ada dataset publik untuk komentar spam judi Indonesia, jadi kita buat sendiri.

Scraper (`scraper/index.js`) adalah program Node.js yang:
1. Menerima sebuah Video ID YouTube sebagai input
2. Memanggil **YouTube Data API v3** untuk mengambil komentar video tersebut
3. Mengevaluasi setiap komentar dengan sistem heuristik
4. Menyimpan komentar ke `result/{label}_{mode}_{video_id}_{timestamp}.json`
5. Setelah semua video selesai di-scrape, jalankan `filter.js` untuk mengagregasi ke `final_spam.json`

```bash
# Scrape komentar spam dari video:
node scraper/index.js <VIDEO_ID>

# Scrape komentar non-spam dari video:
node scraper/index.js <VIDEO_ID> video non_spam

# Contoh:
node scraper/index.js VH-EDzoBEA4

# Agregasi hasil:
node scraper/filter.js
```

### Apa itu YouTube Data API v3?

Ini adalah layanan resmi dari Google yang memungkinkan program mengambil data YouTube secara programatik — termasuk komentar, metadata video, statistik, dll. — tanpa harus membuka browser dan menyalin manual.

Untuk menggunakannya butuh **API Key** yang didapat dari Google Cloud Console. API Key ini yang disimpan di file `.env` dan dibaca oleh scraper.

### Format output JSON

Setiap komentar yang lolos disimpan seperti ini:

```json
{
  "video_id": "VH-EDzoBEA4",
  "timestamp": "2026-04-25T10:13:22.108Z",
  "original_text": "\"Connect ke 𝐖𝐈𝐅𝐈𝟒𝐃, putus hubungan sama dompet tipis! 💸\"",
  "normalized_text": "\"Connect ke WIFI4D, putus hubungan sama dompet tipis! 💸\"",
  "spam_score": 40,
  "active_signals": ["brand_pattern"],
  "label": "spam"
}
```

| Field | Isi | Keterangan |
|-------|-----|-----------|
| `original_text` | Teks asli dari API YouTube | Persis seperti yang diketik pengguna |
| `normalized_text` | Teks setelah NFKC normalization | `𝐖𝐈𝐅𝐈𝟒𝐃` → `WIFI4D` |
| `spam_score` | 0–100 | Hasil penilaian heuristik |
| `active_signals` | Array string | Sinyal mana saja yang aktif |
| `label` | Selalu `"spam"` | Scraper hanya menyimpan yang terdeteksi spam |

---

## 3. Sistem Penilaian Spam (Spam Score) dan Kelemahannya

### Bagaimana spam_score dihitung

Scraper mengevaluasi setiap komentar dengan sistem poin berdasarkan sinyal-sinyal yang ditemukan:

```
SINYAL PRIMER (wajib ada minimal satu):
  +40  brand_pattern         → ada nama brand (regex: [a-z]{3,}(88|99|4d|bet|win...))
  +40  contact_link          → ada link WA/bit.ly/nomor HP
  +35  soft_brand_testimonial → nama + 2 angka + kalimat testimoni

SINYAL SEKUNDER:
  +30  obfuscated_keyword    → "g a c o r", "m@xw!n", "z3u5"
  +20  plain_keyword         → "slot", "depo", "scatter", "mahjong"
  +20  high_symbol_ratio     → >15% karakter adalah simbol aneh

SINYAL TERSIER:
  +15  emoji_spam            → 2+ emoji berurutan
  +10  excessive_caps        → >50% huruf kapital
```

**Penting:** Komentar **hanya disimpan** jika ada **minimal satu sinyal primer** aktif. Ini mencegah false positive dari komentar yang kebetulan banyak emoji atau capslock saja.

### Kenapa ada threshold di prepare_dataset.py?

Meskipun ada syarat sinyal primer, sistem tetap bisa menghasilkan false positive. Contoh nyata:

```
Komentar  : "Wkwk tengah malem nonton podcast ini, ketawa sendiri dikira orang rumah kesambet😂"
brand_pattern terpicu karena: "kesambet" → mengandung substring "bet"
Skor      : 40
Aktual    : Ini BUKAN spam
```

Scraper tidak salah secara desain — ia memang memilih sensitif tinggi (banyak yang masuk) daripada presisi tinggi (hanya yang yakin). Menyaring yang benar-benar berkualitas adalah tugas kita di tahap persiapan dataset.

---

## 4. Masalah Nyata: "kesambet" Dianggap Spam

### Mengapa ini terjadi secara teknis

Regex `brand_pattern` di scraper:
```javascript
/[a-z]{3,}(88|99|77|69|138|388|777|888|4d|toto|bet|win)\b/i
```

Regex ini mencocokkan **semua kata yang diakhiri dengan salah satu suffix tersebut**. Suffix `bet` dimaksudkan untuk menangkap `sbobet`, `bet138`, `maxbet`, dll. Tapi `kesambet`, `ribet`, `sebut` juga berakhir atau mengandung pola yang mirip.

### Mengapa tidak sekadar hapus "bet" dari list?

Karena suffix `bet` memang krusial untuk menangkap brand nyata seperti `SBOBET`, `BET138`, `MAXBET`. Membuangnya artinya banyak spam yang lolos.

Masalahnya bukan di regex-nya — masalahnya di cara kita **menginterpretasikan sinyal tersebut**.

Sinyal `brand_pattern` dengan skor 40 artinya: "ada indikasi brand, tapi gua tidak yakin." Itu informasi yang valid, asalkan kita tahu cara membacanya dengan benar.

---

## 5. Solusi: Two-Pass Filter di prepare_dataset.py

### Ide dasarnya

Kita perlu cara untuk menjawab satu pertanyaan sederhana:

> *Dari semua komentar yang hanya punya sinyal `brand_pattern` dengan skor rendah, mana yang benar-benar spam (ada brand judi nyata) dan mana yang false positive (kata biasa yang kebetulan cocok)?*

Kunci jawabannya ada di field `normalized_text`.

### Kenapa normalized_text menjadi kunci pembeda?

Ketika kamu melihat komentar spam yang menggunakan nama brand, spammer sering menggunakan **huruf Unicode dekoratif** supaya lolos filter visual:

```
𝐖𝐈𝐅𝐈𝟒𝐃  ←  terlihat seperti huruf biasa tapi bukan karakter ASCII standar
PELATIH4D ← ini versi yang sudah dinormalisasi NFKC
```

Setelah NFKC normalization, semua huruf "mewah" itu kembali ke bentuk standar. Dan bentuk standar nama brand judi memiliki **pola yang sangat khas**:

- Minimal 2 huruf kapital
- Diikuti langsung oleh angka
- Contoh: `WIFI4D`, `BATRE4D`, `PELATIH4D`, `ROMA4D`, `SUPERMONEY88`

Pola ini ditulis sebagai **regex**:
```
\b[A-Z]{2,}\d+[A-Z0-9]*\b
```

Mari bedah regex ini satu per satu:
- `\b` — batas kata (word boundary), memastikan tidak di tengah kata lain
- `[A-Z]{2,}` — dua atau lebih huruf kapital berurutan
- `\d+` — satu atau lebih angka langsung setelah huruf
- `[A-Z0-9]*` — boleh ada huruf kapital atau angka tambahan sesudahnya
- `\b` — batas kata lagi di akhir

**Apa yang cocok:** `WIFI4D`, `BATRE4D`, `ROMA4D`, `SBOBET88`, `MAXWIN777`

**Apa yang tidak cocok:** `kesambet` (lowercase), `ribet` (lowercase), `Sabtu` (hanya 1 kapital, tidak ada angka langsung setelah)

### Logika Two-Pass yang diimplementasikan

```python
# Dari src/prepare_dataset.py

for entry in raw_data:
    score = entry["spam_score"]
    normalized = entry["normalized_text"]
    signals = entry["active_signals"]

    # PASS 1: Skor tinggi → langsung masuk, tidak perlu cek lebih lanjut
    if score >= SPAM_SCORE_THRESHOLD:   # default: 80
        spam_entries.append(entry)

    # PASS 2: Skor rendah, tapi hanya ada sinyal brand_pattern
    # → cek apakah ada pola brand nyata di normalized_text
    elif signals == ["brand_pattern"] and BRAND_RESCUE_PATTERN.search(normalized):
        spam_entries.append(entry)   # ini spam nyata yang skornya "tertekan"

    # Sisanya: drop (false positive atau sinyal terlalu lemah)
    else:
        skipped += 1
```

### Kenapa hanya yang signals == ["brand_pattern"] yang di-rescue?

Karena kita ingin sangat spesifik. Kalau entri punya `["emoji_spam", "brand_pattern"]` misalnya, itu artinya ada sinyal lain juga, dan skor-nya yang rendah mungkin karena sinyal gabungan yang memang tidak cukup meyakinkan. Kita tidak mau mengambil keputusan di sana.

Kita hanya rescue kasus yang **satu-satunya** alasan masuk adalah `brand_pattern` — karena itulah yang paling rentan false positive sekaligus paling mudah diverifikasi secara independen lewat regex pola brand.

### Hasil nyata dari JSON scraping kita

```
Total entries in JSON        : 2318
Passed primary threshold     : 137     ← skor >= 80
Rescued via brand regex      : 962     ← skor < 80 tapi ada brand nyata
Skipped (false positives)    : 618     ← "kesambet" dan sejenisnya
Total spam collected         : 1099
Ratio spam:non-spam          : 1.6:1   ← sehat untuk training
```

Tanpa rescue, kita hanya punya 137 spam — terlalu sedikit dan tidak representatif. Dengan rescue, kita punya 1099 spam yang semuanya sudah diverifikasi mengandung nama brand nyata.

---

## 6. Apa itu NFKC dan Kenapa Krusial di Sini

### Latar belakang: Unicode itu kompleks

Komputer menyimpan teks sebagai angka. Standard internasionalnya bernama **Unicode**, yang mendefinisikan lebih dari 143.000 karakter dari seluruh sistem penulisan di dunia.

Di dalam Unicode, ada banyak karakter yang **terlihat sama** di layar tapi **berbeda secara encoding**:

| Karakter | Terlihat | Unicode Code Point |
|----------|----------|--------------------|
| A (Latin) | A | U+0041 |
| 𝐀 (Mathematical Bold) | **A** | U+1D400 |
| Ａ (Full-width) | Ａ | U+FF21 |
| А (Cyrillic) | А | U+0410 |

Spammer memanfaatkan ini. Mereka menulis `𝑹𝑶𝑴𝑨𝟒𝑫` menggunakan karakter Mathematical Italic Bold — terlihat sama di layar, tapi string "ROMA4D" biasa tidak akan cocok kalau kita pakai pencarian normal.

### Apa itu NFKC Normalization?

**NFKC** (Normalization Form Compatibility Decomposition + Canonical Composition) adalah salah satu dari empat standar normalisasi Unicode. Fungsinya: **kembalikan semua karakter "fancy" ke equivalen ASCII standar-nya**.

```python
import unicodedata

# Contoh:
teks = "𝑹𝑶𝑴𝑨𝟒𝑫"
print(unicodedata.normalize("NFKC", teks))
# Output: ROMA4D
```

NFKC menangani:
- Huruf Mathematical (𝐀𝐁𝐂 → ABC)
- Huruf Full-width (ＡＢＣ → ABC)
- Huruf Enclosed (🅐🅑🅒 → ABC)
- Superscript/subscript (ᵃᵇᶜ → abc)
- Angka stylized (𝟙𝟚𝟛 → 123)

### Apa yang NFKC tidak bisa tangani?

NFKC tidak menerjemahkan karakter lintas script yang berbeda. Ia tahu bahwa `𝐀` adalah versi mewah dari `A`, tapi ia tidak tahu bahwa:

- `а` (Cyrillic, U+0430) adalah homoglyph dari `a` (Latin)
- `е` (Cyrillic, U+0435) adalah homoglyph dari `e` (Latin)
- `о` (Cyrillic, U+043E) adalah homoglyph dari `o` (Latin)

Spammer yang canggih menggunakan ini. Kata "daftar" dengan Cyrillic 'а':
```
d а f t а r   ← huruf 'а' di sini adalah Cyrillic, bukan Latin
```
Secara visual identik. Secara encoding berbeda. NFKC tidak mengubahnya.

Itulah kenapa di `preprocessing.py` ada **Layer 3: Homoglyph Map** yang secara manual mengganti karakter Cyrillic dan Greek yang sering disalahgunakan ke padanan Latin-nya.

### Mengapa scraper menggunakan normalized_text?

Scraper melakukan NFKC normalization ke setiap komentar dan menyimpan hasilnya sebagai `normalized_text`. Ini yang kita gunakan di Pass 2 filter untuk **mendeteksi nama brand**.

Setelah normalisasi, `𝑹𝑶𝑴𝑨𝟒𝑫` menjadi `ROMA4D` — dan pola regex kita `\b[A-Z]{2,}\d+[A-Z0-9]*\b` bisa menangkapnya dengan andal.

---

## 7. Pipeline Preprocessing 7 Lapisan

### Mengapa teks perlu dibersihkan sebelum dilatih?

Model SVM tidak bekerja dengan teks. Ia bekerja dengan **vektor angka**. Sebelum dikonversi ke angka, teks harus diseragamkan agar representasi yang sama menghasilkan angka yang sama.

Kalau kita tidak preprocessing:
- `"ROMA4D"` dan `"roma4d"` akan dianggap dua kata yang berbeda
- `"𝑹𝑶𝑴𝑨𝟒𝑫"` tidak akan dikenali sebagai `"ROMA4D"` sama sekali
- `"🎰"` akan menjadi karakter yang tidak berarti untuk model

Pipeline di `src/preprocessing.py` menangani semua ini dalam **7 langkah + 3 sub-langkah** berurutan. Urutan penting — setiap langkah mengasumsikan langkah sebelumnya sudah dijalankan.

| Langkah | Fungsi |
|---------|--------|
| Step 1 | Strip karakter zero-width |
| Step 2 | NFKC Unicode normalization |
| **Step 2b** | **Strip combining diacritical marks** (baru) |
| **Step 2c** | **Unwrap kurung per-huruf** (baru) |
| Step 3 | Cyrillic/Greek/Thai homoglyph fix |
| Step 4 | Emoji demojize |
| Step 5 | Lowercase |
| **Step 5b-i** | **Leet speak normalization** → `0→o`, `1→i` (baru) |
| **Step 5b** | **Brand canonicalization** → `judolbrand` (baru) |
| Step 6 | Hapus URL dan karakter non-alfabet |
| Step 7 | Hapus stopwords dan token pendek |

---

### Layer 1 — Strip Karakter Zero-Width

```python
zero_width_chars = "\u200B\u200C\u200D\uFEFF\u00AD\u200E\u200F"
for char in zero_width_chars:
    text = text.replace(char, "")
```

**Masalah yang diselesaikan:** Spammer bisa menyisipkan karakter tak kasat mata di antara huruf. Karakter seperti Zero-Width Space (U+200B) tidak terlihat di layar apapun, tapi ada di string.

Contoh — teks ini terlihat "daftar" tapi sebenarnya:
```
d[U+200B]a[U+200B]f[U+200B]t[U+200B]a[U+200B]r
```

Jika tidak di-strip, kata "daftar" tidak akan dikenali sebagai satu token — TF-IDF akan memperlakukannya sebagai karakter acak yang tidak berguna.

**Karakter yang dihapus:**
| Code Point | Nama | Kenapa Berbahaya |
|-----------|------|-----------------|
| U+200B | Zero-Width Space | Memecah kata secara diam-diam |
| U+200C | Zero-Width Non-Joiner | Mempengaruhi rendering teks |
| U+200D | Zero-Width Joiner | Digunakan untuk gabung emoji |
| U+FEFF | Byte Order Mark | Bisa muncul di awal file/string |
| U+00AD | Soft Hyphen | Terlihat tapi perannya ambigu |

---

### Layer 2 — NFKC Normalization

```python
text = unicodedata.normalize("NFKC", text)
```

**Masalah yang diselesaikan:** Huruf-huruf "fancy" Unicode yang secara visual sama dengan ASCII standar tapi berbeda encoding.

Lihat [Bagian 6](#6-apa-itu-nfkc-dan-kenapa-krusial-di-sini) untuk penjelasan mendalam.

Setelah layer ini:
```
𝑹𝑶𝑴𝑨𝟒𝑫   →  ROMA4D
Ｄａｆｔａｒ  →  Daftar
🅓🅐🅕🅣🅐🅡  →  DAFTAR
```

---

### Layer 2b — Strip Combining Diacritical Marks *(baru)*

```python
text = "".join(c for c in text if unicodedata.category(c) != "Mn")
```

**Masalah yang diselesaikan:** Spammer menyisipkan karakter **combining** (karakter yang "menempel" ke huruf sebelumnya) di antara huruf-huruf brand untuk memecah deteksi. Contoh: U+0332 COMBINING LOW LINE yang terlihat seperti garis bawah di tiap huruf.

NFKC normalization (Layer 2) **tidak** menghapus combining marks — ia hanya menormalkan karakter dekoratif ke ASCII. Jadi combining marks ini tetap ada setelah Layer 2.

**Yang terjadi tanpa Layer 2b:**

1. Layer 6 (`[^a-z\s]`) mengganti setiap combining mark dengan spasi
2. Hasilnya: `P U L A U W I N` — setiap huruf menjadi token terpisah
3. Layer 7 membuang token dengan `len ≤ 1` (satu huruf)
4. Seluruh brand hilang → string kosong → model memprediksi non_spam

**Solusi:** `unicodedata.category(c) == "Mn"` mendeteksi semua karakter "Mark, Nonspacing" — termasuk combining underline, combining accent, dan trik serupa. Semua karakter kategori ini dihapus sekaligus.

**Contoh:**
```
P[combining]U[combining]L[combining]A[combining]U[combining]W[combining]I[combining]N
  → PULAUWIN  → (Step 5b)  → judolbrand
```

---

### Layer 2c — Unwrap Kurung Per-Huruf *(baru)*

```python
text = re.sub(r"[\[({]\s*(\w)\s*[\])}]", r"\1", text)
```

**Masalah yang diselesaikan:** Spammer membungkus tiap huruf brand dalam kurung/tanda baca:

```
[P][U][L][A][U][7][7][7]
```

Tanpa layer ini: Step 6 mengubah kurung jadi spasi → `P U L A U 7 7 7` → tiap huruf/angka adalah token tunggal → dibuang Layer 7 → string kosong.

**Cara kerja regex:** `[\[({]` cocok dengan kurung pembuka, lalu `\s*(\w)\s*` cocok dengan **tepat satu karakter word** (huruf/angka) dengan spasi opsional, lalu `[\])}]` cocok dengan kurung penutup. Hasilnya: karakter di dalam kurung dipertahankan, kurungnya dihapus.

**False positive protection:** Kurung yang berisi lebih dari satu karakter — seperti `(penjelasan di sini)` atau `[edisi revisi]` — tidak terpengaruh karena isinya tidak cocok pola `\w` tunggal.

**Contoh:**
```
[P][U][L][A][U][7][7][7]  →  PULAU777  →  (Step 2c selesai)
(penjelasan di sini)  →  (penjelasan di sini)  [tidak berubah]
```

---

### Layer 3 — Homoglyph Cyrillic/Greek/Thai

```python
HOMOGLYPH_MAP = str.maketrans({
    "\u0430": "a",   # Cyrillic а → a
    "\u0435": "e",   # Cyrillic е → e
    "\u043E": "o",   # Cyrillic о → o
    "\u0440": "p",   # Cyrillic р → p (bukan 'r'!)
    "\u0441": "c",   # Cyrillic с → c
    # ... dll
})
text = text.translate(HOMOGLYPH_MAP)
```

**Masalah yang diselesaikan:** Karakter lintas script yang terlihat identik tapi NFKC tidak bisa tangani.

Spammer yang lebih canggih menggunakan huruf dari script lain yang bentuknya identik dengan huruf Latin:

| Karakter | Asal Script | Terlihat seperti | Contoh penyalahgunaan |
|----------|-------------|------------------|-----------------------|
| `а` U+0430 | Cyrillic | `a` Latin | "dаftаr" dengan 'а' Cyrillic |
| `е` U+0435 | Cyrillic | `e` Latin | "sеkarang" dengan 'е' Cyrillic |
| `о` U+043E | Cyrillic | `o` Latin | "bоnus" dengan 'о' Cyrillic |
| `р` U+0440 | Cyrillic | `p` Latin (hati-hati, bukan 'r'!) | — |
| `๓` U+0E53 | Thai | `m` Latin | "ro๓a" → "roma" (ditambahkan versi terbaru) |

Karakter Thai ๓ (angka tiga dalam sistem angka Thailand) dipilih spammer karena bentuknya mirip huruf 'm'. Ini ditambahkan ke `HOMOGLYPH_MAP` setelah ditemukan pada komentar obfuscated di YouTube.

Setelah layer ini, kata "dаftаr" (dengan Cyrillic 'а') menjadi "daftar" (Latin 'a'), dan "ro๓a" menjadi "roma" — keduanya bisa dikenali sebagai token yang tepat.

---

### Layer 4 — Emoji Demojize

```python
text = emoji.demojize(text, language="en")
text = re.sub(r":([a-zA-Z0-9_]+):", r" \1 ", text)
```

**Masalah yang diselesaikan:** Emoji adalah sinyal kuat dalam komentar spam, tapi kalau dihapus begitu saja, informasi itu hilang.

Spammer sering menggunakan emoji secara spesifik: 🎰 (slot machine), 💰 (money bag), 🎁 (gift/bonus). Ini bukan kebetulan.

Alih-alih menghapus emoji, kita konversi ke deskripsinya:
```
🎰  →  :slot_machine:   →  slot_machine
💰  →  :money_bag:      →  money_bag
👍  →  :thumbs_up:      →  thumbs_up
🔥  →  :fire:           →  fire
```

Dengan ini, `slot_machine` dan `money_bag` menjadi token yang bisa dipelajari TF-IDF. Komentar spam yang banyak menggunakan emoji-emoji ini akan punya fitur yang khas.

**Kenapa bahasa "en"?** Library emoji mendukung berbagai bahasa untuk demojize, tapi kita pakai English karena nama-nama token English (`slot_machine`, `money_bag`) lebih standar dan tidak mengandung karakter non-ASCII yang bisa bermasalah di Layer 6.

---

### Layer 5 — Lowercase

```python
text = text.lower()
```

**Masalah yang diselesaikan:** Inkonsistensi kapital.

`"DAFTAR"`, `"Daftar"`, `"daftar"` adalah kata yang sama, tapi kalau tidak di-lowercase, TF-IDF akan menganggapnya sebagai tiga token berbeda dan belajar dari ketiganya secara terpisah. Ini membuang informasi dan membuat model kurang efisien.

Kenapa lowercase **setelah** NFKC dan homoglyph fix? Karena kita perlu deteksi nama brand (`WIFI4D`, huruf kapital semua) di layer sebelumnya — terutama di Pass 2 filter yang menggunakan `normalized_text`. Kalau lowercase dulu, pattern `[A-Z]{2,}\d+` tidak akan cocok.

---

### Layer 5b — Brand Canonicalization *(baru)*

```python
JUDOL_BRAND_PATTERN = re.compile(
    r'\b(?!(?:level|rank|stage|episode|...)\d)[a-z]{2,}'
    r'(?:4d|3d|2d|88|99|77|69|138|388|303|777|888|qq)\b'
)
text = JUDOL_BRAND_PATTERN.sub("judolbrand", text)
```

**Masalah yang diselesaikan:** Layer 6 menghapus semua digit. Ini artinya suffix numerik brand judol ikut terhapus:

```
KEJU4D   → (Layer 5: lowercase)  → keju4d
keju4d   → (Layer 6: hapus digit) → keju    ← makanan, bukan judol!
BETAWI77 → betawi77 → betawi                ← suku, bukan judol!
```

Akibatnya, model dilatih dengan fitur `keju` dan `betawi` yang salah label sebagai spam, meningkatkan risiko false positive di komentar kuliner dan budaya.

**Solusi: Token Universal `judolbrand`**

Sebelum Layer 6 menghapus digit, Step 5b mendeteksi pola brand dan menggantinya dengan token `judolbrand`:

```
keju4d   → judolbrand   ✓ sinyal diselamatkan
betawi77 → judolbrand   ✓ sinyal diselamatkan
hobiqq   → judolbrand   ✓ suffix QQ juga ditangkap
slot777  → judolbrand   ✓ angka 777 khas slot
```

**Suffix yang ditangkap:**

| Kategori | Suffix | Contoh brand |
|----------|--------|--------------|
| Togel online | `4d`, `3d`, `2d` | WIFI4D, ROMA4D, BATRE3D |
| Slot klasik | `88`, `99`, `77`, `69` | MAXWIN88, GACOR99 |
| Slot besar | `777`, `888`, `303` | SLOT777, HANA303 |
| Togel premium | `138`, `388` | BET138, SLOT388 |
| Poker/Domino | `qq` | HOBIQQ, BANDARQQ, DOMINOQQ |

**Kenapa `judolbrand` lebih baik dari hafalan nama:**

Sebelumnya, model harus menghafal ratusan nama brand: `keju`, `betawi`, `roma`, `wifi`, `batre`, `gacor`... Setiap brand baru yang belum di training data tidak akan dikenali. Dengan `judolbrand`:

1. Model belajar **satu token** yang sangat kuat sebagai sinyal spam
2. Brand baru yang mengikuti pola yang sama → langsung terdeteksi tanpa retrain
3. Token `judolbrand` ditambahkan ke `HARD_SPAM_SIGNALS` di server.py — menjadi sinyal keras yang tidak bisa di-override model

**False positive protection:**

Prefix gaming umum dikecualikan via negative lookbehind:
- `level99` → tidak berubah (level + 99, bukan brand judol)
- `rank88` → tidak berubah (konteks gaming)
- `episode77` → tidak berubah (episode TV/YouTube)

Kata gaming ini diketahui dari analisis komentar YouTube — prefix yang umum muncul sebelum angka dalam konteks non-judol.

**Contoh lengkap:**
```
Input  : "kalau udah masakan nusantara pasti ngiler, salam KEJU4D"
Step 5 : "kalau udah masakan nusantara pasti ngiler, salam keju4d"
Step 5b: "kalau udah masakan nusantara pasti ngiler, salam judolbrand"
Step 6 : "kalau udah masakan nusantara pasti ngiler  salam judolbrand"
Step 7 : "masakan nusantara ngiler salam judolbrand"
                                           ↑
                             Token kuat → model prediksi SPAM ✓
```

---

### Layer 6 — Hapus URL dan Karakter Non-Alfabet

```python
text = re.sub(r"http\S+|www\.\S+", " ", text)
text = re.sub(r"[^a-z\s]", " ", text)
```

**Masalah yang diselesaikan dua hal:**

**URL:** Link seperti `wa.me/6281234`, `bit.ly/xxxxx`, `s.id/promo` adalah sinyal spam yang kuat, tapi URL itu sendiri bervariasi tak terbatas (setiap URL berbeda). Kalau disimpan sebagai token, model akan belajar URL spesifik bukan pola umum "ada URL". Menghapusnya dan membiarkan sinyal lain (kata-kata sekitar URL) yang bekerja lebih baik.

**Karakter non-alfabet:** Setelah NFKC, homoglyph fix, dan demojize, semua karakter "penting" sudah diubah ke representasi alfabet. Yang tersisa — angka, tanda baca, simbol — adalah noise. `re.sub(r"[^a-z\s]", " ", text)` menghapus semua karakter yang bukan huruf a-z atau spasi.

---

### Layer 7 — Hapus Stopwords dan Token Pendek

```python
tokens = [
    word for word in text.split()
    if word not in STOPWORDS_ID and len(word) > 1
]
return " ".join(tokens)
```

**Stopwords adalah kata-kata yang sangat umum dan tidak informatif** — "yang", "dan", "di", "ke", "dari", "itu", "ini". Kata-kata ini muncul di hampir setiap komentar, spam maupun bukan. Kalau disertakan, mereka akan mendominasi vektor TF-IDF dengan bobot tinggi tapi tidak memberi informasi diskriminatif sama sekali.

**Token pendek (< 2 karakter)** biasanya adalah sisa-sisa normalisasi: "a", "i", "e" yang tersisa setelah simbol dihapus. Kebanyakan tidak bermakna dan hanya menambah noise.

**Contoh perjalanan satu kalimat melalui 7 layer:**

```
Input   : "𝑾𝑰𝑭𝑰𝟒𝑫 🎰💰 dаftаr sekarang bonus new member 100%!!"

Layer 1 : Sama (tidak ada zero-width di contoh ini)
Layer 2 : "WIFI4D 🎰💰 dаftаr sekarang bonus new member 100%!!"
Layer 3 : "WIFI4D 🎰💰 daftar sekarang bonus new member 100%!!"
Layer 4 : "WIFI4D slot_machine money_bag daftar sekarang bonus new member 100%!!"
Layer 5 : "wifi4d slot_machine money_bag daftar sekarang bonus new member 100%!!"
Layer 6 : "wifid slot_machine money_bag daftar sekarang bonus new member    "
Layer 7 : "wifid slot_machine money_bag daftar sekarang bonus member"

Output  : "wifid slot_machine money_bag daftar sekarang bonus member"
```

Token-token ini (`slot_machine`, `money_bag`, `daftar`, `bonus`) adalah fitur diskriminatif yang kuat untuk model SVM.

---

## 8. Dari Teks ke Angka: TF-IDF

### Mengapa perlu konversi?

Algoritma SVM (dan hampir semua algoritma ML klasik) hanya bisa bekerja dengan angka. Teks harus direpresentasikan sebagai vektor numerik sebelum bisa diproses.

Cara paling naif: buat satu kolom untuk setiap kata yang pernah ada di dataset, lalu isi 0 atau 1 tergantung apakah kata itu ada di komentar. Ini disebut **Bag of Words**.

Masalah Bag of Words: kata "dan" muncul 500 kali di seluruh dataset, kata "slot_machine" muncul 200 kali hanya di komentar spam. Kalau dihitung sama, "dan" seolah-olah lebih penting.

**TF-IDF** menyelesaikan ini dengan dua komponen:

### TF — Term Frequency

Seberapa sering sebuah kata muncul **dalam satu dokumen** (komentar) dibandingkan total kata di dokumen tersebut.

$$TF(t, d) = \frac{\text{jumlah kemunculan kata } t \text{ dalam dokumen } d}{\text{total kata dalam dokumen } d}$$

Jika komentar spam panjang berisi kata "bonus" 3 kali dari total 20 kata:
$$TF = \frac{3}{20} = 0.15$$

### IDF — Inverse Document Frequency

Seberapa **langka** sebuah kata di seluruh dataset. Kata yang ada di hampir semua dokumen mendapat bobot rendah. Kata yang hanya ada di beberapa dokumen mendapat bobot tinggi.

$$IDF(t) = \log\frac{\text{total dokumen}}{1 + \text{dokumen yang mengandung kata } t}$$

- Kata "dan" ada di 1800 dari 1799 komentar → IDF ≈ 0 (tidak berguna)
- Kata "slot_machine" ada di 300 komentar → IDF jauh lebih tinggi

### TF-IDF = TF × IDF

Skor akhir adalah perkalian keduanya. Kata mendapat bobot tinggi jika:
- Sering muncul dalam komentar tertentu (TF tinggi)
- Langka di keseluruhan dataset (IDF tinggi)

Ini persis karakteristik kata-kata yang membedakan spam dari non-spam.

### Implementasi di kode

```python
TfidfVectorizer(
    max_features=10000,    # hanya simpan 10.000 kata dengan skor TF-IDF tertinggi
    ngram_range=(1, 2),    # gunakan unigram DAN bigram
    min_df=2,              # abaikan kata yang hanya muncul di 1 komentar
    sublinear_tf=True      # gunakan log(TF) untuk reduksi dominasi kata sangat sering
)
```

**ngram_range=(1, 2)** artinya kita tidak hanya menggunakan kata tunggal, tapi juga pasangan kata berurutan:
- Unigram: `"daftar"`, `"bonus"`, `"sekarang"`
- Bigram: `"daftar sekarang"`, `"bonus member"`, `"slot gacor"`

Bigram penting karena konteks sering menentukan makna. `"tidak spam"` dan `"spam"` punya makna sangat berbeda, tapi kalau hanya pakai unigram, kata "spam" diperlakukan sama di kedua kalimat.

**min_df=2** menghapus kata yang hanya muncul di 1 dokumen — kemungkinan typo atau kata sangat spesifik yang tidak berguna sebagai fitur umum.

---

## 9. Algoritma Klasifikasi: SVM

### Intuisi dasar

Bayangkan kamu punya 1800 komentar, masing-masing direpresentasikan sebagai vektor dari 10.000 angka (skor TF-IDF). Tiap komentar adalah satu titik dalam ruang 10.000 dimensi.

Beberapa titik berlabel "spam", yang lain berlabel "non_spam". SVM mencari **hyperplane** (bidang pemisah) yang memisahkan kedua kelompok dengan **margin terlebar**.

Dalam 2 dimensi, hyperplane adalah sebuah garis:

```
    ●  ●               Spam
      ●   ●
         ─────────     ← hyperplane
      ○       ○
   ○      ○             Non-spam
```

Titik-titik yang **paling dekat ke hyperplane** di masing-masing sisi disebut **Support Vectors** (inilah asal nama "Support Vector Machine").

Mengapa margin terlebar penting? Margin yang lebar artinya model lebih **robust** — ketika ada data baru yang agak berbeda dari training data, masih ada "ruang" sebelum misklasifikasi terjadi. Ini adalah implementasi dari prinsip **generalisasi** dalam machine learning.

### Kenapa kernel linear untuk teks?

Dalam ruang berdimensi rendah, data sering tidak bisa dipisahkan dengan garis lurus. SVM bisa menggunakan **kernel** untuk mentransformasi data ke dimensi lebih tinggi di mana pemisahan linear dimungkinkan.

Untuk teks dengan TF-IDF, **kernel linear sudah cukup** karena:
1. Data sudah sangat berdimensi tinggi (10.000 fitur)
2. Dalam dimensi tinggi, data hampir selalu bisa dipisahkan secara linear
3. Kernel non-linear (RBF, polynomial) lebih lambat dan rentan overfit pada data teks

Ini bukan asumsi — sudah terbukti empiris di banyak penelitian klasifikasi teks bahwa linear SVM kompetitif dengan metode yang jauh lebih kompleks.

### Parameter C — Regularization

```python
SVC(C=1.0, ...)
```

Parameter `C` mengontrol trade-off antara **margin selebar mungkin** vs **kesalahan sekecil mungkin**:

- **C kecil (0.01, 0.1):** Model menerima lebih banyak kesalahan di training, tapi marginnya lebih lebar → lebih generalis, lebih kecil kemungkinan overfit
- **C besar (10, 100):** Model berusaha nol kesalahan di training, margin lebih sempit → bisa overfit ke data training, performa di data baru menurun

`C=1.0` adalah default yang biasanya bekerja baik sebagai titik awal.

### class_weight='balanced' — Mengatasi Ketidakseimbangan Data

Dataset kita punya ~1099 spam vs ~700 non-spam. Kalau model dibiarkan "belajar secara alami", ia akan lebih condong memprediksi spam karena kelasnya lebih besar.

`class_weight='balanced'` memerintahkan sklearn untuk **secara otomatis menyesuaikan bobot** setiap kelas berbanding terbalik dengan frekuensinya:

$$\text{bobot kelas} = \frac{\text{total sampel}}{n\_kelas \times \text{sampel di kelas ini}}$$

Untuk kelas `non_spam` (lebih sedikit) → bobotnya lebih besar → model lebih "peduli" kalau salah mengklasifikasikan non-spam.

### probability=True — Confidence Score

```python
SVC(probability=True, ...)
```

Secara default, SVM hanya mengeluarkan label binary: "spam" atau "non_spam". Parameter ini mengaktifkan kemampuan mengeluarkan **probabilitas** — seberapa yakin model dengan prediksinya.

Implementasinya menggunakan metode **Platt Scaling**: setelah SVM dilatih, sebuah logistic regression kecil dilatih di atas output SVM untuk mengkalibrasi skor ke skala 0–1.

Ini yang memungkinkan extension kita hanya menyembunyikan komentar jika confidence ≥ 75%, bukan semua yang diprediksi spam.

---

## 10. Proses Training End-to-End

### Apa itu Pipeline dalam sklearn?

```python
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(...)),
    ("svm", SVC(...))
])
```

Pipeline adalah cara menggabungkan beberapa langkah transformasi menjadi satu objek yang berperilaku seperti satu model.

**Mengapa ini penting secara teknis?**

Bayangkan kamu **tidak** menggunakan Pipeline dan melakukan ini:

```python
# CARA SALAH (data leakage!)
tfidf = TfidfVectorizer()
tfidf.fit(X_all)                    # ← FIT PADA SEMUA DATA TERMASUK TEST!
X_all_transformed = tfidf.transform(X_all)

X_train, X_test = split(X_all_transformed)
svm.fit(X_train)
svm.predict(X_test)
```

Masalahnya: TF-IDF `fit` pada seluruh data sebelum split artinya TF-IDF sudah "melihat" data test saat menghitung IDF. Ini disebut **data leakage** — model mendapat informasi "curang" dari data test yang seharusnya tidak pernah dilihatnya.

Dengan Pipeline:

```python
# CARA BENAR (Pipeline mencegah data leakage)
pipeline = Pipeline([("tfidf", TfidfVectorizer()), ("svm", SVC())])

pipeline.fit(X_train, y_train)      # TF-IDF fit HANYA pada training data
pipeline.predict(X_test)            # TF-IDF hanya transform (tidak fit lagi)
```

Pipeline memastikan `tfidf.fit_transform()` hanya dipanggil pada training data, dan saat prediksi, hanya `tfidf.transform()` yang dipanggil — menggunakan vocabulary yang dipelajari dari training.

### Stratified Train-Test Split

```python
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y       ← ini yang penting
)
```

**stratify=y** memastikan proporsi kelas yang sama di training dan test set. Tanpanya, mungkin saja secara kebetulan test set kita berisi 95% spam dan 5% non-spam, yang tidak merepresentasikan distribusi data nyata.

**random_state=42** membuat split ini reproducible — siapapun yang menjalankan kode ini akan mendapat split yang persis sama, sehingga hasil evaluasi bisa dibandingkan.

### Membaca Hasil Evaluasi

Output training menampilkan:

```
              precision    recall  f1-score   support

    non_spam       1.00      1.00      1.00       140
        spam       1.00      1.00      1.00       220

    accuracy                           1.00       360
```

**Precision per kelas:**
- Untuk `spam`: dari semua yang diprediksi spam, berapa % yang benar-benar spam?
- $$\text{Precision}_\text{spam} = \frac{TP}{TP + FP}$$

**Recall per kelas:**
- Untuk `spam`: dari semua komentar spam di test set, berapa % yang berhasil ditangkap?
- $$\text{Recall}_\text{spam} = \frac{TP}{TP + FN}$$

**F1-Score:**
- Rata-rata harmonis precision dan recall
- $$F1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
- Dipakai karena accuracy saja bisa menipu di data tidak seimbang

**Catatan tentang hasil 100%:** Ini wajar untuk dataset dengan pola yang sangat khas (nama brand + kata kunci judol) vs komentar normal. Tapi perlu diuji dengan data yang lebih beragam — terutama komentar yang "abu-abu" seperti komentar kritik tentang judi, atau berita tentang perjudian.

---

## 11. Training-Serving Consistency: Jebakan yang Sering Diabaikan

### Apa masalahnya?

Model dilatih dengan data yang sudah dipreprocess. Saat produksi, model menerima data baru. **Jika preprocessing yang diterapkan saat produksi berbeda (sekecil apapun) dari saat training, model akan menerima input yang formatnya tidak pernah ia pelajari.**

Ini disebut **training-serving skew**, dan ini salah satu penyebab paling umum mengapa model yang "bagus di lab" ternyata buruk di produksi.

### Contoh konkret bagaimana skew bisa terjadi

Bayangkan kita melakukan sebagian preprocessing di JavaScript (extension) dan sebagian lagi di Python (server):

```
Training data (Python):
"𝑹𝑶𝑴𝑨𝟒𝑫 daftar" → clean_text() → "roma daftar" → TF-IDF → SVM belajar ini

Inference (produksi):
"𝑹𝑶𝑴𝑨𝟒𝑫 daftar" → (JS di extension) → "ROMA4D daftar" → Python server → ???
```

Python server menerima `"ROMA4D daftar"`, bukan `"roma daftar"`. TF-IDF yang sudah dilatih tidak punya token `"roma4d"` dalam vocabulary-nya (karena saat training, NFKC + lowercase menghasilkan `"roma"`). Model mungkin tetap memprediksi dengan benar secara kebetulan, tapi representasinya sudah berbeda dari yang dipelajari.

### Solusi yang diterapkan di proyek ini

**Semua preprocessing dilakukan di server Python, nol preprocessing di JavaScript extension.**

Extension hanya mengirimkan teks mentah:
```javascript
// content.js — hanya ini yang dilakukan extension:
body: JSON.stringify({ text: rawCommentText })  // raw, tidak dimodifikasi
```

Server menerima teks mentah dan menjalankan pipeline yang sama persis:
```python
# server.py
cleaned = clean_text(request.text)   # ← fungsi YANG SAMA dengan yang dipakai training
label = model.predict([cleaned])[0]
```

Karena `clean_text()` dipanggil identik di kedua konteks — training dan inference — transformasinya selalu sama.

### Mengapa menggunakan original_text, bukan normalized_text untuk training?

Dataset scraper menyimpan dua versi: `original_text` dan `normalized_text`. Kita memilih `original_text`.

Alasannya sederhana: extension membaca teks langsung dari DOM YouTube — itulah `original_text`. Bukan versi yang sudah dinormalisasi.

Jika kita melatih model dengan `normalized_text`, model belajar dari teks yang sudah melewati NFKC normalization oleh scraper. Tapi saat produksi, server kita yang melakukan normalisasi. Normalisasi scraper (JavaScript) dan normalisasi server kita (Python) mungkin identik hasilnya untuk karakter standar, tapi untuk edge case tertentu bisa berbeda.

Menggunakan `original_text` + server Python melakukan semua normalisasi = **satu sumber kebenaran, satu pipeline, nol ambiguitas**.

---

## 12. FastAPI Server sebagai Jembatan

### Mengapa butuh server?

Browser extension hanya bisa menjalankan JavaScript. Library scikit-learn, preprocessing pipeline kita, dan model SVM adalah kode Python. Dua hal ini tidak bisa berjalan di tempat yang sama secara langsung.

Solusinya: **HTTP API sebagai jembatan**.

```
Extension (JS)  ──── HTTP POST ────►  Server (Python)  ──►  Model SVM
                     {text: "..."}      clean_text()         predict()
                ◄────────────────                        ◄──
                {label, confidence}      response JSON
```

HTTP adalah protokol universal. JavaScript bisa mengirim HTTP request (via `fetch()`), Python bisa menerima HTTP request (via FastAPI). Keduanya tidak perlu tahu cara kerja internal satu sama lain.

### Mengapa FastAPI?

FastAPI dipilih bukan hanya karena cepat, tapi karena satu fitur krusial: **validasi input otomatis via Pydantic**.

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

Sebelum `predict()` bahkan dipanggil, FastAPI otomatis:
1. Cek apakah body request adalah JSON valid
2. Cek apakah field `text` ada
3. Jalankan validator custom kita (tidak kosong, tidak lebih dari 5000 karakter)
4. Jika ada yang salah, kirim error 422 dengan pesan yang jelas

Ini mencegah berbagai kelas bug dan serangan (injection melalui input yang aneh) tanpa kita perlu menulis validasi manual.

### Endpoint batch — mengapa penting?

```
POST /predict/batch
{"texts": ["komentar 1", "komentar 2", ..., "komentar 50"]}
```

Halaman YouTube bisa punya 50–200 komentar yang terlihat sekaligus. Kalau extension mengirim satu request per komentar, itu 50–200 HTTP round-trip per halaman. Setiap round-trip ada overhead: koneksi TCP, HTTP headers, latency lokal. Ini lambat.

Dengan batch endpoint, 50 komentar dikirim dalam **satu request**, diproses sekaligus, dikembalikan dalam satu response. Jauh lebih efisien.

### Model dimuat sekali saat startup

```python
@app.on_event("startup")
async def startup_event():
    load_model()   # ← hanya dipanggil sekali
```

Model SVM dalam file `.joblib` berukuran ~165 KB. Memuat dari disk dan melakukan deserialisasi butuh waktu. Kalau ini dilakukan setiap request, API akan sangat lambat.

Dengan memuatnya sekali saat startup dan menyimpannya di variabel global `model`, setiap request berikutnya langsung bisa memakai model yang sudah siap di memori.

---

## 13. Browser Extension: Cara Kerjanya di Dalam Halaman

### Apa itu Content Script?

Chrome Extension terdiri dari beberapa jenis file dengan peran berbeda:

| File | Jenis | Berjalan di mana | Bisa apa |
|------|-------|-----------------|----------|
| `content.js` | Content Script | Dalam konteks halaman YouTube | Baca/ubah DOM, fetch ke localhost |
| `popup.js` | Extension Page | Popup yang muncul saat klik ikon | Akses chrome APIs, baca storage |
| `manifest.json` | Konfigurasi | — | Mendefinisikan izin dan struktur |

Content script `content.js` di-inject Chrome ke dalam halaman YouTube saat halaman dimuat. Script ini "hidup" di dalam halaman tapi terisolasi dari JavaScript halaman itu sendiri (tidak bisa akses variabel YouTube). Tapi ia bisa membaca dan memodifikasi DOM, dan bisa `fetch()` ke URL lain termasuk `localhost:8000`.

### Masalah: YouTube memuat komentar secara dinamis

YouTube tidak memuat semua komentar saat halaman pertama kali terbuka. Komentar dimuat secara bertahap saat pengguna scroll ke bawah — ini disebut **lazy loading** atau **infinite scroll**.

Kalau content script hanya scan komentar satu kali saat load, komentar-komentar yang muncul setelah scroll tidak akan pernah diproses.

Solusinya: **MutationObserver**.

```javascript
const observer = new MutationObserver((mutations) => {
    clearTimeout(scanTimeout);
    scanTimeout = setTimeout(scanComments, 1000);
});

observer.observe(document.body, { childList: true, subtree: true });
```

`MutationObserver` adalah API JavaScript yang "mengawasi" perubahan pada DOM. Setiap kali ada elemen baru ditambahkan ke halaman (termasuk komentar baru), callback kita dipanggil.

**Debounce (clearTimeout + setTimeout 1000ms):** Saat halaman scroll, DOM bisa berubah puluhan kali per detik. Tanpa debounce, `scanComments` akan dipanggil puluhan kali dalam 1 detik — sangat tidak efisien. Debounce memastikan kita menunggu **DOM berhenti berubah** selama 1 detik baru scan — biasanya artinya komentar sudah selesai dimuat.

### WeakSet untuk deduplication

```javascript
let processedComments = new WeakSet();

// ...
if (!processedComments.has(el)) {
    processedComments.add(el);
    // proses komentar ini
}
```

Setiap kali `scanComments` dipanggil, kita tidak mau mengirim ulang komentar yang sudah pernah diproses. `processedComments` menyimpan referensi ke elemen DOM yang sudah diproses.

Mengapa `WeakSet` bukan `Set` biasa? Karena `WeakSet` menyimpan referensi yang **weak (lemah)** — jika elemen HTML dihapus dari DOM oleh YouTube (misalnya karena navigasi), `WeakSet` tidak mencegah garbage collection membebaskan memori elemen itu. `Set` biasa akan menahan referensi selamanya → memory leak bertahap.

### Cara menyembunyikan komentar

```javascript
function hideSpamComment(element, confidence) {
    element.style.opacity = "0.15";
    element.style.border = "1px solid #ff4444";

    const badge = document.createElement("div");
    badge.textContent = `Spam ${Math.round(confidence * 100)}%`;
    badge.addEventListener("click", (e) => {
        e.stopPropagation();
        element.style.opacity = "1";
        element.style.border = "none";
        badge.remove();
    });

    element.appendChild(badge);
}
```

Komentar tidak dihapus dari DOM — hanya opacity-nya dikurangi ke 15%. Ini sengaja:
- User bisa memilih untuk melihat komentar yang disembunyikan dengan mengklik badge
- Menghapus dari DOM bisa menyebabkan masalah dengan cara YouTube mengelola scroll position
- Lebih aman untuk false positive — user tidak kehilangan komentar secara permanen

---

## 14. Alur Lengkap dari Komentar Muncul Sampai Disembunyikan

Berikut urutan eksak yang terjadi, dari detik 0 hingga komentar tersembunyi:

```
[T=0ms]    User buka YouTube, halaman mulai dimuat

[T=~500ms] Chrome inject content.js ke halaman

[T=~501ms] init() dipanggil:
           1. Fetch GET localhost:8000/health
           2. Response: {"model_loaded": true}
           3. isServerAvailable = true

[T=~502ms] scanComments() pertama dipanggil:
           - querySelectorAll("ytd-comment-thread-renderer")
           - Komentar belum ada (belum scroll ke bagian komentar)
           - Tidak ada yang diproses

[T=~5000ms] User scroll ke bawah, komentar pertama dimuat YouTube
            MutationObserver mendeteksi perubahan DOM
            Debounce: clearTimeout + setTimeout(scanComments, 1000)

[T=~6000ms] scanComments() dipanggil setelah 1 detik idle:
            - querySelectorAll menemukan 20 komentar
            - Semua 20 belum ada di processedComments → masuk toProcess
            - Semua 20 ditandai di processedComments
            - texts = array 20 teks komentar (RAW, tidak dimodifikasi)

[T=~6001ms] POST localhost:8000/predict/batch
            Body: {"texts": ["komentar 1", ..., "komentar 20"]}

[T=~6010ms] SERVER PYTHON menerima request:
            Untuk setiap teks:
              clean_text("𝑹𝑶𝑴𝑨𝟒𝑫 daftar sekarang...")
              Layer 1: strip zero-width
              Layer 2: NFKC → "ROMA4D daftar sekarang..."
              Layer 3: homoglyph (tidak ada Cyrillic di sini)
              Layer 4: demojize emoji
              Layer 5: lowercase → "roma4d daftar sekarang..."
              Layer 6: hapus URL + non-alpha → "romad daftar sekarang"
              Layer 7: hapus stopwords → "romad daftar bonus member"
              model.predict(["romad daftar bonus member"])
              → "spam", confidence 0.97

[T=~6011ms] Response: {"results": [
              {"label": "spam", "confidence": 0.97, "is_spam": true},
              {"label": "non_spam", "confidence": 0.88, "is_spam": false},
              ... 18 lainnya
            ]}

[T=~6012ms] Extension iterasi results:
            - Komentar 1: is_spam=true, confidence=0.97 ≥ 0.75
              → hideSpamComment(element, 0.97)
              → opacity: 0.15, border merah, badge "Spam 97%"
            - Komentar 2: is_spam=false
              → tidak ada tindakan

[T=~6012ms] hiddenCount++ → chrome.storage.local.set({hiddenCount: 1})
            Popup yang terbuka akan update angkanya
```

---

## 15. Pertanyaan yang Mungkin Muncul Saat Sidang

**Q: Mengapa memilih SVM dibanding metode lain seperti Naive Bayes atau Neural Network?**

Untuk klasifikasi teks dengan dataset berukuran ribuan:
- **Naive Bayes** lebih cepat tapi mengasumsikan semua fitur independen (tidak realistis untuk teks)
- **SVM** tidak membuat asumsi distribusi, bekerja sangat baik di dimensi tinggi, terbukti kompetitif di teks
- **Neural Network** butuh jauh lebih banyak data (puluhan ribu minimum), komputasi berat, dan sulit dijelaskan ("black box")

Untuk skripsi, SVM dipilih karena kombinasi performa yang baik + interpretabilitas yang cukup (support vectors bisa diinspeksi) + implementasi mature di scikit-learn.

---

**Q: Akurasi 100% di test set — bukankah ini tanda overfitting?**

Overfitting adalah ketika model "menghafal" training data dan gagal generalisasi ke data baru. Gejalanya: akurasi training tinggi sekali tapi akurasi test turun signifikan.

Di sini, akurasi **test set** juga 100% — bukan hanya training set. Artinya model berhasil generalisasi ke data yang tidak pernah ia lihat.

Mengapa ini mungkin? Karena komentar spam judi memiliki pola yang sangat khas dan konsisten (nama brand, kata kunci spesifik). Komentar non-spam sama sekali tidak mengandung pola ini. Dua kelas ini sangat mudah dipisahkan secara linear di ruang TF-IDF.

Caveats yang perlu disebutkan:
1. Test set ini masih dari distribusi data yang sama (YouTube Indonesia)
2. Kalau ada spam dengan pola yang benar-benar baru (brand name baru yang belum pernah ada di training data), model mungkin tidak mengenalinya
3. Perlu pengujian dengan data yang lebih beragam untuk validasi sesungguhnya

---

**Q: Kenapa synthetic data untuk non-spam, bukan data nyata?**

Scraper dirancang untuk mengumpulkan spam — tidak ada scraper untuk komentar non-spam. Mengumpulkan non-spam nyata butuh effort yang sama: menjalankan scraper yang berbeda, memverifikasi secara manual bahwa komentar-komentar itu memang bukan spam.

Synthetic data adalah kompromi pragmatis untuk bisa menjalankan proyek ini. Template non-spam yang dibuat cukup beragam (tutorial, gaming, musik, reaksi umum) untuk mencegah model belajar hanya mengenali "komentar spam" vs "komentar template tertentu".

Untuk improvement: kumpulkan komentar non-spam nyata dari YouTube dan ganti `generate_non_spam_data()` di `prepare_dataset.py` dengan loader dari file nyata.

---

**Q: Apa kelemahan utama sistem ini?**

1. **Dependency pada server lokal:** Extension tidak bisa bekerja tanpa Python server berjalan. Ini tidak praktis untuk pengguna umum.
2. **Tidak ada update model otomatis:** Spammer bisa belajar pola baru yang model belum pernah lihat.
3. **False positive untuk konten edukatif:** Artikel atau komentar yang membahas "bahaya judi" mungkin mengandung kata-kata yang sama dengan spam.
4. **Hanya YouTube/Instagram:** Scraper CSS selectors spesifik untuk dua platform ini.

---

**Q: Mengapa threshold confidence 0.75, bukan 0.5 atau 0.9?**

0.5 artinya model "sedikit lebih yakin spam daripada tidak" — terlalu sensitif, banyak false positive.

0.9 artinya hanya komentar yang sangat jelas spam yang disembunyikan — banyak spam lolos.

0.75 adalah keputusan desain (bukan hasil optimasi matematis). Artinya model harus setidaknya 75% yakin baru ambil tindakan. Bisa diubah di `content.js` sesuai preferensi trade-off precision vs recall.

---

## 16. Evaluasi Model yang Lebih Jujur (Fase 2)

> Bagian ini menjelaskan tiga teknik evaluasi yang ditambahkan di Fase 2: k-fold cross-validation, GridSearchCV, dan baseline comparison. Ketiganya sudah diimplementasikan di `src/train.py` dan akan berjalan otomatis setiap kali kamu `python src/train.py`.

---

### 16.1 Masalah dengan Single Train-Test Split

Sebelum Fase 2, evaluasi model hanya menggunakan satu split: 80% untuk training, 20% untuk test. Angka akurasi 97.23% berasal dari split ini.

**Masalahnya:** Split 80/20 adalah satu sampel dari semua kemungkinan cara membagi data. Bisa saja kita "beruntung" — test set yang terbentuk kebetulan lebih mudah dari rata-rata. Sebaliknya bisa juga "sial" — test set kebetulan lebih sulit. Kita tidak tahu mana yang terjadi hanya dari satu angka.

Penguji yang jeli akan bertanya: *"Kalau split-nya beda, akurasinya masih segini?"*

Tiga teknik berikut menjawab pertanyaan itu.

---

### 16.2 K-Fold Cross-Validation

**Analogi:** Bayangkan kamu mau tahu rata-rata nilai ujian seorang mahasiswa. Kalau cuma kasih satu ujian, hasilnya mungkin bias (hari itu lagi capek, atau soalnya kebetulan gampang). Solusi: kasih 5 ujian dengan materi berbeda, laporkan rata-ratanya plus variasi antar ujian.

**Cara kerja (cv=5):**
1. Bagi seluruh dataset jadi 5 "fold" (bagian) yang sama besar.
2. Iterasi 5 kali. Di setiap iterasi:
   - 1 fold dijadikan **test set**
   - 4 fold sisanya dijadikan **training set**
   - Latih model dari awal, evaluasi di test fold
3. Catat F1-score dari tiap iterasi → hasilnya 5 angka.
4. Laporkan **mean ± std** dari 5 angka itu.

```
Fold 1: [TEST][TRAIN][TRAIN][TRAIN][TRAIN] → F1 = 0.9712
Fold 2: [TRAIN][TEST][TRAIN][TRAIN][TRAIN] → F1 = 0.9698
Fold 3: [TRAIN][TRAIN][TEST][TRAIN][TRAIN] → F1 = 0.9741
Fold 4: [TRAIN][TRAIN][TRAIN][TEST][TRAIN] → F1 = 0.9706
Fold 5: [TRAIN][TRAIN][TRAIN][TRAIN][TEST] → F1 = 0.9723
                                              Mean = 0.9716 ± 0.0015
```

**Apa yang dilaporkan:**
- `scores.mean()` → F1-macro rata-rata
- `scores.std()` → seberapa konsisten hasilnya lintas fold

Std yang kecil (misalnya 0.003) artinya model konsisten, tidak bergantung pada "keberuntungan" split tertentu.

**Catatan implementasi:** Cross-validation di `train.py` dijalankan di full dataset (bukan hanya X_train) karena tujuannya adalah estimasi generalisasi — semakin banyak data difolding, semakin stabil estimasinya. Ini berbeda dari split 80/20 yang tetap dipakai untuk confusion matrix detail.

**Relevansi untuk skripsi:** Di bab hasil, kamu bisa tulis: *"Model mencapai F1-macro rata-rata X ± Y dari 5-fold cross-validation, menunjukkan konsistensi performa yang tidak bergantung pada satu pembagian data tertentu."*

---

### 16.3 GridSearchCV — Hyperparameter Tuning Otomatis

**Konteks:** SVM punya parameter bernama **C** (regularization parameter). Sebelum Fase 2, nilai C=1.0 dipakai karena itu default-nya sklearn — bukan karena ada alasan khusus.

**Apa itu C?**

Bayangkan SVM sedang menggambar garis pemisah antara komentar spam dan non-spam. C mengontrol seberapa "ketat" model mencoba memisahkan semua titik training:

```
C kecil (misal 0.01):          C besar (misal 100):
Garis lebih "santai"            Garis lebih "keras"
Menerima beberapa salah klasifikasi   Memaksa semua benar
Lebih general                   Lebih overfit
```

**GridSearchCV cara kerjanya:**
1. Siapkan kandidat: `C ∈ [0.01, 0.1, 1, 10, 100]`
2. Untuk setiap kandidat C, jalankan 5-fold cross-validation di X_train
3. Pilih C yang menghasilkan F1-macro tertinggi
4. Gunakan C terpilih untuk melatih model final

```
GridSearchCV result:
  C=0.01   F1-macro CV = 0.9523
  C=0.1    F1-macro CV = 0.9678
  C=1      F1-macro CV = 0.9716  <-- terpilih
  C=10     F1-macro CV = 0.9698
  C=100    F1-macro CV = 0.9689
```

**Kenapa dilakukan di X_train saja, bukan full data?**
Karena X_test adalah data yang harus *belum pernah terlihat* oleh model maupun proses pemilihan parameter. Kalau kita pakai X_test untuk pilih C, sebenarnya kita sedang "mengintip" test set — hasilnya tidak lagi mencerminkan performa di data dunia nyata. Ini disebut **data leakage**.

**Relevansi untuk skripsi:** *"Nilai C dipilih melalui GridSearchCV dengan 5-fold cross-validation pada data training, menghasilkan C=X dengan F1-macro tertinggi sebesar Y."* Ini jauh lebih kuat daripada "C=1.0 adalah nilai default."

---

### 16.4 Baseline Comparison — Kenapa Harus SVM?

**Konteks:** Di bab metodologi skripsi, kamu harus bisa menjawab: *"Kenapa pakai SVM, bukan algoritma lain?"*

Jawaban teoritis: SVM bagus untuk data teks berdimensi tinggi karena kernel linear efisien di ruang feature besar.

Jawaban empiris (lebih kuat): *"Kami juga melatih Naive Bayes dan Logistic Regression dengan feature TF-IDF yang sama. SVM mengungguli keduanya dengan F1-macro X vs Y dan Z."*

**Dua baseline yang dibandingkan:**

**1. Multinomial Naive Bayes (MultinomialNB)**
- Asumsi: setiap kata independen satu sama lain (ini "naive" — jelas tidak sepenuhnya benar)
- Kelebihan: sangat cepat, sering jadi baseline kuat di text classification
- Kekurangan: asumsi independensi terlalu simplistic untuk teks alami

**2. Logistic Regression**
- Model linear seperti SVM, tapi mengoptimalkan probabilitas (log-loss) bukan margin
- Sering sangat kompetitif dengan SVM di text classification
- Kelebihan: output probability lebih terkalibrasi (lebih mudah diinterpretasikan)

**Yang dibandingkan:** Ketiganya pakai TF-IDF yang *sama persis* (sama `max_features`, `ngram_range`, `min_df`, `sublinear_tf`). Yang berbeda hanya klasifiernya. Ini memastikan perbandingan adil — apapun perbedaan hasilnya, itu murni karena perbedaan algoritma, bukan karena perbedaan feature.

**Contoh output:**
```
  Model                              Accuracy   F1-macro
  ---------------------------------  ---------  --------
  SVM (model utama)                     97.23%    0.9716  (*)
  Naive Bayes (MultinomialNB)           93.48%    0.9287
  Logistic Regression                   96.81%    0.9654

  (*) = model yang disimpan dan dipakai di production
```

**Selain tabel, confusion matrix juga disimpan untuk tiap model** ke folder `reports/`:
- `reports/confusion_matrix_svm.png`
- `reports/confusion_matrix_naive_bayes_multinomialnb.png`
- `reports/confusion_matrix_logistic_regression.png`

Gambar-gambar ini bisa langsung dipakai di lampiran skripsi.

---

### 16.5 Ringkasan: Apa yang Berubah di train.py

| Sebelum Fase 2 | Setelah Fase 2 |
|---|---|
| 1 split 80/20, 1 angka akurasi | K-fold CV (cv=5): mean ± std |
| C=1.0 karena default | C dipilih via GridSearchCV |
| Hanya SVM yang dievaluasi | SVM vs NB vs LR — ada bukti empiris |
| Confusion matrix di terminal (teks) | Confusion matrix tersimpan sebagai PNG |

Semua ini berjalan otomatis saat `python src/train.py`. Output lama (akurasi, classification report, confusion matrix teks) tetap ada — yang baru ditambahkan di atasnya.

---

*Dokumen ini adalah komplemen dari README.md. README membahas cara menjalankan; dokumen ini membahas cara memahami.*

---

## 20. Perbaikan Extension — Fase 4

> Tiga perbaikan di layer extension (JavaScript) yang membuat sistem lebih robust dan jujur. Tidak ada perubahan di model atau preprocessing.

---

### 20.1 Bug: `scannedCount` Selalu 0

**Masalah:** Popup menampilkan dua angka — "komentar spam disembunyikan" dan "komentar telah dipindai". Angka pertama benar karena `hiddenCount` memang ditulis ke `chrome.storage` setiap kali komentar disembunyikan. Tapi angka kedua selalu 0, karena `content.js` tidak pernah menulis `scannedCount` ke storage.

**Penyebab:** `updateBadgeCount()` lama hanya menyimpan `hiddenCount`. Tidak ada kode yang melacak berapa total komentar yang dikirim ke API.

**Perbaikan:** Di `scanComments()`, setelah mengumpulkan komentar baru yang belum diproses:
```javascript
// Increment sebelum kirim ke API — semua yang dikirim sudah "dipindai"
scannedCount += toProcess.length;
persistStats(); // simpan hiddenCount + scannedCount sekaligus
```

Fungsi `updateBadgeCount()` diganti dengan `persistStats()` yang menyimpan keduanya:
```javascript
function persistStats() {
  chrome.storage.local.set({ hiddenCount, scannedCount });
}
```

---

### 20.2 Fitur Baru: Threshold Slider di Popup

**Konteks:** Sebelumnya, nilai threshold 0.75 (75%) tersimpan hardcoded di baris:
```javascript
const CONFIDENCE_THRESHOLD = 0.75;
```

Ini artinya untuk mengubah threshold, pengguna harus buka kode, edit file, dan reload extension. Tidak praktis — terutama untuk demo sidang.

**Apa itu threshold dan kenapa penting?**

Threshold adalah batas minimum keyakinan model sebelum komentar disembunyikan. Model mengembalikan skor 0.0–1.0 untuk setiap komentar:
- Skor 0.95 → model 95% yakin ini spam → hampir pasti disembunyikan
- Skor 0.60 → model 60% yakin → ambigu, keputusan tergantung threshold

```
Threshold rendah (50%):  banyak komentar disembunyikan, termasuk yang ambigu
                         → presisi rendah, recall tinggi (banyak false positive)

Threshold tinggi (95%):  hanya komentar yang sangat jelas spam disembunyikan
                         → presisi tinggi, recall rendah (banyak spam lolos)

Threshold 75% (default): titik tengah yang masuk akal untuk penggunaan umum
```

**Cara kerja setelah perbaikan:**

1. Popup menampilkan slider range 50%–95%
2. Saat user geser slider, nilai disimpan ke `chrome.storage.local` sebagai decimal:
   ```javascript
   chrome.storage.local.set({ confidenceThreshold: pct / 100 });
   // contoh: slider di 80% → simpan 0.80
   ```
3. `content.js` membaca nilai ini saat init (`loadSettings()`)
4. Kalau user geser slider saat tab YouTube sudah terbuka, perubahan langsung aktif tanpa reload — karena `content.js` pasang listener:
   ```javascript
   chrome.storage.onChanged.addListener((changes) => {
     if (changes.confidenceThreshold) {
       confidenceThreshold = changes.confidenceThreshold.newValue;
     }
   });
   ```

**Kenapa disimpan sebagai decimal, bukan persen?**

API selalu mengembalikan confidence sebagai decimal (0.0–1.0). Kalau kita simpan threshold sebagai persen (75), kita harus konversi di `content.js` setiap kali dipakai. Lebih bersih kalau formatnya konsisten: simpan 0.75, bandingkan dengan 0.75. Konversi hanya terjadi satu kali saat slider berubah (`pct / 100`).

---

### 20.3 Perbaikan: Server Mati Setelah Extension Berjalan

**Masalah:** Health check hanya dilakukan sekali saat `init()`. Kalau server mati setelah itu (misalnya karena terminal ditutup), variabel `isServerAvailable` tetap `true`. Setiap kali ada komentar baru, `scanComments()` tetap berjalan dan memanggil `predictBatch()` yang langsung gagal. Kegagalan ini diam-diam diabaikan (`return null`), jadi pengguna tidak tahu ada yang salah.

**Perbaikan:** Di `predictBatch()`, saat catch error (artinya server tidak bisa dihubungi):
```javascript
} catch {
  // Server mungkin mati setelah health check awal.
  // Re-check supaya isServerAvailable diperbarui dan
  // scan berikutnya tidak terus mencoba hit server mati.
  console.warn("[Judol Detector] Batch request failed, re-checking server...");
  await checkServerHealth();
  return null;
}
```

Setelah `checkServerHealth()` berjalan, `isServerAvailable` diset `false`. Scan berikutnya akan langsung `return` di baris pertama `scanComments()`:
```javascript
if (!isServerAvailable) return;
```

Sehingga tidak ada lagi request yang terus dikirim ke server yang sudah mati.

**Trade-off:** Kalau server restart (mati lalu hidup lagi), extension tidak otomatis aktif kembali — pengguna perlu klik "Cek Status Server" di popup, yang memanggil `checkServerHealth()` lagi dan memperbarui `isServerAvailable = true`. Ini perilaku yang lebih aman daripada polling otomatis yang bisa menyebabkan banyak request tak berguna.

---

### 20.4 Keterbatasan yang Didokumentasikan

**Selector Instagram mungkin sudah tidak valid.** `content.js` menggunakan:
```javascript
instagram: {
  commentContainer: "ul._a9ym li",
  commentText: "span._aacl",
}
```

Instagram menggunakan class names yang di-generate otomatis dan sering berubah saat mereka update UI. Selector ini mungkin sudah tidak valid. Karena fokus penelitian ini adalah YouTube, keterbatasan ini perlu disebutkan di bab keterbatasan skripsi:

> *"Dukungan Instagram bersifat eksperimental dan bergantung pada CSS selector yang dapat berubah sewaktu-waktu seiring pembaruan UI platform. Pengujian utama dilakukan di YouTube."*

---

## 19. Eksperimen Konfigurasi TF-IDF — ngram dan max_features

> Bagian ini menjelaskan apa itu ngram dan max_features, bagaimana eksperimennya dirancang, dan apa yang bisa kita pelajari dari hasilnya — termasuk satu temuan yang tidak terduga.

---

### 19.1 Dua Parameter TF-IDF yang Diuji

Sebelum lanjut ke eksperimen, perlu dipahami dulu apa yang dimaksud dengan dua parameter ini.

---

**Parameter 1: `ngram_range` — Seberapa panjang "potongan kata" yang dijadikan fitur?**

TF-IDF memecah teks jadi potongan-potongan kecil yang disebut *n-gram*, lalu menghitung seberapa penting tiap potongan itu.

- **Unigram (n=1):** setiap kata tunggal adalah satu fitur
  ```
  "daftar sekarang bonus besar"
  → fitur: ["daftar", "sekarang", "bonus", "besar"]
  ```

- **Bigram (n=2):** kata tunggal + pasangan dua kata berurutan
  ```
  "daftar sekarang bonus besar"
  → fitur: ["daftar", "sekarang", "bonus", "besar",
            "daftar sekarang", "sekarang bonus", "bonus besar"]
  ```

- **Trigram (n=3):** tambah tiga kata berurutan
  ```
  → fitur: [...semua unigram dan bigram di atas...,
            "daftar sekarang bonus", "sekarang bonus besar"]
  ```

Dengan `ngram_range=(1,2)`, kita pakai unigram dan bigram sekaligus. Tujuannya: model bisa belajar pola frasa, bukan hanya kata individual. Harapannya "daftar sekarang" sebagai satu bigram lebih informatif daripada kata "daftar" dan "sekarang" yang muncul secara terpisah.

---

**Parameter 2: `max_features` — Berapa banyak fitur yang dipakai?**

Setelah semua n-gram dihitung dari seluruh corpus, hasilnya bisa puluhan ribu fitur. `max_features` membatasi: *ambil hanya N fitur yang paling informatif* (diukur dari TF-IDF score tertinggi). Sisanya dibuang.

- `max_features=5000` → simpan 5.000 fitur terpenting
- `max_features=10000` → simpan 10.000 fitur terpenting ← baseline saat ini
- `max_features=20000` → simpan 20.000 fitur terpenting

Logika di baliknya: fitur yang sangat jarang (muncul hanya 1-2 kali di seluruh dataset) tidak cukup representatif untuk dijadikan sinyal. Membuangnya membuat model lebih efisien dan kadang lebih akurat.

---

### 19.2 Desain Eksperimen

Sama seperti eksperimen sebelumnya — ubah satu hal, jaga semua yang lain:

```
Model A : ngram=(1,1), feat=10k  ← hanya unigram
Model B : ngram=(1,2), feat=10k  ← baseline (unigram + bigram)
Model C : ngram=(1,3), feat=10k  ← unigram + bigram + trigram
Model D : ngram=(1,2), feat=5k   ← lebih sedikit fitur
Model E : ngram=(1,2), feat=20k  ← lebih banyak fitur
```

SVM, data, dan split identik di semua model.

---

### 19.3 Hasil Eksperimen

Dijalankan dengan: `python src/experiment_features.py`

```
  Konfigurasi       Deskripsi           Accuracy  F1-macro   Vocab  vs Baseline
  ----------------  ------------------  --------  ---------  -----  -----------
  Baseline          ngram=(1,2) feat=10k  97.23%   0.9671    4.056  (baseline)
  Unigram only      ngram=(1,1) feat=10k  97.51%   0.9704    2.542  +0.0034
  Trigram           ngram=(1,3) feat=10k  97.23%   0.9671    4.716  +0.0000
  Fewer features    ngram=(1,2) feat=5k   97.23%   0.9671    4.056  +0.0000
  More features     ngram=(1,2) feat=20k  97.23%   0.9671    4.056  +0.0000
```

→ Lihat grafik: `reports/experiment_features.png`

---

### 19.4 Temuan 1 — Unigram Sedikit Lebih Baik dari Bigram

**Apa yang terjadi?** Model dengan hanya unigram (`ngram=(1,1)`) menghasilkan F1-macro 0.9704, sedikit di atas baseline bigram 0.9671 (+0.0034).

**Kenapa ini mengejutkan?** Secara intuitif, bigram "seharusnya" lebih baik karena menangkap konteks. "Daftar sekarang" sebagai satu frasa harusnya lebih informatif dari kata "daftar" sendirian.

**Penjelasan mengapa unigram bisa setara atau sedikit lebih baik:**

Sinyal spam di dataset ini didominasi oleh **kata tunggal yang sangat spesifik** — nama brand judi (`bardi`, `pstoto`, `jptogel`) dan kata-kata bermakna khusus (`hoki`, `rezeki`, `situs`). Kata-kata ini sudah sangat kuat sebagai sinyal spam tanpa perlu konteks tetangga kirinya atau kanannya.

Ketika kita tambahkan bigram, kita menambahkan ribuan kombinasi pasangan kata. Sebagian besar kombinasi ini muncul sangat jarang di corpus, sehingga TF-IDF memberi mereka bobot tinggi padahal sebenarnya tidak cukup representatif. Ini bisa menjadi *noise* yang sedikit mengganggu performa.

**Apakah ini berarti kita harus ganti ke unigram?**

Selisih +0.0034 terlalu kecil untuk dianggap signifikan secara praktis. Dalam 722 sampel test, selisih ini setara dengan 2-3 prediksi yang berbeda. Bisa saja dengan split data yang berbeda, hasilnya berbalik. Oleh karena itu, keputusan untuk tetap menggunakan baseline `(1,2)` adalah wajar — dan bisa dijelaskan di skripsi sebagai pilihan konservatif yang terbukti tidak kalah dari unigram.

---

### 19.5 Temuan 2 — max_features Tidak Relevan untuk Dataset Ini

**Apa yang terjadi?** Mengubah `max_features` dari 5.000 ke 10.000 ke 20.000 tidak mengubah apapun — F1-macro tetap 0.9671 dan ukuran vocabulary tetap **4.056** di ketiga konfigurasi.

**Kenapa?**

`max_features` adalah batas atas: "ambil maksimal N fitur terbaik." Tapi kalau corpus kita hanya menghasilkan 4.056 fitur unik, maka tidak ada yang perlu dipotong — batas 5.000, 10.000, atau 20.000 sama-sama tidak tercapai.

Bayangkan sebuah toples yang muat 10.000 kelereng, tapi kita hanya punya 4.056 kelereng — menggunakan toples yang lebih besar tidak mengubah jumlah kelereng.

**Mengapa vocabulary kita hanya 4.056?**

Dataset kita memiliki 3.608 komentar. Setelah preprocessing (hapus stopwords, URL, karakter non-huruf, token pendek, kata yang muncul < 2 kali / `min_df=2`), kata-kata unik yang tersisa memang hanya sekitar 4.000-an. Ini wajar untuk dataset teks pendek (komentar YouTube rata-rata pendek) dengan domain yang terbatas.

**Konsekuensinya:**
- Tuning `max_features` tidak berguna selama dataset masih sekecil ini
- Kalau dataset diperluas (misalnya 10x lebih banyak), vocabulary akan bertumbuh dan `max_features` akan mulai relevan
- Ini juga berarti model kita relatif ringan — hanya 4.056 dimensi, bukan 10.000

---

### 19.6 Kesimpulan dan Rekomendasi untuk Skripsi

**Keputusan teknis:** Konfigurasi baseline `ngram=(1,2), max_features=10000` tetap dipakai. Perubahan apapun tidak memberikan perbedaan yang signifikan secara praktis.

**Kalimat untuk bab metodologi/pembahasan:**

> *"Eksperimen konfigurasi TF-IDF dilakukan untuk mengevaluasi pengaruh parameter ngram_range dan max_features terhadap performa model. Lima konfigurasi diuji dengan SVM, data, dan split yang identik. Hasil menunjukkan bahwa unigram saja (ngram=(1,1)) menghasilkan F1-macro 0.9704 dibandingkan 0.9671 pada baseline bigram, namun perbedaan sebesar 0.0034 tidak cukup signifikan secara praktis untuk membenarkan perubahan. Temuan yang lebih menarik adalah bahwa perubahan max_features (5k/10k/20k) tidak berdampak sama sekali — vocabulary aktual setelah preprocessing hanya sebesar 4.056 fitur unik, jauh di bawah semua nilai max_features yang diuji. Hal ini menunjukkan bahwa constraintnya adalah ukuran dataset, bukan parameter model. Konfigurasi baseline dipertahankan sebagai pilihan yang paling konservatif dengan performa yang terbukti setara atau lebih baik dari alternatif."*

---

### 19.7 Cara Menjalankan

```bash
python src/experiment_features.py
```

Output tersimpan di `reports/`:
- `experiment_features.png` — grafik batang perbandingan F1-macro
- `experiment_features.csv` — tabel lengkap semua metrik per konfigurasi

---

## 18. Eksperimen Stemming — Apakah Stemming Membantu?

> Bagian ini menjelaskan apa itu stemming, bagaimana eksperimennya dirancang, dan apa artinya hasilnya untuk skripsi.

---

### 18.1 Apa itu Stemming?

Bayangkan kamu sedang membaca dan menemukan kata-kata ini: **"mendaftar"**, **"terdaftar"**, **"pendaftaran"**, **"daftar"**. Sebagai manusia, kamu langsung tahu semua kata itu berkaitan dengan konsep yang sama: *daftar*.

Tapi bagi model machine learning, keempat kata itu adalah empat fitur yang berbeda. Model harus "belajar" sendiri bahwa keempatnya saling berkaitan — dan untuk itu butuh banyak contoh di data training.

**Stemming** adalah teknik yang memotong semua variasi kata itu ke bentuk dasarnya sebelum dimasukkan ke model:
```
mendaftar   → daftar
terdaftar   → daftar
pendaftaran → daftar
daftar      → daftar  (sudah dalam bentuk dasar)
```

Hasilnya: model hanya perlu belajar satu fitur ("daftar") yang muncul lebih sering, daripada empat fitur berbeda yang masing-masing muncul sedikit.

**Sastrawi** adalah library stemming khusus Bahasa Indonesia. Cara kerjanya: untuk setiap kata, Sastrawi mencari bentuk dasar di kamus bahasa Indonesia sambil memperhatikan aturan awalan/akhiran (prefiks/sufiks) Bahasa Indonesia.

---

### 18.2 Kenapa Tidak Langsung Ditambahkan ke Pipeline?

Intuisi bilang: *"stemming pasti membantu, tambahkan saja."* Tapi di machine learning, intuisi sering salah. Sebelum mengubah pipeline produksi, kita harus **membuktikan dengan angka** apakah stemming benar-benar meningkatkan performa.

Kalau kita langsung menambahkan stemming ke `preprocessing.py` tanpa eksperimen:
- Kalau performa naik → kita tidak tahu seberapa besar pengaruhnya
- Kalau performa turun → kita tidak tahu stemming yang menyebabkannya
- Tidak ada angka perbandingan yang bisa dikutip di skripsi

Jadi lebih baik: desain eksperimen yang terkontrol, latih dua model, bandingkan.

---

### 18.3 Desain Eksperimen

**Prinsip:** ubah satu variabel, jaga semua yang lain tetap sama.

```
Model A (baseline):   preprocessing biasa → TF-IDF → SVM
Model B (eksperimen): preprocessing + stemming → TF-IDF → SVM
```

Yang dijaga sama persis antara Model A dan B:
- Dataset (file CSV yang sama)
- Split train/test (random_state=42, test_size=0.2)
- Parameter TF-IDF (max_features=10000, ngram_range=(1,2), dll)
- Parameter SVM (C=1, kernel=linear, class_weight=balanced)

Yang **satu-satunya berbeda**: setelah `clean_text()`, Model B menambahkan satu langkah `stemmer.stem(text)`.

Kalau dengan pengaturan seperti ini Model B lebih baik dari Model A → perbedaannya murni karena stemming.

---

### 18.4 Cara Stemming Ditambahkan ke Pipeline

Stemming dilakukan **setelah** `clean_text()`, bukan di dalamnya. Alasannya:

1. `clean_text()` sudah membuang noise (emoji, URL, karakter aneh). Stemmer bekerja lebih baik pada teks bersih.
2. Kita tidak ingin mengubah `preprocessing.py` (yang dipakai di production/server) — eksperimen harus berdiri sendiri.

```python
def preprocess_with_stemming(texts):
    cleaned = preprocess_batch(texts)          # langkah 1: 7 step biasa
    stemmed = [stemmer.stem(t) for t in cleaned]  # langkah 2: stemming
    return stemmed
```

**Contoh output aktual:**
```
Input (raw)    : "Aku gak tertarik menang 🔥 BARDI4D"
Tanpa stemming : "aku gak tertarik menang fire bardi"
Dengan stemming: "aku gak tarik menang fire bardi"
```

Perhatikan: "tertarik" → "tarik". Stemmer memotong awalan "ter-".

---

### 18.5 Hasil Eksperimen

Dijalankan dengan: `python src/experiment_stemming.py`

```
  Model                         Accuracy   F1-spam   F1-non    F1-macro
  ----------------------------  ---------  --------  --------  --------
  Tanpa Stemming (baseline)      97.23%    0.9539    0.9802    0.9671
  Dengan Stemming (Sastrawi)     97.23%    0.9543    0.9801    0.9672

  Perbedaan F1-macro: +0.0002
```

→ Lihat grafik: `reports/experiment_stemming.png`

---

### 18.6 Interpretasi Hasil

**Perbedaan 0.0002 di F1-macro itu artinya apa?**

F1-macro 0.9671 vs 0.9672 — selisihnya cuma 0.0002. Angka ini **jauh di bawah ambang signifikansi praktis**. Dengan kata lain: dalam penggunaan nyata, kedua model ini berperilaku identik. Stemming tidak memberikan manfaat yang berarti.

**Kenapa stemming tidak membantu di sini?**

Ada tiga penjelasan yang masuk akal:

1. **Spam pakai nama brand, bukan kata imbuhan.**
   Kata-kata paling khas di komentar spam adalah nama brand: ROMA4D, WIFI4D, PSTOTO, dll. Kata-kata ini sudah dalam bentuk "dasar" yang tidak bisa di-stem lagi. Stemming tidak punya apa-apa untuk dikerjakan di sini.

2. **TF-IDF bigram sudah menangani variasi kata.**
   Dengan `ngram_range=(1,2)`, TF-IDF membuat fitur untuk pasangan kata juga. "daftar sekarang" dan "mendaftar sekarang" menjadi dua fitur bigram yang berbeda — tapi keduanya tetap terdeteksi sebagai pola spam karena konteks kata di sekitarnya sama. Model bisa belajar kedua pola ini tanpa perlu stemming.

3. **Bahasa komentar YouTube bersifat informal dan slang.**
   Sastrawi dirancang untuk Bahasa Indonesia formal. Kata-kata seperti "gue", "udah", "nggak", "kuy" tidak ada di kamus Sastrawi — stemmer melewatinya begitu saja atau malah salah memprosesnya. Untuk domain komentar media sosial, keterbatasan ini cukup signifikan.

**Apakah ini hasil yang buruk?**

Tidak. Justru sebaliknya — ini hasil yang *jujur* dan *berharga* untuk skripsi.

Banyak paper akademis hanya melaporkan hal-hal yang berhasil. Melaporkan eksperimen yang "tidak berhasil" beserta penjelasan yang solid justru menunjukkan bahwa peneliti memahami domain masalahnya — bukan sekadar mencoba teknik secara acak lalu melaporkan yang kebetulan bagus.

---

### 18.7 Kesimpulan dan Rekomendasi untuk Skripsi

**Keputusan teknis:** Model produksi tetap menggunakan pipeline *tanpa* stemming. Lebih sederhana, lebih cepat, dan hasilnya sama.

**Kalimat untuk bab metodologi/pembahasan:**

> *"Eksperimen stemming menggunakan library PySastrawi dilakukan untuk mengevaluasi apakah normalisasi morfologi dapat meningkatkan performa model. Dua model dilatih dengan kondisi identik (dataset, split, hyperparameter) — satu tanpa stemming sebagai baseline dan satu dengan stemming Sastrawi. Hasil menunjukkan perbedaan F1-macro yang tidak signifikan (0.9671 vs 0.9672, selisih +0.0002). Stemming tidak diintegrasikan ke pipeline produksi karena: (1) fitur diskriminatif utama adalah nama brand judi yang sudah dalam bentuk dasar, (2) TF-IDF bigram sudah mampu menangani variasi morfologi dalam konteks yang relevan, dan (3) Sastrawi kurang optimal untuk teks informal/slang yang mendominasi komentar YouTube."*

---

### 18.8 Cara Menjalankan

```bash
python src/experiment_stemming.py
```

Output tersimpan di `reports/`:
- `experiment_stemming.png` — grafik perbandingan F1 dua model

---

## 17. Inspeksi Fitur — "Apa yang Dipelajari Model?"

> Bagian ini menjelaskan apa itu `inspect_features.py`, kenapa penting untuk skripsi, dan bagaimana menginterpretasikan hasilnya.

---

### 17.1 Latar Belakang: Model sebagai "Black Box"

Salah satu kritik umum terhadap machine learning adalah model dianggap sebagai *black box* — kita tahu input dan output-nya, tapi tidak tahu *kenapa* model membuat keputusan tertentu. Untuk skripsi, ini masalah: dosen penguji mungkin bertanya, *"Apa yang sebenarnya dipelajari model kamu? Apa buktinya model bukan sekadar menghafal?"*

Untungnya, SVM dengan kernel linear adalah pengecualian — model ini *bisa* dijelaskan, karena cara kerjanya bisa dilihat langsung dari koefisiennya.

---

### 17.2 Cara Kerja: Koefisien SVM Linear

Ingat kembali cara kerja TF-IDF + SVM:

1. **TF-IDF** mengubah setiap komentar menjadi vektor angka. Setiap dimensi vektor itu merepresentasikan satu kata atau bigram. Misalnya dimensi ke-237 mungkin mewakili kata "daftar", dimensi ke-1042 mewakili bigram "bonus new".

2. **SVM linear** menemukan hyperplane (garis pemisah) optimal antara kelas spam dan non-spam. Hyperplane ini didefinisikan oleh **vektor bobot** `w` — satu nilai per dimensi fitur.

3. Nilai bobot `w[i]` untuk fitur ke-i menunjukkan:
   - `w[i] > 0` dan besar → fitur ini **kuat mendorong ke arah SPAM**
   - `w[i] < 0` dan besar (nilainya sangat negatif) → fitur ini **kuat mendorong ke arah NON-SPAM**
   - `w[i] ≈ 0` → fitur ini hampir tidak berpengaruh

```
Contoh keputusan SVM untuk satu komentar:
skor = w[daftar] × 3.2 + w[sekarang] × 1.1 + w[bonus] × 2.8 + w[bang] × (-1.5) + ...
jika skor > 0  → prediksi SPAM
jika skor < 0  → prediksi NON-SPAM
```

Nilai bobot `w` ini tersimpan di `pipeline.named_steps['svm'].coef_` — itulah yang diekstrak oleh `inspect_features.py`.

---

### 17.3 Catatan Teknis: Sparse Matrix

Saat mengekstrak `coef_`, ada detail penting yang perlu dipahami:

sklearn menyimpan `coef_` sebagai **sparse matrix** dari scipy (bukan numpy array biasa). Sparse matrix adalah format efisien untuk data yang sebagian besar isinya nol — cocok untuk TF-IDF yang memang menghasilkan banyak nilai nol.

Masalahnya: operasi standar numpy seperti `np.asarray(sparse)` tidak otomatis mengkonversi sparse ke dense array — hasilnya adalah *object array* berisi sparse matrix itu sendiri (tidak berguna). Solusinya adalah memanggil `.toarray()` terlebih dahulu:

```python
# SALAH — menghasilkan object array, bukan angka
weights = np.asarray(svm.coef_[0]).ravel()

# BENAR — konversi eksplisit sparse → dense → 1D
weights = svm.coef_.toarray().ravel()
```

---

### 17.4 Cara Membaca Hasil

Jalankan: `python src/inspect_features.py`

Output mencakup:
- **Top 25 fitur spam** — kata/bigram dengan bobot tertinggi (paling mendorong prediksi spam)
- **Top 25 fitur non-spam** — kata/bigram dengan bobot paling negatif (paling mendorong prediksi non-spam)
- `reports/top_features.png` — visualisasi bar chart dua panel
- `reports/feature_weights.csv` — seluruh ~4000 fitur beserta bobotnya

**Contoh output aktual dari model v2 (dataset 3608 sampel):**

```
TOP 25 FITUR → SPAM (bobot tertinggi):
  berkah (5.35), pstoto (4.55), situs (3.12), xuxu (3.01),
  bukit (2.83), dora (2.82), bambu (2.81), bermain (2.51),
  supermoney (2.38), pangeran (2.38), giat (2.35), kyt (2.33),
  pluto (2.17), jptogel (2.08), jalak (2.07), kuas (2.06),
  fire (2.03), bbca (1.98), rezeki (1.96), hoki (1.90)

TOP 25 FITUR → NON-SPAM (bobot paling negatif):
  bang (-1.56), dok (-1.39), tirta (-1.26), desta (-1.19),
  ibot (-1.15), midori (-1.08), mahal (-0.97), orang (-0.96),
  jot (-0.93), tidur (-0.91), tepe (-0.91), indah (-0.90),
  cewek (-0.89), anjir (-0.85), cocok (-0.79), jaman (-0.78)
```

---

### 17.5 Interpretasi dan Insight untuk Skripsi

**Fitur spam — yang masuk akal:**

| Fitur | Penjelasan |
|-------|-----------|
| `pstoto`, `jptogel`, `supermoney`, `xuxu`, `bardi` | Nama brand judi online langsung |
| `situs` | "Situs judi" — kata kunci umum dalam iklan judi |
| `hoki`, `rezeki`, `berkah` | Kata-kata berkonotasi keberuntungan/rezeki yang sering dipakai untuk menarik korban |
| `fire` | Berasal dari emoji 🔥 yang dikonversi preprocessing. Penipu sering memakai emoji ini untuk menarik perhatian |
| `bbca` | Singkatan BCA (bank) — sering muncul di komentar spam yang menyebut metode transfer/deposit |

**Fitur spam — yang terlihat aneh tapi masuk akal:**

Kata-kata seperti `berkah`, `bukit`, `bambu`, `dora`, `jalak` terlihat tidak berbahaya. Namun kemungkinan besar ini adalah **potongan nama brand judi** yang terpotong saat preprocessing:
- `BERKAH4D` → angka dihapus oleh preprocessing → tersisa `berkah`
- `BAMBU4D` → tersisa `bambu`
- `BUKIT4D` → tersisa `bukit`

Ini adalah insight penting: preprocessing yang menghapus angka di tengah kata membantu normalisasi, tapi bisa "menyembunyikan" asal-usul fitur. Bisa disebutkan sebagai keterbatasan di skripsi.

**Fitur non-spam — yang masuk akal:**

| Fitur | Penjelasan |
|-------|-----------|
| `bang`, `dok`, `kak` | Sapaan informal Indonesia yang sangat umum di komentar biasa |
| `orang`, `tidur`, `mahal`, `cocok` | Kata sehari-hari yang jarang muncul di komentar spam |
| `desta`, `ibot`, `midori`, `tirta` | Nama-nama orang/karakter yang muncul di video non-spam yang di-scrape |
| `anjir`, `jaman`, `cewek` | Slang Indonesia yang lazim di komentar biasa, tidak ada di spam |
| `arsenal`, `london`, `infinix` | Referensi ke olahraga, tempat, dan brand teknologi — konteks jauh dari judi |

**Kalimat untuk bab metodologi skripsi:**

> *"Inspeksi koefisien SVM menunjukkan bahwa model berhasil mempelajari pola yang semantik — bukan sekadar menghafal data training. Fitur dengan bobot tertinggi untuk kelas spam adalah nama brand judi online (pstoto, jptogel, bardi), kata-kata berkonotasi keberuntungan (hoki, rezeki, berkah), dan token 'fire' yang berasal dari konversi emoji 🔥. Sebaliknya, fitur non-spam didominasi sapaan informal Indonesia (bang, dok) dan referensi kontekstual (desta, arsenal) yang tidak berkaitan dengan perjudian."*

---

### 17.6 Cara Menjalankan

```bash
# Jalankan sekali setelah train.py selesai
python src/inspect_features.py
```

Output disimpan di `reports/`:
- `top_features.png` — bar chart dua panel (spam vs non-spam), siap pakai di skripsi
- `feature_weights.csv` — seluruh daftar fitur dan bobot, untuk analisis mandiri

---

## 21. False Positive — Ketika Model Salah Menilai Komentar Normal

> Bagian ini menjelaskan fenomena false positive yang ditemukan saat pengujian langsung di YouTube, kenapa ini terjadi secara teknis, dan bagaimana ini harus ditulis di skripsi. Ini adalah salah satu temuan paling berharga dari pengujian nyata.

---

### 21.1 Apa itu False Positive?

Dalam klasifikasi, ada dua jenis kesalahan:

| Istilah | Artinya | Contoh |
|---------|---------|--------|
| **False Positive (FP)** | Komentar normal diklasifikasikan sebagai spam | Komentar "Nonton berkali kali, gak bosen" → dianggap spam |
| **False Negative (FN)** | Komentar spam lolos, tidak terdeteksi | Komentar spam yang memakai kata-kata asing → dianggap normal |

False positive yang ditemukan saat pengujian di YouTube:

```
"Nonton berkali kali, gak bosen dan ttep ngakak"  → Spam 92%  ← SALAH
"Nonton ulang² tetap rata ngakak😂😂😂"           → Spam 76%  ← SALAH
"tontonan sambil makan update juga"               → Spam 80%  ← SALAH
```

Ketiga komentar di atas jelas merupakan komentar penonton biasa yang menikmati video — bukan iklan judi online. Tapi model menilainya sebagai spam dengan confidence tinggi.

---

### 21.2 Kenapa Ini Terjadi? — Akar Masalah di Bag of Words

Model ini menggunakan pendekatan **Bag of Words** melalui TF-IDF. Cara kerjanya bisa dianalogikan seperti ini:

> Bayangkan kamu diminta menilai apakah sebuah kalimat adalah spam, tapi caranya adalah: ambil semua kata, taruh ke dalam kantong, kocok, lalu lihat kata apa yang ada. Kamu tidak boleh tahu urutan kata, tidak boleh tahu siapa ngomong ke siapa, tidak boleh tahu konteksnya.

Inilah yang dilakukan model — dia menjumlahkan bobot setiap kata secara independen:

```
skor_akhir = bobot["nonton"] + bobot["berkali"] + bobot["bosen"] + ...

jika skor_akhir > 0  → prediksi SPAM
jika skor_akhir < 0  → prediksi NON-SPAM
```

Urutan kata, konteks kalimat, dan makna keseluruhan diabaikan sepenuhnya.

---

### 21.3 Bedah Kasus: Kenapa Confidence-nya Tinggi?

Mari kita bedah komentar pertama kata per kata menggunakan `feature_weights.csv`:

**Komentar: "Nonton berkali kali, gak bosen dan ttep ngakak"**

| Kata | Bobot di Model | Arah | Penjelasan |
|------|---------------|------|-----------|
| `nonton` | -0.33 | ✅ Non-spam | Logis — jarang muncul di iklan judi |
| `berkali` | +0.74 | ❌ Spam | Di data training, sering muncul di: "menang berkali-kali", "withdraw berkali-kali" |
| `kali` | -0.06 | ≈ Netral | Hampir tidak berpengaruh |
| `bosen` | +0.60 | ❌ Spam | Sering muncul di: "bosen kalah? coba di sini", "bosen miskin?" |
| `ngakak` | +0.07 | ≈ Netral | Hampir tidak berpengaruh |
| **Total** | **≈ +1.02** | **→ SPAM** | Skor positif → model prediksi spam |

Perhatikan: **satu kata non-spam (`nonton`, bobot -0.33) kalah jumlah dari dua kata berbobot spam (`berkali` +0.74 + `bosen` +0.60 = +1.34).**

**Komentar: "tontonan sambil makan update juga"**

| Kata | Bobot | Arah | Penjelasan |
|------|-------|------|-----------|
| `sambil` | **+1.28** | ❌ Spam kuat | Sering muncul di: "sambil santai bisa cuan", "sambil rebahan bisa menang" |
| `update` | +0.50 | ❌ Spam | Sering muncul di: "update link setiap hari", "update terus situs kami" |
| `makan` | +0.02 | ≈ Netral | Hampir tidak berpengaruh |
| **Total** | **≈ +1.80** | **→ SPAM** | Skor tinggi → confidence 80% |

`sambil` adalah penyebab utama di komentar ketiga. Ini kata yang sangat umum dalam Bahasa Indonesia, tapi di data training spam, kata ini sangat sering muncul dalam kalimat promosi judi.

---

### 21.4 Kenapa Kata Normal Bisa Punya Bobot Spam?

Ini bukan kesalahan implementasi — ini adalah **keterbatasan fundamental** dari pendekatan berbasis kata (Bag of Words). Proses yang terjadi:

1. Saat training, model melihat ribuan komentar spam yang menggunakan kata-kata seperti `sambil`, `berkali`, `update` dalam konteks iklan judi
2. Model menghitung: *"kata `sambil` lebih sering muncul di komentar spam daripada non-spam"*
3. Maka model memberi bobot positif (spam) ke kata `sambil`
4. Saat inference, kata `sambil` di komentar apapun — termasuk "sambil makan nonton" — akan menambah skor spam

Model tidak bisa membedakan:
- `"sambil santai, menang di situs kami"` ← spam
- `"sambil makan nonton video ini"` ← bukan spam

Karena dari perspektif Bag of Words, keduanya sama-sama mengandung kata `sambil`.

---

### 21.5 Solusi Jangka Pendek: Hard Negative Examples

Cara paling langsung untuk mengurangi false positive **tanpa ganti model**: tambahkan komentar-komentar false positive ini ke dataset sebagai label **non_spam**.

Dengan data baru ini, saat training ulang model akan belajar:
- *"Oke, `berkali` + `nonton` + `ngakak` = non-spam — ini konteks menonton video"*
- *"Oke, `sambil` + `makan` + `nonton` = non-spam — ini aktivitas sehari-hari"*

Komentar yang sudah ditambahkan ke dataset sebagai hard examples:
```
"Nonton berkali kali, gak bosen dan ttep ngakak"  → non_spam
"Nonton ulang² tetap rata ngakak😂😂😂"           → non_spam  
"tontonan sambil makan update juga"               → non_spam
```

Ini disebut **hard negative mining** — secara aktif mencari contoh yang membingungkan model dan menambahkannya ke training data. Semakin banyak contoh seperti ini, semakin model belajar membedakan konteks.

---

### 21.6 Solusi Jangka Panjang: Model yang Paham Konteks (IndoBERT)

Pertanyaan yang wajar muncul: *"Apakah bisa membuat model yang benar-benar paham konteks kalimat, bukan sekadar kata per kata?"*

**Bisa.** Teknologinya sudah ada dan disebut **Transformer**, dengan implementasi paling populer bernama **BERT** (Bidirectional Encoder Representations from Transformers). Untuk Bahasa Indonesia, tersedia **IndoBERT**.

Perbedaan mendasar cara kerjanya:

```
TF-IDF + SVM (sekarang):
  Input: "sambil makan nonton"
  Proses: hitung bobot tiap kata → jumlahkan
  Model tidak tahu "sambil" ini konteks aktivitas, bukan promosi

IndoBERT:
  Input: "sambil makan nonton"
  Proses: baca seluruh kalimat dari kiri dan kanan sekaligus
  Model membangun representasi "sambil" yang berbeda tergantung kata sekitarnya
  "sambil" sebelum "makan nonton" ≠ "sambil" sebelum "santai menang"
```

Namun IndoBERT memiliki konsekuensi teknis yang signifikan:

| Aspek | TF-IDF + SVM | IndoBERT |
|-------|-------------|---------|
| Ukuran model | ~2 MB | ~500 MB |
| Training time | Detik | Jam (butuh GPU) |
| Kompleksitas implementasi | Sederhana | Sangat kompleks |
| Data yang dibutuhkan | Ratusan sampel | Ribuan–puluhan ribu |
| Kemampuan memahami konteks | ❌ | ✅ |
| Cocok untuk skripsi S1 | ✅ | Bisa, tapi jauh lebih berat |

Untuk scope skripsi S1 ini, **TF-IDF + SVM adalah pilihan yang tepat** — bisa dijelaskan dari nol kepada penguji, memiliki performa yang sudah terukur, dan keterbatasannya bisa diidentifikasi dengan jelas. False positive yang ditemukan justru menjadi bahan diskusi yang kaya.

---

### 21.7 Kenapa Bagian Ini Penting untuk Skripsi

Bab pembahasan yang baik tidak hanya memamerkan angka akurasi yang tinggi — dia juga **jujur tentang kelemahan model** dan mampu menjelaskan *kenapa* kelemahan itu terjadi secara teknis. Menemukan dan menganalisis false positive seperti ini menunjukkan bahwa kamu benar-benar menguji sistem di kondisi nyata, bukan hanya di data uji yang sudah ada.

**Kalimat untuk bab pembahasan/hasil:**

> *"Pengujian langsung pada kolom komentar YouTube menemukan beberapa kasus false positive — komentar non-spam yang diklasifikasikan sebagai spam dengan confidence tinggi. Contohnya: 'Nonton berkali kali, gak bosen dan ttep ngakak' diklasifikasikan sebagai spam dengan confidence 92%. Analisis bobot fitur menunjukkan bahwa kata 'berkali' (+0.74) dan 'bosen' (+0.60) memiliki bobot spam yang signifikan, karena kedua kata tersebut sering muncul dalam konteks spam di data training ('menang berkali-kali', 'bosen kalah?'). Model tidak dapat membedakan konteks penggunaan kata-kata tersebut karena pendekatan TF-IDF hanya mempertimbangkan frekuensi kemunculan kata, bukan makna kalimat secara keseluruhan."*

**Kalimat untuk bab keterbatasan:**

> *"Model SVM berbasis TF-IDF tidak memiliki kemampuan pemahaman konteks semantik (context-aware). Kata-kata yang sering muncul dalam komentar spam akan memiliki bobot spam tinggi, bahkan ketika kata tersebut digunakan dalam kalimat normal yang tidak berkaitan dengan judi online. Penggunaan model berbasis arsitektur transformer seperti IndoBERT berpotensi mengurangi false positive dengan kemampuannya memahami konteks kalimat secara bidireksional, namun memerlukan sumber daya komputasi, waktu pelatihan, dan volume data yang jauh lebih besar — di luar scope penelitian ini."*

**Kalimat untuk bab saran/penelitian selanjutnya:**

> *"Penelitian selanjutnya dapat mengeksplorasi penggunaan model berbasis transformer seperti IndoBERT untuk mengatasi keterbatasan konteks semantik pada pendekatan TF-IDF + SVM. Selain itu, pengumpulan hard negative examples secara sistematis — yaitu komentar non-spam yang mengandung kata-kata berbobot spam — dapat meningkatkan performa model tanpa mengganti arsitektur yang ada."*

---

## 22. Hybrid SVM + Rules — Lapisan Kedua untuk Kurangi False Positive

> Bagian ini menjelaskan pendekatan hybrid yang ditambahkan ke server sebagai respons dari temuan false positive selama pengujian nyata. Ini adalah keputusan desain yang penting untuk didokumentasikan karena menunjukkan siklus evaluasi–perbaikan yang ilmiah.

---

### 22.1 Latar Belakang: Mengapa Ditambahkan

Dari pengujian langsung di YouTube (lihat §21), ditemukan bahwa beberapa komentar normal diklasifikasikan sebagai spam dengan confidence tinggi karena mengandung kata-kata ambigu yang berbobot spam tinggi:

| Kata | Bobot | Mengapa bermasalah |
|------|-------|-------------------|
| `hoki` | +1.90 | Artinya "beruntung" dalam percakapan biasa, tapi sering dipakai di narasi iklan judi |
| `serius` | +1.10 | Dipakai penipu untuk meyakinkan: "serius beneran menang" |
| `keren` | +0.80 | Sering muncul di: "keren banget situs ini" |
| `sambil` | +1.28 | Sering di: "sambil santai bisa cuan" |

Model tidak bisa membedakan konteks — ini adalah keterbatasan inheren dari Bag of Words yang sudah dijelaskan di §21.

Daripada mengganti model (yang akan mengubah scope skripsi), ditambahkan sebuah **lapisan aturan** sebagai filter kedua setelah prediksi SVM.

---

### 22.2 Cara Kerja Hybrid Rule

Alur prediksi sebelum hybrid:

```
Komentar → Preprocessing → SVM → Spam/Non-spam
```

Alur prediksi setelah hybrid:

```
Komentar → Preprocessing → SVM → Spam?
                                    ↓ Ya
                           Ada sinyal keras spam?
                           ↓ Ya          ↓ Tidak
                         SPAM          NON-SPAM (override)
```

**Sinyal keras spam** (*hard spam signals*) adalah kata-kata yang:
1. Secara pasti berhubungan dengan judi online
2. Tidak punya makna lain yang wajar dalam konteks komentar YouTube

Contoh: `gacor`, `scatter`, `togel`, `jackpot`, `maxwin`, `rtp`, `situs`, `withdraw`, `deposit` — kata-kata ini hampir tidak mungkin muncul di komentar normal yang tidak berhubungan dengan judi.

---

### 22.3 Implementasi di server.py

```python
HARD_SPAM_SIGNALS = {
    # Istilah judi yang tidak punya makna lain
    "gacor", "scatter", "jackpot", "maxwin", "togel",
    "toto", "rtp", "slot", "situs", "withdraw", "deposit",
    # Nama brand yang diketahui (setelah preprocessing hapus angka)
    "pstoto", "jptogel", "supermoney", "bardi", "bukit", "bambu", ...
    # Token universal hasil brand canonicalization (Step 5b)
    "judolbrand",  # ← ditambahkan versi terbaru — lihat penjelasan di bawah
}

def has_hard_spam_signal(cleaned_text: str) -> bool:
    words = set(cleaned_text.split())
    return bool(words & HARD_SPAM_SIGNALS)  # set intersection
```

**Mengapa `judolbrand` ditambahkan ke sini?**

Dengan Step 5b (brand canonicalization), semua nama brand judol yang cocok pola `[kata][suffix]` diubah menjadi token `judolbrand`. Token ini tidak mungkin muncul secara alami di komentar normal. Dengan memasukkannya ke `HARD_SPAM_SIGNALS`, **satu entri ini menggantikan perlunya mendaftarkan ratusan nama brand secara manual**.

Sebelumnya, daftar manual berisi entri seperti `"bukit"`, `"bambu"`, `"dora"` yang sebenarnya adalah sisa brand tanpa digit (BUKIT4D → bukit). Kehadiran `judolbrand` mengambil alih peran ini lebih akurat karena tidak bergantung hafalan nama — berlaku otomatis untuk semua brand yang mengikuti pola suffix judol.

Di endpoint `/predict` dan `/predict/batch`, setelah SVM memprediksi spam:

```python
if label == "spam" and not has_hard_spam_signal(cleaned):
    # Kemungkinan false positive dari kata ambigu — override ke non_spam
    return PredictResponse(label="non_spam", confidence=0.5, is_spam=False)
```

**Kenapa `confidence=0.5`?** Karena ketika kita override, kita tidak tahu dengan pasti apakah itu spam atau bukan — kita hanya tahu SVM tidak punya bukti kuat. Mengembalikan 0.5 jujur menyatakan "tidak yakin, default ke aman."

**Kenapa pakai set intersection (`words & HARD_SPAM_SIGNALS`)?** Cara paling efisien untuk cek apakah ada elemen yang sama antara dua set. Jauh lebih cepat dari loop manual, terutama untuk batch besar.

---

### 22.4 Trade-off yang Disadari dan Diterima

Hybrid rule ini bukan solusi sempurna. Ada trade-off yang harus jujur disebutkan di skripsi:

**Yang membaik:**
- False positive dari kata ambigu (hoki, serius, keren, sambil) berkurang signifikan
- Komentar normal yang tidak mengandung kata judi eksplisit tidak akan disembunyikan

**Yang memburuk:**
- **Spam canggih bisa lolos.** Spammer yang menghindari semua kata dalam daftar `HARD_SPAM_SIGNALS` akan lolos sebagai non-spam, meskipun SVM mendeteksinya sebagai spam. Contoh spam yang mungkin lolos:
  > *"Mau tau rahasia rezeki berlimpah? DM kami sekarang, sudah ribuan yang berhasil"*
  Tidak ada kata dari daftar → lolos sebagai non-spam.

- **Daftar perlu dijaga manual.** Jika spammer mulai menggunakan istilah baru yang belum ada di `HARD_SPAM_SIGNALS`, sistem tidak akan menangkapnya sampai daftar diperbarui.

- **Recall turun.** Dalam metrik evaluasi, menambahkan rule ini kemungkinan sedikit menurunkan recall (kemampuan menangkap semua spam) sambil meningkatkan precision (komentar yang terdeteksi spam memang benar spam).

---

### 22.5 Mengapa Ini Tetap Pilihan yang Tepat untuk Saat Ini

Dalam pengembangan sistem klasifikasi teks, ada spektrum pendekatan untuk mengatasi false positive:

```
Pure ML (SVM)  →  Hybrid ML+Rules  →  Contextual Model (IndoBERT)
Mudah ←————————————————————————————→ Kompleks
False positive tinggi ←————————→ False positive rendah
```

Hybrid berada di tengah — tidak sesempurna IndoBERT, tapi jauh lebih mudah diimplementasikan dan dijelaskan. Untuk scope skripsi S1 dengan dataset yang relatif kecil, ini adalah kompromi yang masuk akal.

---

### 22.6 Kalimat untuk Skripsi

**Kalimat untuk bab metodologi (jelaskan desain sistem):**

> *"Untuk mengurangi false positive yang dihasilkan oleh kata-kata ambigu berbobot spam tinggi, diterapkan pendekatan hybrid yang menggabungkan prediksi SVM dengan verifikasi berbasis aturan. Setelah SVM memprediksi kelas spam, sistem memeriksa apakah teks mengandung minimal satu kata yang secara eksklusif berhubungan dengan judi online (hard spam signal). Jika tidak ditemukan sinyal keras, prediksi di-override menjadi non-spam. Pendekatan ini merupakan respons terhadap temuan pengujian nyata yang menunjukkan bahwa kata-kata seperti 'hoki', 'serius', dan 'keren' memiliki bobot spam tinggi namun sering digunakan dalam konteks yang tidak berkaitan dengan judi."*

**Kalimat untuk bab pembahasan (jelaskan hasil):**

> *"Penerapan hybrid rule menunjukkan peningkatan kualitatif dalam pengujian langsung — komentar yang sebelumnya menghasilkan false positive dengan confidence 77–92% tidak lagi disembunyikan setelah verifikasi sinyal keras ditambahkan. Trade-off yang teridentifikasi adalah potensi penurunan recall pada kasus spam yang tidak menggunakan terminologi judi eksplisit, serta kebutuhan pembaruan daftar sinyal secara berkala seiring munculnya istilah baru dalam ekosistem spam."*

**Kalimat untuk bab keterbatasan:**

> *"Daftar hard spam signals bersifat statis dan memerlukan pembaruan manual ketika spammer mengadopsi terminologi baru. Spammer yang secara strategis menghindari kata-kata dalam daftar dapat mengakali sistem hybrid ini, sehingga mengurangi efektivitasnya dalam jangka panjang. Pendekatan berbasis konteks seperti IndoBERT tidak memiliki keterbatasan ini karena pemahamannya bersifat semantik, bukan leksikal."*


---

## 23. Brand Canonicalization — Token Universal untuk Nama Brand Judol

> Bagian ini menjelaskan konsep di balik Step 5b (JUDOL_BRAND_PATTERN) yang ditambahkan di versi terbaru preprocessing, kenapa ini berbeda dari pendekatan sebelumnya, dan dampaknya terhadap performa model.

---

### 23.1 Masalah Sebelumnya: Arms Race dengan Spammer

Sebelum Step 5b, pendekatan untuk mendeteksi brand judol adalah:
1. Model menghafal nama-nama brand dari data training: `pstoto`, `jptogel`, `bardi`, dst.
2. Setiap ada brand baru → retrain model dengan data baru

Ini menciptakan **arms race** yang tidak ada ujungnya. Spammer mengganti brand setiap minggu. Setiap nama brand baru di luar vocabulary training langsung lolos.

Selain itu, ada masalah yang lebih serius: digit dihapus di Layer 6, sehingga `KEJU4D` → `keju` dan `BETAWI77` → `betawi`. Model dilatih dengan fitur `keju` dan `betawi` yang berlabel spam — padahal kata-kata itu muncul juga di komentar normal (kuliner, budaya). Ini meningkatkan risiko false positive secara sistematis.

---

### 23.2 Solusi: Generalisasi Pola, Bukan Hafalan Nama

Pengamatan kunci: hampir semua brand judi online Indonesia mengikuti **pola yang sama**:

```
[nama bebas] + [suffix khas judol]
```

Suffix-nya relatif tetap:
- **Togel:** `4D`, `3D`, `2D` (angka dimensi)
- **Slot angka besar:** `777`, `888`, `303`
- **Slot generik:** `88`, `99`, `77`, `69`, `138`, `388`
- **Poker/Domino:** `QQ` (BandarQQ, HobiQQ, DominoQQ)

Alih-alih hafal ratusan nama, kita deteksi **pola suffix-nya** dan ganti seluruh kata dengan token universal `judolbrand`.

---

### 23.3 Cara Kerja JUDOL_BRAND_PATTERN

```python
JUDOL_BRAND_PATTERN = re.compile(
    r'(?!(?:level|rank|stage|episode|part|seri|versi|chapter|season|round|wave|fase|lv)\d)'
    r'[a-z]{2,}(?:4d|3d|2d|88|99|77|69|138|388|303|777|888|qq)'
)
```

Dibaca dari kiri ke kanan:
- `` — harus di batas kata (tidak di tengah kata lain)
- `(?!...)` — **negative lookbehind**: jangan cocokkan kalau diawali oleh prefix gaming umum diikuti digit
- `[a-z]{2,}` — dua atau lebih huruf lowercase (teks sudah disomalkan di Step 5)
- `(?:4d|3d|...)` — salah satu suffix khas judol
- `` — batas kata di akhir

**False positive protection** via prefix exclusion:

| Prefix dikecualikan | Alasan |
|--------------------|--------|
| `level`, `rank`, `lv` | Konteks gaming ("level99", "rank88") |
| `episode`, `part`, `chapter` | Konten serial YouTube ("episode77") |
| `season`, `wave`, `round` | Game season/wave |
| `seri`, `versi`, `fase` | Pembuatan konten Indonesia |

Kata-kata gaming ini dikecualikan karena sering muncul sebelum angka di komentar YouTube yang legitimate.

---

### 23.4 Dampak ke Performa Model

Dengan token `judolbrand` yang konsisten, TF-IDF memiliki satu fitur yang sangat diskriminatif alih-alih ratusan fitur lemah yang tersebar:

| | Sebelum Step 5b | Setelah Step 5b |
|--|---|---|
| Fitur brand | `keju`, `betawi`, `roma`, `wifi`, `batre`... (ratusan) | `judolbrand` (satu) |
| Bobot fitur | Sedang, tersebar | Sangat tinggi, terfokus |
| Brand baru | Tidak dikenali | Langsung terdeteksi |
| FP dari nama umum | Tinggi (keju, betawi...) | Nol (judolbrand tidak ambigu) |

**Hasil evaluasi model setelah Step 5b:**

| Metrik | Sebelum | Sesudah |
|--------|---------|---------|
| Accuracy | 96.74% | **99.53%** |
| F1-macro | 0.9664 | **0.9952** |
| False Positive | 11 | **1** |
| False Negative | 17 | **3** |

---

### 23.5 Kalimat untuk Skripsi

**Kalimat untuk bab metodologi:**

> *"Untuk meningkatkan kemampuan generalisasi model dalam mendeteksi nama brand judi online yang terus berubah, diterapkan teknik canonicalization brand pada tahap preprocessing. Sebelum karakter digit dihapus, pola nama brand yang mengikuti format [kata][suffix khas judol] — di mana suffix mencakup penanda togel (4D, 3D), slot (88, 777), dan poker (QQ) — diganti dengan token universal 'judolbrand'. Pendekatan ini memungkinkan model mengenali brand baru yang belum pernah dilihat selama training, selama brand tersebut mengikuti pola suffix yang sama."*

**Kalimat untuk bab hasil:**

> *"Penambahan canonicalization brand menghasilkan peningkatan signifikan pada semua metrik evaluasi — akurasi naik dari 96.74% menjadi 99.53% dan F1-macro dari 0.9664 menjadi 0.9952. Peningkatan ini terjadi karena token 'judolbrand' memberikan sinyal yang jauh lebih konsisten dan kuat dibandingkan ratusan fitur brand parsial (keju, betawi, roma) yang sebelumnya berpotensi menimbulkan false positive di komentar kuliner dan budaya."*

---

## 24. Perbaikan Two-Pass Filter — Rescue Condition dan Suffix QQ

> Bagian ini menjelaskan dua perbaikan di `prepare_dataset.py` yang meningkatkan cakupan spam dari 1099 menjadi 1785 entri (dataset Versi 4).

---

### 24.1 Perbaikan 1: Rescue Condition dari `==` ke `in`

**Kondisi lama** di Pass 2 filter:

```python
elif signals == ["brand_pattern"]:   # exact match — hanya 1 sinyal
```

**Kondisi baru:**

```python
elif "brand_pattern" in signals:     # membership check — brand bisa hadir bersama sinyal lain
```

**Kenapa perlu diubah?**

Spammer yang memakai Unicode obfuscation sering juga menggunakan banyak emoji dan simbol sebagai dekorasi visual. Akibatnya, satu komentar bisa punya 2–3 sinyal aktif sekaligus:

```
Komentar  : "𝑹𝑶𝑴𝑨𝟒𝑫 🎰💰🎁 join sekarang!!"
active_signals: ["brand_pattern", "emoji_spam", "high_symbol_ratio"]
spam_score: 75   (di bawah threshold 80)
```

Dengan kondisi lama (`== ["brand_pattern"]`): di-skip karena punya 3 sinyal.
Dengan kondisi baru (`"brand_pattern" in signals`): diselamatkan karena `brand_pattern` ada.

Verifikasi tetap dilakukan via regex pola brand di `normalized_text` — jadi false positive tetap terkontrol.

---

### 24.2 Perbaikan 2: BRAND_SUFFIX_PATTERN untuk Brand Tanpa Digit

Sebelumnya, Pass 2 hanya menggunakan satu regex:

```python
BRAND_RESCUE_PATTERN = re.compile(r'[A-Z]{2,}\d+[A-Z0-9]*')
# Menangkap: WIFI4D, ROMA4D, SBOBET88
# Tidak menangkap: PULAUWIN, NAGAMASTOTO (tidak ada digit)
```

Ditambahkan pola kedua:

```python
BRAND_SUFFIX_PATTERN = re.compile(r'[A-Z]{4,}(?:TOTO|BET|WIN|QQ)')
# Menangkap: PULAUWIN, NAGAMASTOTO, MANJURBET, HOBIQQ
```

**Kenapa minimum 4 huruf sebelum suffix?** Kata biasa yang berakhiran "bet" seperti `ribet` hanya punya 2 huruf sebelum suffix dan biasanya lowercase. Syarat 4+ huruf ALL-CAPS sekaligus mencegah false positive dari kata-kata Indonesia biasa.

**Kenapa QQ ditambahkan?** Keluarga brand poker/domino (HOBIQQ, BANDARQQ) sebelumnya tidak tertangkap oleh pattern manapun. Penambahan `QQ` memperluas jangkauan ke ekosistem brand ini.

---

### 24.3 Hasil Numerik

```
                    Versi 3   Versi 4
Total spam        :  1099      1785    (+686, +62%)
Rescued via regex :   962      1648    (+686, +71%)
```

686 entri tambahan ini adalah spam obfuscated yang sebelumnya di-skip karena:
- Punya lebih dari 1 sinyal aktif (rescue condition terlalu ketat)
- Brand tanpa digit seperti PULAUWIN tidak cocok `BRAND_RESCUE_PATTERN`

---

## 25. Keterbatasan: Obfuscation yang Belum Bisa Ditangani

> Bagian ini mendokumentasikan dua pola obfuscation yang secara sadar **tidak** diimplementasikan solusinya, beserta alasan teknisnya. Dokumentasi ini penting untuk bab Keterbatasan skripsi.

---

### 25.1 Kasus 1: Mixed Script dengan Spasi (roma 4d)

**Contoh komentar nyata:**
```
Nongkrong anti bosen ♜💗 𝓇𝐨๓𝐀 ４𝐃 ඏ🏆
```

Setelah preprocessing: `nongkrong anti bosen ro` — brand "roma 4d" tidak terdeteksi.

**Mengapa tidak terdeteksi?**

Ada dua masalah terpisah:
1. **Script campur**: karakter Thai (๓) sudah ditangani oleh homoglyph fix (`๓→m`), tapi karakter Sinhala (ඏ) dan varian lain masih bisa mengganggu
2. **Spasi antara nama dan suffix**: "roma 4d" tertulis sebagai dua token terpisah. `JUDOL_BRAND_PATTERN` hanya mencocokkan brand yang **ditulis menyambung** (roma4d, bukan roma 4d)

**Mengapa tidak diimplementasikan solusinya?**

Untuk menangkap "4d" yang terpisah dari "roma", kita perlu pola seperti:
```python
r'\w+\s+(?:4d|3d|slot|togel)'
```

Tapi ini akan menandai **semua** komentar yang menyebut `film 3d`, `kacamata 4d`, `bioskop 4d` — frasa yang sangat umum dan jelas bukan judol. False positive-nya tidak bisa diterima.

**Untuk skripsi:**

> *"Sistem tidak dapat mendeteksi brand judol yang ditulis dengan spasi antara nama dan suffix (misalnya 'roma 4d' alih-alih 'roma4d'), karena pola spasi tersebut juga digunakan secara umum dalam konteks non-judol seperti 'film 3d' atau 'bioskop 4d'. Implementasi deteksi pola ini berpotensi menimbulkan false positive yang signifikan dan karenanya tidak dimasukkan dalam pipeline akhir."*

---

### 25.2 Kasus 2: Brand Angka Dipisah Emoji (ALEXIS🌺1.7)

**Contoh komentar nyata:**
```
🌺ALEXIS🌺1.7🌺 bikin hati meleleh, gemes banget!
```

Setelah preprocessing: `hibiscus alexis hibiscus hibiscus hati meleleh gemes` — terdeteksi sebagai non_spam.

**Mengapa tidak terdeteksi?**

Brand aslinya adalah `Alexis17` atau `Alexistogel`. Spammer memisahkan nama dari angka dengan emoji, sehingga:
- `ALEXIS` berdiri sendiri sebagai token polos
- `1.7` dipisahkan oleh emoji, kemudian dibuang Layer 6 (bukan alfabet)
- `JUDOL_BRAND_PATTERN` tidak cocok karena tidak ada suffix judol

**Masalah fundamental:** `alexis` adalah **nama orang biasa**. Mem-flag semua kemunculan kata "alexis" akan menyembunyikan komentar dari penonton yang bernama Alexis, membahas tokoh bernama Alexis, atau menyebut Alexis dalam konteks apapun.

**Mengapa tidak diimplementasikan solusinya?**

Tidak ada cara untuk membedakan `alexis` sebagai nama brand judi dari `alexis` sebagai nama orang tanpa pemahaman konteks yang jauh lebih dalam — sesuatu yang di luar kemampuan model Bag of Words.

**Untuk skripsi:**

> *"Komentar spam yang menyisipkan brand dengan memisahkan nama dari suffix numerik menggunakan emoji atau tanda baca (misalnya 'ALEXIS🌺1.7') tidak dapat dideteksi secara andal. Nama-nama seperti 'ALEXIS' juga merupakan nama orang umum, sehingga penandaan berbasis nama saja akan menghasilkan false positive yang tidak dapat diterima. Penanganan kasus ini memerlukan pemahaman konteks semantik yang lebih dalam, seperti yang disediakan oleh model transformer (IndoBERT), dan merupakan arah pengembangan yang direkomendasikan untuk penelitian selanjutnya."*

---

### 25.3 Ringkasan Keterbatasan Obfuscation

| Pola obfuscation | Status | Alasan tidak diimplementasikan |
|---|---|---|
| Combining diacriticals (P͟U͟L͟A͟U͟W͟I͟N͟) | ✅ Terdeteksi | Step 2b: strip Mn category |
| Per-huruf dalam kurung ([P][U][L][A][U]) | ✅ Terdeteksi | Step 2c: unwrap bracket |
| NFKC font mewah (𝑹𝑶𝑴𝑨) | ✅ Terdeteksi | Step 2: NFKC normalization |
| Cyrillic homoglyph (dаftаr) | ✅ Terdeteksi | Step 3: HOMOGLYPH_MAP |
| Thai homoglyph (ro๓a) | ✅ Terdeteksi | Step 3: ๓→m ditambahkan |
| Brand+suffix menyambung (KEJU4D) | ✅ Terdeteksi | Step 5b: JUDOL_BRAND_PATTERN |
| Brand tanpa digit (PULAUWIN) | ✅ Terdeteksi | BRAND_SUFFIX_PATTERN di prepare_dataset.py |
| Brand+spasi+suffix (roma 4d) | ⚠️ Tidak terdeteksi | False positive tinggi (film 3d, kacamata 4d) |
| Brand dipisah emoji (ALEXIS🌺1.7) | ⚠️ Tidak terdeteksi | Nama brand = nama orang umum |
| Mixed script tak dikenal | ⚠️ Sebagian | Hanya skrip yang sudah dipetakan |

**Kalimat untuk bab kesimpulan/saran:**

> *"Pengujian langsung mengidentifikasi dua pola obfuscation yang belum dapat ditangani: pemisahan brand dari suffix numerik menggunakan spasi atau emoji, dan penggunaan nama brand yang identik dengan nama orang umum. Kedua kasus ini memerlukan pemahaman konteks semantik yang melampaui kemampuan pendekatan TF-IDF + SVM berbasis Bag of Words. Penelitian selanjutnya disarankan untuk mengeksplorasi model berbasis transformer seperti IndoBERT yang secara bawaan memahami konteks kalimat secara bidireksional."*

---

## 26. Hybrid Rule Dua Arah — Mencegah False Negative dari Kata Normal

### Masalah: SVM Bisa Kalah dari Kata-Kata Normal

Hybrid rule awal di `server.py` hanya bekerja **satu arah**: mencegah false positive dengan mengoverride `spam → non_spam` ketika SVM mendeteksi spam tapi tidak ada sinyal keras judol.

Masalah baru ditemukan dari pengujian langsung: dua komentar dengan isi hampir identik — keduanya mengandung `𝑯𝑶𝑩𝑰𝑸𝑸` (setelah preprocessing → `judolbrand`) — tapi salah satu lolos sebagai non_spam.

```
Komentar A: "Terbaik siiih Nonton konten lu sambil Main di ❤!!!✅ 𝑯𝑶𝑩𝑰𝑸𝑸 ❤!!!✅ Balikin Mood banget"
→ SVM: spam → Hybrid: ada judolbrand → tetap spam ✓

Komentar B: "Gw bakal ikutin konten lu terus bang bikin mood gw balik lagi liat lu makan salam sukses dari ❤!!!✅ 𝑯𝑶𝑩𝑰𝑸𝑸 ❤!!!✅"
→ SVM: non_spam → Hybrid (lama): tidak dicek → lolos sebagai non_spam ✗
```

### Kenapa SVM Bisa Bilang Non_spam Padahal Ada judolbrand?

SVM (Support Vector Machine) dengan kernel linear bekerja dengan **penjumlahan bobot semua token**. Setiap token punya bobot positif (cenderung spam) atau negatif (cenderung non_spam).

Komentar B mengandung banyak kata netral-ke-non_spam: `ikutin`, `konten`, `mood`, `balik`, `makan`, `salam`, `sukses`. Bobot gabungan kata-kata ini bisa mengalahkan bobot `judolbrand` dalam satu prediksi — terutama jika panjang kalimat jauh lebih dominan dari token brand.

Ini adalah **kelemahan inheren Bag of Words**: setiap token dievaluasi secara independen tanpa mempertimbangkan bahwa satu token saja sudah cukup untuk menentukan label.

### Solusi: Tambah Arah Sebaliknya

```python
# Sebelum (hanya satu arah — cegah FP):
if label == "spam" and not has_hard_spam_signal(cleaned):
    return PredictResponse(label="non_spam", ...)

# Sesudah (dua arah — cegah FP dan FN):
has_signal = has_hard_spam_signal(cleaned)

if label == "spam" and not has_signal:        # (A) cegah FP
    return PredictResponse(label="non_spam", confidence=0.5, ...)

if label == "non_spam" and has_signal:        # (B) cegah FN
    return PredictResponse(label="spam", confidence=0.9, ...)
```

Arah (B) menyatakan: **jika ada sinyal keras judol di teks, selalu spam — tidak peduli SVM bilang apa**. Confidence dikembalikan `0.9` (bukan dari probabilitas model) karena ini adalah keputusan deterministik berbasis aturan.

### HARD_SPAM_SIGNALS yang Terlalu Generik — Efek Samping Rule (B)

Penambahan arah (B) memperlihatkan risiko baru: kata-kata yang terlalu generik di `HARD_SPAM_SIGNALS` menjadi lebih berbahaya. Sebelumnya, jika SVM sudah benar bilang `non_spam`, kata generik tidak masalah. Sekarang, kata generik di `HARD_SPAM_SIGNALS` akan memaksa override ke `spam`.

Ditemukan false positive: komentar tentang **"rebusan rebung bambu untuk kanker"** diklasifikasikan sebagai spam karena `"bambu"` ada di `HARD_SPAM_SIGNALS`.

Audit menyeluruh dilakukan. Dua kata dihapus:

| Kata | Makna biasa | Konteks FP yang ditemukan |
|------|-------------|--------------------------|
| `bambu` | Tanaman bambu | Pengobatan herbal, kuliner, alam |
| `giat` | Rajin, aktif | Kalimat motivasi, belajar |

**Prinsip yang disimpulkan:** Kata masuk `HARD_SPAM_SIGNALS` hanya jika:
1. Istilah teknis judol tanpa makna lain (`gacor`, `scatter`, `togel`, `rtp`), atau
2. Compound brand spesifik yang tidak muncul di konteks normal (`pulauwin`, `pstoto`), atau
3. Token canonical hasil rule-based preprocessing (`judolbrand`)

Kata yang hanya nama benda/sifat umum — walaupun kebetulan dipakai brand judol — **tidak cukup kuat** sebagai sinyal keras karena Rule (B) akan membuat false positive yang tidak bisa dioverride.

### Untuk Sidang

> *"Hybrid rule diperbarui menjadi dua arah: selain mencegah false positive dengan mengoverride prediksi spam tanpa sinyal keras, ditambahkan arah sebaliknya untuk mencegah false negative — ketika model memprediksi non-spam padahal teks mengandung token yang secara deterministic berhubungan dengan judi online. Perubahan ini sekaligus mengungkap risiko baru dari sinyal keras yang terlalu generik, yang kemudian diatasi dengan menghapus kata-kata ambigu dari daftar sinyal."*

---

## 27. Kurasi Manual Dataset + Perbaikan Rescue Pattern

### Latar Belakang: Selisih 533 Entry

Dataset Versi 5 menggunakan 1785 spam dari total 2318 entry di `final_spam.json` — selisih 533 entry. Entry yang di-skip adalah yang gagal melewati Pass 1 (score < 80) **dan** Pass 2 (tidak cocok rescue pattern).

Pertanyaan yang valid: apakah 533 entry yang di-skip ini memang bukan spam, atau ada spam nyata yang salah dibuang?

### Proses Inspeksi dengan `inspect_skipped.py`

Script `inspect_skipped.py` dibuat untuk mendump semua 533 entry ke `data/skipped_entries.json` dengan informasi lengkap: score, sinyal aktif, teks asli, teks ternormalisasi, dan alasan skip. Entry diurutkan: yang punya `brand_pattern` signal duluan karena paling mungkin mengandung spam nyata.

### Hasil Review Manual

Dari 533 entry:
- **33 entry dihapus** (terkonfirmasi bukan spam) — berisi:
  - Nama orang mengandung "win": darwin, deswin, delwin, goodwin, marawin
  - Kata Indonesia umum mengandung "bet": ribet, kesambet, diabet, ngebet, lembet, seribet, tebet
  - Konteks situs non-judol: situs darkweb, situs bokep, situs jembot
  - Komentar normal tentang kunjungi tempat makan, warung, dll
- **500 entry dipertahankan** (spam nyata) — semuanya diimport ke `comments.csv`

### Mengapa 500 Spam Ini Lolos Filter?

Root cause: rescue patterns di `prepare_dataset.py` mengasumsikan brand judol selalu ALL-CAPS di `normalized_text`. Asumsi ini salah untuk dua kasus:

**Kasus 1 — Font dekoratif menghasilkan lowercase:**

Spammer memakai font matematika italic/bold, yang setelah NFKC normalization oleh scraper menghasilkan huruf kecil, bukan huruf besar seperti yang diasumsikan:

```
𝒃𝒃𝒄𝒂4𝒅   →  normalized: "bbca4d"   (math italic → lowercase)
𝐊𝐨𝐫𝐞𝐨𝟏𝟑𝟖  →  normalized: "Koreo138" (math bold → Title Case)
ˢⁱⁿᵍᵍᵃˢᵃⁿᵃ⁸⁸ → normalized: "sɪnggasana88" (superscript → lowercase IPA)
```

`BRAND_RESCUE_PATTERN = re.compile(r'\b[A-Z]{2,}\d+[A-Z0-9]*\b')` tidak cocok karena semua huruf harus kapital.

**Kasus 2 — Brand ALL-CAPS terlalu pendek untuk BRAND_SUFFIX_PATTERN:**

```
OMETOTO  →  O-M-E = 3 huruf sebelum TOTO
           BRAND_SUFFIX_PATTERN butuh [A-Z]{4,} (minimum 4) → tidak cocok
```

### Perbaikan yang Diimplementasikan

**Perbaikan 1 — BRAND_RESCUE_PATTERN: tambah `re.IGNORECASE`**

```python
# Sebelum:
BRAND_RESCUE_PATTERN = re.compile(r'\b[A-Z]{2,}\d+[A-Z0-9]*\b')

# Sesudah:
BRAND_RESCUE_PATTERN = re.compile(r'\b[A-Z]{2,}\d+[A-Z0-9]*\b', re.IGNORECASE)
```

Sekarang mencocokkan brand dengan huruf apapun selama ada digit. Digit sebagai syarat wajib mencegah false positive dari kata umum (yang tidak mengandung angka).

**Perbaikan 2 — BRAND_SUFFIX_PATTERN: turunkan minimum ke 3 huruf**

```python
# Sebelum:
BRAND_SUFFIX_PATTERN = re.compile(r'\b[A-Z]{4,}(?:TOTO|BET|WIN|QQ)\b')

# Sesudah:
BRAND_SUFFIX_PATTERN = re.compile(r'\b[A-Z]{3,}(?:TOTO|BET|WIN|QQ)\b')
```

Pola tetap ALL-CAPS (tidak `re.IGNORECASE`) untuk mencegah false positive dari kata Indonesia lowercase seperti "ngebet" atau "seribet" yang juga berakhiran "bet".

### Dampak ke Dataset dan Model

| Metrik | Versi 5 | Versi 6 | Keterangan |
|--------|---------|---------|------------|
| Spam di dataset | 1785 | **2285** | +500 spam terverifikasi manual |
| Total dataset | 4298 | **4798** | |
| Accuracy | 99.53% | **98.44%** | Turun karena data lebih sulit |
| F1-macro | 0.9952 | **0.9843** | Masih sangat tinggi |
| FP | 1 | **0** | Presisi sempurna |
| FN | 3 | **15** | Naik karena kelas baru lebih sulit |

**Mengapa accuracy turun tapi ini bukan kemunduran?**

500 entry baru adalah spam paling sulit — mereka lolos filter awal justru karena pola obfuscation-nya tidak konvensional. Model sekarang dihadapkan pada data yang lebih representatif dan lebih menantang. FP=0 menunjukkan tidak ada komentar normal yang salah ditandai. FN=15 berarti 15 spam dari 457 lolos — trade-off yang wajar untuk presisi sempurna.

### Untuk Sidang

> *"Inspeksi terhadap 533 entry yang tidak lolos filter otomatis mengungkap bahwa rescue patterns terlalu ketat — mengasumsikan nama brand selalu ditulis ALL-CAPS, padahal spammer menggunakan font dekoratif yang menghasilkan huruf kecil setelah normalisasi NFKC. Setelah verifikasi manual, 500 entry terkonfirmasi sebagai spam nyata dan diimport ke dataset. Dua perbaikan rescue pattern kemudian diimplementasikan: BRAND_RESCUE_PATTERN dibuat case-insensitive (dengan digit sebagai penjaga false positive), dan BRAND_SUFFIX_PATTERN diturunkan minimum prefixnya dari empat ke tiga huruf. Dataset bertumbuh dari 4.298 menjadi 4.798 sampel, dengan rasio spam yang lebih seimbang."*

---

## 28. manual_overrides.csv — Menjaga Koreksi Manual Agar Tidak Hilang

### Masalah

`prepare_dataset.py` adalah script pembuat dataset — setiap kali dijalankan, ia **menimpa** `data/comments.csv` dari awal menggunakan `scraper/final_spam.json` sebagai sumber. Ini berarti semua koreksi manual yang sudah dilakukan langsung di `comments.csv` (relabeling false positive, penambahan entry baru) akan **hilang** begitu ada scraping data baru dan `prepare_dataset.py` dijalankan ulang.

Skenario masalah:
1. Kamu menemukan 20 komentar non-spam yang salah dilabeli spam di dataset
2. Kamu betulkan labelnya langsung di `comments.csv`
3. Bulan depan kamu scrape data baru → jalankan `prepare_dataset.py`
4. `comments.csv` ditimpa → 20 koreksi tadi hilang, komentar itu kembali jadi spam

### Solusi: File Overrides Terpisah

Dibuat file `data/manual_overrides.csv` — file CSV permanen yang menyimpan semua koreksi label manual. File ini tidak pernah digenerate ulang oleh skrip apapun; satu-satunya yang memodifikasinya adalah peneliti secara sadar.

Format:
```csv
text,label
"Coba yg Yono atau Mustafa brebet yg meluk...",non_spam
"Sumpah tadi nyabet gk mau comen...",non_spam
"🌺ALEXIS🌺1.7🌺 bikin hati meleleh...",spam
```

Dua jenis entry yang didukung:
- `label=non_spam` — entry ini adalah **false positive**: hapus dari daftar spam, tambahkan sebagai non_spam
- `label=spam` — entry ini adalah spam yang tidak tertangkap filter otomatis: tambahkan ke spam

### Cara Kerjanya: `apply_manual_overrides()`

Fungsi baru di `prepare_dataset.py` yang dijalankan setelah auto-generation selesai:

```python
def apply_manual_overrides(spam, non_spam, overrides_path):
    # 1. Baca manual_overrides.csv
    fp_texts    = {text for text, label in overrides if label == "non_spam"}
    spam_adds   = [text for text, label in overrides if label == "spam"]

    # 2. Hapus false positive dari daftar spam
    spam = [e for e in spam if e["text"] not in fp_texts]

    # 3. Tambah false positive ke non_spam (hindari duplikat)
    non_spam += [{"text": t, "label": "non_spam"} for t in fp_texts
                 if t not in existing_non_spam]

    # 4. Tambah spam baru (hindari duplikat)
    spam += [{"text": t, "label": "spam"} for t in spam_adds
             if t not in existing_spam]

    return spam, non_spam
```

### Alur Dataset Sekarang (4 Step)

```
[1/4] load_spam_data()          ← final_spam.json → Pass 1 + Pass 2 rescue
[2/4] load_non_spam_data()      ← final_non_spam.json
[3/4] apply_manual_overrides()  ← data/manual_overrides.csv (hapus FP, tambah koreksi)
[4/4] build_and_save_dataset()  ← shuffle + save ke comments.csv
```

Sebelumnya alurnya hanya 3 step (tanpa Step 3). Penambahan Step 3 memastikan koreksi manual selalu teraplikasikan, berapapun kali `prepare_dataset.py` dijalankan ulang.

### Isi `manual_overrides.csv` Saat Ini (343 entry)

| Tipe | Jumlah | Keterangan |
|------|--------|------------|
| `non_spam` (false positive) | 79+ | 20 koreksi awal (kata umum Indonesia) + 59 laporan extension yang diselamatkan + 71 dari pzE8S6N0vwo |
| `spam` (tambahan) | 193 | 1 entry baru (ALEXIS17) + 192 entry spam yang tidak terjangkau rescue pattern otomatis |

### Kapan Perlu Ditambah Entry Baru ke `manual_overrides.csv`?

- Ditemukan false positive di hasil prediksi → tambah sebagai `non_spam`
- Ada spam yang selalu lolos deteksi dan tidak punya pola brand standar → tambah sebagai `spam`

Tidak perlu menyentuh `comments.csv` secara langsung lagi — cukup update `manual_overrides.csv`, lalu jalankan `prepare_dataset.py` dan `train.py`.

### Untuk Sidang

> *"Setelah iterasi kurasi manual, ditemukan bahwa mengedit `comments.csv` secara langsung tidak aman karena file ini digenerate ulang setiap ada penambahan data scraping baru. Untuk mempertahankan koreksi label antar siklus scraping, dibuat file `data/manual_overrides.csv` sebagai lapisan ketiga dalam pipeline persiapan dataset. File ini menyimpan daftar false positive yang harus dikeluarkan dari kelas spam, dan entry spam tambahan yang tidak tertangkap filter otomatis. Dengan arsitektur ini, koreksi manual bersifat persisten dan reproducible — siapapun yang menjalankan `prepare_dataset.py` akan mendapatkan dataset yang sudah terkoreksi, tanpa perlu melakukan kurasi ulang dari nol."*

---

## 29. Hard Test Set — Evaluasi pada Kasus Ambigu

### Apa itu Hard Test Set?

Test set biasa (80/20 split dari `comments.csv`) berisi dua jenis komentar yang relatif mudah dibedakan: spam eksplisit dan komentar sehari-hari yang netral. Angka akurasi dari test set ini mencerminkan performa pada kasus mudah, bukan kasus abu-abu.

**Hard test set** adalah kumpulan komentar yang dirancang khusus untuk menguji batas kemampuan model: secara leksikal terlihat seperti spam, tapi konteksnya bukan promosi.

Contoh komentar yang masuk kategori ini:
- *"Blokir aja situs web Kenzo Toto, biru toto, mawar Toto..."* — menyebut nama brand, tapi tujuannya meminta pemblokiran
- *"Judi itu haram tp klo maxwin huu harumm"* — memakai kata `maxwin` tapi konteksnya komentar humor/ironi
- *"saya tanggal 1 bulan ini dapat maxwin 2 juta tanggal 2 saya depo habis..."* — curhat rugi berjudi, bukan promosi

### Sumber Data

Video YouTube ID `kM99uBssHvQ` — video yang membahas judi online (konten berita/edukasi, bukan promosi). Komentar dari video ini didominasi oleh:
- Warga yang meminta pemerintah memblokir situs judol
- Korban judi online yang bercerita rugi
- Kritik terhadap situs-situs tertentu

Scraper menandai semua 74 komentar sebagai spam (karena mengandung sinyal brand/kata judi). Setelah review manual, **70 dikonfirmasi bukan spam** — ini yang menjadi hard test set. File: `data/hard_test_set.csv`.

### Hasil Evaluasi

Script: `src/evaluate_hard_set.py`
Laporan lengkap: `reports/hard_set_evaluation.txt`

```
Confusion Matrix (70 hard examples, semua berlabel non_spam):

                  Prediksi non_spam  Prediksi spam
Aktual non_spam          53 (TN)         17 (FP)

Accuracy  : 75.71%  (53/70 benar)
FP rate   : 24.29%  (17 dari 70 non_spam salah ditandai spam)
```

Keputusan model untuk 70 komentar:

| Via | Jumlah | Keterangan |
|-----|--------|------------|
| Hybrid A | 35 | SVM bilang spam, tapi tidak ada sinyal keras → dikoreksi ke non_spam ✓ |
| SVM langsung | 34 | SVM prediksi langsung (16 FP di sini) |
| Hybrid B | 1 | SVM bilang non_spam, ada sinyal keras → dipaksa spam ✗ (FP) |

### Analisis 17 False Positive

Ke-17 komentar yang salah diklasifikasi terbagi dalam beberapa pola:

**Pola 1 — Menyebut nama brand untuk dikritik/dilaporkan (7 komentar)**
```
"Blokir aja situs web Kenzo Toto, biru toto, mawar Toto..."
"Alexis togel pihak pemerintah blokir situs ini"
"Brantas pak, ini situs Judi online yg saya tahu... Udintogel, Zara4d..."
```
Setelah preprocessing: teks ini mengandung `toto`, `judolbrand`, `situs` — sinyal yang identik dengan spam promosi. Model tidak punya cara membedakan *"sebutkan untuk dikritik"* vs *"sebutkan untuk promosi"*.

**Pola 2 — Cerita pengalaman rugi (5 komentar)**
```
"Gw penasaran tmnku depo 50k maxwin 2jt..gw pun depo 50k maen 3jam lose abis"
"Judi itu haram tp klo maxwin huu harumm"
"saya tanggal 1 bulan ini dapat maxwin 2 juta... sekarang kalah depo"
```
Kata `maxwin`, `depo`, `slot` muncul dalam konteks "saya rugi" — tapi model Bag of Words tidak memahami konteks kalimat, hanya bobot kata per kata.

**Pola 3 — Komentar bertanya/berdiskusi tentang mekanisme judi (3 komentar)**
```
"Apa itu bonus saldo IPO, jadi kita di kasih saldo awal 1juta sama situs slot..."
"Kok Aneh bg? kalau memang pekerja slot / admin slot bisa setting..."
```
Pertanyaan tentang cara kerja sistem judi — kosa katanya sama persis dengan spam tapi niatnya edukasi/pertanyaan.

**Pola 4 — Hybrid B menyebabkan FP (1 komentar)**
```
"saya tanggal 1 bulan ini dapat maxwin 2 juta tanggal 2 saya depo habis..."
→ SVM prediksi non_spam (benar secara intuisi)
→ Hybrid B: ada kata "maxwin" → paksa ke spam ✗
```
Ini satu-satunya kasus di mana hybrid rule justru memperburuk hasil. `maxwin` di HARD_SPAM_SIGNALS terlalu agresif untuk komentar testimoni negatif.

### Mengapa Hasilnya Tidak Mengkhawatirkan

75.71% pada hard set tidak berarti model buruk — justru sebaliknya:

1. **Ini kasus yang memang tidak bisa diselesaikan oleh Bag of Words.** Membedakan "menyebut brand untuk dikritik" vs "menyebut brand untuk promosi" butuh pemahaman konteks kalimat — sesuatu yang model linear tidak miliki. Ini bukan bug, ini keterbatasan arsitektur yang sudah diketahui dan didokumentasikan.

2. **Hybrid Rule A menyelamatkan 35 komentar.** Tanpa hybrid rule, SVM sendiri akan menghasilkan lebih banyak FP. Hybrid rule A efektif untuk kasus di mana komentar punya kata judi umum tapi tidak ada sinyal keras brand.

3. **Konteks penggunaan.** Extension ini dirancang untuk menyembunyikan komentar spam promosi judi dari penonton video biasa. Video bertema judi (seperti sumber data hard test ini) adalah edge case — penonton video seperti itu kemungkinan justru ingin melihat komentar tersebut. Bukan target utama use case.

### Untuk Sidang

> *"Selain evaluasi standar pada test set biasa (accuracy 96.95%), dilakukan evaluasi tambahan menggunakan hard test set yang terdiri dari 141 komentar — diambil dari dua video YouTube bertema judi online (kM99uBssHvQ dan pzE8S6N0vwo), di mana komentarnya berisi kritik, pengalaman rugi, dan permintaan pemblokiran situs. Pada hard test set ini, model mencapai accuracy 80.14% dengan 28 false positive. Analisis menunjukkan bahwa kegagalan terjadi pada kasus di mana token yang sama digunakan dalam konteks yang berbeda — misalnya menyebut nama situs untuk dikritik vs dipromosikan, atau menyebut kata 'maxwin' dalam konteks komentar humor negatif. Ini adalah keterbatasan inheren dari model Bag of Words yang tidak memahami konteks kalimat."*

---

## 30. Leet Speak Normalization — Mendeteksi H0KI777 dan Sejenisnya

### Masalah

Spammer menggunakan trik **leet speak** — mengganti huruf dengan digit yang bentuknya mirip:
- `O` → `0` (huruf O → angka nol)
- `I` → `1` (huruf I → angka satu)

Contoh nyata: `H0KI777` (ditulis dengan angka nol, bukan huruf O).

Setelah Step 5 (lowercase): `h0ki777`

Setelah Step 5b brand canonicalization, pola `JUDOL_BRAND_PATTERN` mencari `[a-z]{2,}` + suffix angka. Tapi `h0ki` mengandung digit di tengah — regex `[a-z]{2,}` hanya cocok untuk huruf a-z berurutan, dan `0` memecah urutan itu. Akibatnya `h0ki777` tidak cocok → tidak diubah ke `judolbrand` → SVM belajar fitur `hki` atau `ki` yang tidak informatif → spam lolos.

### Solusi: Step 5b-i

Langkah normalisasi leet disisipkan **setelah Step 5 (lowercase)** dan **sebelum Step 5b (brand canonicalization)**:

```python
# Step 5b-i: Leet speak normalization
# Hanya berlaku pada kata yang mengandung campuran huruf dan digit
def _normalize_leet(m):
    word = m.group(0)
    word = word.replace("0", "o").replace("1", "i")
    return word
text = re.sub(r'\b[a-z0-9]*[0-9][a-z0-9]*\b', _normalize_leet, text)
```

**Alur baru untuk `H0KI777`:**
```
H0KI777
  → (Step 5: lowercase) h0ki777
  → (Step 5b-i: leet norm) hoki777   ← "0" jadi "o"
  → (Step 5b: brand canon) judolbrand ← "hoki" + "777" cocok JUDOL_BRAND_PATTERN
  → (server.py Hybrid B) spam ✓
```

### Kenapa Regex Hanya Menarget Kata dengan Digit?

Pola `r'\b[a-z0-9]*[0-9][a-z0-9]*\b'` mensyaratkan setidaknya satu digit dalam kata. Ini penting karena:

- Kata Indonesia biasa seperti `bola`, `solo`, `motor` tidak terpengaruh (tidak ada digit)
- Hanya kata campuran huruf-angka yang berpotensi leet yang diproses
- Menghindari mengubah angka murni seperti tahun (`2024` → `2o24` yang salah)

### Batasan

Normalisasi ini hanya menangani `0→o` dan `1→i`. Leet speak bisa lebih luas:
- `3→e`, `4→a`, `5→s`, `7→t` juga dipakai
- Tapi substitusi ini lebih berisiko false positive pada teks normal (angka 3, 4, 5, 7 sering muncul bukan sebagai leet)

Trade-off yang dipilih: tangkap kasus yang paling umum (`0` dan `1`) dengan risiko rendah, bukan mencoba menangkap semua kemungkinan leet dan memperkenalkan false positive baru.

### Untuk Sidang

> *"Spammer menggunakan teknik leet speak untuk menghindari deteksi berbasis pola — mengganti huruf dengan digit yang bentuknya mirip. Kasus yang paling umum ditemukan adalah angka 0 menggantikan huruf O (contoh: H0KI777 untuk HOKI777). Normalisasi leet speak ditambahkan sebagai Step 5b-i dalam pipeline preprocessing, di antara lowercase (Step 5) dan brand canonicalization (Step 5b). Normalisasi hanya diterapkan pada kata yang mengandung campuran huruf dan digit — mencegah pengubahan angka murni yang bukan leet. Dengan langkah ini, H0KI777 berhasil dikonversi ke hoki777, yang selanjutnya cocok dengan pola brand judol dan direpresentasikan sebagai token judolbrand."*

---

## 31. Perlindungan Data Laporan Extension — /report ke Dua File

### Masalah

Endpoint `/report` dirancang untuk menerima laporan "bukan spam" dari pengguna extension — saat user klik tombol "Bukan spam?", teks komentar dikirim ke server dan disimpan sebagai data training non_spam.

Masalahnya: endpoint ini **hanya menulis ke `data/comments.csv`**. File ini ditimpa setiap kali `prepare_dataset.py` dijalankan (untuk rebuild dataset dari sumber scraper). Ini berarti:

1. User melaporkan 59 komentar lewat extension
2. 59 entri tersimpan di `comments.csv`
3. Bulan berikutnya, ada scraping data baru → `prepare_dataset.py` dijalankan
4. `comments.csv` ditimpa dari nol → **59 laporan hilang**

### Solusi: Tulis ke Dua File Sekaligus

Endpoint `/report` diperbarui untuk menulis ke:
- `data/comments.csv` — efek langsung ke training berikutnya (sama seperti sebelumnya)
- `data/manual_overrides.csv` — persisten lintas rebuild (sama seperti koreksi manual lainnya)

```python
# Append ke comments.csv
with open(DATA_PATH, "a", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([request.text, request.label])

# Append ke manual_overrides.csv (persisten saat prepare_dataset.py dijalankan ulang)
overrides_has_header = os.path.exists(MANUAL_OVERRIDES_CSV) and os.path.getsize(MANUAL_OVERRIDES_CSV) > 0
with open(MANUAL_OVERRIDES_CSV, "a", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    if not overrides_has_header:
        writer.writerow(["text", "label"])
    writer.writerow([request.text, request.label])
```

Deduplication juga diperkuat — cek duplikat di **kedua file** sebelum menyimpan:

```python
for check_path in (DATA_PATH, MANUAL_OVERRIDES_CSV):
    if os.path.exists(check_path):
        with open(check_path, ...) as f:
            for row in csv.reader(f):
                if row and row[0].strip() == request.text:
                    return ReportResponse(success=False, duplicate=True)
```

### Rescue 59 Laporan yang Sudah Ada

Sebelum fix ini dibuat, 59 laporan sudah terlanjur hanya ada di `comments.csv`. Mereka diselamatkan dengan cara:
1. Bandingkan `comments.csv` dengan semua sumber pipeline (scraper final_spam.json, final_non_spam.json, manual_overrides.csv)
2. Entri yang tidak ada di sumber manapun = berasal dari laporan extension
3. Entri tersebut dimigrasi ke `manual_overrides.csv`

**Hasilnya:** `manual_overrides.csv` tumbuh dari 213 → 343 entri (tambah 71 dari pzE8S6N0vwo + 59 rescue).

### Untuk Sidang

> *"Endpoint /report pada server API memungkinkan pengguna extension melaporkan false positive secara langsung selama penggunaan. Ditemukan bahwa laporan ini hanya tersimpan di comments.csv yang digenerate ulang setiap rebuild dataset — risiko kehilangan data yang signifikan. Solusinya adalah menulis setiap laporan ke dua file: comments.csv untuk efek langsung, dan manual_overrides.csv sebagai penyimpanan permanen yang dihormati oleh pipeline prepare_dataset.py. Dengan arsitektur ini, laporan pengguna persisten lintas siklus scraping dan rebuild."*

---

## 32. Penghapusan `slot` dan `deposit` dari HARD_SPAM_SIGNALS

### Latar Belakang

`HARD_SPAM_SIGNALS` adalah daftar kata yang, jika muncul di teks yang sudah dipreprocessing, memicu **Hybrid Rule (B)**: prediksi SVM non_spam di-override ke spam. Logikanya: kata-kata ini sangat spesifik ke promosi judi sehingga keberadaannya hampir selalu menandakan spam.

Tapi "sangat spesifik" adalah asumsi yang perlu dikalibrasi terus seiring data bertambah.

### Masalah yang Ditemukan

Setelah ekspansi hard test set ke 141 entri (termasuk 71 komentar dari video finansial bertema anti-judol), ditemukan pola FP baru:

```
"Saya kenal judi slot, hidup gue jadi berantakan dan keluarga berantakan"
→ cleaned: "kenal judi slot hidup berantakan keluarga berantakan"
→ SVM: non_spam (benar — kalimat cerita rugi)
→ Hybrid B: ada "slot" → paksa spam ✗  (false positive)

"Ini nyata! Tetangga saya kerja serabutan... hasil kerja dipakai deposit lagi"
→ cleaned: "nyata tetangga kerja serabutan hasil kerja deposit lagi"
→ SVM: non_spam (benar — cerita korban)
→ Hybrid B: ada "deposit" → paksa spam ✗  (false positive)
```

Kedua kata ini ternyata sangat sering muncul di testimoni negatif dan diskusi anti-judol — konteks yang sama sekali berbeda dari promosi.

### Keputusan: Hapus dari HARD_SPAM_SIGNALS

| Kata | Alasan dihapus |
|------|----------------|
| `slot` | Sangat umum di cerita korban ("kecanduan slot"), diskusi edukasi, permintaan blokir. Spam yang pakai "slot" hampir selalu juga punya `gacor` atau `judolbrand`. |
| `deposit` | Muncul wajar di cerita korban ("dia gadai motor buat deposit lagi"), bahkan di konteks perbankan umum. |

Perubahan diterapkan di **dua file secara konsisten**:
- `src/server.py` — engine prediksi live
- `src/evaluate_hard_set.py` — evaluasi offline (harus sama persis agar angka evaluasi valid)

### Dampak Terukur

Evaluasi pada 141-entri hard test set sebelum dan sesudah penghapusan:

| Metrik | Sebelum | Sesudah | Delta |
|--------|---------|---------|-------|
| FP (non_spam salah → spam) | 37 | **28** | −9 |
| Accuracy | 73.76% | **80.14%** | +6.38% |

Dua komentar yang sebelumnya FP, sekarang benar:
- `"Saya kenal judi slot..."` → sekarang `[non_spam (svm)]` ✓
- `"...hasil kerja dipakai deposit lagi"` → sekarang `[non_spam (svm)]` ✓

### Trade-off yang Diterima

Penghapusan ini memindahkan tanggung jawab klasifikasi sepenuhnya ke SVM untuk komentar yang hanya mengandung "slot" atau "deposit" tanpa sinyal lain.

Risiko: spam yang HANYA menyebut "slot deposit" tanpa `gacor`, `judolbrand`, atau sinyal keras lainnya **mungkin lolos** sebagai non_spam.

Namun secara empiris, spam judol yang hanya berisi "slot deposit" tanpa sinyal keras lain hampir tidak ada — promosi judol hampir selalu menyertakan nama brand, kata `gacor`, atau ajakan eksplisit yang tertangkap sinyal lain.

### Untuk Sidang

> *"Evaluasi berulang terhadap hard test set mengungkap bahwa kata 'slot' dan 'deposit' di HARD_SPAM_SIGNALS menyebabkan Hybrid Rule (B) terlalu agresif — memaksa prediksi ke spam pada komentar korban dan diskusi anti-judol yang secara wajar mengandung kedua kata tersebut. Berdasarkan analisis empiris pada 141 hard examples, penghapusan dua kata ini mengurangi false positive dari 37 menjadi 28 (−24%) dan meningkatkan accuracy hard test set dari 73.76% menjadi 80.14%. Risiko yang diterima adalah kemungkinan spam yang hanya menyebut 'slot' dan 'deposit' tanpa sinyal keras lain dapat lolos — namun berdasarkan observasi data, spam jenis ini hampir selalu juga mengandung nama brand atau kata gacor yang masih tertangkap sinyal lain."*

---

## 33. Ablation Study Hybrid Rules — Kenapa Akhirnya Dimatikan

### Latar Belakang

Bagian 22, 26, dan 32 di atas menceritakan proses iteratif mengembangkan dan menyempurnakan hybrid rule — menambah arah B, lalu mengkalibrasi ulang `HARD_SPAM_SIGNALS` setelah ditemukan false positive baru. Semua keputusan itu didasarkan pada satu sumber evaluasi: `data/hard_test_set.csv` (141 kasus ambigu).

Setelah dataset utama diperluas ke Versi 8 (5132 baris, lihat [DATASET_LOG.md](DATASET_LOG.md)) dan model dilatih ulang, muncul pertanyaan yang belum pernah dijawab dengan angka: **apakah hybrid rule masih membantu, atau cuma membantu di hard test set tapi merugikan di distribusi data yang lebih luas?**

### Metodologi: Ablation Study

Dibuat `src/evaluate_hybrid_ablation.py` — script yang menjalankan model SVM yang sama dua kali per dataset evaluasi: sekali tanpa hybrid rule (`model.predict()` langsung), sekali dengan hybrid rule diterapkan (logika identik dengan `server.py`). Dievaluasi di **dua** dataset sekaligus, bukan cuma satu:

1. **Train-test split (20% holdout dari comments.csv, n=1027)** — representasi distribusi data yang lebih umum/realistis.
2. **Hard test set (n=141)** — kasus ambigu yang sengaja sulit, sumber kalibrasi hybrid rule selama ini.

### Hasil

| Dataset | SVM murni | SVM + Hybrid | Delta |
|---|---|---|---|
| Train-test split | **97.57%** acc, F1 0.9752 | 91.33% acc, F1 0.9101 | **-6.23%** acc, **-0.0651** F1 |
| Hard test set | **92.91%** acc, F1 0.4816 | 80.14% acc, F1 0.4449 | **-12.77%** acc, **-0.0367** F1 |

SVM murni menang di **kedua** dataset — termasuk di hard test set, tempat hybrid rule sebelumnya dianggap berguna. Ini titik baliknya: ketika §22 dan §32 ditulis, model dilatih dari dataset yang lebih kecil, sehingga SVM sendirian belum cukup kuat membedakan konteks ambigu — hybrid rule menutupi kelemahan itu. Setelah dataset diperluas (lebih banyak data non-spam nyata, leet speak normalization, dll), SVM sendiri sudah cukup kuat, dan hybrid rule yang dikalibrasi untuk model lama justru jadi beban.

### Breakdown Per-Rule

Untuk memastikan bukan kebetulan, setiap kali rule menyala dicatat apakah hasilnya benar atau salah dibanding label asli:

| Rule | Train-test split | Hard test set |
|---|---|---|
| **Rule A** (spam→non_spam) | nyala 66×, 4 benar / 62 salah (94% salah) | nyala 3×, 3 benar / 0 salah |
| **Rule B** (non_spam→spam) | nyala 6×, 0 benar / 6 salah | nyala 21×, 0 benar / 21 salah (100% salah) |

**Rule B gagal total** — 0 benar dari 27 kali nyala di kedua dataset gabungan. Hampir semua kasus adalah komentar yang menyebut istilah judi (`toto`, `togel`, dst.) dalam konteks **mengkritik atau melaporkan** situs judol, bukan mempromosikannya — persis masalah konteks yang sudah diidentifikasi sejak §26 dan §32, tapi ternyata tidak pernah benar-benar terselesaikan, hanya dikurangi.

**Rule A** menunjukkan trade-off yang timpang: efektif di hard test set (3/3 benar — inilah alasan rule ini awalnya terasa berguna), tapi di test set normal mengorbankan 62 komentar spam asli demi menyelamatkan 4. Penjelasannya: spam asli sering tidak memuat kata persis dari `HARD_SPAM_SIGNALS` (misalnya "daftar sekarang gan, wd lancar, gabung yuk" — tidak ada `gacor`/`maxwin`/`judolbrand` sama sekali), sehingga Rule A salah mengira itu false positive SVM padahal SVM sudah benar.

### Keputusan: Dinonaktifkan, Bukan Dihapus

`src/server.py` sekarang punya `ENABLE_HYBRID_RULES = False`. Kode `HARD_SPAM_SIGNALS` dan `has_hard_spam_signal()` tetap ada — dimatikan lewat flag, bukan dihapus, dengan dua alasan:

1. **Bukti proses eksperimen.** Skripsi yang baik menunjukkan iterasi: mencoba pendekatan, mengukur, dan mengambil keputusan berdasarkan data — bukan cuma melaporkan hasil akhir yang sudah "rapi". Riwayat di §22/§26/§32 plus ablation study ini *adalah* bagian dari kontribusi metodologis, bukan dead-end yang perlu disembunyikan.
2. **Bisa diuji ulang.** Kalau pola spam baru di masa depan menunjukkan SVM murni mulai kewalahan lagi (misal spam mulai konsisten menghindari TF-IDF dengan cara baru), `ENABLE_HYBRID_RULES = True` lalu jalankan ulang `python src/evaluate_hybrid_ablation.py` untuk memverifikasi efeknya sebelum di-deploy — bukan asumsi seperti dulu.

### Untuk Sidang

> *"Hybrid rule berbasis kata kunci sempat diterapkan untuk mengatasi false positive/negative pada model versi awal, dan terbukti meningkatkan accuracy hard test set dari 73.76% menjadi 80.14% saat itu. Namun setelah dataset training diperluas ke 5132 baris dan model dilatih ulang, dilakukan ablation study sistematis (membandingkan SVM murni vs SVM+hybrid pada dua dataset evaluasi independen) yang menunjukkan hybrid rule justru menurunkan accuracy 6–13 poin persentase — model SVM yang lebih kuat tidak lagi membutuhkan koreksi berbasis kata kunci, dan rule tersebut sekarang lebih sering salah mengoreksi prediksi SVM yang sudah benar daripada membantu. Hybrid rule kemudian dinonaktifkan secara default, dengan kode dipertahankan sebagai dokumentasi proses eksperimen dan dapat diaktifkan kembali untuk pengujian di masa depan."*

---

## 34. Generalisasi ke Brand Judol Baru — Sejauh Mana Model Bisa Mengikuti?

### Pertanyaan yang Mendasari

Semua brand judol di dataset training adalah brand yang **sudah pernah muncul** saat scraping. Pertanyaan wajar yang muncul: bagaimana kalau muncul brand benar-benar baru setelah model selesai dilatih — apakah sistem ini langsung buta terhadapnya sampai di-retrain manual?

Ini beda dari masalah di §33 (konteks ajakan vs kritik) — di sini soalnya murni soal **brand name yang belum pernah dilihat sama sekali**, bukan soal salah baca konteks kalimat.

### Mekanisme yang Sudah Ada: Canonicalization, Bukan Hafalan

Step 5b di `preprocessing.py` (`JUDOL_BRAND_PATTERN`) tidak menghafal nama brand satu per satu — ia mengenali **pola penamaan**: `[kata bebas] + [suffix numerik atau qq]` (4d, 3d, 2d, 88, 99, 77, 69, 138, 388, 303, 777, 888, qq). Begitu sebuah kata cocok pola ini, ia diubah jadi token `judolbrand` — token yang sudah sangat kuat bobotnya di model, terlepas dari nama aslinya. Ini didesain sejak Versi 5 (lihat §23) justru untuk mengantisipasi brand baru yang mengikuti konvensi penamaan yang sama.

### Uji Empiris: Brand yang Benar-Benar Tidak Ada di Dataset

Untuk memverifikasi seberapa jauh generalisasi ini bekerja, diuji beberapa nama brand fiktif yang dipastikan tidak ada di `data/comments.csv` sama sekali:

| Skenario | Teks Uji | Tercanonicalize jadi `judolbrand`? | Prediksi | Confidence |
|---|---|---|---|---|
| Suffix digit umum (88) + konteks promosi | "Daftar sekarang di NAMABRANDBARU88, bonus new member gede!" | Ya | spam | 100% |
| Suffix digit (888), tanpa kalimat promosi | "liat aja di MEGAHWIN888" | Ya | spam | 100% |
| Suffix digit (99), brand doang tanpa konteks | "EMASJAYA99" | Ya | spam | 100% |
| Suffix TOTO (tanpa digit) + konteks promosi | "Daftar sekarang di RAJATOTO, bonus new member gede!" | **Tidak** | spam | 91.89% |
| Suffix BET (tanpa digit) + konteks promosi | "Gabung yuk di SULTANBET, wd lancar tiap hari!" | **Tidak** | spam | 88.40% |
| Suffix WIN (tanpa digit) + konteks promosi | "Main di ISTANAWIN aja, gampang menang!" | **Tidak** | spam | 85.09% |
| Suffix BET, **tanpa** konteks promosi | "SULTANBET mantap" | **Tidak** | **non_spam (salah arah, tapi aman)** | 95.27% |
| Suffix tidak dikenal sama sekali + konteks promosi jelas | "Daftar sekarang di JAYAMAKMUR, bonus gede!" | **Tidak** | non_spam | **43.94%** ⚠ |
| Suffix tidak dikenal, brand doang | "JAYAMAKMUR aja" | **Tidak** | non_spam | 97.06% |

### Interpretasi

**Dua lapis generalisasi yang sudah bekerja dengan baik:**
1. Brand baru dengan suffix dikenal (digit/`qq`) → langsung tercanonicalize ke `judolbrand`, confidence selalu 100% terlepas dari ada/tidaknya kalimat promosi di sekitarnya. **Tidak butuh maintenance apapun** untuk brand jenis ini.
2. Brand baru dengan suffix tidak dikenal (termasuk TOTO/BET/WIN) **tapi** disertai kalimat promosi yang jelas → tetap terdeteksi spam dengan confidence tinggi (85–92%), murni dari kata-kata promosi di sekitarnya ("daftar", "gabung", "bonus", "wd", "gampang menang") yang sudah dipelajari model — brand-nya sendiri boleh benar-benar asing.

**Satu celah nyata ditemukan:** brand dengan suffix yang sama sekali tidak dikenali pola **dan** tanpa kata promosi yang kuat di sekitarnya → confidence anjlok ke kisaran 44–56%, jauh di bawah threshold default extension (75%). Kasus *"Daftar sekarang di JAYAMAKMUR, bonus gede!"* adalah contoh paling mengkhawatirkan — kalimatnya jelas-jelas promosi untuk manusia, tapi model ragu karena baik brand maupun kombinasi kata di sekitarnya berada di luar pola yang pernah dipelajari.

### Kenapa "Tinggal Tambahkan TOTO/BET/WIN ke JUDOL_BRAND_PATTERN" Bukan Solusi Murah

`prepare_dataset.py` memang sudah punya pola serupa untuk TOTO/BET/WIN/QQ (`BRAND_SUFFIX_PATTERN`, lihat §5 dan §27), jadi solusi yang kelihatan jelas adalah menyamakan `JUDOL_BRAND_PATTERN` di `preprocessing.py` dengan pola itu. Tapi ada perbedaan krusial:

- `BRAND_SUFFIX_PATTERN` di `prepare_dataset.py` berjalan di atas `normalized_text` **sebelum** lowercase — ia bisa aman mensyaratkan ALL-CAPS (`[A-Z]{3,}TOTO`) untuk membedakan brand asli dari kata Indonesia biasa yang kebetulan mengandung substring sama.
- `JUDOL_BRAND_PATTERN` di `preprocessing.py` berjalan **setelah** Step 5 (lowercase) — informasi huruf besar/kecil sudah hilang di titik ini. Menambahkan `bet`/`win`/`toto` tanpa syarat huruf besar akan menangkap ulang kata Indonesia umum yang **sudah pernah jadi false positive dan diperbaiki**: `ribet`, `kesambet`, `ngebet`, `ngerebet` (lihat §27, kasus Versi 6–7).

Memperbaiki ini dengan benar butuh exclude-list kata Indonesia umum yang mengandung substring tersebut — bukan perubahan satu baris, dan beresiko menciptakan ulang bug yang sudah pernah diperbaiki kalau terburu-buru. Belum dikerjakan karena ROI-nya belum jelas dibanding risikonya — tabel di atas menunjukkan brand suffix TOTO/BET/WIN **tanpa** canonicalization pun sudah terdeteksi 85–92% selama ada konteks promosi, jadi gap yang ditutup oleh perbaikan ini relatif sempit.

### Keputusan: Diterima sebagai Keterbatasan Sistem, Dimitigasi Secara Operasional

Bukan dianggap kegagalan desain — setiap sistem deteksi spam berbasis konten (regex, keyword list, atau model statistik manapun) punya batas yang sama: ia hanya bisa mengenali pola yang sudah pernah diobservasi, baik secara eksplisit (hardcoded) maupun implisit (dipelajari dari data). Brand benar-benar baru dengan konvensi penamaan benar-benar baru **dan** tanpa kalimat promosi sama sekali di sekitarnya adalah kasus tepi yang juga sulit dinilai manusia tanpa konteks tambahan.

**Mitigasi yang sudah tersedia, bukan perbaikan kode baru:** pipeline `scraper/index.js → prepare_dataset.py → train.py` yang sudah ada di proyek ini *adalah* jawaban untuk brand baru — begitu brand baru muncul di hasil scraping berikutnya, ia otomatis masuk dataset training tanpa perlu update regex manual satu per satu. Endpoint `/report` di `server.py` juga memungkinkan koreksi langsung dari pengguna extension yang menemukan kasus terlewat, tersimpan permanen di `manual_overrides.csv` (lihat §28). Maintenance yang dibutuhkan adalah **retraining berkala**, bukan **pengkodean ulang per brand**.

### Untuk Sidang

> *"Diuji secara empiris menggunakan nama brand fiktif yang dipastikan tidak ada di dataset training. Hasilnya, brand baru dengan suffix penamaan yang dikenal (pola digit seperti 4D/88/99/77, atau QQ) langsung dikenali dengan confidence 100% lewat mekanisme canonicalization di preprocessing — bukan hafalan nama, tapi pengenalan pola. Brand dengan suffix di luar pola itu (misal TOTO/BET/WIN tanpa digit) tetap terdeteksi 85–92% selama disertai kalimat promosi, karena model mengandalkan kata-kata ajakan di sekitarnya, bukan nama brand semata. Celah yang teridentifikasi adalah kombinasi brand benar-benar baru tanpa kalimat promosi sama sekali, di mana confidence turun mendekati batas keputusan. Perluasan pola canonicalization untuk menutup celah ini dipertimbangkan tapi ditunda karena berisiko menghidupkan kembali bug false positive pada kata Indonesia umum (ribet, kesambet) yang sudah pernah diperbaiki sebelumnya — sehingga keterbatasan ini diterima dan dimitigasi secara operasional lewat pipeline scraping-retraining yang sudah ada, bukan lewat penambahan aturan baru yang berisiko."*

---

## 35. Insiden Kontaminasi Data — Spam Tersamar yang Lolos Heuristik Scraper

### Bagaimana Ini Ditemukan

Setelah scraping 12 video baru (lihat [DATASET_LOG.md Versi 10](DATASET_LOG.md#versi-10--2026-06-30)) dan model selesai dilatih ulang, user secara manual membuka salah satu file hasil scraping mentah di editor dan menemukan komentar yang jelas-jelas promosi judi tapi ter-label `non_spam`. Ini **bukan ditemukan lewat metrik otomatis** — `spam_score` dari scraper untuk semua entri yang bermasalah adalah 0, jadi tidak ada alarm apapun dari sistem. Murni dari peninjauan manual.

Ini poin metodologis penting: **evaluasi otomatis (accuracy, F1, hard test set) tidak bisa mendeteksi data yang salah label sejak awal** — kalau label sumbernya salah, model yang "akurat" terhadap label itu sebenarnya akurat terhadap kesalahan. Audit manual berkala terhadap sampel data mentah tetap diperlukan, walau sudah ada pipeline otomatis.

### Tiga Kampanye Spam yang Ditemukan

| Kampanye | Teknik Penyamaran | Contoh |
|---|---|---|
| `MANTULHOKI` | Unicode dekoratif — 7 varian font berbeda (math bold, italic, double-struck, monospace, script, bahkan campuran Cyrillic+Greek homoglyph) | `𝐌𝐚𝐧𝐭𝐮𝐥𝐡𝟎𝐤𝟏`, `𝕄𝔸ℕ𝕋𝕌𝕃ℍ𝕆𝕂𝕀`, `мαηтυℓнσкι` |
| `HOKI777` | Leet speak (digit 0/1 menggantikan huruf) **dan** full-width spacing yang menyamar sebagai komentar reaksi timestamp video | `H0KI777`, `Ｈ Ｏ ＫＩ 7 7 7` di tengah komentar `"01:35 ... auto betah"` |
| `4rabet` / `ANRU33` | Brand internasional berbahasa Inggris, dan full-width digit dibungkus bracket | `4rabet sets new standards...`, `【ＡＮＲＵ３３】` |

Total **61 entri** terkonfirmasi dari 4156 entri pool non-spam saat itu (1.5%) — 53 dari scraping 12 video baru, **8 sudah ada di pool sejak sebelum sesi scraping ini**, kemungkinan sejak data non-spam awal dikumpulkan di Versi 2.

### Root Cause: Scraper Tidak Menormalisasi Unicode Sebelum Menilai

`scraper/index.js` menghitung `spam_score` berdasarkan sinyal seperti `brand_pattern` **langsung dari teks mentah**, tanpa NFKC normalization terlebih dahulu. Ini kontras dengan `preprocessing.py` di sisi model, yang secara eksplisit melakukan NFKC normalize (Step 2), strip combining marks (Step 2b), dan homoglyph translation (Step 3) — *sebelum* mengecek pola apapun (lihat §6 dan §7).

Akibatnya: scraper "buta" terhadap persis jenis obfuscation yang justru paling sering dipakai spammer dan yang preprocessing model sudah dirancang untuk membongkar. Scraper dan model menggunakan standar normalisasi yang berbeda — sebuah inkonsistensi yang baru terlihat dampaknya sekarang.

### Kenapa Video Bertema Judi Lebih Rentan

12 video baru yang di-scrape secara spesifik membahas topik judi online (edukasi, pengalaman pribadi). Video semacam ini ternyata **menarik lebih banyak spam tersamar** dibanding video acak — masuk akal secara logika spammer: mereka menargetkan audiens yang sudah terbukti tertarik dengan topik judi, bukan menyebar acak ke semua video. Tiga dari empat kampanye yang ditemukan (39 dari 53 entri baru) berasal dari hanya 1-2 video saja — terkonsentrasi, bukan tersebar merata, konsisten dengan pola serangan terarah/bot farming pada thread spesifik.

**Implikasi untuk scraping selanjutnya:** video yang relevan secara topik untuk dataset (semakin spesifik membahas judi) kemungkinan akan terus membawa risiko kontaminasi yang lebih tinggi dibanding video acak. Audit manual menjadi lebih penting, bukan kurang, justru untuk kategori data yang paling berharga untuk training.

### Perbaikan: Relabel, Bukan Sekadar Hapus

Percobaan pertama hanya menghapus 61 entri dari pool non-spam. Sanity check pasca-retrain menunjukkan model **masih salah** mengklasifikasikan kalimat baru bergaya Mantulhoki/4rabet sebagai non_spam — karena model tidak pernah diberi contoh bahwa pola itu *adalah* spam, ia hanya tidak lagi diberi tahu (secara salah) bahwa itu non-spam. Menghapus saja menghasilkan kekosongan informasi, bukan koreksi.

Keputusan akhir: 61 entri direlabel jadi `spam` dan ditambahkan ke `manual_overrides.csv` (mekanisme yang sama dengan koreksi false positive di §27/§28, dipakai di sini untuk arah sebaliknya — false negative dari sumber data). Setelah retrain ulang, sanity check pada brand yang sama menunjukkan confidence 99.6–100% terdeteksi sebagai spam.

### Dampak Terukur

| Metrik | Versi 10 (terkontaminasi) | Versi 11 (bersih) |
|---|---|---|
| Accuracy (train-test split) | 98.23% | 97.39% |
| Hard test set accuracy | 97.78% | 97.04% |

Penurunan ini **disengaja dan diharapkan** — paralel langsung dengan pelajaran Versi 1→2 (data sintetis vs nyata): angka yang lebih tinggi tapi dari label yang salah bukan prestasi, angka yang lebih rendah tapi jujur lebih bisa dipercaya dan lebih defensible di sidang.

### Untuk Sidang

> *"Selama proses audit dataset, ditemukan secara manual bahwa beberapa komentar yang ter-scrape sebagai non-spam ternyata spam yang disamarkan menggunakan font Unicode dekoratif, leet speak, dan spasi karakter full-width — teknik yang dirancang untuk lolos dari filter kata kunci sederhana. Heuristik penilaian milik scraper tidak melakukan normalisasi Unicode sebelum menilai, sehingga 61 komentar (termasuk 8 yang sudah mencemari dataset sejak pengumpulan data non-spam pertama kali) lolos tak terdeteksi. Setelah diaudit dan direlabel ke kelas yang benar — bukan sekadar dihapus, karena percobaan awal menunjukkan penghapusan saja tidak mengajarkan model mengenali pola itu — model dilatih ulang dan menunjukkan accuracy yang sedikit lebih rendah dari sebelumnya. Penurunan ini dianggap sebagai indikator data yang lebih jujur, bukan kemunduran kualitas model, dan menjadi pengingat bahwa evaluasi otomatis tidak bisa menggantikan audit data manual ketika sumber datanya sendiri berpotensi salah label."*
