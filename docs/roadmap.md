# Status dan Rencana

## Yang sudah selesai

### Pengumpulan dan kualitas data

- Pengambilan komentar lewat YouTube Data API v3 dengan pemberian skor
  heuristik awal
- Penyaringan dua tahap di `prepare_dataset.py`, menggabungkan ambang skor
  dengan penyelamatan berbasis pola nama situs
- Koreksi label yang bertahan lintas rebuild lewat `manual_overrides.csv`
- Dataset 6.690 komentar dari beragam jenis video: gaming, berita, musik,
  podcast, dan edukasi
- Kumpulan 135 kasus ambigu yang terpisah dari data latih
- Penelusuran asal tiap baris lewat kolom `source`
- Perbaikan penyebab kontaminasi di scraper, dengan menjalankan normalisasi
  homoglif dan leet speak sebelum sinyal regex diperiksa
- Penyimpanan komentar berskor 10 sampai 29 yang sebelumnya dibuang tanpa
  jejak

### Pemrosesan teks

- Normalisasi tujuh tahap, dipakai bersama oleh pelatihan dan prediksi
- Penanganan penyamaran Unicode: karakter tak terlihat, diakritik penggabung,
  karakter dalam kurung, dan homoglif Sirilik, Yunani, serta Thai
- Normalisasi leet speak
- Kanonikalisasi nama situs judi menjadi satu token universal
- Emoji diubah menjadi token teks, bukan dibuang

### Model

- Pipeline TF-IDF dan SVM kernel linear, tersimpan sebagai satu artefak
- Pemilihan nilai C secara empiris lewat `GridSearchCV`
- Cross-validation 5-fold yang berjalan otomatis setiap pelatihan
- Perbandingan dengan Logistic Regression dan Naive Bayes
- Confusion matrix tersimpan otomatis untuk setiap model
- Arsip checkpoint model per versi dataset

### Eksperimen

- Uji pengaruh stemming dengan cross-validation berpasangan dan paired t-test
- Uji konfigurasi n-gram dan `max_features`
- Ablasi aturan heuristik tambahan pada dua kumpulan data uji
- Inspeksi bobot fitur

### Server

- Empat endpoint: prediksi tunggal, prediksi kelompok, pemeriksaan kesehatan,
  dan pelaporan koreksi
- Validasi masukan lewat Pydantic
- Pembatasan CORS ke origin yang spesifik
- Endpoint pelaporan dilindungi token, dan nonaktif secara bawaan jika token
  tidak dikonfigurasi
- Deployment ke VPS dengan systemd, Nginx, dan sertifikat TLS

### Ekstensi

- Manifest V3 dengan izin minimal
- Pemrosesan berkelompok, maksimal 50 komentar per permintaan
- `MutationObserver` untuk komentar yang muncul saat menggulir
- Dua mode penyembunyian: redupkan dan hilangkan
- Ambang kepercayaan yang bisa diatur, tersimpan dan langsung berlaku
- ID ekstensi yang dipatok agar CORS tetap berfungsi di komputer mana pun
- Penanganan server mati, agar pemindaian tidak terus mencoba menghubungi
  server yang tidak merespons

## Yang bisa dikembangkan

### Menjalankan model di peramban

Mengonversi model ke ONNX Runtime Web atau TensorFlow.js supaya prediksi
berjalan langsung di peramban tanpa server Python.

Ini perbaikan yang paling berdampak. Ketergantungan pada server adalah
keterbatasan terbesar sistem saat ini: menambah latensi, membuat ekstensi
tidak berfungsi saat offline, dan memindahkan teks komentar ke pihak ketiga.
Pipeline TF-IDF dan SVM linear relatif mudah dikonversi karena pada dasarnya
hanya perkalian matriks jarang.

Yang perlu diselesaikan adalah menerjemahkan seluruh tahap normalisasi ke
JavaScript dengan hasil yang identik. Kesulitannya bukan pada modelnya,
melainkan pada memastikan penanganan Unicode di JavaScript persis sama dengan
Python.

### Memahami konteks kalimat

Dua false positive yang tersisa keduanya adalah komentar yang melaporkan situs
judi, bukan mempromosikannya. Model linear menjumlahkan bobot per token tanpa
memahami struktur kalimat, sehingga kata yang menandakan niat melaporkan bisa
kalah oleh kemunculan nama situs berkali-kali.

Model yang memperhatikan urutan kata, misalnya berbasis transformer seperti
IndoBERT, kemungkinan menangani ini lebih baik. Konsekuensinya latensi dan
ukuran model bertambah, sehingga baru masuk akal jika digabungkan dengan
perbaikan sebelumnya atau dijalankan sebagai tahap kedua hanya untuk kasus
yang skornya di sekitar ambang.

### Meninjau komentar zona abai

Komentar berskor 10 sampai 29 kini disimpan tetapi belum pernah ditinjau
manual. Rentang ini adalah kandidat terbaik untuk menambah contoh pola
"mengkritik sambil menyebut nama situs", yaitu pola yang paling sering salah
diklasifikasi.

### Dukungan platform lain

Instagram dan TikTok punya masalah yang sama. Model dan servernya bisa dipakai
ulang apa adanya; yang perlu ditulis hanya content script baru dengan selektor
DOM yang sesuai.

### Stopword khusus domain

Sapaan seperti `kak`, `bang`, dan `min` sempat dipertimbangkan untuk
ditambahkan ke daftar stopword. Prioritasnya rendah, karena inspeksi bobot
fitur menunjukkan `bang` dan `dok` justru penanda non-spam yang kuat dengan
bobot negatif 1,55 dan 1,39. Membuangnya kemungkinan menurunkan performa, jadi
perlu diukur dulu sebelum diterapkan.

### Pembaruan model berkala

Nama situs judi berganti cepat. Kanonikalisasi pola menangani sebagian besar
kasus, tetapi nama yang tidak mengikuti pola tetap lolos. Alur pengumpulan dan
pelatihan ulang secara berkala akan membuat model tidak cepat usang.

### Paket server mandiri

Mengemas server menjadi berkas executable agar bisa dijalankan tanpa memasang
Python. Relevan hanya jika model tetap berjalan di server.
