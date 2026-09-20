# Model v3 — 2026-06-18

Commit: `e5de4f3`
Dataset: 1099 spam / 2513 non_spam / 3612 total
Accuracy: 97.23% (F1 0.9671) — lihat tabel Versi 4 di DATASET_LOG

## Apa yang berubah di versi ini

+3 hard negative examples (kata berbobot spam dalam konteks normal kalimat).

Penjelasan lengkap (kenapa, contoh kasus, dampak terukur) ada di
[Riwayat dataset](../../../docs/riwayat-dataset.md#versi-3--2026-06-18).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 4094 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [881, 459] |
| Ukuran file | 340.5 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v3/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
