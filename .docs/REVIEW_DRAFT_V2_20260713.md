# Review Draft Skripsi V2 — `[DRAFT] 221232017 - 20260713.pdf`

**Tanggal review:** 13 Juli 2026
**Reviewer:** Claude (cross-check ke kode & data live di repo)
**Cakupan:** 124 halaman, BAB I–V + Daftar Pustaka. Semua angka empiris dicocokkan ke `data/`, `src/`, `reports/`, `extension/`, `scraper/`.

---

## 0. Ringkasan Eksekutif

Kabar baik dulu: draft V2 ini **jauh lebih matang** dari V1. BAB V, Abstrak, sub-bab 4.9–4.12, use case narrative, sequence/activity diagram — semua sudah terisi. Semua **angka statistik terverifikasi akurat** terhadap data live (97,53% / F1 0,9726 / CV 0,9741±0,30% / hard set 98,52% 2 FP / ablation hibrida / dll). Dua sitasi prior work paling krusial (Angelo 2025 & Airlangga 2024) juga **terverifikasi asli dan angkanya benar**.

Tapi ada **5 temuan kritis** yang wajib dibereskan sebelum sidang, plus isu italic yang cukup banyak. Urutan prioritas ada di [Bagian 7](#7-checklist-prioritas).

| # | Temuan | Tingkat | Sifat |
|---|--------|---------|-------|
| K1 | Cross-reference nomor tabel salah di 4.11 (nyebut Tabel 4.4–4.7, harusnya 4.9–4.12) | 🔴 Kritis | Pasti ketahuan penguji |
| K2 | Kontradiksi angka stemming: 4.5.5 tulis **+0,0002**, 4.11.7 tulis **−0,0006** | 🔴 Kritis | Kontradiksi internal |
| K3 | Kode ekstensi masih `localhost:8000`, tapi tesis klaim deploy **VPS** | 🔴 Kritis | Klaim vs realita kode |
| K4 | 2.11 mendefinisikan pengumpulan data sebagai "web scraping" (parsing HTML), padahal kode & bab lain pakai **YouTube Data API v3** (JSON) | 🟠 Penting | Kontradiksi konseptual |
| K5 | Sitasi hilang & orphan di Daftar Pustaka (Arrayyan, Efrizoni, Somantri) | 🟠 Penting | Integritas referensi |
| I1 | Italic istilah asing tidak konsisten (banyak) | 🟡 Sedang | Format pedoman 4.2.9 |

---

## 1. Temuan Kritis

### 🔴 K1 — Nomor tabel di sub-bab 4.11 salah rujuk (off-by-5)

Ini temuan paling gampang ketahuan penguji. Di BAB IV, **Tabel 4.4–4.8 dipakai untuk Use Case Narrative** (4.7). Waktu nulis sub-bab pengujian (4.11), penomoran belum digeser, jadi teksnya masih nyebut nomor lama:

| Lokasi (hal.) | Teks draft menyebut | Tabel sebenarnya di bawahnya | Perbaikan |
|---|---|---|---|
| 4.11.1 (hal. 94) | "Hasil evaluasi disajikan pada **Tabel 4.4**." | Tabel 4.9 Hasil Evaluasi Model SVM | → **Tabel 4.9** |
| 4.11.1 (hal. 95) | "confusion matrix pada **Tabel 4.5**." | Tabel 4.10 Confusion Matrix | → **Tabel 4.10** |
| 4.11.4 (hal. 98) | "Hasil perbandingan disajikan pada **Tabel 4.6**." | Tabel 4.11 Perbandingan Baseline | → **Tabel 4.11** |
| 4.11.6 (hal. 99) | "Hasilnya disajikan pada **Tabel 4.7**." | Tabel 4.12 SVM Murni vs Hibrida | → **Tabel 4.12** |

Kalau dibiarkan, teks "lihat Tabel 4.4" malah nunjuk ke *Use Case Narrative Menyaring Komentar Spam* — salah total. **Wajib diperbaiki.**

> Saran: setelah dibetulkan, pakai fitur cross-reference Word (Insert → Cross-reference) supaya nomor auto-update dan gak kejadian lagi.

---

### 🔴 K2 — Kontradiksi angka stemming (+0,0002 vs −0,0006)

- **Sub-bab 4.5.5** (hal. 74): *"...peningkatan F1-macro yang tidak signifikan sebesar **+0,0002**..."* → berarti stemming **sedikit lebih baik**.
- **Sub-bab 4.11.7** (hal. 100): *"...rata-rata F1-macro dengan stemming justru **sedikit lebih rendah (selisih −0,0006)**, dan 4 dari 5 fold ... lebih buruk ... p-value = 0,3575..."* → berarti stemming **sedikit lebih buruk**.

Dua sub-bab ini membahas **eksperimen yang sama** tapi kasih arah kesimpulan berlawanan (naik vs turun). Angka yang **benar** (sesuai `reports/experiment_stemming_cv.png` + script `experiment_stemming.py`, memakai paired t-test 5-fold) adalah **−0,0006, p=0,3575, 4/5 fold lebih buruk**. Angka **+0,0002 di 4.5.5 adalah sisa dari draft lama** (kemungkinan dari single split 80/20, bukan CV).

**Perbaikan:** samakan 4.5.5 dengan 4.11.7. Karena 4.5.5 memang cuma "pengantar" yang menunda detail ke 4.11.7, cukup ubah kalimatnya jadi netral, misalnya:

> "...hasil eksperimen menunjukkan stemming **tidak memberikan peningkatan performa yang signifikan** (dibahas rinci pada sub-bab pengujian), sehingga stemming diputuskan tidak diintegrasikan ke pipeline produksi."

Jangan tulis angka spesifik di 4.5.5 kalau angkanya beda sama 4.11.7.

---

### 🔴 K3 — Kode ekstensi masih `localhost`, tesis klaim VPS

Tesis konsisten & tegas menyatakan server di-deploy ke **VPS Ubuntu 24.04** yang diakses lewat internet:

- 4.1.2 Keamanan: *"Server API di-deploy pada infrastruktur Virtual Private Server (VPS)..."*
- Tabel 4.1 & 4.2: Ubuntu Server 24.04 LTS, spesifikasi VPS (2 vCPU, 2 GB, 40 GB SSD)
- 4.6.3, 4.12.1, Abstrak, 4.4.2: semua bilang server jalan di VPS via internet
- Kebutuhan Fungsional #2: *"...melalui jaringan internet..."*

Tapi kode yang ada di repo **masih hardcode localhost**:

| File | Baris | Isi |
|---|---|---|
| `extension/content.js` | 29–30 | `http://localhost:8000/predict` & `/predict/batch` |
| `extension/content.js` | 94, 235 | `http://localhost:8000/health`, `/report` |
| `extension/popup.js` | 8 | `API_BASE = "http://localhost:8000"` |
| `extension/popup.html` | 271 | teks status `localhost:8000` |
| `extension/manifest.json` | 13 | `host_permissions` cuma izinin `http://localhost:8000/*` |

**Konsekuensi:** kalau penguji minta demo live atau buka popup, yang muncul `localhost:8000` — kontradiksi langsung sama narasi VPS. Ekstensi seperti sekarang **secara teknis gak bisa** ngobrol ke VPS (host_permissions gak mengizinkan).

**Pilihan (keputusan lu):**
1. **Kalau VPS beneran dipakai** → ganti 5 titik di atas dengan IP/domain VPS asli sebelum sidang. Gua bisa bantu edit kalau lu kasih alamatnya.
2. **Kalau demo tetap di localhost** → turunkan klaim VPS di tesis jadi "dapat di-deploy ke VPS (dalam skripsi ini dijalankan di lingkungan lokal untuk pengujian)". Lebih jujur & aman.

⚠️ Jangan biarkan status quo (tesis bilang VPS, kode bilang localhost).

---

### 🟠 K4 — "Web scraping" vs "YouTube Data API v3"

Sub-bab **2.11** berjudul "Web Scraping dan Analisis Heuristik" dan mendefinisikan metodenya sebagai:

> *"...mengirimkan permintaan protokol jaringan ke peladen situs web, kemudian **memuat struktur kode HTML secara utuh, dan mem-parsing elemen-elemen spesifik**... Pada arsitektur sistem ini, **web scraping** berjalan ... melalui Node.js untuk mengekstraksi komentar..."*

Padahal implementasi asli (`scraper/index.js` baris 348) memakai **YouTube Data API v3** resmi:
```
https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=...&key=API_KEY
```
Ini **request API yang balikin JSON**, bukan parsing HTML. Dan semua bab lain (Abstrak, 1.4.2, 4.3.1, 4.12.3) sudah benar menyebut "YouTube Data API v3". Jadi 2.11 satu-satunya yang framing-nya keliru — dan ini yang paling gampang dicecar ("Jadi ini scraping HTML atau pakai API resmi, Mas?").

**Perbaikan:** revisi 2.11 supaya definisi web scraping tetap ada sebagai teori umum, TAPI perjelas bahwa penelitian ini memakai **API resmi** sebagai bentuk pengumpulan data terstruktur, bukan HTML parsing. Contoh kalimat penutup 2.11:

> "Dalam penelitian ini, pengumpulan data tidak dilakukan melalui parsing HTML mentah, melainkan melalui **YouTube Data API v3** — antarmuka resmi yang mengembalikan data komentar dalam format JSON terstruktur — yang secara konsep tetap merupakan otomatisasi pengumpulan data, namun lebih andal dan sah secara ketentuan layanan."

Ini juga bikin klaim "Kelayakan Hukum" (4.12.3) makin kuat & konsisten.

---

### 🟠 K5 — Sitasi hilang & orphan di Daftar Pustaka

| Sitasi | Muncul di | Status |
|---|---|---|
| **Arrayyan dkk., 2025** | body hal. 15 (sub-bab 2.5, TF-IDF) | ❌ **TIDAK ADA** di Daftar Pustaka |
| **Efrizoni dkk., 2022** | body hal. 15 (sub-bab 2.5, perbandingan BoW/Doc2Vec) | ❌ **TIDAK ADA** di Daftar Pustaka |
| **Somantri, Wiyono & Dairoh (2020)** | Daftar Pustaka hal. 122 | ⚠️ **Orphan** — gak dikutip di mana pun di body |

**Perbaikan:**
- Tambahkan entri lengkap Arrayyan (2025) & Efrizoni (2022) ke Daftar Pustaka — **atau** kalau lupa sumbernya, ganti sitasinya dengan referensi TF-IDF yang sudah ada (mis. Ardiansyah dkk., 2025 / Efrizoni sudah dipakai — cari yang beneran ada di daftar).
- Somantri (2020): entah dikutip di body (kalau relevan, tambah sitasinya), entah dihapus dari Daftar Pustaka. Referensi yang gak dikutip = temuan klasik penguji.

> Cek juga manual: pastikan **semua** nama di body ada di Daftar Pustaka dan sebaliknya. Tiga ini yang gua temukan lewat scan otomatis, tapi worth di-sweep sekali lagi manual.

---

## 2. Verifikasi Kesesuaian Draft ↔ Project Real

Semua dicocokkan langsung ke kode/data. **Semua cocok** kecuali yang sudah ditandai di Bagian 1.

| Klaim di draft | Sumber verifikasi | Status |
|---|---|---|
| Dataset 2.332 spam / 4.358 non-spam / 6.690 total | `data/comments.csv` (dihitung) | ✅ Persis |
| Split 80:20 → 5.352 latih / 1.338 uji, `stratify=y`, `random_state=42` | `train.py:200` | ✅ |
| Holdout: acc 97,53%, F1-macro 0,9726 | rerun + `reports/` | ✅ |
| Confusion matrix TN 863 / FP 9 / FN 24 / TP 442 | `hybrid_ablation.txt` | ✅ |
| CV 5-fold: 0,9741 ± 0,30% (std 0,0030) | `reports/cv_5fold_scores.png` | ✅ (std sudah benar 0,30%, bukan 0,21%) |
| Baseline: LR 97,09% / NB 93,95% | `compare_baselines.py` | ✅ |
| Hard set: 135 komentar, 100% non-spam, acc 98,52%, 2 FP, 0 FN | `data/hard_test_set.csv` + `hard_set_evaluation.txt` | ✅ |
| Ablation hibrida: SVM murni 97,53%/0,9726 vs +Hibrida 90,21%/0,8867; hard 98,52% vs 82,22%; turun 7,32 & 16,30 poin | `hybrid_ablation.txt` | ✅ |
| Stemming: p=0,3575 tidak signifikan, 4/5 fold lebih buruk | `experiment_stemming.py` | ✅ (tapi lihat K2 soal −0,0006 vs +0,0002) |
| TF-IDF: `max_features=10000`, `ngram_range=(1,2)`, `min_df=2`, `sublinear_tf=True` | `train.py:64-67` | ✅ |
| SVM: `kernel='linear'`, `class_weight='balanced'`, `random_state=42` | `train.py:125` | ✅ |
| GridSearchCV C ∈ {0,01, 0,1, 1, 10, 100}, terpilih C=1 | `train.py:233` | ✅ |
| Platt Scaling via `probability=True` | `train.py:240,339` | ✅ |
| Pipeline prapemrosesan **7 tahap** (zero-width → NFKC → diakritik → unwrap → homoglyph → leet → brand → stopword) | `preprocessing.py:31-43` | ✅ (dokumen bilang "tujuh tahap", kode 7 langkah + sub-langkah — cocok) |
| Pelabelan 2 tahap: skor ≥80 + rescue brand terkonfirmasi | `prepare_dataset.py` | ✅ (4.3.1 sudah benar, tidak lagi salah seperti V1) |
| Scraper = Node.js CLI, argumen video ID, `commentThreads` API | `scraper/index.js` | ✅ (kesalahan fatal "Chrome Extension Node.js" di V1 **sudah diperbaiki**) |
| 4 endpoint: `/health`, `/predict`, `/predict/batch`, `/report` | `server.py` | ✅ |
| `/predict/batch` maks 50 | `server.py:350` | ✅ |
| `ENABLE_HYBRID_RULES = False` di sistem final | `server.py:175` | ✅ |
| Threshold default 0,75; rentang 50–95% | `content.js:34` | ✅ |
| MutationObserver + WeakSet dedup | `content.js:76,502` | ✅ |
| Mode Redupkan (opacity 15% + badge) & Hilangkan (`display:none`) | `content.js` | ✅ |

**Kesimpulan verifikasi:** kesesuaian draft ↔ kode **sangat tinggi**. Tidak ada angka yang dikarang. Cuma isu localhost/VPS (K3) yang benar-benar mismatch antara narasi dan kode.

---

## 3. Verifikasi Sitasi Kunci (via web)

| Sitasi | Verifikasi | Hasil |
|---|---|---|
| **Angelo, Robet & Hendrik (2025)** — JTMI 11(2), DOI 10.26905/jtmi.v11i2.16286 | jurnal.unmer.ac.id | ✅ **Asli**. Angka di 2.17 (1.648→9.111 via pseudo-labelling, 4 algoritma + SMOTE, test 1.823, SVM F1 **0,9908**) **cocok persis** dengan abstrak paper. |
| **Airlangga (2024a)** — Brilliance 4(2):500–508 | jurnal.itscience.org | ✅ Asli. |
| **Airlangga (2024b)** — MALCOM 4(4):1533–1538 (LSTM 95,65%) | journal.irpi.or.id | ✅ Asli. |

Sitasi lain (Herawati 2025, Khairunnisa 2021, Géron 2022, Rosa & Shalahuddin 2019, dll) formatnya konsisten APA dan ada di Daftar Pustaka. Yang **belum sempat gua verifikasi angka internalnya** (opsional, kalau mau ekstra aman): klaim "Sastrawi akurasi 97,73%" (Sinaga & Nainggolan 2023) di hal. 12 — worth dicek kalau lu masih punya PDF-nya.

---

## 4. Format Italic Istilah Asing (Pedoman 4.2.9)

Gua scan **font per-karakter** dari PDF (pakai pdfminer) buat lihat mana istilah asing yang muncul TANPA italic. Hasilnya: **italic dipakai tapi tidak konsisten** — banyak istilah yang di satu tempat miring, di tempat lain enggak.

### 4a. Jelas kelewat (di body text — harus diperbaiki)

| Istilah | Halaman (plain) | Catatan |
|---|---|---|
| *obfuscation* | 14, 22 | mayoritas sudah italic (27×), 3× kelewat |
| *sigmoid* | 36, 38 | **tidak pernah** diitalic (0×) — hal. 36 & 38 |
| *stemming* | 14, 115 | mayoritas italic (23×), body kelewat di 14 & 115 |
| *noise* | 78 | |
| *keyword* | 22 | |
| *unigram* / *trigram* | 33 / 34 | (bigram sudah italic) |
| *homoglyphs* | 18 | |
| *swimlane* | 101 | **tidak pernah** diitalic |
| *hyperplane* | 12 (caption Gambar 2.2) | body-nya konsisten italic |

### 4b. Inkonsistan (kadang italic kadang enggak — samakan saja)

`dataset`, `server`, `threshold`, `confidence`, `endpoint`, `baseline`, `popup`, `default`, `deploy`, `input`, `output`, `margin`, `framework`, `review`, `preprocessing`.

> Contoh: *dataset* muncul 19× italic tapi 34× plain; *threshold* 18× italic 2× plain; *endpoint* 15× italic 2× plain.

### 4c. Abu-abu (boleh plain, tergantung selera pembimbing)
- **Judul/heading, caption Gambar/Tabel, Daftar Isi** → banyak dokumen tidak mengitalic istilah di heading. Konsisten aja.
- **Nama file / identifier kode** (`popup.js`, `scraper/index.js`, `sublinear_tf`) → memang tidak perlu italic.
- **Judul artikel di Daftar Pustaka** (mis. "text preprocessing" pada entri Khairunnisa) → itu judul referensi, bukan istilah — biarkan sesuai gaya APA.

**Saran praktis:** pakai Find & Replace atau baca ulang per-bab, samakan **satu keputusan per istilah**. Minimal beresin yang di **4a** karena itu jelas-jelas di badan teks. Kata yang sudah jadi serapan umum (server, dataset) sebenarnya bisa diargumentasikan plain — tapi kalau di tempat lain kamu italic-kan, konsistenkan.

> ⚠️ Catatan: deteksi ini berbasis nama font PDF, jadi ada kemungkinan kecil false-positive di kata yang kepotong antar-baris. Verifikasi visual singkat di halaman yang disebut tetap disarankan.

---

## 5. Temuan Minor

1. **Abstrak — hitungan halaman.** Ditulis *"(xiii + 106 halaman + 0 lampiran)"*. Padahal (a) Abstrak sendiri ada di halaman **xiv**, dan (b) ada halaman **Lampiran L-1** (hal. 124). Jadi "xiii" dan "0 lampiran" agak meleset. Cek: kalau ada lampiran, jangan tulis "0 lampiran".
2. **Konsistensi istilah "judol" vs "judi online".** Di body konsisten "judi online" (bagus, formal). Token `judolbrand` cuma di penjelasan teknis — OK.
3. **Gambar grayscale (arahan dosen poin 10).** Belum bisa gua cek dari ekstraksi teks. Pastikan Gambar 3.1, 4.1–4.12 hitam-putih/grayscale. Cek visual manual.
4. **"Setiap teori dikasih kesimpulan" (arahan dosen poin 4).** Dari yang gua baca, sub-bab BAB II **sudah** ditutup paragraf kesimpulan (2.1, 2.3, 2.5, 2.6, 2.7, 2.8, dst). 👍 Tapi cek yang belum: 2.12 (Spam), 2.13 (Chrome Extension) sudah ada; **2.14 (FastAPI), 2.15 (UML), 2.16 (PIECES), 2.10, 2.4** — pastikan semua punya kalimat penutup. 2.14 kelihatannya berhenti tanpa paragraf sintesis.
5. **Pratama (2026).** Referensi bertahun 2026 (tahun berjalan). Bukan salah, tapi siap-siap kalau ditanya "sudah terbit?".
6. **Nama pembimbing II** — di Kata Pengantar tertulis "Septiani Ningtyas", di lembar persetujuan & abstrak "Septiana Ningtyas". Samakan ejaan namanya (kemungkinan "Septiana").

---

## 6. Yang Sudah Bagus (Pertahankan)

- ✅ **Semua angka empiris jujur & terverifikasi** — gak ada yang dikarang. Ini modal kuat di sidang.
- ✅ Struktur BAB III "Objek Penelitian" **sesuai template pedoman** (Lampiran L-10/11) — jangan diubah judulnya.
- ✅ 4.11.5 sudah menjelaskan hard test set **single-class by design** (uji presisi, kenapa recall/F1 tidak dipakai) — ini justru mengantisipasi pertanyaan penguji. 👍
- ✅ Use Case Narrative UC02 actor = "-" (proses internal) + penjelasan relasi include — konsisten & benar secara UML.
- ✅ Kesalahan fatal V1 (scraper "Chrome Extension Node.js") **sudah diperbaiki** jadi Node.js CLI + API v3.
- ✅ PIECES di BAB III + ringkasan Tabel 3.1, lalu BAB IV dibuka dengan sintesis PIECES → solusi (arahan dosen poin 9) — sudah dipenuhi.
- ✅ Ablation study & uji stemming pakai bukti empiris (paired t-test) — "keputusan desain berdasarkan bukti, bukan asumsi" itu kalimat bagus di 4.11.8.
- ✅ BAB V Kesimpulan menautkan balik ke aspek PIECES (Kendali & Efisiensi) — nyambung dari BAB III. Rapi.

---

## 7. Checklist Prioritas

**Sebelum sidang — WAJIB:**
- [ ] **K1** Betulkan 4 rujukan tabel di 4.11 (4.4→4.9, 4.5→4.10, 4.6→4.11, 4.7→4.12).
- [ ] **K2** Samakan angka stemming 4.5.5 dengan 4.11.7 (buang "+0,0002", pakai narasi netral / −0,0006).
- [ ] **K3** Putuskan VPS vs localhost — update kode ekstensi (5 titik) **atau** turunkan klaim VPS di tesis.
- [ ] **K5** Tambah entri Arrayyan (2025) & Efrizoni (2022); beresin orphan Somantri (2020).

**Sebelum sidang — penting:**
- [ ] **K4** Revisi framing 2.11: "web scraping" → perjelas pakai YouTube Data API v3.
- [ ] **I1** Konsistenkan italic istilah asing (minimal daftar Bagian 4a).
- [ ] Betulkan ejaan nama pembimbing II (Septiani/Septiana).
- [ ] Betulkan hitungan halaman di Abstrak (xiii→xiv, "0 lampiran").

**Cek manual (gak bisa dari teks):**
- [ ] Gambar 3.1 & 4.1–4.12 grayscale/hitam-putih.
- [ ] Pastikan tiap sub-bab BAB II (khususnya 2.14) punya paragraf kesimpulan.
- [ ] Sweep manual sekali lagi: semua sitasi body ↔ Daftar Pustaka nyambung.

---

*Catatan: file draft V1 lama sudah diarsipkan ke `.docs/archive_draft_v1/`. Review ini khusus untuk draft V2 (20260713).*
