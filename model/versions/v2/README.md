# Model v2 — 2026-06-17

Commit: `f514c13`
Dataset: 1099 spam / 2509 non_spam / 3608 total
Accuracy: 97.23% (F1 0.9671)

## Apa yang berubah di versi ini

Non-spam diganti ke data scraping nyata (2509 komentar). K-fold CV + GridSearchCV + baseline comparison mulai ada di train.py.

Penjelasan lengkap (kenapa, contoh kasus, dampak terukur) ada di
[Riwayat dataset](../../../docs/riwayat-dataset.md#versi-2--2026-06-16).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 4056 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [889, 460] |
| Ukuran file | 338.6 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v2/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
