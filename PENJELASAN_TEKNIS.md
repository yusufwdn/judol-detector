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

Pipeline di `src/preprocessing.py` menangani semua ini dalam 7 langkah berurutan. Urutan penting — setiap langkah mengasumsikan langkah sebelumnya sudah dijalankan.

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

### Layer 3 — Homoglyph Cyrillic/Greek

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

Spammer yang lebih canggih menggunakan huruf Cyrillic yang bentuknya identik dengan huruf Latin:

| Karakter | Asal | Terlihat seperti |
|----------|------|-----------------|
| `а` U+0430 | Cyrillic | `a` Latin |
| `е` U+0435 | Cyrillic | `e` Latin |
| `о` U+043E | Cyrillic | `o` Latin |
| `р` U+0440 | Cyrillic | `p` Latin (hati-hati, bukan 'r'!) |

Setelah layer ini, kata "dаftаr" (dengan Cyrillic 'а') menjadi "daftar" (Latin 'a') — dan bisa dikenali sebagai satu token yang sama.

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

*Dokumen ini adalah komplemen dari README.md. README membahas cara menjalankan; dokumen ini membahas cara memahami.*
