# 06 — Bank Pertanyaan Sidang

> Pertanyaan yang mungkin muncul, diurutkan berdasarkan kemungkinan, lengkap dengan jawaban siap pakai.

## Cara memakai dokumen ini

Jangan dihafal kata per kata — nanti terdengar seperti membaca teks. Yang perlu kamu kuasai adalah **kerangka jawabannya**, lalu sampaikan dengan bahasamu sendiri.

Latihan yang efektif: tutup bagian jawaban, coba jawab sendiri dengan suara keras, baru buka dan bandingkan. Bagian yang tidak bisa kamu jawab tanpa melihat, itulah yang perlu diulang.

**Tanda tingkat risiko:**
- 🔴 Hampir pasti ditanya — harus lancar tanpa berpikir
- 🟠 Sering ditanya
- 🟡 Mungkin ditanya
- ⚫ Pertanyaan menjebak — perlu kehati-hatian

---

# A. Pertanyaan pembuka

## 🔴 A1. "Coba jelaskan penelitian Anda secara singkat."

Ini pertanyaan pertama hampir di semua sidang. Siapkan versi **60 detik**. Jangan bertele-tele.

> "Penelitian ini membangun ekstensi Chrome yang mendeteksi dan menyembunyikan komentar promosi judi online di YouTube secara real-time.
>
> Masalahnya, filter kata kunci milik YouTube mudah dilewati karena penyebar spam menyamarkan tulisan — misalnya mengganti huruf dengan karakter Unicode yang bentuknya mirip, atau mengganti huruf dengan angka.
>
> Solusinya dua tahap: pertama, teks yang disamarkan dinormalkan dulu kembali ke bentuk standar lewat String Normalization. Kedua, teks bersih itu diklasifikasikan dengan algoritma Support Vector Machine yang dilatih pada 6.690 komentar berlabel.
>
> Hasilnya akurasi 97,53% dengan F1-macro 0,9726, mengungguli Logistic Regression dan Naive Bayes sebagai pembanding."

Empat bagian: **masalah → kenapa sulit → solusi → hasil**. Kalau gugup, pegang urutan itu saja.

---

## 🔴 A2. "Apa kontribusi atau kebaruan penelitian Anda?"

> "Ada tiga, Pak.
>
> Pertama, **domainnya spesifik** — komentar promosi judi online berbahasa Indonesia. Penelitian deteksi spam yang ada umumnya menyasar spam umum atau berbahasa Inggris.
>
> Kedua, **penanganan obfuscation secara berlapis**. Sebagian besar penelitian mengasumsikan teksnya normal, sementara penelitian ini justru berangkat dari asumsi bahwa teksnya sengaja disamarkan.
>
> Ketiga, **luarannya produk yang berjalan**, bukan berhenti di evaluasi model. Modelnya diintegrasikan ke ekstensi peramban yang bekerja real-time di sisi klien."

---

# B. Pertanyaan tentang angka

## 🔴 B1. "Akurasi 97,53% itu dari mana?"

> "Dari 1.338 data uji, Pak — 20% dari total 6.690 yang disisihkan dan tidak pernah dilihat model saat pelatihan.
>
> Dari 1.338 itu, model menebak benar 1.305: yaitu 442 spam yang benar terdeteksi, ditambah 863 non-spam yang benar dibiarkan. Sisanya 33 salah — 9 komentar normal yang salah ditandai spam, dan 24 spam yang lolos.
>
> Jadi 1.305 dibagi 1.338 sama dengan 0,9753."

⚠️ Hafalkan empat angka ini di luar kepala: **863 / 9 / 24 / 442**. Dan ingat urutannya: TN, FP, FN, TP.

---

## 🔴 B2. "Kenapa pakai F1-score, bukan akurasi saja?"

> "Karena datanya tidak seimbang, Pak — 2.332 spam berbanding 4.358 non-spam. Pada data timpang, akurasi bisa menipu: model yang selalu menjawab 'bukan spam' saja sudah mendapat akurasi sekitar 65% tanpa belajar apa pun.
>
> F1-score menggabungkan presisi dan recall, jadi model hanya mendapat nilai tinggi kalau benar-benar bisa mendeteksi kelas spam. Saya pakai F1-macro supaya kedua kelas dihitung setara, tidak didominasi kelas yang lebih banyak."

---

## 🟠 B3. "Apa bedanya presisi dan recall? Mana yang lebih penting?"

> "Presisi menjawab: kalau model bilang spam, seberapa sering dia benar. Nilainya 0,98.
> Recall menjawab: dari semua spam yang ada, berapa yang berhasil ditangkap. Nilainya 0,95.
>
> Keduanya penting tapi konsekuensinya berbeda. Presisi rendah berarti komentar normal ikut tersembunyi — itu mengganggu pengguna. Recall rendah berarti spam lolos — itu menggagalkan tujuan sistem.
>
> Pada sistem ini presisi sedikit lebih tinggi, artinya model cenderung berhati-hati sebelum menuduh. Tapi karena preferensinya bisa berbeda tiap orang, ambang batasnya saya buat bisa diatur pengguna antara 50% sampai 95%."

---

## 🟠 B4. "Apa itu cross-validation? Kenapa perlu kalau sudah ada data uji?"

> "Supaya hasilnya tidak bergantung pada satu pembagian data yang kebetulan menguntungkan, Pak.
>
> Cara kerjanya, data dibagi lima bagian lalu diuji lima kali bergantian — tiap putaran satu bagian jadi penguji dan empat sisanya jadi bahan latih.
>
> Hasilnya rata-rata 0,9741 dengan simpangan baku 0,0030. Simpangan sekecil itu menunjukkan performanya konsisten di kelima putaran, bukan kebetulan bagus di satu pembagian saja."

---

## ⚫ B5. "Di berkas laporan ini tertulis F1-macro 0,4963. Kok rendah sekali?"

**Ini pertanyaan paling berbahaya di seluruh daftar.** Jawab dengan tenang — jangan panik, karena modelnya memang tidak bermasalah.

> "Angka itu memang terlihat rendah, Pak, tapi tidak bermakna dalam konteks pengujian tersebut.
>
> Hard test set sengaja saya susun berisi 135 komentar yang **seluruhnya bukan spam** — tidak ada satu pun contoh spam di dalamnya. Isinya komentar ambigu seperti korban judol atau kritik yang menyebut nama situs judi.
>
> Karena F1-macro merata-ratakan kedua kelas, dan kelas spam tidak punya data sama sekali di pengujian itu, F1 untuk kelas spam otomatis nol — bukan karena model gagal, tapi karena memang tidak ada yang bisa dideteksi. Nol itu lalu menyeret rata-ratanya jadi sekitar 0,50.
>
> Metrik yang tepat untuk pengujian satu kelas seperti ini adalah akurasi dan jumlah false positive. Hasilnya 98,52% dengan hanya 2 false positive dari 135 komentar. Itulah yang saya laporkan di skripsi."

Kalau kamu bisa menjawab ini lancar, kesannya justru sangat menguasai.

---

# C. Pertanyaan tentang metode

## 🔴 C1. "Kenapa memilih SVM?"

> "Empat alasan, Pak.
>
> Pertama, SVM kuat pada data berdimensi tinggi. Representasi teks di penelitian ini menghasilkan 10.000 fitur.
>
> Kedua, SVM memilih pemisah dengan margin terlebar — bukan sekadar pemisah yang kebetulan berhasil — sehingga lebih tahan terhadap data baru.
>
> Ketiga, dengan kernel linear prediksinya ringan, dan itu penting karena sistem harus merespons real-time saat pengguna menggulir halaman.
>
> Keempat, dan ini yang paling penting: saya tidak hanya berasumsi. Saya membandingkannya dengan Logistic Regression dan Naive Bayes memakai fitur dan pembagian data yang sama persis. SVM unggul di keduanya."

---

## 🔴 C2. "Bagaimana cara kerja SVM?"

Jelaskan pelan, jangan buru-buru pakai istilah.

> "Setelah teks diubah jadi angka lewat TF-IDF, tiap komentar menjadi satu titik dalam ruang berdimensi banyak. Komentar spam cenderung berkumpul di satu wilayah, non-spam di wilayah lain.
>
> SVM mencari batas pemisah antara keduanya — namanya hyperplane. Yang membedakan SVM dari algoritma lain, dia tidak asal menarik batas. Dari sekian banyak batas yang mungkin, dia memilih yang **jaraknya paling jauh** dari titik terdekat kedua kelompok. Jarak itu disebut margin.
>
> Titik-titik yang berada persis di tepi margin disebut support vector, dan merekalah yang menentukan posisi batasnya. Titik lain yang jauh dari perbatasan tidak berpengaruh.
>
> Saat ada komentar baru, sistem menghitung komentar itu jatuh di sisi mana dari batas tersebut."

---

## 🔴 C3. "Apa itu TF-IDF? Kenapa tidak hitung frekuensi biasa?"

> "TF-IDF memberi bobot pada tiap kata berdasarkan dua hal: seberapa sering kata itu muncul di satu komentar, dan seberapa langka kata itu di seluruh dataset.
>
> Kalau hanya frekuensi biasa, kata seperti 'yang' dan 'di' akan mendominasi karena paling sering muncul — padahal tidak membedakan apa-apa antara spam dan bukan.
>
> TF-IDF menambahkan faktor kelangkaan. Kata yang muncul di semua dokumen otomatis mendapat bobot nol, karena rumusnya melibatkan logaritma dari total dokumen dibagi jumlah dokumen yang memuat kata itu. Kalau muncul di semua, hasilnya log 1 sama dengan nol.
>
> Jadi kata pasaran terbuang sendiri secara matematis, dan kata penciri spam seperti 'gacor' mendapat bobot tinggi."

Kalau diminta contoh, pakai contoh dari skripsimu: kata "slot" bobotnya 0,176, kata "ini" bobotnya 0.

---

## 🟠 C4. "Apa itu String Normalization? Kenapa perlu?"

> "Itu tahap membersihkan teks yang sengaja disamarkan, Pak, supaya kembali ke bentuk standar sebelum diproses model.
>
> Penyebar spam memakai beberapa teknik penyamaran: mengganti huruf Latin dengan karakter dari sistem tulisan lain yang bentuknya mirip — misalnya huruf a Cyrillic yang tampak identik dengan a Latin tapi bagi komputer berbeda; menyisipkan karakter tak terlihat; menambahkan tanda diakritik; atau mengganti huruf dengan angka seperti menulis situs dengan angka satu.
>
> Tanpa normalisasi, semua variasi itu dianggap kata yang berbeda-beda, sehingga model tidak bisa mengenalinya. Prosesnya ada tujuh tahap, dan seluruhnya dijalankan oleh satu berkas yang sama baik saat pelatihan maupun saat prediksi."

---

## 🟠 C5. "Kenapa 80:20? Kenapa random_state 42?"

> "80:20 adalah proporsi yang paling lazim. Dengan 6.690 data, 20% memberi 1.338 sampel uji — cukup besar untuk hasil yang stabil sambil menyisakan data latih yang memadai.
>
> `random_state=42` adalah kunci acakan supaya pembagiannya sama persis setiap kali kode dijalankan. Tujuannya keterulangan — siapa pun yang menjalankan ulang kode ini akan mendapat angka yang sama. Nilai 42 itu sendiri tidak punya arti khusus, hanya angka konvensi yang lazim dipakai. Yang penting nilainya tetap, bukan berapa nilainya."

Jangan mengarang makna filosofis untuk angka 42. Jawaban jujur justru lebih meyakinkan.

---

# D. Pertanyaan tentang hasil negatif

Dua pertanyaan ini **hampir pasti muncul** dan paling sering membuat mahasiswa tersendat.

## 🔴 D1. "Kenapa tidak menambahkan aturan kata kunci untuk memperkuat model?"

> "Sudah saya coba dan justru merugikan, Pak.
>
> Saya menguji lewat ablation study: SVM murni dibandingkan dengan SVM yang ditambah aturan heuristik. Hasilnya akurasi turun 7,32 poin pada data uji, dan turun 16,30 poin pada hard test set.
>
> Penyebabnya, aturan kata kunci tidak bisa membedakan komentar yang **melaporkan** situs judi dari yang **mempromosikannya**. Dia hanya melihat ada kata kuncinya lalu langsung menuduh. Akibatnya false positive melonjak dari 2 menjadi 24.
>
> SVM bisa membedakan karena mempertimbangkan seluruh kombinasi kata dalam kalimat, bukan satu kata secara terpisah. Karena itu SVM murni yang dipertahankan."

---

## 🔴 D2. "Kenapa tidak pakai stemming? Bukankah itu standar dalam pemrosesan teks Bahasa Indonesia?"

> "Memang lazim, Pak, dan saya sudah mengujinya memakai Sastrawi.
>
> Pengujiannya berpasangan pada lima fold cross-validation. Selisih F1-macro rata-ratanya hanya −0,0006, dan uji t berpasangan menghasilkan p-value 0,3575.
>
> Karena jauh di atas 0,05, perbedaannya belum bisa dianggap signifikan secara statistik. Jadi stemming tidak dipakai karena menambah waktu komputasi tanpa manfaat yang terbukti — dan waktu komputasi itu berpengaruh karena sistem harus merespons real-time."

⚠️ Perhatikan pilihan kata: **"belum terbukti membantu"**, bukan "terbukti tidak membantu". Uji statistik tidak bisa membuktikan ketiadaan efek.

---

# E. Pertanyaan tentang kode dan sistem

## 🟠 E1. "Coba tunjukkan bagian kode yang melakukan X."

Hafalkan peta ini:

| Kalau ditanya | Buka berkas |
|---|---|
| Pembersihan / normalisasi teks | `src/preprocessing.py` — fungsi `clean_text` |
| Pengaturan TF-IDF | `src/train.py` baris 63–68 |
| Pelatihan model | `src/train.py` |
| Pencarian nilai C | `src/train.py` baris 233 |
| Perhitungan akurasi | `src/train.py` baris 409 |
| Endpoint API | `src/server.py` — cari tanda `@app.` |
| Penyembunyian komentar | `extension/content.js` |
| Pengambilan data | `scraper/index.js` |
| Perbandingan algoritma | `src/compare_baselines.py` |

Kalau tidak ingat baris persisnya, **jangan mengarang**. Katakan saja: *"Ada di berkas preprocessing.py, Pak, boleh saya buka sebentar?"* Membuka berkas di depan penguji itu wajar dan tidak mengurangi nilai.

---

## 🟠 E2. "Kenapa normalisasi dilakukan di server, bukan di ekstensi?"

> "Supaya konsisten antara pelatihan dan prediksi, Pak.
>
> Kalau normalisasi dipecah antara JavaScript di ekstensi dan Python di server, perbedaan kecil dalam cara keduanya menangani karakter Unicode bisa membuat model menerima masukan yang tidak sama persis dengan saat dilatih. Istilahnya training-serving skew, dan dampaknya akurasi turun tanpa terlihat penyebabnya.
>
> Jadi ekstensi mengirim teks mentah apa adanya, dan seluruh normalisasi dijalankan oleh satu berkas Python yang sama — berkas yang persis sama dengan yang dipakai saat pelatihan."

---

## 🟡 E3. "Bagaimana sistem menangani komentar yang muncul saat halaman digulir?"

> "Memakai MutationObserver, Pak — mekanisme bawaan peramban yang memantau perubahan pada struktur halaman. Setiap kali komentar baru dimuat, ekstensi mendeteksinya lalu mengirim teksnya untuk diklasifikasi.
>
> Komentar yang sudah pernah diproses dicatat supaya tidak dikirim ulang, dan pengiriman dilakukan berkelompok maksimal 50 komentar per permintaan agar tidak membebani server."

---

## ⚫ E4. "Servernya berjalan di mana? Apakah sudah di-deploy?"

**Jawab sesuai kondisi saat sidang.** Jangan mengaku sudah di VPS kalau saat itu masih berjalan lokal — penguji bisa minta ditunjukkan.

Kalau **sudah** naik ke VPS:
> "Sudah, Pak, di VPS dengan Ubuntu. Ekstensi mengarah ke alamat tersebut."

Kalau **belum**:
> "Arsitekturnya dirancang untuk berjalan di VPS dan sudah siap di-deploy, Pak. Saat demonstrasi ini servernya berjalan lokal karena prosesnya belum selesai. Secara teknis tidak ada perbedaan alur — yang berubah hanya alamat tujuan pada konfigurasi ekstensi."

Jujur soal ini jauh lebih aman. Sistem yang berjalan lokal tetap sah untuk penelitian.

---

## 🟡 E5. "Kenapa penelitian ini dibatasi pada YouTube, bukan platform lain?"

> "Ruang lingkup penelitian ini memang dibatasi pada YouTube, Pak, sesuai judul. Seluruh pengujian dan evaluasi — dataset, akurasi, hard test set — dilakukan pada komentar YouTube. Adaptasi ke platform lain seperti Instagram atau TikTok saya cantumkan sebagai saran pengembangan lanjutan di Bab V, dan ekstensinya sendiri sekarang hanya meminta izin akses ke YouTube, konsisten dengan itu."

Atau hapus saja barisnya sebelum sidang — lihat `04-kenapa-a-bukan-b.md` bagian 7.

---

# F. Pertanyaan tentang data

## 🔴 F1. "Data dari mana? Berapa banyak? Bagaimana melabelinya?"

> "Data diambil dari kolom komentar YouTube memakai YouTube Data API v3 resmi, dengan kunci API terdaftar. Total 6.690 komentar — 2.332 spam dan 4.358 non-spam.
>
> Pelabelannya dua tahap. Tahap pertama, scraper memberi skor heuristik pada tiap komentar berdasarkan sinyal-sinyal seperti pola nama situs judi. Komentar dengan skor di atas ambang tertentu ditandai spam.
>
> Tahap kedua, penyelamatan: komentar berskor rendah tapi mengandung pola nama brand judi yang jelas tetap ditandai spam, karena banyak brand asli yang hanya memicu satu sinyal.
>
> Selain itu tersedia mekanisme koreksi manual untuk kasus yang salah label, tercatat pada kolom sumber di berkas dataset."

---

## ⚫ F2. "Apakah pelabelan Anda bias? Siapa yang menentukan sebuah komentar itu spam?"

Pertanyaan tajam dan sah. Jawab dengan mengakui keterbatasannya.

> "Pelabelan awal dilakukan otomatis berdasarkan sinyal heuristik, lalu saya periksa dan koreksi manual untuk kasus yang meragukan. Jadi memang ada unsur penilaian saya sebagai peneliti, dan itu keterbatasan yang saya sadari.
>
> Untuk menguranginya, saya menyusun hard test set berisi 135 komentar ambigu — seperti komentar korban judol atau kritik yang menyebut nama situs judi — dan mengujinya secara terpisah. Justru pada data yang paling mudah salah label itulah model diuji ketahanannya, dan hasilnya hanya 2 false positive dari 135.
>
> Pelabelan oleh lebih dari satu orang beserta pengukuran kesepakatan antar-pelabel akan lebih ideal, dan itu saya catat sebagai keterbatasan penelitian."

Mengakui keterbatasan dengan disertai upaya mitigasi jauh lebih kuat daripada bersikeras tidak ada bias.

---

## 🟡 F3. "Apakah 6.690 data itu cukup?"

> "Untuk metode yang dipakai, cukup, Pak. Indikatornya, cross-validation lima fold menghasilkan simpangan baku hanya 0,0030 — artinya performanya sudah stabil, tidak berubah-ubah tergantung pembagian data.
>
> Kalau datanya kurang, biasanya terlihat dari variasi antar-fold yang besar. Untuk pendekatan Deep Learning memang butuh jauh lebih banyak, dan itu salah satu alasan penelitian ini memilih Machine Learning konvensional."

---

# G. Pertanyaan tentang keterbatasan

## 🟠 G1. "Apa keterbatasan penelitian Anda?"

Pertanyaan ini **hadiah**, bukan jebakan. Menjawabnya dengan sadar menunjukkan kedewasaan berpikir. Siapkan tiga:

> "Ada beberapa, Pak.
>
> Pertama, dataset bersifat statis sementara pola spam terus berubah. Sistem perlu pelatihan ulang berkala.
>
> Kedua, model berbasis TF-IDF masih rentan pada kasus ambigu — komentar yang menyebut nama situs judi dalam konteks mengkritik masih bisa salah tertandai. Dari hard test set, 2 dari 135 masih keliru.
>
> Ketiga, sistem bergantung pada struktur halaman YouTube. Kalau YouTube mengubah struktur halamannya, penyeleksi elemen di ekstensi perlu disesuaikan.
>
> Keempat, pengujian terbatas pada YouTube berbahasa Indonesia, belum diuji pada platform atau bahasa lain."

---

## 🟡 G2. "Apa saran untuk pengembangan selanjutnya?"

Ambil dari Bab V skripsimu:
> "Pelatihan ulang berkala memanfaatkan data koreksi dari endpoint laporan; eksplorasi fitur tambahan seperti rasio simbol atau embedding kontekstual untuk menangani kasus ambigu; pengujian pada platform lain seperti Instagram dan TikTok; serta perbandingan dengan model Deep Learning beserta kajian pertukaran antara akurasi dan latensi."

---

# H. Pertanyaan personal

## ⚫ H1. "Ini Anda buat sendiri? Bagian mana yang Anda kerjakan?"

Pertanyaan ini bisa muncul, terutama kalau penguji melihat kodenya rapi dan terdokumentasi baik.

**Jawablah jujur.** Menggunakan alat bantu dalam pengembangan itu praktik yang lazim di industri, dan yang dinilai dalam skripsi adalah **penguasaanmu atas sistem dan keputusan di dalamnya**, bukan siapa yang mengetik tiap baris.

Kerangka jawaban yang jujur sekaligus kuat:

> "Saya yang merumuskan masalahnya, merancang alur sistemnya, dan menentukan aturan mana yang dianggap spam. Saya juga yang memutuskan eksperimen apa yang perlu dijalankan — perbandingan algoritma, ablation study aturan hibrida, dan pengujian stemming — lalu menafsirkan hasilnya untuk mengambil keputusan desain.
>
> Dalam penulisan kodenya saya memakai bantuan alat pengembangan, sebagaimana lazim di praktik rekayasa perangkat lunak. Tapi setiap keputusan teknis di dalamnya bisa saya pertanggungjawabkan, dan dengan senang hati saya jelaskan bagian mana pun yang Bapak/Ibu ingin dalami."

Kalimat terakhir itu penting — kamu **mempersilakan** diuji. Itu hanya bisa diucapkan orang yang siap, dan efeknya justru menenangkan.

Kuncinya: **pastikan kalimat itu benar.** Itulah gunanya seminggu ini.

---

# I. Daftar periksa terakhir

Malam sebelum sidang, pastikan kamu bisa menjawab ini tanpa membuka catatan:

- [ ] Empat angka confusion matrix: 863, 9, 24, 442 — dan mana TN/FP/FN/TP
- [ ] Rumus akurasi, presisi, recall, F1
- [ ] Kenapa F1-macro, bukan akurasi saja
- [ ] Kenapa angka 0,4963 pada hard test set tidak bermakna
- [ ] Kenapa aturan hibrida tidak dipakai (−7,32 dan −16,30)
- [ ] Kenapa stemming tidak dipakai (p = 0,3575)
- [ ] Cara kerja SVM dalam tiga kalimat
- [ ] Cara kerja TF-IDF beserta contoh angka 0,176
- [ ] Apa itu margin dan support vector
- [ ] Kenapa C = 1 dan dari mana asalnya
- [ ] Kenapa `class_weight='balanced'`
- [ ] Empat pengaturan TF-IDF beserta alasannya
- [ ] Dari mana angka persentase di badge (Platt Scaling)
- [ ] Kenapa API resmi, bukan mengikis HTML
- [ ] Status server saat itu — lokal atau VPS
- [ ] Tiga keterbatasan penelitian

---

## Latihan yang paling efektif

Bacaan saja tidak cukup untuk menemukan lubang pemahaman. **Minta disimulasikan sidangnya** — kamu akan dicecar dengan pertanyaan acak dari daftar ini, lalu jawabanmu dinilai dan ditunjukkan bagian mana yang masih goyah.

Paling efektif dilakukan pada hari ke-6 atau ke-7, setelah semua dokumen dibaca.

---

## Selanjutnya

Lanjut ke `02-bedah-kode.md` untuk memahami tiap berkas secara rinci, atau `LAB-praktik.md` kalau ingin langsung mencoba menjalankan sendiri.
