# Model v13 — 2026-06-30

Commit: *(belum di-commit)*
Dataset: 2332 spam / 4358 non_spam / 6690 total
Accuracy: **97.46%** (train-test split) — **hard test set: 98.52%** (rekor tertinggi, 2 FP/135)

## Apa yang berubah di versi ini

Lanjutan investigasi kasus FN "PBB4D" (lihat v12). Ditemukan bahwa scraper
punya dua batasan yang membuat scraping ulang video yang sama terasa
percuma: `order=relevance` default (hasil konsisten sama tiap scrape) dan
early-stop begitu `TARGET_COUNT` tercapai (cuma ~100-200 komentar tersentuh
dari video yang bisa punya ribuan). Ditambahkan env var `COMMENT_ORDER`,
scrape ulang `1eNUtmfTckk` + `wxhbjPxrDR0` dengan `order=time` +
`TARGET_COUNT=400` + threshold dilebarkan sementara — menyisir 561 komentar
(vs ~215 sebelumnya), salah satunya tuntas sampai habis.

Tidak menemukan kandidat PBB4D-style baru (pola itu memang langka), tapi
menemukan 181 komentar non-spam bertema judi lain yang sebelumnya terbuang
karena kepadatan keyword saja (bukan promosi). Direview manual (8 dibuang
karena kependekan, 1 dibuang karena pakai Unicode dekoratif mencurigakan),
181 sisanya ditambahkan ke training.

**Temuan penting:** PBB4D kali ini benar-benar masuk training set (bukan
test set seperti di v12), tapi model TETAP memprediksi spam (99.18%
confidence). Bukti empiris kuat bahwa ini keterbatasan struktural SVM
linear teregularisasi terhadap token brand yang diulang 3x dalam satu
komentar — bukan soal kurang data.

Penjelasan lengkap ada di
[DATASET_LOG.md](../../../DATASET_LOG.md#versi-12--2026-06-30).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 8342 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [1311, 691] |
| Ukuran file | 668.1 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v13/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
