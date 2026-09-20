# Model v9 — 2026-06-30

> **Disusul oleh [`v10/`](../v10/) di hari yang sama** — error analysis lanjutan
> pada hard test set menghasilkan model dengan komposisi training sedikit
> berbeda. v9 tetap diarsipkan sebagai checkpoint "hybrid rules baru
> dimatikan, sebelum error analysis hard test set".

Commit: `(belum di-commit)`
Dataset: 2271 spam / 2861 non_spam / 5132 total
Accuracy: 97.57% (F1 0.9752) -- SVM murni, hybrid rules off

## Apa yang berubah di versi ini

Dataset di-rebuild bersih dari prepare_dataset.py (resolve ketidaksinkronan v8b). Hybrid rules (server.py) DIMATIKAN setelah ablation study membuktikan menurunkan akurasi 6-13 poin. Model produksi saat ini.

Penjelasan lengkap (kenapa, contoh kasus, dampak terukur) ada di
[Riwayat dataset](../../../docs/riwayat-dataset.md#versi-8--2026-06-19).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 6375 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [1037, 697] |
| Ukuran file | 537.1 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v9/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
