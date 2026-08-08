# 09 — Naskah Presentasi Sidang (10 Menit)

> Naskah ini juga sudah tertanam sebagai **speaker notes** di dalam PPT. Buka Presenter View di PowerPoint, notes-nya muncul otomatis di layar laptopmu.

Deck sekarang: **15 slide inti + 20 slide lampiran** (dari sebelumnya 31 slide inti).

---

## Anggaran waktu

10 menit = 600 detik. Ini pembagiannya:

| # | Slide | Durasi | Kumulatif |
|---|---|---|---|
| 1 | Cover | 0:15 | 0:15 |
| 2 | Latar Belakang | 0:50 | 1:05 |
| 3 | Rumusan Masalah & Tujuan | 0:45 | 1:50 |
| 4 | Obfuscation & String Normalization | 0:55 | 2:45 |
| 5 | Sistem Berjalan | 0:35 | 3:20 |
| 6 | Analisis PIECES | 0:45 | 4:05 |
| 7 | Dataset Penelitian | 0:45 | 4:50 |
| 8 | Alur Pelatihan Model | 0:40 | 5:30 |
| 9 | Arsitektur Sistem | 0:45 | 6:15 |
| 10 | Hasil Pengujian | 0:50 | 7:05 |
| 11 | Perbandingan Algoritma | 0:40 | 7:45 |
| 12 | Uji Ketahanan & Ablasi | 0:45 | 8:30 |
| 13 | **Demonstrasi Sistem** | 1:15 | 9:45 |
| 14 | Kesimpulan & Saran | 0:15 | 10:00 |
| 15 | Terima Kasih | — | — |

⚠️ **Tidak ada slack sama sekali.** Kalau di slide 7 kamu belum sampai menit 5, kamu sudah tertinggal.

### Kalau ternyata mepet, potong sesuai urutan ini

1. **Demo dipangkas jadi 45 detik** — cukup langkah 1, 2, 3. Lewati mode Hilangkan.
2. **Slide 5 (Sistem Berjalan)** — lewati, cukup satu kalimat sambil pindah slide.
3. **Slide 11 (Perbandingan Algoritma)** — sebut satu kalimat: "SVM unggul atas Logistic Regression dan Naive Bayes." Lanjut.

Jangan pernah memotong slide **4, 10, atau 12**. Itu tiga slide yang membedakan skripsimu dari sekadar laporan.

---

## Aturan main

- **Jangan membaca slide.** Penguji bisa baca sendiri. Suaramu untuk hal yang tidak tertulis di layar.
- **Satu slide, satu gagasan utama.** Kalau kamu bingung mau bilang apa di suatu slide, sebut kalimat kuncinya saja lalu lanjut.
- **Jangan minta maaf** karena waktu singkat, karena gugup, atau karena ada yang keliru. Sebut, perbaiki, lanjut.
- **Latih dengan stopwatch minimal 3 kali.** Bukan dibaca dalam hati — diucapkan keras.

---

# NASKAH PER SLIDE

---

## Slide 1 — Cover · 0:15

> "Assalamualaikum warahmatullahi wabarakatuh. Selamat pagi Bapak dan Ibu penguji.
>
> Perkenalkan, saya Yusuf Wandana, NIM 221232017, dari Program Studi Teknik Informatika.
>
> Pada kesempatan ini saya akan memaparkan hasil penelitian saya mengenai penerapan algoritma Support Vector Machine dengan teknik String Normalization, untuk mendeteksi komentar spam judi online di YouTube, yang diimplementasikan dalam bentuk ekstensi Chrome."

❌ Jangan membacakan judul lengkap kata per kata. Judulnya panjang dan sudah terpampang.

---

## Slide 2 — Latar Belakang · 0:50

Empat kuadran, satu kalimat masing-masing. Ucapkan berurutan searah jarum jam.

> "Promosi judi online menyebar sangat masif melalui kolom komentar YouTube, dan sudah dikategorikan sebagai ancaman nirmiliter terhadap ketahanan nasional.
>
> YouTube sebenarnya sudah menyediakan filter kata terlarang. Persoalannya, filter itu bekerja dengan mencocokkan kata kunci secara harfiah — sementara penyebar spam menyamarkan teksnya menggunakan homoglyph, tanda diakritik, dan leet speak. Akibatnya lolos.
>
> Karena itu pendekatan yang saya usulkan adalah menormalkan lebih dulu teks yang tersamar melalui String Normalization, baru kemudian diklasifikasikan dengan TF-IDF dan Support Vector Machine.
>
> Bentuk implementasinya adalah ekstensi Chrome berbasis Manifest V3, yang bekerja real-time di sisi klien tanpa membebani peladen YouTube."

🎯 **Kalimat kunci yang harus keluar:**
> *"Masalahnya bukan filternya tidak ada — tapi filternya bisa dilewati."*

---

## Slide 3 — Rumusan Masalah & Tujuan · 0:45

> "Rumusan masalah penelitian ini satu: bagaimana merancang dan mengimplementasikan SVM yang dikombinasikan dengan String Normalization ke dalam ekstensi Chrome Manifest V3, untuk mendeteksi dan menyembunyikan komentar spam judi online berbahasa Indonesia yang tersamar, secara real-time.
>
> Dari rumusan tersebut diturunkan tiga tujuan: **merancang** ekstensinya, **mengimplementasikan** deteksi real-time di sisi klien, dan **mengukur** performanya melalui akurasi, presisi, recall, dan F1-score."

💡 Tiga kata itu — merancang, mengimplementasikan, mengukur — **panggil lagi di slide penutup**. Itu yang membuat presentasi terasa utuh.

---

## Slide 4 — Obfuscation & String Normalization · 0:55 ⭐

**Ini inti kebaruan penelitianmu. Jangan buru-buru.**

> "Sebelah kiri adalah cara penyebar spam menyamarkan teksnya. Ada empat teknik, dan saya beri contoh konkretnya.
>
> Pertama, **homoglyph** — huruf 'a' Latin diganti dengan huruf 'a' Cyrillic. Di mata manusia bentuknya identik, tapi kode Unicode-nya sama sekali berbeda, sehingga pencocokan kata kunci gagal.
>
> Kedua, **penyisipan tanda diakritik** — misalnya nama situs ditulis dengan garis bawah di setiap hurufnya.
>
> Ketiga, **leet speak** — huruf diganti angka, misalnya ROMA4D dengan angka empat menggantikan huruf A.
>
> Keempat, penyisipan simbol dan spasi tidak beraturan.
>
> Sebelah kanan adalah penanganannya. String Normalization mengembalikan teks tersamar ke bentuk ASCII standar melalui tujuh tahap prapemrosesan. Tiga yang paling menentukan adalah normalisasi Unicode NFKC, pelipatan diakritik, dan penyeragaman seluruh nama situs judi menjadi satu token tunggal."

🎯 **Kalimat kunci:**
> *"Filter kata kunci gagal karena teksnya sudah bukan huruf yang dia cari. Saya kembalikan dulu ke bentuk standarnya, baru diklasifikasikan."*

💡 Kalau diminta membuktikan: `python src/preprocessing.py` menampilkan 10 kasus uji beserta hasil normalisasinya.

---

## Slide 5 — Sistem Berjalan · 0:35

> "Ini sistem yang berjalan saat ini. Moderasi komentar di YouTube bertumpu pada dua mekanisme: filter kata terlarang yang harus diisi manual oleh pemilik kanal, dan pelaporan oleh pengguna.
>
> Keduanya bersifat reaktif dan berbasis pencocokan harfiah. Begitu teksnya disamarkan, dua-duanya tidak mengenali. Di sinilah letak celah yang saya teliti."

👉 Tunjuk gambarnya. Jangan berdiri diam sambil bicara ke layar.

---

## Slide 6 — Analisis PIECES · 0:45

> "Kelemahan sistem berjalan saya analisis menggunakan kerangka PIECES. Empat aspek yang paling menonjol.
>
> Dari sisi **kendali** — dan ini kelemahan utamanya — filter hanya mencocokkan kata kunci secara harfiah, sehingga tidak mengenali teks yang disamarkan.
>
> Dari sisi **efisiensi**, kamus kata kunci harus diperbarui manual, sehingga selalu tertinggal dari variasi penyamaran yang baru.
>
> Dari sisi **kinerja**, komentar spam tetap tampil dan menurunkan kualitas ruang diskusi. Dan dari sisi **pelayanan**, pengguna tidak memiliki kendali atas tingkat sensitivitas penyaringan."

💡 Aspek **kendali** yang melahirkan penelitian ini — tekankan yang itu, tiga sisanya sebut cepat.
💡 Aspek **pelayanan** nanti terjawab oleh fitur slider ambang batas. Boleh disinggung sebagai jembatan.

---

## Slide 7 — Dataset Penelitian · 0:45

**Bagian ini sering dikejar penguji. Hafalkan angkanya.**

> "Dataset yang digunakan berjumlah 6.690 komentar YouTube berbahasa Indonesia, terdiri atas 2.332 komentar spam dan 4.358 non-spam.
>
> Karena kelasnya tidak seimbang, saya tangani melalui parameter `class_weight balanced` pada model — bukan dengan membuang data, supaya tidak ada informasi yang hilang.
>
> Pengumpulannya menggunakan **YouTube Data API v3 resmi** melalui skrip Node.js. Ini penting, karena berkaitan langsung dengan aspek kelayakan hukum sistem.
>
> Pelabelannya dua kelas, spam dan ham, dengan penyaringan heuristik sebagai tahap pertama lalu koreksi manual. Pembagiannya 80 banding 20 secara berstrata, menghasilkan 5.352 data latih dan 1.338 data uji."

⚠️ **Bersiap** — gambar di slide berikutnya masih tertulis "Web Scraping". Kamu akan mengoreksinya sendiri.

---

## Slide 8 — Alur Pelatihan Model · 0:40

> "Alur pelatihannya lima tahap: pengumpulan data, prapemrosesan dengan String Normalization, ekstraksi fitur TF-IDF, pelatihan SVM kernel linear, lalu evaluasi dan penyimpanan model dalam format joblib.
>
> Tahap ini dijalankan sekali saja di luar sistem. Hasil akhirnya satu berkas model yang kemudian dipakai berulang-ulang saat inferensi."

### 🔴 Koreksi diri di sini — sebelum ditanya

> "Satu koreksi, Pak — pada kotak pertama gambar ini masih tertulis *Web Scraping*. Itu keliru, dan sudah saya sadari. Yang benar, dan yang benar-benar dipakai, adalah YouTube Data API v3 resmi, sesuai yang saya tuliskan di BAB II."

Ucapkan tenang, lalu **langsung lanjut**. Jangan berhenti untuk minta maaf.

💡 Mengoreksi duluan mengubah temuan penguji menjadi bukti ketelitianmu. Detailnya di [`08-daftar-kesalahan.md`](08-daftar-kesalahan.md).

---

## Slide 9 — Arsitektur Sistem · 0:45

> "Sistem terdiri dari tiga komponen.
>
> Pertama, **scraper** berbasis Node.js — perannya murni mengumpulkan data latih, dan tidak terlibat sama sekali saat ekstensi digunakan pengguna akhir.
>
> Kedua, **ekstensi Chrome** Manifest V3 — content script membaca komentar dari halaman, dan popup menjadi antarmuka kendali pengguna.
>
> Ketiga, **server FastAPI** — memuat model joblib sekali saat menyala, lalu menyediakan endpoint REST.
>
> Alur saat digunakan: content script mengambil komentar dari halaman, mengirimkannya per batch 50 komentar ke endpoint `/predict/batch`, server mengembalikan label beserta skor keyakinan, lalu ekstensi menyembunyikan komentar yang melewati ambang batas."

🎯 **Ini yang membedakanmu dari mahasiswa yang tidak paham sistemnya sendiri:**
> *"Normalisasi teks dilakukan di sisi server, memakai fungsi yang sama persis dengan yang dipakai saat pelatihan. Ini untuk mencegah training-serving skew — supaya tidak ada dua versi logika yang bisa berbeda."*

❓ Kalau ditanya kenapa batch 50: mengurangi jumlah permintaan HTTP. Satu komentar satu request itu boros dan lambat.

---

## Slide 10 — Hasil Pengujian · 0:50 ⭐⭐

**Slide paling penting. Pelan-pelan.**

> "Dari 1.338 data uji, confusion matrix-nya sebagai berikut: 863 komentar non-spam dikenali dengan benar, 442 spam dikenali dengan benar, 9 false positive yaitu non-spam yang salah dituduh spam, dan 24 false negative yaitu spam yang lolos.
>
> Akurasinya dihitung dari 442 ditambah 863, dibagi 1.338 — hasilnya 1.305 per 1.338, yaitu **97,53 persen**.
>
> F1-macro-nya 0,9726. Presisi untuk kelas spam 0,98 dan recall 0,9485.
>
> Presisi sengaja saya jaga lebih tinggi daripada recall, karena dalam kasus ini menyembunyikan komentar orang yang tidak bersalah lebih merugikan daripada meloloskan satu spam."

💡 Kalau ditanya *"angka ini dari mana?"* — **sebut confusion matrix-nya dulu, lalu rumusnya, baru hasilnya.** Jangan langsung menyebut hasil. Urutan itu yang membedakan orang yang menghitung dari orang yang menyalin.

📎 Rumus lengkap dan perhitungan riil ada di **lampiran slide 22 dan 23**.

---

## Slide 11 — Perbandingan Algoritma · 0:40

> "Untuk membuktikan pemilihan SVM bukan keputusan sembarangan, saya menguji dua algoritma pembanding pada dataset dan pembagian data yang sama persis.
>
> SVM mencapai akurasi 97,53 persen dengan F1-macro 0,9726. Logistic Regression 97,09 persen dengan F1-macro 0,9675. Multinomial Naive Bayes 93,95 persen dengan F1-macro 0,9313.
>
> SVM unggul. Naive Bayes paling rendah karena asumsi independensi antarfiturnya kurang sesuai untuk teks tersamar, di mana antar-karakter justru saling bergantung.
>
> Selisih dengan Logistic Regression memang tipis, namun SVM konsisten unggul di seluruh fold."

❓ **Kenapa kernel linear, bukan RBF?**
> "Karena data teks hasil TF-IDF berdimensi sangat tinggi dan sudah terpisah secara linear. RBF hanya menambah biaya komputasi tanpa peningkatan yang berarti."

📎 Grafik validasi silang dan pencarian nilai C ada di **lampiran slide 25 dan 26**.

---

## Slide 12 — Uji Ketahanan & Ablasi · 0:45 ⭐

**Ini nilai tambah akademik skripsimu. Jangan dilewat.**

> "Saya melakukan tiga pengujian tambahan.
>
> Pertama, **hard test set** — 135 komentar ambigu yang seluruhnya bukan spam. Isinya komentar korban judi, kritik, dan diskusi anti-judol yang kebetulan menyebut nama situs. Model mencapai akurasi 98,52 persen dengan hanya 2 false positive. Ini menguji ketahanan terhadap salah tuduh.
>
> Kedua, **ablasi aturan hibrida**. Saya coba menambahkan aturan kata kunci di atas SVM. Hasilnya justru menurunkan akurasi 7,32 poin pada data uji, dan 16,30 poin pada hard test set. Karena itu SVM murni yang dipertahankan.
>
> Ketiga, **pengujian stemming**. Stemming Sastrawi tidak memberikan peningkatan yang signifikan secara statistik, dengan p-value 0,3575, sehingga tidak digunakan pada pipeline akhir."

🎯 **Kalimat penutup slide ini — ucapkan dengan percaya diri, bukan minta maaf:**
> *"Dua eksperimen terakhir hasilnya negatif, dan tetap saya laporkan apa adanya — karena justru membuktikan bahwa pipeline yang saya pakai sudah yang paling sederhana namun efektif."*

⚠️ **Ranjau:** kalau penguji membuka `reports/hard_set_evaluation.txt`, di situ tertulis F1-macro **0,4963**. Itu bukan tanda model rusak — hard test set isinya satu kelas saja, sehingga F1 kelas spam otomatis nol. Itulah sebabnya yang dilaporkan accuracy, bukan F1-macro.

---

## Slide 13 — Demonstrasi Sistem · 1:15

**Harus sudah dilatih sampai hafal. Jangan improvisasi.**

Urutan peragaan:

1. **Buka popup** — tunjuk status server dan panel statistik (dipindai / disembunyikan)
2. **Gulir ke kolom komentar** — tunjuk spam yang otomatis diredupkan
3. **Klik satu badge persentase** — munculkan komentar aslinya, tunjuk skor keyakinannya
4. **Ganti ke mode Hilangkan** — tunjuk bedanya
5. **Selesai** — kembali ke slide

> "Ambang batasnya bisa diatur pengguna dari 50 sampai 95 persen, dengan nilai bawaan 75 persen."

⚠️ Kalau waktu mepet: **jangan geser slider**, cukup sebut lisan seperti kalimat di atas.

### Kalau demo gagal

1. Cek server — buka tab `localhost:8000/health`
2. Kalau server mati — nyalakan ulang **sambil terus menjelaskan arsitekturnya**
3. Kalau YouTube tidak kooperatif — buka `localhost:8000/docs`, uji satu komentar di `/predict`
4. Kalau semuanya gagal — buka **lampiran slide 33 dan 34** (Mode Redupkan & Hilangkan)

Jangan panik, jangan minta maaf berlebihan. Yang dinilai pemahamanmu, bukan kelancaran jaringan.

---

## Slide 14 — Kesimpulan & Saran · 0:15

Baca cepat. Sebut intinya, jangan dibaca utuh.

> "Kesimpulannya empat. Sistem berjalan terbukti lemah terhadap komentar yang disamarkan. Model SVM kernel linear dengan C sama dengan 1 mencapai akurasi 97,53 persen dan F1-macro 0,9726, stabil pada validasi silang, dan tangguh pada hard test set. Menambah kompleksitas pipeline justru tidak meningkatkan performa. Dan sistem bekerja real-time di sisi klien serta layak diterapkan dari aspek teknologi, operasional, maupun hukum.
>
> Sarannya, pembaruan dataset secara berkala melalui mekanisme re-training, dan adaptasi pipeline ke platform lain.
>
> **Dengan demikian, ketiga tujuan penelitian yang saya sampaikan di awal telah tercapai.**"

💡 Kalimat terakhir itu yang menutup lingkaran. Jangan dilupakan.

---

## Slide 15 — Terima Kasih

> "Demikian pemaparan saya. Terima kasih atas perhatian Bapak dan Ibu. Saya persilakan untuk pertanyaan dan masukan."

Lalu **berhenti bicara**. Jangan mengisi keheningan. Tarik napas.

---

# Peta Lampiran

Slide 16 adalah pembatas LAMPIRAN. **Jangan diklik kecuali diminta.** Hafalkan nomornya supaya bisa langsung lompat pakai `Ctrl` + nomor slide + `Enter`.

| Slide | Isi | Dibuka kalau ditanya |
|---|---|---|
| 17 | Konsep SVM | "Jelaskan cara kerja SVM" |
| 18 | Rumus TF-IDF | "Rumus TF-IDF-nya bagaimana?" |
| 19 | Contoh perhitungan TF-IDF | "Coba contohkan perhitungannya" |
| 20 | Rumus SVM kernel linear | "Rumus hyperplane-nya?" |
| 21 | Kalibrasi probabilitas (Platt) | "Persentase keyakinan itu dari mana?" |
| 22 | Rumus metrik evaluasi | "Rumus akurasi/presisi/recall?" |
| 23 | **Perhitungan data riil** | **"Angka 97,53% dari mana?"** ⭐ |
| 24 | Konfigurasi model | "Parameternya apa saja?" |
| 25 | Validasi silang 5-fold | "Apakah hasilnya stabil?" |
| 26 | Pencarian nilai C | "Kenapa C = 1?" |
| 27 | Eksperimen stemming | "Kenapa tidak pakai stemming?" |
| 28 | Metode Waterfall | "Metode pengembangannya apa?" |
| 29 | Alur inferensi real-time | "Alur saat dipakai bagaimana?" |
| 30 | Use case diagram | "Mana diagram UML-nya?" |
| 31 | Activity diagram | idem |
| 32 | Sequence diagram | idem |
| 33 | Mode Redupkan | cadangan demo |
| 34 | Mode Hilangkan | cadangan demo |
| 35 | Kegunaan penelitian | "Apa manfaat penelitian ini?" |

**Tiga yang paling mungkin dipakai: 23, 26, 27.** Hafalkan tiga nomor itu.

---

# Daftar periksa sebelum masuk ruangan

- [ ] Server sudah menyala, `localhost:8000/health` merespons
- [ ] Tab `localhost:8000/docs` sudah terbuka di latar
- [ ] Video YouTube cadangan (yang dipastikan ada spam judol) sudah terbuka
- [ ] Ekstensi terpasang dan ikonnya tersemat
- [ ] PowerPoint dalam **Presenter View** supaya speaker notes terlihat
- [ ] Sudah latihan penuh dengan stopwatch minimal 3 kali
- [ ] Sudah baca [`08-daftar-kesalahan.md`](08-daftar-kesalahan.md) — tahu apa yang keliru dan cara mengakuinya
- [ ] Hafal tiga nomor slide lampiran: **23, 26, 27**

---

# Yang wajib keluar dari mulutmu

Kalau dari seluruh naskah ini kamu cuma sempat menghafal lima kalimat, pilih ini:

1. *"Masalahnya bukan filternya tidak ada — tapi filternya bisa dilewati."*
2. *"Saya kembalikan dulu teksnya ke bentuk standar, baru diklasifikasikan."*
3. *"Normalisasi dilakukan di sisi server dengan fungsi yang sama persis seperti saat pelatihan, untuk mencegah training-serving skew."*
4. *"Presisi saya jaga lebih tinggi dari recall, karena salah menuduh lebih merugikan daripada meloloskan satu spam."*
5. *"Dua eksperimen hasilnya negatif dan tetap saya laporkan, karena justru membuktikan pipeline saya sudah yang paling sederhana namun efektif."*

Lima kalimat itu yang menunjukkan kamu **memahami**, bukan menghafal.
