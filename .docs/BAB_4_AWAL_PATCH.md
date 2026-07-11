# Patch BAB IV — Solusi PIECES (awal 4.1) + Narasi Use Case (4.7)

## A. Paragraf Solusi — sisipkan SEBELUM "4.1 Analisis Kebutuhan Sistem"

*(Posisi: setelah heading "BAB IV PERANCANGAN SISTEM", sebelum sub-judul "4.1 Analisis Kebutuhan Sistem". Ini menjawab dosen poin 9 — mengaitkan solusi ke analisis PIECES yang sudah ditulis di BAB III Tabel 3.1, jadi BAB III dan BAB IV nyambung, bukan dua bab yang berdiri sendiri.)*

Berdasarkan hasil analisis PIECES terhadap sistem berjalan pada Bab III, ditemukan bahwa kelemahan paling mendasar dari mekanisme pemfilteran komentar YouTube saat ini terletak pada aspek Kendali (Control) dan Efisiensi (Efficiency), yang kemudian berdampak berantai pada aspek Kinerja, Informasi, Ekonomi, dan Pelayanan. Untuk menjawab kelemahan tersebut, penelitian ini mengusulkan sebuah sistem berupa ekstensi peramban Google Chrome yang mengombinasikan teknik String Normalization dengan algoritma klasifikasi Support Vector Machine (SVM).

Secara garis besar, solusi yang ditawarkan bekerja dengan menyisipkan lapisan normalisasi teks di sisi klien sebelum komentar sempat tampil kepada pengguna, sehingga karakter-karakter hasil manipulasi (obfuscation) yang selama ini lolos dari filter kata kunci bawaan YouTube dapat dikenali kembali dalam bentuk standarnya. Teks yang telah dinormalisasi kemudian diklasifikasikan secara real-time oleh model SVM yang telah dilatih menggunakan data komentar spam judi online berbahasa Indonesia, sehingga keputusan penyaringan tidak lagi bergantung pada pencocokan kata kunci statis, melainkan pada pola bahasa yang telah dipelajari dari data.

Dengan pendekatan ini, aspek Kendali diperkuat melalui normalisasi karakter yang mampu menangkal berbagai teknik obfuscation, aspek Efisiensi meningkat karena sistem tidak lagi bergantung pada pembaruan daftar kata kunci secara manual, aspek Informasi terjaga karena komentar menyesatkan dapat disembunyikan secara otomatis, aspek Ekonomi tertangani karena sistem berjalan tanpa biaya berlangganan tambahan, dan aspek Pelayanan meningkat melalui pengalaman berselancar yang lebih bersih bagi pengguna. Rincian kebutuhan, arsitektur, serta implementasi dari solusi ini diuraikan pada sub-bab berikut.

---

## B. Use Case Narrative — sisipkan SETELAH paragraf "Berdasarkan use case diagram di atas, sistem melibatkan dua aktor dan lima use case utama..." dan MENGGANTIKAN daftar "Aktor:" dan "Use Cases:" yang sudah ada di 4.7

*(Dosen poin 11. Format: tabel "Use Case Narrative" dengan Use Case Id, kolom berpasangan Actor Action / System Response per langkah — mengikuti konvensi Rosa & Shalahuddin (2019) yang sudah jadi sitasi di 2.15 UML, jadi tidak perlu sitasi tambahan. Kelima use case SAMA PERSIS dengan yang sudah diidentifikasi di draft asli 4.7 — cuma diformalkan strukturnya, bukan use case baru.)*

### A. Use Case Narrative Menyaring Komentar Spam

Use case ini memungkinkan pengguna untuk mendapatkan perlindungan otomatis dari komentar promosi judi online saat menjelajahi halaman video YouTube. Proses ini dipicu ketika pengguna membuka atau menggulir halaman video, di mana sistem akan memantau, mengklasifikasikan, dan menyembunyikan komentar yang terindikasi spam secara real-time tanpa memerlukan interaksi manual dari pengguna.

**Tabel 4.X Use Case Narrative Menyaring Komentar Spam**

| Use Case Name | Menyaring Komentar Spam |
|---|---|
| Use Case Id | UC01 |
| Actor | Pengguna |
| Description | Use case yang menyaring komentar promosi judi online secara otomatis pada halaman video YouTube. |
| Pre Condition | Ekstensi telah terpasang dan aktif pada peramban Chrome; server API dalam kondisi tersedia (online). |
| Post Condition | Komentar yang terklasifikasi sebagai spam telah disembunyikan sesuai mode yang dipilih pengguna. |
| Trigger | Pengguna membuka atau menggulir halaman video YouTube. |
| **Typical Course of Events** | **Actor Action** \| **System Response** |
| Langkah 1 | Membuka atau menggulir halaman video YouTube. | |
| Langkah 2 | | Mendeteksi komentar baru yang dimuat secara dinamis pada DOM melalui MutationObserver. |
| Langkah 3 | | Memicu use case Mengklasifikasikan Teks (include) untuk setiap komentar baru. |
| Langkah 4 | | Menerima hasil klasifikasi (label dan confidence) dari server. |
| Langkah 5 | | Menyembunyikan komentar berlabel spam dengan skor keyakinan di atas ambang batas, sesuai mode Redupkan atau Hilangkan. |
| Alternate Course | Apabila server API tidak tersedia, sistem menampilkan status offline pada popup dan tidak melakukan penyembunyian komentar apa pun. |
| Extend | Melaporkan Kesalahan Klasifikasi (UC05) |
| Include | Mengklasifikasikan Teks (UC02) |

### B. Use Case Narrative Mengklasifikasikan Teks

Use case ini menjelaskan bagaimana server API memproses teks komentar yang diterima dari ekstensi hingga menghasilkan keputusan klasifikasi. Proses ini selalu dijalankan sebagai bagian tak terpisahkan dari use case Menyaring Komentar Spam melalui relasi include.

**Tabel 4.X Use Case Narrative Mengklasifikasikan Teks**

| Use Case Name | Mengklasifikasikan Teks |
|---|---|
| Use Case Id | UC02 |
| Actor | Server API |
| Description | Use case yang menjalankan prapemrosesan, ekstraksi fitur, dan klasifikasi SVM terhadap teks komentar. |
| Pre Condition | Server API aktif dan model SVM telah dimuat ke memori. |
| Post Condition | Label klasifikasi beserta skor keyakinan telah dikembalikan ke ekstensi. |
| Trigger | Ekstensi mengirimkan teks komentar melalui endpoint /predict/batch. |
| **Typical Course of Events** | **Actor Action** \| **System Response** |
| Langkah 1 | Mengirimkan teks komentar ke endpoint /predict/batch. | |
| Langkah 2 | | Menjalankan pipeline prapemrosesan (normalisasi teks) yang identik dengan tahap pelatihan. |
| Langkah 3 | | Mengekstraksi fitur TF-IDF dari teks yang telah dinormalisasi. |
| Langkah 4 | | Model SVM menghasilkan label klasifikasi beserta skor keyakinan (confidence). |
| Langkah 5 | | Mengembalikan hasil klasifikasi dalam format JSON ke ekstensi. |
| Alternate Course | Apabila teks komentar kosong setelah dinormalisasi, sistem langsung mengembalikan label non-spam tanpa melalui proses klasifikasi model. |
| Extend | - |
| Include | - |

### C. Use Case Narrative Mengatur Confidence Threshold

Use case ini memungkinkan pengguna menyesuaikan tingkat sensitivitas deteksi sesuai preferensi masing-masing, dengan cara mengubah ambang batas keyakinan minimum sebelum sebuah komentar dianggap spam dan disembunyikan.

**Tabel 4.X Use Case Narrative Mengatur Confidence Threshold**

| Use Case Name | Mengatur Confidence Threshold |
|---|---|
| Use Case Id | UC03 |
| Actor | Pengguna |
| Description | Use case yang memungkinkan pengguna menyesuaikan ambang batas keyakinan minimum untuk penyembunyian komentar. |
| Pre Condition | Pengguna telah membuka antarmuka popup ekstensi. |
| Post Condition | Nilai confidence threshold baru tersimpan dan berlaku untuk proses klasifikasi berikutnya. |
| Trigger | Pengguna ingin mengubah tingkat sensitivitas deteksi. |
| **Typical Course of Events** | **Actor Action** \| **System Response** |
| Langkah 1 | Membuka popup ekstensi. | |
| Langkah 2 | | Menampilkan slider confidence threshold dengan nilai saat ini (default 75%). |
| Langkah 3 | Menggeser slider ke nilai baru (rentang 50%-95%). | |
| Langkah 4 | | Menyimpan nilai baru ke penyimpanan lokal peramban (chrome.storage). |
| Langkah 5 | | Menerapkan nilai threshold baru pada proses klasifikasi selanjutnya tanpa perlu memuat ulang halaman. |
| Alternate Course | Apabila pengguna belum pernah mengatur threshold sebelumnya, sistem menggunakan nilai bawaan (default) sebesar 75%. |
| Extend | - |
| Include | - |

### D. Use Case Narrative Memantau Statistik Deteksi

Use case ini memungkinkan pengguna melihat efektivitas sistem secara langsung melalui jumlah komentar yang telah dipindai dan disembunyikan sejak ekstensi aktif pada tab yang sedang dibuka.

**Tabel 4.X Use Case Narrative Memantau Statistik Deteksi**

| Use Case Name | Memantau Statistik Deteksi |
|---|---|
| Use Case Id | UC04 |
| Actor | Pengguna |
| Description | Use case yang menampilkan jumlah komentar yang telah dipindai dan disembunyikan. |
| Pre Condition | Ekstensi aktif dan setidaknya satu komentar telah diproses pada halaman yang sedang dibuka. |
| Post Condition | Statistik terkini ditampilkan pada antarmuka popup. |
| Trigger | Pengguna membuka popup ekstensi. |
| **Typical Course of Events** | **Actor Action** \| **System Response** |
| Langkah 1 | Membuka popup ekstensi. | |
| Langkah 2 | | Mengambil nilai jumlah komentar dipindai dan disembunyikan dari Content Script pada tab aktif. |
| Langkah 3 | | Menampilkan kedua nilai tersebut pada panel statistik popup. |
| Langkah 4 (opsional) | Menekan tombol "Reset Statistik". | |
| Langkah 5 (opsional) | | Mengembalikan kedua nilai statistik ke nol. |
| Alternate Course | - |
| Extend | - |
| Include | - |

### E. Use Case Narrative Melaporkan Kesalahan Klasifikasi

Use case ini memungkinkan pengguna melaporkan komentar yang keliru diklasifikasikan sebagai spam (false positive), khusus pada mode pengembangan (dev mode), sebagai mekanisme pengumpulan data koreksi untuk pelatihan ulang model.

**Tabel 4.X Use Case Narrative Melaporkan Kesalahan Klasifikasi**

| Use Case Name | Melaporkan Kesalahan Klasifikasi |
|---|---|
| Use Case Id | UC05 |
| Actor | Pengguna |
| Description | Use case yang memungkinkan pengguna melaporkan komentar yang keliru disembunyikan. |
| Pre Condition | Sistem berjalan dalam mode pengembangan; sebuah komentar telah disembunyikan pada mode Redupkan. |
| Post Condition | Komentar yang dilaporkan tersimpan sebagai data koreksi untuk pelatihan ulang model. |
| Trigger | Pengguna menilai sebuah komentar salah diklasifikasikan sebagai spam. |
| **Typical Course of Events** | **Actor Action** \| **System Response** |
| Langkah 1 | Melihat komentar yang diredupkan beserta tombol "Bukan spam?". | |
| Langkah 2 | Menekan tombol "Bukan spam?". | |
| Langkah 3 | | Mengirimkan teks komentar ke endpoint /report pada server. |
| Langkah 4 | | Menyimpan koreksi tersebut untuk digunakan pada iterasi pelatihan model berikutnya. |
| Alternate Course | Use case ini tidak tersedia pada mode produksi, karena tombol "Bukan spam?" hanya dimunculkan pada mode pengembangan. |
| Extend of | Menyaring Komentar Spam (UC01) |
| Include | - |

> **Catatan konversi ke Word:** tabel di atas ditulis markdown dengan baris "Typical Course of Events" berisi 2 sub-kolom (Actor Action | System Response) — ini SAMA seperti contoh referensi lu (kolom kiri = aksi aktor, kolom kanan = respons sistem, satu-satunya yang terisi per baris sesuai siapa yang beraksi di langkah itu). Nomor tabel "4.X" sesuaikan urutan final (lanjutan dari Tabel 4.3 yang sudah ada).
