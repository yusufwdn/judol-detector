# Dataset Log — Judol Spam Detector

Setiap kali dataset diperbarui, catat di sini: tanggal, jumlah data, dan sumber.
Berguna untuk bab metodologi skripsi dan untuk melacak versi mana yang menghasilkan hasil evaluasi tertentu.

---

## Versi 2 — 2026-06-16

### Perubahan dari versi sebelumnya
- Data non-spam **diganti dari sintetis ke nyata** (2509 komentar asli dari YouTube)
- Akurasi turun dari ~100% ke 97.23% — ini **lebih jujur dan lebih baik untuk skripsi**

### Statistik dataset (`data/comments.csv`)

| Label    | Jumlah |
|----------|--------|
| spam     | 1099   |
| non_spam | 2509   |
| **Total**| **3608** |

### Sumber data spam (`scraper/final_spam.json`)

- Raw entries dari scraper : 2318
- Lolos threshold >= 80    : 137
- Diselamatkan brand regex : 962
- Dibuang (false positive) : 1219
- **Total spam dipakai**   : **1099**
- Dikumpulkan dari         : **75 video** YouTube

### Sumber data non-spam (`scraper/final_non_spam.json`)

- **Total non-spam dipakai**: **2509**
- Dikumpulkan dari          : **17 video** YouTube (komentar nyata, bukan sintetis)

### Hasil evaluasi model

**K-Fold Cross-Validation (cv=5, full dataset):**
- Fold scores (F1-macro): 0.9572, 0.9621, 0.9738, 0.9705, 0.9669
- **Mean F1-macro: 96.61% ± 0.59%**

**GridSearchCV (hyperparameter tuning):**
- C kandidat: [0.01, 0.1, 1, 10, 100]
- C terpilih: **1** (F1-macro CV = 0.9543)

**Train-test split (80/20, test set = 722 sampel):**

| Metrik | Nilai |
|--------|-------|
| Accuracy | 97.23% |
| F1-macro | 0.9671 |
| Spam Precision | 0.97 |
| Spam Recall | 0.94 |
| Spam F1 | 0.95 |
| Non-spam F1 | 0.98 |

Confusion matrix:
```
                  Prediksi non_spam  Prediksi spam
Aktual non_spam        495 (TN)          7 (FP)
Aktual spam             13 (FN)        207 (TP)
```

→ Lihat gambar: `reports/confusion_matrix_svm.png`

**Perbandingan dengan baseline (data training dan test sama):**

| Model | Accuracy | F1-macro |
|-------|----------|----------|
| SVM (C=1, linear) | **97.23%** | **0.9671** |
| Logistic Regression | 95.15% | 0.9423 |
| Naive Bayes (MultinomialNB) | 94.32% | 0.9305 |

---

## Versi 1 — (sebelum 2026-06-16)

### Statistik dataset

| Label    | Jumlah |
|----------|--------|
| spam     | 1099   |
| non_spam | 700    |
| **Total**| **1799** |

### Catatan
- Data non-spam berasal dari template sintetis (`NON_SPAM_TEMPLATES` di `prepare_dataset.py`)
- Akurasi test set ~100% — kemungkinan terlalu optimis karena non-spam sintetis terlalu seragam
