# Model v11 — 2026-06-30

> ⚠️ **TERKONTAMINASI — diarsipkan untuk dokumentasi, jangan dipakai produksi.**
> Setelah versi ini dibuat, ditemukan 61 entri data non-spam yang sebenarnya
> spam tersamar (kampanye Mantulhoki/Hoki777/4rabet/Anru33 yang lolos
> heuristik scraper). Akurasi 98.23% di bawah ini **terinflasi** karena
> model sebagian menghafal label yang salah. Lihat
> [`v12/`](../v12/) untuk versi yang sudah diperbaiki, dan
> [Riwayat dataset, Versi 11](../../../docs/riwayat-dataset.md#versi-11--2026-06-30)
> untuk investigasi lengkapnya. Diarsipkan tetap di sini sebagai bukti nyata
> kenapa audit data manual penting — bukan cuma percaya heuristik otomatis.

Commit: *(belum di-commit)*
Dataset: 2271 spam / 4238 non_spam / 6509 total
Accuracy: **98.23%** (F1 0.9804, train-test split) — **hard test set: 97.78%** (3 FP/135, naik dari 97.04%/4 FP di v10)

## Apa yang berubah di versi ini

Scraping tertarget 12 video baru (tema edukasi/pengalaman pribadi soal judi
online) untuk mengisi kesenjangan: audit dataset menemukan cuma 8% data
non-spam yang benar-benar menyinggung topik judi. Setelah scraping, naik
ke 11.3% (471 dari 4156 entri non-spam, dari 14 video relevan vs 2
sebelumnya).

Hasil paling penting: salah satu dari 2 contoh yang sengaja ditahan sebagai
uji generalisasi di v10 ("100% situs NAGAPOKER...") sekarang terklasifikasi
benar **tanpa pernah dilatih dengan kalimat itu** — bukti generalisasi
nyata dari keberagaman data, bukan hafalan.

Penjelasan lengkap (metodologi scraping, evaluasi sebelum/sesudah, daftar
video ID) ada di
[Riwayat dataset](../../../docs/riwayat-dataset.md#versi-10--2026-06-30).

## Metadata model (diekstrak dari file ini)

| Atribut | Nilai |
|---|---|
| Jumlah fitur TF-IDF | 7894 |
| SVM C | 1 |
| Support vectors (non_spam, spam) | [1288, 654] |
| Ukuran file | 638.6 KB |

## Cara load

```python
import joblib
model = joblib.load("model/versions/v11/svm_model.joblib")
```

Lihat [../INDEX.md](../INDEX.md) untuk tabel perbandingan semua versi.
