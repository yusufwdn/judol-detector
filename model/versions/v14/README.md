# Model v14 — 2026-07-04

Commit: `5b93f73`
Dataset: 2332 spam / 4358 non_spam / 6690 total (identik dengan v13 — tidak ada perubahan data)
Accuracy: **97.53%** (train-test split, `compare_baselines.py`)

## Apa yang berubah di versi ini

Tidak ada perubahan dataset atau parameter dari v13. Versi ini murni hasil
`train.py` dijalankan ulang saat menambahkan metodologi evaluasi 5-fold
cross-validation dan analisis statistik dampak stemming (lihat
`src/experiment_stemming.py`, commit `5b93f73`). Konfigurasi TF-IDF, C, dan
dataset persis sama dengan v13, tapi retrain menghasilkan file `.joblib`
dengan hash biner berbeda dari v13 — kemungkinan karena non-determinisme
kecil di estimasi probabilitas SVM (`probability=True` memakai internal
5-fold CV Platt scaling) atau urutan floating-point saat fit ulang.

Diarsipkan supaya jejak audit tetap konsisten — sebelumnya model produksi
sempat di-retrain tanpa checkpoint terpisah (lihat catatan "lubang versi 4 & 5"
di [../INDEX.md](../INDEX.md)), jadi retrain kali ini langsung disalin ke sini
sebelum lanjut eksperimen berikutnya.

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 8342 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [1311, 691] |
| Ukuran file | 668.1 KB |

## Perbandingan baseline (`compare_baselines.py`, 2026-07-04)

| Model | Accuracy | F1-macro |
|---|---|---|
| SVM (model ini) | 97.53% | 0.9726 |
| Naive Bayes (MultinomialNB) | 93.95% | 0.9313 |
| Logistic Regression | 97.09% | 0.9675 |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v14/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
