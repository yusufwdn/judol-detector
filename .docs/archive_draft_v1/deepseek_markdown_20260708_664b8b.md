# LOG ANALISIS SKRIPSI – 8 JULI 2026

**Proyek:** Deteksi Komentar Spam Judi Online (SVM + String Normalization + Chrome Extension)
**Mahasiswa:** Yusuf Wandana (221232017)
**Tujuan Log:** Merekam temuan kesenjangan antara Draft Skripsi vs Implementasi Kode (Repomix), serta memberikan panduan prioritas perbaikan sebelum sidang.

---

## 1. RINGKASAN EKSEKUTIF (BACA INI DULU)

Secara substansi keilmuan, draft skripsimu sudah **sangat baik**. Alur dari latar belakang, rumusan masalah, teori, hingga metodologi mengalir logis. Kamu paham betul bidang yang kamu tekuni (NLP, SVM, dan arsitektur browser extension).

**TAPI, ada 3 masalah besar yang harus kamu kejar sebelum sidang:**

1.  **BAB 4 Masih Setengah Jadi (Fatal):** Sub-bab 4.9 (Sequence Diagram), 4.10 (Rancangan Tampilan), 4.11 (Pengujian Sistem), dan 4.12 (Analisis Kelayakan) masih **kosong**. Ini adalah bagian inti dari skripsi teknik, dosen pasti akan menyorotnya.
2.  **Ketidaksesuaian Klaim vs Kode:** Ada beberapa pernyataan di BAB 2 dan 4 yang tidak sesuai dengan implementasi aktual di file `src/` dan `reports/` (contoh: eksperimen stemming dan hybrid rules).
3.  **11 Poin Revisi Dosen (Format & Administratif):** Sebagian besar poin revisi dari dosen pembimbing (terkait italic, penomoran list, kesimpulan teori, dll.) belum kamu penuhi.

---

## 2. KETIDAKSESUAIAN DRAFT vs KODE (WAJIB DIPERBAIKI)

Berikut 4 poin kritis di mana apa yang kamu tulis di skripsi **berbeda** dengan apa yang ada di kode (Repomix) atau hasil eksperimen.

### ❌ 2.1. Eksperimen Stemming (BAB 4.5.5)
- **Klaim di Draft:** "Hasil eksperimen menunjukkan peningkatan F1-macro yang tidak signifikan sebesar +0,0002."
- **Fakta di Kode (`experiment_stemming.py` & `reports/experiment_stemming_cv.png`):**
    - Eksperimen terbaru (dataset 6690 baris) justru menunjukkan rata-rata stemming **sedikit lebih buruk** (delta **-0.0006**) dibandingkan tanpa stemming.
    - Hasil uji statistik (*paired t-test*) menunjukkan **p-value = 0.3575**, yang artinya perbedaan performa antara pakai stemming dan tidak pakai stemming **tidak signifikan secara statistik** (jauh di atas ambang 0.05). 4 dari 5 fold cross-validation menunjukkan stemming justru kalah.
- **Harus Diperbaiki Menjadi:** Tulis ulang paragraf tersebut dengan menyebutkan bahwa setelah dilakukan verifikasi lanjutan dengan 5-fold cross-validation dan uji statistik, stemming terbukti tidak memberikan peningkatan yang konsisten (bahkan cenderung menurunkan performa tipis), sehingga keputusan untuk **tidak** mengintegrasikan stemming ke produksi tetap dipertahankan. (Lihat contoh kalimat di bagian 6).

### ❌ 2.2. Pendekatan Hibrida (BAB 4.5.6 & 4.11)
- **Klaim di Draft:** "Hasil pengujian dan keputusan akhir mengenai pendekatan ini dibahas pada sub-bab pengujian sistem di bab ini."
- **Fakta di Kode (`server.py`, `evaluate_hybrid_ablation.py`, `reports/hybrid_ablation.txt`):**
    - Di kode, hybrid rules sudah **DINONAKTIFKAN** (`ENABLE_HYBRID_RULES = False`).
    - Ablation study membuktikan hybrid rules **MENURUNKAN** akurasi 6-13 poin persentase. Di train-test split, akurasi turun dari 97.53% (SVM murni) menjadi 90.21% (SVM+Hybrid). Di hard test set, turun dari 98.52% menjadi 82.22%.
- **Harus Diperbaiki:** Kamu harus mengisi BAB 4.11 dengan data empiris ini dan menyimpulkan bahwa hybrid rules akhirnya tidak dipakai karena merugikan performa setelah dataset diperbesar.

### ❌ 2.3. BAB 4.11 (Pengujian Sistem) Kosong
- **Klaim di Draft:** Tidak ada isi.
- **Fakta di Kode (`train.py`, `compare_baselines.py`, `reports/`):**
    - Semua angka evaluasi sudah tersedia di folder `reports/` dan log `DATASET_LOG.md`.
- **Harus Diperbaiki:** Isi BAB 4.11 dengan data riil ini (lihat template di bagian 3.3).

### ❌ 2.4. Penjelasan Preprocessing Kurang Detail (BAB 2.4)
- **Klaim di Draft:** Menjelaskan String Normalization secara umum.
- **Fakta di Kode (`preprocessing.py`):** Ada 3 sub-langkah krusial yang lu lewatkan di penjelasan teoritis, padahal ini adalah kontribusi teknis utama:
    1.  **Step 2b (Strip Combining Diacritics):** Menangani trik `P͟U͟L͟A͟U͟W͟I͟N͟` (karakter garis bawah di bawah huruf).
    2.  **Step 2c (Unwrap Bracketed Chars):** Menangani trik `[P][U][L][A][U][7][7][7]`.
    3.  **Step 5b-i (Leet Speak Normalization):** Menangani trik `H0KI777` (angka 0 mengganti huruf O).
    4.  **Step 5b (Brand Canonicalization):** Mengubah `keju4d` menjadi token universal `judolbrand` agar model bisa generalisasi ke brand baru tanpa harus menghafal satu per satu.
- **Harus Diperbaiki:** Tambahkan penjelasan keempat sub-langkah ini di BAB 2.4 untuk memperkuat landasan teori.

---

## 3. TEMPLATE PENGISIAN BAB 4 (4.9 - 4.12)

Berikut adalah draft narasi yang bisa langsung kamu kembangkan dan masukkan ke BAB 4 untuk mengisi bagian yang kosong.

### 3.1. Sub-bab 4.9 Sequence Diagram
> *"Sequence diagram pada Gambar 4.X menggambarkan interaksi antar komponen sistem berdasarkan urutan waktu. Proses dimulai dari inisiasi (health check), konfigurasi threshold oleh pengguna melalui popup, hingga deteksi dan klasifikasi komentar secara real-time. Diagram ini memperlihatkan alur komunikasi asynchronous antara Pengguna, Popup UI, Content Script, Server API, dan DOM YouTube, serta dilengkapi dengan mekanisme pelaporan kesalahan (dev mode) untuk keperluan perbaikan dataset."*

### 3.2. Sub-bab 4.10 Rancangan Tampilan
> *"Rancangan antarmuka terdiri dari dua komponen. **Pertama**, popup extension (Gambar 4.X) menampilkan status server, statistik komentar (dipindai vs disembunyikan), slider confidence threshold (50-95%), serta toggle mode penyembunyian (Redupkan atau Hilangkan). **Kedua**, pada halaman YouTube, komentar yang terdeteksi spam akan memiliki efek visual berupa opacity 15% dan badge merah yang menampilkan persentase keyakinan model (mode Redupkan), atau hilang sepenuhnya dari tampilan (mode Hilangkan). Pengguna dapat mengklik badge untuk memunculkan kembali komentar yang diredupkan."*

### 3.3. Sub-bab 4.11 Pengujian Sistem (Isi dengan Angka Ini)
> *"Pengujian sistem dilakukan pada dataset berjumlah 6.690 komentar (2.332 spam, 4.358 non-spam) dengan pembagian 80:20. Model SVM mencapai akurasi **97.53%** dan F1-macro **0.9726** pada data uji. **5-fold cross-validation** menghasilkan rata-rata F1-macro **97.41% ± 0.21%**, menunjukkan konsistensi model terhadap variasi data. **Hyperparameter tuning** melalui GridSearchCV memilih nilai C=1 dengan skor F1-macro tertinggi. Pada **hard test set** yang berisi 135 kasus ambigu (komentar kritik/diskusi yang menyebut brand judol), model mencapai akurasi **98.52%** dengan hanya 2 false positive, membuktikan ketahanan model terhadap kasus sulit. Perbandingan dengan algoritma baseline menunjukkan SVM (97.53%) mengungguli Logistic Regression (97.09%) dan Naive Bayes (93.95%). Eksperimen tambahan berupa **ablation study hybrid rules** membuktikan bahwa penambahan aturan berbasis kata kunci justru menurunkan akurasi 6-13 poin, sehingga pendekatan tersebut tidak digunakan. Eksperimen stemming dengan 5-fold cross-validation menghasilkan p-value 0.3575 (tidak signifikan), sehingga stemming juga tidak diintegrasikan ke dalam pipeline produksi."*

### 3.4. Sub-bab 4.12 Analisis Kelayakan Sistem (PIECES)
> *"Menggunakan kerangka PIECES yang sama dengan analisis sistem berjalan (BAB 3), sistem usulan dinilai layak dari berbagai aspek. Dari sisi **Performance**, sistem mampu memproses 50 komentar per batch request dengan latensi rendah. Dari sisi **Information**, akurasi 97.53% menjamin kualitas informasi yang disajikan. Dari sisi **Economics**, sistem gratis dan mengurangi biaya moderasi manual. Dari sisi **Control**, pipeline preprocessing 7+3 langkah secara efektif menangkal berbagai teknik obfuscation. Dari sisi **Efficiency**, otomatisasi deteksi real-time jauh lebih efisien dibanding metode manual. Dari sisi **Service**, antarmuka popup yang intuitif dan opsi mode penyembunyian memberikan pengalaman pengguna yang optimal."*

---

## 4. STATUS 11 POIN REVISI DOSEN (CEKLIST)

| No | Perintah Dosen | Status Saat Ini | Solusi/Tindakan |
| :--- | :--- | :--- | :--- |
| **1** | Tujuan dibuat satu paragraf mengikuti rumusan masalah | ❌ **BELUM** | Gabungkan 3 poin bernomor di BAB 1.3.1 menjadi 1 paragraf naratif. (Lihat contoh di bagian 6). |
| **2** | Istilah asing & brand harus *italic* (termasuk judul) | ⚠️ **SEBAGIAN** | Cek seluruh dokumen. Pastikan *FastAPI*, *REST API*, *DOM*, *CSS*, *Support Vector Machine*, *YouTube*, *Chrome Extension* ditulis miring. |
| **3** | Heading 1 (BAB) harus kapital penuh | ✅ **OK** | Judul BAB sudah ALL CAPS (BAB I PENDAHULUAN). |
| **4** | Setiap teori dikasih kesimpulan | ❌ **BELUM** | Di setiap sub-bab teori (2.1, 2.2, 2.5, 2.6, dst.), tambahkan paragraf terakhir berisi "Berdasarkan uraian di atas, dapat disimpulkan bahwa..." |
| **5** | List jangan pake poin, pake angka/huruf | ❌ **BELUM** | Ganti semua simbol bullet (`-`, `•`) di seluruh dokumen menjadi angka (1), 2), atau huruf a), b). |
| **6** | BAB 3 salah judul | ❌ **SALAH** | Ganti judul "OBJEK PENELITIAN" menjadi **"SISTEM BERJALAN DAN OBJEK PENELITIAN"** (sesuai pedoman hal. 14). |
| **7** | Struktur organisasi YouTube ditambahkan | ⚠️ **KURANG** | Di BAB 3.1.2, tambahkan deskripsi tentang struktur data komentar YouTube atau arsitektur DOM halaman YouTube sebagai objek penelitian. |
| **8** | Setiap gambar/tabel ada kalimat pengantar | ⚠️ **PERLU DICEK** | Pastikan tidak ada gambar/tabel yang muncul langsung setelah sub-judul tanpa ada kalimat "Berikut merupakan..." atau "Pada Gambar X disajikan...". |
| **9** | BAB 4 sub bab pertama harus ada *pieces* (solusi) | ❌ **BELUM** | Di awal BAB 4 (setelah atau di dalam 4.1), tambahkan paragraf yang menjelaskan solusi yang ditawarkan sistem secara global sebelum masuk ke detail kebutuhan. |
| **10** | Diagram dibuat hitam-putih | ⚠️ **BELUM DICEK** | Pastikan semua diagram (flowchart, use case, dll.) dicetak dalam mode grayscale/putih-hitam, bukan berwarna. |
| **11** | Use case narasinya harus ada | ⚠️ **KURANG** | Kembangkan narasi use case. Format yang diharapkan: *"Use Case: Menyaring Komentar Spam. Actor: Pengguna. Precondition: Ekstensi terinstall. Flow: 1. Pengguna membuka video... 2. Sistem mendeteksi komentar..."* |

---

## 5. PRIORITAS PENGERJAAN

Agar tidak kewalahan, kerjakan secara bertahap:

- **PRIORITAS 1 (HARUS SELESAI):**
    - [ ] Isi BAB 4.9, 4.10, 4.11, 4.12 (pakai template di bagian 3).
    - [ ] Perbaiki Poin 1 (Tujuan jadi 1 paragraf).
    - [ ] Perbaiki Poin 4 (Tambahkan kesimpulan teori).
    - [ ] Perbaiki Poin 6 (Judul BAB 3).
    - [ ] Perbaiki Poin 9 (Tambahkan *pieces* di BAB 4).

- **PRIORITAS 2 (SEGERA SETELAH PRIORITAS 1):**
    - [ ] Perbaiki Poin 5 (Ganti bullet list).
    - [ ] Perbaiki Poin 11 (Narasi Use Case).
    - [ ] Perbaiki Poin 8 (Kalimat pengantar gambar/tabel).

- **PRIORITAS 3 (PENYEMPURNAAN):**
    - [ ] Perbaiki Poin 2 (Cek *italic*).
    - [ ] Perbaiki Poin 7 (Struktur YouTube).
    - [ ] Perbaiki Poin 10 (Warna diagram).

---

## 6. CONTOH KALIMAT SIAP PAKAI (COPY-PASTE KE DRAFT)

### Contoh Perbaikan Poin 1 (Tujuan Penelitian)
> *"Sesuai dengan rumusan masalah yang telah ditetapkan, tujuan utama dari penelitian ini adalah membangun sebuah sistem filtrasi cerdas berbasis algoritma Support Vector Machine (SVM) dan teknik String Normalization guna mendeteksi serta menyembunyikan komentar spam promosi judi online di platform YouTube. Sistem ini diimplementasikan sebagai ekstensi Google Chrome berbasis Manifest V3 yang beroperasi secara real-time di sisi klien, dengan menerapkan String Normalization sebagai tahap prapemrosesan awal untuk membersihkan karakter manipulatif (obfuscation) seperti homoglyphs dan leet speak sebelum diklasifikasikan oleh SVM. Performa sistem kemudian diukur, dianalisis, dan divalidasi menggunakan metrik akurasi, presisi, recall, dan F1-Score untuk memastikan efektivitas deteksi."*

### Contoh Perbaikan Poin 4 (Kesimpulan Teori TF-IDF)
> *"Berdasarkan uraian di atas, dapat disimpulkan bahwa TF-IDF merupakan metode ekstraksi fitur yang efektif untuk klasifikasi teks karena mampu memberikan bobot tinggi pada kata-kata yang spesifik dan diskriminatif, serta bobot rendah pada kata-kata umum yang tidak informatif. Penerapan TF-IDF dengan parameter max_features=10000, ngram_range=(1,2), min_df=2, dan sublinear_tf=True dalam penelitian ini bertujuan untuk menghasilkan representasi numerik yang optimal bagi algoritma SVM."*

### Contoh Perbaikan Poin 4 (Kesimpulan Teori SVM)
> *"Berdasarkan uraian di atas, algoritma SVM merupakan metode klasifikasi yang andal untuk menangani data teks berdimensi tinggi. Kemampuannya dalam menemukan hyperplane optimal dengan margin terlebar menjadikannya solusi yang relevan untuk diimplementasikan dalam sistem deteksi spam, terutama ketika dikombinasikan dengan teknik prapemrosesan dan ekstraksi fitur yang kuat. Penggunaan kernel linear dipilih karena data TF-IDF sudah berada dalam ruang fitur berdimensi tinggi yang secara umum dapat dipisahkan secara linear."*

### Contoh Perbaikan Poin 2 (Penulisan Italic)
- **Salah:** "Model ini menggunakan Support Vector Machine dan di-deploy menggunakan FastAPI."
- **Benar:** "Model ini menggunakan *Support Vector Machine* dan di-deploy menggunakan *FastAPI*."

---

## 7. BAGAIMANA MENGGUNAKAN FILE INI UNTUK SESI SELANJUTNYA

Kalau nanti kamu mau lanjut konsultasi ke Claude (atau ke gua lagi), cukup **copy-paste seluruh isi file ini** sebagai pesan pembuka, lalu tulis pertanyaan spesifikmu, misalnya:

> *"Ini adalah log analisis terakhir. Saat ini saya sudah menyelesaikan Prioritas 1 dan 2, tapi saya kesulitan di bagian X. Tolong bantu saya tuliskan paragraf untuk Y..."*

Dengan begitu, AI yang kamu ajak bicara langsung paham konteks proyek, apa yang sudah kamu kerjakan, dan apa yang masih kurang, tanpa harus kamu jelaskan dari awal lagi.

---

**Semangat revisinya, Yusuf! Fokus ke BAB 4 dulu, sisanya bisa kejar. Gaskeun! 🚀**