# BAB III — OBJEK PENELITIAN (Draft Lengkap Revisi)

> **Catatan penggunaan:**
> - Teks asli dipertahankan; yang **BARU** ditandai jelas. Perubahan: (a) tambah 3.1.3 Profil Perusahaan YouTube + 3.1.4 Struktur Organisasi YouTube (permintaan dosen), (b) kalimat pengantar sebelum Gambar & Tabel (dosen poin 8), (c) penomoran gambar disesuaikan.
> - **Italic istilah asing BELUM diterapkan** — tahap manual di Word (poin 9).
> - ⚠️ **WAJIB VERIFIKASI + SITASI**: semua fakta tentang perusahaan YouTube (tahun, nilai akuisisi, nama CEO) ditandai `[VERIFIKASI]`. Cek ke sumber resmi/kredibel sebelum final, jangan asal percaya draft ini. Per pedoman, sitasi website sebaiknya dari sumber berbasis keilmuan.
> - ⚠️ **PENOMORAN GAMBAR BERUBAH**: karena ada bagan struktur organisasi baru, urutannya jadi — Gambar 3.1 = Struktur Organisasi YouTube (BARU), Gambar 3.2 = Flowchart Sistem Berjalan (dulu 3.1). Update juga Daftar Gambar & referensi silangnya.

---

## BAB III OBJEK PENELITIAN

## 3.1 Tinjauan Umum Objek Penelitian

Objek penelitian pada skripsi ini difokuskan pada pengembangan perangkat lunak berbasis klien (client-side), yaitu berupa ekstensi peramban web (browser extension) Google Chrome. Perangkat lunak ini dirancang secara khusus untuk melakukan deteksi dan penyembunyian secara instan terhadap komentar yang bermuatan promosi judi online pada antarmuka platform YouTube. Pendekatan ini dipilih untuk memberikan lapisan keamanan tambahan yang independen bagi pengguna, tanpa perlu menunggu intervensi dari administrator platform utama.

### 3.1.1 Behaviour (Tingkah Laku) Objek Penelitian

Tingkah laku (behaviour) dari objek penelitian ini bertumpu pada interaksi langsung dan dinamis antara ekstensi peramban dengan Document Object Model (DOM) pada halaman web YouTube yang sedang dimuat oleh pengguna. Perangkat lunak ini beroperasi secara asynchronous di latar belakang untuk meminimalisasi beban komputasi peramban. Secara teknis, alur tingkah laku sistem dapat diuraikan melalui tahapan operasional berikut:

1. **Inisiasi dan Pemantauan Elemen (DOM Observation)**
   Ekstensi memanfaatkan antarmuka MutationObserver bawaan peramban untuk memantau setiap perubahan pada struktur DOM. Saat pengguna menggulir halaman dan komentar baru dimuat secara dinamis oleh YouTube (melalui AJAX/Fetch), ekstensi secara otomatis mendeteksi node teks baru tersebut tanpa perlu memuat ulang halaman.
2. **Ekstraksi dan Prapemrosesan Klien (String Normalization)**
   Teks komentar yang berhasil ditangkap kemudian diekstrak dan langsung diproses secara lokal. Modul ini menjalankan algoritma String Normalization menggunakan reguler ekspresi (RegEx) untuk membersihkan karakter pengganggu, serta memetakan dan mengonversi variasi karakter Unicode khusus (seperti huruf Cyrillic atau simbol yang menyerupai alfabet Latin) kembali menjadi format teks ASCII standar.
3. **Transmisi Data Asynchronous**
   Teks yang telah dinormalisasi dikemas dalam format JavaScript Object Notation (JSON) dan dikirimkan secara real-time menuju peladen API (backend server) menggunakan metode HTTP POST request tanpa mengganggu pengalaman menonton pengguna.
4. **Klasifikasi pada Peladen (Model Evaluation)**
   Peladen berbasis Python menggunakan kerangka kerja FastAPI menerima data teks dan mengeksekusi ekstraksi fitur lanjutan menggunakan TF-IDF. Representasi numerik tersebut kemudian dimasukkan ke dalam model Support Vector Machine (SVM) yang telah dilatih sebelumnya, guna menentukan garis pemisah (hyperplane) dan menghasilkan label klasifikasi (Spam atau Normal).
5. **Manipulasi Antarmuka Pengguna (DOM Manipulation)**
   Peladen mengembalikan hasil prediksi ke ekstensi Chrome. Apabila label yang dikembalikan adalah "Spam", Content Script dari ekstensi akan mencari ID elemen komentar yang bersangkutan dan menerapkan injeksi kode properti Cascading Style Sheets (CSS) dengan parameter display: none atau visibility: hidden. Hal ini secara instan menghilangkan komentar tersebut dari pandangan pengguna dalam peramban web yang digunakan.

Tingkah laku dari objek penelitian ini memiliki keunggulan yang signifikan, yaitu kemampuannya memberikan perlindungan proaktif yang disesuaikan secara lokal di komputer pengguna, sehingga tidak memerlukan modifikasi pada arsitektur basis data (database) milik YouTube. Namun, batasan dari tingkah laku ini mencakup tingkat ketergantungan yang tinggi terhadap ketersediaan koneksi internet yang stabil untuk mengakses peladen API, serta kerentanan jika pihak YouTube melakukan perombakan besar-besaran pada struktur tag HTML dan penamaan class DOM mereka.

### 3.1.2 Struktur/Kategori Objek Penelitian

Objek penelitian ini dikategorikan sebagai perangkat lunak filtrasi konten berbasis peramban dengan standar arsitektur pengembangan Manifest V3. Guna mendukung proses deteksi berbasis Machine Learning yang berat, struktur sistem ini mengusung pola arsitektur terdistribusi yang memisahkan beban kerja antara sisi klien dan sisi peladen. Struktur objek penelitian ini terdiri dari:

1. **Sisi Klien (Ekstensi Chrome)**
   Bertindak sebagai agen interaktif di sisi pengguna. Terdiri dari Manifest File (manifest.json) yang mengatur hak akses permission peramban, Content Scripts yang diinjeksi langsung ke halaman YouTube untuk membaca teks dan mengeksekusi manipulasi DOM, serta Service Workers (background.js) yang mengelola siklus hidup ekstensi dan menangani rute komunikasi ke peladen luar secara efisien.
2. **Sisi Peladen (Backend API)**
   Bertindak sebagai pusat pemrosesan cerdas. Lingkungan peladen dibangun menggunakan bahasa pemrograman Python dengan kerangka kerja FastAPI, yang mengadopsi mekanisme pemrograman asynchronous sehingga sangat optimal untuk menangani permintaan teks secara bersamaan dari ekstensi. Peladen ini memuat pipeline prapemrosesan teks, ekstraksi fitur TF-IDF, dan model Support Vector Machine (SVM) yang telah dilatih, serta menyediakan dua endpoint REST API yaitu /predict untuk klasifikasi tunggal dan /predict/batch untuk klasifikasi hingga 50 komentar sekaligus.

### 3.1.3 Profil Perusahaan YouTube  *(BARU)*

Meskipun objek utama penelitian ini berupa perangkat lunak ekstensi peramban, platform tempat sistem ini beroperasi, yaitu YouTube, dikelola oleh sebuah entitas perusahaan. Oleh karena itu, profil dan struktur organisasi perusahaan tersebut perlu diuraikan sebagai bagian dari konteks penelitian.

YouTube merupakan platform berbagi video yang didirikan pada tahun 2005 oleh Chad Hurley, Steve Chen, dan Jawed Karim `[VERIFIKASI]`. Pada tahun 2006, YouTube diakuisisi oleh Google dengan nilai sekitar 1,65 miliar dolar Amerika Serikat `[VERIFIKASI]`, dan sejak saat itu beroperasi sebagai anak perusahaan (subsidiary) di bawah Google. Setelah restrukturisasi korporat pada tahun 2015, Google berada di bawah perusahaan induk Alphabet Inc. `[VERIFIKASI]`. Dengan demikian, secara struktural YouTube menempati posisi sebagai unit bisnis di bawah Google LLC yang merupakan anak perusahaan dari Alphabet Inc.

Kegiatan bisnis utama YouTube berpusat pada penyediaan layanan berbagi dan streaming video, dengan model pendapatan utama berasal dari periklanan digital, layanan berlangganan (YouTube Premium dan YouTube TV), serta fitur monetisasi kreator seperti channel membership dan Super Chat. Sebagai salah satu platform dengan basis pengguna terbesar di dunia, YouTube memproses miliaran interaksi pengguna setiap harinya, termasuk unggahan video, penayangan, dan komentar, sehingga volume interaksi yang masif ini menjadikan platform tersebut rentan terhadap penyalahgunaan berupa penyebaran komentar spam secara otomatis.

### 3.1.4 Struktur Organisasi YouTube  *(BARU)*

Posisi YouTube dalam struktur korporat serta pembagian unit fungsional yang relevan dengan penelitian ini digambarkan pada Gambar 3.1 berikut.

> **[GAMBAR 3.1: Struktur Organisasi YouTube]**
>
> *Panduan menggambar bagan (buat di Word/Visio, mode hitam-putih sesuai dosen poin 10). Struktur pohon:*
> ```
> Alphabet Inc. (Sundar Pichai — CEO) [VERIFIKASI]
>        │
>   Google LLC (Sundar Pichai — CEO) [VERIFIKASI]
>        │
>   YouTube (Neal Mohan — CEO, sejak 2023) [VERIFIKASI CEO saat ini]
>        │
>   ┌────────────┬───────────────┬──────────────┬─────────────────┐
> Product &   Content &       Business /     Trust & Safety    ...
> Engineering Creator Partn.  Advertising    (moderasi konten,
>                                             anti-spam)
> ```

Secara korporat, kepemimpinan tertinggi berada pada Alphabet Inc. dan Google LLC yang dipimpin oleh Sundar Pichai selaku Chief Executive Officer (CEO) `[VERIFIKASI]`. Di tingkat YouTube, kepemimpinan dipegang oleh seorang CEO YouTube, yaitu Neal Mohan sejak tahun 2023 `[VERIFIKASI CEO yang menjabat saat penulisan]`, yang membawahi sejumlah divisi fungsional. Divisi-divisi tersebut secara umum mencakup Product & Engineering yang menangani pengembangan produk dan infrastruktur teknis, Content & Creator Partnerships yang mengelola hubungan dengan kreator konten, Business dan Advertising yang menangani monetisasi platform, serta Trust & Safety yang bertanggung jawab atas keamanan platform, moderasi konten, dan penanganan penyalahgunaan termasuk spam.

> ⚠️ *Catatan: rincian pembagian divisi di atas bersifat gambaran umum fungsi organisasi, bukan salinan bagan resmi internal YouTube yang dipublikasikan. Sebutkan sumber acuan yang digunakan, atau beri keterangan bahwa bagan merupakan penyederhanaan fungsional agar tidak dianggap klaim absolut.*

Dalam konteks penelitian ini, divisi yang paling relevan adalah Trust & Safety, karena unit inilah yang menangani kebijakan dan mekanisme moderasi komentar, termasuk penyaringan spam promosi judi online yang menjadi fokus penelitian. Keterbatasan mekanisme moderasi otomatis yang dikelola oleh divisi ini menjadi dasar bagi analisis sistem berjalan yang diuraikan pada sub-bab berikutnya.

## 3.2 Sistem Berjalan

### 3.2.1 Tinjauan Umum

Sistem penyaringan komentar yang berjalan saat ini pada platform YouTube pada dasarnya beroperasi melalui mekanisme hibrida, yang menggabungkan filtrasi otomatis berbasis kamus kata kunci (keyword-based filtering / regular expressions blacklist) dan sistem moderasi manual berbasis pelaporan dari komunitas (flagging). YouTube secara terpusat menyaring atau menahan komentar yang secara eksplisit memuat kata-kata kasar, tautan URL ke situs berbahaya, atau kosakata spesifik yang telah dimasukkan ke dalam konfigurasi daftar hitam oleh kreator konten pada panel YouTube Studio.

### 3.2.2 Analisis Proses Sistem Berjalan

Walaupun sistem filter bawaan platform ini mampu beroperasi pada skala besar (jutaan komentar per detik), proses identifikasi spam konvensional ini memiliki celah struktural dalam menangani analisis semantik tingkat lanjut, khususnya terhadap teknik penyamaran teks manipulatif (obfuscation). Analisis terhadap alur kelemahan sistem berjalan dapat diuraikan melalui tahapan berikut:

1. Pelaku serangan (spammer) menggunakan skrip otomatis untuk menghasilkan teks promosi judi online yang telah dimanipulasi secara visual. Manipulasi ini memanfaatkan teknik substitusi karakter (homoglyphs), contohnya mengganti alfabet Latin "O" dengan angka nol "0" atau huruf Yunani "Omicron", serta menyisipkan tanda baca acak di antara susunan kata (contoh: "S.L.O.T", "J-u-d-i").
2. Komentar manipulatif tersebut dikirimkan ke pangkalan data server YouTube melalui protokol standar aplikasi.
3. Mesin filtrasi bawaan platform menjalankan pencocokan string linier dengan kamus kata kunci terlarang (misalnya: mencari kata "slot").
4. Karena susunan byte dari karakter-karakter manipulatif tersebut (secara Unicode) berbeda dengan kamus dasar, algoritma platform gagal mengidentifikasinya sebagai leksikon yang melanggar kebijakan. Platform menganggap susunan tersebut sebagai teks acak yang tidak bermakna atau tidak membahayakan.
5. Komentar dinyatakan berstatus valid dan diotorisasi untuk ditampilkan pada antarmuka publik. Akibatnya, promosi ilegal tersebut berhasil menembus lapisan keamanan dan terpapar kepada jutaan pengguna.

### 3.2.3 Flowchart Sistem Berjalan

Alur kelemahan sistem berjalan yang telah diuraikan pada sub-bab sebelumnya dapat divisualisasikan dalam bentuk diagram alir (flowchart) sebagaimana disajikan pada Gambar 3.2 berikut.  *(← KALIMAT PENGANTAR BARU, dosen poin 8. Perhatikan nomor gambar berubah jadi 3.2)*

> **[GAMBAR 3.2: Flowchart Sistem Berjalan]**  *(dulu Gambar 3.1)*

Berikut ini adalah penjelasan dari diagram flowchart sistem berjalan:

1. Mulai (Start)
2. Entitas pengguna atau bot mengirimkan masukan berupa teks komentar ke server YouTube.
3. Sistem YouTube menerima permintaan dan menjalankan proses pencocokan dengan pangkalan data kata kunci (Keyword Blacklist Checking).
4. Titik Keputusan (Decision): Apakah teks komentar mengandung entitas kata terlarang secara presisi?
5. Apabila kondisi bernilai "Ya", sistem menjalankan proses pemblokiran dan menyembunyikan komentar ke peninjauan (Hold for Review).
6. Apabila kondisi bernilai "Tidak" (kata disamarkan dengan obfuscation yang tidak terdaftar), sistem menjalankan proses otorisasi.
7. Komentar lolos dan dirender pada DOM halaman video secara publik.
8. Selesai (End).

## 3.3 Permasalahan Sistem (PIECES)

Untuk mengukur keandalan dan mendiagnosis secara presisi kelemahan yang ada pada sistem berjalan, penelitian ini menggunakan metode evaluasi PIECES (Performance, Information, Economics, Control, Efficiency, dan Service). Berikut adalah penjabaran analisis permasalahan dari sistem pemfilteran YouTube saat ini:

1. **Analisis Kinerja (Performance)**
   Kinerja infrastruktur YouTube sangat mumpuni dalam memproses dan menyaring jutaan komentar teks baku per detik. Namun, throughput (kemampuan menyelesaikan pekerjaan) sistem ini menurun drastis ketika berhadapan dengan teks yang dimanipulasi (obfuscation). Kegagalan sistem dalam membedah karakter manipulatif secara instan mengakibatkan latensi tinggi dalam penanganan spam, karena pada akhirnya platform harus bergantung pada proses moderasi (flagging) manual oleh pengguna yang membutuhkan waktu respon (response time) sangat lambat.
2. **Analisis Informasi (Information)**
   Sistem berjalan gagal mempertahankan kualitas informasi yang disajikan di ruang publik. Lemahnya pemfilteran menyebabkan kolom komentar dibanjiri oleh teks dan tautan yang sama sekali tidak relevan dengan konteks video. Informasi promosi judi online yang lolos dari sistem ini sangat menyesatkan, mereduksi nilai edukasi atau hiburan dari konten utama, dan mendegradasi kualitas informasi platform secara keseluruhan.
3. **Analisis Ekonomi (Economics)**
   Dari sudut pandang makro, lolosnya promosi perjudian ilegal ini menimbulkan ancaman kerugian finansial yang masif bagi masyarakat yang terjerat. Sementara dari sisi operasional platform, mempekerjakan ribuan moderator manusia untuk menyaring sisa komentar spam yang gagal ditangkap oleh mesin otomatis merupakan pemborosan anggaran (inefisiensi biaya) yang seharusnya dapat ditekan dengan sistem cerdas di sisi klien.
4. **Analisis Kendali (Control)**
   Tingkat pengendalian (control) sistem berjalan terbukti sangat lemah terhadap serangan manipulasi String. Ketiadaan mekanisme String Normalization yang agresif membuat sistem kehilangan kendali saat berhadapan dengan homoglyphs, penyisipan tanda baca, atau penggunaan variasi fon Unicode khusus. Celah keamanan ini mempermudah pihak tak bertanggung jawab menyisipkan Uniform Resource Locator (URL) berbahaya yang mengancam privasi dan keamanan data pengguna.
5. **Analisis Efisiensi (Efficiency)**
   Mekanisme pemfilteran bawaan yang mengandalkan pembaruan daftar hitam (blacklist) kata kunci secara manual sangat tidak efisien. Spammer hanya perlu mengubah satu struktur karakter (misalnya "SLOT" menjadi "5L0T") untuk menembus filter. Pola ini memaksa administrator untuk terus memperbarui kamus data secara konstan, sebuah proses yang menghabiskan waktu dan tenaga, serta selalu tertinggal selangkah dari laju otomatisasi bot penyerang.
6. **Analisis Pelayanan (Service)**
   Dampak akumulatif dari kelemahan sistem berjalan bermuara pada buruknya tingkat pelayanan dan pengalaman pengguna (user experience). Kegagalan platform dalam menciptakan lingkungan digital yang aman dari paparan promosi ilegal memicu ketidaknyamanan berinteraksi, mematikan diskusi yang konstruktif di kolom komentar, dan menurunkan tingkat kepercayaan (trust) pengguna terhadap kredibilitas layanan platform tersebut.

Ringkasan dari keenam aspek analisis PIECES beserta identifikasi masalah dan solusi yang diusulkan disajikan pada Tabel 3.1 berikut.  *(← KALIMAT PENGANTAR BARU, dosen poin 8)*

**Tabel 3.1 Ringkasan Analisis PIECES Sistem Berjalan**

| Aspek PIECES | Identifikasi Masalah | Solusi yang Diusulkan |
|--------------|----------------------|-----------------------|
| Analisis Kinerja (Performance) | Throughput sistem menurun drastis dan latensi memanjang jika berhadapan dengan komentar yang menggunakan teknik penyamaran teks (obfuscation). | Penerapan normalisasi teks otomatis di sisi klien sebelum proses klasifikasi dimulai. |
| Analisis Informasi (Information) | Informasi promosi judi online yang lolos mereduksi kualitas konten, menyesatkan publik, dan mendegradasi nilai edukasi/hiburan platform. | Implementasi model klasifikasi berbasis machine learning untuk mengidentifikasi dan menyembunyikan konten menyesatkan secara otomatis. |
| Analisis Ekonomi (Economics) | Lolosnya spam memicu risiko kerugian finansial di masyarakat, serta inefisiensi biaya operasional karena masih bergantung pada moderator manusia. | Pengembangan sistem deteksi otomatis di sisi klien yang dapat diakses secara gratis tanpa biaya berlangganan layanan moderasi berbayar. |
| Analisis Kendali (Control) | Lemahnya kendali sistem (String Normalization yang tidak agresif) menyebabkan platform gagal memetakan karakter Unicode khusus dan URL berbahaya. | Penerapan tujuh tahap normalisasi teks termasuk konversi NFKC Unicode, penanganan homoglyph lintas skrip, dan kanonisasi nama brand judi online memperkuat lapisan kendali deteksi. |
| Analisis Efisiensi (Efficiency) | Pembaruan kamus blacklist secara manual sangat tidak efisien dan selalu tertinggal dari laju pembaruan otomatisasi skrip bot spammer. | Penerapan lapisan normalisasi karakter yang agresif untuk memperkuat kendali deteksi terhadap berbagai teknik penyamaran teks. |
| Analisis Pelayanan (Service) | Paparan promosi ilegal menurunkan kenyamanan (user experience), merusak diskusi konstruktif, dan mendegradasi kredibilitas layanan platform. | Penyembunyian komentar spam secara otomatis di peramban pengguna untuk menciptakan pengalaman berselancar yang lebih bersih dan aman. |

Berdasarkan hasil analisis menggunakan metode PIECES terhadap sistem yang berjalan, dapat disimpulkan bahwa kelemahan paling fundamental terletak pada aspek Kendali (Control) dan Efisiensi (Efficiency). Ketidakmampuan sistem native platform dalam mengurai teks yang dimanipulasi (obfuscation) menyebabkan efisiensi pemfilteran menurun dan hilangnya kendali terhadap penyebaran promosi perjudian. Kegagalan pada dua aspek inti ini secara berantai berdampak buruk pada Kinerja (Performance) moderasi, merusak validitas Informasi (Information), memicu kerugian Ekonomi (Economics), dan pada akhirnya mendegradasi kualitas Pelayanan (Service) kepada pengguna.

Oleh karena itu, sebagai solusi ilmiah dan teknis atas permasalahan tersebut, sangat mendesak untuk dirancang sebuah sistem usulan berupa ekstensi peramban Google Chrome. Sistem usulan ini diproyeksikan mampu menutupi celah kendali platform dengan mengimplementasikan teknik String Normalization langsung di sisi klien (client-side), serta meningkatkan efisiensi deteksi secara signifikan melalui integrasi model kecerdasan buatan berbasis Support Vector Machine (SVM). Kombinasi teknologi ini akan menciptakan benteng pertahanan yang proaktif, adaptif, dan mampu menyembunyikan ancaman spam secara real-time sebelum terpapar kepada pengguna.
