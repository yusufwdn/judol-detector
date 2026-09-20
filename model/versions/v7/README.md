# Model v7 — 2026-06-19

Commit: `6928ef5`
Dataset: 2266 spam / 2533 non_spam / 4799 total
Accuracy: 98.23% (F1 0.9822)

## Apa yang berubah di versi ini

20 entri direlabel (false positive spam->non_spam), manual_overrides.csv dibuat untuk persistensi koreksi lintas rebuild.

Penjelasan lengkap (kenapa, contoh kasus, dampak terukur) ada di
[Riwayat dataset](../../../docs/riwayat-dataset.md#versi-7--2026-06-19).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 5480 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [866, 680] |
| Ukuran file | 458.9 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v7/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
