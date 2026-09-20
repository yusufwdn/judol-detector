# Eksperimen

Tiga eksperimen dijalankan untuk menguji apakah pipeline perlu ditambah.
Dua di antaranya menghasilkan temuan negatif, dan keduanya tetap dilaporkan.

Alasannya sederhana. Ketiga pendekatan ini masuk akal secara teori dan wajar
ditanyakan siapa pun yang membaca kode ini. Tanpa pengukuran, jawabannya hanya
bisa "tidak dipakai". Dengan pengukuran, jawabannya menjadi "sudah diuji, dan
ini hasilnya".

## Aturan heuristik tambahan

```bash
python src/evaluate_hybrid_ablation.py
```

### Yang diuji

Gagasannya menambahkan aturan berbasis kata kunci di atas keputusan SVM, untuk
menangkap kasus yang diduga sulit bagi model.

| Aturan | Perilaku |
|---|---|
| A | SVM memutuskan spam, tetapi teks tidak memuat kata judi yang pasti, maka keputusan diubah menjadi non-spam |
| B | SVM memutuskan non-spam, tetapi teks memuat kata judi yang pasti, maka keputusan diubah menjadi spam |

Aturan A dimaksudkan menekan false positive dari kata ambigu seperti `hoki`,
dan aturan B menekan false negative.

### Hasil

| Data uji | SVM murni | SVM + aturan | Selisih akurasi |
|---|---|---|---|
| Data uji (1.338 baris) | 97,53% | 90,21% | −7,32 poin |
| Kasus ambigu (135 baris) | 98,52% | 82,22% | −16,30 poin |

Rincian per aturan:

- **Aturan A** aktif 66 kali pada data uji. Hanya 4 di antaranya benar, 62
  salah. Penyebabnya, spam asli sering tidak memuat kata persis dari daftar
  kata kunci. Kalimat seperti "daftar sekarang, wd lancar, gabung yuk" adalah
  promosi yang jelas bagi model, tetapi tidak memuat satu pun kata dari daftar,
  sehingga aturan A justru membatalkan deteksi yang sudah benar.
- **Aturan B** aktif 27 kali di kedua data uji, dan **tidak satu pun benar**.
  Kata seperti `togel` dan `toto` justru paling sering muncul di komentar yang
  mengkritik judi online, bukan yang mempromosikannya. Aturan berbasis kata
  kunci tidak punya cara membedakan konteks itu.

### Kesimpulan

Begitu model dilatih dengan data yang cukup banyak dan beragam, SVM sendiri
sudah lebih baik daripada penimpaan berbasis kata kunci manual.

Kodenya tidak dihapus, melainkan dimatikan lewat `ENABLE_HYBRID_RULES = False`
di [`src/server.py`](../src/server.py), supaya hasil eksperimennya bisa
diverifikasi ulang. Keluaran lengkapnya ada di `reports/hybrid_ablation.txt`.

Temuan ini juga menjadi dasar empiris untuk tidak mengejar model yang lebih
rumit: pada kasus ini, menambah kompleksitas terbukti menurunkan performa.

## Stemming

```bash
python src/experiment_stemming.py
```

### Yang diuji

Stemming memangkas imbuhan sehingga `mendaftar`, `pendaftaran`, dan `daftar`
menjadi satu token. Secara teori ini mengurangi jumlah fitur dan memperkuat
sinyal tiap kata dasar. Pustaka yang dipakai adalah Sastrawi.

### Hasil

Dua pipeline yang identik kecuali pada tahap stemming dibandingkan memakai
5-fold cross-validation berpasangan, lalu selisihnya diuji dengan paired
t-test.

| Ukuran | Nilai |
|---|---|
| Rata-rata selisih F1-macro | −0,0006 |
| Nilai p | 0,3575 |

Selisihnya sangat kecil dan arahnya justru negatif. Dengan p jauh di atas
0,05, tidak ada dasar untuk menyimpulkan stemming memberi perbedaan.

### Kesimpulan

Stemming tidak dimasukkan ke pipeline produksi. Dugaan penyebabnya, kata
penciri spam judi online umumnya sudah berupa kata dasar, nama situs, atau
slang yang tidak berimbuhan, sehingga tidak banyak yang bisa dipangkas.

Sastrawi tetap tercantum di `requirements.txt` supaya eksperimen ini bisa
dijalankan ulang oleh siapa pun yang ingin memverifikasinya. Grafiknya ada di
`reports/experiment_stemming_cv.png`.

## Konfigurasi TF-IDF

```bash
python src/experiment_features.py
```

### Yang diuji

Beberapa kombinasi `ngram_range` dan `max_features` dibandingkan terhadap
konfigurasi yang dipakai, yaitu unigram dan bigram dengan 10.000 fitur.

### Hasil

Unigram saja sedikit lebih baik, dengan selisih +0,0034, tetapi selisih itu
tidak signifikan. Menambahkan trigram tidak membantu dan hanya menambah jumlah
fitur.

### Kesimpulan

Konfigurasi awal dipertahankan. Bigram tetap disertakan karena beberapa
frasa dua kata membawa makna yang hilang jika dipecah, dan biayanya tidak
besar. Keluarannya ada di `reports/experiment_features.csv` dan
`reports/experiment_features.png`.
