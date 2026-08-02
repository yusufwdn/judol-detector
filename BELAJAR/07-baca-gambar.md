# 07 — Cara Membaca Gambar di Skripsi

> Tiap gambar: cara membacanya, nilainya dari mana, kenapa harus ada di skripsi, dan apa yang mungkin ditanyakan penguji.

Gambar itu sasaran empuk penguji. Alasannya sederhana: gambar **kelihatan mudah ditanya**. Penguji tinggal menunjuk satu titik dan bertanya "ini apa?" — tanpa perlu menyiapkan pertanyaan rumit.

Karena itu tiap gambar di skripsimu harus bisa kamu jelaskan dalam tiga lapis:
1. **Ini gambar apa** — satu kalimat
2. **Cara membacanya** — sumbunya apa, simbolnya apa artinya
3. **Kenapa ada di skripsi** — klaim apa yang didukung gambar ini

⚠️ **Baca dulu bagian F di akhir dokumen ini.** Ada tiga ketidakcocokan antara gambar dan kondisi sebenarnya yang perlu kamu putuskan sebelum sidang.

---

# BAGIAN A — Gambar alur dan arsitektur

## Gambar 4.1 — Alur Pelatihan Model

📄 Sub-bab 4.4.1

**Ini gambar apa:** diagram alur (*flowchart*) yang menunjukkan sembilan langkah dari pengumpulan data sampai model tersimpan.

**Cara membacanya:** ikuti panah dari atas ke bawah. Ada satu percabangan berbentuk belah ketupat di tengah — itu titik keputusan.

**Isi tiap kotak dan asalnya:**

| Kotak | Isinya | Sumber di kode |
|---|---|---|
| 1. Pengumpulan Data | Ambil komentar YouTube | `scraper/index.js` |
| 2. Persiapan Dataset | Saring & beri label | `src/prepare_dataset.py` |
| ◇ `spam_score ≥ 80?` | Percabangan: lolos atau ditolak | `prepare_dataset.py:155` |
| 3. Prapemrosesan | 7 tahap normalisasi teks | `src/preprocessing.py` |
| 4. Ekstraksi TF-IDF | `ngram=(1,2)`, `max_features=10.000`, dll | `train.py:63–68` |
| 5. Pembagian Dataset | 80% latih / 20% uji, `stratify=y` | `train.py:197` |
| 6. Pencarian Parameter | GridSearchCV, C: 0,01–100 | `train.py:233` |
| 7. Pelatihan Model | Linear SVM, `class_weight=balanced` | `train.py:334` |
| 8. Evaluasi | Data uji + hard test set | `train.py:409` |
| 9. Simpan Model | `svm_model.joblib` | `train.py:439` |

🔍 **Kenapa gambar ini ada di skripsi:** untuk membuktikan metodologimu **sistematis dan bisa diulang**. Tanpa gambar ini, pembaca harus menyusun sendiri urutannya dari teks yang bertebaran.

Perhatikan bentuk kotak nomor 9 — berbentuk silinder, bukan persegi. Itu simbol baku *flowchart* untuk **penyimpanan data**, bukan proses. Detail kecil, tapi kalau ditanya kamu bisa jawab.

❓ **Yang mungkin ditanya:** *"Kenapa ada percabangan `spam_score ≥ 80`? Kalau di bawah 80 langsung dibuang?"*
> "Tidak selalu dibuang, Pak. Ambang 80 adalah penyaring utama, tapi ada tahap kedua berupa penyelamatan: komentar berskor rendah yang mengandung pola nama situs judi yang jelas tetap ditandai spam. Itu karena banyak spam asli hanya memicu satu sinyal saja sehingga skornya rendah."

---

## Gambar 4.2 — Alur Inferensi Real-Time

📄 Sub-bab 4.4.2

**Ini gambar apa:** alur yang terjadi **saat sistem dipakai**, berbeda dari Gambar 4.1 yang terjadi saat pelatihan.

🔍 **Kenapa perlu dua gambar terpisah?** Ini pertanyaan yang bagus untuk dipahami. Karena keduanya berjalan di **waktu yang berbeda**:

- **Gambar 4.1 (pelatihan)** — dijalankan sekali, manual, makan waktu menit, hasilnya berkas model
- **Gambar 4.2 (inferensi)** — dijalankan tiap kali ada komentar baru, otomatis, harus selesai dalam milidetik

**Analogi:** Gambar 4.1 itu koki berlatih resep sampai jago lalu menuliskannya. Gambar 4.2 itu dapur memasak pesanan berbekal buku resep tadi. Yang satu lama tapi sekali, yang satu cepat tapi berulang terus.

**Titik yang paling penting di gambar ini:** langkah prapemrosesan. Perhatikan bahwa gambar ini memakai `preprocessing.py` **yang sama** dengan Gambar 4.1. Itu bukan kebetulan — itulah jaminan konsistensi pelatihan-prediksi yang jadi argumen arsitekturmu.

❓ **Yang mungkin ditanya:** *"Kenapa alurnya dipisah jadi dua gambar?"*
> "Karena keduanya berjalan pada waktu dan konteks yang berbeda, Pak. Alur pelatihan dijalankan sekali secara manual dan menghasilkan berkas model. Alur inferensi dijalankan berulang setiap ada komentar baru, dan harus selesai dalam hitungan milidetik. Yang menghubungkan keduanya adalah berkas model dan berkas prapemrosesan yang sama persis."

---

## Gambar 4.3 — Arsitektur Komponen Sistem

📄 Sub-bab 4.6

**Ini gambar apa:** peta seluruh komponen sistem beserta hubungannya. Gambar paling padat informasi di skripsimu.

**Cara membacanya — perhatikan pembagian besarnya dulu:**

```
┌─ Fase Pengembangan ─┐   ┌─────── Fase Produksi ────────┐
│  Scraper            │   │  Sisi Klien  │  Sisi Peladen │
│  Training Pipeline  │   │  (Chrome)    │  (FastAPI)    │
└─────────────────────┘   └──────────────────────────────┘
```

Kotak kiri = yang dijalankan sekali saat membangun. Kotak kanan = yang berjalan saat sistem dipakai.

**Cara membaca jenis panahnya:**
- **Panah putus-putus** = aliran berkas (misalnya `svm_model.joblib` dari Training Pipeline ke server)
- **Panah penuh dua arah** = komunikasi HTTP antara ekstensi dan server
- **Silinder** = penyimpanan (berkas model dan `comments.csv`)

**Angka yang muncul di gambar ini:**
- `6.690 baris (2.332 spam + 4.358 non-spam)` — dari `data/comments.csv`
- `localhost:8000` — alamat server
- `≤50 komentar` pada endpoint batch — dari `content.js:380`

🔍 **Kenapa gambar ini ada:** untuk menjawab pertanyaan "sistem ini terdiri dari apa saja dan bagaimana mereka terhubung" dalam satu pandangan. Ini gambar yang paling sering ditunjuk penguji karena paling informatif.

❓ **Yang mungkin ditanya:** *"Kenapa Scraper ada di fase pengembangan, bukan produksi?"*
> "Karena pengambilan data hanya dilakukan sekali saat membangun dataset, Pak, tidak berjalan saat sistem dipakai. Pengguna ekstensi tidak menjalankan scraper sama sekali. Yang berjalan saat produksi hanya ekstensi di sisi klien dan server klasifikasi."

⚠️ **Gambar ini punya tiga ketidakcocokan dengan kondisi sebenarnya.** Lihat Bagian F.

---

# BAGIAN B — Diagram UML

Tiga diagram ini menjawab tiga pertanyaan berbeda. Kalau ditanya "kenapa perlu tiga?", jawabannya:

| Diagram | Menjawab pertanyaan |
|---|---|
| Use Case (4.4) | **Siapa** bisa melakukan **apa** |
| Activity (4.5) | **Bagaimana urutan** prosesnya |
| Sequence (4.6) | **Siapa mengirim pesan apa** ke siapa, dan kapan |

## Gambar 4.4 — Use Case Diagram

📄 Sub-bab 4.7

**Cara membacanya:**
- **Orang lidi** = aktor. Di sistemmu cuma ada satu: **Pengguna**
- **Kotak besar** = batas sistem. Apa yang di dalam = tanggung jawab sistemmu; di luar = bukan
- **Elips** = use case, yaitu satu fungsi yang bisa dijalankan
- **Garis** = aktor bisa mengakses use case itu

**Lima use case di sistemmu:**
1. Menyaring Komentar Spam
2. Mengklasifikasikan Teks
3. Mengatur Confidence Threshold
4. Memantau Statistik Deteksi
5. Melaporkan Kesalahan Klasifikasi

**Dua jenis hubungan yang WAJIB kamu bisa jelaskan** — ini pertanyaan klasik:

**«include»** — dari *Menyaring Komentar Spam* ke *Mengklasifikasikan Teks*
🎯 Artinya **wajib selalu terjadi**. Setiap kali sistem menyaring komentar, dia **pasti** menjalankan klasifikasi. Tidak ada penyaringan tanpa klasifikasi.

**«extend»** — dari *Melaporkan Kesalahan Klasifikasi* ke *Menyaring Komentar Spam*
🎯 Artinya **opsional, hanya pada kondisi tertentu**. Pengguna boleh melaporkan kesalahan, tapi boleh juga tidak. Penyaringan tetap berjalan normal tanpa itu.

**Cara mengingatnya:** *include* itu **selalu**, *extend* itu **kadang**.

🔍 **Perhatikan detail ini:** *Menyaring Komentar Spam* tidak terhubung langsung ke aktor lewat garis biasa. Itu **disengaja** — proses tersebut berjalan **otomatis** saat pengguna membuka halaman, bukan karena pengguna menekan tombol.

❓ **Yang mungkin ditanya:** *"Apa bedanya include dan extend?"*
> "Include berarti hubungan wajib — use case utama selalu memanggil yang di-include. Dalam sistem ini, menyaring komentar selalu memerlukan klasifikasi teks, tidak bisa tidak. Sedangkan extend berarti opsional, hanya terjadi pada kondisi tertentu. Melaporkan kesalahan klasifikasi hanya terjadi kalau pengguna memilih melakukannya, dan penyaringan tetap berjalan normal tanpa itu."

❓ **Yang mungkin ditanya:** *"Kenapa aktornya cuma satu?"*
> "Karena sistem ini berjalan sepenuhnya di sisi klien, Pak, dan tidak punya pembagian peran seperti admin atau operator. Semua fungsi tersedia untuk pengguna yang sama. Server bukan aktor karena dia bagian dari sistem, bukan pihak di luar sistem."

---

## Gambar 4.5 — Activity Diagram

📄 Sub-bab 4.8

**Cara membacanya:** diagram ini memakai format ***swimlane*** — kolom vertikal yang membagi tanggung jawab. Ada tiga jalur:

| Jalur | Tanggung jawabnya |
|---|---|
| Pengguna YouTube | Membuka halaman, menggulir komentar |
| Ekstensi Chrome | Mendeteksi komentar baru, mengirim, menyembunyikan |
| Server API | Membersihkan teks, mengklasifikasi, mengembalikan hasil |

🔍 **Kenapa pakai swimlane?** Supaya terlihat jelas **siapa mengerjakan apa**. Tanpa pembagian jalur, semua langkah tampak dikerjakan satu entitas — padahal ini sistem terdistribusi dengan tiga pihak.

**Simbol yang perlu kamu kenali:**
- Lingkaran hitam penuh = titik awal
- Lingkaran hitam bertepi = titik akhir
- Persegi panjang tumpul = aksi
- Belah ketupat = percabangan keputusan

❓ **Yang mungkin ditanya:** *"Apa bedanya activity diagram dengan flowchart di Bab III?"*
> "Flowchart di Bab III menggambarkan alur sistem yang sedang berjalan, yaitu mekanisme filter milik YouTube. Sedangkan activity diagram ini menggambarkan alur sistem yang saya usulkan, dan memakai format swimlane untuk memperlihatkan pembagian tanggung jawab antara pengguna, ekstensi, dan server."

---

## Gambar 4.6 — Sequence Diagram

📄 Sub-bab 4.9

**Cara membacanya — ini yang paling sering salah dibaca:**

- **Sumbu horizontal** = objek atau komponen yang terlibat
- **Sumbu vertikal** = **WAKTU**, mengalir dari atas ke bawah
- **Garis putus-putus vertikal** = *lifeline*, umur objek
- **Persegi panjang tipis** di atas lifeline = *activation bar*, periode objek sedang aktif bekerja
- **Panah horizontal** = pesan yang dikirim

**Tiga jenis panah:**
| Bentuk | Nama | Artinya |
|---|---|---|
| Panah penuh | *synchronous* | Pengirim **menunggu** balasan |
| Panah putus-putus | *return* | Balasannya |
| Panah terbuka | *asynchronous* | Pengirim **tidak menunggu**, lanjut kerja |

🔍 **Bedanya dengan activity diagram:** activity fokus pada **urutan langkah**, sequence fokus pada **percakapan antar komponen beserta waktunya**. Activity menjawab "apa yang terjadi", sequence menjawab "siapa memanggil siapa, dan menunggu atau tidak".

❓ **Yang mungkin ditanya:** *"Kenapa ada panah yang putus-putus dan ada yang penuh?"*
> "Panah penuh berarti pesan synchronous — pengirim menunggu balasan sebelum melanjutkan. Panah putus-putus adalah balasan atau return dari pemanggilan tersebut. Dalam sistem ini, ekstensi mengirim permintaan klasifikasi lalu menunggu hasilnya sebelum bisa menyembunyikan komentar."

---

# BAGIAN C — Grafik hasil ⭐

**Ini bagian terpenting.** Grafik memuat angka, dan angka itulah yang paling sering dikejar penguji.

## Gambar 4.7 — Confusion Matrix (heatmap)

📄 Sub-bab 4.10.1

**Cara membacanya:**
- **Baris** = label sebenarnya
- **Kolom** = tebakan model
- **Diagonal** (kiri-atas dan kanan-bawah) = **tebakan benar**
- **Di luar diagonal** = **kesalahan**
- **Warna makin gelap** = angkanya makin besar

```
                Prediksi non_spam   Prediksi spam
Aktual non_spam       863                9
Aktual spam            24               442
```

**Cara cepat menilai gambar ini:** kalau warna gelap berkumpul di diagonal, model bekerja baik. Kalau warna gelap tersebar ke luar diagonal, model bermasalah. Di gambarmu, dua kotak diagonal jauh lebih gelap — itu tanda baik.

**Dari mana angkanya:** `train.py:418` → `confusion_matrix(y_test, y_pred, labels=labels)`
Jumlah keempatnya = 863+9+24+442 = **1.338** = jumlah data uji.

🔍 **Kenapa perlu heatmap, padahal sudah ada Tabel 4.11 yang isinya sama?** Karena tabel memberi angka persis, gambar memberi kesan cepat. Penguji yang melirik sekilas langsung tahu modelnya bagus dari sebaran warnanya, tanpa membaca angka.

❓ **Yang mungkin ditanya:** *"Kotak mana yang paling mengkhawatirkan?"*
> "Kotak kanan atas, Pak — 9 false positive, yaitu komentar normal yang ikut disembunyikan. Itu yang paling mengganggu pengguna. Sedangkan 24 false negative di kiri bawah adalah spam yang lolos. Keduanya kesalahan, tapi dampaknya berbeda: yang satu merugikan pengguna tak bersalah, yang satu menggagalkan tujuan sistem."

---

## Gambar 4.8 — F1-macro per Fold

📄 Sub-bab 4.10.2

**Cara membacanya:**
- **Sumbu X** = lima putaran cross-validation (Fold 1 sampai 5)
- **Sumbu Y** = skor F1-macro
- **Batang** = skor tiap putaran
- **Garis putus-putus horizontal** = rata-rata (0,9741)
- **Pita abu-abu di sekitar garis** = rentang ± simpangan baku (0,0030)

**Angka tiap batang:** 0,9734 · 0,9700 · 0,9743 · 0,9734 · 0,9793

🔍 **Yang harus kamu lihat dari gambar ini:** perhatikan kelima batang **hampir sama tinggi**. Itulah pesan utamanya. Kalau ada satu batang yang jauh lebih pendek, artinya performa model bergantung pada keberuntungan pembagian data.

**Kenapa perlu grafik, bukan cukup tulis "0,9741 ± 0,0030"?** Karena angka rata-rata menyembunyikan sebarannya. Rata-rata 0,9741 bisa berasal dari lima nilai yang seragam, atau dari empat nilai tinggi dan satu yang jeblok. Grafik memperlihatkan bedanya seketika.

**Dari mana angkanya:** `train.py:128` → `cross_val_score(..., cv=5, scoring="f1_macro")`

❓ **Yang mungkin ditanya:** *"Kenapa fold 5 paling tinggi?"*
Jawaban jujur:
> "Variasi antar fold itu wajar karena tiap fold memakai pembagian data yang berbeda, Pak. Yang penting selisihnya sangat kecil — simpangan bakunya hanya 0,0030. Kalau selisihnya besar, itu baru menandakan ada masalah kestabilan."

Jangan mengarang alasan spesifik kenapa fold 5 lebih tinggi. Itu variasi acak biasa.

---

## Gambar 4.9 — Hasil GridSearchCV

📄 Sub-bab 4.10.3

**Cara membacanya:**
- **Sumbu X** = nilai C, dalam **skala logaritmik** (0,01 → 0,1 → 1 → 10 → 100)
- **Sumbu Y** = F1-macro rata-rata dari 5-fold CV
- **Titik merah besar** = nilai yang terpilih, yaitu **C = 1**
- **Garis tegak kecil pada tiap titik** = *error bar*, menunjukkan simpangan baku

**Nilai tiap titik:**

| C | F1-macro | Catatan |
|---|---|---|
| 0,01 | ~0,735 | Sangat buruk, error bar-nya panjang |
| 0,1 | ~0,947 | Naik tajam |
| **1** | **~0,972** | **Puncak — terpilih** |
| 10 | ~0,967 | Mulai turun sedikit |
| 100 | ~0,963 | Turun lagi |

🔍 **Ini grafik yang paling "bercerita" di skripsimu.** Bentuk kurvanya memperlihatkan pertukaran parameter C secara visual:

- **Kiri (C kecil)** — model terlalu longgar, tidak cukup tegas memisahkan. Skornya jeblok, dan error bar-nya panjang artinya hasilnya juga tidak stabil.
- **Puncak (C = 1)** — keseimbangan terbaik.
- **Kanan (C besar)** — model terlalu keras menghukum kesalahan, mulai menghafal data latih. Skornya turun perlahan. Inilah **overfitting yang terlihat secara visual**.

**Kenapa sumbu X pakai skala logaritmik?** Karena nilainya melompat kelipatan sepuluh. Kalau memakai skala biasa, titik 0,01 / 0,1 / 1 akan menumpuk berdempetan di kiri sementara 100 jauh sendirian di kanan.

**Dari mana angkanya:** `train.py:233` (daftar kandidat) dan `train.py:245` (pencariannya)

❓ **Yang mungkin ditanya:** *"Kenapa skornya turun setelah C = 1?"*
> "Karena C mengatur seberapa keras model menghukum kesalahan saat belajar. C yang terlalu besar membuat model memaksakan diri agar tidak ada kesalahan sama sekali di data latih, termasuk menghafal kasus-kasus yang tidak umum. Akibatnya performanya di data baru justru menurun. Itu gejala overfitting, dan di grafik ini terlihat sebagai penurunan setelah titik puncak."

**Ini jawaban yang bagus** karena kamu menjelaskan konsep sekaligus menunjuk buktinya di gambar.

---

## Gambar 4.10 — Perbandingan Stemming

📄 Sub-bab 4.10.7

**Cara membacanya:**
- **Sumbu X** = lima fold
- **Sumbu Y** = F1-macro
- **Dua batang berpasangan** di tiap fold — kiri tanpa stemming, kanan dengan stemming
- **Judul grafik memuat hasil uji statistik:** `paired t-test: p=0.3575, tidak signifikan`

**Yang harus kamu lihat:** batangnya **hampir sama tinggi** di semua fold. Bahkan di fold 5, yang dengan stemming justru sedikit lebih tinggi. Ketidakkonsistenan arah itulah bukti visual bahwa tidak ada pola yang jelas.

🔍 **Kenapa disebut "berpasangan" (*paired*)?** Karena kedua kondisi diuji pada **pembagian data yang sama persis**. Fold 1 tanpa stemming dan fold 1 dengan stemming memakai data yang identik — yang berbeda hanya perlakuannya.

**Analogi SE:** ini seperti *benchmark* dua versi kode pada mesin dan beban yang sama persis. Kalau lingkungannya berbeda, perbandingannya tidak sah.

❓ **Yang mungkin ditanya:** *"Kalau di fold 5 stemming lebih tinggi, berarti kadang membantu dong?"*
> "Justru itu yang menunjukkan tidak ada pola konsisten, Pak. Di empat fold hasilnya sedikit lebih rendah, di satu fold sedikit lebih tinggi. Kalau stemming benar-benar membantu, seharusnya konsisten unggul di semua fold. Uji t berpasangan mengonfirmasi hal ini dengan p-value 0,3575, jauh di atas ambang 0,05, sehingga perbedaannya belum bisa dianggap nyata."

---

# BAGIAN D — Gambar tampilan

| Gambar | Isinya | Fungsinya di skripsi |
|---|---|---|
| 4.11 | Antarmuka popup ekstensi | Menunjukkan kendali yang tersedia bagi pengguna |
| 4.12 | Halaman YouTube dengan ekstensi aktif | Menunjukkan sistem bekerja di lingkungan nyata |
| 4.13 | Rancangan antarmuka popup | Rancangan **sebelum** dibuat |
| 4.14 | Hasil mode Redupkan | Bukti fungsi berjalan |
| 4.15 | Hasil mode Hilangkan | Bukti fungsi berjalan |

🔍 **Kenapa ada 4.13 (rancangan) padahal sudah ada 4.11 (hasil jadi)?** Karena keduanya menunjukkan tahap berbeda dalam metode Waterfall: 4.13 adalah keluaran tahap **perancangan**, 4.11 keluaran tahap **implementasi**. Menampilkan keduanya membuktikan implementasimu mengikuti rancangan, bukan dikerjakan asal jalan.

❓ **Yang mungkin ditanya:** *"Apa bedanya mode Redupkan dan Hilangkan? Kenapa perlu dua?"*
> "Mode Redupkan menyamarkan komentar sampai transparansi 15% dan tetap menampilkan badge persentase keyakinan, sehingga pengguna masih bisa mengkliknya untuk melihat isi aslinya. Mode Hilangkan menyembunyikan komentar sepenuhnya. Keduanya disediakan karena ada pertukaran antara kebersihan tampilan dan kesempatan koreksi — kalau model salah menuduh, mode Redupkan masih memberi jalan bagi pengguna untuk memeriksanya."

---

# BAGIAN E — Gambar BAB II dan III

Lebih jarang ditanya karena sifatnya teori, tapi tetap perlu dikenali.

| Gambar | Isinya | Yang perlu diingat |
|---|---|---|
| 2.1 | Contoh matriks bobot TF-IDF | Contoh perhitungan: kata "slot" bobotnya 0,176, kata "ini" bobotnya 0 |
| 2.2 | Hyperplane dan margin | Titik dua warna, garis pemisah, dan pita margin. Titik di tepi pita = *support vector* |
| 2.3 | Tahapan Waterfall | Lima tahap berurutan: analisis → perancangan → implementasi → pengujian → pemeliharaan |
| 2.4–2.6 | Simbol UML | Simbol use case, activity, sequence |
| 3.1 | Struktur organisasi YouTube | Konteks objek penelitian |
| 3.2 | Flowchart sistem berjalan | **Menunjukkan di mana filter YouTube gagal** |

## Gambar 3.2 layak perhatian khusus

Ini gambar yang menjelaskan **kenapa penelitianmu perlu ada**. Alurnya:

```
Komentar dikirim → Server YouTube menerima
        ↓
Pencocokan dengan kamus kata terlarang
        ↓
    ◇ Mengandung kata terlarang secara presisi?
     Ya ↓                    ↓ Tidak (Terjadi Obfuscation)
  Diblokir            Komentar diotorisasi → TAMPIL
```

🔍 **Titik kegagalannya ada di percabangan itu.** Karena pencocokannya harfiah, teks yang disamarkan masuk ke jalur "Tidak" dan lolos tampil. Seluruh skripsimu adalah upaya menutup celah tersebut.

❓ **Yang mungkin ditanya:** *"Dari gambar ini, di mana tepatnya letak masalahnya?"*
> "Di percabangan pencocokan kata, Pak. Filter YouTube membandingkan teks komentar dengan kamus kata terlarang secara harfiah. Ketika spammer mengganti huruf dengan karakter Unicode yang mirip, susunan bytenya berbeda sehingga pencocokan gagal, dan komentar lolos ke jalur otorisasi. Sistem yang saya usulkan menambahkan tahap normalisasi sebelum klasifikasi, supaya teks yang disamarkan dikembalikan dulu ke bentuk standar."

---

# BAGIAN F — ⚠️ Ketidakcocokan yang perlu kamu putuskan

Saya membandingkan isi gambar dengan kode dan naskah terkini. Ada **tiga ketidakcocokan**. Semuanya bisa ditanyakan penguji, jadi sebaiknya diputuskan sebelum sidang.

## ① Gambar 4.1 masih menulis "Web Scraping"

Kotak nomor 1 berbunyi:
> **1. Pengumpulan Data (Web Scraping via Node.js)**

Padahal naskah skripsimu **sudah diperbaiki** menjadi YouTube Data API v3 — itu perbaikan temuan K4. Kode juga memang memanggil API resmi, bukan mengikis HTML.

🔴 **Ini yang paling penting dari ketiganya**, karena menyangkut argumen kelayakan hukum di Sub-bab 4.12.3. Kamu berargumen sistemmu legal **justru karena** memakai API resmi — lalu ada gambar yang menulis "web scraping".

**Perbaikannya:** ubah teks kotak jadi *"Pengumpulan Data (YouTube Data API v3 via Node.js)"*.

## ② Gambar 4.3 menulis "Ekstraksi komentar via YouTube DOM"

Masalah yang sama pada kotak Scraper. "YouTube DOM" berarti membaca struktur halaman — itu pengikisan HTML, bukan API.

**Perbaikannya:** ubah jadi *"Ekstraksi komentar via YouTube Data API v3"*.

## ③ Gambar 4.3 memuat dua detail kecil yang keliru

| Tertulis di gambar | Kondisi sebenarnya | Sumber |
|---|---|---|
| Slider confidence threshold **(0–100%)** | **50–95%** | `popup.html:355` (`min="50"`) |
| Hak akses: activeTab, **scripting**, storage | Hanya **storage, activeTab** | `manifest.json` |

Keduanya kecil, tapi kalau penguji membandingkan gambar dengan kode, ketidakcocokan sekecil apa pun bisa memicu pertanyaan lanjutan.

---

## Kalau tidak sempat memperbaiki gambarnya

Prioritaskan **nomor ① dan ②** — dua itu menyangkut argumen legalitas.

Kalau benar-benar tidak sempat, minimal siapkan jawabannya:
> "Betul, Pak, keterangan pada gambar itu masih memakai istilah lama dari draf awal. Yang benar dan konsisten dengan naskah serta implementasinya adalah YouTube Data API v3 resmi, bukan pengikisan HTML. Ini kekeliruan penulisan pada gambar yang belum sempat saya perbarui."

Mengakui kekeliruan kecil dengan tenang jauh lebih baik daripada berusaha membenarkan sesuatu yang jelas tidak cocok dengan kode.

**Kalau mau, saya bisa bantu memperbaiki ketiga gambar itu** — tinggal bilang.

---

# Ringkasan: satu kalimat per gambar

| Gambar | Kalau ditanya "ini gambar apa?" |
|---|---|
| 4.1 | Sembilan langkah pelatihan model, dari pengumpulan data sampai model tersimpan |
| 4.2 | Alur saat sistem dipakai, berjalan tiap ada komentar baru |
| 4.3 | Peta seluruh komponen: scraper, pelatihan, ekstensi, dan server |
| 4.4 | Lima fungsi sistem dari sudut pandang pengguna |
| 4.5 | Urutan proses dengan pembagian tanggung jawab tiga pihak |
| 4.6 | Percakapan antar komponen beserta urutan waktunya |
| 4.7 | Rincian benar-salah model: 863, 9, 24, 442 |
| 4.8 | Bukti performa stabil di lima putaran pengujian |
| 4.9 | Pencarian nilai C terbaik; puncaknya di C = 1 |
| 4.10 | Bukti stemming tidak memberi peningkatan berarti |
| 4.11–4.15 | Tampilan dan bukti sistem berjalan |
| 3.2 | Letak kegagalan filter YouTube saat ini |
| 2.2 | Konsep hyperplane dan margin pada SVM |
