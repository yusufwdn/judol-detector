# Review Revisi BAB IV — 2026-07-19

Menjawab 2 poin revisi hasil bimbingan terakhir, terhadap draft `.docs/[DRAFT] 221232017 - 20260713.pdf` (124 halaman). Method: scan font per-span (PyMuPDF) untuk seluruh dokumen buat poin 1, baca penuh BAB II (hal. 23-57) + BAB IV (hal. 71-117) buat poin 2, plus cek kode asli (`svm-judol-spam/src/prepare_dataset.py`, `scraper-judol-yt-comment/index.js`) buat verifikasi angka `spam_score`.

---

## 1. Peta Italic Istilah Asing

Dasar aturan: **Pedoman 4.2.9** — "huruf cetak miring dipakai apabila menggunakan istilah, kata, **atau singkatan** yang berasal dari kata asing." Jadi secara literal bahkan singkatan (SVM, API, dst) termasuk — tapi ini jarang ditegakkan ketat di praktik, jadi gua kasih catatan terpisah soal itu di bagian 1d.

Exempt yang sudah gua saring dari daftar di bawah: **Daftar Isi/Daftar Gambar/Daftar Tabel** (hal. 1-13, heading tidak perlu italic), **Daftar Pustaka** (hal. 121-124, judul referensi dikutip apa adanya, bukan istilah asing yang disisipkan ke kalimat).

### 1a. Jelas kelewat — tinggal italic-kan (mayoritas kemunculan lain sudah italic, cuma beberapa yang lolos)

| Istilah       | Halaman yang belum di-italic | Sudah italic di | Status Perbaikan |
| ------------- | ---------------------------- | --------------- | ---------------- |
| _obfuscation_ | 22                           | 19× lainnya     | v                |
| _string_      | 28                           | 15× lainnya     | v                |
| _endpoint_    | 77, 120                      | 13× lainnya     | v                |
| _threshold_   | 97                           | 12× lainnya     | v                |
| _extension_   | 55, 91                       | 10× lainnya     | v                |
| _real-time_   | 55, 93                       | 16× lainnya     | v                |
| _stemming_    | 53, 115                      | 8× lainnya      | v                |
| _unigram_     | 33                           | 3× lainnya      | v                |
| _trigram_     | 34                           | 1× lainnya      | v                |
| _flowchart_   | 65, 66                       | 1× lainnya      | v                |
| _deploy_      | 116                          | 4× lainnya      | v                |
| _deployment_  | 53                           | 1× lainnya      | v                |
| _popup_       | 91, 97, 99, 105              | 11× lainnya     | v                |
| _online_      | 17, 21, 32                   | 33× lainnya     | v                |
| _learning_    | 34, 120                      | 19× lainnya     | v                |
| _use case_    | 47, 94, 95                   | 14× lainnya     | v                |

### 1b. Tidak pernah di-italic sama sekali (paling gampang kelewat karena tidak ada "contoh benar" di tempat lain)

- **sigmoid** — hal. 36, 38 (istilah fungsi matematis, jelas istilah asing) [Done]
- **swimlane** — hal. 101 (caption/istilah diagram) [Done]

### 1c. Campur aduk, dominasi terbalik — perlu diputuskan satu kebijakan dulu baru diseragamkan semua

| Istilah    | Italic | Plain | Catatan                                                                                                                                                                           |
| ---------- | ------ | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| _dataset_  | 12     | 18    | Lebih banyak plain. Istilah inti penelitian, disarankan **italic** konsisten.                                                                                                     |
| _pipeline_ | 13     | 8     | Lebih banyak italic, selesaikan sisanya jadi italic.                                                                                                                              |
| _kernel_   | 2      | 4     | Istilah SVM inti, disarankan **italic** konsisten (hal. 35, 87, 112, 115).                                                                                                        |
| _server_   | 17     | 13    | Berimbang. Bisa diargumentasikan sudah terserap umum → boleh plain semua, **asal konsisten**.                                                                                     |
| _linear_   | 3      | 16    | Dominan plain, kemungkinan besar karena dipakai sbg kata sifat ("kernel linear"). Cek konteks satu-satu; kalau memang merujuk istilah teknis (linear kernel/regression) → italic. |

### 1d. Bukan istilah asing biasa — kemungkinan EXEMPT, JANGAN dipaksa italic

Ini nama merek/produk/nama fitur buatan sendiri, bukan "istilah asing yang diserap ke kalimat" — kalau sudah kepalang di-italic di sebagian tempat, justru sebaiknya **dihapus italic-nya** biar konsisten ke arah plain:

- **Chrome** (9× kena italic, 18× plain) — nama merek/browser, seperti "Google", "Windows".
- **Manifest V3** (nama versi API resmi Chrome, muncul plain 13×, italic 1×)
- **Node.js** (nama runtime, plain 7×, italic 2×)
- **Unicode** (nama standar internasional, plain 14×, italic 5×)
- **Mode Redupkan** / **Mode Hilangkan** — nama fitur yang kamu ciptakan sendiri di aplikasi, bukan istilah asing (plain 18×, italic 4×)
- **platform**, **input**, **output** — sudah sangat umum terserap ke Bahasa Indonesia teknis, dokumen ini pun sudah konsisten treat sebagai plain (platform: 1 italic vs 27 plain) → biarkan plain, tinggal rapikan 1 yang nyasar italic.

**Saran tindakan:** karena ini pekerjaan manual (bukan Find & Replace polos, karena satu kata bisa muncul di konteks judul/caption yang exempt), cara paling efisien: buka PDF, `Ctrl+F` tiap istilah di atas, cek satu-satu apakah dia di badan teks (kena) atau di heading/caption/nama file (exempt), lalu putuskan sekali per istilah dan terapkan ke semua kemunculan di badan teks.

---

## 2. Sumber Angka di BAB IV — Kenapa Dosen Nanya "Ini Dari Mana?"

**Keputusan struktur:** semua penjelasan rumus/penerapan tetap di BAB IV, tidak ada yang ditambahkan ke BAB II. BAB II (Landasan Teori) sudah cukup dengan definisi konseptual generik yang sudah ada (Accuracy/Precision/Recall/F1 per-kelas di 2.8, TF-IDF di 2.5, hyperplane SVM di 2.6) — itu memang levelnya "teori dari textbook". Sedangkan F1-macro, standar deviasi CV, paired t-test, dan skema bobot spam_score adalah **penerapan spesifik** ke penelitian ini, jadi lebih pas dijelaskan langsung di BAB IV, tepat di tempat angkanya pertama kali muncul — pembaca nggak perlu bolak-balik ke bab lain buat ngerti dari mana angka itu datang.

Di bawah ini teks lengkap siap-tempel untuk tiap gap, bukan cuma potongan kalimat. Masing-masing dikasih label **[LOKASI]** persis mau disisipkan di mana, semuanya di dalam BAB IV. Placeholder seperti nomor Tabel/Gambar/Persamaan (`4.x`) perlu kamu sesuaikan manual dengan penomoran final di dokumen.

---

### 2a. Paragraf pembuka baru di awal Sub-bab 4.11 "Pengujian Sistem" — definisi semua rumus metrik sebelum dipakai

**[LOKASI]** Sisipkan sebagai paragraf tambahan tepat setelah paragraf pembuka 4.11 yang sudah ada ("Pengujian sistem difokuskan pada evaluasi performa model klasifikasi SVM... eksperimen pengaruh stemming.") dan sebelum heading "4.11.1 Evaluasi pada Data Uji (Holdout)". Ini jadi "kamus rumus" yang dipakai berulang di seluruh sub-bab 4.11, jadi nggak perlu diulang-ulang tiap sub-bab.

**[TEKS SISIPAN]**

> Seluruh skema pengujian di atas menggunakan metrik evaluasi yang konsep dasarnya telah diuraikan pada Sub-bab 2.8, yaitu accuracy, precision, recall, dan F1-Score yang dihitung berdasarkan empat komponen confusion matrix — *True Positive* (TP), *True Negative* (TN), *False Positive* (FP), dan *False Negative* (FN):
>
> Accuracy = (TP + TN) / (TP + TN + FP + FN)
>
> Precision = TP / (TP + FP)
>
> Recall = TP / (TP + FN)
>
> F1-Score = 2 × (Precision × Recall) / (Precision + Recall)
>
> Karena klasifikasi pada penelitian ini bersifat biner (spam dan non-spam), presisi, recall, dan F1-Score di atas dihitung secara terpisah untuk masing-masing kelas dengan memperlakukan kelas yang bersangkutan sebagai kelas positif secara bergantian. Untuk memperoleh satu nilai tunggal yang merepresentasikan performa model terhadap kedua kelas secara seimbang — penting mengingat jumlah data non-spam lebih banyak dibandingkan data spam pada Tabel 4.3 — penelitian ini menggunakan skema rata-rata makro (*macro average*), yaitu rata-rata aritmetika F1-Score dari kedua kelas tanpa mempertimbangkan proporsi jumlah datanya:
>
> F1-macro = (F1-Score_spam + F1-Score_non-spam) / 2
>
> F1-macro dipilih sebagai metrik utama pada penelitian ini karena performanya tidak tenggelam oleh kelas mayoritas, sehingga digunakan sebagai metrik scoring pada pencarian hiperparameter (Sub-bab 4.5.3) dan validasi silang (Sub-bab 4.5.4), serta menjadi metrik pembanding utama pada seluruh skema pengujian di sub-bab ini.

---

### 2b. Substitusi angka nyata dari confusion matrix (Sub-bab 4.11.1)

**[LOKASI]** Sisipkan sebagai paragraf baru di antara Tabel 4.10 (Confusion Matrix) dan paragraf "Dari total 1.338 data uji, model hanya melakukan 9 kesalahan..." di Sub-bab 4.11.1 (hal. 96).

**[TEKS SISIPAN]**

> Berdasarkan persamaan yang diuraikan di awal Sub-bab 4.11, keempat metrik pada Tabel 4.9 dapat ditelusuri langsung dari nilai TP, TN, FP, dan FN pada Tabel 4.10. Nilai akurasi dihitung sebagai:
>
> Accuracy = (442 + 863) / (442 + 863 + 9 + 24) = 1.305 / 1.338 = 0,9753 (97,53%)
>
> Nilai presisi kelas spam:
>
> Precision = 442 / (442 + 9) = 442 / 451 = 0,98
>
> Nilai recall kelas spam:
>
> Recall = 442 / (442 + 24) = 442 / 466 = 0,95
>
> Nilai F1-Score kelas spam, dari rata-rata harmonik presisi dan recall di atas:
>
> F1-Score = 2 × (0,98 × 0,95) / (0,98 + 0,95) = 1,862 / 1,93 = 0,96
>
> Perhitungan yang identik berlaku untuk kelas non-spam dengan memperlakukan TN sebagai *True Positive* dan FP sebagai *False Negative* pada kelas tersebut, menghasilkan F1-Score non-spam sebesar 0,98. Nilai F1-macro pada Tabel 4.9 kemudian diperoleh dari rata-rata F1-Score kedua kelas:
>
> F1-macro = (0,96 + 0,98) / 2 = 0,97
>
> Nilai ini sedikit berbeda dari nilai F1-macro yang dilaporkan (0,9726) karena perhitungan aktual pada sistem menggunakan nilai presisi dan recall penuh sebelum dibulatkan menjadi dua angka desimal seperti pada Tabel 4.9.

Paragraf "Dari total 1.338 data uji..." yang sudah ada tetap dipertahankan setelah paragraf sisipan ini, tidak perlu diubah.

---

### 2c. Standar deviasi 5-fold CV — belum dijelaskan itu ukuran sebaran dari apa (Sub-bab 4.11.2)

**[LOKASI]** Sisipkan di Sub-bab 4.11.2 (hal. 96-97), di antara kalimat "...rata-rata F1-macro sebesar 0,9741 dengan standar deviasi 0,0030 (±0,30%)." dan kalimat "Standar deviasi yang sangat kecil ini membuktikan bahwa performa model stabil...".

**[TEKS SISIPAN]**

> Standar deviasi yang dilaporkan merupakan ukuran sebaran dari lima nilai F1-macro yang dihasilkan pada kelima fold, dihitung menggunakan persamaan standar deviasi:
>
> σ = √( Σ(xᵢ − x̄)² / n )
>
> dengan xᵢ adalah skor F1-macro pada fold ke-i, x̄ adalah rata-rata F1-macro dari kelima fold (0,9741), dan n adalah jumlah fold (5).

---

### 2d. Paired t-test / p-value — konsepnya belum pernah diperkenalkan sama sekali (Sub-bab 4.11.7)

Ini gap paling besar: istilah "uji-t berpasangan", "p-value", dan "signifikansi statistik" muncul langsung di hasil tanpa pengantar konsep sama sekali. Karena keputusan strukturnya "cukup di BAB IV", penjelasan konsepnya ditaruh sebagai paragraf pembuka di Sub-bab 4.11.7 sendiri, tepat sebelum hasil p-value-nya disajikan.

**[LOKASI]** Ganti paragraf pertama Sub-bab 4.11.7 (hal. 100) — yang sekarang cuma "Pengujian ini menjawab pertimbangan pada sub-bab 4.5.5 mengenai penggunaan stemming. Eksperimen dilakukan dengan membandingkan performa model tanpa stemming dan dengan stemming Sastrawi menggunakan 5-fold cross-validation, lalu diuji signifikansinya melalui paired t-test." — dengan versi berikut, yang menyisipkan penjelasan konsep sebelum kalimat terakhirnya:

**[TEKS PENGGANTI — BAB IV, Sub-bab 4.11.7]**

> Pengujian ini menjawab pertimbangan pada Sub-bab 4.5.5 mengenai penggunaan stemming. Eksperimen dilakukan dengan membandingkan performa model tanpa stemming dan dengan stemming Sastrawi menggunakan 5-fold cross-validation.
>
> Untuk memastikan bahwa selisih performa yang teramati bukan sekadar kebetulan akibat variasi acak antar fold, digunakan uji-t berpasangan (*paired t-test*), yaitu uji hipotesis yang membandingkan rata-rata dari dua kelompok data yang saling berpasangan atau berasal dari sumber pengukuran yang sama — dalam kasus ini, skor F1-macro dari fold cross-validation yang sama, diukur dengan dan tanpa stemming. Uji ini dirumuskan melalui dua hipotesis: H0 (tidak terdapat perbedaan rata-rata performa yang signifikan antara kedua kondisi) dan H1 (terdapat perbedaan rata-rata performa yang signifikan). Nilai statistik uji dihitung dengan persamaan:
>
> t = d̄ / (s_d / √n)
>
> dengan d̄ adalah rata-rata selisih skor F1-macro berpasangan antar fold, s_d adalah standar deviasi dari selisih tersebut, dan n adalah jumlah fold (5). Nilai t kemudian dikonversi menjadi p-value, yaitu probabilitas memperoleh selisih seperti yang teramati apabila H0 benar. Keputusan diambil dengan membandingkan p-value terhadap ambang signifikansi (α) sebesar 0,05: apabila p-value < 0,05, H0 ditolak dan perbedaan dianggap signifikan secara statistik; apabila p-value ≥ 0,05, H0 tidak dapat ditolak dan perbedaan dianggap tidak signifikan.
>
> Hasil eksperimen menunjukkan bahwa rata-rata F1-macro dengan stemming justru sedikit lebih rendah (selisih -0,0006), dan 4 dari 5 fold menunjukkan stemming berperforma lebih buruk. Uji statistik menghasilkan p-value = 0,3575, yang jauh di atas ambang signifikansi α = 0,05, sehingga H0 tidak dapat ditolak: perbedaan performa antara menggunakan dan tidak menggunakan stemming tidak signifikan secara statistik, dan kemungkinan besar hanya disebabkan oleh variasi acak antar fold.

Kalimat-kalimat setelahnya ("Berdasarkan temuan ini, stemming tidak diintegrasikan...") tetap dipertahankan tanpa perubahan.

> ⚠️ **Kalau mau tetap pakai sitasi buat definisi paired t-test, jangan pakai sitasi bikinan gua.** Paragraf di atas sengaja ditulis tanpa nama penulis buku statistik. Kalau dosen kamu suka semua konsep ada rujukan pustakanya, cari sendiri sumber yang benar-benar kamu pegang/baca (buku statistik dasar yang dipakai kampus, atau paper metodologi ML yang juga pakai paired t-test) — jangan sampai ditanya balik soal isi buku yang kamu sendiri belum pernah baca.

---

### 2e. Skema pembobotan `spam_score` — angka "80" jadi bukan angka ajaib lagi (Sub-bab 4.3.1)

**[LOKASI]** Ganti paragraf kedua Sub-bab 4.3.1 (hal. 78) — yang sekarang: "Setiap komentar yang diperoleh diberi skor heuristik (spam_score) yang dihitung secara otomatis berdasarkan kehadiran sinyal-sinyal primer seperti nama brand judi online dan tautan kontak, serta sinyal sekunder seperti rasio emoji dan pola karakter Unicode." — dengan versi berikut yang langsung membawa rincian bobotnya, tanpa perlu rujuk ke bab lain:

**[TEKS PENGGANTI — BAB IV, Sub-bab 4.3.1]**

> Setiap komentar yang diperoleh diberi skor heuristik (spam_score) yang dihitung secara otomatis menggunakan skema penjumlahan bobot (*weighted additive scoring*) terhadap delapan sinyal yang diperiksa pada teks komentar hasil normalisasi. Setiap sinyal yang terdeteksi menyumbangkan bobot tertentu terhadap skor akhir, dengan skor total dibatasi maksimum 100. Rincian sinyal dan bobotnya disajikan pada Tabel 4.x.
>
> Tabel 4.x Skema Pembobotan Skor Heuristik (spam_score)
>
> | Sinyal | Kategori | Deskripsi | Bobot |
> |---|---|---|---|
> | brand_pattern | Primer | Pola nama brand judi + angka khas (mis. "SLOT777", "MAXWIN88") | +40 |
> | contact_link | Primer | Tautan atau nomor kontak (mis. "wa.me/...", "bit.ly/...") | +40 |
> | soft_brand_testimonial | Primer | Nama + 2 digit angka disertai kalimat bernuansa testimoni (mis. "ALEXIS17 sukses bantu") | +35 |
> | obfuscated_keyword | Sekunder | Kata kunci judi dengan teknik obfuscation (mis. "g a c o r", "m@xw!n") | +30 |
> | plain_keyword | Sekunder | Kata kunci judi tanpa obfuscation (hanya dihitung bila obfuscation tidak terdeteksi) | +20 |
> | high_symbol_ratio | Sekunder | Rasio karakter simbol lebih dari 15% dari total karakter | +20 |
> | emoji_spam | Tersier | Dua atau lebih emoji berurutan | +15 |
> | excessive_caps | Tersier | Lebih dari 50% karakter berupa huruf kapital | +10 |
>
> Sinyal primer merupakan indikator kuat keberadaan promosi judi online, sedangkan sinyal sekunder dan tersier berfungsi sebagai bukti pendukung. Ambang skor 80 yang digunakan pada tahap penyaringan pertama (dijelaskan pada paragraf berikutnya) dipilih karena nilai tersebut hanya dapat dicapai apabila komentar memiliki minimal satu sinyal primer yang kuat disertai sinyal pendukung tambahan — misalnya komentar dengan brand_pattern (+40) dan contact_link (+40) yang menghasilkan skor tepat 80 — sehingga meminimalkan risiko kesalahan label akibat sinyal tunggal yang lemah.

Kalimat-kalimat setelahnya (tentang tahap penyaringan dua tahap dan mekanisme *rescue*) tetap dipertahankan tanpa perubahan, karena sudah konsisten dengan tabel di atas.

*(Catatan kecil, bukan error: kode di repo `scraper-judol-yt-comment` yang sedang aktif dikembangkan sekarang pakai threshold berbeda (30/10) — itu versi eksperimen lanjutan (lihat komentar "TODO.md Fase 1"), BUKAN versi yang dipakai untuk generate dataset final di skripsi. Dataset final (6.690 baris) tetap pakai threshold 80 sesuai `DATASET_LOG.md`. Aman, tapi kalau ditanya dosen soal ini, jelasin bedanya biar tidak keliatan kontradiksi.)*

---

### 2f. Ringkasan prioritas & checklist penyisipan

Semua di bawah ini masuk BAB IV — tidak ada perubahan ke BAB II. Kalau waktu terbatas sebelum bimbingan berikutnya, urutan prioritas + checklist tempel:

- [ ] **2d** — Paired t-test, ganti paragraf pertama Sub-bab 4.11.7 — paling exposed karena konsep statistiknya belum pernah dijelaskan sama sekali.
- [ ] **2a** — Paragraf pembuka Sub-bab 4.11 (definisi Accuracy/Precision/Recall/F1-macro sekaligus) — jadi fondasi buat 2b, kerjakan sebelum 2b.
- [ ] **2e** — spam_score ambang 80, ganti paragraf kedua Sub-bab 4.3.1 — paling gampang dibenahi dan paling terlihat "angka ajaib" buat pembaca yang belum lihat kode.
- [ ] **2b** — Substitusi angka confusion matrix di Sub-bab 4.11.1 — tinggal tempel setelah 2a selesai.
- [ ] **2c** — Standar deviasi CV di Sub-bab 4.11.2 — kecil, cukup 1 paragraf.

**Ingat:** setelah nambah paragraf pembuka baru di 4.11 dan tabel baru di 4.3.1, nomor tabel di BAB IV setelahnya (Tabel 4.x dst) akan geser — cek ulang seluruh cross-reference nomor tabel/gambar di BAB IV (dan bagian lain yang merujuk ke situ, misalnya Daftar Tabel) sebelum submit final.

---

## 3. Yang Harus Di-Take Out dari BAB II

Karena instruksi sebelumnya (versi awal chat ini) sudah kamu terapkan ke BAB II, dan sekarang kita pindah semua ke BAB IV, ada **3 blok** yang perlu dihapus lagi dari BAB II supaya kontennya nggak dobel (sama persis muncul di BAB II dan BAB IV). Gua kasih ciri teks pembuka & penutup tiap blok biar gampang di-cari (Ctrl+F) di dokumen kamu — gua nggak pegang file sumber kamu (Word/Google Docs), jadi patokan pencarian di bawah ini yang paling aman, bukan nomor halaman (nomor halaman kemungkinan sudah geser sejak kamu edit).

### 3a. Hapus dari Sub-bab 2.8 (Evaluasi Model Klasifikasi)

Paragraf yang **dimulai** dengan:
> "Pada klasifikasi biner seperti spam dan non-spam, keempat metrik evaluasi di atas dihitung secara terpisah untuk masing-masing kelas..."

dan **berakhir** dengan:
> "...sehingga F1-macro dipilih sebagai metrik utama dalam proses pencarian hiperparameter (Sub-bab 4.5.3) dan validasi silang (Sub-bab 4.5.4)."

Hapus seluruh paragraf ini (termasuk 2 baris rumus F1-macro di tengahnya). Definisi F1-macro versi baru sudah pindah ke paragraf pembuka Sub-bab 4.11 (lihat 2a di atas).

### 3b. Hapus sub-bab 2.8.1 "Uji Signifikansi Statistik (Paired t-test)" — seluruhnya

Kalau kamu kasih nomor sub-bab sendiri (2.8.1), hapus **seluruh sub-bab ini**, dari judulnya sampai paragraf terakhir yang isinya aturan keputusan p-value (dan termasuk kalimat sitasi yang kamu tambahkan sendiri di situ, kalau ada). Cirinya, paragraf **pertama** dimulai dengan:
> "Ketika dua konfigurasi model dibandingkan pada dataset yang identik..."

dan paragraf **terakhir** berakhir dengan:
> "...H0 tidak dapat ditolak dan perbedaan dianggap tidak signifikan, sehingga kemungkinan besar hanya disebabkan oleh variasi acak."

**Karena ini sub-bab nested (2.8.1, bukan 2.9 baru), menghapusnya TIDAK menggeser nomor sub-bab 2.9, 2.10, 2.11 dst setelahnya** — aman dari sisi renumbering BAB II. Konsep ini sekarang jadi paragraf pembuka Sub-bab 4.11.7 (lihat 2d di atas).

### 3c. Hapus dari Sub-bab 2.11 (Web Scraping dan Analisis Heuristik)

Paragraf + tabel yang **dimulai** dengan:
> "Pada penelitian ini, skor heuristik dihitung menggunakan skema penjumlahan bobot (*weighted additive scoring*) terhadap delapan sinyal..."

termasuk **Tabel 2.x "Skema Pembobotan Skor Heuristik"** di bawahnya, dan **berakhir** dengan:
> "...sedangkan komentar yang hanya mengandung kata kunci umum (plain_keyword, +20) dan rasio simbol tinggi (high_symbol_ratio, +20) memperoleh skor 40."

Hapus paragraf dan tabel ini seluruhnya. **Karena ini menghapus sebuah tabel (bukan cuma teks), cek ulang penomoran Tabel 2.x setelahnya di BAB II** (kalau ada tabel lain sesudah 2.11 yang nomornya lebih besar dari tabel yang dihapus, nomornya perlu digeser turun 1) — beda dengan 3b yang aman, ini satu-satunya bagian di daftar hapus yang berisiko menggeser nomor. Tabelnya sendiri sekarang pindah jadi Tabel 4.x di Sub-bab 4.3.1 (lihat 2e di atas).

### 3d. Checklist hapus dari BAB II

- [ ] **3a** — Paragraf F1-macro di Sub-bab 2.8 (aman, nggak ada renumbering)
- [ ] **3b** — Sub-bab 2.8.1 Paired t-test, seluruhnya (aman, nggak ada renumbering karena nested)
- [ ] **3c** — Paragraf + Tabel 2.x skema bobot spam_score di Sub-bab 2.11 (⚠️ cek ulang nomor tabel Bab II setelahnya)
