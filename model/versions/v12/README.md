# Model v12 — 2026-06-30

Commit: *(belum di-commit)*
Dataset: 2332 spam / 4177 non_spam / 6509 total
Accuracy: **97.39%** (F1 0.9713, train-test split) — hard test set: **97.04%**

## Apa yang berubah di versi ini

**Perbaikan kualitas data, bukan penambahan.** User menemukan komentar
spam yang salah label `non_spam` di hasil scraping v11. Investigasi
menemukan 3 kampanye spam tersamar (Unicode dekoratif, leet speak,
full-width spacing) yang lolos heuristik scraper — total 61 entri,
termasuk 8 yang sudah ada di pool non-spam sejak sebelum sesi ini.

Semua 61 entri direlabel jadi `spam` (bukan sekadar dihapus) dan dataset
di-retrain. Accuracy turun dari v11 (98.23% → 97.39%) **secara sengaja** —
v11 sebagian "curang" karena belajar label yang salah. Sanity check
mengkonfirmasi: brand yang dibersihkan (Mantulhoki, Hoki777, 4rabet)
sekarang terdeteksi spam dengan confidence 99.6–100%.

Penjelasan lengkap (daftar kampanye, root cause kenapa scraper tidak
mendeteksi, before/after) ada di
[DATASET_LOG.md](../../../DATASET_LOG.md#versi-11--2026-06-30).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 8006 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [1276, 694] |
| Ukuran file | 641.0 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v12/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
