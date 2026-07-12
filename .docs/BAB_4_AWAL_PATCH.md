# Patch BAB IV — Solusi PIECES (awal 4.1) + Narasi Use Case (4.7)

## A. Paragraf Solusi — sisipkan SEBELUM "4.1 Analisis Kebutuhan Sistem"

*(Posisi: setelah heading "BAB IV PERANCANGAN SISTEM", sebelum sub-judul "4.1 Analisis Kebutuhan Sistem". Ini menjawab dosen poin 9 — mengaitkan solusi ke analisis PIECES yang sudah ditulis di BAB III Tabel 3.1, jadi BAB III dan BAB IV nyambung, bukan dua bab yang berdiri sendiri.)*

Berdasarkan hasil analisis PIECES terhadap sistem berjalan pada Bab III, ditemukan bahwa kelemahan paling mendasar dari mekanisme pemfilteran komentar YouTube saat ini terletak pada aspek Kendali (Control) dan Efisiensi (Efficiency), yang kemudian berdampak berantai pada aspek Kinerja, Informasi, Ekonomi, dan Pelayanan. Untuk menjawab kelemahan tersebut, penelitian ini mengusulkan sebuah sistem berupa ekstensi peramban Google Chrome yang mengombinasikan teknik String Normalization dengan algoritma klasifikasi Support Vector Machine (SVM).

Secara garis besar, solusi yang ditawarkan bekerja dengan menyisipkan lapisan normalisasi teks di sisi klien sebelum komentar sempat tampil kepada pengguna, sehingga karakter-karakter hasil manipulasi (obfuscation) yang selama ini lolos dari filter kata kunci bawaan YouTube dapat dikenali kembali dalam bentuk standarnya. Teks yang telah dinormalisasi kemudian diklasifikasikan secara real-time oleh model SVM yang telah dilatih menggunakan data komentar spam judi online berbahasa Indonesia, sehingga keputusan penyaringan tidak lagi bergantung pada pencocokan kata kunci statis, melainkan pada pola bahasa yang telah dipelajari dari data.

Dengan pendekatan ini, aspek Kendali diperkuat melalui normalisasi karakter yang mampu menangkal berbagai teknik obfuscation, aspek Efisiensi meningkat karena sistem tidak lagi bergantung pada pembaruan daftar kata kunci secara manual, aspek Informasi terjaga karena komentar menyesatkan dapat disembunyikan secara otomatis, aspek Ekonomi tertangani karena sistem berjalan tanpa biaya berlangganan tambahan, dan aspek Pelayanan meningkat melalui pengalaman berselancar yang lebih bersih bagi pengguna. Rincian kebutuhan, arsitektur, serta implementasi dari solusi ini diuraikan pada sub-bab berikut.

---

## B0. PERBAIKAN Gambar 4.4 (Use Case Diagram) — WAJIB dilakukan sebelum bagian B di bawah

**Masalah:** Diagram use case saat ini menggambar boundary "Sistem Ekstensi Chrome" dengan "Server API (VPS)" sebagai aktor di luar kotak. Ini kontradiksi dengan 3.1.2 dan 4.6, yang keduanya menyebut sisi klien DAN sisi peladen sebagai bagian dari SATU sistem yang sama yang diteliti/dibangun. Aktor dalam UML seharusnya pihak yang benar-benar di luar kendali sistem (seperti Pengguna) — server yang dibangun sendiri oleh peneliti bukan aktor eksternal.

**Perbaikan yang harus dilakukan pada Gambar 4.4:**
1. Perbesar boundary menjadi mencakup seluruh sistem, ganti label kotak dari "Sistem Ekstensi Chrome" menjadi **"Sistem Deteksi Spam Komentar YouTube"**.
2. **Hapus** aktor "Server API (VPS)" beserta garis penghubungnya.
3. Use case "Mengklasifikasikan Teks" tetap berada di dalam kotak, tetap terhubung `«include»` dari "Menyaring Komentar Spam" — sekarang tanpa panah dari aktor manapun, karena statusnya proses internal.
4. **Pengguna** menjadi satu-satunya aktor. Garis asosiasi Pengguna harus terhubung ke **EMPAT** use case berikut (bukan cuma dua seperti gambar lama):
   - Mengatur Confidence Threshold (aksi eksplisit di popup)
   - Memantau Statistik Deteksi (aksi eksplisit membuka popup)
   - **Menyaring Komentar Spam** (dipicu kehadiran/scroll Pengguna di halaman video — meski otomatis, use case ini tidak boleh "menggantung" tanpa garis ke aktor manapun)
   - **Melaporkan Kesalahan Klasifikasi** (aksi eksplisit klik tombol "Bukan spam?")

   Satu-satunya use case yang **BOLEH tanpa garis langsung ke aktor** adalah "Mengklasifikasikan Teks", karena ia hanya dijangkau melalui relasi `«include»` dari "Menyaring Komentar Spam" — itu konvensi UML yang sah (use case yang di-include tidak butuh garis aktor sendiri, include yang menariknya).

   > Referensi visual (kasar, buat panduan struktur — bukan buat ditempel langsung): `reports/usecase_diagram_revisi_v2.png`. Redraw versi rapi di Visio/draw.io mengikuti struktur koneksi ini.

**Ganti paragraf pembuka 4.7** dari "...sistem melibatkan dua aktor dan lima use case utama..." menjadi:

*Berdasarkan use case diagram di atas, sistem melibatkan satu aktor, yaitu Pengguna, dan lima use case utama. Proses klasifikasi teks berjalan sebagai bagian internal sistem yang dipicu melalui relasi include, bukan sebagai interaksi dengan pihak eksternal, karena baik sisi klien maupun sisi peladen merupakan bagian dari sistem yang sama sebagaimana telah diuraikan pada Sub-bab 3.1.2 dan 4.6.*

**Hapus** daftar "Aktor: 1. Pengguna 2. Server API (VPS)..." yang lama — cukup satu aktor (Pengguna) yang dideskripsikan.

---

## B. Use Case Narrative — sisipkan SETELAH paragraf pembuka yang sudah direvisi di atas

*(Dosen poin 11. Format: tabel "Use Case Narrative" dengan Use Case Id, field-field standar, dan tabel "Typical Course of Events" TERPISAH berisi 3 kolom (Langkah | Actor Action | System Response) — mengikuti konvensi Rosa & Shalahuddin (2019) yang sudah jadi sitasi di 2.15 UML, jadi tidak perlu sitasi tambahan. Kelima use case SAMA PERSIS dengan yang sudah diidentifikasi di draft asli 4.7 — cuma diformalkan strukturnya, bukan use case baru.*
*⚠️ PERBAIKAN dari draft sebelumnya: tabel "Typical Course of Events" sebelumnya digabung ke tabel field utama (2 kolom), yang menyebabkan kolom "System Response" hilang saat dirender karena tabel utama cuma punya 2 kolom. Sekarang dipisah jadi tabel sendiri (3 kolom) — perbaikan murni format, isi/datanya sama persis dengan sebelumnya.)*

### A. Use Case Narrative Menyaring Komentar Spam

Use case ini memungkinkan pengguna untuk mendapatkan perlindungan otomatis dari komentar promosi judi online saat menjelajahi halaman video YouTube. Proses ini dipicu ketika pengguna membuka atau menggulir halaman video, di mana sistem akan memantau, mengklasifikasikan, dan menyembunyikan komentar yang terindikasi spam secara real-time tanpa memerlukan interaksi manual dari pengguna.

**Tabel 4.X Use Case Narrative Menyaring Komentar Spam**

| Field | Keterangan |
|---|---|
| Use Case Name | Menyaring Komentar Spam |
| Use Case Id | UC01 |
| Actor | Pengguna |
| Description | Use case yang menyaring komentar promosi judi online secara otomatis pada halaman video YouTube. |
| Pre Condition | Ekstensi telah terpasang dan aktif pada peramban Chrome; server API dalam kondisi tersedia (online). |
| Post Condition | Komentar yang terklasifikasi sebagai spam telah disembunyikan sesuai mode yang dipilih pengguna. |
| Trigger | Pengguna membuka atau menggulir halaman video YouTube. |
| Alternate Course | Apabila server API tidak tersedia, sistem menampilkan status offline pada popup dan tidak melakukan penyembunyian komentar apa pun. |
| Extend | Melaporkan Kesalahan Klasifikasi (UC05) |
| Include | Mengklasifikasikan Teks (UC02) |

**Typical Course of Events — UC01**

| Langkah | Actor Action | System Response |
|---|---|---|
| 1 | Membuka atau menggulir halaman video YouTube. | |
| 2 | | Mendeteksi komentar baru yang dimuat secara dinamis pada DOM melalui MutationObserver. |
| 3 | | Memicu use case Mengklasifikasikan Teks (include) untuk setiap komentar baru. |
| 4 | | Menerima hasil klasifikasi (label dan confidence) dari server. |
| 5 | | Menyembunyikan komentar berlabel spam dengan skor keyakinan di atas ambang batas, sesuai mode Redupkan atau Hilangkan. |

### B. Use Case Narrative Mengklasifikasikan Teks

Use case ini menjelaskan proses internal sistem dalam mengolah teks komentar hingga menghasilkan keputusan klasifikasi. Proses ini selalu dijalankan sebagai bagian tak terpisahkan dari use case Menyaring Komentar Spam melalui relasi include, dan tidak dipicu oleh aktor eksternal manapun karena berlangsung sepenuhnya di dalam batas sistem.

**Tabel 4.X Use Case Narrative Mengklasifikasikan Teks**

| Field | Keterangan |
|---|---|
| Use Case Name | Mengklasifikasikan Teks |
| Use Case Id | UC02 |
| Actor | - (proses internal sistem, dipicu melalui relasi include dari UC01) |
| Description | Use case internal yang menjalankan prapemrosesan, ekstraksi fitur, dan klasifikasi SVM terhadap teks komentar. Dijalankan oleh komponen sisi peladen sebagai bagian dari sistem yang sama, bukan interaksi dengan pihak eksternal. |
| Pre Condition | Model SVM telah dimuat ke memori pada komponen sisi peladen. |
| Post Condition | Label klasifikasi beserta skor keyakinan telah dihasilkan dan diteruskan ke UC01. |
| Trigger | Dipanggil secara otomatis oleh use case Menyaring Komentar Spam (UC01) melalui relasi include. |
| Alternate Course | Apabila teks komentar kosong setelah dinormalisasi, sistem langsung mengembalikan label non-spam tanpa melalui proses klasifikasi model. |
| Extend | - |
| Include | - |

**Typical Course of Events — UC02**

| Langkah | Actor Action | System Response |
|---|---|---|
| 1 | | Menerima teks komentar dari proses UC01 melalui endpoint /predict/batch. |
| 2 | | Menjalankan pipeline prapemrosesan (normalisasi teks) yang identik dengan tahap pelatihan. |
| 3 | | Mengekstraksi fitur TF-IDF dari teks yang telah dinormalisasi. |
| 4 | | Model SVM menghasilkan label klasifikasi beserta skor keyakinan (confidence). |
| 5 | | Mengembalikan hasil klasifikasi dalam format JSON ke UC01. |

### C. Use Case Narrative Mengatur Confidence Threshold

Use case ini memungkinkan pengguna menyesuaikan tingkat sensitivitas deteksi sesuai preferensi masing-masing, dengan cara mengubah ambang batas keyakinan minimum sebelum sebuah komentar dianggap spam dan disembunyikan.

**Tabel 4.X Use Case Narrative Mengatur Confidence Threshold**

| Field | Keterangan |
|---|---|
| Use Case Name | Mengatur Confidence Threshold |
| Use Case Id | UC03 |
| Actor | Pengguna |
| Description | Use case yang memungkinkan pengguna menyesuaikan ambang batas keyakinan minimum untuk penyembunyian komentar. |
| Pre Condition | Pengguna telah membuka antarmuka popup ekstensi. |
| Post Condition | Nilai confidence threshold baru tersimpan dan berlaku untuk proses klasifikasi berikutnya. |
| Trigger | Pengguna ingin mengubah tingkat sensitivitas deteksi. |
| Alternate Course | Apabila pengguna belum pernah mengatur threshold sebelumnya, sistem menggunakan nilai bawaan (default) sebesar 75%. |
| Extend | - |
| Include | - |

**Typical Course of Events — UC03**

| Langkah | Actor Action | System Response |
|---|---|---|
| 1 | Membuka popup ekstensi. | |
| 2 | | Menampilkan slider confidence threshold dengan nilai saat ini (default 75%). |
| 3 | Menggeser slider ke nilai baru (rentang 50%-95%). | |
| 4 | | Menyimpan nilai baru ke penyimpanan lokal peramban (chrome.storage). |
| 5 | | Menerapkan nilai threshold baru pada proses klasifikasi selanjutnya tanpa perlu memuat ulang halaman. |

### D. Use Case Narrative Memantau Statistik Deteksi

Use case ini memungkinkan pengguna melihat efektivitas sistem secara langsung melalui jumlah komentar yang telah dipindai dan disembunyikan sejak ekstensi aktif pada tab yang sedang dibuka.

**Tabel 4.X Use Case Narrative Memantau Statistik Deteksi**

| Field | Keterangan |
|---|---|
| Use Case Name | Memantau Statistik Deteksi |
| Use Case Id | UC04 |
| Actor | Pengguna |
| Description | Use case yang menampilkan jumlah komentar yang telah dipindai dan disembunyikan. |
| Pre Condition | Ekstensi aktif dan setidaknya satu komentar telah diproses pada halaman yang sedang dibuka. |
| Post Condition | Statistik terkini ditampilkan pada antarmuka popup. |
| Trigger | Pengguna membuka popup ekstensi. |
| Alternate Course | - |
| Extend | - |
| Include | - |

**Typical Course of Events — UC04**

| Langkah | Actor Action | System Response |
|---|---|---|
| 1 | Membuka popup ekstensi. | |
| 2 | | Mengambil nilai jumlah komentar dipindai dan disembunyikan dari Content Script pada tab aktif. |
| 3 | | Menampilkan kedua nilai tersebut pada panel statistik popup. |
| 4 (opsional) | Menekan tombol "Reset Statistik". | |
| 5 (opsional) | | Mengembalikan kedua nilai statistik ke nol. |

### E. Use Case Narrative Melaporkan Kesalahan Klasifikasi

Use case ini memungkinkan pengguna melaporkan komentar yang keliru diklasifikasikan sebagai spam (false positive), khusus pada mode pengembangan (dev mode), sebagai mekanisme pengumpulan data koreksi untuk pelatihan ulang model.

**Tabel 4.X Use Case Narrative Melaporkan Kesalahan Klasifikasi**

| Field | Keterangan |
|---|---|
| Use Case Name | Melaporkan Kesalahan Klasifikasi |
| Use Case Id | UC05 |
| Actor | Pengguna |
| Description | Use case yang memungkinkan pengguna melaporkan komentar yang keliru disembunyikan. |
| Pre Condition | Sistem berjalan dalam mode pengembangan; sebuah komentar telah disembunyikan pada mode Redupkan. |
| Post Condition | Komentar yang dilaporkan tersimpan sebagai data koreksi untuk pelatihan ulang model. |
| Trigger | Pengguna menilai sebuah komentar salah diklasifikasikan sebagai spam. |
| Alternate Course | Use case ini tidak tersedia pada mode produksi, karena tombol "Bukan spam?" hanya dimunculkan pada mode pengembangan. |
| Extend of | Menyaring Komentar Spam (UC01) |
| Include | - |

**Typical Course of Events — UC05**

| Langkah | Actor Action | System Response |
|---|---|---|
| 1 | Melihat komentar yang diredupkan beserta tombol "Bukan spam?". | |
| 2 | Menekan tombol "Bukan spam?". | |
| 3 | | Mengirimkan teks komentar ke endpoint /report pada server. |
| 4 | | Menyimpan koreksi tersebut untuk digunakan pada iterasi pelatihan model berikutnya. |

> **Catatan konversi ke Word:** kalau lu mau tetap format SATU tabel gabungan persis kayak contoh referensi (field di atas, lalu "Typical Course of Events" sebagai sub-tabel di dalam baris yang sama), itu bisa dilakukan di Word dengan cara membuat nested table di dalam satu cell — Word mendukung ini, markdown tidak. Cara paling gampang: buat tabel utama seperti di atas, lalu sisipkan tabel Typical Course of Events sebagai tabel baru tepat di dalam baris terakhir sebelum "Alternate Course" (klik di dalam cell → Insert Table). Atau, kalau mau lebih simpel dan tetap rapi, biarkan sebagai dua tabel terpisah berurutan seperti di atas — ini juga lazim dipakai dan tidak melanggar aturan manapun di pedoman.