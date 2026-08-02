# 04 — Kenapa A, Bukan B

> Setiap keputusan teknis di proyek ini, beserta alasannya dan alternatif yang tidak dipilih.

Ini pola pertanyaan favorit penguji: *"kenapa pakai X?"* Yang dicari bukan jawaban hafalan, tapi bukti bahwa kamu **sadar ada pilihan lain** dan punya alasan memilih.

Pola menjawab yang baik selalu tiga bagian:
1. Apa yang dipilih
2. Kenapa cocok untuk kasus ini
3. Alternatifnya apa, dan kenapa tidak dipakai

---

# 1. Kenapa SVM?

🎯 **Jawaban singkat:** karena kuat pada data berdimensi tinggi, memaksimalkan margin sehingga tahan terhadap data baru, ringan saat prediksi, dan **terbukti unggul lewat perbandingan empiris**.

## Dibanding Naive Bayes

Naive Bayes berasumsi tiap fitur **saling bebas** — kemunculan kata "slot" dianggap tidak berhubungan dengan kemunculan "gacor". Pada spam judol, asumsi itu justru salah: kata-kata tersebut muncul bersamaan sebagai satu pola khas.

Buktinya ada di angkanya: **93,95%** vs SVM **97,53%**. Selisih 3,58 poin.

## Dibanding Logistic Regression

Ini alternatif paling kompetitif: **97,09%**, cuma 0,44 poin di bawah SVM.

⚠️ **Jangan mengarang keunggulan yang tidak ada.** Kalau ditanya soal selisih tipis ini, jawab jujur:

> "Selisihnya memang tipis, Pak. SVM tetap dipilih karena unggul konsisten di semua metrik, punya dasar teoretis margin maksimum yang membuatnya lebih tahan pada data baru, dan sesuai fokus penelitian. Tapi saya juga mencatat di skripsi bahwa Logistic Regression adalah alternatif yang sangat kompetitif untuk kasus ini."

Mengakui kedekatan angka justru menunjukkan kamu paham datanya, bukan sekadar membela pilihan.

## Dibanding Deep Learning

Tiga alasan, dan semuanya bisa dipertahankan:

1. **Kebutuhan real-time di peramban.** Sistem harus menjawab saat pengguna menggulir. Model Deep Learning lebih berat dan lambat.
2. **Ukuran data.** 6.690 sampel itu relatif kecil untuk Deep Learning, yang biasanya baru unggul pada data jauh lebih besar.
3. **Bukti empiris dari penelitianmu sendiri.** Ini yang paling kuat: kamu sudah membuktikan bahwa **menambah kompleksitas justru menurunkan performa** (lihat ablasi hibrida, −7,32 poin). Argumen "lebih rumit belum tentu lebih baik" bukan asumsi — kamu punya datanya.

📄 **Di skripsi:** Sub-bab 2.10 membahas perbandingan Machine Learning dan Deep Learning.

❓ **Kalau ditanya "kenapa tidak pakai BERT atau IndoBERT saja?"**
> "Pertimbangan utamanya latensi dan sumber daya, Pak. Sistem ini berjalan di sisi klien dan harus merespons saat pengguna menggulir halaman, sementara model berbasis transformer jauh lebih berat. Selain itu ukuran data 6.690 sampel belum berada di rentang yang membuat model besar unggul signifikan. Saya juga mencatat eksplorasi Deep Learning sebagai saran pengembangan lanjutan di Bab V."

---

# 2. Kenapa TF-IDF?

🎯 **Jawaban singkat:** sederhana, cepat, hasilnya bisa ditelusuri, dan cocok dipasangkan dengan pemisah linear.

## Dibanding Bag of Words biasa

Bag of Words cuma menghitung frekuensi. Akibatnya kata "yang" dan "di" mendominasi karena paling sering muncul, padahal tidak membedakan apa-apa. TF-IDF menambahkan faktor kelangkaan sehingga kata pasaran otomatis berbobot nol.

## Dibanding Word2Vec / embedding

Embedding menangkap kemiripan makna — "raja" dan "ratu" berdekatan. Terdengar lebih canggih, tapi untuk kasus ini justru kurang cocok:

- Spam judol dikenali dari **kata penciri yang spesifik** (nama brand, "gacor", "wd"), bukan dari kemiripan makna.
- Embedding butuh data latih jauh lebih besar.
- **Hasilnya sulit ditelusuri.** Dengan TF-IDF kamu bisa membuka daftar kata paling berpengaruh dan menunjukkannya ke penguji — itu ada di `src/inspect_features.py`. Dengan embedding, hampir mustahil menjelaskan kenapa sebuah keputusan diambil.

Poin ketiga itu nilai jual yang kuat saat sidang: **modelmu bisa dijelaskan**.

📄 Ada rujukan pendukung di skripsimu: Efrizoni dkk. (2022) menemukan TF-IDF paling stabil di berbagai algoritma.

---

# 3. Kenapa kernel linear?

🎯 **Jawaban singkat:** data teks berdimensi tinggi umumnya sudah bisa dipisah garis lurus, dan kernel linear jauh lebih cepat.

🔍 Dengan 10.000 fitur, ruangnya sangat longgar sehingga pemisah lurus biasanya cukup. Kernel non-linear seperti RBF menambah beban komputasi besar untuk keuntungan yang tipis pada kasus teks — sementara sistemmu punya batasan waktu respons.

Analogi SE: memilih algoritma O(n) yang sudah memadai, ketimbang O(n²) yang sedikit lebih akurat tapi membuat permintaan *timeout*.

---

# 4. Kenapa Python untuk ML, tapi Node.js untuk scraper?

Ini sering ditanya karena terlihat tidak konsisten. Padahal alasannya kuat: **pakai alat sesuai ekosistemnya.**

| Bagian | Bahasa | Alasan |
|---|---|---|
| Pelatihan & prediksi | Python | Ekosistem ML matang: scikit-learn, pandas, numpy. Tidak ada padanan sepadan di Node.js. |
| Pengumpulan data | Node.js | Tugasnya murni panggil REST API dan olah JSON — Node.js sangat nyaman untuk itu, dan JSON adalah warga kelas satu di JavaScript. |
| Ekstensi peramban | JavaScript | Tidak ada pilihan. Peramban cuma menjalankan JavaScript. |

❓ **Kalau ditanya "kenapa tidak semuanya Python saja?"**
> "Karena tiap bagian dipilih sesuai ekosistem yang paling matang untuk tugasnya, Pak. Pelatihan model memakai Python karena scikit-learn tidak punya padanan sepadan di Node.js. Scraper memakai Node.js karena tugasnya murni memanggil REST API dan mengolah JSON. Sedangkan ekstensi memang wajib JavaScript karena itu satu-satunya yang dijalankan peramban. Ketiganya terhubung lewat berkas dan HTTP, jadi perbedaan bahasa tidak menjadi masalah."

---

# 5. Kenapa FastAPI?

🎯 **Jawaban singkat:** cepat, validasi masukan otomatis, dan dokumentasi API dibuatkan sendiri.

## Dibanding Flask

Flask lebih sederhana tapi tidak punya validasi bawaan. Dengan FastAPI + Pydantic, aturan seperti "teks tidak boleh kosong" dan "batch maksimal 50" ditulis sebagai model data, dan permintaan yang melanggar otomatis ditolak dengan pesan yang jelas — tanpa perlu menulis pengecekan manual di tiap endpoint.

📍 Contohnya di `src/server.py` baris 108 (`text_must_not_be_empty`) dan baris 245 (`label_must_be_valid`).

## Dibanding Django

Django terlalu berat untuk kasus ini. Django membawa ORM, sistem admin, template engine — sementara yang dibutuhkan cuma empat endpoint JSON tanpa basis data.

## Nilai tambah untuk demo sidang

FastAPI otomatis menyediakan halaman dokumentasi interaktif di `http://localhost:8000/docs`. **Kamu bisa membuka halaman itu saat sidang** dan mendemonstrasikan endpoint langsung tanpa perlu Postman. Ini kesan yang bagus dan gratis.

📄 **Di skripsi:** Sub-bab 2.14, dengan rujukan Azhari (2022) yang membandingkan Flask dan FastAPI.

---

# 6. Kenapa YouTube Data API v3, bukan mengikis HTML?

🎯 **Jawaban singkat:** legal, stabil, dan datanya terstruktur.

Ini **pertanyaan berisiko tinggi** karena menyangkut etika penelitian. Untungnya jawabanmu kuat:

| Aspek | API resmi | Mengikis HTML |
|---|---|---|
| Legalitas | Sesuai ketentuan layanan | Berpotensi melanggar |
| Stabilitas | Kontrak API terjaga | Rusak tiap kali tampilan berubah |
| Format | JSON terstruktur | Perlu penguraian rapuh |
| Batasan | Kuota jelas dan terdokumentasi | Berisiko diblokir |

⚠️ **Catatan penting:** istilah "web scraping" sempat dipakai di draf skripsi versi awal dan **sudah diperbaiki**. Yang benar dan konsisten dipakai sekarang: **YouTube Data API v3**. Kalau ada penguji yang menyinggung istilah scraping, luruskan dengan tenang.

📍 **Di kode:** `svm-judol-spam/scraper/index.js` baris 348 memanggil `https://www.googleapis.com/youtube/v3/commentThreads`.

❓ **Kalau ditanya "apakah pengambilan datanya melanggar hak cipta atau ketentuan platform?"**
> "Tidak, Pak. Pengambilan data memakai YouTube Data API v3 resmi dengan kunci API terdaftar, jadi mengikuti ketentuan layanan yang disediakan Google. Sistem juga tidak mengubah data apa pun milik platform — penyembunyian komentar hanya terjadi di tampilan peramban pengguna sendiri, tidak menyentuh basis data YouTube."

---

# 7. Kenapa Manifest V3 dan sisi klien?

🎯 **Manifest V3** adalah standar wajib ekstensi Chrome saat ini. Manifest V2 sudah dihentikan Google. Jadi ini bukan pilihan — ini keharusan.

🎯 **Kenapa penyaringan di sisi klien, bukan di server YouTube?** Karena kamu memang tidak punya akses ke sana. Yang bisa dilakukan pihak ketiga adalah memanipulasi tampilan di peramban pengguna sendiri.

Ini justru punya keuntungan yang layak disebut: **tidak membebani peladen YouTube sama sekali**, dan tiap pengguna bisa mengatur sensitivitasnya sendiri.

---

## ⚠️ Temuan yang perlu kamu tahu sebelum sidang

Berkas `extension/manifest.json` mencantumkan **Instagram**, padahal skripsimu khusus membahas YouTube:

```json
"host_permissions": [
    "http://localhost:8000/*",
    "https://www.youtube.com/*",
    "https://www.instagram.com/*"      ← ini
],
"content_scripts": [{
    "matches": [
        "https://www.youtube.com/*",
        "https://www.instagram.com/*"  ← dan ini
    ], ...
}]
```

Kalau penguji membuka berkas ini, dia bisa bertanya *"katanya cuma YouTube, kenapa ada Instagram?"*

**Dua pilihan, pilih salah satu sebelum sidang:**

**Pilihan A — hapus Instagram dari manifest.** Paling aman dan konsisten dengan skripsi. Cukup hapus dua baris itu, muat ulang ekstensinya, selesai.

**Pilihan B — pertahankan dan siapkan jawaban.** Kalau memang ingin menunjukkan potensi perluasan:
> "Izin untuk Instagram sudah disiapkan sebagai jalur perluasan, Pak, tapi ruang lingkup penelitian ini dibatasi pada YouTube. Pengujian dan evaluasi seluruhnya dilakukan pada komentar YouTube. Adaptasi ke platform lain saya cantumkan sebagai saran pengembangan lanjutan di Bab V."

Pilihan B sebenarnya sejalan dengan saran di Bab V skripsimu yang menyebut Instagram dan TikTok. **Tapi jangan sampai kamu baru sadar ada baris itu saat penguji yang menunjukkannya.**

---

# 8. Kenapa joblib untuk menyimpan model?

🎯 **Jawaban singkat:** joblib efisien untuk objek berisi array numerik besar, dan merupakan cara yang dianjurkan scikit-learn.

Analogi SE: ini **serialisasi** biasa, seperti menyimpan objek ke berkas biner. Bedanya `pickle` bawaan Python kurang efisien untuk array numpy berukuran besar, sedangkan joblib dioptimalkan khusus untuk itu.

Yang disimpan bukan cuma modelnya, tapi **seluruh pipeline** — termasuk TF-IDF yang sudah dilatih. Ini penting: kalau yang disimpan hanya SVM-nya, saat prediksi kamu tidak punya kamus kata yang sama dan hasilnya kacau.

📍 **Di kode:** `src/train.py:439` → `joblib.dump(pipeline, path)`

---

# 9. Kenapa pustaka `emoji`?

🎯 Untuk mengubah emoji jadi token teks, bukan membuangnya.

🔍 Emoji itu **sinyal**, bukan sampah. 🎰 dan 💰 adalah penanda spam yang kuat, sementara 👍 cenderung netral. Kalau emoji dihapus begitu saja, informasi itu hilang.

Pustaka `emoji` mengubah 🎰 jadi `slot_machine`, yang lalu menjadi fitur TF-IDF biasa. Model belajar sendiri bahwa `slot_machine` berkorelasi dengan spam.

📍 **Di kode:** `src/preprocessing.py` baris 257–266

---

# 10. Kenapa Sastrawi dipasang tapi tidak dipakai?

Ini terlihat aneh di `requirements.txt` dan bisa ditanyakan.

🎯 **Jawabannya:** Sastrawi dipakai untuk **eksperimen**, bukan untuk pipeline akhir.

📍 Dipakai di `src/experiment_stemming.py`, yang menghasilkan bukti bahwa stemming tidak signifikan (p = 0,3575). Setelah terbukti tidak membantu, stemming tidak dimasukkan ke pipeline produksi — tapi pustakanya tetap terpasang supaya eksperimennya bisa diulang siapa pun yang ingin memverifikasi.

❓ **Kalau ditanya "kenapa ada Sastrawi di requirements tapi tidak dipakai?"**
> "Sastrawi dipakai untuk menjalankan eksperimen stemming, Pak, bukan untuk pipeline akhir. Hasilnya menunjukkan stemming tidak memberi peningkatan signifikan, jadi tidak dipakai. Pustakanya tetap dicantumkan supaya eksperimen itu bisa diulang dan diverifikasi."

---

# 11. Kenapa hasil negatif tetap dilaporkan?

Ini bukan pertanyaan teknis, tapi pertanyaan **integritas penelitian** — dan jawabannya bisa jadi nilai tambah besar.

Dua hasil negatif di skripsimu:
- Aturan hibrida menurunkan akurasi 7,32–16,30 poin
- Stemming tidak signifikan (p = 0,3575)

🎯 **Kenapa tidak dihapus saja dari laporan?** Karena keduanya menjawab pertanyaan yang wajar muncul di benak pembaca: *"kenapa tidak ditambah aturan?"* dan *"kenapa tidak pakai stemming?"*

Tanpa eksperimen itu, jawabanmu cuma bisa "tidak dipakai". Dengan eksperimen itu, jawabanmu jadi **"sudah diuji dan terbukti merugikan, ini datanya"**. Jauh lebih kuat.

❓ **Kalau ditanya "kenapa melaporkan eksperimen yang gagal?"**
> "Karena hasilnya justru menjawab pertanyaan penting, Pak. Keduanya adalah pendekatan yang secara teori masuk akal dan wajar ditanyakan orang. Dengan mengujinya secara terukur, saya bisa menunjukkan bahwa penyederhanaan pipeline itu keputusan berbasis bukti, bukan karena tidak sempat mencoba. Menurut saya melaporkan hasil yang tidak sesuai dugaan justru bagian dari penelitian yang jujur."

---

# 12. Kenapa metode Waterfall?

📄 **Di skripsi:** Sub-bab 2.9 dan 4.2

🎯 **Jawaban singkat:** karena kebutuhan sistem sudah jelas dan tetap sejak awal.

🔍 Waterfall cocok ketika kebutuhan tidak banyak berubah di tengah jalan. Di penelitian ini, tujuannya sudah pasti dari awal: deteksi komentar spam judol secara real-time di peramban. Tidak ada pelanggan yang mengubah permintaan di tengah pengerjaan.

Kalau ditanya kenapa bukan Agile atau Prototyping: metode iteratif unggul ketika kebutuhan masih kabur dan perlu umpan balik pengguna berulang. Untuk penelitian dengan ruang lingkup yang sudah ditetapkan di proposal, tahapan berurutan justru lebih sesuai dan lebih mudah didokumentasikan.

⚠️ Perlu diingat: proposal awalmu sempat menyebut *prototyping*, dan itu **sudah diselaraskan** menjadi Waterfall agar konsisten dengan skripsi.

---

# Ringkasan untuk dihafal

| Pertanyaan | Inti jawaban |
|---|---|
| Kenapa SVM? | Margin maksimum, kuat di dimensi tinggi, ringan, **dan terbukti unggul lewat perbandingan** |
| Kenapa bukan Naive Bayes? | Asumsi antar-fitur bebas tidak terpenuhi pada pola spam. 93,95% vs 97,53% |
| Kenapa bukan Logistic Regression? | Selisih tipis 0,44 poin — **akui saja**, SVM unggul konsisten & sesuai fokus penelitian |
| Kenapa bukan Deep Learning? | Butuh real-time, data belum cukup besar, dan terbukti kompleksitas tambahan justru merugikan |
| Kenapa TF-IDF? | Cepat, cocok untuk kata penciri spesifik, **dan bisa ditelusuri** |
| Kenapa kernel linear? | Teks berdimensi tinggi umumnya terpisah linear; jauh lebih cepat |
| Kenapa Python + Node.js? | Tiap bagian pakai ekosistem yang paling matang untuk tugasnya |
| Kenapa FastAPI? | Validasi otomatis, cepat, dokumentasi interaktif bawaan |
| Kenapa API resmi? | Legal, stabil, terstruktur — dan menjaga kelayakan hukum penelitian |
| Kenapa sisi klien? | Tidak punya akses ke peladen YouTube; sekaligus tidak membebaninya |
| Kenapa hasil negatif dilaporkan? | Menjawab pertanyaan wajar pembaca dengan bukti, bukan asumsi |

---

## Selanjutnya

Lanjut ke `06-bank-pertanyaan.md` untuk latihan tanya jawab menyeluruh.
