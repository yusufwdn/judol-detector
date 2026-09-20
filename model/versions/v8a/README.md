# Model v8a — 2026-06-19

Commit: `2636549`
Dataset: 2274 spam / 2799 non_spam / 5073 total
Accuracy: (tidak dicatat terpisah — lihat v8b)

## Apa yang berubah di versi ini

Commit eksplisit "Versi 8": leet speak normalization ditambahkan, hard test set diperluas ke 141 entri. Non-spam belum final di commit ini.

Penjelasan lengkap (kenapa, contoh kasus, dampak terukur) ada di
[Riwayat dataset](../../../docs/riwayat-dataset.md#versi-8--2026-06-19).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 6010 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [992, 685] |
| Ukuran file | 508.9 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v8a/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
