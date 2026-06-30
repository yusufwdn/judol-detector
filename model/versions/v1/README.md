# Model v1 — 2026-06-16

Commit: `20faef6`
Dataset: 1099 spam / 700 non_spam / 1799 total
Accuracy: ~100% (tidak realistis, lihat README FAQ)

## Apa yang berubah di versi ini

Dataset awal. Non-spam SINTETIS (template), bukan data nyata.

Penjelasan lengkap (kenapa, contoh kasus, dampak terukur) ada di
[DATASET_LOG.md](../../../DATASET_LOG.md#versi-1--sebelum-2026-06-16).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 2433 |
| SVM C | 1.0 |
| Support vectors (non_spam, spam) | [144, 340] |
| Ukuran file | 165.7 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v1/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
