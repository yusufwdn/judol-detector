# BAB V — KESIMPULAN DAN SARAN (Draft)

> **Catatan penggunaan:**
> - BAB V ini sebelumnya TIDAK ADA sama sekali di draft (bahkan di Daftar Isi). Ini tulisan baru, bukan revisi dari teks lama.
> - Seluruh angka bersumber dari 4.11 yang sudah diverifikasi terhadap kode (lihat `BAB_4_LANJUTAN.md`) — bukan diambil ulang dari klaim DeepSeek yang belum dicek.
> - Per pedoman (BAB III bagian Bagian Utama poin c): Kesimpulan = ringkasan hasil, **tidak boleh memuat temuan baru** yang tidak dibahas di bab sebelumnya. Saran = hal yang belum ditempuh, layak dilaksanakan ke depan.
> - **Italic istilah asing BELUM diterapkan** — tahap manual di Word.

---

## BAB V KESIMPULAN DAN SARAN

## 5.1 Kesimpulan

Sistem berjalan pada YouTube terbukti lemah menangani komentar promosi judi online yang disamarkan melalui teknik obfuscation (homoglyph, diakritik, leet speak), karena hanya mengandalkan pencocokan kata kunci statis — kelemahan ini teridentifikasi pada aspek Kendali dan Efisiensi melalui analisis PIECES di Bab III dan berdampak berantai ke aspek Kinerja, Informasi, Ekonomi, dan Pelayanan. Untuk menjawabnya, penelitian ini merancang ekstensi Google Chrome berbasis Manifest V3 yang mengombinasikan String Normalization dengan algoritma SVM. Berdasarkan hasil pengujian, dapat disimpulkan:

1. Sistem beroperasi real-time di sisi klien tanpa membebani server YouTube maupun bergantung pada pembaruan kamus kata kunci manual, langsung menjawab kelemahan Kendali dan Efisiensi pada sistem berjalan.

2. String Normalization terbukti efektif menangani berbagai teknik obfuscation yang sebelumnya lolos dari filter YouTube, menjadi fondasi bagi model klasifikasi mengenali pola spam yang tersamarkan.

3. Model SVM kernel linear (C=1) mencapai accuracy 97,53% dan F1-macro 0,9726 pada data uji, dengan 5-fold cross-validation 0,9741±0,30% (stabil) dan accuracy 98,52% pada hard test set (135 kasus ambigu, 2 false positive) — mengungguli Logistic Regression (97,09%) dan Naive Bayes (93,95%), membuktikan pemilihan SVM didukung bukti empiris.

4. Dua eksperimen tambahan — ablation study aturan hibrida (turun 7,32-16,30 poin persentase) dan pengujian stemming Sastrawi (p-value 0,3575, tidak signifikan) — membuktikan penambahan kompleksitas pipeline tidak selalu meningkatkan performa, sehingga keduanya tidak digunakan pada sistem final.

5. Mekanisme confidence threshold (50%-95%, default 75%, dikalibrasi via Platt Scaling) dan dua mode penyembunyian (Redupkan/Hilangkan) memberi kendali kepada pengguna sesuai preferensi masing-masing terhadap risiko false positive dan false negative.

6. Sistem layak diterapkan dari aspek teknologi, operasional, maupun hukum, karena pengumpulan data dilakukan melalui YouTube Data API v3 resmi tanpa memodifikasi data milik platform.

Secara keseluruhan, sistem yang diusulkan berhasil menjawab kelemahan Kendali dan Efisiensi pada sistem berjalan, sekaligus berdampak positif pada aspek Kinerja, Informasi, Ekonomi, dan Pelayanan bagi pengguna YouTube.

## 5.2 Saran

Berdasarkan keterbatasan yang ditemukan selama penelitian, berikut adalah saran untuk pengembangan lanjutan:

1. **Pembaruan Dataset.** Dataset bersifat statis, sementara pola spam terus berkembang. Disarankan mekanisme re-training berkala memanfaatkan data dari endpoint /report.

2. **Fitur Rekayasa Tambahan.** Model berbasis TF-IDF masih rentan pada kasus ambigu (komentar korban/kritik yang menyebut brand). Disarankan eksplorasi fitur tambahan seperti rasio simbol atau embedding kontekstual.

3. **Evaluasi pada Platform Lain.** Penelitian ini terbatas pada YouTube berbahasa Indonesia. Disarankan pengujian dan adaptasi pipeline pada platform seperti Instagram atau TikTok.

4. **Approval Queue untuk Endpoint /report.** Endpoint ini masih development-only tanpa validasi. Disarankan penambahan mekanisme antrean persetujuan sebelum data koreksi digunakan untuk pelatihan ulang.

5. **Perbandingan dengan Deep Learning.** Penelitian ini membatasi diri pada Machine Learning konvensional demi efisiensi real-time. Disarankan eksplorasi model seperti LSTM atau transformer beserta kajian trade-off akurasi versus latensi.

6. **Ketahanan terhadap Perubahan Struktur DOM.** Sistem bergantung pada struktur DOM YouTube yang dapat berubah sewaktu-waktu. Disarankan mekanisme pemantauan otomatis terhadap perubahan struktur halaman.
