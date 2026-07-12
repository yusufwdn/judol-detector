# ABSTRAK (Draft)

> **Catatan penggunaan:**
> - Format & struktur ini mengikuti pedoman resmi (Lampiran L-15/L-16): judul kapital, nama pembimbing + nama mahasiswa (NIM), "Skripsi, Program Studi Teknik Informatika, [tahun]", Kata Kunci (maks 5), jumlah halaman + lampiran, isi 4 paragraf wajib (latar belakang → metode & rumusan masalah → hasil → kesimpulan & saran), rentang tahun Daftar Pustaka.
> - Diketik **1 spasi**, 1 halaman, **200-250 kata** — draf ini sudah dihitung agar masuk rentang tersebut (lihat catatan jumlah kata di bawah).
> - ⚠️ **Nama Pembimbing II ada 2 ejaan berbeda di draft**: "Septiana Ningtyas" (Lembar Persetujuan, hal. ii) vs "Septiani Ningtyas" (Kata Pengantar, hal. vi). Draft ini pakai "Septiana" — **WAJIB dikonfirmasi mana yang benar** sebelum final, lalu samakan di SEMUA halaman (sampul, lembar persetujuan, kata pengantar, abstrak).
> - ⚠️ **"(xiii+XX halaman+YY lampiran)"** — jumlah halaman belum bisa dipastikan karena dokumen masih direvisi (BAB V baru ditambahkan, dll). Isi placeholder `XX` dan `YY` setelah dokumen final dan sudah di-page-number ulang.
> - Istilah asing **belum di-italic** — terapkan manual di Word.

---

## ABSTRAK

**PERANCANGAN DAN IMPLEMENTASI ALGORITMA SUPPORT VECTOR MACHINE (SVM) DENGAN TEKNIK STRING NORMALIZATION UNTUK DETEKSI KOMENTAR SPAM JUDI ONLINE PADA YOUTUBE BERBASIS CHROME EXTENSION**

Dr. Usanto S., S.Kom., M.Kom., Septiana Ningtyas, S.Kom., M.Kom., Yusuf Wandana (221232017)
Skripsi, Program Studi Teknik Informatika, 2026
Kata Kunci: Support Vector Machine, String Normalization, spam judi online, Chrome Extension, YouTube
(xiii+XX halaman+YY lampiran)

Penyebaran promosi judi online melalui kolom komentar YouTube telah menjadi ancaman siber yang meresahkan di Indonesia. Penyebar spam memanfaatkan teknik penyamaran teks (obfuscation), seperti substitusi karakter Unicode, penyisipan tanda diakritik, dan penggantian huruf dengan angka, sehingga mampu meloloskan diri dari sistem filtrasi berbasis kata kunci statis yang digunakan YouTube saat ini.

Penelitian ini merancang dan mengimplementasikan sebuah ekstensi Google Chrome berbasis Manifest V3 yang mengombinasikan teknik String Normalization dengan algoritma Support Vector Machine (SVM) untuk mendeteksi dan menyembunyikan komentar spam tersebut secara real-time di sisi klien. Data komentar dikumpulkan melalui YouTube Data API v3, diberi label, kemudian diproses melalui pipeline normalisasi teks dan diekstraksi fiturnya menggunakan Term Frequency-Inverse Document Frequency (TF-IDF) sebelum diklasifikasikan oleh model SVM berkernel linear.

Hasil pengujian pada 1.338 data uji menunjukkan model mencapai accuracy 97,53% dan F1-macro 0,9726, mengungguli algoritma pembanding Logistic Regression (97,09%) dan Multinomial Naive Bayes (93,95%). Validasi 5-fold cross-validation menghasilkan F1-macro rata-rata 0,9741 dengan standar deviasi ±0,30%, menunjukkan performa yang konsisten. Pada hard test set berisi 135 komentar ambigu, model mencapai accuracy 98,52% dengan hanya 2 false positive. Eksperimen tambahan membuktikan bahwa pendekatan hibrida berbasis kata kunci dan stemming Sastrawi tidak meningkatkan performa, sehingga tidak digunakan pada sistem final.

Penelitian ini menyimpulkan bahwa kombinasi String Normalization dan SVM efektif menutupi celah deteksi pada sistem filtrasi konvensional YouTube. Saran bagi penelitian selanjutnya meliputi pembaruan dataset secara berkala, pengembangan fitur rekayasa tambahan, serta pengujian pada platform media sosial lain.

Daftar Pustaka (2018-2026)
