# Model v6 — 2026-06-18

Commit: `453a85f`
Dataset: 2285 spam / 2513 non_spam / 4798 total
Accuracy: 98.44% (F1 0.9843)

## Apa yang berubah di versi ini

500 spam manual diimport, hybrid rule jadi dua arah (A+B), rescue pattern brand diperbaiki (case-insensitive, minimum 3 huruf).

Penjelasan lengkap (kenapa, contoh kasus, dampak terukur) ada di
[Riwayat dataset](../../../docs/riwayat-dataset.md#versi-6--2026-06-18).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 5476 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [899, 676] |
| Ukuran file | 464.7 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v6/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
