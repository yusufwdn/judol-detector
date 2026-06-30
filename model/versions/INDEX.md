# Model Versioning — Histori Lengkap

Folder ini menyimpan **snapshot biner `svm_model.joblib`** dari setiap titik penting dalam pengembangan proyek, diekstrak langsung dari riwayat Git (`git log --follow -- model/svm_model.joblib`). Tujuannya: bisa membuktikan progres model secara konkret (bukan cuma angka di tabel) — file-file ini bisa langsung di-`joblib.load()` dan dibandingkan kapan saja, termasuk saat sidang kalau ditanya "coba tunjukkan model versi awal vs sekarang".

Penjelasan naratif tiap perubahan (kenapa, apa yang diubah, dampaknya) ada di **[`../../DATASET_LOG.md`](../../DATASET_LOG.md)** — dokumen ini fokus ke pemetaan versi ↔ commit ↔ file biner saja.

> **Model produksi yang dipakai sekarang ada di `model/svm_model.joblib`** (root, bukan di folder `versions/`). Folder ini murni arsip historis.

---

## Tabel Versi

| Versi | Folder | Commit | Tanggal | Dataset (spam/non_spam/total) | Fitur TF-IDF | Accuracy (test split) | Catatan |
|---|---|---|---|---|---|---|---|
| 1 | [`v1/`](v1/) | `20faef6` | 2026-06-16 | 1099 / 700 / 1799 | 2433 | ~100%* | Non-spam **sintetis** (template). Akurasi tidak realistis — lihat catatan di bawah. |
| 2 | [`v2/`](v2/) | `f514c13` | 2026-06-17 | 1099 / 2509 / 3608 | 4056 | 97.23% | Non-spam diganti ke data nyata. K-fold CV + GridSearchCV + baseline comparison mulai diimplementasikan di `train.py`. |
| 3 | [`v3/`](v3/) | `e5de4f3` | 2026-06-18 | 1099 / 2513 / 3612 | 4094 | 97.23%** | +3 hard negative examples (kata berbobot spam dalam konteks normal). |
| **4** | *(tidak ada)* | — | 2026-06-18 | 1785 / 2513 / 4298 | — | 96.74% | **Tidak ada checkpoint Git terpisah** — preprocessing Step 2b ditambahkan & rescue filter diperbaiki, tapi model tidak sempat di-commit sebelum lanjut ke Versi 5 di hari yang sama. Angka dari `DATASET_LOG.md`. |
| **5** | *(tidak ada)* | — | 2026-06-18 | 1785 / 2513 / 4298 | — | 99.53% | **Tidak ada checkpoint Git terpisah** — Step 5b brand canonicalization & Step 2c ditambahkan, dataset sama dengan V4. Angka dari `DATASET_LOG.md`. |
| 6 | [`v6/`](v6/) | `453a85f` | 2026-06-18 | 2285 / 2513 / 4798 | 5476 | 98.44% | 500 spam manual diimport, hybrid rule jadi dua arah, rescue pattern diperbaiki. |
| 7 | [`v7/`](v7/) | `6928ef5` | 2026-06-19 | 2266 / 2533 / 4799 | 5480 | 98.23% | 20 FP direlabel, `manual_overrides.csv` dibuat. |
| 8a | [`v8a/`](v8a/) | `2636549` | 2026-06-19 | 2274 / 2799 / 5073 | 6010 | — | Commit pertama bertanda "Versi 8" (leet speak normalization, hard test set 141 entri). Jumlah non_spam belum final. |
| 8b | [`v8b/`](v8b/) | `c46c2d4` | 2026-06-19 | 2268 / 2864 / 5132 | 6360 | 96.95% | Commit terakhir sebelum sesi audit ini — total baris sudah 5132 sesuai `DATASET_LOG.md`, tapi split spam/non_spam sedikit beda dari tabel V8 (2274/2858) karena ada entri masuk lewat endpoint `/report` tanpa full rebuild. |
| 9 | [`v9/`](v9/) | `d932f41`/`349c813` | 2026-06-30 | 2271 / 2861 / 5132 | 6375 | 97.57% | Dataset di-rebuild bersih dari `prepare_dataset.py` (menghilangkan ketidaksinkronan v8b). Hybrid rules (`ENABLE_HYBRID_RULES`) dimatikan setelah ablation study membuktikan menurunkan akurasi — lihat [`PENJELASAN_TEKNIS.md §33`](../../PENJELASAN_TEKNIS.md#33-ablation-study-hybrid-rules--kenapa-akhirnya-dimatikan). **Disusul v10 di hari yang sama** setelah error analysis lanjutan. |
| 10 | [`v10/`](v10/) | `9490089` | 2026-06-30 | 2271 / 2861 / 5132*** | 6378 | 97.57% (hard test set: 97.04%, naik dari 92.91% di v9) | Error analysis sistematis pada hard test set: 3 contoh "kata laporan tenggelam oleh brand" dipindah dari eval ke training, 3 fragmen terlalu pendek dibuang dari eval. Detail di [`DATASET_LOG.md` Versi 9](../../DATASET_LOG.md#versi-9--2026-06-30). |
| 11 ⚠️ | [`v11/`](v11/) | *(belum di-commit)* | 2026-06-30 | 2271 / 4238 / 6509 | 7894 | ~~98.23%~~ **(terkontaminasi)** | **TERKONTAMINASI — jangan dipakai.** Scraping 12 video baru menutup gap "non-spam yang menyinggung judi" (8.0%→11.3%), tapi 61 dari komentar yang ter-scrape ternyata spam tersamar (lolos heuristik scraper) yang baru ketahuan setelah versi ini selesai dilatih. Akurasi di atas terinflasi. Lihat [`v12/`](v12/) untuk perbaikannya. |
| **12** | [`v12/`](v12/) | *(belum di-commit)* | 2026-06-30 | 2332 / 4177 / 6509 | 8006 | **97.39%** (hard test set: **97.04%**) | **Model produksi saat ini.** 61 entri kontaminasi (3 kampanye spam tersamar: Mantulhoki, Hoki777, 4rabet/Anru33 — termasuk 8 yang sudah ada sejak sebelum sesi ini) direlabel dari non_spam ke spam, bukan sekadar dihapus. Akurasi turun dari v11 secara sengaja — v11 sebagian menghafal label salah. Sanity check: brand yang dibersihkan sekarang terdeteksi spam 99.6–100%. Detail di [`DATASET_LOG.md` Versi 11](../../DATASET_LOG.md#versi-11--2026-06-30). |

\* Versi 1 dianggap tidak realistis karena non-spam sintetis terlalu seragam — lihat [`DATASET_LOG.md` Versi 1](../../DATASET_LOG.md#versi-1--sebelum-2026-06-16) dan [README.md FAQ](../../README.md#11-faq--pertanyaan-yang-mungkin-muncul).
\** Angka Versi 3 diambil dari tabel perbandingan di `DATASET_LOG.md` Versi 4 (kolom "Versi 3") — dataset Versi 3 tidak punya tabel evaluasi independen di bagiannya sendiri.
\*** Total baris sama dengan v9, tapi komposisi beda — 3 baris diganti (lihat `DATASET_LOG.md` Versi 9).

---

## Kenapa Ada Lubang di Versi 4 & 5?

Proyek ini dikembangkan dengan retrain manual yang sering (`python src/prepare_dataset.py && python src/train.py`), tapi tidak setiap retrain langsung di-`git commit`. Versi 4 dan 5 dikerjakan di hari yang sama dengan Versi 3 dan 6 (2026-06-18) — perubahannya tercatat lengkap secara naratif di `DATASET_LOG.md` (termasuk metrik evaluasi), tapi file `.joblib` hasil retrain-nya tertimpa oleh retrain berikutnya sebelum sempat di-commit ke Git.

**Pelajaran untuk metodologi skripsi:** ini alasan kenapa folder `versions/` ini dibuat — supaya kejadian serupa tidak terulang untuk model versi selanjutnya. Mulai dari Versi 9, setiap retrain yang dianggap final sebaiknya langsung disalin ke `model/versions/vN/` SEBELUM lanjut eksperimen berikutnya.

## Kenapa Ada 8a dan 8b untuk Versi 8?

`DATASET_LOG.md` mendokumentasikan Versi 8 sebagai satu kesatuan (2274 spam / 2858 non_spam), tapi di Git ada dua commit terpisah yang membungkus proses itu: `2636549` (commit eksplisit "Versi 8", non_spam masih 2799) dan `c46c2d4` (commit berikutnya, "expand dataset... fix report persistence", non_spam naik ke 2864). Selisih ini kemungkinan dari entri yang masuk lewat endpoint `/report` (dev mode) antara dua commit tersebut. Keduanya diarsipkan terpisah (`v8a`, `v8b`) supaya histori tetap akurat — daripada dipaksa jadi satu versi yang menyamarkan perbedaan nyata di datanya.

## Cara Memuat Model Versi Lama

```python
import joblib

model_v6 = joblib.load("model/versions/v6/svm_model.joblib")
prediction = model_v6.predict(["contoh teks yang sudah di-clean_text()"])
```

**Penting:** model lama dilatih dengan preprocessing pipeline pada masanya. Kalau mau membandingkan prediksi model lama vs baru pada teks yang sama, gunakan `clean_text()` versi **saat model itu dilatih** (bisa di-checkout dari Git di commit yang sama), bukan `clean_text()` versi sekarang — kalau tidak, perbandingannya tidak adil karena training-serving consistency model lama jadi rusak.

## Untuk Sidang

> *"Untuk menjaga jejak audit perkembangan model, setiap checkpoint signifikan diarsipkan sebagai file biner terpisah di `model/versions/`, bukan hanya dicatat sebagai angka di tabel. Ini memungkinkan perbandingan langsung antar versi — termasuk memuat ulang model versi pertama (akurasi ~100% tapi dari data sintetis) dan membandingkannya dengan model versi terbaru (97.57% dari data nyata yang jauh lebih beragam) untuk menunjukkan secara konkret bagaimana akurasi yang lebih 'jujur' justru mencerminkan dataset yang lebih representatif, bukan model yang memburuk."*
