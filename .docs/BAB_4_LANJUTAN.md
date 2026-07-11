# BAB IV — Sub-bab 4.9 s/d 4.12 (Draft Pengisi Bagian Kosong)

> **Catatan penggunaan:**
> - Ini mengisi 4 sub-bab yang tadinya kosong di BAB IV.
> - **Italic istilah asing BELUM diterapkan** — tahap manual di Word.
> - Angka di 4.11 **sudah diverifikasi ulang terhadap kode & reports** (bukan sekadar salin dari DeepSeek). CV std = 0,30% (bukan 0,21%). Stemming delta = -0,0006.
> - Penanda `[GAMBAR ...]` / `[TABEL ...]` = tinggal dibuat/diletakkan. Nomor gambar/tabel **sesuaikan** dengan urutan final di dokumen lu (existing terakhir: Gambar 4.5, Tabel 4.3).
> - 4.12 memakai kerangka **Teknologi/Operasional/Hukum** sesuai pedoman hal. 18 (BUKAN PIECES — PIECES sudah di BAB III).

---

## 4.9 Sequence Diagram

Sequence diagram menggambarkan interaksi antar komponen sistem berdasarkan urutan waktu (time-ordered), mulai dari inisialisasi hingga proses penyembunyian komentar spam secara real-time. Diagram ini melibatkan lima objek utama, yaitu Pengguna, antarmuka Popup, Content Script, Server API, dan DOM halaman YouTube. Alur interaksi sistem disajikan pada Gambar 4.6.

> **[GAMBAR 4.6: Sequence Diagram Sistem Deteksi Spam Komentar YouTube]**
>
> *Panduan menggambar (buat di Word/Visio/draw.io, hitam-putih). Lima lifeline: Pengguna | Popup UI | Content Script | Server API (VPS) | DOM YouTube. Urutan pesan:*
> ```
> 1. Pengguna → Popup: membuka popup ekstensi
> 2. Popup → Server API: GET /health
> 3. Server API --> Popup: status (model_loaded=true)
> 4. Pengguna → Popup: atur confidence threshold & mode (Redupkan/Hilangkan)
> 5. Popup → Content Script: simpan pengaturan (chrome.storage)
> 6. Pengguna → DOM YouTube: membuka & menggulir halaman video
> 7. DOM YouTube → Content Script: MutationObserver mendeteksi komentar baru
> 8. Content Script → Server API: POST /predict/batch (daftar teks komentar, JSON)
> 9. Server API → Server API: preprocessing + TF-IDF + prediksi SVM
> 10. Server API --> Content Script: hasil klasifikasi (label + confidence)
> 11. Content Script → DOM YouTube: sembunyikan komentar (opacity 15% / display:none)
>     sesuai mode & jika confidence >= threshold
> ```

Berdasarkan sequence diagram di atas, proses dimulai ketika pengguna membuka antarmuka popup, yang memicu pemeriksaan status server melalui endpoint /health untuk memastikan model telah dimuat. Setelah pengguna menetapkan nilai confidence threshold dan mode penyembunyian, pengaturan tersebut disimpan dan digunakan oleh Content Script. Ketika pengguna membuka dan menggulir halaman video, MutationObserver pada Content Script mendeteksi komentar yang dimuat secara dinamis, lalu mengirimkannya secara kolektif ke endpoint /predict/batch. Server API menjalankan pipeline prapemrosesan, ekstraksi fitur TF-IDF, dan klasifikasi SVM, kemudian mengembalikan label beserta skor keyakinan. Content Script menyembunyikan komentar yang diklasifikasikan sebagai spam dengan skor keyakinan melampaui ambang batas, sesuai mode yang dipilih pengguna.

## 4.10 Rancangan Tampilan

Rancangan tampilan sistem terdiri atas dua bagian, yaitu struktur tampilan yang menggambarkan hierarki antarmuka, dan rancangan layar yang menampilkan wujud visual dari setiap komponen antarmuka.

### 4.10.1 Struktur Tampilan

Antarmuka sistem terbagi menjadi dua bagian utama. Bagian pertama adalah antarmuka popup ekstensi yang muncul ketika pengguna mengklik ikon ekstensi pada peramban. Bagian kedua adalah antarmuka hasil pada halaman YouTube, yaitu perubahan visual pada elemen komentar yang terdeteksi sebagai spam. Struktur hierarki tampilan sistem disajikan sebagai berikut:

1. Antarmuka Popup Ekstensi
   a. Header (nama dan identitas ekstensi)
   b. Kartu Status Server (indikator koneksi ke server)
   c. Panel Statistik (jumlah komentar dipindai dan disembunyikan)
   d. Pemilih Mode Penyembunyian (Redupkan / Hilangkan)
   e. Pengatur Confidence Threshold (slider)
   f. Tombol Aksi (Cek Status Server dan Reset Statistik)
2. Antarmuka Hasil pada Halaman YouTube
   a. Tampilan mode Redupkan (komentar diredupkan + badge keyakinan)
   b. Tampilan mode Hilangkan (komentar disembunyikan sepenuhnya)

### 4.10.2 Rancangan Layar

Rancangan layar antarmuka popup ekstensi ditunjukkan pada Gambar 4.7. Popup menampilkan kartu status server yang menunjukkan ketersediaan koneksi (indikator berwarna hijau untuk aktif, merah untuk tidak aktif) beserta alamat server. Di bawahnya terdapat panel statistik berisi dua nilai, yaitu jumlah komentar spam yang disembunyikan dan jumlah komentar yang telah dipindai. Pengguna dapat memilih mode penyembunyian melalui tombol Redupkan atau Hilangkan, serta menyesuaikan nilai confidence threshold antara 50% hingga 95% melalui slider. Bagian bawah menyediakan tombol untuk memeriksa ulang status server dan mengatur ulang statistik.

> **[GAMBAR 4.7: Rancangan Antarmuka Popup Ekstensi]**

Rancangan tampilan hasil pada halaman YouTube ditunjukkan pada Gambar 4.8. Pada mode Redupkan, komentar yang terdeteksi sebagai spam tetap berada pada halaman namun ditampilkan dengan transparansi rendah (opacity 15%) disertai badge yang menampilkan persentase keyakinan model, yang dapat diklik untuk memunculkan kembali komentar tersebut. Pada mode Hilangkan, komentar yang terdeteksi sebagai spam disembunyikan sepenuhnya dari tampilan sehingga tidak lagi terlihat oleh pengguna.

> **[GAMBAR 4.8: Rancangan Tampilan Komentar pada Mode Redupkan dan Mode Hilangkan]**

## 4.11 Pengujian Sistem

Pengujian sistem difokuskan pada evaluasi performa model klasifikasi SVM sebagai inti dari sistem deteksi. Pengujian dilakukan melalui lima skema, yaitu evaluasi pada data uji (holdout), validasi silang (cross-validation), pencarian hiperparameter, perbandingan dengan algoritma baseline, serta dua eksperimen tambahan berupa ablation study pendekatan hibrida dan pengujian pengaruh stemming.

### 4.11.1 Evaluasi pada Data Uji (Holdout)

Model SVM dievaluasi menggunakan 20% data uji (1.338 sampel) yang tidak pernah dilihat selama pelatihan. Hasil evaluasi disajikan pada Tabel 4.4.

**Tabel 4.4 Hasil Evaluasi Model SVM pada Data Uji**

| Metrik | Nilai |
|--------|-------|
| Accuracy | 97,53% |
| F1-macro | 0,9726 |
| Presisi (kelas spam) | 0,98 |
| Recall (kelas spam) | 0,95 |
| F1-Score (kelas spam) | 0,96 |
| F1-Score (kelas non-spam) | 0,98 |

Rincian prediksi model terhadap data uji digambarkan melalui confusion matrix pada Tabel 4.5.

**Tabel 4.5 Confusion Matrix Model SVM pada Data Uji**

| | Prediksi non-spam | Prediksi spam |
|---|---|---|
| **Aktual non-spam** | 863 (TN) | 9 (FP) |
| **Aktual spam** | 24 (FN) | 442 (TP) |

Dari total 1.338 data uji, model hanya melakukan 9 kesalahan false positive (komentar normal yang keliru ditandai spam) dan 24 kesalahan false negative (komentar spam yang lolos). Nilai presisi kelas spam yang tinggi (0,98) menunjukkan bahwa ketika model menandai sebuah komentar sebagai spam, keputusan tersebut hampir selalu benar.

> **[GAMBAR 4.9: Confusion Matrix Model SVM (visualisasi heatmap)]** — sumber: `reports/confusion_matrix_svm.png`

### 4.11.2 Validasi Silang (5-Fold Cross-Validation)

Untuk menguji konsistensi performa model terhadap variasi pembagian data, dilakukan 5-fold cross-validation pada keseluruhan dataset. Hasilnya menunjukkan rata-rata F1-macro sebesar **0,9741 dengan standar deviasi 0,0030 (±0,30%)**. Standar deviasi yang sangat kecil ini membuktikan bahwa performa model stabil dan tidak bergantung pada pembagian data tertentu. Skor F1-macro per fold disajikan pada Gambar 4.10.

> **[GAMBAR 4.10: Skor F1-macro per Fold pada 5-Fold Cross-Validation]** — sumber: `reports/cv_5fold_scores.png`

### 4.11.3 Pencarian Hiperparameter (GridSearchCV)

Pencarian nilai parameter regularisasi C dilakukan melalui GridSearchCV terhadap lima kandidat nilai (0,01, 0,1, 1, 10, dan 100) menggunakan 5-fold cross-validation. Nilai **C = 1** terpilih karena menghasilkan skor F1-macro rata-rata tertinggi. Hasil pencarian disajikan pada Gambar 4.11.

> **[GAMBAR 4.11: Hasil GridSearchCV Pencarian Nilai C Terbaik]** — sumber: `reports/gridsearch_c_sweep.png`

### 4.11.4 Perbandingan dengan Algoritma Baseline

Untuk membuktikan secara empiris bahwa pemilihan SVM bukan sekadar asumsi, model dibandingkan dengan dua algoritma baseline, yaitu Multinomial Naive Bayes dan Logistic Regression, menggunakan pembagian data dan parameter TF-IDF yang identik. Hasil perbandingan disajikan pada Tabel 4.6.

**Tabel 4.6 Perbandingan Performa SVM dengan Algoritma Baseline**

| Model | Accuracy | F1-macro |
|-------|----------|----------|
| **SVM (C=1, kernel linear)** | **97,53%** | **0,9726** |
| Logistic Regression | 97,09% | 0,9675 |
| Multinomial Naive Bayes | 93,95% | 0,9313 |

Hasil ini membuktikan bahwa SVM memberikan performa terbaik dibandingkan kedua algoritma baseline, sehingga pemilihannya sebagai model utama didukung oleh bukti kuantitatif.

### 4.11.5 Evaluasi pada Hard Test Set

Selain data uji reguler, model diuji terhadap hard test set yang berisi 135 komentar dengan tingkat ambiguitas tinggi. Perlu ditekankan bahwa hard test set ini **secara sengaja dirancang hanya berisi komentar non-spam** — yaitu komentar yang menyebut nama situs judi online dalam konteks kritik, cerita korban, atau diskusi anti-judol. Dengan demikian, dataset ini berfungsi sebagai pengujian ketahanan model terhadap false positive (uji presisi), bukan sebagai dataset berimbang. Oleh karena itu, metrik yang relevan pada pengujian ini adalah accuracy dan jumlah false positive, sementara recall dan F1-macro tidak digunakan karena ketiadaan kelas spam pada dataset.

Pada pengujian ini, model mencapai accuracy **98,52%** dengan hanya **2 false positive** dari 135 komentar. Hal ini membuktikan bahwa model mampu membedakan penyebutan nama situs judi dalam konteks non-promosi, sehingga tidak mudah keliru menyembunyikan komentar kritik atau diskusi yang sah.

### 4.11.6 Ablation Study Pendekatan Hibrida

Pengujian ini menjawab pertimbangan pada Sub-bab 4.5.6 mengenai pendekatan hibrida (penggabungan SVM dengan aturan berbasis kata kunci). Dilakukan perbandingan performa antara SVM murni dan SVM yang dikombinasikan dengan aturan hibrida (ENABLE_HYBRID_RULES). Hasilnya disajikan pada Tabel 4.7.

**Tabel 4.7 Perbandingan SVM Murni dengan SVM + Aturan Hibrida**

| Dataset | Mode | Accuracy | F1-macro | FP | FN |
|---------|------|----------|----------|----|----|
| Data Uji (n=1.338) | SVM murni | 97,53% | 0,9726 | 9 | 24 |
| Data Uji (n=1.338) | SVM + Hibrida | 90,21% | 0,8867 | 22 | 109 |
| Hard Test Set (n=135) | SVM murni | 98,52% | — | 2 | 0 |
| Hard Test Set (n=135) | SVM + Hibrida | 82,22% | — | 24 | 0 |

Hasil ablation study membuktikan bahwa penambahan aturan hibrida justru **menurunkan** performa secara signifikan, baik pada data uji (turun 7,32 poin persentase) maupun pada hard test set (turun 16,30 poin persentase). Penurunan ini terjadi karena aturan berbasis kata kunci memaksa komentar yang menyebut sinyal keras menjadi spam, sehingga meningkatkan false positive. Berdasarkan temuan ini, pendekatan hibrida **dinonaktifkan** (ENABLE_HYBRID_RULES = False) dan tidak digunakan pada sistem final.

### 4.11.7 Pengujian Pengaruh Stemming

Pengujian ini menjawab pertimbangan pada Sub-bab 4.5.5 mengenai penggunaan stemming. Eksperimen dilakukan dengan membandingkan performa model tanpa stemming dan dengan stemming Sastrawi menggunakan 5-fold cross-validation, lalu diuji signifikansinya melalui paired t-test. Hasilnya menunjukkan bahwa rata-rata F1-macro dengan stemming justru sedikit lebih rendah (selisih -0,0006), dan 4 dari 5 fold menunjukkan stemming berperforma lebih buruk. Uji statistik menghasilkan **p-value = 0,3575**, yang jauh di atas ambang signifikansi 0,05, sehingga perbedaan performa antara menggunakan dan tidak menggunakan stemming **tidak signifikan secara statistik**. Berdasarkan temuan ini, stemming **tidak diintegrasikan** ke dalam pipeline prapemrosesan produksi. Hasil pengujian disajikan pada Gambar 4.12.

> **[GAMBAR 4.12: Perbandingan F1-macro Tanpa Stemming vs Dengan Stemming (5-Fold CV)]** — sumber: `reports/experiment_stemming_cv.png`

### 4.11.8 Ringkasan Hasil Pengujian

Berdasarkan seluruh pengujian di atas, dapat disimpulkan bahwa model SVM dengan kernel linear dan parameter C=1 memberikan performa deteksi yang tinggi dan stabil (accuracy 97,53%, F1-macro 0,9726, CV 0,9741 ± 0,30%), mengungguli algoritma baseline, serta tangguh terhadap kasus ambigu pada hard test set (accuracy 98,52%). Dua eksperimen tambahan membuktikan bahwa baik pendekatan hibrida maupun stemming tidak memberikan manfaat, sehingga keduanya tidak digunakan pada sistem final. Keputusan-keputusan desain ini didasarkan pada bukti empiris, bukan asumsi.

## 4.12 Analisis Kelayakan Sistem

Analisis kelayakan sistem dilakukan untuk menilai apakah sistem usulan layak diterapkan, ditinjau dari tiga aspek sesuai pedoman, yaitu kelayakan teknologi, kelayakan operasional, dan kelayakan hukum.

### 4.12.1 Kelayakan Teknologi

Secara teknologi, sistem yang diusulkan layak untuk diterapkan karena seluruh komponennya dibangun menggunakan teknologi yang matang dan tersedia luas. Sisi klien menggunakan ekstensi Google Chrome berbasis Manifest V3 yang didukung oleh peramban Chrome versi 88 ke atas. Sisi peladen menggunakan bahasa Python dengan kerangka kerja FastAPI dan pustaka Scikit-learn, yang di-deploy pada Virtual Private Server (VPS) dengan spesifikasi minimum 2 vCPU, RAM 2 GB, dan penyimpanan 40 GB. Kebutuhan sumber daya yang relatif ringan ini menunjukkan bahwa sistem dapat dijalankan tanpa memerlukan infrastruktur komputasi berbiaya tinggi, sehingga secara teknologi sistem ini feasible untuk diimplementasikan dan dioperasikan secara berkelanjutan.

### 4.12.2 Kelayakan Operasional

Secara operasional, sistem dirancang agar mudah digunakan oleh pengguna awam tanpa memerlukan keahlian teknis khusus. Setelah ekstensi terpasang, sistem beroperasi secara otomatis di latar belakang setiap kali pengguna membuka halaman YouTube, tanpa memerlukan interaksi manual untuk setiap komentar. Pengguna hanya perlu melakukan pengaturan sederhana melalui antarmuka popup yang intuitif, seperti memilih mode penyembunyian dan menyesuaikan tingkat sensitivitas deteksi. Dengan tingkat keterlibatan pengguna yang minimal dan antarmuka yang sederhana, sistem ini layak dari sisi operasional.

### 4.12.3 Kelayakan Hukum

Secara hukum, sistem yang diusulkan telah dirancang untuk mematuhi ketentuan yang berlaku. Pengumpulan data komentar dilakukan melalui YouTube Data API v3, yaitu antarmuka resmi yang disediakan YouTube, sehingga pengambilan data tidak melanggar ketentuan layanan (terms of service) platform. Sistem juga tidak melakukan modifikasi terhadap basis data atau konten milik YouTube; penyembunyian komentar hanya terjadi secara lokal pada tampilan peramban pengguna (sisi klien) tanpa mengubah data di server YouTube. Selain itu, tujuan sistem ini, yaitu menyaring promosi judi online, sejalan dengan upaya penegakan hukum di Indonesia yang melarang segala bentuk promosi dan praktik perjudian daring. Dengan demikian, sistem ini layak secara hukum untuk diterapkan.
