# 09 — Naskah Presentasi Sidang (10 Menit)

> Naskah ini juga sudah tertanam sebagai **speaker notes** di dalam PPT. Buka Presenter View di PowerPoint, notes-nya muncul otomatis di layar laptopmu.

Deck sekarang: **16 slide inti + 19 slide lampiran** (dari 31 slide inti sebelumnya).

---

## Anggaran waktu

10 menit = 600 detik.

| # | Slide | Durasi | Kumulatif |
|---|---|---|---|
| 1 | Cover | 0:15 | 0:15 |
| 2 | Latar Belakang | 0:45 | 1:00 |
| 3 | Rumusan Masalah & Tujuan | 0:40 | 1:40 |
| 4 | Obfuscation & String Normalization ⭐ | 0:55 | 2:35 |
| 5 | Sistem Berjalan | 0:30 | 3:05 |
| 6 | Analisis PIECES | 0:40 | 3:45 |
| 7 | Dataset Penelitian | 0:40 | 4:25 |
| 8 | Alur Pelatihan Model | 0:35 | 5:00 |
| 9 | Arsitektur Sistem | 0:40 | 5:40 |
| 10 | **Alur Inferensi Real-Time** | 0:40 | 6:20 |
| 11 | Hasil Pengujian ⭐ | 0:50 | 7:10 |
| 12 | Perbandingan Algoritma | 0:30 | 7:40 |
| 13 | Uji Ketahanan & Ablasi ⭐ | 0:40 | 8:20 |
| 14 | **Demonstrasi Sistem** | 1:10 | 9:30 |
| 15 | Kesimpulan & Saran | 0:20 | 9:50 |
| 16 | Terima Kasih | 0:10 | 10:00 |

⚠️ **Nol slack.** Kalau di slide 7 kamu belum sampai menit 4:30, kamu sudah tertinggal.

### Kalau mepet, potong sesuai urutan ini

1. **Demo dipangkas jadi 40 detik** — cukup langkah 1, 2, 3.
2. **Slide 5 (Sistem Berjalan)** — lewati, cukup satu kalimat sambil pindah slide.
3. **Slide 12 (Perbandingan Algoritma)** — sebut satu kalimat: *"SVM unggul atas Logistic Regression dan Naive Bayes."*

Jangan pernah memotong **4, 10, 11, atau 13**.

---

## Aturan main

- **Jangan membaca slide.** Suaramu untuk hal yang tidak tertulis di layar.
- **Satu slide, satu gagasan utama.** Bingung mau bilang apa? Sebut kalimat kuncinya, lalu lanjut.
- **Jangan minta maaf** karena waktu singkat, gugup, atau ada yang keliru. Sebut, perbaiki, lanjut.
- **Latih dengan stopwatch minimal 3 kali**, diucapkan keras — bukan dibaca dalam hati.

---

# NASKAH PER SLIDE

---

## Slide 1 — Cover · 0:15

> "Assalamualaikum warahmatullahi wabarakatuh. Selamat pagi Bapak dan Ibu penguji.
>
> Perkenalkan, saya Yusuf Wandana, NIM 221232017, dari Program Studi Teknik Informatika.
>
> Pada kesempatan ini saya akan memaparkan hasil penelitian saya mengenai penerapan algoritma Support Vector Machine dengan teknik String Normalization, untuk mendeteksi komentar spam judi online di YouTube, yang diimplementasikan dalam bentuk ekstensi Chrome."

❌ Jangan membacakan judul lengkap kata per kata.

---

## Slide 2 — Latar Belakang · 0:45

> "Promosi judi online menyebar sangat masif melalui kolom komentar YouTube, dan sudah dikategorikan sebagai ancaman nirmiliter terhadap ketahanan nasional.
>
> YouTube sebenarnya sudah menyediakan filter kata terlarang. Persoalannya, filter itu bekerja dengan mencocokkan kata kunci secara harfiah — sementara penyebar spam menyamarkan teksnya menggunakan homoglyph, tanda diakritik, dan leet speak. Akibatnya lolos.
>
> Karena itu pendekatan yang saya usulkan adalah menormalkan lebih dulu teks yang tersamar melalui String Normalization, baru kemudian diklasifikasikan dengan TF-IDF dan Support Vector Machine.
>
> Bentuk implementasinya adalah ekstensi Chrome berbasis Manifest V3, yang bekerja real-time di sisi klien tanpa membebani peladen YouTube."

🎯 **Kalimat kunci:** *"Masalahnya bukan filternya tidak ada — tapi filternya bisa dilewati."*

---

## Slide 3 — Rumusan Masalah & Tujuan · 0:40

> "Rumusan masalah penelitian ini satu: bagaimana merancang dan mengimplementasikan SVM yang dikombinasikan dengan String Normalization ke dalam ekstensi Chrome Manifest V3, untuk mendeteksi dan menyembunyikan komentar spam judi online berbahasa Indonesia yang tersamar, secara real-time.
>
> Dari rumusan tersebut diturunkan tiga tujuan: **merancang** ekstensinya, **mengimplementasikan** deteksi real-time di sisi klien, dan **mengukur** performanya melalui akurasi, presisi, recall, dan F1-score."

💡 Tiga kata itu — merancang, mengimplementasikan, mengukur — **panggil lagi di slide penutup.**

---

## Slide 4 — Obfuscation & String Normalization · 0:55 ⭐

**Inti kebaruan penelitianmu. Jangan buru-buru.**

> "Sebelah kiri adalah cara penyebar spam menyamarkan teksnya.
>
> Pertama, **homoglyph** — huruf 'a' Latin diganti dengan huruf 'a' Cyrillic. Di mata manusia bentuknya identik, tapi kode Unicode-nya sama sekali berbeda, sehingga pencocokan kata kunci gagal.
>
> Kedua, **penyisipan tanda diakritik** — nama situs ditulis dengan garis bawah di setiap hurufnya.
>
> Ketiga, **leet speak** — huruf diganti angka, misalnya ROMA4D dengan angka empat menggantikan huruf A. Keempat, penyisipan simbol dan spasi tidak beraturan.
>
> Sebelah kanan penanganannya. String Normalization mengembalikan teks tersamar ke bentuk ASCII standar melalui tujuh tahap prapemrosesan. Tiga yang paling menentukan: normalisasi Unicode NFKC, pelipatan diakritik, dan penyeragaman seluruh nama situs judi menjadi satu token tunggal."

🎯 **Kalimat kunci:** *"Filter kata kunci gagal karena teksnya sudah bukan huruf yang dia cari. Saya kembalikan dulu ke bentuk standarnya, baru diklasifikasikan."*

💡 Kalau diminta bukti: `python src/preprocessing.py` menampilkan 10 kasus uji beserta hasil normalisasinya.

---

## Slide 5 — Sistem Berjalan · 0:30

> "Ini sistem yang berjalan saat ini. Moderasi komentar di YouTube bertumpu pada dua mekanisme: filter kata terlarang yang harus diisi manual oleh pemilik kanal, dan pelaporan oleh pengguna.
>
> Keduanya bersifat reaktif dan berbasis pencocokan harfiah. Begitu teksnya disamarkan, dua-duanya tidak mengenali. Di sinilah letak celah yang saya teliti."

👉 Tunjuk gambarnya.

---

## Slide 6 — Analisis PIECES · 0:40

> "Kelemahan sistem berjalan saya analisis menggunakan kerangka PIECES.
>
> Dari sisi **kendali** — dan ini kelemahan utamanya — filter hanya mencocokkan kata kunci secara harfiah, sehingga tidak mengenali teks yang disamarkan.
>
> Dari sisi **efisiensi**, kamus kata kunci harus diperbarui manual, sehingga selalu tertinggal dari variasi penyamaran yang baru.
>
> Dari sisi **kinerja**, komentar spam tetap tampil dan menurunkan kualitas ruang diskusi. Dan dari sisi **pelayanan**, pengguna tidak memiliki kendali atas tingkat sensitivitas penyaringan."

💡 Aspek **kendali** yang melahirkan penelitian ini. Aspek **pelayanan** nanti terjawab oleh slider ambang batas — boleh dijadikan jembatan.

---

## Slide 7 — Dataset Penelitian · 0:40

**Sering dikejar penguji. Hafalkan angkanya.**

> "Dataset yang digunakan berjumlah 6.690 komentar YouTube berbahasa Indonesia, terdiri atas 2.332 komentar spam dan 4.358 non-spam.
>
> Karena kelasnya tidak seimbang, saya tangani melalui parameter `class_weight balanced` pada model — bukan dengan membuang data, supaya tidak ada informasi yang hilang.
>
> Pengumpulannya menggunakan **YouTube Data API v3 resmi** melalui skrip Node.js. Ini penting karena berkaitan langsung dengan aspek kelayakan hukum sistem.
>
> Pelabelannya dua kelas, spam dan ham, dengan penyaringan heuristik sebagai tahap pertama lalu koreksi manual. Pembagiannya 80 banding 20 secara berstrata, menghasilkan 5.352 data latih dan 1.338 data uji."

⚠️ **Bersiap** — gambar di slide berikutnya masih tertulis "Web Scraping".

---

## Slide 8 — Alur Pelatihan Model · 0:35

> "Alur pelatihannya lima tahap: pengumpulan data, prapemrosesan dengan String Normalization, ekstraksi fitur TF-IDF, pelatihan SVM kernel linear, lalu evaluasi dan penyimpanan model dalam format joblib.
>
> Tahap ini dijalankan sekali saja di luar sistem. Hasil akhirnya satu berkas model yang kemudian dipakai berulang-ulang saat inferensi."

### 🔴 Koreksi diri di sini — sebelum ditanya

> "Satu koreksi, Pak — pada kotak pertama gambar ini masih tertulis *Web Scraping*. Itu keliru, dan sudah saya sadari. Yang benar, dan yang benar-benar dipakai, adalah YouTube Data API v3 resmi, sesuai yang saya tuliskan di BAB II."

Ucapkan tenang, lalu **langsung lanjut**.

---

## Slide 9 — Arsitektur Sistem · 0:40

> "Sistem terdiri dari tiga komponen.
>
> Pertama, **scraper** berbasis Node.js — perannya murni mengumpulkan data latih, dan tidak terlibat sama sekali saat ekstensi digunakan pengguna akhir.
>
> Kedua, **ekstensi Chrome** Manifest V3 — content script membaca komentar dari halaman, dan popup menjadi antarmuka kendali pengguna.
>
> Ketiga, **server FastAPI** — di-deploy pada VPS berbasis Ubuntu Server 24.04 LTS, dan diakses melalui `https://api-svm.cupsky.my.id` dengan HTTPS."

🎯 **Sebut VPS-nya.** Ini sekarang kekuatan: servernya benar-benar online dan bisa diakses dari mana saja, persis seperti yang tertulis di naskah.

🎯 **Kalimat yang membedakanmu dari orang yang tidak paham sistemnya sendiri:**
> *"Normalisasi teks dilakukan di sisi server, memakai fungsi yang sama persis dengan yang dipakai saat pelatihan — untuk mencegah training-serving skew."*

### ⚠️ Kalau penguji jeli membaca gambarnya

Tiga keterangan pada Gambar 4.3 keliru. Akui saja kalau ditanya:

| Tertulis di gambar | Yang benar |
|---|---|
| Scraper "via YouTube DOM" | YouTube Data API v3 |
| Slider "0–100%" | 50–95% |
| Izin "scripting" | hanya `storage` dan `activeTab` |

---

## Slide 10 — Alur Inferensi Real-Time · 0:40

**Ini jawaban untuk *"bagaimana sistem usulan Anda bekerja?"***

> "Alur sistem saat digunakan ada enam langkah.
>
> Pengguna membuka halaman YouTube, dan content script otomatis aktif. Content script mengambil teks komentar dari DOM halaman, lalu mengemasnya dalam format JSON dan mengirimkannya **per batch 50 komentar** ke endpoint `/predict/batch`.
>
> Di sisi server, teks dinormalkan menggunakan fungsi yang sama dengan saat pelatihan, diubah menjadi vektor TF-IDF, lalu diklasifikasikan oleh model SVM.
>
> Server mengembalikan label beserta skor keyakinan hasil kalibrasi Platt Scaling. Komentar berlabel spam yang skornya melewati ambang batas kemudian disembunyikan sesuai mode pilihan pengguna — Redupkan atau Hilangkan.
>
> Seluruh proses ini berjalan tanpa menyentuh peladen YouTube sama sekali."

❓ **Kenapa batch 50?** Mengurangi jumlah permintaan HTTP. Satu komentar satu request itu boros dan lambat.

❓ **Bagaimana komentar baru saat scroll?** Ada `MutationObserver` yang memantau perubahan DOM, sehingga komentar yang baru dimuat otomatis ikut dipindai.

---

## Slide 11 — Hasil Pengujian · 0:50 ⭐⭐

**Slide paling penting. Pelan-pelan.**

> "Dari 1.338 data uji, confusion matrix-nya sebagai berikut: 863 komentar non-spam dikenali dengan benar, 442 spam dikenali dengan benar, 9 false positive yaitu non-spam yang salah dituduh spam, dan 24 false negative yaitu spam yang lolos.
>
> Akurasinya dihitung dari 442 ditambah 863, dibagi 1.338 — hasilnya 1.305 per 1.338, yaitu **97,53 persen**.
>
> F1-macro-nya 0,9726. Presisi untuk kelas spam 0,98 dan recall 0,9485.
>
> Presisi sengaja saya jaga lebih tinggi daripada recall, karena dalam kasus ini menyembunyikan komentar orang yang tidak bersalah lebih merugikan daripada meloloskan satu spam."

💡 Kalau ditanya *"angka ini dari mana?"* — **sebut confusion matrix dulu, lalu rumusnya, baru hasilnya.** Urutan itu yang membedakan orang yang menghitung dari orang yang menyalin.

📎 Rumus & perhitungan riil: **lampiran slide 24**.

---

## Slide 12 — Perbandingan Algoritma · 0:30

> "Untuk membuktikan pemilihan SVM bukan keputusan sembarangan, saya menguji dua algoritma pembanding pada dataset dan pembagian data yang sama persis.
>
> SVM 97,53 persen dengan F1-macro 0,9726. Logistic Regression 97,09 persen. Multinomial Naive Bayes 93,95 persen.
>
> Naive Bayes paling rendah karena asumsi independensi antarfiturnya kurang sesuai untuk teks tersamar, di mana antar-karakter justru saling bergantung. Selisih dengan Logistic Regression tipis, namun SVM konsisten unggul di seluruh fold."

❓ **Kenapa kernel linear, bukan RBF?** Data teks hasil TF-IDF berdimensi sangat tinggi dan sudah terpisah secara linear. RBF hanya menambah biaya komputasi tanpa peningkatan berarti.

📎 Grafik: **lampiran slide 26 dan 27**.

---

## Slide 13 — Uji Ketahanan & Ablasi · 0:40 ⭐

**Nilai tambah akademik. Jangan dilewat.**

> "Saya melakukan tiga pengujian tambahan.
>
> Pertama, **hard test set** — 135 komentar ambigu yang seluruhnya bukan spam. Isinya komentar korban judi, kritik, dan diskusi anti-judol yang kebetulan menyebut nama situs. Model mencapai akurasi 98,52 persen dengan hanya 2 false positive.
>
> Kedua, **ablasi aturan hibrida**. Saya coba menambahkan aturan kata kunci di atas SVM. Hasilnya justru menurunkan akurasi 7,32 poin pada data uji, dan 16,30 poin pada hard test set. Karena itu SVM murni yang dipertahankan.
>
> Ketiga, **pengujian stemming**. Stemming Sastrawi tidak memberikan peningkatan yang signifikan secara statistik, dengan p-value 0,3575, sehingga tidak digunakan pada pipeline akhir."

🎯 **Ucapkan dengan percaya diri, bukan minta maaf:**
> *"Dua eksperimen terakhir hasilnya negatif, dan tetap saya laporkan apa adanya — karena justru membuktikan bahwa pipeline yang saya pakai sudah yang paling sederhana namun efektif."*

⚠️ **Ranjau:** `reports/hard_set_evaluation.txt` memuat F1-macro **0,4963**. Itu bukan tanda model rusak — hard test set isinya satu kelas saja, sehingga F1 kelas spam otomatis nol. Itulah sebabnya yang dilaporkan accuracy.

---

## Slide 14 — Demonstrasi Sistem · 1:10

**Slide ini sudah berisi tangkapan layar sistem yang benar-benar berjalan** — jadi kalau demo langsung gagal, slide ini sendiri sudah menjadi bukti.

Urutan peragaan — jangan improvisasi:

1. **Buka popup** — tunjuk status server (`api-svm.cupsky.my.id`) dan panel statistik
2. **Gulir ke kolom komentar** — tunjuk spam yang otomatis diredupkan
3. **Klik satu badge persentase** — munculkan komentar aslinya, tunjuk skor keyakinannya
4. **Ganti ke mode Hilangkan** — tunjuk bedanya
5. **Selesai** — kembali ke slide

> "Ambang batasnya bisa diatur pengguna dari 50 sampai 95 persen, dengan nilai bawaan 75 persen."

🎯 **Nilai jual yang harus disebut:**
> *"Servernya tidak berjalan di laptop saya, Pak, tapi di VPS yang diakses melalui internet."*

### Kalau demo gagal

1. Cek `https://api-svm.cupsky.my.id/health` di tab lain
2. Kalau server bermasalah — buka `https://api-svm.cupsky.my.id/docs`, uji satu komentar di `/predict`
3. Kalau semuanya gagal — slide ini sendiri sudah tangkapan layar. **Lampiran slide 31** untuk Mode Hilangkan.

Jangan panik, jangan minta maaf berlebihan.

---

## Slide 15 — Kesimpulan & Saran · 0:20

> "Kesimpulannya empat. Sistem berjalan terbukti lemah terhadap komentar yang disamarkan. Model SVM kernel linear dengan C sama dengan 1 mencapai akurasi 97,53 persen dan F1-macro 0,9726, stabil pada validasi silang, dan tangguh pada hard test set. Menambah kompleksitas pipeline justru tidak meningkatkan performa. Dan sistem bekerja real-time di sisi klien serta layak diterapkan dari aspek teknologi, operasional, maupun hukum.
>
> Sarannya, pembaruan dataset secara berkala melalui mekanisme re-training, dan adaptasi pipeline ke platform lain.
>
> **Dengan demikian, ketiga tujuan penelitian yang saya sampaikan di awal telah tercapai.**"

💡 Kalimat terakhir itu yang menutup lingkaran.

---

## Slide 16 — Terima Kasih · 0:10

> "Demikian pemaparan saya. Terima kasih atas perhatian Bapak dan Ibu. Saya persilakan untuk pertanyaan dan masukan."

Lalu **berhenti bicara**. Tarik napas.

---

# Peta Lampiran

Slide 17 adalah pembatas LAMPIRAN. **Jangan diklik kecuali diminta.** Lompat cepat dengan mengetik nomor slide lalu `Enter` saat mode presentasi.

| Slide | Isi | Dibuka kalau ditanya |
|---|---|---|
| 18 | Konsep SVM | "Jelaskan cara kerja SVM" |
| 19 | Rumus TF-IDF | "Rumus TF-IDF-nya bagaimana?" |
| 20 | Contoh perhitungan TF-IDF | "Coba contohkan perhitungannya" |
| 21 | Rumus SVM kernel linear | "Rumus hyperplane-nya?" |
| 22 | Kalibrasi probabilitas (Platt) | "Persentase keyakinan itu dari mana?" |
| 23 | Rumus metrik evaluasi | "Rumus akurasi/presisi/recall?" |
| **24** | **Perhitungan data riil** | **"Angka 97,53% dari mana?"** ⭐ |
| 25 | Konfigurasi model | "Parameternya apa saja?" |
| 26 | Validasi silang 5-fold | "Apakah hasilnya stabil?" |
| **27** | **Pencarian nilai C** | **"Kenapa C = 1?"** ⭐ |
| **28** | **Eksperimen stemming** | **"Kenapa tidak pakai stemming?"** ⭐ |
| 29 | Metode Waterfall | "Metode pengembangannya apa?" |
| 30 | Rancangan antarmuka popup | "Mana rancangan layarnya?" |
| 31 | Mode Hilangkan | cadangan demo |
| 32 | Use case diagram | "Mana diagram UML-nya?" |
| 33 | Activity diagram | idem |
| 34 | Sequence diagram | idem |
| 35 | Kegunaan penelitian | "Apa manfaat penelitian ini?" |

**Hafalkan tiga nomor: 24, 27, 28.** Itu yang paling mungkin dipakai.

---

# Daftar periksa sebelum masuk ruangan

- [ ] `https://api-svm.cupsky.my.id/health` merespons
- [ ] Tab `https://api-svm.cupsky.my.id/docs` sudah terbuka di latar
- [ ] Video YouTube cadangan (dipastikan ada spam judol) sudah terbuka
- [ ] Ekstensi terpasang dan ikonnya tersemat
- [ ] PowerPoint dalam **Presenter View** supaya speaker notes terlihat
- [ ] Sudah latihan penuh dengan stopwatch minimal 3 kali
- [ ] Sudah baca [`08-daftar-kesalahan.md`](08-daftar-kesalahan.md)
- [ ] Hafal tiga nomor lampiran: **24, 27, 28**

---

# Yang wajib keluar dari mulutmu

Lima kalimat. Kalau cuma sempat menghafal ini, sudah cukup untuk terdengar menguasai:

1. *"Masalahnya bukan filternya tidak ada — tapi filternya bisa dilewati."*
2. *"Saya kembalikan dulu teksnya ke bentuk standar, baru diklasifikasikan."*
3. *"Normalisasi dilakukan di sisi server dengan fungsi yang sama persis seperti saat pelatihan, untuk mencegah training-serving skew."*
4. *"Presisi saya jaga lebih tinggi dari recall, karena salah menuduh lebih merugikan daripada meloloskan satu spam."*
5. *"Dua eksperimen hasilnya negatif dan tetap saya laporkan, karena justru membuktikan pipeline saya sudah yang paling sederhana namun efektif."*
