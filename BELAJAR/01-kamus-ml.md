# 01 — Kamus ML untuk Anak Software Engineering

> Semua istilah ML yang muncul di skripsimu, dijelaskan pakai analogi dari dunia yang sudah kamu kuasai.

Dibaca berurutan. Tiap kelompok dibangun di atas kelompok sebelumnya.

---

# Kelompok 1 — Fondasi

## Machine Learning (supervised learning)

🎯 **Intinya:** menulis aturan secara otomatis dari contoh, bukan mengetiknya sendiri.

🔍 Bayangkan kamu diminta membuat penyaring spam. Cara SE biasa:

```javascript
if (text.includes("slot") || text.includes("gacor") || text.includes("wd")) {
  return "spam";
}
```

Masalahnya kamu sudah tahu: spammer tinggal menulis `sl0t`, `ｇａｃｏｒ`, atau `g4c0r`, dan aturanmu jebol. Kamu tambah kondisi, mereka ubah lagi. Selamanya.

**Supervised learning membalik arahnya.** Kamu tidak menulis kondisinya. Kamu memberikan 6.690 contoh komentar yang sudah dilabeli "ini spam / ini bukan", lalu algoritma yang menyusun sendiri aturannya — termasuk kombinasi yang tidak akan pernah terpikir olehmu.

"Supervised" artinya tiap contoh **ada kunci jawabannya**. Itulah kenapa pelabelan jadi begitu penting: kalau kunci jawabannya salah, yang dipelajari juga salah.

❓ **Kalau ditanya "apa bedanya dengan filter kata kunci biasa?"**
> "Filter kata kunci aturannya ditulis manual dan statis, Pak. Begitu spammer mengubah tulisan, aturannya harus diperbarui manual dan selalu tertinggal. Model ini menyusun aturannya sendiri dari 6.690 contoh berlabel, jadi bisa mengenali kombinasi pola yang tidak ditulis eksplisit."

---

## Fitur (*feature*)

🎯 **Intinya:** satu kolom data yang jadi bahan pertimbangan model.

🔍 Kalau kamu punya tabel database, tiap **kolom** itu satu fitur. Model melihat baris, membaca nilai tiap kolom, lalu memutuskan.

Masalahnya: teks bukan tabel. Komentar `"daftar slot gacor"` itu satu string, bukan kolom-kolom. Jadi harus diubah dulu jadi tabel — dan itulah tugas TF-IDF.

Di proyekmu, **tiap kata unik jadi satu kolom**. Dengan `max_features=10000`, artinya tabelnya punya maksimal 10.000 kolom.

---

## Vektorisasi

🎯 **Intinya:** mengubah teks jadi deretan angka.

🔍 Ini persis seperti **serialisasi**. Objek di memori tidak bisa dikirim lewat jaringan apa adanya — harus diubah jadi JSON dulu. Sama halnya, teks tidak bisa dihitung secara matematis — harus diubah jadi array angka dulu.

Bedanya: JSON dirancang supaya bisa dikembalikan ke bentuk semula. Vektorisasi teks **tidak** — begitu jadi angka, urutan kata hilang sebagian. Itu konsekuensi yang diterima demi bisa menghitung.

---

# Kelompok 2 — Mengubah teks jadi angka

## TF-IDF

🎯 **Intinya:** memberi nilai penting pada tiap kata. Kata yang sering muncul di satu komentar tapi jarang muncul di komentar lain = paling bernilai.

🔍 Ini sebenarnya bukan konsep ML — ini konsep **information retrieval**, teknik yang sama dipakai mesin pencari untuk memberi peringkat dokumen. Kalau kamu pernah menyentuh Elasticsearch atau *full-text search* di PostgreSQL, kamu sudah pernah bertemu ini.

Namanya gabungan dua bagian:

**TF (*Term Frequency*)** — seberapa sering kata ini muncul di komentar ini.
Kata "slot" muncul 3 kali di satu komentar → TF = 3. Sederhana.

**IDF (*Inverse Document Frequency*)** — seberapa langka kata ini di seluruh dataset.

Ini bagian yang cerdas. Pikirkan: kata "yang" muncul di hampir semua komentar. Apakah "yang" membantu membedakan spam dari bukan spam? **Tidak sama sekali.** Sedangkan kata "gacor" cuma muncul di sedikit komentar — dan ketika muncul, sangat informatif.

Jadi IDF memberi **bobot besar untuk kata langka, bobot kecil untuk kata pasaran**:

```
IDF(kata) = log( total_dokumen / jumlah_dokumen_yang_memuat_kata )
```

Kalau sebuah kata muncul di **semua** dokumen, maka `total / jumlah = 1`, dan `log(1) = 0`. Bobotnya **nol**. Kata pasaran otomatis terbuang tanpa perlu daftar hitam.

**Bobot akhir = TF × IDF.**

🔍 **Contoh nyata dari skripsimu** (Sub-bab 2.5), dataset mini 3 komentar:

```
Komentar 1: "link slot paling gacor hari ini"
Komentar 2: "video edukasi ini sangat bermanfaat"
Komentar 3: "depo slot anti rungkad di sini"
```

Hitung bobot kata **"slot"** di Komentar 1:
- TF = 1 (muncul sekali)
- Muncul di 2 dari 3 komentar → IDF = log(3/2) = **0,176**
- Bobot = 1 × 0,176 = **0,176**

Hitung bobot kata **"ini"** di Komentar 1:
- TF = 1
- Muncul di 3 dari 3 komentar → IDF = log(3/3) = log(1) = **0**
- Bobot = 1 × 0 = **0**

Kata "ini" otomatis dianggap tidak berguna. Tidak ada yang menulis aturan "abaikan kata ini" — matematikanya yang membuangnya sendiri.

📍 **Di kode:** `src/train.py` baris 63–68
📄 **Di skripsi:** Sub-bab 2.5, Gambar 2.1

❓ **Kalau ditanya "kenapa pakai TF-IDF, bukan hitung frekuensi biasa?"**
> "Kalau hanya frekuensi, kata seperti 'yang' dan 'di' akan mendominasi karena paling sering muncul, padahal tidak membedakan apa-apa. TF-IDF menambahkan faktor kelangkaan, sehingga kata yang muncul di semua komentar otomatis berbobot nol dan kata penciri spam mendapat bobot tinggi."

---

## Empat pengaturan TF-IDF di proyekmu

📍 `src/train.py` baris 63–68:

```python
TFIDF_PARAMS = dict(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True,
)
```

Tiap baris ada alasannya. Ini sering ditanya satu per satu.

### `max_features=10000`
🎯 Ambil 10.000 kata paling sering saja, sisanya buang.

🔍 Tanpa batas ini, tiap kata unik jadi kolom — termasuk salah ketik yang cuma muncul sekali. Dataset 6.690 komentar bisa menghasilkan puluhan ribu kolom, mayoritas sampah. Ini seperti membatasi ukuran indeks: ambil yang berguna, buang ekor panjangnya.

### `ngram_range=(1, 2)`
🎯 Jadikan fitur bukan cuma kata tunggal, tapi juga pasangan kata berurutan.

🔍 **Unigram** = satu kata: `daftar`, `sekarang`.
**Bigram** = dua kata berurutan: `daftar sekarang`.

Kenapa perlu? Karena makna bisa berubah tergantung pasangan. Kata `link` sendirian netral. Kata `slot` sendirian bisa saja soal *slot* waktu. Tapi `link slot` berurutan → jelas judol.

Kenapa tidak sampai trigram (1,3)? Karena jumlah kolom meledak sementara tambahan informasinya kecil. Kamu punya eksperimennya di `src/experiment_features.py`.

### `min_df=2`
🎯 Kata yang cuma muncul di 1 komentar seumur hidup, buang.

🔍 `df` = *document frequency*. Kalau sebuah kata cuma pernah muncul sekali di seluruh 6.690 komentar, kemungkinan besar itu salah ketik atau nama orang — tidak ada gunanya jadi aturan. Ini seperti mengabaikan *outlier* yang cuma muncul sekali di log.

### `sublinear_tf=True`
🎯 Kata yang muncul 10 kali tidak dianggap 10 kali lebih penting.

🔍 Ini yang paling jarang dipahami, padahal alasannya masuk akal. Bayangkan komentar spam yang menulis `"slot slot slot slot slot"`. Dengan TF biasa, bobotnya 5× lipat. Padahal informasinya tidak 5× lebih banyak — pengulangan tidak menambah kepastian sebanyak itu.

`sublinear_tf` mengubah rumusnya jadi `1 + log(TF)`, sehingga pertambahannya melandai. Muncul 1 kali → 1,0. Muncul 5 kali → sekitar 2,6. Naik, tapi tidak lima kali lipat.

Analogi SE: seperti **skala logaritmik pada grafik monitoring**. Kamu pakai log karena lonjakan ekstrem tidak boleh menenggelamkan seluruh grafik.

❓ **Kalau ditanya "kenapa `sublinear_tf` diaktifkan?"**
> "Supaya pengulangan kata tidak memberi bobot berlebihan, Pak. Komentar spam sering mengulang kata yang sama berkali-kali. Tanpa ini, pengulangan 5 kali dianggap 5 kali lebih penting, padahal informasinya tidak bertambah sebanyak itu. Dengan `sublinear_tf`, pertambahan bobotnya melandai secara logaritmik."

---

# Kelompok 3 — Mengambil keputusan

## SVM (*Support Vector Machine*)

🎯 **Intinya:** menarik garis pemisah terbaik antara dua kelompok.

🔍 Setelah TF-IDF, tiap komentar jadi satu titik di ruang berdimensi banyak. Komentar spam berkumpul di satu wilayah, non-spam di wilayah lain. Tugas SVM: **menarik batas** di antara keduanya.

Kalau digambar 2 dimensi (lihat Gambar 2.2 di skripsimu): titik biru di kiri atas, titik hijau di kanan bawah, dan ada garis merah memisahkan.

Analogi SE: ini seperti *decision boundary* — pada dasarnya sebuah kondisi `if` raksasa, tapi disusun otomatis dari data dan melibatkan ribuan variabel sekaligus.

## Hyperplane

🎯 **Intinya:** nama resmi "garis pemisah" itu, untuk dimensi berapa pun.

🔍 Di 2 dimensi, pemisahnya berupa **garis**. Di 3 dimensi, berupa **bidang**. Di 10.000 dimensi (jumlah fitur TF-IDF-mu), tidak ada namanya dalam bahasa sehari-hari — jadi disebut ***hyperplane***.

Jangan coba membayangkannya secara visual. Matematikanya tetap sama persis; cuma jumlah sumbunya lebih banyak. Ini sama seperti kamu tenang saja memakai array 10.000 elemen tanpa perlu membayangkannya sebagai bentuk fisik.

Rumusnya: `w · x − b = 0`
- `x` = komentar dalam bentuk angka
- `w` = bobot tiap fitur (seberapa besar pengaruh tiap kata)
- `b` = pergeseran garis

## Margin dan *support vector*

🎯 **Intinya:** SVM tidak asal menarik garis pemisah — dia mencari garis yang **jaraknya paling jauh** dari titik terdekat kedua kelompok.

🔍 Ini yang membuat SVM berbeda. Kalau dua kelompok bisa dipisah, biasanya ada **tak hingga banyak** garis yang bisa memisahkannya. Yang mana yang terbaik?

SVM menjawab: yang **paling lega**. Yang punya jarak aman paling lebar ke titik terdekat di kedua sisi. Jarak aman itu namanya **margin**.

Analogi SE: seperti menaruh *threshold* di tengah-tengah zona aman, bukan mepet ke nilai yang pernah terjadi. Kalau kamu set *alert* memori di 79,9% padahal pernah tercatat 79,8%, sedikit fluktuasi langsung memicu alarm palsu. Kalau ditaruh di tengah antara pola normal dan pola bermasalah, sistemnya lebih tahan guncangan.

**Support vector** = titik-titik yang persis berada di tepi margin. Merekalah yang menentukan posisi garis. Titik-titik lain yang jauh dari batas **tidak berpengaruh sama sekali** — kalau dihapus, garisnya tidak bergeser.

Analogi SE: ini persis ***boundary test case***. Yang menentukan benar-tidaknya sebuah aturan adalah kasus-kasus di perbatasan, bukan kasus yang jelas-jelas aman.

❓ **Kalau ditanya "apa keunggulan SVM dibanding algoritma lain?"**
> "SVM memilih pemisah dengan margin terlebar, bukan sekadar pemisah yang kebetulan berhasil. Itu membuatnya lebih tahan terhadap variasi data baru. Selain itu SVM kuat pada data berdimensi tinggi seperti teks — dalam penelitian ini ada 10.000 fitur — dan hanya bergantung pada *support vector*, bukan seluruh data."

---

## Kernel linear

🎯 **Intinya:** pemisahnya berupa garis lurus, bukan lengkung.

🔍 SVM bisa memakai pemisah melengkung lewat *kernel* lain (RBF, polinomial). Kenapa proyekmu memilih yang lurus?

Dua alasan:
1. **Data teks berdimensi tinggi biasanya sudah bisa dipisahkan garis lurus.** Dengan 10.000 sumbu, ruangnya begitu longgar sehingga garis lurus umumnya cukup. Ini temuan umum dalam klasifikasi teks.
2. **Jauh lebih cepat.** Dan kecepatan itu penting karena sistemmu harus menjawab *real-time* saat pengguna menggulir halaman.

Analogi SE: memilih algoritma O(n) yang cukup, ketimbang O(n²) yang sedikit lebih akurat tapi bikin permintaan *timeout*.

---

## Parameter C

🎯 **Intinya:** seberapa galak model menghukum kesalahan saat belajar.

🔍 Ada pertukaran di sini:

- **C kecil** (misal 0,01) → "santai, salah sedikit tidak apa-apa". Margin jadi lebar, model lebih umum, tapi bisa terlalu longgar.
- **C besar** (misal 100) → "jangan sampai ada yang salah". Model memaksakan diri menghafal tiap kasus, termasuk yang aneh-aneh. Bagus di data latih, jeblok di data baru.

Analogi SE: seperti pengaturan *linter*. Terlalu longgar, bug lolos. Terlalu ketat, kamu menghabiskan waktu menambal peringatan yang tidak penting.

Proyekmu memakai **C = 1**, dan angka itu **tidak dikarang** — dicari otomatis lewat GridSearchCV yang menguji C = 0,01 / 0,1 / 1 / 10 / 100 dan memilih yang skornya terbaik.

📍 **Di kode:** `src/train.py` baris 240
📄 **Di skripsi:** Sub-bab 4.10.3, Gambar 4.9

---

## `class_weight="balanced"`

🎯 **Intinya:** mengimbangi jumlah data yang timpang.

🔍 Datasetmu **tidak seimbang**: 2.332 spam vs 4.358 non-spam. Non-spam hampir dua kali lipat.

Kenapa ini masalah? Karena model yang malas bisa mencapai akurasi 65% hanya dengan **selalu menjawab "non-spam"** tanpa belajar apa-apa. Secara angka kelihatan lumayan, padahal tidak berguna sama sekali.

`class_weight="balanced"` membuat kesalahan pada kelas minoritas **dihitung lebih mahal**. Karena spam lebih sedikit, tiap spam yang lolos dihukum lebih berat. Model jadi terpaksa serius mempelajari kelas yang jarang.

Analogi SE: seperti memberi bobot lebih pada *error* kritikal dibanding *warning* biasa di sistem peringatan. Bukan semua kesalahan setara.

📍 **Di kode:** `src/train.py` baris 240

❓ **Kalau ditanya "data kamu tidak seimbang, bagaimana mengatasinya?"**
> "Betul, komposisinya 2.332 spam dan 4.358 non-spam. Ditangani lewat parameter `class_weight='balanced'` pada SVM, yang membuat kesalahan pada kelas minoritas dihukum lebih berat secara proporsional. Selain itu metrik utamanya memakai F1-macro, bukan akurasi, supaya kelas yang lebih sedikit tetap dihitung setara."

---

# Kelompok 4 — Mengukur hasil

## Overfitting

🎯 **Intinya:** model menghafal, bukan memahami.

🔍 Analogi paling pas untuk SE: bayangkan seseorang menulis fungsi supaya lolos tes, tapi caranya dengan `if input == 5 return 25; if input == 6 return 36;` — bukan dengan `return input * input`. Semua tes hijau, tapi begitu diberi masukan baru, hancur.

Itu overfitting. Modelnya hafal data latih, bukan menangkap polanya.

Cara mendeteksinya: **uji dengan data yang belum pernah dilihat**. Itulah gunanya pemisahan data latih dan data uji.

---

## Pemisahan data latih / uji

🎯 **Intinya:** sembunyikan sebagian data, pakai untuk ujian.

🔍 Dari 6.690 komentar: **5.352 (80%) untuk belajar**, **1.338 (20%) disimpan untuk ujian**. Model tidak pernah melihat 1.338 itu selama pelatihan.

Tiga pengaturannya:

- `test_size=0.2` → 20% disisihkan
- `random_state=42` → **kunci acakan**, supaya pembagiannya sama persis tiap kali dijalankan. Ini sama persis dengan konsep *reproducible build*: hasil kemarin harus bisa diulang hari ini. Kalau ditanya "kenapa 42?" jawabannya jujur saja: itu angka konvensi yang lazim dipakai, nilainya sendiri tidak penting — yang penting **tetap**.
- `stratify=y` → **pastikan komposisi spam/non-spam sama di kedua bagian**. Tanpa ini, bisa saja secara kebetulan data uji kebanyakan non-spam, dan hasil ujiannya jadi tidak mewakili.

📍 **Di kode:** `src/train.py` baris 197–201

---

## Confusion matrix

🎯 **Intinya:** tabel 2×2 yang merinci jenis kesalahan model.

🔍 Akurasi saja menipu, karena tidak membedakan **jenis** kesalahan. Confusion matrix membedakannya:

|  | Ditebak non-spam | Ditebak spam |
|---|---|---|
| **Aslinya non-spam** | TN = 863 ✅ | **FP = 9** ❌ |
| **Aslinya spam** | **FN = 24** ❌ | TP = 442 ✅ |

- **TP** (*true positive*) = spam, ditebak spam. Benar.
- **TN** (*true negative*) = bukan spam, ditebak bukan spam. Benar.
- **FP** (*false positive*) = **komentar normal disangka spam.** Ini yang bikin pengguna kesal — komentar orang tidak bersalah ikut disembunyikan.
- **FN** (*false negative*) = **spam lolos.** Ini kegagalan tujuan utama sistem.

Analogi SE: persis seperti sistem *alerting*. FP = alarm palsu yang bikin tim capek. FN = insiden nyata yang tidak terdeteksi. Keduanya buruk dengan cara berbeda, dan kamu harus memilih mau condong ke mana.

📄 **Di skripsi:** Tabel 4.11 dan Gambar 4.7

---

## Accuracy, Precision, Recall, F1

Empat metrik, masing-masing menjawab pertanyaan berbeda. Ini **wajib hafal**.

### Accuracy — "berapa persen tebakan yang benar?"
```
(TP + TN) / total  =  (442 + 863) / 1.338  =  0,9753  →  97,53%
```
Kelemahannya: menipu kalau data timpang.

### Precision — "kalau model bilang spam, seberapa sering dia benar?"
```
TP / (TP + FP)  =  442 / 451  =  0,9800
```
Precision tinggi = **jarang salah tuduh**. Ini yang menjaga pengalaman pengguna.

### Recall — "dari semua spam yang ada, berapa yang berhasil ditangkap?"
```
TP / (TP + FN)  =  442 / 466  =  0,9485
```
Recall tinggi = **jarang kecolongan**. Ini yang menjaga tujuan sistem.

### F1 — "gabungan seimbang precision dan recall"
```
2 × (0,9800 × 0,9485) / (0,9800 + 0,9485)  =  0,9640
```

🔍 **Kenapa harus ada empat?** Karena precision dan recall **tarik-menarik**. Kalau model dibuat sangat berhati-hati (cuma menuduh saat sangat yakin), precision naik tapi banyak spam lolos → recall turun. Kalau dibuat agresif, sebaliknya.

F1 adalah rata-rata harmonik keduanya. Dipakai rata-rata harmonik, bukan rata-rata biasa, karena rata-rata harmonik **menghukum ketimpangan**. Precision 1,0 dan recall 0,0 menghasilkan rata-rata biasa 0,5 (kelihatan lumayan), tapi F1-nya 0 (jujur: modelnya tidak berguna).

---

## F1-macro vs F1-weighted

🎯 **Intinya:** macro memperlakukan kedua kelas setara; weighted memihak kelas mayoritas.

🔍 **Macro** = hitung F1 tiap kelas, lalu rata-ratakan biasa. Kelas kecil dan kelas besar punya suara sama.
**Weighted** = rata-rata tapi ditimbang jumlah datanya. Kelas besar lebih berpengaruh.

Proyekmu memakai **F1-macro** justru karena datanya timpang. Kalau pakai weighted, performa pada kelas spam (yang lebih sedikit) bisa tertutupi oleh performa non-spam.

Nilai F1-macro modelmu: **0,9726**.

⚠️ **Ini penting — dan ada jebakannya.** Baca bagian F1-macro 0,4963 di `03-angka-ke-kode.md` sebelum sidang. Ada satu angka di berkas laporanmu yang terlihat seperti kegagalan besar padahal bukan.

---

## Cross-validation (k-fold)

🎯 **Intinya:** ujian diulang 5 kali dengan pembagian data berbeda, lalu dirata-rata.

🔍 Masalah dengan satu kali pembagian data: bisa saja kamu **beruntung**. Kebetulan data uji yang terpilih kebetulan mudah, jadi skornya bagus — padahal bukan karena modelnya bagus.

5-fold cross-validation menyelesaikan ini: data dibagi 5 bagian, lalu diuji 5 kali. Tiap putaran, 1 bagian jadi penguji dan 4 sisanya jadi bahan belajar. Bergiliran sampai semua bagian pernah jadi penguji.

Analogi SE: seperti menjalankan *test suite* di 5 lingkungan berbeda, bukan cuma di laptop sendiri. Kalau lulus di semuanya, kamu jauh lebih yakin.

Hasil modelmu: **rata-rata 0,9741 dengan simpangan baku 0,0030**.

Angka simpangan baku yang kecil itu **kabar bagus dan layak dibanggakan** — artinya performanya konsisten di kelima putaran, bukan bagus di satu putaran dan jeblok di putaran lain.

📍 **Di kode:** `src/train.py` baris 105–138
📄 **Di skripsi:** Sub-bab 4.10.2, Gambar 4.8

❓ **Kalau ditanya "kenapa perlu cross-validation kalau sudah ada data uji?"**
> "Supaya hasilnya tidak bergantung pada satu pembagian data yang kebetulan menguntungkan. Cross-validation mengulang pengujian lima kali dengan pembagian berbeda. Hasilnya 0,9741 dengan simpangan baku hanya 0,0030, yang menunjukkan performanya stabil, bukan kebetulan."

---

## GridSearchCV

🎯 **Intinya:** mencoba semua kombinasi pengaturan secara otomatis, ambil yang terbaik.

🔍 Nilai C harus ditentukan sebelum pelatihan, tapi tidak ada rumus untuk menebaknya. Jadi caranya: coba saja semuanya.

GridSearchCV mencoba C = 0,01 / 0,1 / 1 / 10 / 100, masing-masing diuji dengan cross-validation, lalu memilih pemenangnya. Hasilnya: **C = 1**.

Analogi SE: seperti *benchmark* beberapa konfigurasi lalu memakai yang tercepat — bukan menebak dari perasaan.

⚠️ **Detail penting:** pencarian ini dijalankan **hanya pada data latih**, tidak menyentuh data uji. Kalau data uji ikut dipakai untuk memilih C, berarti data uji sudah "bocor" mempengaruhi model, dan skor akhirnya tidak jujur lagi. Istilahnya **data leakage**. Kodenya sudah benar dalam hal ini.

📍 **Di kode:** `src/train.py` baris 245 (dilatih pada `X_train` saja)

---

## Platt Scaling — asal angka persentase keyakinan

🎯 **Intinya:** mengubah "jarak ke garis pemisah" jadi "persentase keyakinan".

🔍 Ini sering ditanya karena angkanya kelihatan di antarmuka.

SVM sebenarnya **tidak menghasilkan probabilitas**. Keluarannya cuma `f(x) = w · x − b`, yaitu seberapa jauh sebuah titik dari garis pemisah, dan di sisi mana. Nilainya bisa 0,3 atau 2,7 atau −1,4. Itu **bukan persentase**.

Tapi di ekstensimu ada tulisan "87% yakin spam". Dari mana?

**Platt Scaling** mengubah jarak tadi jadi rentang 0–1 lewat fungsi sigmoid:

```
P(spam | x) = 1 / (1 + exp(A · f(x) + B))
```

`A` dan `B` bukan angka karangan — keduanya diperkirakan lewat cross-validation internal pada data latih, terpisah dari proses pembentukan hyperplane, supaya hasilnya tidak bias.

Analogi SE: seperti **normalisasi** skor mentah jadi persentase yang bisa dipahami manusia. Skor mentah bermakna bagi mesin, persentase bermakna bagi pengguna.

📍 **Di kode:** `src/train.py` baris 240 dan 339 (`probability=True`), `src/server.py` baris 307 (`predict_proba`)
📄 **Di skripsi:** Sub-bab 2.6.1

❓ **Kalau ditanya "angka persentase di badge itu dari mana?"**
> "Dari kalibrasi Platt Scaling, Pak. SVM sendiri keluarannya jarak ke hyperplane, bukan probabilitas. Jarak itu dipetakan ke rentang 0–1 lewat fungsi sigmoid, dengan parameter yang diestimasi lewat cross-validation internal. Di scikit-learn diaktifkan lewat `probability=True`, lalu diambil dengan `predict_proba`."

---

## Threshold (ambang batas)

🎯 **Intinya:** batas keyakinan minimum sebelum komentar disembunyikan.

🔍 Model mengeluarkan angka keyakinan 0–1. Tapi berapa yang cukup untuk bertindak? Itu **bukan keputusan matematis, tapi keputusan produk**.

Proyekmu memakai **0,75** sebagai bawaan, bisa diatur pengguna antara 0,50–0,95.

Menaikkan ambang → lebih berhati-hati, lebih sedikit salah tuduh, tapi lebih banyak spam lolos.
Menurunkan ambang → lebih agresif, lebih sedikit yang lolos, tapi lebih sering salah tuduh.

Analogi SE: persis pengaturan sensitivitas alarm. Dan seperti alarm, **tidak ada nilai yang benar secara universal** — tergantung mana yang lebih mengganggu bagi penggunanya. Itu sebabnya di sistemmu nilainya bisa diubah pengguna, bukan dipatok mati.

---

# Kelompok 5 — Istilah eksperimen

## Baseline

🎯 **Intinya:** pembanding, untuk membuktikan pilihanmu memang lebih baik.

🔍 Mengatakan "SVM mencapai 97,53%" itu tidak bermakna kalau berdiri sendiri. Bagus dibanding apa? Mungkin masalahnya memang mudah dan algoritma apa pun bisa mencapai angka itu.

Makanya kamu menguji dua pembanding dengan fitur yang **sama persis**:

| Algoritma | Akurasi | F1-macro |
|---|---|---|
| **SVM** | **97,53%** | **0,9726** |
| Logistic Regression | 97,09% | 0,9675 |
| Multinomial Naive Bayes | 93,95% | 0,9313 |

Analogi SE: seperti *control group* pada A/B testing. Tanpa pembanding, angka apa pun tidak punya arti.

📍 **Di kode:** `src/compare_baselines.py`

---

## Ablation study

🎯 **Intinya:** matikan satu komponen, ukur dampaknya.

🔍 Kalau kamu ingin tahu apakah sebuah komponen benar-benar berguna, cara paling jujur adalah mencabutnya lalu mengukur seberapa buruk hasilnya.

Analogi SE: persis seperti mematikan *feature flag* lalu mengukur metrik. Kalau tidak ada bedanya, berarti fitur itu memang tidak memberi nilai.

Di proyekmu, hasilnya **berlawanan dengan dugaan**: menambahkan aturan heuristik di atas SVM justru **menurunkan** akurasi 7,32 poin pada data uji dan 16,30 poin pada hard test set.

Ini temuan yang bagus, bukan kegagalan. Penjelasannya ada di `04-kenapa-a-bukan-b.md`.

📍 **Di kode:** `src/evaluate_hybrid_ablation.py`

---

## p-value dan signifikansi statistik

🎯 **Intinya:** ukuran apakah suatu perbedaan itu nyata atau cuma kebetulan.

🔍 Ini analogi paling mudah untuk SE: **A/B testing**.

Bayangkan versi A mengonversi 10,2% dan versi B mengonversi 10,4%. Apakah B lebih baik? Belum tentu — selisih 0,2% bisa saja cuma noise. Kamu butuh uji statistik untuk memastikan.

p-value menjawab: *"kalau sebenarnya tidak ada perbedaan sama sekali, seberapa mungkin aku melihat selisih sebesar ini karena kebetulan belaka?"*

- p kecil (< 0,05) → kecil kemungkinan kebetulan → **perbedaannya nyata**
- p besar (> 0,05) → sangat mungkin kebetulan → **belum terbukti berbeda**

Eksperimen *stemming* di proyekmu menghasilkan **p = 0,3575**. Artinya: kalau sebenarnya stemming tidak berpengaruh apa-apa, peluang melihat selisih sebesar itu karena kebetulan adalah **36%**. Jauh terlalu besar untuk disebut bukti.

Kesimpulan yang benar: **belum terbukti stemming membantu**. Perhatikan kalimatnya — bukan "stemming terbukti tidak membantu". Bedanya halus tapi penting, dan penguji yang teliti akan menghargainya.

📍 **Di kode:** `src/experiment_stemming.py`
📄 **Di skripsi:** Sub-bab 4.10.7, Gambar 4.10

---

## Stemming dan stopwords

**Stopwords** 🎯 kata pasaran yang dibuang karena tidak membedakan apa-apa: "yang", "dan", "di".
📍 Daftarnya ada di `src/preprocessing.py` baris 123–135, berisi juga ragam tidak baku khas YouTube seperti "gua", "kalo", "udah".

**Stemming** 🎯 memotong imbuhan supaya kata serumpun jadi satu bentuk: "mendaftar", "pendaftaran", "didaftarkan" → "daftar".

Secara teori stemming membantu karena mengurangi jumlah fitur. Tapi di proyekmu **diuji dan ternyata tidak signifikan**, jadi tidak dipakai di pipeline akhir. Ini keputusan berbasis bukti, dan itu justru nilai tambah.

---

## Obfuscation, homoglyph, leet speak

Tiga istilah yang jadi inti masalah skripsimu.

**Obfuscation** 🎯 penyamaran teks supaya lolos deteksi. Istilah payungnya.

**Homoglyph** 🎯 karakter dari sistem tulisan lain yang bentuknya mirip huruf Latin.
Contoh: `а` Cyrillic (U+0430) terlihat identik dengan `a` Latin (U+0061), tapi bagi komputer **sama sekali berbeda**. Spammer menulis `dаftаr` dengan huruf Cyrillic, dan pencocokan kata kunci gagal total.
📍 Daftar penanganannya di `src/preprocessing.py` baris 148–175.

**Leet speak** 🎯 mengganti huruf dengan angka mirip: `s1tus` → `situs`, `d3p0s1t` → `deposit`, `H0KI` → `HOKI`.
📍 Penanganannya di `src/preprocessing.py` baris 271–292.

🔍 Menariknya, kodemu hanya menormalkan `0 → o` dan `1 → i`, tidak `3 → e` atau `4 → a`. Ini **disengaja** — alasannya tertulis di komentar kode baris 280–284: substitusi yang lebih agresif berisiko merusak angka yang sah, misalnya skor "354" berubah jadi "ses". Ini contoh bagus dari pertukaran teknik yang bisa kamu ceritakan saat sidang.

---

# Ringkasan satu halaman

Kalau besok sidang dan cuma sempat baca satu hal, baca ini:

| Istilah | Satu kalimat |
|---|---|
| TF-IDF | Kata langka tapi sering di satu komentar = paling bernilai |
| N-gram (1,2) | Fiturnya kata tunggal **dan** pasangan kata |
| Hyperplane | Garis pemisah antara spam dan bukan spam |
| Margin | Jarak aman ke titik terdekat; SVM memaksimalkannya |
| Support vector | Titik di perbatasan yang menentukan posisi garis |
| C = 1 | Ketegasan model, dipilih otomatis lewat GridSearchCV |
| class_weight balanced | Penyeimbang karena spam lebih sedikit (2.332 vs 4.358) |
| Accuracy 97,53% | (442+863)/1.338 |
| Precision 0,98 | Kalau bilang spam, 98% benar |
| Recall 0,95 | Dari semua spam, 95% tertangkap |
| F1-macro 0,9726 | Gabungan seimbang, kedua kelas dihitung setara |
| CV 0,9741 ± 0,0030 | Diuji 5 kali, hasilnya konsisten |
| Platt Scaling | Pengubah jarak jadi persentase keyakinan |
| Threshold 0,75 | Batas keyakinan sebelum komentar disembunyikan |
| p = 0,3575 | Stemming belum terbukti membantu |

---

## Selanjutnya

Lanjut ke `02-bedah-kode.md` — membedah tiap berkas, mulai dari pengumpulan data.
