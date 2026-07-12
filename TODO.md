# Status & Roadmap — Judol Spam Detector

Checklist perkembangan proyek per fase. Item selesai ditandai `[x]`, yang
ditunda ke "Future Work" ditandai jelas kenapa.

---

## Daftar Isi

- [Fase 0 — Housekeeping](#fase-0--housekeeping)
- [Fase 1 — Kualitas Dataset](#fase-1--kualitas-dataset)
- [Fase 2 — Evaluasi Model](#fase-2--evaluasi-model)
- [Fase 3 — Preprocessing & Eksperimen Model](#fase-3--preprocessing--eksperimen-model)
- [Fase 4 — Robustness Extension](#fase-4--robustness-extension)
- [Future Work](#future-work)
- [Fase 5 — Penulisan Skripsi](#fase-5--penulisan-skripsi)

---

## Fase 0 — Housekeeping

- [x] Inisialisasi Git repository, `.gitignore` (env/, __pycache__, node_modules, .env)
- [x] `model/svm_model.joblib` dan `data/comments.csv` ikut masuk Git — supaya
  dosen bisa clone dan langsung jalankan tanpa re-generate dataset/model
- [x] `.env` scraper (`YOUTUBE_API_KEY`) dipastikan tidak ke-commit

---

## Fase 1 — Kualitas Dataset

- [x] Kumpulkan komentar non-spam asli dari YouTube (bukan template sintetis)
  lewat `scraper/index.js` mode `non_spam`, diagregasi via `scraper/filter.js`
  ke `scraper/final_non_spam.json`, direview manual.
- [x] Scrape lebih banyak video (gaming, berita, musik, podcast, edukasi)
  untuk variasi gaya spam.
- [x] Kumpulkan 141 hard examples manual dari dua video bertema judi online
  (`kM99uBssHvQ`, `pzE8S6N0vwo`) → `data/hard_test_set.csv`.
- [x] Log setiap perubahan dataset (tanggal, jumlah spam/non-spam, sumber) →
  [DATASET_LOG.md](DATASET_LOG.md).
- [x] Rebuild dataset (2026-06-30) setelah ditemukan drift kecil antara
  `comments.csv` ter-commit dan hasil rebuild murni — sekarang 2271 spam /
  2861 non-spam = 5132, model di-retrain (97.57% accuracy, F1-macro 0.9752).
- [x] Insiden kontaminasi data (2026-06-30): 61 komentar spam tersamar
  (Unicode dekoratif/leet speak — Mantulhoki/Hoki777/4rabet/Anru33) lolos
  heuristik scraper dan salah ter-label non-spam. Direlabel via
  `manual_overrides.csv`, model di-retrain. Detail:
  [PENJELASAN_TEKNIS.md §35](PENJELASAN_TEKNIS.md#35-insiden-kontaminasi-data--spam-tersamar-yang-lolos-heuristik-scraper),
  [DATASET_LOG.md Versi 11](DATASET_LOG.md#versi-11--2026-06-30).
- [x] Root cause diperbaiki di `scraper/index.js` (2026-07-03): ditambahkan
  `applyHomoglyphMap()` dan `normalizeLeetSpeak()` sebelum signal regex
  dicek, supaya kontaminasi serupa tidak terulang di scraping berikutnya.
- [x] Scraper "dead zone" diperbaiki (2026-07-03): komentar skor 10-29
  sekarang disimpan (`isBorderlineComment()`) ke
  `result/borderline_*.json` alih-alih dibuang tanpa jejak. Data
  borderline-nya sendiri belum direview → [Future Work](#future-work).

---

## Fase 2 — Evaluasi Model

→ Detail: [PENJELASAN_TEKNIS.md §16](PENJELASAN_TEKNIS.md#16-evaluasi-model-yang-lebih-jujur-fase-2), [DATASET_LOG.md](DATASET_LOG.md)

- [x] Hard test set terpisah — accuracy 75.71% murni SVM, 17 FP dari 70
  non_spam hard examples. Script: `src/evaluate_hard_set.py`.
- [x] 5-fold cross-validation di `src/train.py`, otomatis tiap run. Hasil
  (Versi 12): F1-macro 97.41% ± 0.30%. Visualisasi: `reports/cv_5fold_scores.png`.
- [x] GridSearchCV untuk C (`0.01`–`100`) di `src/train.py`. C=1 terpilih
  (F1-macro CV 0.9728). Visualisasi: `reports/gridsearch_c_sweep.png`.
- [x] Baseline comparison (`src/compare_baselines.py`): SVM 97.53%/0.9726,
  Naive Bayes 93.95%/0.9313, Logistic Regression 97.09%/0.9675.
- [x] Confusion matrix per model, tersimpan otomatis ke `reports/`.
- [x] Ablation study hybrid rules vs SVM murni (2026-06-30):
  `src/evaluate_hybrid_ablation.py` menunjukkan hybrid rules **menurunkan**
  accuracy 6–13 poin setelah dataset diperbesar — SVM murni menang di
  train-test split (97.57% vs 91.33%) dan hard test set (92.91% vs 80.14%).
  Rule B gagal total (0/27). Dinonaktifkan
  (`ENABLE_HYBRID_RULES = False` di `src/server.py`), kode dipertahankan
  sebagai bukti eksperimen. Detail:
  [PENJELASAN_TEKNIS.md §33](PENJELASAN_TEKNIS.md#33-ablation-study-hybrid-rules--kenapa-akhirnya-dimatikan).

---

## Fase 3 — Preprocessing & Eksperimen Model

> Aturan: setiap kali `src/preprocessing.py` diubah, jalankan ulang
> `prepare_dataset.py` lalu `train.py` — kalau tidak, terjadi
> *training-serving skew* ([PENJELASAN_TEKNIS.md §11](PENJELASAN_TEKNIS.md)).

- [x] Eksperimen stemming Sastrawi (`src/experiment_stemming.py`). Hasil
  akhir setelah 5-fold CV berpasangan + paired t-test (2026-07-03, dataset
  Versi 12): mean delta F1-macro **−0.0006**, p=0.3575 — stemming tidak
  membantu secara statistik. Keputusan awal (tanpa stemming) dipertahankan.
  Grafik: `reports/experiment_stemming_cv.png`. Detail:
  [PENJELASAN_TEKNIS.md §18](PENJELASAN_TEKNIS.md#18-eksperimen-stemming--apakah-stemming-membantu).
- [x] Inspeksi fitur (`src/inspect_features.py`) → `reports/top_features.png`,
  `reports/feature_weights.csv`. Detail:
  [PENJELASAN_TEKNIS.md §17](PENJELASAN_TEKNIS.md#17-inspeksi-fitur--apa-yang-dipelajari-model).
- [x] Eksperimen `max_features`/`ngram_range` (`src/experiment_features.py`):
  unigram-only sedikit lebih baik (+0.0034, tidak signifikan), trigram tidak
  membantu, konfigurasi baseline dipertahankan. Detail:
  [PENJELASAN_TEKNIS.md §19](PENJELASAN_TEKNIS.md#19-eksperimen-konfigurasi-tf-idf--ngram-dan-max_features).
- [ ] Stopwords domain-spesifik — dipindah ke [Future Work](#future-work).

---

## Fase 4 — Robustness Extension

- [x] Uji langsung di YouTube (video `pzE8S6N0vwo`). Ditemukan & diperbaiki:
  `slot`/`deposit` dihapus dari HARD_SPAM_SIGNALS (Versi 8, salah flag
  komentar korban/anti-judol), leet speak `H0KI777` diperbaiki via Step 5b-i.
- [x] Selector Instagram dibiarkan tidak diverifikasi — di luar scope judul
  ("...PADA YOUTUBE BERBASIS CHROME EXTENSION").
- [x] Threshold confidence bisa diatur dari popup (slider 50%–95%, tersimpan
  di `chrome.storage`, aktif langsung tanpa reload).
- [x] `scannedCount` diperbaiki — sekarang benar-benar diincrement per scan.
- [x] Server-down handling — `predictBatch()` memicu `checkServerHealth()`
  saat network error, supaya scan berikutnya tidak retry ke server mati.

---

## Future Work

Item yang sengaja ditunda, tidak menghalangi penulisan skripsi — semua
metrik/klaim di README, DATASET_LOG, dan PENJELASAN_TEKNIS sudah valid dan
reproducible tanpa item-item ini.

- [ ] Review manual `final_borderline.json` (belum pernah dijalankan sejak
  `isBorderlineComment()` ditambahkan 2026-07-03) — kandidat terbaik untuk
  menambah contoh "kritik + sebut brand", limitasi yang dibahas di
  [PENJELASAN_TEKNIS.md §34](PENJELASAN_TEKNIS.md#34-generalisasi-ke-brand-judol-baru--sejauh-mana-model-bisa-mengikuti).
- [ ] Stopwords domain-spesifik ("kak", "bang", "min", dll) — prioritas
  rendah, inspeksi fitur menunjukkan `bang`/`dok` justru sinyal non-spam kuat
  (bobot −1.55/−1.39), jadi kemungkinan performa turun kalau dihapus.
- [ ] Packaging server jadi executable (PyInstaller), auto-start launcher —
  di luar scope inti skripsi.
- [ ] Riset konversi model ke ONNX Runtime Web / TensorFlow.js agar prediksi
  jalan langsung di browser tanpa server Python.

---

## Fase 5 — Penulisan Skripsi

- [ ] Bab Metodologi — alur Fase 0–3 sebagai metodologi penelitian
- [ ] Bab Hasil & Pembahasan — hasil Fase 2, termasuk hard test set dan
  analisis error, bukan hanya angka test-set biasa
- [ ] Bab Implementasi — arsitektur extension + server
- [ ] Bab Keterbatasan & Saran — dependency server lokal, generalisasi ke
  brand baru ([PENJELASAN_TEKNIS.md §34](PENJELASAN_TEKNIS.md#34-generalisasi-ke-brand-judol-baru--sejauh-mana-model-bisa-mengikuti)),
  generalisasi pola "kritik + sebut brand"
  ([DATASET_LOG.md Versi 9](DATASET_LOG.md#versi-9--2026-06-30))
- [ ] Demo live untuk sidang
