# Patch Teks — BAB I (1.4.2) dan BAB IV (4.3.1)

> Teks ini sebelumnya cuma ada di riwayat chat, dipindah ke file biar nggak hilang.
> Konteks: reframe "web scraping" → YouTube Data API v3 (lihat `TODO_BAB1-3.md` bagian "Reframe web scraping").

---

## GANTI seluruh 1.4.2 (BAB I)

**1.4.2 Observasi dan Pengumpulan Data (YouTube Data API)**

Observasi merupakan teknik pengumpulan data empiris yang mengedepankan pengamatan langsung terhadap objek, perilaku, dan kejadian pada situasi tertentu untuk mendapatkan data primer yang akurat (Sugiyono, 2022).

Pengumpulan data teks pada penelitian ini diotomatisasi menggunakan YouTube Data API v3, yaitu antarmuka pemrograman aplikasi resmi dari YouTube, yang diakses melalui skrip berbasis Node.js. Pengambilan data difokuskan pada sejumlah video YouTube yang memiliki kepadatan interaksi tinggi dan berpotensi menjadi target penyebaran spam judi online. Proses pengambilan data ini dikombinasikan secara sistematis dengan metode analisis heuristik yang memberikan pembobotan (scoring) awal pada setiap komentar yang masuk. Pendekatan heuristik ini berfungsi untuk mengidentifikasi secara cepat indikasi spam berdasarkan kepadatan karakter manipulatif (obfuscation) atau keyword tertentu, sehingga memfasilitasi dan memvalidasi proses pengumpulan data latih secara efisien.

Hasil pengumpulan data kemudian dikonversi ke dalam format CSV untuk keperluan pelabelan. Pengumpulan data berbasis perangkat lunak ini bertujuan untuk:

*(poin 1, 2, 3 di bawahnya TETAP SAMA seperti draft asli — tidak berubah)*

---

## GANTI 2 paragraf pertama 4.3.1 (BAB IV)

**4.3.1 Sumber dan Metode Pengumpulan Data**

Dataset yang digunakan dalam penelitian ini dikumpulkan dari platform YouTube melalui YouTube Data API v3, yaitu antarmuka pemrograman aplikasi resmi yang disediakan YouTube untuk mengakses data komentar secara terstruktur. Proses pengambilan data diotomatisasi menggunakan skrip berbasis Node.js yang dijalankan melalui terminal, dengan ID video YouTube sebagai parameter masukan. Skrip tersebut mengirimkan permintaan ke endpoint commentThreads pada YouTube Data API menggunakan kunci API (API key), lalu menerima seluruh komentar beserta metadata-nya dalam format JSON. Data dikumpulkan dari video-video YouTube berbahasa Indonesia yang memiliki tingkat interaksi tinggi dan berpotensi menjadi target penyebaran komentar promosi judi online.

Setiap komentar yang diperoleh diberi skor heuristik (spam_score) yang dihitung secara otomatis berdasarkan kehadiran sinyal-sinyal primer seperti nama brand judi online dan tautan kontak, serta sinyal sekunder seperti rasio emoji dan pola karakter Unicode. Hasil pengambilan data kemudian dikonsolidasikan ke dalam dua file terpisah, yaitu final_spam.json untuk komentar terindikasi spam dan final_non_spam.json untuk komentar normal.

Sebelum masuk ke dataset pelatihan, komentar melewati proses penyaringan dua tahap. Tahap pertama memasukkan seluruh komentar dengan skor heuristik lebih besar atau sama dengan 80, yang mengindikasikan kehadiran minimal satu sinyal primer yang kuat. Tahap kedua merupakan mekanisme penyelamatan (rescue) terhadap komentar dengan skor di bawah 80 yang tetap mengandung nama brand judi online terkonfirmasi pada teks ternormalisasi — komentar semacam ini turut dimasukkan agar contoh spam yang valid tidak terbuang hanya karena skornya rendah. Mekanisme dua tahap ini bertujuan memaksimalkan kualitas label sekaligus meminimalkan noise pada dataset.

*(paragraf selanjutnya, 4.3.2 Proses Pelabelan Data dst., TETAP SAMA seperti draft asli — tidak berubah)*
