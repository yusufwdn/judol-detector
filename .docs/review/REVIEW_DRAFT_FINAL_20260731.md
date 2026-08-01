# Review Draft Final Skripsi — 221232017 (Yusuf Wandana)

**Dokumen ditinjau:** `Skripsi/2-RIWAYAT/skripsi/2026-07-31/[DRAFT] 221232017 - 20260731.pdf` (127 halaman PDF / 109 halaman isi)
**Tanggal review:** 31 Juli 2026
**Acuan:** `.docs/pedoman/PEDOMAN_SKRIPSI_TEKNIK_INFORMATIKA.pdf` (ringkasan di `.docs/pedoman/PEDOMAN_RINGKAS.md`) + arahan dosen pembimbing
**Kode yang diverifikasi:** commit `fd1a74e` di `svm-judol-spam`

> **Catatan konversi halaman:** halaman PDF = halaman cetak + 13. Contoh: halaman cetak 93 = halaman PDF 106.

---

## RINGKASAN EKSEKUTIF

**Kabar baiknya:** seluruh angka empiris di skripsi ini **100% akurat**. Saya reproduksi ulang training/evaluasi dari `data/comments.csv` dan hasilnya persis sama sampai digit terakhir. Struktur bab sudah sesuai jalur pedoman (Objek Penelitian non-perusahaan), analisis kelayakan lengkap, abstrak 236 kata (dalam rentang 200-250), 28 referensi (minimum 15), tahun tertua 2018 (batas 2016), 2 penelitian terdahulu tahun 2024-2025 (batas 2021). Masalah italic yang dulu berantakan sekarang sudah rapi.

**Yang harus dibereskan sebelum submit:** ada **6 temuan kritis** yang gampang ketahuan penguji, dan semuanya perbaikannya cepat (< 1 jam total). Tiga di antaranya adalah sisa masalah dari draft sebelumnya yang belum sempat ditutup.

| Prioritas | Jumlah | Estimasi waktu |
|---|---|---|
| 🔴 Kritis (wajib) | 6 | ~45 menit |
| 🟠 Penting | 7 | ~1 jam |
| 🟡 Kosmetik | 9 | ~45 menit |

---

## STATUS PENGERJAAN (update 31 Juli 2026)

Dikerjakan langsung di `Skripsi/2-RIWAYAT/skripsi/2026-07-31/[DRAFT] 221232017 - 20260731.docx`.
Cadangan sebelum diedit: `[DRAFT] 221232017 - 20260731 (BACKUP sebelum fix K4-K5).docx`.

| Temuan | Status |
|---|---|
| **K4** web scraping vs API | ✅ **SELESAI** — judul 2.11 diubah jadi "Pengumpulan Data melalui API dan Analisis Heuristik", paragraf pertama ditulis ulang, kalimat "teknik scraping ini" diganti |
| **K5** sitasi bolong dua arah | ✅ **SELESAI** — entri Arrayyan dkk. (2025) & Efrizoni dkk. (2022) ditambahkan (sumber diverifikasi ke penerbit aslinya), sitasi Somantri dkk. (2020) disisipkan di Sub-bab 2.6. Sitasi kini 1:1 dua arah, Daftar Pustaka 31 entri, urutan alfabetis terjaga |
| **K5 bonus** klaim Efrizoni | ✅ **SELESAI** — kalimat di 2.5 diperbaiki karena klaim lama tidak didukung isi papernya (lihat catatan di bawah) |
| **P5 + P6** gaya sitasi | ✅ **SELESAI** — seluruh sitasi diseragamkan ke APA dengan "dkk." (lihat tabel di bawah). Diaudit terhadap jumlah penulis asli tiap sumber: **31 bentuk sitasi, 0 masalah** |
| **K1** caption `Gambar 2II.6` | ✅ **SELESAI (1 Agustus)** — akar masalahnya field `STYLEREF` (lihat catatan di bawah) |
| **K2** kontradiksi stemming | ✅ **SELESAI** — sudah diperbaiki sendiri oleh penulis; 4.5.5 kini netral, "+0,0002" tidak ada lagi |
| **K3** dua rujukan silang salah | ✅ **SELESAI** — rujukan "Tabel 4.9" sudah diperbaiki penulis; "Sub-bab" (sempat bergeser jadi 4.12) dikoreksi ke **4.10** |
| **K6** VPS vs localhost | ⏳ Ditunda — VPS akan dinaikkan dalam beberapa hari. **Draft masih menyatakan VPS padahal sistem masih lokal** |
| Sisa temuan 🟠 dan 🟡 | ⬜ Belum dikerjakan |

### Akar masalah caption `Gambar 2II.6` — dan audit rujukan silang menyeluruh

Caption Gambar 2.6 memuat **dua** sumber nomor sekaligus: teks literal `"2"` **plus** field `STYLEREF 1 \s` yang mengembalikan nomor bab sebagai angka Romawi (`II`), lalu diikuti field `SEQ`. Saat Word me-render ulang, hasilnya `Gambar` + `2` + `II` + `.` + `6` = **"Gambar 2II.6"**. Caption lain tidak memakai STYLEREF sehingga aman.

Perbaikannya: rentang field `STYLEREF` dibuang, field `SEQ` dipertahankan — penomoran otomatis tetap jalan dan bug tidak bisa muncul lagi. **Sisa STYLEREF di seluruh dokumen kini 0.**

> Bug identik ditemukan di proposal (`Tabel 2II.2`) dan sudah diperbaiki dengan cara yang sama.

Setelah K1 dan K3 selesai, dilakukan **audit seluruh rujukan silang** terhadap struktur dokumen yang sebenarnya:

| Pemeriksaan | Hasil |
|---|---|
| Rujukan "Sub-bab X.Y" | 11 rujukan, **semuanya menunjuk sub-bab yang benar** ✅ |
| Rujukan "Tabel X.Y" / "Gambar X.Y" | **0 yang menunjuk caption tidak ada** ✅ |
| Caption rusak pola `2II.x` | **0** ✅ |
| Field STYLEREF tersisa | **0** ✅ |

Cadangan sebelum perbaikan: `2026-08-01/[DRAFT] 221232017 - 20260801 (BACKUP sebelum K1-K2-K3).docx`

### Hasil audit kelengkapan sitasi (K5 — final)

| Pemeriksaan | Hasil |
|---|---|
| Sitasi di teks tanpa entri Daftar Pustaka | **0** ✅ |
| Entri Daftar Pustaka tidak pernah disitasi | **0** ✅ |
| Total entri Daftar Pustaka | **30** (minimum pedoman 15) ✅ |
| Rentang tahun | 2018–2026 (batas pedoman ≥2016) ✅ |
| Urutan alfabetis | rapi ✅ |
| Bentuk sitasi unik yang diperiksa | semuanya sesuai APA ✅ |

> Catatan: `Robet (2025)` sempat terdeteksi sebagai sitasi yatim, tetapi itu berasal dari listing Sub-bab 2.17 yang mengeja ketiga penulis Angelo dkk. — bukan sumber terpisah. Sudah ikut diseragamkan.

#### Somantri dkk. (2020) — DIHAPUS

Awalnya masalah "referensi yatim" ini ditutup dengan menambahkan sitasi di Sub-bab 2.6. Namun setelah detail terbitannya ditelusuri, **entri Daftar Pustaka-nya tidak dapat diverifikasi**:

- Draft menulis: *JEPIN (Jurnal Edukasi dan Penelitian Informatika), 6(3), 312–319, 2020*
- Yang ditemukan: papernya nyata (Somantri, Wiyono, Dairoh — Politeknik Harapan Bersama Tegal, SVM + K-Means, akurasi 86,21% vs 85,38%), tetapi terbit di **Telematika vol. 13 no. 2 (2017)** dan versi lain di **Scientific Journal of Informatics vol. 3 no. 1 (2016)**. Versi JEPIN 2020 tidak ditemukan meskipun dicari langsung ke jurnal.untan.ac.id.

Karena sitasi dengan detail terbitan yang keliru lebih berisiko daripada tidak menyitasi sama sekali, dan kalimatnya tidak menopang argumen apa pun (Sub-bab 2.6 sudah didukung Airlangga 2024a dan Ardiansyah dkk. 2025), **entri beserta kalimat sitasinya dihapus**. Daftar Pustaka menjadi 30 entri — masih jauh di atas minimum 15.

Kalau nanti mau dipakai lagi, gunakan versi **Telematika (2017)** yang masih memenuhi syarat umur referensi ≤10 tahun, dan pastikan nomor halamannya dicek ulang ke sumber aslinya.

### Penyeragaman gaya sitasi (P5 + P6)

Aturan APA 7 yang diterapkan, diverifikasi terhadap **jumlah penulis sebenarnya** pada tiap entri Daftar Pustaka:

| Jumlah penulis | Bentuk in-text | Contoh |
|---|---|---|
| 1 | `(Nama, tahun)` | (Airlangga, 2024a) |
| 2 | `(Nama & Nama, tahun)` | (Koprawi & Putra, 2023) |
| 3 atau lebih | `(Nama dkk., tahun)` | (Kaddoura dkk., 2022) |

Perubahan yang dilakukan:

| Sebelum | Sesudah | Alasan |
|---|---|---|
| (Chua et al., 2024) | (Chua dkk., 2024) | 4 penulis — "et al." diganti "dkk." |
| (Nanda et al., 2022) | (Nanda dkk., 2022) | 4 penulis — "et al." diganti "dkk." |
| (Khairunnisa & Adiwijaya, 2021) ×2 | (Khairunnisa dkk., 2021) | Sumbernya **3 penulis** (Khairunnisa, Adiwijaya, & Al Faraby), jadi bentuk dua-penulis itu keliru |
| Angelo, Robet & Hendrik (2025) | Angelo dkk. (2025) | 3 penulis — APA in-text tidak mengeja semua penulis |
| (Sari dan Asmendri, 2020) | (Sari & Asmendri, 2020) | 2 penulis — APA memakai "&", bukan "dan" |

**Kenapa sitasi dua penulis TIDAK diubah jadi "dkk."** — dalam APA, "dkk./et al." hanya dipakai untuk **tiga penulis atau lebih**. Sumber dua penulis wajib menyebut keduanya. Jadi (Koprawi & Putra, 2023), (Rosa & Shalahuddin, 2019), (Sinaga & Nainggolan, 2023), (Ramadhan & Fauzan, 2023), (Helmiyah & Pramestiawan, 2025), (Kinanti & Indriyanti, 2021), dan (Sari & Asmendri, 2020) memang sudah benar apa adanya. Kalau ditanya penguji: *"Sitasi mengikuti APA 7th edition — satu penulis disebut langsung, dua penulis disambung ampersand, tiga penulis atau lebih memakai dkk."*

> ⚠️ **WAJIB DILAKUKAN DI WORD SETELAH INI:** judul Sub-bab 2.11 berubah, jadi **Daftar Isi harus di-refresh** — klik kanan pada Daftar Isi → *Update Field* → *Update entire table*. Kalau tidak, Daftar Isi masih menampilkan judul lama.

### Catatan penting soal referensi baru

Kedua sumber **terverifikasi nyata**, bukan karangan:

- **Efrizoni dkk. (2022)** — diverifikasi langsung dari halaman penerbit ([journal.universitasbumigora.ac.id](https://journal.universitasbumigora.ac.id/index.php/matrik/article/view/1851)). MATRIK vol. 21 no. 3, hal. 653–666, DOI 10.30812/matrik.v21i3.1851. Isinya memang membandingkan BoW, TF-IDF, Doc2Vec, dan Word2Vec pada enam algoritma *machine learning* — cocok dengan konteks pemakaiannya di Sub-bab 2.5.

- **Arrayyan dkk. (2025)** — halaman penerbit menolak akses langsung (HTTP 403), tapi dikuatkan tiga sumber independen: [Jurnal Algoritma ITG](https://jurnal.itg.ac.id/index.php/algoritma/article/view/3012), [UPI Repository](https://repository.upi.edu/148996/), dan [ResearchGate](https://www.researchgate.net/publication/398372398_Deteksi_Komentar_Spam_Judi_Online_Berbahasa_Indonesia_Menggunakan_XGBoost_dan_TF-IDF). Jurnal Algoritma vol. 22 no. 2, hal. 2066–2075, DOI 10.33364/algoritma/v.22-2.3012. **Tolong cek ulang nomor halaman dan DOI-nya** karena halaman resminya tidak bisa dibuka otomatis.

**Klaim Efrizoni yang diperbaiki.** Kalimat lama berbunyi: *"TF-IDF secara konsisten menunjukkan performa kompetitif ketika dikombinasikan dengan algoritma machine learning **seperti SVM**"*. Ini **tidak didukung** papernya — Efrizoni dkk. justru menemukan SVM performa terbaiknya dengan **Doc2Vec** (81%), sementara hasil terbaik keseluruhan adalah Naive Bayes + TF-IDF (87%). Kalimat diganti jadi:

> "...TF-IDF menunjukkan performa yang paling stabil di berbagai algoritma *machine learning* pada klasifikasi teks berbahasa Indonesia (Efrizoni dkk., 2022)."

Versi ini akurat: TF-IDF memberi hasil tertinggi (87%) dan tertinggi kedua (83%), dan tidak pernah kolaps seperti Word2Vec (<50%). Kalau ditanya penguji, itu jawabannya.

---

## ✅ HASIL VERIFIKASI TERHADAP KODE — SEMUA COCOK

Saya jalankan ulang pipeline-nya dari nol. Berikut perbandingannya:

| Klaim di skripsi | Hasil reproduksi dari kode | Status |
|---|---|---|
| Dataset 6.690 baris (2.332 spam / 4.358 non-spam) | 6.690 (2.332 / 4.358) | ✅ |
| Split 80:20 → 5.352 latih / 1.338 uji | 5.352 / 1.338 | ✅ |
| Accuracy 97,53% | 0.9753 | ✅ |
| F1-macro 0,9726 | 0.9726 | ✅ |
| Confusion matrix: TN 863, FP 9, FN 24, TP 442 | 863 / 9 / 24 / 442 | ✅ |
| Presisi spam 0,98 · Recall spam 0,95 | 0.9800 / 0.9485 | ✅ |
| F1 spam 0,96 · F1 non-spam 0,98 | 0.9640 / 0.9812 | ✅ |
| CV 5-fold: 0,9741 ± 0,30% | mean 0.9741, std 0.0030 | ✅ |
| Logistic Regression 97,09% / 0,9675 | 97.09% / 0.9675 | ✅ |
| Multinomial NB 93,95% / 0,9313 | 93.95% / 0.9313 | ✅ |
| Hard test set: 135 komentar, acc 98,52%, 2 FP | 135 (semua non_spam), 98.52%, FP=2, FN=0 | ✅ |
| Ablation hibrida: 90,21%/0,8867, turun 7,32 & 16,30 poin | identik dengan `reports/hybrid_ablation.txt` | ✅ |
| C=1 terpilih dari [0,01; 0,1; 1; 10; 100] | `model.named_steps['svm'].C == 1` | ✅ |
| TF-IDF: max_features=10.000, ngram (1,2), min_df=2, sublinear_tf=True | identik di `src/train.py:66-71` | ✅ |
| SVC kernel linear, class_weight balanced, probability=True, random_state=42 | identik | ✅ |
| 7 tahap preprocessing (zero-width→NFKC→homoglyph→emoji→lowercase→leet+brand→stopword) | identik di `src/preprocessing.py:31-42` | ✅ |
| Normalisasi *leet speak* | ada, `preprocessing.py:271-292` (Step 5b-i) | ✅ |
| 4 endpoint: /health, /predict, /predict/batch, /report | ada semua di `src/server.py` | ✅ |
| Batch maksimum 50 komentar | `server.py:350-351` | ✅ |
| Threshold default 0,75; slider 50%-95% | `content.js:34`, `popup.html:355-356` | ✅ |
| Mode Redupkan opacity 15% / Hilangkan display:none | `content.js:280-288` | ✅ |
| MutationObserver + WeakSet | `content.js:502`, `content.js:76` | ✅ |
| Tombol "Bukan spam?" hanya di dev mode | `content.js:218, 321` | ✅ |

**Daftar Isi:** nomor halaman BAB I–V dan sub-bab yang saya cek semuanya akurat. ✅

**Bebas dari pelanggaran ini:** tidak ada bullet point (pedoman 4.2.8) ✅ · tidak ada kata "penulis/saya/kita/anda" di luar Kata Pengantar (4.6.2) ✅ · tidak ada kalimat diawali "Sehingga"/"Sedangkan" (4.6.3.a) ✅ · tidak ada kata "dimana" (4.6.3.c) ✅

---

## 🔴 TEMUAN KRITIS (wajib diperbaiki)

### K1 — Caption gambar rusak: "Gambar 2II.6"
**Lokasi:** halaman cetak 36 (PDF 49)

```
Gambar 2II.6 Simbol-Simbol Sequence Diagram     ← salah
Gambar 2.6 Simbol-Simbol Sequence Diagram       ← benar
```

Ini bug *cross-reference field* Word. Daftar Gambar sudah menulis "Gambar 2.6" dengan benar, jadi hanya caption-nya yang rusak. Ini tipe kesalahan yang langsung kelihatan waktu penguji buka halaman itu.

**Perbaikan:** klik kanan pada nomor caption → Update Field, atau ketik manual "2.6".

---

### K2 — Kontradiksi angka stemming (sisa dari draft sebelumnya, belum ditutup)
**Lokasi:** Sub-bab 4.5.5 halaman cetak 75 (PDF 88) vs Sub-bab 4.10.7 halaman cetak 99 (PDF 112)

| Tempat | Yang tertulis |
|---|---|
| 4.5.5 | "menunjukkan **peningkatan** F1-macro yang tidak signifikan sebesar **+0,0002**" |
| 4.10.7 | "rata-rata F1-macro dengan stemming justru **sedikit lebih rendah** (selisih **−0,0006**)" |

Eksperimen yang sama, arah yang berlawanan. Angka yang **benar** adalah **−0,0006** (p-value 0,3575, 4 dari 5 fold lebih buruk) — itu yang konsisten dengan `reports/experiment_stemming_cv.png` dan dengan narasi di BAB V. Angka +0,0002 adalah sisa dari draft lama.

**Perbaikan** — ganti kalimat di 4.5.5 jadi netral supaya tidak mendahului hasil pengujian:

> Sebagai bagian dari proses eksplorasi metodologi, dilakukan eksperimen terpisah untuk menguji pengaruh *stemming* Sastrawi terhadap performa model. Hasil eksperimen menunjukkan bahwa *stemming* tidak memberikan peningkatan performa yang signifikan secara statistik, sehingga *stemming* diputuskan tidak diintegrasikan ke dalam *pipeline* prapemrosesan produksi. Detail hasil eksperimen ini dibahas lebih lanjut pada Sub-bab 4.10.7.

Kalau ditanya penguji "kenapa tidak pakai stemming?", jawabannya: *"Sudah diuji dengan paired t-test pada 5-fold CV. Selisihnya −0,0006 dengan p-value 0,3575, jauh di atas α = 0,05, jadi tidak signifikan secara statistik. Menambah stemming berarti menambah beban komputasi tanpa manfaat terukur."*

---

### K3 — Dua rujukan silang salah nomor di Sub-bab 4.10.1
**Lokasi:** halaman cetak 93 (PDF 106) — dua-duanya di halaman yang sama

| Yang tertulis | Seharusnya | Kenapa salah |
|---|---|---|
| "Berdasarkan persamaan yang diuraikan di awal **Sub-bab 4.11**" | **Sub-bab 4.10** | 4.11 itu "Rancangan Tampilan", tidak ada persamaan di sana. Persamaan ada di pembuka 4.10 |
| "...F1-score non-spam sebesar 0,98 sebagaimana disajikan pada **Tabel 4.9**" | **Tabel 4.10** | Tabel 4.9 itu "Use Case Narrative Melaporkan Kesalahan Klasifikasi" |

Ini sisa dari pergeseran nomor waktu tabel use case (4.5–4.9) disisipkan. Rujukan lain di bab yang sama sudah benar semua — tinggal dua ini.

---

### K4 — Sub-bab 2.11 mendefinisikan "web scraping", tapi kode pakai API resmi
**Lokasi:** halaman cetak 29-30 (PDF 42-43)

Sub-bab 2.11 menulis:
> "Teknik ini dilakukan dengan mengirimkan permintaan protokol jaringan ke peladen situs web, kemudian **memuat struktur kode HTML secara utuh, dan mem-parsing elemen-elemen spesifik**... Pada arsitektur sistem ini, **web scraping** berjalan secara *asynchronous* melalui *runtime environment* Node.js untuk mengekstraksi komentar-komentar pada platform YouTube."

Padahal `scraper/index.js` **tidak mem-parsing HTML sama sekali** — dia memanggil endpoint `commentThreads` YouTube Data API v3 dan menerima JSON. Semua bab lain sudah benar menyebut API (1.4.2, 3.1, 4.3.1, 4.12.3 Kelayakan Hukum).

**Kenapa ini berbahaya:** 4.12.3 mengklaim sistem legal *justru karena* memakai API resmi, bukan scraping. Kalau 2.11 bilang "ini web scraping", argumen kelayakan hukum jadi kontradiktif — dan itu pertanyaan penguji yang sangat mungkin muncul.

**Perbaikan** — ubah judul jadi **"2.11 Pengumpulan Data melalui API dan Analisis Heuristik"**, lalu ganti paragraf pertama:

> Dalam pengembangan kecerdasan buatan, ketersediaan himpunan data (*dataset*) yang melimpah dan relevan menjadi syarat mutlak. Pengumpulan data dari platform web dapat dilakukan melalui dua pendekatan, yaitu *web scraping* yang mem-*parsing* struktur HTML halaman secara langsung, dan pemanfaatan *Application Programming Interface* (API) resmi yang disediakan platform (Koprawi & Putra, 2023). Pendekatan berbasis API lebih diutamakan karena data diterima dalam format terstruktur (JSON), lebih stabil terhadap perubahan tampilan halaman, serta tidak melanggar ketentuan layanan platform. Pada penelitian ini, pengumpulan data dilakukan melalui YouTube Data API v3 yang diakses secara *asynchronous* melalui *runtime environment* Node.js.

Sisa paragraf tentang heuristik tidak perlu diubah.

---

### K5 — Dua sitasi tidak ada di Daftar Pustaka, satu referensi tidak pernah dikutip
**Lokasi:** halaman cetak 15 (PDF 28) dan Daftar Pustaka

| Masalah | Detail |
|---|---|
| ❌ **(Arrayyan dkk., 2025)** | Dikutip di 2.5 hal. 15, **TIDAK ADA di Daftar Pustaka** |
| ❌ **(Efrizoni dkk., 2022)** | Dikutip di 2.5 hal. 15, **TIDAK ADA di Daftar Pustaka** |
| ❌ **Somantri dkk. (2020)** | Ada di Daftar Pustaka, **tidak pernah dikutip** di badan tulisan (0 kemunculan) |

Pedoman tegas soal ini (bagian Kutipan dan Acuan): *"sumber yang ditulis dalam daftar pustaka benar-benar dirujuk dalam tubuh artikel. Sebaliknya, semua acuan yang telah disebutkan dalam artikel harus dicantumkan dalam daftar pustaka."* Ini pelanggaran dua arah sekaligus, dan gampang dicek penguji.

**Perbaikan — pilih salah satu:**
- **(A) Lengkapi:** tambahkan entri Arrayyan dkk. (2025) dan Efrizoni dkk. (2022) ke Daftar Pustaka, lalu sisipkan sitasi Somantri dkk. (2020) di tempat yang relevan (paling pas di 2.6 SVM, karena papernya soal optimasi SVM).
- **(B) Hapus:** ganti dua sitasi itu dengan sumber yang sudah ada di Daftar Pustaka, lalu buang entri Somantri.

Opsi A lebih aman — jumlah referensi jadi 30, dan tidak ada klaim yang kehilangan dasar.

---

### K6 — Skripsi mengklaim deploy VPS, tapi kode masih hardcode `localhost:8000`
**Lokasi klaim VPS:** 4.1.2 poin 4 (hal. 60), Tabel 4.1 & 4.2 (hal. 61), 4.2 poin 3 (hal. 63), 4.4.2 (hal. 71), 4.6.3 (hal. 78), 4.12.1 (hal. 105)

Skripsi menyatakan sangat spesifik: *"Server API di-deploy pada infrastruktur Virtual Private Server (VPS) yang terpisah dari perangkat pengguna"*, lengkap dengan Ubuntu Server 24.04 LTS, 2 vCPU, RAM 2 GB, 40 GB SSD.

Tapi kode masih menunjuk ke localhost di **6 tempat**:

| File | Baris | Isi |
|---|---|---|
| `extension/content.js` | 29 | `const API_URL = "http://localhost:8000/predict";` |
| `extension/content.js` | 30 | `const BATCH_API_URL = "http://localhost:8000/predict/batch";` |
| `extension/content.js` | 94 | `fetch("http://localhost:8000/health", ...)` |
| `extension/content.js` | 235 | `fetch("http://localhost:8000/report", ...)` |
| `extension/popup.js` | 8 | `const API_BASE = "http://localhost:8000";` |
| `extension/manifest.json` | 13 | `"host_permissions": ["http://localhost:8000/*", ...]` |
| `extension/popup.html` | 317 | `<div class="sub" id="statusSub">localhost:8000</div>` |

**Risiko sidang:** kalau penguji minta demo langsung, atau minta lihat `manifest.json`, klaim VPS langsung runtuh. Ini temuan paling berisiko dari semuanya.

**Dua jalan keluar — harus pilih salah satu:**

- **(A) Kalau VPS-nya memang sudah jalan:** kasih tahu saya IP/domainnya, saya update 7 lokasi kode itu sekaligus. Ini opsi terbaik karena skripsi tidak perlu diubah sama sekali.

- **(B) Kalau belum ada VPS:** lunakkan klaimnya jadi arsitektur yang *mendukung* deployment VPS, dengan pengujian dilakukan di lingkungan lokal. Contoh revisi untuk 4.1.2 poin 4:

  > **4. Keamanan**
  > Model dan *pipeline* klasifikasi dijalankan pada komponen peladen yang terpisah dari sisi klien, sehingga tidak dapat diakses atau dimodifikasi secara langsung oleh pengguna akhir. Arsitektur ini dirancang agar dapat di-*deploy* pada *Virtual Private Server* (VPS); pada tahap penelitian ini pengujian dilakukan pada lingkungan lokal (*localhost*) dengan spesifikasi setara.

  Lalu Tabel 4.1/4.2 ubah label "(VPS)" jadi "(Server)" dan tambahkan keterangan "spesifikasi minimum untuk *deployment*", dan 4.12.1 tambahkan satu kalimat bahwa pengujian dilakukan pada lingkungan lokal yang setara.

Opsi B tetap jujur dan tetap defensible — yang tidak defensible adalah klaim VPS yang tidak bisa ditunjukkan.

---

## 🟠 TEMUAN PENTING

### P1 — Halaman Daftar Pustaka tidak diberi nomor
**Lokasi:** PDF 123-125

Pedoman 4.3.1.b: *"Bagian utama dan bagian akhir, mulai dari pendahuluan hingga halaman terakhir (lampiran), memakai angka Arab"*, dan 4.3.1.d: *"Penomoran halaman daftar pustaka langsung menyambung ke halaman lampiran."*

Isi berakhir di halaman 109, jadi Daftar Pustaka **harus** bernomor **110, 111, 112**. Sekarang kosong. Daftar Isi juga menulis "DAFTAR PUSTAKA" tanpa nomor halaman.

**Perbaikan:** lanjutkan penomoran Arab, lalu update Daftar Isi jadi `DAFTAR PUSTAKA .......... 110`.

---

### P2 — Halaman "L-1" kosong vs abstrak yang bilang "0 lampiran"
**Lokasi:** PDF 126 (kosong total) dan PDF 127 (hanya berisi "L-1")

Ada halaman lampiran kosong, padahal abstrak menulis "0 lampiran" dan tidak ada DAFTAR LAMPIRAN.

**Perbaikan — pilih:**
- Hapus dua halaman itu (paling simpel, konsisten dengan "0 lampiran"), **atau**
- Isi L-1 dengan sesuatu yang berguna (*listing* program inti / tangkapan layar dataset), lalu tambahkan DAFTAR LAMPIRAN dan ubah abstrak jadi "1 lampiran".

Pedoman menyebut *listing* program sebagai isi lampiran yang lazim, jadi opsi kedua justru menambah nilai.

---

### P3 — Keterangan jumlah halaman di abstrak salah
**Lokasi:** halaman xiii

Tertulis: `(xii + 109 halaman + 0 lampiran)`

Abstrak sendiri ada di halaman **xiii**, jadi bagian awal itu **xiii halaman**, bukan xii. Bagian "0 lampiran" juga bertabrakan dengan adanya halaman L-1 (lihat P2).

**Perbaikan:** `(xiii + 109 halaman + 0 lampiran)` — atau `+ 1 lampiran` kalau L-1 diisi.

---

### P4 — Nama Pembimbing II tidak konsisten
| Lokasi | Tertulis |
|---|---|
| Lembar Persetujuan (hal. ii) | Septian**a** Ningtyas |
| Lembar Pengesahan (hal. iii) | Septian**a** Ningtyas |
| Abstrak (hal. xiii) | Septian**a** Ningtyas |
| **Kata Pengantar (hal. vi) poin 3** | **Septiani** Ningtyas ❌ |

3 lawan 1 — kemungkinan besar yang benar "Septiana". **Tolong konfirmasi ejaan resminya** sebelum diperbaiki; salah tulis nama pembimbing di halaman ucapan terima kasih itu sensitif.

---

### P5 — Gaya sitasi tidak konsisten (`&` vs `dan`, `et al.` vs `dkk.`) — ✅ SUDAH DIPERBAIKI

Pedoman (bagian Kutipan dan Acuan, hal. 27) menetapkan: dua pengarang disambung **"dan"**, lebih dari dua pakai **"dkk."**.

**a) Pakai "et al." padahal harus "dkk." — 2 tempat:**
| Lokasi | Tertulis | Seharusnya |
|---|---|---|
| hal. 2 | `(Chua et al., 2024)` | `(Chua dkk., 2024)` |
| hal. 3 | `(Nanda et al., 2022)` | `(Nanda dkk., 2022)` |

**b) Pakai "&" padahal pedoman minta "dan" — 7 sumber:**
`Helmiyah &`, `Khairunnisa &`, `Kinanti &`, `Koprawi &`, `Ramadhan &`, `Rosa &`, `Sinaga &`

Sementara `(Sari dan Asmendri, 2020)` sudah pakai "dan". Jadi di dalam dokumen sendiri sudah tidak konsisten.

> **Rekomendasi realistis:** yang **wajib** diperbaiki adalah (a) — "et al." vs "dkk." itu campur bahasa dan paling mencolok. Untuk (b), pilih satu gaya lalu konsisten. Kalau memilih tetap "&" (gaya APA, dan Daftar Pustaka Anda memang sudah APA penuh), ubah `Sari dan Asmendri` jadi `Sari & Asmendri` supaya seragam — dan siapkan jawaban: *"format sitasi mengikuti gaya APA secara konsisten di seluruh dokumen."* Itu defensible. Yang tidak defensible adalah campur-campur.

---

### P6 — `(Khairunnisa & Adiwijaya, 2021)` salah jumlah pengarang — ✅ SUDAH DIPERBAIKI
**Lokasi:** halaman 2 dan halaman 9

Di Daftar Pustaka sumbernya adalah **Khairunnisa, S., Adiwijaya, A., & Al Faraby, S. (2021)** — **tiga** pengarang. Jadi bentuk "& Adiwijaya" keliru; harus **"Khairunnisa dkk., 2021"**.

Menariknya, di halaman 10 sudah ditulis benar sebagai `(Khairunnisa dkk., 2021)`. Jadi tinggal samakan 2 tempat yang salah.

---

### P7 — Lima sub-bab teori tidak ditutup kalimat kesimpulan
Ini aturan dosen pembimbing ("setiap teori dikasih kesimpulan"). Sebagian besar BAB II sudah patuh — 2.1 s/d 2.8, 2.12, 2.13, 2.17 semuanya punya paragraf penutup yang bagus. Yang belum:

| Sub-bab | Berakhir dengan |
|---|---|
| **2.9** Waterfall | "...pengembangan lanjutan setelah sistem digunakan." (langsung habis) |
| **2.10** ML vs Deep Learning | berakhir di sitasi (Airlangga, 2024a) |
| **2.11** Web Scraping | "...sebelum diteruskan ke model pelatihan SVM." |
| **2.14** REST API & FastAPI | "...tervalidasi sebelum diproses lebih lanjut." |
| **2.16** PIECES | langsung habis setelah Tabel 2.1, tanpa paragraf penutup |

**Contoh penutup yang bisa dipakai:**

- **2.9:** *"Berdasarkan uraian di atas, metode Waterfall dinilai sesuai untuk penelitian ini karena kebutuhan sistem telah terdefinisi sejak awal dan tidak memerlukan perubahan spesifikasi berulang, sehingga tahapan pengembangan dapat dijalankan secara berurutan dan terdokumentasi dengan jelas."*

- **2.10:** *"Dengan demikian, meskipun Deep Learning menawarkan akurasi yang kompetitif, penelitian ini memilih pendekatan Machine Learning konvensional karena kebutuhan inferensi real-time pada sisi peramban menuntut model yang ringan dan berlatensi rendah, sementara selisih akurasinya tidak sebanding dengan tambahan beban komputasinya."*

- **2.11:** *"Dari uraian tersebut dapat disimpulkan bahwa kombinasi pengumpulan data melalui API resmi dengan penyaringan heuristik memberikan dua keuntungan sekaligus, yaitu keabsahan sumber data secara legal dan efisiensi proses pelabelan awal sebelum data digunakan untuk melatih model."*

- **2.14:** *"Berdasarkan pemaparan di atas, FastAPI dipilih sebagai kerangka kerja peladen pada penelitian ini karena kemampuan asynchronous dan validasi tipe data bawaannya sesuai dengan kebutuhan sistem yang harus melayani permintaan klasifikasi secara cepat dan andal."*

- **2.16:** *"Keenam aspek pada Tabel 2.1 tersebut menjadi kerangka acuan dalam mendiagnosis kelemahan sistem berjalan pada Bab III, sekaligus menjadi dasar dalam merumuskan solusi yang diusulkan pada Bab IV."*

---

## 🟡 TEMUAN KOSMETIK

### C1 — Typo
| Lokasi | Salah | Benar |
|---|---|---|
| Daftar Gambar (hal. xi) & caption hal. 102 | "YouTube **denga** Chrome Extension" | "**dengan**" |
| hal. 52 | "adalah **penejelasan** dari diagram" | "**penjelasan**" |
| Daftar Isi & judul 4.7.1 (hal. 80) | "Use Case **Narative**" | "**Narrative**" (4.7.2–4.7.5 sudah benar) |
| Tabel 4.2 (hal. 61) | "1.8 **Ghz**" | "1,8 **GHz**" |
| 4.6.3 poin d (hal. 79) | "**Report** :" | "**/report** :" (poin a-c pakai garis miring) |

### C2 — Desimal pakai titik, seharusnya koma
**Lokasi:** halaman 16-17 (contoh perhitungan TF-IDF)

Pedoman 4.2.2.b: *"Bilangan desimal ditandai dengan tanda koma (,) bukan tanda titik (.)"*

| Tertulis | Seharusnya |
|---|---|
| `log(1.5) ≈ 0.176` | `log(1,5) ≈ 0,176` |
| `W = 1 × 0.176 = 0.176` | `W = 1 × 0,176 = 0,176` |
| `bobot 0.176` | `bobot 0,176` |
| `1.8 Ghz` (Tabel 4.2) | `1,8 GHz` |

Sisa dokumen sudah konsisten pakai koma (97,53% · 0,9726 · 0,75), jadi ini satu-satunya kantong yang terlewat. `10.000` sudah benar (itu pemisah ribuan).

### C3 — "Bab 4" vs "Bab IV"
**Lokasi:** akhir Sub-bab 2.4, halaman 14

Tertulis "diuraikan lebih lanjut pada **Bab 4**", padahal 2.2, 2.3, dan 2.5 semuanya menulis "**Bab IV**". Samakan jadi angka Romawi.

### C4 — "Sub-bab" vs "sub-bab"
Kapitalisasi campur: `Sub-bab 2.9`, `Sub-bab 4.1`, `Sub-bab 2.6`, `Sub-bab 4.5.3` (kapital) vs `sub-bab 3.1.2 dan 4.6` (hal. 80), `sub-bab 4.5.6` (hal. 97) (kecil). Pilih satu.

### C5 — Judul BAB IV lebih sempit dari isinya
Judul sekarang: **"PERANCANGAN SISTEM"**. Pedoman menamainya **"Perancangan dan Implementasi Sistem"**, dan isi bab ini memang sudah mencakup implementasi (4.10 Pengujian Sistem, 4.11 dengan tangkapan layar "Hasil Implementasi").

**Rekomendasi:** ubah jadi **"PERANCANGAN DAN IMPLEMENTASI SISTEM"** agar cocok dengan pedoman sekaligus dengan isinya. Kalau dosen sudah ACC judul yang sekarang, ini boleh dilewat — tapi siapkan jawaban kalau ditanya.

### C6 — Urutan Daftar Gambar dan Daftar Tabel terbalik
Draft: DAFTAR GAMBAR (xi) → DAFTAR TABEL (xii).
Template pedoman (L-10/L-11): **Daftar Tabel dulu, baru Daftar Gambar**. Prioritas rendah, tapi kalau mau persis template, tukar posisinya.

### C7 — Beberapa istilah asing masih tegak
Analisis tingkat font menunjukkan italic sudah **jauh lebih rapi** dari draft sebelumnya — *sigmoid*, *swimlane*, *obfuscation*, *noise*, *unigram*, *bigram*, *trigram*, *endpoint*, *badge*, *opacity*, *client-side* sekarang konsisten miring semua. ✅

Yang masih tegak di badan tulisan:
| Istilah | Halaman cetak |
|---|---|
| *homoglyph* | 4 |
| *keyword* | 8 |
| *margin* | 20, 74 |
| *baseline* | 96 |
| *default* | 84, 108 |
| *stemming* | 98 |

(Kemunculan tegak di Daftar Isi, Daftar Gambar/Tabel, dan Daftar Pustaka **tidak perlu** diperbaiki — itu wilayah abu-abu yang wajar.)

### C8 — Sebagian gambar masih berwarna
Dosen mensyaratkan diagram hitam-putih. Hasil pemindaian warna per gambar:

**Sudah grayscale ✅:** Gambar 2.3 (Waterfall), 2.4, 2.5, 2.6 (simbol UML), 3.1 (Struktur Organisasi), 3.2 (Flowchart), 4.1, 4.2 (pipeline), 4.3 (Arsitektur), 4.4 (Use Case), 4.5 (Activity), 4.6 (Sequence), 4.11, 4.12 (antarmuka)

**Masih berwarna ❌:**
| Gambar | Halaman cetak | Isi |
|---|---|---|
| **2.2** | 20 | Ilustrasi Hyperplane dan Margin |
| **4.7** | 94 | Confusion Matrix (heatmap biru) |
| **4.8** | 95 | Skor F1-macro per Fold (batang biru + garis merah) |
| **4.10** | 100 | Perbandingan Stemming |
| **4.13** | 103 | Rancangan Antarmuka Popup |

> **Nuansa penting:** semua **diagram** (UML, flowchart, arsitektur) sudah hitam-putih — bagian ini sudah patuh. Yang berwarna tinggal **grafik hasil matplotlib** dan **tangkapan layar antarmuka**.
>
> **Gambar 2.2 paling perlu dibereskan** karena itu ilustrasi konseptual, bukan grafik data — paling jelas masuk kategori "diagram".
>
> Untuk grafik 4.7/4.8/4.10, regenerasi grayscale gampang: di `src/train.py` ganti `cmap="Blues"` jadi `cmap="Greys"` (baris ~377) dan warna `#1565c0`/`#d32f2f` jadi `#404040`/`#000000`. Bilang saja kalau mau saya kerjakan.
>
> Gambar 4.13-4.15 adalah tangkapan layar antarmuka — warna di sini justru informatif (indikator hijau/merah status server). Ini defensible: *"tangkapan layar antarmuka ditampilkan berwarna karena warna merupakan bagian dari informasi yang disampaikan."*

### C9 — Banyak gambar/tabel tidak dirujuk dengan nomornya di teks
Pedoman: *"Tuliskan tabel tertentu secara spesifik, misalnya Tabel 1, saat merujuk suatu tabel"* — ditambah aturan dosen bahwa setiap gambar/tabel harus didahului kalimat pengantar.

**Sudah punya rujukan bernomor ✅:** Gambar 3.1, 4.6, 4.8, 4.9, 4.10, 4.13, 4.14 · Tabel 3.1, 4.3, 4.10, 4.11, 4.12, 4.13

**Belum dirujuk dengan nomor ❌:**
- Gambar: **2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5, 4.7, 4.11, 4.12, 4.15**
- Tabel: **2.1** (tertulis "tabel berikut", bukan "Tabel 2.1"), **4.1, 4.2, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9**

**Pola perbaikan** — sisipkan satu kalimat sebelum tiap gambar/tabel:
- Sebelum Gambar 2.1: *"Ilustrasi matriks bobot TF-IDF pada komentar YouTube disajikan pada Gambar 2.1."*
- Sebelum Gambar 2.2: *"Ilustrasi hyperplane dan margin pada Linear SVM ditunjukkan pada Gambar 2.2."*
- Tabel 2.1: ubah "dijabarkan pada tabel berikut" → *"dijabarkan pada **Tabel 2.1**."*
- Sebelum Tabel 4.1: *"Rincian kebutuhan perangkat lunak disajikan pada Tabel 4.1."*
- Sebelum Tabel 4.5: *"Rincian use case narrative menyaring komentar spam disajikan pada Tabel 4.5."* (pola sama untuk 4.6–4.9)
- Sebelum Gambar 4.1: *"Keseluruhan tahapan alur pelatihan model divisualisasikan pada Gambar 4.1."*

Ini yang paling makan waktu di antara semua temuan (± 26 sisipan), tapi paling mekanis. Kalau waktunya mepet, **prioritaskan tabel** — tabel lebih sering ditanya penguji daripada gambar.

---

## ❓ PERTANYAAN & CATATAN UNTUK ANDA

1. **VPS-nya sudah ada atau belum?** Ini menentukan K6 diselesaikan lewat jalur A atau B. Jawaban ini yang paling saya butuhkan.

2. **Ejaan Pembimbing II: "Septiana" atau "Septiani"?** (P4)

3. **Gaya sitasi: mau pakai `&` (APA) atau `dan` (pedoman)?** Saran saya tetap `&` karena Daftar Pustaka sudah APA penuh — tinggal ubah satu-satunya `Sari dan Asmendri` jadi `&`, jauh lebih sedikit editan daripada mengubah 7 sumber. (P5b)

4. **Format Daftar Pustaka.** Draft memakai APA 7 penuh (dengan DOI). Pedoman hal. 32 mencontohkan format lain: `Nama (tahun). "Judul". Kota, Penerbit.` Menurut saya **jangan diubah** — APA lebih standar, konsisten, dan lebih informatif. Tapi siapkan jawaban kalau ditanya: *"Daftar Pustaka disusun mengikuti gaya APA 7th edition secara konsisten, tetap memenuhi ketentuan pedoman yaitu urut alfabetis tanpa gelar, minimum 15 referensi, dan tahun terbit tidak lebih dari 10 tahun."* Semua tiga syarat itu memang terpenuhi. ✅

5. **Sumber Wikipedia (hal. 46-48).** Ini **aman** — pedoman hal. 33 secara eksplisit mengizinkan: *"tulisan tersebut harus berada pada website website berbasis keilmuan (**Wikipedia** atau website yang dimiliki sebuah kampus)"*. Kalau ditanya penguji, kutip halaman itu.

6. **Judul BAB III = "OBJEK PENELITIAN"** — sudah tepat, persis mengikuti template Daftar Isi pedoman (L-10). Jangan diubah.

7. **(Pratama, 2026)** — referensi tahun 2026 di skripsi 2026. Secara aturan tidak masalah (batasnya *terlalu tua*, bukan terlalu baru), tapi pastikan jurnalnya memang sudah terbit, bukan *in press*. Kalau ditanya, siap dengan bukti terbitnya.

8. **`hard_test_set` disebut "141 kasus ambigu" di `reports/hybrid_ablation.txt`** padahal isinya 135. Skripsi sudah benar menulis 135, jadi tidak ada yang perlu diubah di skripsi — hanya label di file laporan yang usang. Tidak perlu diapa-apakan kecuali file itu ikut dilampirkan.

9. **Saran non-wajib untuk memperkuat BAB IV:** hard test set berisi 135 komentar non-spam semua, dan skripsi sudah jujur menjelaskan ini di 4.10.5 (bagus!). Kalau ada waktu, menambahkan ~30 komentar spam ter-*obfuscate* ke hard test set akan membuatnya jadi uji ketangguhan dua arah. Tapi ini **jangan dikerjakan sekarang** — draft besok harus disubmit, dan ini akan mengubah semua angka.

---

## URUTAN KERJA YANG SAYA SARANKAN

**Tahap 1 — 45 menit, wajib:**
1. K1 caption `Gambar 2II.6` → `Gambar 2.6` *(2 menit)*
2. K3 dua rujukan silang di hal. 93 *(3 menit)*
3. K2 kalimat stemming di 4.5.5 *(5 menit)*
4. P3 `xii` → `xiii` di abstrak *(1 menit)*
5. P4 nama Pembimbing II *(1 menit, setelah dikonfirmasi)*
6. C1 semua typo *(5 menit)*
7. C2 desimal titik → koma *(5 menit)*
8. ~~K5 lengkapi Daftar Pustaka~~ ✅ SELESAI
9. P1 nomor halaman Daftar Pustaka *(5 menit)*

**Tahap 2 — 1 jam, sangat disarankan:**
10. K6 putuskan VPS vs localhost *(tergantung jawaban Anda)*
11. ~~K4 tulis ulang 2.11~~ ✅ SELESAI
12. P7 lima paragraf penutup *(15 menit, teks sudah saya siapkan)*
13. ~~P5 + P6 gaya sitasi~~ ✅ SELESAI
14. P2 halaman L-1 *(5 menit)*

**Tahap 3 — kalau masih ada waktu:**
15. C9 sisipkan rujukan bernomor (dahulukan tabel)
16. C8 regenerasi Gambar 2.2 jadi hitam-putih
17. C3, C4, C5, C6, C7

---

**Kesimpulan saya:** substansi skripsi ini kuat dan datanya bersih — itu bagian yang paling susah, dan sudah beres. Yang tersisa murni kerapian editorial. Kalau Tahap 1 dan 2 dikerjakan, draft ini siap disubmit dengan percaya diri.

---

# EVALUASI ULANG MENYELURUH — 1 Agustus 2026 (sebelum penyusunan PPT sidang)

Audit dijalankan ulang dari nol terhadap `Skripsi/1-AKTIF/[DRAFT] 221232017.docx`, bukan sekadar mengecek daftar temuan lama. Seluruh angka empiris dihitung ulang dari `data/comments.csv`.

## A. Angka empiris — SEMUA COCOK PERSIS

`data/comments.csv` tidak berubah sejak 30 Juni. Pipeline dijalankan ulang penuh:

| Klaim skripsi | Hasil hitung ulang | Status |
|---|---|---|
| 6.690 baris (2.332 spam / 4.358 non-spam) | idem | cocok |
| Latih 5.352 / uji 1.338 | idem | cocok |
| Akurasi 97,53% · F1-macro 0,9726 | 0,9753 / 0,9726 | cocok |
| Confusion matrix 863 / 9 / 24 / 442 | idem | cocok |
| Presisi spam 0,98 · recall 0,95 (Tabel 4.10) | 0,9800 / 0,9485 | cocok (pembulatan 2 desimal) |
| CV 5-fold 0,9741 ± 0,0030 | idem | cocok |
| C terbaik = 1 (GridSearchCV) | idem | cocok |
| LogReg 97,09% / 0,9675 · MultinomialNB 93,95% / 0,9313 | idem | cocok |
| Hard set 135 kasus, 98,52%, 2 FP, 0 FN | idem | cocok |
| Ablasi hibrida −7,32 / −16,30 poin | idem | cocok |

## B. Temuan baru

| # | Prioritas | Temuan |
|---|---|---|
| **E1** | KRITIS | Abstrak menulis **"(xiii + 11 halaman + 0 lampiran)"**. Badan skripsi bernomor 1–110 (PDF hal. 14–123), jadi seharusnya **110 halaman**. Angka "110" terpotong jadi "11". `xiii` sendiri sudah benar (front matter PDF 1–13). |
| **E2** | KRITIS | Kode masih `localhost:8000` di 7 tempat sementara skripsi mengklaim *deploy* VPS. Penulis menyatakan akan benar-benar deploy — harus tuntas sebelum sidang, kalau tidak demo berjalan lokal sementara dokumen mengklaim VPS. |
| **E3** | PENTING | **23 dari 38 gambar/tabel tidak pernah disebut nomornya di badan teks** (melanggar arahan lisan dosen soal kalimat pengantar). |
| **E4** | PENTING | **2 sub-bab BAB II tanpa kalimat penutup sintesis**: **2.15 UML** (berakhir pada definisi Sequence Diagram + caption) dan **2.18 Persyaratan Sistem Konseptual** (berakhir pada butir daftar "Pengembangan (Improvement): …"). Temuan P7 lama menyebut 5 sub-bab — 2.9, 2.10, 2.11, 2.14, 2.16 kini **sudah** punya sintesis, jadi P7 menyusut jadi 2. |
| **E5** | PENTING | **5 gambar masih berwarna** padahal dosen meminta hitam-putih: **2.2** (hyperplane), **4.7** (heatmap confusion matrix), **4.8** (F1 per fold), **4.10** (perbandingan stemming), **4.13** (mockup popup). 4.7/4.8/4.10 dihasilkan matplotlib di `src/train.py` → bisa diregenerasi dengan `cmap="Greys"`. Gambar 4.14/4.15 berwarna tetapi berupa tangkapan layar, masih bisa dipertahankan. |
| **E6** | SEDANG | Halaman **L-1 kosong** masih ada (PDF hal. 127) sementara abstrak menyatakan "0 lampiran". |
| **E7** | KOSMETIK | Cetak miring tercampur pada 3 istilah, masing-masing hanya 1 kemunculan tegak: *stemming* (1 dari 22), *dataset* (1 dari 40), *real-time* (1 dari 20). `margin` konsisten tegak 6× — keputusan penulis. |
| **E8** | KOSMETIK | Ada paragraf **Heading 1 kosong** tepat sebelum BAB V (par 904). Tidak bernomor sehingga tidak merusak penomoran bab maupun Daftar Isi, tetapi menyisakan baris kosong berukuran heading. |

## C. Yang sudah bersih (diverifikasi ulang, bukan diasumsikan)

- **Rujukan silang**: 11 rujukan "Sub-bab X.Y" semuanya resolve; 0 rujukan Gambar/Tabel menggantung.
- **Caption**: 38 caption, 0 nilai `SEQ` tersimpan yang salah, penempatan 100% benar (tabel di atas, gambar di bawah), tidak ada yang diakhiri titik.
- **Daftar Pustaka**: 30 entri, 2018–2026 (≤10 tahun), 0 entri tidak dikutip, 0 sitasi tanpa entri, 0 "et al.".
- **Bahasa**: 0 "dimana", 0 kalimat diawali "Sehingga"/"Sedangkan", 0 desimal bertitik, 0 bullet. Kata "saya"/"penulis" hanya di Lembar Pernyataan dan Kata Pengantar — keduanya diizinkan pedoman 4.6.2.
- **Abstrak**: 234 kata (pedoman 200–250), 5 kata kunci, 4 paragraf sesuai template L-15, baris "Daftar Pustaka (2018-2026)" **ada dan akurat**.
- **Penomoran halaman**: sec2–sec6 (BAB I–V) semua benar — nomor kanan atas pada halaman lanjutan, bawah-tengah pada halaman pembuka BAB, tanpa restart. Daftar Pustaka tanpa nomor (sesuai keputusan penulis), Lampiran memakai `L-n`.

## D. Tindak lanjut E1–E8 — 1 Agustus 2026

| # | Status | Tindakan |
|---|---|---|
| E1 | SELESAI (oleh penulis) | Abstrak kini `(xiii + 110 halaman + 0 lampiran)` |
| E2 | TERTUNDA | Deploy VPS menyusul; kode masih `localhost:8000` |
| E3 | SELESAI | 22 kalimat pengantar ditambahkan; **0 dari 38** gambar/tabel kini tanpa rujukan (Gambar 4.11 dan 4.12 dirujuk dalam satu kalimat) |
| E4 | SELESAI | Penutup sintesis ditambahkan pada **2.15 UML** dan **2.18 Persyaratan Sistem Konseptual** |
| E5 | **BUKAN MASALAH** | Lihat catatan di bawah |
| E6 | SELESAI | Dua section lampiran kosong dihapus; pengaturan section Daftar Pustaka dipindah ke level body. Section 10 → 8, dokumen berakhir pada entri pustaka terakhir |
| E7 | SELESAI | 21 kemunculan istilah asing dimiringkan (*stemming*, *dataset*, *real-time*, *recall*, *accuracy*, *linear*, *server*, *online*, *slider*, *p-value*, *N-gram*, *hard test set*) |
| E8 | SELESAI (dengan koreksi) | Paragraf tersebut **memuat `sectPr` yang memulai BAB V** — menghapusnya akan merusak penomoran halaman. Gaya diturunkan Heading 1 → Normal, section break dipertahankan |

### Koreksi E5 — laporan sebelumnya keliru

Analisis pertama menyebut Gambar 2.2 dan 3.2 "dark mode" (kecerahan rata-rata 64,8 dan 37,5). **Itu artefak pengukuran**: kedua PNG punya latar transparan, dan `Image.convert('L')` menjadikan piksel transparan hitam. Setelah transparansi dikomposit ke putih seperti kondisi cetak sebenarnya, kecerahannya 240,8 dan 248,5 — keduanya berlatar terang.

Kelima gambar berwarna (2.2, 4.7, 4.8, 4.10, 4.13) juga dirender ulang ke grayscale dan diperiksa secara visual: **semuanya tetap terbaca**. Titik biru dan hijau pada Gambar 2.2 menjadi abu gelap dan abu terang yang masih kontras; angka pada heatmap 4.7 tetap jelas; batang pada 4.8 dan 4.10 tetap terbeda; mockup 4.13 tetap terbaca. **Tidak ada gambar yang perlu diubah.**

### Sisa keputusan cetak miring (penulis)

Istilah berikut konsisten tegak di badan teks dan perlu keputusan apakah termasuk serapan KBBI: `margin` (7×), `label` (16×), `file` (9×), `input` (6×), `output` (5×), `token` (3×), `link` (1×). Juga `spam` (104× tegak, 2× miring), `web`, `bot`, `ham` — kemungkinan besar sudah serapan sehingga tegak sudah benar; yang perlu diseragamkan hanya beberapa kemunculan miring yang tersisa.

### Keputusan cetak miring lanjutan (1 Agustus 2026)

Penulis memutuskan `margin`, `token`, dan `link` bukan serapan KBBI sehingga harus dimiringkan. Diterapkan: **`margin` 7× dan `token` 3×** di badan teks.

`link` **tidak** dimiringkan. Satu-satunya kemunculannya ada di dalam kutipan contoh komentar spam — `"link slot paling gacor hari ini"` — yang seluruhnya ditulis tegak sebagai data mentah. Memiringkan satu kata di dalam kutipan verbatim akan tidak konsisten dengan contoh komentar lainnya.

Caption dan judul sengaja dilewati (Gambar 2.2 masih memuat kata "Margin" tegak pada judulnya), mengikuti kelaziman bahwa judul gambar/tabel tidak dimiringkan per istilah.

## E. Verifikasi 30 rujukan — 1 Agustus 2026 (SELESAI)

Ke-30 entri Daftar Pustaka diverifikasi satu per satu lewat Crossref API dan halaman penerbit. **Semua rujukan nyata — tidak ada yang halusinasi**, tetapi ditemukan **6 kesalahan data**, dua di antaranya berupa daftar penulis yang keliru sepenuhnya.

| # | Entri | Kesalahan | Koreksi | Lokasi |
|---|---|---|---|---|
| R1 | ~~Apricia dkk. (2024)~~ | **Daftar penulis salah total.** Judul, jurnal, volume, dan halaman benar | **Azzahra, F. N., Rohana, T., Rahmat, R., & Juwita, A. R.** | Daftar Pustaka + sitasi di **Sub-bab 2.7.1** |
| R2 | ~~Maulana (2025)~~ | **Maulana adalah penulis ketiga**, bukan pertama; volume salah | **Firizkiansah, A., Muhammad, A., & Maulana, I. R.** — JIKOMTI **2(1), 29–36** | Daftar Pustaka + sitasi di **Sub-bab 2.7.2** |
| R3 | Anis dkk. (2024) | Nomor terbitan, halaman, dan DOI salah | **6(2), 329–338**, DOI `10.47233/jteksis.v6i2.1351` | Daftar Pustaka |
| R4 | Azhari (2022) | Halaman salah | **58–65** (bukan 80–87) | Daftar Pustaka |
| R5 | Iriananda dkk. (2024) | Halaman salah | **743–752** (bukan 835–846) | Daftar Pustaka |
| R6 | Ardiansyah dkk. (2025) | Memakai URL OJS, bukan DOI | DOI `10.60076/indotech.v3i3.1762` | Daftar Pustaka |

Sitasi dalam teks ikut diperbarui: `(Apricia dkk., 2024)` → `(Azzahra dkk., 2024)`, `(Maulana, 2025)` → `(Firizkiansah dkk., 2025)`. Urutan alfabetis disesuaikan (Azzahra setelah Azhari, Firizkiansah setelah Efrizoni). Hasil akhir: **30 entri, alfabetis, 0 yatim dua arah, media file identik.**

**Terverifikasi benar tanpa perubahan:** Abdillah, Airlangga 2024a/b, Angelo, Arrayyan (22(2), 2066–2075), Chua, Efrizoni, Helmiyah, Herawati, Kaddoura (e830), Khairunnisa, Khan, Koprawi, Nanda, Oktavia, Pratama, Putri, Ramadhan, Sari & Asmendri, Sinaga, serta empat sumber buku/web (Géron, Sugiyono, Rosa & Shalahuddin, Wikipedia).

### Pemeriksaan salah ketik

Bersih: tidak ada kata ganda, tidak ada titik tanpa spasi, tidak ada desimal bertitik. Tiga "spasi ganda" berada di blok identitas (`Nama   :` / `NIM     :`) yang memang sengaja diratakan. Pola seperti `maka . Nilai .` adalah rumus inline OMML yang tidak terbaca python-docx, **bukan** salah ketik.

Inkonsistensi ringan yang dibiarkan (keputusan penulis): `Ekstensi Chrome` (2×) vs `ekstensi Chrome` (4×); `peladen` (21×) vs `server` (58×); `kata kunci` (22×) vs `keyword` (5×); `peramban` (34×) vs `browser` (2×); satu `daring` di antara 57 `online`.

### Pelengkapan DOI (1 Agustus 2026)

Empat DOI ditemukan lewat pencarian Crossref (`api.crossref.org/works?query.bibliographic=…`) dan ditambahkan sebagai hyperlink asli bergaya `Hyperlink` agar seragam dengan entri lain.

| Entri | DOI |
|---|---|
| Abdillah dkk. (2021) | `10.46772/intech.v3i02.556` |
| Azzahra dkk. (2024) | `10.47065/josh.v5i3.5070` (menggantikan URL OJS) |
| Khan (2018) | `10.54692/ijeci.2018.020425` |
| Nanda dkk. (2022) | `10.32672/jnkti.v5i2.4193` |

**Temuan ke-7 (R7):** verifikasi DOI Khan menunjukkan artikel tersebut terbit pada **Volume 2, Issue 4**, bukan 2(2) seperti tertulis. Sudah diperbaiki.

Oktavia dkk. ditambahi URL artikel. **Tujuh entri sisanya memang tidak punya DOI dan itu wajar**: tiga buku (Géron, Rosa & Shalahuddin, Sugiyono), satu laman web (Wikipedia), serta tiga jurnal yang tidak terdaftar Crossref (Firizkiansah/JIKOMTI, Putri/JEISBI, Oktavia/BIIKMA) — ketiganya sudah mencantumkan URL artikel sesuai APA.

### Bekal menghadapi pertanyaan sumber buku

Tiga buku hanya menyangga klaim yang sangat spesifik, sehingga yang perlu dikuasai adalah klaimnya, bukan keseluruhan isi buku.

| Buku | Lokasi | Klaim yang disitasi | Pendukung |
|---|---|---|---|
| Géron (2022) | Sub-bab 2.6.1 | *Platt Scaling*: keluaran fungsi keputusan SVM dipetakan ke probabilitas lewat sigmoid; parameter A dan B diestimasi via *cross-validation* internal terpisah dari pembentukan *hyperplane* | **Terverifikasi di kode**: `src/train.py:240`, `:339` (`probability=True`), `src/server.py:307` (`predict_proba`) |
| Rosa & Shalahuddin (2019) | Sub-bab 2.15 | Definisi UML sebagai bahasa pemodelan grafis untuk identifikasi kebutuhan, perancangan arsitektur, dan dokumentasi spesifikasi berorientasi objek | Alasan pemilihan tiga diagram sudah tertulis di kalimat penutup 2.15 |
| Sugiyono (2022) | Sub-bab 1.4 dan 1.4.2 | Definisi metode penelitian (rasional, empiris, sistematis) dan definisi observasi | — |

Klaim Géron adalah yang paling teknis sekaligus paling mudah dipertahankan karena dapat ditunjukkan langsung pada kode. Nomor halaman buku sengaja tidak dicantumkan di sini — sebaiknya diverifikasi sendiri dari PDF bukunya daripada mengarang.
