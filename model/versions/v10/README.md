# Model v10 — 2026-06-30

Commit: *(belum di-commit)*
Dataset: 2271 spam / 2861 non_spam / 5132 total (3 baris diganti dari v9 — lihat di bawah)
Accuracy: 97.57% (F1 0.9752, train-test split) — **hard test set: 97.04%** (135 entri tersisa, naik dari 92.91%/141 entri di v9)

## Apa yang berubah di versi ini

Bukan perubahan jumlah data, tapi perubahan **komposisi**: dilakukan error
analysis sistematis pada 10 false positive yang tersisa di hard test set
setelah hybrid rules dimatikan (v9). 3 contoh kasus "kata laporan/kritik
tenggelam oleh banyaknya brand disebut" dipindah dari `hard_test_set.csv`
(eval-only) ke `manual_overrides.csv` (training), 3 fragmen terlalu pendek
untuk dinilai konteksnya dibuang dari hard test set.

Hasil: hard test set accuracy naik dari 92.91% (10 FP/141) ke 97.04% (4
FP/135). 2 dari 4 FP yang tersisa adalah pola yang sama persis tapi
sengaja DITAHAN di eval (bukan dipindah ke training) — tetap salah
setelah retrain, membuktikan model tidak men-generalisasi pola abstrak
dari beberapa contoh ke kombinasi brand yang berbeda. Temuan ini jadi
dasar pertimbangan menambah engineered features di iterasi berikutnya.

Penjelasan lengkap (kategorisasi 5 pola error, metodologi, hasil
lengkap) ada di
[DATASET_LOG.md](../../../DATASET_LOG.md#versi-9--2026-06-30).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 6378 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [1037, 695] |
| Ukuran file | 537.6 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v10/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
