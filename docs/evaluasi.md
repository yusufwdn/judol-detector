# Evaluasi

Seluruh angka di halaman ini dihasilkan oleh skrip di `src/` dan tersimpan di
`reports/`. Setiap bagian menyebutkan skrip mana yang menghasilkannya, supaya
bisa diverifikasi ulang.

## Ringkasan

| Pengujian | Hasil | Dihasilkan oleh |
|---|---|---|
| Akurasi pada data uji | 97,53% | `src/train.py` |
| F1-macro | 0,9726 | `src/train.py` |
| Cross-validation 5-fold | 0,9741 ± 0,0030 | `src/train.py` |
| Akurasi pada kasus ambigu | 98,52% | `src/evaluate_hard_set.py` |
| Logistic Regression | 97,09% | `src/compare_baselines.py` |
| Naive Bayes | 93,95% | `src/compare_baselines.py` |

## Pengujian pada data uji

Dari 6.690 baris, 1.338 disisihkan sebagai data uji dan tidak pernah dilihat
model selama pelatihan.

Confusion matrix:

|  | Diprediksi non-spam | Diprediksi spam |
|---|---|---|
| **Sebenarnya non-spam** | 863 | 9 |
| **Sebenarnya spam** | 24 | 442 |

Akurasi dihitung dari (863 + 442) / 1.338 = 97,53%.

Sembilan false positive berarti sembilan komentar normal ikut disembunyikan,
dan 24 false negative berarti 24 spam lolos. Untuk kasus penggunaan ini,
false positive lebih merugikan karena menyembunyikan komentar yang sah dari
pengguna. Ambang kepercayaan yang bisa diatur di ekstensi ada untuk memberi
pengguna kendali atas keseimbangan tersebut.

Visualisasinya ada di `reports/confusion_matrix_svm.png`.

## Cross-validation

Akurasi dari satu kali pembagian data bisa kebetulan menguntungkan. Untuk
memeriksanya, 5-fold cross-validation dijalankan pada seluruh data setiap kali
`train.py` dipanggil.

Hasilnya F1-macro **0,9741 ± 0,0030**. Simpangan baku yang kecil menunjukkan
performa model tidak bergantung pada pembagian data tertentu.

Grafik per fold ada di `reports/cv_5fold_scores.png`.

## Perbandingan dengan algoritma lain

```bash
python src/compare_baselines.py
```

Ketiganya dilatih pada dataset dan pembagian data yang sama.

| Algoritma | Akurasi | F1-macro |
|---|---|---|
| SVM | 97,53% | 0,9726 |
| Logistic Regression | 97,09% | 0,9675 |
| Naive Bayes | 93,95% | 0,9313 |

Confusion matrix masing-masing tersimpan terpisah di `reports/`.

## Pengujian pada kasus ambigu

```bash
python src/evaluate_hard_set.py
```

Diuji pada 135 komentar di `data/hard_test_set.csv` yang tidak ikut dilatih.

```
Accuracy : 98,52%
FP       : 2
FN       : 0
```

### Membaca angka F1-macro pada pengujian ini

Berkas `reports/hard_set_evaluation.txt` mencantumkan F1-macro **0,4963**,
yang sekilas terlihat seperti model gagal total. Angka itu menyesatkan, dan
penyebabnya ada pada komposisi data ujinya sendiri.

Seluruh 135 entri dalam kumpulan ini berlabel non-spam. Tidak ada satu pun
entri spam di dalamnya, karena kumpulan ini memang dirancang khusus untuk
menguji satu hal: apakah model salah menuduh komentar yang menyebut nama situs
judi tetapi bukan promosi.

F1-macro merata-ratakan F1 dari kedua kelas. Karena kelas spam tidak punya
satu pun contoh sebenarnya, F1 untuk kelas itu bernilai nol, dan rata-ratanya
otomatis tertarik ke sekitar setengah. Yang bermakna pada pengujian ini adalah
akurasi dan jumlah false positive, bukan F1-macro.

### Dua kesalahan yang tersisa

```
[1] Brantas pak, ini situs Judi online yg saya tahu... Udintogel, Zara4d, Playbook88 dll
[2] Sabung marmut aja dri pda GACOR88
```

Keduanya adalah komentar yang **melaporkan atau menyindir** situs judi, bukan
mempromosikannya. Keduanya juga memuat beberapa nama situs sekaligus.

Setelah normalisasi, kalimat pertama menjadi
`brantas pak situs judi online udintogel judolbrand judolbrand dll`. Kata yang
menandakan niat melaporkan, yaitu `brantas`, kalah bobot oleh kemunculan token
`judolbrand` berkali-kali.

## Keterbatasan

**Nama situs yang tidak mengikuti pola.** Kanonikalisasi nama situs bekerja
dengan mengenali pola nama ditambah akhiran numerik atau akhiran khas. Nama
yang tidak mengikuti pola itu tidak terkonversi, dan jika belum pernah muncul
di data latih maka tidak punya bobot sama sekali.

**Kata laporan yang tenggelam oleh nama situs.** Seperti terlihat pada kedua
false positive di atas, komentar yang menyebut banyak nama situs sekaligus
cenderung diklasifikasikan sebagai spam meskipun niatnya melaporkan. Ini
konsekuensi dari model linear yang menjumlahkan bobot per token tanpa memahami
struktur kalimat.

Satu kasus diuji secara khusus untuk memastikan ini bukan sekadar soal kurang
data. Sebuah komentar yang semula salah diklasifikasi sengaja ditambahkan ke
data latih, lalu model dilatih ulang. Model tetap salah mengklasifikasikannya.
Ini menunjukkan batasannya bersifat struktural pada SVM linear, bukan masalah
jumlah contoh.

**Bahasa.** Model dilatih pada komentar berbahasa Indonesia. Komentar dalam
bahasa lain tidak diuji.

**Ketergantungan pada server.** Prediksi terjadi di server, sehingga ekstensi
tidak berfungsi tanpa koneksi. Kemungkinan menjalankan model langsung di
peramban tercatat di [roadmap.md](roadmap.md).
