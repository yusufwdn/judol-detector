# Model dan Pelatihan

Pelatihan dijalankan oleh [`src/train.py`](../src/train.py). Keluarannya satu
berkas, `model/svm_model.joblib`, yang berisi seluruh pipeline dalam keadaan
sudah terlatih.

```bash
python src/train.py
```

## Pipeline

```
teks mentah
    |
    v  clean_text()          lihat preprocessing.md
    |
    v  TfidfVectorizer       teks menjadi vektor numerik
    |
    v  SVC(kernel="linear")  vektor menjadi keputusan
    |
    v  spam / non_spam
```

Yang disimpan ke berkas bukan hanya SVM-nya, melainkan seluruh pipeline
termasuk TF-IDF yang sudah dilatih. Ini penting: TF-IDF menyimpan kamus kata
beserta bobot inverse document frequency-nya. Kalau yang disimpan hanya
SVM-nya, saat prediksi tidak ada kamus yang sama dan nomor fitur tidak lagi
merujuk kata yang sama.

joblib dipakai alih-alih `pickle` bawaan Python karena lebih efisien untuk
objek berisi array numerik besar, dan merupakan cara yang dianjurkan
scikit-learn.

## TF-IDF

```python
TFIDF_PARAMS = {
    "max_features": 10000,
    "ngram_range": (1, 2),
}
```

Pada dataset saat ini, konfigurasi tersebut menghasilkan 8.342 fitur.

TF-IDF memberi bobot tinggi pada kata yang sering muncul di satu dokumen
tetapi jarang di dokumen lain. Kata pasaran seperti `yang` dan `di` otomatis
mendapat bobot mendekati nol tanpa perlu aturan khusus, sedangkan kata penciri
seperti `daftar` atau token `judolbrand` mendapat bobot tinggi.

Pendekatan berbasis word embedding dipertimbangkan tetapi tidak dipakai. Spam
judi online dikenali dari kata penciri yang spesifik, bukan dari kemiripan
makna antar kata, sehingga keunggulan utama embedding tidak terpakai di kasus
ini. Embedding juga membutuhkan data latih jauh lebih besar, dan yang paling
menentukan, hasilnya sulit ditelusuri. Dengan TF-IDF, bobot tiap kata bisa
dibuka dan diperiksa:

```bash
python src/inspect_features.py
```

Skrip tersebut menghasilkan `reports/top_features.png` dan
`reports/feature_weights.csv`.

## SVM

```python
SVC(
    C=best_C,
    kernel="linear",
    class_weight="balanced",
    probability=True,
    random_state=42,
)
```

### Kernel linear

Data teks berdimensi sangat tinggi. Dengan ribuan fitur, ruangnya cukup
longgar sehingga kedua kelas umumnya sudah bisa dipisahkan oleh sebuah
hyperplane lurus. Kernel non-linear seperti RBF menambah beban komputasi yang
besar untuk keuntungan yang tipis pada kasus teks, sementara sistem ini punya
batasan waktu respons karena prediksi terjadi saat pengguna menggulir halaman.

### class_weight balanced

Dataset timpang, 2.332 spam berbanding 4.358 non-spam. Ketimpangan ini
mencerminkan keadaan sebenarnya di kolom komentar dan sengaja tidak diratakan
dengan membuang data. Sebagai gantinya, `class_weight="balanced"` membuat
kesalahan pada kelas minoritas dihitung lebih berat, dan F1-macro dipakai
sebagai metrik utama karena memperlakukan kedua kelas setara.

### probability=True

Dibutuhkan agar model bisa mengeluarkan nilai kepercayaan, bukan hanya label.
Ekstensi memakai nilai itu untuk menerapkan ambang batas yang bisa diatur
pengguna. Lihat [extension.md](extension.md).

## Pemilihan nilai C

Nilai C tidak ditetapkan sebagai bawaan, melainkan dicari secara empiris
dengan `GridSearchCV`:

```python
param_grid = {"svm__C": [0.01, 0.1, 1, 10, 100]}
```

Pencarian memakai 5-fold cross-validation pada data latih dengan F1-macro
sebagai skor. Hasilnya `C = 1`, dengan F1-macro cross-validation 0,9728.
Kurva pencariannya tersimpan di `reports/gridsearch_c_sweep.png`.

C mengatur seberapa keras model menghukum kesalahan pada data latih. Nilai
kecil menghasilkan margin lebih lebar dan model yang lebih toleran, nilai
besar memaksa model mengikuti data latih lebih rapat dengan risiko overfitting.

## Pembagian data

```python
train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
```

Dari 6.690 baris, 5.352 dipakai untuk melatih dan 1.338 untuk menguji.
`random_state` dikunci supaya pembagiannya bisa diulang persis, dan `stratify`
menjaga proporsi spam terhadap non-spam tetap sama di kedua bagian.

## Kenapa SVM

| Pembanding | Akurasi | Catatan |
|---|---|---|
| SVM | 97,53% | Dipakai |
| Logistic Regression | 97,09% | Alternatif yang sangat kompetitif |
| Naive Bayes | 93,95% | Asumsi kebebasan antar fitur tidak terpenuhi |

Naive Bayes mengasumsikan setiap fitur saling bebas, sehingga kemunculan kata
`slot` dianggap tidak berhubungan dengan kemunculan `gacor`. Pada spam judi
online asumsi itu justru salah, karena kata-kata tersebut muncul bersamaan
sebagai satu pola.

Selisih terhadap Logistic Regression hanya 0,44 poin dan layak disebut apa
adanya. SVM tetap dipilih karena unggul konsisten di seluruh metrik dan karena
prinsip margin maksimum memberi dasar teoretis untuk ketahanan pada data baru.

Pendekatan deep learning tidak dipakai karena tiga alasan: sistem membutuhkan
respons cepat saat pengguna menggulir, ukuran data 6.690 sampel relatif kecil
untuk model besar, dan pengukuran di proyek ini sendiri menunjukkan bahwa
menambah kompleksitas di atas SVM justru menurunkan performa. Lihat
[eksperimen.md](eksperimen.md).

## Arsip versi model

Setiap checkpoint penting disimpan di `model/versions/` beserta catatan
perubahannya di [`model/versions/INDEX.md`](../model/versions/INDEX.md).
Model produksi tetap berada di `model/svm_model.joblib`.

Saat membandingkan model lama dengan model baru, teks harus dinormalisasi
dengan `clean_text()` versi ketika model itu dilatih, bukan versi terkini.
Kalau tidak, perbandingannya tidak adil karena konsistensi pelatihan dan
prediksi model lama menjadi rusak.
