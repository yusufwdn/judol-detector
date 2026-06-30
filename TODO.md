# TODO & Roadmap — Judol Spam Detector

> Dokumen ini adalah peta jalan pengembangan proyek, ditulis supaya kamu (sebagai
> pemilik proyek) tahu **apa yang harus dikerjakan, kenapa itu penting, dan
> urutannya gimana**. Setiap fase punya tujuan, alasan, dan saran konkret.
>
> Cara pakai: kerjakan dari Fase 0 ke bawah secara berurutan. Tiap selesai satu
> item, centang `[x]`. Tidak semua fase wajib — ada yang opsional tergantung
> waktu dan target skripsi kamu (lihat catatan prioritas di tiap fase).

---

## Daftar Isi

- [Fase 0 — Housekeeping (Quick Wins, lakukan duluan)](#fase-0--housekeeping-quick-wins-lakukan-duluan)
- [Fase 1 — Kualitas Dataset](#fase-1--kualitas-dataset-prioritas-tertinggi)
- [Fase 2 — Evaluasi Model yang Lebih Jujur](#fase-2--evaluasi-model-yang-lebih-jujur)
- [Fase 3 — Preprocessing & Eksperimen Model](#fase-3--preprocessing--eksperimen-model)
- [Fase 4 — Robustness Extension](#fase-4--robustness-extension)
- [Fase 5 — Deployment (Opsional)](#fase-5--deployment-opsional)
- [Fase 6 — Penulisan Skripsi](#fase-6--penulisan-skripsi)
- [Tips Belajar & Cara Kerja untuk Junior](#tips-belajar--cara-kerja-untuk-junior)
- [Pertanyaan untuk Diskusi Lanjut](#pertanyaan-untuk-diskusi-lanjut)

---

## Fase 0 — Housekeeping (Quick Wins, lakukan duluan)

**Tujuan:** Bikin proyek ini "aman" dan rapi secara administratif sebelum kamu
mulai bereksperimen lebih jauh. Ini bukan kerjaan AI/ML, tapi penting supaya
kerja kerasmu tidak hilang.

- [✅] **Inisialisasi Git repository.**
  Saat ini proyek **belum** di-track oleh Git. Artinya kalau ada file
  ke-overwrite atau ke-hapus tidak sengaja (misalnya `data/comments.csv` atau
  `model/svm_model.joblib` setelah re-training), kamu tidak punya cara untuk
  kembali ke versi sebelumnya.
  ```bash
  git init
  git add <file-file penting>
  git commit -m "initial commit"
  ```

- [✅] **Buat `.gitignore`.**
  Beberapa folder/file sebaiknya TIDAK di-commit:
  - `env/` — virtual environment Python (ribuan file, besar banget, bisa
    di-generate ulang dari `requirements.txt`)
  - `__pycache__/`, `*.pyc`
  - `node_modules/` (kalau nanti `npm install` di folder `scraper/`)
  - `.env` (berisi API key — **jangan pernah** ikut ter-commit)

  Contoh isi `.gitignore`:
  ```
  env/
  __pycache__/
  *.pyc
  node_modules/
  .env
  ```

- [✅] **Putuskan: `model/svm_model.joblib` dan `data/comments.csv` masuk Git
  atau tidak?**
  Dua pendapat:
  - **Masuk Git** → reviewer (dosen) bisa langsung clone dan jalankan tanpa
    perlu re-generate dataset/model. Cocok untuk skripsi.
  - **Tidak masuk Git** (di-`.gitignore`) → repo tetap kecil, tapi orang lain
    harus jalankan `prepare_dataset.py` + `train.py` dulu.

  **Saran:** untuk skripsi, masukkan saja keduanya — ukurannya kecil (model
  ~165 KB, dataset ~1800 baris) dan memudahkan reproduksi.

- [✅] **Cek `.env` scraper tidak ke-expose.**
  File `.env` berisi `YOUTUBE_API_KEY`. Pastikan file ini ada di `.gitignore`
  SEBELUM commit pertama. Kalau API key sudah pernah ke-push ke remote
  (GitHub dll), segera regenerate key tersebut di Google Cloud Console.

---

## Fase 1 — Kualitas Dataset (Prioritas Tertinggi)

**Tujuan:** Dataset adalah fondasi seluruh sistem. Model SVM sehebat apapun
tidak akan berguna kalau datanya tidak representatif. Ini adalah area dengan
**ROI (return on investment) tertinggi** untuk skripsimu — perbaikan di sini
akan terlihat langsung di hasil evaluasi.

- [✅] **Kumpulkan komentar non-spam ASLI dari YouTube** (bukan sintetis).
  Saat ini 700 sampel non-spam dibuat dari template (`NON_SPAM_TEMPLATES` di
  `prepare_dataset.py`). Ini "kompromi pragmatis", bukan ideal.

  **Scraper sudah mendukung mode non_spam** — tinggal jalankan dan integrasikan:
  1. Scrape komentar non-spam dari beberapa video dengan perintah:
     ```bash
     node scraper/index.js <VIDEO_ID> video non_spam
     ```
  2. Agregasikan dengan `node scraper/filter.js` → hasilnya di `scraper/final_non_spam.json`.
  3. **Review manual** sebagian untuk memastikan memang bukan spam.
  4. Modifikasi `prepare_dataset.py`: ganti/lengkapi `generate_non_spam_data()`
     dengan loader yang membaca `scraper/final_non_spam.json`.

  **Kenapa ini penting?** Distribusi kalimat sintetis (template) cenderung
  "terlalu bersih" — pola kalimatnya seragam. Model bisa jadi belajar
  membedakan "gaya template" vs "gaya spam", bukan "spam vs bukan spam" yang
  sesungguhnya. Ini bisa membuat performa di real-world lebih buruk dari yang
  ditunjukkan test set.

- [✅] **Scrape lebih banyak video untuk variasi spam.**
  Variasi video (gaming, berita, musik, podcast, edukasi) akan menangkap gaya
  spam yang berbeda-beda. Jalankan:
  ```bash
  node scraper/index.js <VIDEO_ID> video spam
  ```
  pada beberapa video populer Indonesia dari kategori berbeda. Setelah selesai,
  jalankan `node scraper/filter.js` untuk mengagregasi ke `scraper/final_spam.json`.

- [✅] **Kumpulkan "hard examples" / kasus ambigu secara manual.**
  141 komentar dari dua video YouTube bertema judi online:
  - `kM99uBssHvQ` — 70 non_spam (kritik, cerita rugi, permintaan blokir)
  - `pzE8S6N0vwo` — 71 non_spam (diskusi anti-judol di video finansial)
  Review manual mengkonfirmasi semuanya bukan spam promosi.
  → File: `data/hard_test_set.csv` (141 entri, kolom: text, label, source_video, note)

- [✅] **Dokumentasikan jumlah data setiap kali dataset diperbarui.**
  Catat di README atau di file log sederhana: tanggal, jumlah spam, jumlah
  non-spam, sumber video. Ini berguna untuk bab metodologi skripsi (perlu
  menjelaskan "dataset versi berapa yang dipakai untuk hasil X").
  → Lihat [DATASET_LOG.md](DATASET_LOG.md)

- [x] **`data/comments.csv` di-rebuild ulang (2026-06-30).**
  Ditemukan saat audit dokumentasi: `comments.csv` yang ter-commit sedikit
  "stale" dibanding hasil rebuild murni dari `prepare_dataset.py` (selisih 3
  baris kategori, kemungkinan dari entry yang masuk lewat endpoint
  `POST /report` tanpa full rebuild). Sudah dijalankan ulang
  `python src/prepare_dataset.py && python src/train.py` — dataset sekarang
  **2271 spam / 2861 non-spam = 5132**, model di-retrain (97.57% accuracy,
  F1-macro 0.9752), dan semua angka di README/PENJELASAN_TEKNIS sudah
  disinkronkan ke hasil rebuild ini.

---

## Fase 2 — Evaluasi Model yang Lebih Jujur

**Tujuan:** Membuat evaluasi lebih kredibel untuk sidang — bukan hanya satu angka akurasi dari satu split.
→ Lihat penjelasan lengkap di [PENJELASAN_TEKNIS.md §16](PENJELASAN_TEKNIS.md#16-evaluasi-model-yang-lebih-jujur-fase-2)
→ Hasil tercatat di [DATASET_LOG.md](DATASET_LOG.md)

- [✅] **Buat "hard test set" terpisah** dari hasil Fase 1 (kasus ambigu).
  Selesai. Hasil evaluasi: accuracy 75.71%, 17 FP dari 70 non_spam hard examples.
  Hybrid Rule A menyelamatkan 35 komentar yang tanpanya akan jadi FP.
  → Script: `src/evaluate_hard_set.py`
  → Laporan: `reports/hard_set_evaluation.txt`
  → Penjelasan: `PENJELASAN_TEKNIS.md §29`

- [✅] **Tambahkan k-fold cross-validation** sebagai pelengkap train-test split.
  Sudah diimplementasikan di `src/train.py`. Dijalankan otomatis setiap
  `python src/train.py`. Hasil: **F1-macro 96.61% ± 0.59%** di 5 fold.

- [✅] **Hyperparameter tuning sistematis** (bukan coba-coba manual).
  `GridSearchCV` dengan `C ∈ [0.01, 0.1, 1, 10, 100]` sudah berjalan di
  `src/train.py`. Hasil: **C=1 terpilih** (F1-macro CV 0.9543) — sekarang ada
  justifikasi empiris, bukan sekadar default.

- [✅] **Bandingkan SVM dengan baseline lain** (sebagai pembanding, bukan
  pengganti). Sudah diimplementasikan di `src/train.py`. Hasil:
  - SVM: accuracy 97.23%, F1-macro 0.9671 ✓
  - Naive Bayes: accuracy 94.32%, F1-macro 0.9305
  - Logistic Regression: accuracy 95.15%, F1-macro 0.9423

- [✅] **Visualisasikan confusion matrix** dengan `matplotlib`/`seaborn`.
  Tersimpan otomatis ke `reports/` setiap run training:
  - `reports/confusion_matrix_svm.png`
  - `reports/confusion_matrix_naive_bayes_multinomialnb.png`
  - `reports/confusion_matrix_logistic_regression.png`

- [✅] **Ablation study: SVM murni vs SVM + Hybrid Rules (2026-06-30).**
  Dibuat `src/evaluate_hybrid_ablation.py` — hasil tersimpan di
  `reports/hybrid_ablation.txt`. Temuan: hybrid rule yang sebelumnya dianggap
  membantu (lihat `PENJELASAN_TEKNIS.md §22/§26/§32`) ternyata **menurunkan**
  accuracy 6–13 poin persentase setelah model dilatih ulang dengan dataset
  yang lebih besar — SVM murni menang di train-test split (97.57% vs 91.33%)
  **dan** di hard test set (92.91% vs 80.14%). Rule B (non_spam→spam) gagal
  100% (0 benar dari 27× nyala). Hybrid rule dinonaktifkan via
  `ENABLE_HYBRID_RULES = False` di `src/server.py` (kode dipertahankan,
  bukan dihapus). Detail lengkap + kalimat siap kutip untuk sidang di
  [PENJELASAN_TEKNIS.md §33](PENJELASAN_TEKNIS.md#33-ablation-study-hybrid-rules--kenapa-akhirnya-dimatikan).

---

## Fase 3 — Preprocessing & Eksperimen Model

**Tujuan:** Setelah dataset dan evaluasi lebih solid, ini saatnya
bereksperimen meningkatkan kualitas model itu sendiri.

> ⚠️ **Aturan wajib:** Setiap kali `src/preprocessing.py` diubah, kamu HARUS
> jalankan ulang `prepare_dataset.py` lalu `train.py`. Kalau tidak, terjadi
> *training-serving skew* (sudah dijelaskan lengkap di
> [`PENJELASAN_TEKNIS.md`](PENJELASAN_TEKNIS.md) bagian 11).

- [✅] **Coba stemming dengan Sastrawi.**
  Dieksperimen di `src/experiment_stemming.py`. Hasil: perbedaan F1-macro
  hanya +0.0002 (0.9671 → 0.9672) — tidak signifikan. Model produksi tetap
  tanpa stemming. Penjelasan + kalimat siap kutip untuk skripsi ada di
  [PENJELASAN_TEKNIS.md §18](PENJELASAN_TEKNIS.md#18-eksperimen-stemming--apakah-stemming-membantu).

- [ ] **Tambah stopwords domain-spesifik** ("kak", "bang", "min", "subscribe",
  "like", "video", "nonton", dll) ke `STOPWORDS_ID`.
  ⚠️ Dari hasil inspeksi fitur ([PENJELASAN_TEKNIS.md §17](PENJELASAN_TEKNIS.md#17-inspeksi-fitur--apa-yang-dipelajari-model)),
  `bang` dan `dok` justru menjadi sinyal non-spam yang kuat (bobot -1.55 dan
  -1.39). Ini terjadi karena kata-kata itu sangat umum di komentar percakapan
  biasa tapi hampir tidak pernah muncul di komentar spam — persis kebalikan
  dari yang diharapkan stopword. Menghapusnya akan menghilangkan sinyal
  diskriminatif yang sudah dipelajari model, sehingga performa kemungkinan
  turun. Eksperimen tetap bisa dilakukan untuk membuktikannya, tapi hasilnya
  sudah bisa diprediksi dari data inspeksi fitur.

- [✅] **Inspeksi fitur paling berpengaruh (support vectors / koefisien).**
  Diimplementasikan di `src/inspect_features.py`. Jalankan setelah training:
  `python src/inspect_features.py`. Output tersimpan di `reports/`:
  - `top_features.png` — bar chart dua panel siap pakai di skripsi
  - `feature_weights.csv` — seluruh ~4000 fitur dan bobotnya
  → Penjelasan lengkap (termasuk kalimat untuk bab metodologi) di
  [PENJELASAN_TEKNIS.md §17](PENJELASAN_TEKNIS.md#17-inspeksi-fitur--apa-yang-dipelajari-model)

- [✅] **Eksperimen `max_features` dan `ngram_range`.**
  Dieksperimen di `src/experiment_features.py`. Hasil utama:
  - Unigram saja (1,1) sedikit lebih baik (+0.0034) — tidak signifikan secara praktis
  - Trigram tidak membantu sama sekali
  - max_features tidak relevan: vocabulary aktual hanya 4.056, jauh di bawah batas
  - Konfigurasi baseline dipertahankan
  → Penjelasan + kalimat siap kutip di
  [PENJELASAN_TEKNIS.md §19](PENJELASAN_TEKNIS.md#19-eksperimen-konfigurasi-tf-idf--ngram-dan-max_features)

---

## Fase 4 — Robustness Extension

**Tujuan:** Pastikan extension benar-benar bekerja di kondisi nyata, bukan
hanya secara teori.

- [✅] **Uji coba langsung di YouTube** (load unpacked extension, scroll
  komentar, cek console log, screenshot hasil deteksi).
  Diuji pada video `pzE8S6N0vwo` (finansial/anti-judol). Temuan:
  - Komentar korban/diskusi anti-judol awalnya banyak yang ter-flag → diperbaiki
    dengan menghapus `slot` dan `deposit` dari HARD_SPAM_SIGNALS (Versi 8)
  - `H0KI777` (leet speak dengan digit `0`) tidak terdeteksi → diperbaiki
    dengan tambah Step 5b-i normalisasi leet di preprocessing

- [x] **~~Cek selector Instagram~~ — di luar scope, diabaikan.**
  Judul skripsi ("...DETEKSI KOMENTAR SPAM JUDI ONLINE PADA YOUTUBE BERBASIS
  CHROME EXTENSION") secara eksplisit hanya menyebut YouTube. Selector
  Instagram di `content.js` (`ul._a9ym li`, `span._aacl`) dibiarkan apa
  adanya sebagai kode tambahan yang tidak diverifikasi/tidak diklaim — kalau
  ditanya saat sidang, jawab bahwa scope proyek memang dibatasi ke YouTube
  sesuai judul, Instagram bukan bagian dari kontribusi yang diuji.

- [✅] **Buat threshold confidence bisa diatur dari popup.**
  Slider ditambahkan di `popup.html` (range 50%–95%, step 5%). Nilai disimpan
  ke `chrome.storage` dan dibaca oleh `content.js` saat init. Perubahan slider
  langsung aktif di tab yang sedang buka (tanpa perlu reload) via
  `chrome.storage.onChanged` listener.

- [✅] **Tambahkan `scannedCount` yang sebenarnya.**
  Bug diperbaiki di `content.js`: `scannedCount` sekarang diincrement di
  `scanComments()` dan disimpan ke `chrome.storage` via `persistStats()`.
  Popup sekarang menampilkan angka yang akurat.

- [✅] **Tangani kasus server mati di tengah sesi.**
  `predictBatch()` sekarang memanggil `checkServerHealth()` saat terjadi
  network error. Ini memperbarui `isServerAvailable = false` sehingga scan
  berikutnya tidak lagi mencoba hit server yang sudah mati.

---

## Fase 5 — Deployment (Opsional)

**Tujuan:** Membuat sistem lebih mudah dipakai orang lain (di luar konteks
skripsi murni). **Fase ini opsional** — kerjakan hanya jika Fase 1–4 sudah
solid dan kamu masih punya waktu/energi.

- [ ] **Packaging server jadi executable** (misal dengan `PyInstaller`) supaya
  pengguna awam tidak perlu install Python + dependencies manual.

- [ ] **Auto-start server** — opsi launcher yang menjalankan server di
  background saat Chrome dibuka (kompleks, butuh native messaging atau
  installer terpisah).

- [ ] *(Eksplorasi jangka panjang, bukan prioritas)* Riset konversi model ke
  ONNX Runtime Web / TensorFlow.js agar prediksi berjalan langsung di
  browser tanpa server Python. Ini sudah disebut di FAQ dokumentasi sebagai
  "di luar scope skripsi" — realistis untuk dijadikan bagian "future work",
  bukan dikerjakan sekarang.

---

## Fase 6 — Penulisan Skripsi

**Tujuan:** Menerjemahkan seluruh kerja teknis menjadi narasi akademis yang
koheren.

- [ ] **Bab Metodologi:** Jelaskan alur Fase 0–3 di atas sebagai metodologi
  penelitian — pengumpulan data (scraper + heuristik scoring), pembersihan
  data (two-pass filter), preprocessing (7 layer), pemodelan (TF-IDF + SVM),
  evaluasi (cross-validation, hyperparameter tuning).

- [ ] **Bab Hasil & Pembahasan:** Sajikan hasil dari Fase 2 — termasuk hasil
  pada hard test set (jangan hanya tampilkan angka 100% dari test set biasa).
  Bahas *kenapa* model bisa salah pada kasus tertentu (analisis error/error
  analysis).

- [ ] **Bab Implementasi:** Jelaskan arsitektur sistem (extension + server),
  bisa langsung adaptasi dari diagram di `README.md` dan
  `PENJELASAN_TEKNIS.md`.

- [ ] **Bab Keterbatasan & Saran:** Tulis jujur — dependency server lokal,
  data non-spam sintetis (jika belum sempat diganti), selector extension yang
  rapuh terhadap perubahan UI platform, dll. Penguji **menghargai** kejujuran
  soal limitasi dibanding klaim berlebihan.

- [ ] **Siapkan demo live** — extension + server jalan saat sidang, dengan
  beberapa video YouTube yang sudah diketahui mengandung komentar spam.

---

## Tips Belajar & Cara Kerja untuk Junior

Karena kamu bilang masih banyak yang belum paham di sisi AI — ini wajar,
proyek ini menyentuh banyak konsep sekaligus (NLP, Unicode, ML klasik, sistem
terdistribusi sederhana). Beberapa saran cara kerja:

1. **Jangan coba pahami semuanya sekaligus.** Pakai dokumen
   [`PENJELASAN_TEKNIS.md`](PENJELASAN_TEKNIS.md) sebagai kamus rujukan —
   buka per bagian sesuai fase yang sedang kamu kerjakan, bukan dibaca habis
   sekaligus dari awal.

2. **Setiap eksperimen, catat hasilnya.** Buat file sederhana, misal
   `EXPERIMENTS.md`, isinya tabel: tanggal, perubahan apa (misal "tambah
   stemming"), hasil F1-score sebelum/sesudah. Ini sangat membantu saat
   menulis skripsi DAN membantu kamu melihat progres.

3. **Selalu jalankan ulang pipeline lengkap setelah perubahan apapun di
   `preprocessing.py`** — `prepare_dataset.py` → `train.py`. Lupakan ini =
   sumber bug paling membingungkan (model "tidak berubah" padahal kode sudah
   diubah).

4. **Manfaatkan `http://localhost:8000/docs`** (Swagger UI otomatis dari
   FastAPI) untuk testing API tanpa perlu extension — sangat membantu saat
   debugging model secara terpisah dari extension.

5. **Kalau bingung dengan suatu konsep (TF-IDF, SVM, NFKC, dll), tanya saja
   di sesi berikutnya** — minta penjelasan dengan analogi atau contoh konkret
   dari proyek ini sendiri. Lebih efektif belajar dari kode yang sudah jalan
   daripada dari teori abstrak duluan.

6. **Prioritaskan Fase 1 dan 2 dulu.** Fase 3–5 itu "nice to have" yang
   meningkatkan kualitas, tapi Fase 1–2 adalah yang paling sering ditanyakan
   penguji ("dari mana datanya?", "kok akurasinya 100%, yakin?").

---

## Pertanyaan untuk Diskusi Lanjut

Supaya sesi berikutnya lebih terarah, coba pikirkan dulu:

1. **Kapan target sidang/deadline skripsi kamu?** Ini menentukan seberapa
   jauh kita bisa masuk ke Fase 3–5.
2. **Apakah kamu (atau ada anggota tim lain) yang akan melakukan scraping
   dan review manual data non-spam asli?** Ini kerjaan yang butuh waktu
   manual, bukan murni coding.
3. **Apakah dosen pembimbing punya concern spesifik** (misal soal akurasi
   100%, soal data sintetis, soal arsitektur server lokal) yang sudah pernah
   disampaikan? Kalau ada, itu bisa langsung jadi prioritas utama.
4. **Mau mulai dari mana di sesi berikutnya** — Fase 0 (housekeeping/git),
   atau langsung loncat ke Fase 1/2 (dataset & evaluasi)?
