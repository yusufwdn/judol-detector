# Dokumentasi Sistem Deteksi Spam Judi Online (Judol)
## Berbasis Support Vector Machine (SVM) dan Browser Extension

---

> **Untuk siapa dokumen ini?**
> Dokumentasi ini ditulis untuk pembaca yang belum familiar dengan machine learning atau pemrograman tingkat lanjut. Setiap konsep teknis akan dijelaskan dengan analogi sehari-hari agar mudah dipahami.

---

## Daftar Isi

1. [Gambaran Umum Sistem](#1-gambaran-umum-sistem)
2. [Arsitektur Keseluruhan](#2-arsitektur-keseluruhan)
3. [Sistem 1 — Scraper Komentar YouTube](#3-sistem-1--scraper-komentar-youtube)
   - [3.1 Cara Kerja](#31-cara-kerja)
   - [3.2 Mesin Penilaian Spam (Heuristic Scoring)](#32-mesin-penilaian-spam-heuristic-scoring)
   - [3.3 Mode Video vs. Mode Live Chat](#33-mode-video-vs-mode-live-chat)
   - [3.4 Cara Menjalankan Scraper](#34-cara-menjalankan-scraper)
4. [Sistem 2 — Klasifikasi SVM](#4-sistem-2--klasifikasi-svm)
   - [4.1 Gambaran Pipeline Machine Learning](#41-gambaran-pipeline-machine-learning)
   - [4.2 Persiapan Dataset (prepare_dataset.py)](#42-persiapan-dataset-prepare_datasetpy)
   - [4.3 Pembersihan Teks / Preprocessing (preprocessing.py)](#43-pembersihan-teks--preprocessing-preprocessingpy)
   - [4.4 Pelatihan Model (train.py)](#44-pelatihan-model-trainpy)
   - [4.5 Server API (server.py)](#45-server-api-serverpy)
   - [4.6 Browser Extension](#46-browser-extension)
5. [Alur Kerja Lengkap dari Awal Hingga Akhir](#5-alur-kerja-lengkap-dari-awal-hingga-akhir)
6. [Struktur Direktori Proyek](#6-struktur-direktori-proyek)
7. [Cara Menjalankan Sistem Secara Keseluruhan](#7-cara-menjalankan-sistem-secara-keseluruhan)
8. [Konsep Teknis Penting](#8-konsep-teknis-penting)
9. [Batasan dan Catatan Pengembangan](#9-batasan-dan-catatan-pengembangan)

---

## 1. Gambaran Umum Sistem

Proyek ini membangun sebuah sistem yang mampu **mendeteksi dan menyembunyikan komentar spam promosi judi online (judol)** di platform YouTube secara otomatis.

Sistem ini terdiri dari **dua subsistem utama** yang bekerja secara berurutan:

| # | Subsistem | Teknologi | Fungsi |
|---|-----------|-----------|--------|
| 1 | **Scraper** | Node.js | Mengumpulkan data komentar spam dari YouTube sebagai bahan latihan |
| 2 | **Klasifikasi SVM** | Python | Melatih model AI, menyajikannya sebagai API, dan menjalankan deteksi real-time melalui browser extension |

**Analogi sederhana:**
Bayangkan sistem ini seperti seorang satpam cerdas di depan pintu gedung.
- **Scraper** = Tim yang pergi ke lapangan untuk mengumpulkan foto-foto orang mencurigakan sebagai referensi.
- **SVM** = Otak satpam yang sudah dilatih dari foto-foto itu untuk mengenali siapa yang mencurigakan.
- **Server API** = Satpam yang berdiri di pos dan siap menjawab pertanyaan "apakah orang ini mencurigakan?" dalam hitungan milidetik.
- **Browser Extension** = Sistem kamera CCTV yang terus memantau dan melapor ke satpam setiap ada tamu baru.

---

## 2. Arsitektur Keseluruhan

```
┌─────────────────────────────────────────────────────────────────┐
│                        FASE PENGUMPULAN DATA                    │
│                                                                 │
│   YouTube API  ──►  Scraper (index.js)  ──►  final_result.json  │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASE PERSIAPAN DATASET                      │
│                                                                 │
│   final_result.json  ──►  prepare_dataset.py  ──►  comments.csv │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FASE PELATIHAN MODEL                      │
│                                                                 │
│  comments.csv  ──►  preprocessing.py  ──►  train.py             │
│                                              │                  │
│                                              ▼                  │
│                                     svm_model.joblib            │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FASE INFERENSI (REAL-TIME)                │
│                                                                 │
│  Browser Extension  ──POST /predict──►  server.py               │
│       (content.js)                          │                   │
│           │                                 ▼                   │
│           │                       svm_model.joblib              │
│           │                          (dimuat sekali)            │
│           │◄──── JSON Response ─────────────┘                   │
│           │  {"label":"spam","confidence":0.94,"is_spam":true}  │
│           │                                                     │
│           └──► Sembunyikan komentar jika is_spam == true        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Sistem 1 — Scraper Komentar YouTube

**File:** `scraper/index.js`

### 3.1 Cara Kerja

Scraper adalah program Node.js yang berkomunikasi dengan **YouTube Data API v3** untuk mengambil komentar dari video YouTube. Program ini kemudian menganalisis setiap komentar menggunakan sistem penilaian berbasis aturan (heuristik), dan menyimpan komentar yang dinilai sebagai spam ke dalam file JSON.

**Analogi:** Bayangkan Anda diminta menyortir ribuan surat masuk di kantor pos. Alih-alih membaca satu per satu dengan seksama, Anda membuat daftar ciri-ciri surat mencurigakan: "ada stempel merah", "ada simbol dolar", "ada nomor telepon". Setiap surat yang memiliki ciri-ciri ini langsung dipisahkan. Itulah yang dilakukan scraper — menyortir komentar menggunakan daftar ciri-ciri spam.

**Alur kerja scraper:**

```
  Video YouTube
       │
       ▼
  YouTube Data API
  (mengambil 100 komentar per halaman)
       │
       ▼
  analyzeSpamScore(teks)
  → Normalisasi Unicode
  → Cek pola brand judol
  → Cek link/kontak
  → Hitung skor 0-100
       │
       ├── Skor >= 30 DAN ada sinyal primer?
       │       │
       │       ▼ YA
       │   Simpan ke array hasil
       │
       └── Sudah mencapai target OR tidak ada halaman berikutnya?
               │
               ▼ YA
           Simpan ke final_result.json
```

Setiap entri yang tersimpan di `final_result.json` memiliki struktur berikut:

```json
{
  "video_id": "z-BTQKhWrJc",
  "timestamp": "2025-06-01T10:30:00.000Z",
  "original_text": "MAXWIN88 daftar sekarang bonus 100% WA 0812xxxx",
  "normalized_text": "MAXWIN88 daftar sekarang bonus 100% WA 0812xxxx",
  "spam_score": 100,
  "active_signals": ["brand_pattern", "contact_link"],
  "label": "spam"
}
```

| Kolom | Keterangan |
|-------|------------|
| `original_text` | Teks asli komentar, digunakan sebagai data latihan |
| `normalized_text` | Teks setelah normalisasi Unicode, digunakan untuk analisis |
| `spam_score` | Skor 0–100, semakin tinggi semakin mencurigakan |
| `active_signals` | Daftar sinyal yang aktif untuk komentar ini |
| `label` | Selalu `"spam"` — label ini akan diverifikasi secara manual |

---

### 3.2 Mesin Penilaian Spam (Heuristic Scoring)

Fungsi `analyzeSpamScore()` menganalisis setiap komentar menggunakan sistem **sinyal berlapis** dengan bobot yang berbeda-beda.

**Analogi:** Bayangkan sistem poin kecurigaan di bandara. Setiap perilaku mencurigakan menambah poin: membawa cairan lebih dari 100ml (+40 poin), terbang tanpa bagasi (+20 poin), beli tiket mendadak (+15 poin). Jika total poin melebihi ambang batas, penumpang diperiksa lebih lanjut. Scraper ini menggunakan logika yang serupa untuk komentar.

**Langkah awal — Normalisasi NFKC:**

Sebelum analisis dimulai, teks dinormalisasi menggunakan standar Unicode NFKC. Ini bertujuan "menghancurkan" font dekoratif yang sering dipakai spammer untuk menghindari filter:

```
"𝗦𝗟𝗢𝗧𝗚𝗔𝗖𝗢𝗥"  →  "SLOTGACOR"
"Ｇａｃｏｒ"    →  "Gacor"
"🅙🅤🅓🅘"      →  "JUDI"
```

**Tabel sinyal dan bobot:**

#### Sinyal Primer (bobot tinggi — wajib ada minimal 1)

| Sinyal | Poin | Contoh Pemicu |
|--------|------|---------------|
| `brand_pattern` | +40 | `MAXWIN88`, `SLOT777`, `BET138`, `WIFI4D` |
| `contact_link` | +40 | `wa.me/628xxx`, `bit.ly/xxx`, `cek profil`, `link di bio` |
| `soft_brand_testimonial` | +35 | `ALEXIS17 sukses bantu`, `HOKI99 terpercaya` |

> **Mengapa sinyal primer wajib ada?**
> Tanpa syarat ini, sebuah komentar normal seperti "KEREN BANGET HAHAHA 🎉🎊🎈" bisa mendapat skor tinggi hanya karena menggunakan capslock dan banyak emoji berjejer — padahal jelas bukan spam. Sinyal primer memastikan ada bukti kuat sebelum komentar dicap spam.

#### Sinyal Sekunder (bobot sedang)

| Sinyal | Poin | Contoh Pemicu |
|--------|------|---------------|
| `obfuscated_keyword` | +30 | `g a c o r`, `m@xw!n`, `z3u5` (kata judol yang sengaja disamarkan) |
| `plain_keyword` | +20 | `depo`, `wd`, `slot`, `scatter`, `mahjong`, `poker` |
| `high_symbol_ratio` | +20 | Jika lebih dari 15% karakter adalah simbol |

#### Sinyal Tersier (bobot rendah)

| Sinyal | Poin | Contoh Pemicu |
|--------|------|---------------|
| `emoji_spam` | +15 | `🎰💰🎁🔥` (2+ emoji berurutan) |
| `excessive_caps` | +10 | Lebih dari 50% huruf adalah kapital |

**Contoh perhitungan skor:**

```
Komentar: "MAXWIN88 daftar sekarang bonus 100% WA 08123456789"

brand_pattern  → MAXWIN88        → +40
contact_link   → 08123456789     → +40
plain_keyword  → daftar/bonus    → +20  (tidak aktif karena obfuscated sudah cukup)
excessive_caps → MAXWIN88        → +10
                              ─────────
                              TOTAL: 100 (batas maksimum)
active_signals: ["brand_pattern", "contact_link", "excessive_caps"]
hasPrimarySignal: true ✓ → SIMPAN
```

---

### 3.3 Mode Video vs. Mode Live Chat

Scraper mendukung dua mode pengumpulan data:

#### Mode Video (default)

Mengambil komentar dari video YouTube yang sudah selesai (tidak sedang live). Menggunakan endpoint `commentThreads` dari YouTube Data API.

- Mengambil **100 komentar per halaman** (maksimum yang diizinkan API)
- Berhenti otomatis ketika target terpenuhi atau semua halaman habis
- Memberi jeda 500ms antar permintaan untuk menghindari pemblokiran

#### Mode Live Chat

Memantau pesan spam dari live chat YouTube yang sedang berlangsung secara real-time. Menggunakan polling (pemeriksaan berkala) karena live chat terus berubah.

Proses dua tahap:
1. **Ambil Live Chat ID** dari data video
2. **Polling berkala** ke endpoint `liveChatMessages`

> **Mengapa ada jeda antar polling?**
> YouTube sendiri memberitahu kita harus menunggu berapa lama (`pollingIntervalMillis`) sebelum mengambil data berikutnya. Jika kita mengabaikan ini dan terus-terusan meminta data, API key bisa diblokir.

**Mekanisme retry (percobaan ulang):**

Jika server YouTube mengembalikan error `HTTP 429` (terlalu banyak permintaan), scraper tidak langsung menyerah. Ia menggunakan strategi **exponential backoff** — menunggu semakin lama di setiap percobaan:

```
Percobaan 1 gagal → tunggu 1 detik → coba lagi
Percobaan 2 gagal → tunggu 2 detik → coba lagi
Percobaan 3 gagal → tunggu 4 detik → coba lagi
Percobaan 4 gagal → berhenti, lempar error
```

**Analogi:** Ini seperti menelepon kantor yang sibuk. Jika tidak diangkat, Anda tidak langsung menelepon lagi setiap detik (itu mengganggu). Sebaliknya, Anda tunggu 1 menit, lalu 2 menit, lalu 4 menit — memberi waktu agar sibuknya reda.

---

### 3.4 Cara Menjalankan Scraper

**Prasyarat:**
- Node.js sudah terpasang
- Memiliki YouTube Data API v3 key dari Google Cloud Console
- File `.env` di root proyek dengan isi:

```
YOUTUBE_API_KEY=masukkan_api_key_anda_disini
SPAM_TARGET_COUNT=1500
```

**Perintah:**

```bash
# Scrape komentar video biasa
node scraper/index.js <VIDEO_ID>

# Contoh
node scraper/index.js z-BTQKhWrJc

# Scrape live chat
node scraper/index.js <VIDEO_ID> live
```

> **Cara mendapatkan VIDEO_ID:** Buka video YouTube, lihat URL-nya: `https://www.youtube.com/watch?v=`**`z-BTQKhWrJc`** — bagian setelah `?v=` itulah Video ID.

**Output:** File JSON disimpan di folder `scraper/result/` dengan nama seperti `spam_video_20250601103045_z-BTQKhWrJc.json`. File ini kemudian digabungkan secara manual menjadi `scraper/final_result.json` sebelum dilanjutkan ke tahap berikutnya.

---

## 4. Sistem 2 — Klasifikasi SVM

Subsistem kedua adalah inti dari proyek ini: melatih model AI yang mampu membedakan komentar spam dari komentar normal, lalu menyajikannya sebagai layanan yang bisa diakses browser extension.

### 4.1 Gambaran Pipeline Machine Learning

**Analogi besar:** Bayangkan Anda ingin mengajarkan asisten baru untuk menyortir surat spam. Anda lakukan langkah berikut:
1. **Kumpulkan contoh** — ambil 2.000 surat, separuh spam separuh normal.
2. **Bersihkan surat** — lepaskan amplop, rapikan kertas, baca hanya isinya.
3. **Ubah isi surat menjadi angka** — hitung berapa kali kata "bonus", "daftar", "WD" muncul.
4. **Latih asisten** — tunjukkan pola angka mana yang berasal dari surat spam vs normal.
5. **Uji asisten** — berikan surat yang belum pernah ia lihat, cek apakah ia bisa menyortir dengan benar.
6. **Simpan "ingatan" asisten** — agar besok tidak perlu dilatih ulang dari nol.

Itulah yang dilakukan pipeline machine learning dalam proyek ini.

---

### 4.2 Persiapan Dataset (`prepare_dataset.py`)

**Tujuan:** Mengubah file JSON hasil scraping menjadi file CSV bersih yang siap dilatih.

#### Langkah 1 — Filter spam dengan ambang batas skor 80

Tidak semua data dari scraper langsung digunakan. Hanya komentar dengan `spam_score >= 80` yang secara otomatis diterima. Ini karena:

- Komentar dengan skor rendah mungkin hanya memiliki sinyal lemah (misalnya banyak emoji saja)
- Skor >= 80 berarti ada kombinasi sinyal kuat yang cukup meyakinkan

**Pengecualian — Brand Rescue:**

Ada kasus khusus di mana brand judol nyata hanya memicu satu sinyal `brand_pattern` tanpa ada sinyal lain, sehingga skornya hanya 40 (di bawah 80). Contoh: `WIFI4D`, `BATRE4D`, `PELATIH4D`.

Untuk menyelamatkan entri ini, ada filter tambahan: jika `normalized_text` mengandung pola **huruf kapital semua + angka** (seperti `WIFI4D`), entri tetap disimpan. Kata Indonesia biasa yang kebetulan mengandung suku kata judol (seperti "keSAMBET" yang memiliki substring "bet") tidak akan memenuhi pola ini karena selalu huruf kecil.

#### Langkah 2 — Buat data non-spam sintetik

Karena scraper hanya mengumpulkan data spam, data non-spam dibuat secara sintetik dari ~180 template komentar YouTube yang normal (tutorial, gaming, musik, reaksi umum).

Sebanyak 700 komentar non-spam sintetik dibuat untuk mendampingi data spam. Rasio spam:non-spam sekitar 2:1, yang mencerminkan kondisi nyata kolom komentar YouTube di video-video yang diserang spam judol.

> **Mengapa tidak 1:1 (seimbang sempurna)?**
> Di dunia nyata, pada video yang diserang spam, komentar spam memang lebih banyak dari komentar normal. Melatih dengan rasio yang mencerminkan realitas membuat model lebih relevan untuk digunakan di kondisi nyata.

> **Catatan penting:** Data non-spam sintetik adalah solusi sementara. Jika tersedia data komentar non-spam nyata dari YouTube, gantikan data sintetik ini untuk meningkatkan akurasi model secara signifikan.

#### Langkah 3 — Gabung, acak, simpan ke CSV

Semua data digabungkan, diacak urutannya, dan disimpan ke `data/comments.csv` dengan dua kolom:

```csv
text,label
"MAXWIN88 daftar sekarang bonus 100%",spam
"Video ini sangat membantu buat belajar",non_spam
...
```

---

### 4.3 Pembersihan Teks / Preprocessing (`preprocessing.py`)

**Tujuan:** Membersihkan dan menyeragamkan teks mentah sebelum dimasukkan ke model.

**Mengapa ini penting?**

Model SVM bekerja dengan angka, bukan teks. Sebelum teks bisa diubah menjadi angka, ia harus dibersihkan agar:
- Kata yang sama tidak dianggap berbeda karena huruf besar-kecil ("Daftar" vs "daftar")
- Font dekoratif yang dipakai spammer tidak lolos begitu saja
- Emoji memberi informasi, bukan kekacauan

**Konsistensi training-inferensi:**

Fungsi `clean_text()` digunakan di **dua tempat**: saat melatih model (`train.py`) dan saat memprediksi komentar baru (`server.py`). Ini disengaja. Jika pembersihan teks dilakukan dengan cara berbeda antara pelatihan dan prediksi, model akan menerima input yang sedikit berbeda dari apa yang ia pelajari — akurasi akan turun. Prinsip ini disebut **training-serving consistency**.

**Analogi:** Bayangkan Anda melatih murid menggunakan soal-soal tertulis rapi. Tapi saat ujian, soalnya ditulis berantakan dengan coretan. Meski materinya sama, murid akan kesulitan karena format yang berbeda. Dengan menggunakan fungsi yang sama di kedua tahap, format soal latihan dan ujian selalu identik.

#### 7 Langkah Pipeline Preprocessing

**Langkah 1 — Hapus karakter tak terlihat (Zero-Width Characters)**

Spammer kadang menyisipkan karakter "tak kasat mata" di antara huruf untuk mengacaukan filter teks biasa. Karakter ini tidak terlihat di layar, tetapi secara teknis membuat kata menjadi berbeda.

```
Contoh: "d​a​f​t​a​r" (ada zero-width space di antara huruf)
Hasil  : "daftar" (setelah dibersihkan)
```

Karakter yang dihapus di langkah ini: zero-width space, zero-width non-joiner, zero-width joiner, Byte Order Mark (BOM), soft hyphen, left-to-right mark, dan right-to-left mark.

---

**Langkah 2 — Normalisasi Unicode NFKC**

Mengembalikan berbagai variasi font Unicode dekoratif menjadi karakter Latin standar.

**Analogi:** Bayangkan seseorang menulis nama "ROMA4D" menggunakan font mewah bergaya kalilgrafi. Walau terlihat berbeda secara visual, maknanya sama. NFKC "mengubah" semua variasi font itu kembali ke huruf biasa.

```
"𝑅𝒪𝑀𝒜𝟦𝒟"  →  "ROMA4D"    (font Mathematical Italic)
"Ｄａｆｔａｒ"  →  "Daftar"    (full-width Latin)
"🅓🅐🅕🅣🅐🅡"  →  "DAFTAR"    (Enclosed Alphanumeric)
```

---

**Langkah 3 — Perbaiki Karakter Homoglif Cyrillic/Yunani**

NFKC tidak bisa menangani karakter dari alfabet yang berbeda yang kebetulan terlihat sama. Spammer memanfaatkan ini dengan mengganti huruf Latin dengan huruf Cyrillic yang tampak identik.

```
"dаftаr" (menggunakan huruf 'а' Cyrillic U+0430)
"daftar" (menggunakan huruf 'a' Latin U+0061)
```

Secara visual kedua kata di atas terlihat sama, tetapi komputer menganggapnya berbeda. Langkah ini memetakan karakter Cyrillic dan Yunani yang paling sering disalahgunakan ke padanan Latin-nya.

| Karakter Asli | Alfabet | Karakter Pengganti |
|---|---|---|
| а (U+0430) | Cyrillic | a |
| е (U+0435) | Cyrillic | e |
| о (U+043E) | Cyrillic | o |
| с (U+0441) | Cyrillic | c |
| ο (U+03BF) | Yunani | o |
| α (U+03B1) | Yunani | a |

---

**Langkah 4 — Konversi Emoji ke Teks**

Daripada menghapus emoji sepenuhnya, emoji diubah menjadi deskripsi teksnya menggunakan library `emoji`.

**Mengapa tidak dihapus saja?**

Karena emoji tertentu adalah sinyal kuat. Jika 🎰 (mesin slot) dan 💰 (kantong uang) selalu dihapus, model kehilangan informasi berharga. Sebaliknya, mengubahnya menjadi kata membuat TF-IDF bisa menghitungnya sebagai fitur.

```
🎰 → slot_machine    (sinyal spam kuat)
💰 → money_bag       (sinyal spam kuat)
👍 → thumbs_up       (netral / non-spam)
```

Tanda titik dua (`:slot_machine:`) dihapus agar tersisa token bersih `slot machine`.

---

**Langkah 5 — Ubah ke Huruf Kecil**

Menyeragamkan semua huruf menjadi kecil agar "Daftar", "DAFTAR", dan "daftar" dianggap kata yang sama.

---

**Langkah 6 — Hapus URL dan Karakter Non-Alfabetik**

URL (tautan web) dihapus karena tidak relevan untuk analisis teks. Semua karakter selain huruf a-z dan spasi juga dihapus — termasuk angka, tanda baca, dan simbol sisa.

```
"kunjungi https://bit.ly/spam123 daftar!!!" → "kunjungi daftar"
```

---

**Langkah 7 — Hapus Stopword dan Token Pendek**

*Stopword* adalah kata-kata yang sangat umum dan tidak memberi informasi pembeda — seperti "yang", "dan", "di", "itu". Kata-kata ini muncul hampir di setiap komentar, baik spam maupun bukan, sehingga keberadaannya justru mengaburkan pola yang ingin dipelajari model.

**Analogi:** Jika Anda ingin membedakan resep masakan dari berita olahraga, kata "dan", "adalah", "untuk" tidak berguna karena ada di mana-mana. Yang berguna adalah kata-kata unik seperti "garam", "gol", "striker".

Token dengan panjang 1 karakter juga dihapus karena tidak bermakna sebagai fitur.

**Contoh lengkap perjalanan sebuah komentar melalui 7 langkah:**

```
INPUT  : "𝗦𝗟𝗢𝗧 G A C O R 🎰💰 dаftаr sekаrаng bonus besar!!!"

Langkah 1: Hapus zero-width → tidak ada perubahan
Langkah 2: NFKC           → "SLOT G A C O R 🎰💰 dаftаr sekаrаng bonus besar!!!"
Langkah 3: Homoglif       → "SLOT G A C O R 🎰💰 daftar sekarang bonus besar!!!"
Langkah 4: Demojize       → "SLOT G A C O R  slot_machine  money_bag  daftar sekarang bonus besar!!!"
Langkah 5: Lowercase      → "slot g a c o r  slot_machine  money_bag  daftar sekarang bonus besar!!!"
Langkah 6: Hapus non-alfa → "slot g a c o r  slot machine  money bag  daftar sekarang bonus besar"
Langkah 7: Stopword       → "slot gacor slot machine money bag daftar bonus besar"

OUTPUT : "slot gacor slot machine money bag daftar bonus besar"
```

---

### 4.4 Pelatihan Model (`train.py`)

**Tujuan:** Melatih model SVM menggunakan dataset yang sudah disiapkan, mengevaluasi performanya, dan menyimpannya ke disk.

Pelatihan berjalan dalam **5 tahap berurutan:**

#### Tahap 1 — Muat Dataset

Membaca `data/comments.csv`, memvalidasi kolom yang diperlukan (`text` dan `label`), dan menghapus baris yang kosong.

#### Tahap 2 — Preprocessing

Menjalankan semua teks melalui fungsi `clean_text()` dari `preprocessing.py` (7 langkah yang sudah dijelaskan di atas).

#### Tahap 3 — Pembagian Data (Train-Test Split)

Dataset dibagi menjadi:
- **80% data latih** — digunakan model untuk belajar
- **20% data uji** — digunakan untuk mengukur performa model pada data yang belum pernah dilihat

**Mengapa harus dipisah?**

**Analogi:** Bayangkan guru yang memberikan latihan soal selama satu semester, lalu ujian akhirnya menggunakan soal yang *persis sama* dengan latihan. Nilai ujian pasti tinggi, tapi itu tidak mencerminkan kemampuan sebenarnya. Siswa yang benar-benar paham akan bisa mengerjakan soal *baru*, bukan hanya mengingat soal lama.

Parameternya:
- `test_size=0.2` — 20% untuk pengujian
- `random_state=42` — benih acak yang tetap agar pembagian bisa direproduksi
- `stratify=y` — menjaga proporsi spam/non-spam tetap sama di kedua bagian

#### Tahap 4 — Membangun dan Melatih Pipeline

Model dibangun sebagai **Pipeline** yang terdiri dari dua tahap berurutan:

```
Teks bersih  →  [TF-IDF Vectorizer]  →  Vektor angka  →  [SVM]  →  Label prediksi
```

**A. TF-IDF Vectorizer**

TF-IDF (Term Frequency - Inverse Document Frequency) adalah cara mengubah teks menjadi angka yang bermakna.

**Analogi:** Bayangkan Anda membuat laporan keunikan setiap kata dalam sebuah buku. Kata "dan" ada di setiap halaman — tidak unik, tidak penting. Kata "mahjong" mungkin hanya muncul di 3 halaman dari 1.000 — sangat unik dan bermakna. TF-IDF memberikan nilai tinggi pada kata yang sering muncul di dokumen tertentu tetapi jarang di dokumen lain.

Parameter yang digunakan:
| Parameter | Nilai | Penjelasan |
|-----------|-------|------------|
| `max_features` | 10.000 | Hanya gunakan 10.000 kata paling relevan |
| `ngram_range` | (1,2) | Hitung kata tunggal DAN pasangan kata (bigram), misalnya "daftar sekarang" sebagai satu fitur |
| `min_df` | 2 | Abaikan kata yang muncul kurang dari 2 dokumen (terlalu langka, kemungkinan typo) |
| `sublinear_tf` | True | Gunakan log dari frekuensi kata, agar kata yang muncul 100x tidak 100x lebih penting dari yang muncul 1x |

**B. Support Vector Machine (SVM)**

SVM adalah algoritma yang mencari **garis pemisah terbaik** antara dua kelas (spam vs non-spam).

**Analogi:** Bayangkan Anda memiliki sekumpulan titik merah (spam) dan titik biru (non-spam) yang tersebar di sebuah kertas. SVM mencari garis lurus yang **paling jauh** dari titik merah maupun biru — garis yang memberi ruang (margin) terbesar di kedua sisi. Semakin lebar margin, semakin yakin model dalam memisahkan kedua kelas.

```
  Titik spam          Garis pemisah         Titik non-spam
  ● ●                                            ○ ○
    ●  ← margin →   ───────────   ← margin →  ○
  ● ●                                            ○ ○
```

Parameter yang digunakan:
| Parameter | Nilai | Penjelasan |
|-----------|-------|------------|
| `kernel` | `linear` | Garis pemisah berbentuk lurus — cocok untuk data teks berdimensi tinggi |
| `C` | `1.0` | Seberapa ketat model mengikuti data latihan (lebih rendah = lebih generalis) |
| `class_weight` | `balanced` | Otomatis menyeimbangkan penalti untuk kelas yang lebih sedikit jumlahnya |
| `probability` | `True` | Mengaktifkan skor kepercayaan (confidence) selain label saja |

**Mengapa Pipeline, bukan dua langkah terpisah?**

Menggunakan Pipeline memastikan TF-IDF **hanya belajar dari data latihan**, bukan dari data uji. Jika TF-IDF dilatih pada seluruh dataset sebelum pembagian, ia akan "mengintip" data uji secara tidak langsung — masalah yang disebut **data leakage** (kebocoran data). Pipeline secara otomatis mencegah hal ini.

#### Tahap 5 — Evaluasi Model

Setelah pelatihan, model diuji pada 20% data uji. Laporan evaluasi mencakup:

**Accuracy (Akurasi):** Persentase prediksi yang benar secara keseluruhan.

**Precision, Recall, dan F1-Score:**

| Metrik | Pertanyaan yang dijawab | Rumus |
|--------|------------------------|-------|
| Precision | Dari semua yang diprediksi spam, berapa persen yang benar-benar spam? | TP / (TP + FP) |
| Recall | Dari semua spam yang sebenarnya ada, berapa persen yang berhasil terdeteksi? | TP / (TP + FN) |
| F1-Score | Rata-rata harmonik dari Precision dan Recall | 2 × (P × R) / (P + R) |

**Analogi:**
- **Precision** = seberapa tepat jaring yang kita lempar (berapa banyak ikan yang tertangkap memang ikan yang kita inginkan, bukan sampah)
- **Recall** = seberapa lengkap tangkapan kita (berapa banyak ikan yang ingin kita tangkap berhasil masuk ke jaring, bukan lolos)
- **F1-Score** = nilai tunggal yang menyeimbangkan keduanya

**Confusion Matrix:**

```
                    Diprediksi: non_spam | Diprediksi: spam
Sebenarnya: non_spam |   TN ✓ (benar)   |  FP ✗ (false alarm)
Sebenarnya: spam     |   FN ✗ (lolos)   |  TP ✓ (benar)
```

- **TN (True Negative)** — komentar normal, diprediksi normal ✓
- **TP (True Positive)** — komentar spam, diprediksi spam ✓
- **FP (False Positive)** — komentar normal, diprediksi spam ✗ (false alarm)
- **FN (False Negative)** — komentar spam yang lolos tidak terdeteksi ✗ (paling berbahaya)

#### Tahap 6 — Simpan Model

Model yang sudah dilatih disimpan ke `model/svm_model.joblib` menggunakan library `joblib`. File ini adalah "ingatan" dari semua yang sudah dipelajari model.

---

### 4.5 Server API (`server.py`)

**Tujuan:** Menyajikan model SVM yang sudah dilatih sebagai layanan HTTP yang bisa dipanggil browser extension.

**Mengapa perlu server?**

Browser extension ditulis dalam JavaScript. JavaScript tidak bisa langsung menggunakan library Python seperti scikit-learn. Solusinya adalah membuat server Python yang bertindak sebagai **jembatan**: extension mengirim teks komentar ke server, server memproses dengan model SVM Python, dan mengembalikan hasilnya sebagai JSON.

```
Extension (JS)  →  POST /predict  →  Server (Python)  →  Model SVM  →  JSON
```

**Analogi:** Ini seperti menggunakan mesin penerjemah melalui telepon. Anda berbicara dalam bahasa Indonesia (JavaScript), mesin menerjemahkan ke bahasa Inggris (Python/scikit-learn), dan mengembalikan hasilnya ke Anda.

#### Model Dimuat Sekali Saat Server Mulai

Model SVM tidak dimuat ulang setiap kali ada permintaan baru. Ia dimuat **satu kali** saat server pertama kali berjalan (`startup_event`), kemudian disimpan di memori. Ini penting untuk performa: memuat model dari disk membutuhkan waktu ratusan milidetik — jika dilakukan setiap permintaan, API akan sangat lambat.

#### Endpoint yang Tersedia

**`GET /`** — Cek status server

```json
{
  "status": "online",
  "message": "Spam Detector API is running. Use POST /predict to classify a comment."
}
```

**`GET /health`** — Cek apakah model sudah dimuat

```json
{
  "status": "ok",
  "model_loaded": true
}
```

**`POST /predict`** — Klasifikasi satu komentar

Request:
```json
{
  "text": "MAXWIN88 daftar sekarang bonus 100% WA 0812xxxx"
}
```

Response:
```json
{
  "label": "spam",
  "confidence": 0.9743,
  "is_spam": true
}
```

| Field | Tipe | Keterangan |
|-------|------|------------|
| `label` | string | `"spam"` atau `"non_spam"` |
| `confidence` | float | Tingkat keyakinan model (0.0 – 1.0) |
| `is_spam` | boolean | Shortcut: `true` jika `label == "spam"` |

**`POST /predict/batch`** — Klasifikasi banyak komentar sekaligus (maks. 50)

Request:
```json
{
  "texts": [
    "MAXWIN88 daftar sekarang bonus 100%",
    "Video ini sangat membantu belajar",
    "Slot gacor hari ini WD cepat"
  ]
}
```

Response:
```json
{
  "results": [
    {"label": "spam",     "confidence": 0.9743, "is_spam": true},
    {"label": "non_spam", "confidence": 0.9821, "is_spam": false},
    {"label": "spam",     "confidence": 0.8912, "is_spam": true}
  ]
}
```

**Mengapa ada endpoint batch?**

Lebih efisien dari memanggil `/predict` satu per satu. Ketika extension memuat halaman YouTube dengan 30 komentar, ia cukup satu kali kirim permintaan batch — bukan 30 permintaan terpisah. Ini mengurangi latensi total secara signifikan.

#### Validasi Input

Sebelum teks diteruskan ke model, server melakukan validasi:
- Teks tidak boleh kosong atau hanya berisi spasi
- Teks tidak boleh lebih dari 5.000 karakter
- Jika teks menjadi kosong setelah preprocessing (misalnya input hanya emoji murni), server mengembalikan `non_spam` dengan confidence 0.5 (tidak yakin)

#### CORS (Cross-Origin Resource Sharing)

Browser secara default memblokir permintaan dari satu origin (misalnya extension Chrome) ke origin lain (localhost:8000). Header CORS dikirim server agar browser mengizinkan komunikasi ini.

> **Catatan keamanan:** Konfigurasi saat ini mengizinkan semua origin (`allow_origins=["*"]`). Untuk deployment produksi, ganti dengan ID extension yang spesifik.

---

### 4.6 Browser Extension

**File:** `extension/manifest.json`

Extension browser bertugas memantau halaman YouTube, mengambil teks komentar yang terlihat, mengirimkannya ke server API, dan menyembunyikan komentar yang terdeteksi sebagai spam.

Extension menggunakan standar **Manifest Version 3** (terbaru) dengan izin berikut:

| Izin | Fungsi |
|------|--------|
| `storage` | Menyimpan pengaturan pengguna (misal: aktif/nonaktif) |
| `activeTab` | Mengakses tab yang sedang aktif |
| `https://www.youtube.com/*` | Izin untuk berjalan di halaman YouTube |
| `https://www.instagram.com/*` | Izin untuk berjalan di halaman Instagram |
| `http://localhost:8000/*` | Izin untuk berkomunikasi dengan server lokal |

**Content Script (`content.js`)** berjalan secara otomatis di setiap halaman YouTube/Instagram setelah halaman selesai dimuat (`document_idle`). Script ini yang bertanggung jawab mendeteksi elemen komentar di DOM halaman dan berinteraksi dengan server API.

---

## 5. Alur Kerja Lengkap dari Awal Hingga Akhir

```
TAHAP 1: PENGUMPULAN DATA
────────────────────────
1. Jalankan scraper untuk beberapa video YouTube yang penuh spam judol
2. Hasil tersimpan di scraper/result/*.json
3. Gabungkan semua file menjadi scraper/final_result.json

TAHAP 2: PERSIAPAN DATASET
──────────────────────────
4. Jalankan: python src/prepare_dataset.py
5. Script membaca final_result.json, filter skor >= 80
6. Tambah 700 data non-spam sintetik
7. Simpan ke data/comments.csv

TAHAP 3: PELATIHAN MODEL
─────────────────────────
8. Jalankan: python src/train.py
9. Baca comments.csv → preprocessing → TF-IDF → SVM
10. Evaluasi pada 20% data uji
11. Simpan model ke model/svm_model.joblib

TAHAP 4: MENJALANKAN SERVER
─────────────────────────────
12. Jalankan: python src/server.py
13. Server memuat model dari disk
14. API tersedia di http://localhost:8000

TAHAP 5: INSTALASI EXTENSION
─────────────────────────────
15. Buka Chrome → chrome://extensions
16. Aktifkan "Developer mode"
17. Klik "Load unpacked" → pilih folder extension/
18. Extension aktif, siap mendeteksi spam di YouTube
```

---

## 6. Struktur Direktori Proyek

```
svm-judol-spam/
│
├── scraper/
│   ├── index.js            ← Scraper komentar YouTube
│   └── final_result.json   ← Hasil scraping gabungan (input untuk prepare_dataset.py)
│
├── src/
│   ├── prepare_dataset.py  ← Konversi JSON → CSV
│   ├── preprocessing.py    ← Pembersihan teks (7 langkah)
│   ├── train.py            ← Pelatihan model SVM
│   └── server.py           ← FastAPI server (REST API)
│
├── extension/
│   ├── manifest.json       ← Konfigurasi browser extension
│   ├── content.js          ← Script yang berjalan di halaman YouTube (belum ada)
│   ├── popup.html          ← UI popup extension (belum ada)
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
│
├── data/
│   └── comments.csv        ← Dataset hasil prepare_dataset.py (dibuat otomatis)
│
├── model/
│   └── svm_model.joblib    ← Model terlatih (dibuat otomatis oleh train.py)
│
└── env/                    ← Virtual environment Python (jangan dimodifikasi)
```

---

## 7. Cara Menjalankan Sistem Secara Keseluruhan

### Prasyarat

- Python 3.8 atau lebih baru
- Node.js 18 atau lebih baru
- YouTube Data API v3 key (dari Google Cloud Console)
- Browser Google Chrome

### Langkah 1 — Instalasi dependensi Python

```bash
# Aktifkan virtual environment (Windows)
env\Scripts\activate

# Install library yang dibutuhkan
pip install fastapi uvicorn scikit-learn pandas joblib emoji pydantic
```

### Langkah 2 — Instalasi dependensi Node.js

```bash
cd scraper
npm install
```

### Langkah 3 — Konfigurasi API key

Buat file `.env` di root proyek:

```
YOUTUBE_API_KEY=masukkan_api_key_anda_disini
SPAM_TARGET_COUNT=1500
```

### Langkah 4 — Scraping data

```bash
node scraper/index.js <VIDEO_ID>
```

Ulangi untuk beberapa video. Setelah selesai, gabungkan semua file `*.json` di folder `scraper/result/` menjadi satu file `scraper/final_result.json`.

### Langkah 5 — Persiapan dataset

```bash
python src/prepare_dataset.py
```

### Langkah 6 — Pelatihan model

```bash
python src/train.py
```

### Langkah 7 — Jalankan server API

```bash
python src/server.py
```

Server akan berjalan di `http://localhost:8000`. Dokumentasi API interaktif tersedia di `http://localhost:8000/docs`.

### Langkah 8 — Instalasi extension

1. Buka `chrome://extensions` di browser Chrome
2. Aktifkan toggle **"Developer mode"** di pojok kanan atas
3. Klik **"Load unpacked"**
4. Pilih folder `extension/` dari proyek ini
5. Extension akan muncul di toolbar browser

---

## 8. Konsep Teknis Penting

### Apa itu Support Vector Machine (SVM)?

SVM adalah algoritma klasifikasi yang mencari **hyperplane** (bidang pemisah) terbaik antara dua kelas data. "Terbaik" berarti hyperplane yang memberikan **margin terlebar** ke titik data terdekat dari masing-masing kelas (disebut *support vectors*).

Untuk data teks, dimensinya sangat tinggi (10.000 fitur dari TF-IDF) — terlalu banyak untuk divisualisasikan. Tapi prinsipnya sama: SVM menemukan pemisah yang paling tegas antara "teks spam" dan "teks normal" di ruang 10.000 dimensi tersebut.

SVM dipilih untuk tugas ini karena:
1. **Performa baik pada teks** — terbukti secara empiris unggul untuk klasifikasi dokumen
2. **Efisien pada data berdimensi tinggi** — tidak kerepotan dengan ribuan fitur
3. **Generalisasi baik** — margin yang lebar berarti model tidak hanya menghafal data latihan

### Apa itu TF-IDF?

TF-IDF adalah cara mengubah teks menjadi angka berdasarkan kepentingan relatif setiap kata.

- **TF (Term Frequency)** — Seberapa sering kata ini muncul dalam dokumen ini?
- **IDF (Inverse Document Frequency)** — Seberapa langka kata ini di seluruh koleksi dokumen?

```
Nilai TF-IDF = TF × IDF
```

Kata yang sering muncul di satu dokumen tetapi jarang di dokumen lain mendapat nilai tinggi → kata tersebut karakteristik dan bermakna untuk dokumen itu.

Kata yang muncul di hampir semua dokumen (seperti "yang", "dan") mendapat nilai rendah → tidak memberi informasi pembeda.

### Apa itu Training-Serving Consistency?

Prinsip bahwa **transformasi yang sama harus diterapkan pada teks saat pelatihan dan saat prediksi**. Jika ada perbedaan sekecil apapun (misalnya urutan langkah yang berbeda, atau penanganan Unicode yang berbeda antara Python dan JavaScript), model akan menerima input yang sedikit berbeda dari format yang ia pelajari, sehingga akurasi turun.

Itulah mengapa preprocessing seluruhnya dilakukan di Python, bukan di JavaScript di sisi extension.

### Apa itu Data Leakage?

Kesalahan metodologi di mana informasi dari data uji "bocor" ke proses pelatihan. Ini membuat evaluasi model terlihat lebih bagus dari kemampuan sebenarnya di dunia nyata.

Contoh kasus: Jika TF-IDF dilatih pada seluruh dataset (termasuk data uji) sebelum pembagian, ia akan "tahu" kata-kata apa yang ada di data uji. Ketika dievaluasi, ia secara tidak adil sudah mengenal data tersebut. Solusinya adalah menggunakan Pipeline yang menjamin TF-IDF hanya dilatih pada data latihan.

---

## 9. Batasan dan Catatan Pengembangan

### Batasan Saat Ini

1. **Data non-spam sintetik** — Data non-spam dihasilkan dari template, bukan dari scraping nyata. Model mungkin kurang akurat menangani variasi komentar non-spam di dunia nyata yang lebih beragam. Prioritaskan penggantian dengan data nyata.

2. **Content script belum ada** — File `content.js` dan `popup.html` untuk extension belum diimplementasikan. Extension saat ini hanya memiliki konfigurasi `manifest.json`.

3. **Server hanya lokal** — Server berjalan di `localhost` dan hanya bisa diakses dari komputer yang sama. Untuk deployment yang lebih luas, server perlu di-host di infrastruktur cloud.

4. **CORS terbuka** — `allow_origins=["*"]` mengizinkan semua origin. Untuk keamanan, batasi hanya ke ID extension Chrome yang spesifik setelah extension dipublikasikan.

5. **Label awal scraper belum diverifikasi** — Komentar yang dikumpulkan scraper diberi label `"spam"` secara otomatis. Verifikasi manual sangat disarankan untuk memastikan kualitas data latihan.

### Rekomendasi Pengembangan Berikutnya

| Prioritas | Item | Dampak |
|-----------|------|--------|
| Tinggi | Ganti data non-spam sintetik dengan data scraping nyata | Meningkatkan akurasi signifikan |
| Tinggi | Implementasi `content.js` dan `popup.html` | Extension bisa berfungsi penuh |
| Sedang | Tambah endpoint `/feedback` agar pengguna bisa melaporkan prediksi yang salah | Memungkinkan pelatihan ulang dengan data yang lebih baik |
| Sedang | Verifikasi manual dataset spam yang dikumpulkan scraper | Mengurangi label noise |
| Rendah | Integrasi stopword library Sastrawi | Preprocessing bahasa Indonesia lebih komprehensif |
| Rendah | Tambah logging ke file untuk monitoring produksi | Memudahkan debugging |

---

*Dokumentasi ini ditulis berdasarkan analisis kode sumber versi pertama proyek. Perbarui dokumen ini setiap kali ada perubahan arsitektur yang signifikan.*
