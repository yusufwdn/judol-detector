# Model v8b — 2026-06-19

Commit: `c46c2d4`
Dataset: 2268 spam / 2864 non_spam / 5132 total
Accuracy: 96.95%

## Apa yang berubah di versi ini

Commit lanjutan Versi 8: dataset diperluas lagi, fix persistensi endpoint /report ke dua file. Total baris sudah 5132 sesuai DATASET_LOG, tapi split spam/non_spam sedikit beda dari tabel resmi (kemungkinan entri /report di luar rebuild).

Penjelasan lengkap (kenapa, contoh kasus, dampak terukur) ada di
[Riwayat dataset](../../../docs/riwayat-dataset.md#versi-8--2026-06-19).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 6360 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [1042, 716] |
| Ukuran file | 540.8 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v8b/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
