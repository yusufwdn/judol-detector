# 08 — Daftar Ketidakcocokan pada Naskah yang Sudah Disubmit

> Naskah sudah dikumpulkan. Dokumen ini **bukan** daftar perbaikan — ini daftar hal yang perlu kamu **ketahui dan akui dengan tenang** kalau ditanya.

Semua temuan di bawah sudah diverifikasi langsung ke kode, bukan dugaan. Diurutkan berdasarkan **risiko ketahuan saat sidang**, bukan berdasarkan tingkat kesalahannya.

---

## Prinsip menjawab

Sebelum masuk daftar, satu hal yang berlaku untuk semuanya:

**Jangan membela sesuatu yang jelas tidak cocok dengan kode.** Penguji yang menemukan ketidakcocokan lalu melihat mahasiswanya berkelit akan menggali lebih dalam. Penguji yang melihat mahasiswanya langsung mengakui dan tahu persis di mana letak salahnya justru menyimpulkan bahwa mahasiswa itu **menguasai karyanya sendiri**.

Pola jawaban yang aman, tiga langkah:
1. **Akui** — "Betul, Pak, itu keliru."
2. **Jelaskan asal-usulnya** — "Itu sisa dari draf awal / itu belum saya perbarui."
3. **Nyatakan yang benar** — "Yang benar dan sesuai implementasinya adalah ..."

Jangan tambahkan alasan pribadi (sibuk kerja, dikejar waktu). Itu tidak ditanya dan tidak membantu.

---

# 🔴 KELOMPOK 1 — Kelihatan saat demo langsung

Dua temuan ini paling berisiko karena **penguji tidak perlu membaca apa pun untuk menemukannya**. Cukup melihat layarmu.

---

## ① ~~Naskah menyatakan server sudah di VPS, padahal demo jalan di localhost~~ ✅ SELESAI

> **Update:** Temuan ini sudah **tuntas diperbaiki**, bukan lagi sekadar jawaban andalan. Server sudah benar-benar di-deploy ke VPS Sumopod (Ubuntu 24.04 LTS, 2 vCPU, RAM 2 GB, 40 GB SSD, Jakarta), diakses lewat `https://api-svm.cupsky.my.id` dengan HTTPS asli. Ekstensi sudah diarahkan ke domain itu, bukan `localhost:8000`. Detail lengkap arsitekturnya ada di `10-deployment-vps.md`.
>
> Bagian di bawah ini **dibiarkan apa adanya** sebagai catatan kondisi *sebelum* diperbaiki — kalau penguji menyinggung soal ini, jawabannya sekarang cukup: "Sudah di-deploy, Pak, ini alamatnya" sambil menunjukkan `https://api-svm.cupsky.my.id/docs`. Tidak perlu lagi jawaban mengelak di bagian ❓ di bawah.

### Apa yang tertulis di naskah

Naskah menyebutkan ini sebagai **fakta yang sudah terjadi**, bukan rencana, di lima tempat:

| Paragraf | Kutipan |
|---|---|
| Sub-bab 3 (batasan) | "Server API **di-deploy** pada infrastruktur Virtual Private Server (VPS) yang terpisah dari perangkat pengguna" |
| Tahap Waterfall | "pengemasan model terlatih dalam format joblib untuk **deployment ke VPS**" |
| Alur pelatihan | "disimpan dalam format joblib ... untuk **di-deploy ke VPS**" |
| 4.x Komponen Server | "**di-deploy** pada Virtual Private Server (VPS) berbasis **Ubuntu Server 24.04 LTS** dan **dapat diakses melalui jaringan internet**" |
| 4.12 Kelayakan Teknologi | "di-deploy pada VPS dengan spesifikasi minimum **2 vCPU, RAM 2 GB, penyimpanan 40 GB**" |

### Apa yang sebenarnya ada di kode

```
extension/content.js:29   const API_URL       = "http://localhost:8000/predict";
extension/content.js:30   const BATCH_API_URL = "http://localhost:8000/predict/batch";
extension/content.js:94   fetch("http://localhost:8000/health", ...)
extension/content.js:235  fetch("http://localhost:8000/report", ...)
extension/popup.js:8      const API_BASE      = "http://localhost:8000";
extension/popup.html:317  <div class="sub" id="statusSub">localhost:8000</div>
```

Dan di `extension/manifest.json`:
```json
"host_permissions": [
  "http://localhost:8000/*",     ← hanya localhost
  ...
]
```

Tidak ada satu pun alamat VPS. Tidak ada `Dockerfile`, `nginx.conf`, `.service`, atau skrip deploy di repositori.

### 🔴 Kenapa ini nomor satu

Paragraf 4.x tentang rancangan popup menyebutkan popup menampilkan **"alamat server"**. Dan `popup.html:317` menampilkan teks itu secara harfiah:

> **localhost:8000**

Artinya: **begitu kamu membuka popup ekstensi di depan penguji, tulisan `localhost:8000` muncul di layar** — sementara naskahmu menyatakan servernya ada di VPS Ubuntu yang bisa diakses lewat internet.

Ini bukan sesuatu yang bisa disembunyikan. Ini terlihat dalam tiga detik pertama demo.

### ❓ Kalau ditanya

**Kalau VPS memang belum jadi:**
> "Terima kasih, Pak. Betul, pada demo ini server saya jalankan di lokal. Penulisan pada naskah menggambarkan **rancangan arsitektur** penempatan server, dan sampai naskah dikumpulkan proses deployment-nya belum tuntas. Seharusnya saya tulis sebagai rencana penerapan, bukan sebagai kondisi yang sudah berjalan. Ini kekeliruan saya dalam penulisan.
>
> Secara teknis, arsitekturnya sendiri tidak berubah — ekstensi berkomunikasi dengan server lewat HTTP REST, jadi memindahkannya ke VPS hanya mengubah satu konstanta alamat di `content.js` dan satu entri `host_permissions` di manifest. Tidak ada perubahan logika."

**Kalau VPS sudah jadi tapi demo tetap pakai lokal:**
> "Servernya sudah berjalan di VPS, Pak, tapi untuk demo ini saya pakai lokal supaya tidak bergantung pada koneksi internet ruangan. Kalau Bapak ingin, saya bisa tunjukkan yang versi VPS-nya."

⚠️ **Jangan mengklaim yang kedua kalau tidak bisa dibuktikan saat itu juga.** Penguji bisa minta ditunjukkan.

### 💡 Yang bisa kamu lakukan sebelum Rabu

Ini satu-satunya temuan yang masih **bisa** kamu perbaiki tanpa menyentuh naskah — dengan benar-benar men-deploy servernya. Kalau berhasil, temuan ini hilang sepenuhnya. Kalau tidak sempat, pakai jawaban di atas.

---

## ② ~~Ekstensi mendukung Instagram, naskah bilang Instagram itu saran penelitian lanjutan~~ ✅ SELESAI

> **Update:** Semua referensi Instagram sudah dihapus dari kode — `manifest.json` (`host_permissions` dan `content_scripts`), `content.js` (selektor dan deteksi platform), `popup.html`, dan CORS di `server.py`. Ekstensi sekarang murni YouTube-only, 100% konsisten dengan naskah. Bagian di bawah dibiarkan sebagai catatan riwayat.

### Apa yang tertulis di naskah

Pada Saran (BAB V):
> "Penelitian ini terbatas pada YouTube berbahasa Indonesia. Disarankan pengujian dan adaptasi pipeline pada platform seperti **Instagram** atau TikTok."

Dan di BAB IV, sistem digambarkan sebagai tiga komponen yang seluruhnya berorientasi YouTube.

### Apa yang sebenarnya ada di kode

`extension/manifest.json` — Instagram sudah terdaftar di **dua** tempat:
```json
"host_permissions": [ ..., "https://www.instagram.com/*" ],
"content_scripts": [{ "matches": [ ..., "https://www.instagram.com/*" ] }]
```

`extension/content.js` — deteksi platform dan selektor Instagram sudah ditulis:
```js
content.js:66    instagram: {
content.js:67      commentContainer: "ul._a9ym li",
content.js:404   if (url.includes("instagram.com")) return "instagram";
```

`extension/popup.html:368` — dan ini yang berbahaya:
> "Pastikan server Python aktif sebelum membuka **YouTube/Instagram**."

### 🔴 Kenapa ini berisiko tinggi

Sama seperti nomor ①: **kalimat itu muncul di dalam popup**. Saat kamu membuka panel ekstensi untuk demo, penguji membaca kata "Instagram" di layar — lima menit setelah kamu menyatakan penelitianmu terbatas pada YouTube.

Ini menimbulkan pertanyaan yang tidak enak: *"Kalau sudah mendukung Instagram, kenapa ditulis sebagai saran? Dan kalau belum diuji, kenapa sudah diaktifkan?"*

### ❓ Kalau ditanya

> "Betul, Pak. Selektor Instagram itu ada di kode sebagai **rintisan awal**, bukan fitur yang sudah teruji. Saya sempat mencoba memperluas ke Instagram, tapi struktur DOM Instagram jauh lebih sering berubah dan selektornya cepat basi, sehingga tidak saya lanjutkan dan tidak saya masukkan ke ruang lingkup penelitian.
>
> Model klasifikasinya sendiri sebenarnya tidak terikat platform — yang bekerja adalah teksnya. Yang platform-spesifik hanya lapisan pengambilan elemen DOM. Karena itu di bagian Saran saya sebut Instagram sebagai arah pengembangan, karena yang perlu diadaptasi hanya lapisan itu.
>
> Yang keliru dari saya adalah membiarkan sisa rintisan itu tetap aktif di manifest, padahal tidak pernah diuji dan tidak masuk ruang lingkup. Seharusnya saya nonaktifkan."

### 💡 Yang bisa kamu lakukan sebelum Rabu

Kode ekstensi **tidak** ikut disubmit sebagai bagian naskah, jadi ini masih bisa dirapikan. Menghapus tiga baris Instagram dari `manifest.json` dan mengubah satu kalimat di `popup.html` akan **menghilangkan temuan ini sepenuhnya** dari pandangan penguji, dan membuat kode jadi konsisten dengan naskah.

Kalau kamu mau, ini bisa dikerjakan dalam lima menit. Tinggal bilang.

---

# 🟠 KELOMPOK 2 — Ada di gambar yang diproyeksikan

Tiga temuan berikut ada di **Gambar 4.1 dan Gambar 4.3**, yang bukan cuma di naskah tapi juga **dipakai di slide PPT** (slide 13 dan 15). Jadi akan tampil besar di layar.

---

## ③ Gambar 4.1 masih menulis "Web Scraping via Node.js"

### Ketidakcocokannya

Kotak nomor 1 pada Gambar 4.1 berbunyi:
> **1. Pengumpulan Data (Web Scraping via Node.js)**

Padahal naskahmu di BAB II sudah menjelaskan sebaliknya, dengan tegas:
> "Pengumpulan data dari platform web dapat dilakukan melalui dua pendekatan, yaitu **web scraping** yang mem-parsing struktur HTML halaman secara langsung, dan pemanfaatan **API resmi** ... Pendekatan berbasis API lebih diutamakan karena ... **tidak melanggar ketentuan layanan platform**. Pada penelitian ini, pengumpulan data dilakukan melalui **YouTube Data API v3**."

Dan kode memang memanggil API resmi (`scraper/index.js:348`), bukan mengurai HTML.

### 🔴 Kenapa ini yang paling serius dari ketiga gambar

Karena menyangkut **argumen kelayakan hukum di Sub-bab 4.12**. Kamu berargumen sistemmu layak secara hukum **justru karena** memakai API resmi dan tidak melanggar ToS. Lalu ada gambar yang menulis "web scraping" — istilah yang di paragraf BAB II-mu sendiri dikontraskan sebagai pendekatan yang lebih berisiko.

Penguji yang jeli bisa berkata: *"Di BAB II Anda bilang API lebih baik karena tidak melanggar ToS, di gambar Anda tulis scraping. Yang mana?"*

### ❓ Kalau ditanya

> "Betul, Pak, keterangan pada gambar itu keliru. Itu istilah dari draf awal yang belum saya perbarui saat gambarnya saya buat. Yang benar — dan yang konsisten dengan naskah maupun implementasinya — adalah **YouTube Data API v3 resmi**, bukan pengurai HTML.
>
> Bisa saya tunjukkan di `scraper/index.js`, pemanggilannya ke endpoint `commentThreads` milik YouTube Data API menggunakan kunci API resmi, bukan permintaan HTTP ke halaman YouTube. Ini kekeliruan penulisan pada gambar."

💡 **Siapkan `scraper/index.js` terbuka di editor.** Menunjukkan barisnya jauh lebih kuat daripada menjelaskan lisan.

---

## ④ Gambar 4.3 menulis "Ekstraksi komentar via YouTube DOM"

Masalah yang sama, pada kotak **Scraper** di diagram arsitektur.

"YouTube DOM" berarti membaca struktur halaman — itu deskripsi *scraping*, bukan API.

**Yang benar:** *"Ekstraksi komentar via YouTube Data API v3"*.

### ❓ Kalau ditanya

Pakai jawaban yang sama dengan nomor ③. Kalau penguji menanyakan keduanya, akui sekaligus:

> "Dua-duanya keliru, Pak, dan penyebabnya sama — kedua gambar itu saya buat lebih awal, sebelum bagian pengumpulan datanya saya perbaiki, dan gambarnya tidak ikut saya perbarui."

⚠️ **Jangan bingung antara "scraper" sebagai nama komponen dan "scraping" sebagai metode.** Folder-nya memang bernama `scraper/` dan naskah menyebut "scraper berbasis Node.js" — itu **nama komponen**, dan tidak salah. Yang salah adalah keterangan yang menyebut **metodenya** sebagai scraping/DOM.

Kalau ditanya soal ini:
> "Nama komponennya memang `scraper`, Pak, karena tugasnya mengumpulkan data. Tapi metodenya API resmi, bukan pengurai HTML. Penamaannya memang kurang tepat."

---

## ⑤ Gambar 4.3 memuat dua detail kecil yang keliru

| Tertulis di gambar | Kondisi sebenarnya | Bukti |
|---|---|---|
| Slider confidence threshold **(0–100%)** | **50–95%**, langkah 5, default 75% | `popup.html:355` → `min="50" max="95" step="5"` |
| Hak akses: activeTab, **scripting**, storage | Hanya **storage, activeTab** | `manifest.json` baris 7–10 |

### Yang bikin nomor slider ini agak menyebalkan

Angka 0–100% di gambar itu **juga bertentangan dengan naskahmu sendiri**, bukan cuma dengan kode. Naskah menulis di dua tempat:

> "menyesuaikan nilai confidence threshold antara **50% hingga 95%** melalui slider" (rancangan popup)
> "Mekanisme confidence threshold (**50%-95%**, default 75%...)" (BAB V)

Jadi ini gambar melawan teks di dokumen yang sama. Kalau penguji membaca teksnya lalu melihat gambarnya, ketidakcocokan itu langsung terlihat tanpa perlu buka kode sama sekali.

### ❓ Kalau ditanya soal slider

> "Rentang yang benar 50% sampai 95%, Pak, dengan langkah 5% dan nilai bawaan 75% — seperti yang tertulis di naskah dan bisa dilihat langsung di popup-nya. Angka 0–100% pada gambar itu keliru.
>
> Batas bawah saya set 50% karena di bawah itu model praktis menebak — untuk klasifikasi dua kelas, keyakinan di bawah 50% berarti kelas lain yang lebih mungkin. Batas atas 95% supaya tidak ada pengguna yang menyetel begitu ketat sampai tidak ada spam yang tersaring sama sekali."

💡 Jawaban ini bagus karena kamu tidak cuma mengakui — kamu menunjukkan **kamu tahu alasan di balik angka aslinya**. Itu justru memperkuat kesan menguasai.

### ❓ Kalau ditanya soal izin `scripting`

> "Izin yang benar hanya `storage` dan `activeTab`, Pak. `scripting` tidak dipakai karena ekstensi ini memasukkan skripnya lewat deklarasi `content_scripts` di manifest, bukan lewat injeksi dinamis, jadi izin itu tidak diperlukan. Penulisan pada gambar keliru.
>
> Justru lebih baik begitu — semakin sedikit izin yang diminta, semakin kecil permukaan risikonya."

---

# 🟡 KELOMPOK 3 — Kecil, tapi tahu lebih baik daripada kaget

---

## ⑥ Penulisan "0,9741±0,30%" mencampur desimal dan persen

Muncul di **Abstrak** dan di **kesimpulan BAB V**:
> "5-fold cross-validation **0,9741±0,30%**"

Nilai rata-ratanya ditulis desimal (0,9741) tapi simpangan bakunya persen (0,30%). Dua satuan berbeda dalam satu ekspresi.

**Yang konsisten seharusnya:** `0,9741 ± 0,0030` atau `97,41% ± 0,30%`.

Kabar baiknya: di **BAB IV** penulisannya sudah benar dan menjelaskan keduanya:
> "rata-rata F1-macro sebesar 0,9741 dengan standar deviasi **0,0030 (±0,30%)**"

Jadi kamu punya pembelaan yang sah — bentuk lengkapnya ada di badan naskah, yang di abstrak cuma ringkasannya yang kurang cermat.

### ❓ Kalau ditanya

> "Betul, Pak, penulisan di abstrak itu kurang konsisten satuannya. Nilai sebenarnya rata-rata 0,9741 dengan simpangan baku 0,0030 — kalau dinyatakan persen jadi 0,30%. Di BAB IV saya tulis lengkap keduanya, tapi ringkasannya di abstrak jadi tercampur. Seharusnya ditulis 0,9741 ± 0,0030."

---

## ⑦ Kata "scraper" muncul di beberapa tempat sebagai nama komponen

Bukan kesalahan, tapi **titik yang gampang memicu pertanyaan** karena bertabrakan dengan argumen API di nomor ③–④.

Tempat kemunculannya:
- "Komentar YouTube dikumpulkan melalui **scraper** berbasis Node.js"
- "sistem ... terdiri dari tiga komponen utama: **scraper** berbasis Node.js untuk pengumpulan data"
- "Komponen **scraper** merupakan skrip berbasis Node.js ..."

Ini konsisten dengan nama foldernya (`scraper/`), jadi tidak salah secara faktual. Tapi kalau kamu sudah kena pertanyaan nomor ③, penguji bisa lanjut ke sini.

Jawabannya sudah ada di nomor ④ di atas: nama komponen ≠ metode.

---

## ⑧ Ranjau F1-macro 0,4963 di berkas laporan

Bukan kesalahan naskah — naskahmu sudah menangani ini dengan benar. Tapi tetap perlu diingat karena **ada di berkas yang bisa dibuka penguji**.

`reports/hard_set_evaluation.txt` memuat angka F1-macro **0,4963**, yang sekilas terlihat seperti model gagal total.

**Penyebabnya:** hard test set berisi **135 baris yang seluruhnya non-spam**. Karena tidak ada satu pun data kelas spam, F1 untuk kelas spam otomatis 0, dan rata-rata makro dari (0,9926 + 0) menghasilkan sekitar 0,4963.

**Naskahmu sudah menjelaskan ini dengan benar** dan itu poin bagus:
> "Perlu ditekankan bahwa hard test set ini **secara sengaja dirancang hanya berisi komentar non-spam** ... dataset ini berfungsi sebagai pengujian ketahanan model terhadap false positive."

Dan naskah melaporkan **accuracy 98,52%** untuk set ini, bukan F1-macro — itu pilihan metrik yang tepat.

### ❓ Kalau ditanya

> "F1-macro tidak bermakna pada dataset itu, Pak, karena isinya satu kelas saja. F1 untuk kelas spam pasti nol karena tidak ada data spam di dalamnya, sehingga rata-rata makronya jadi menyesatkan. Karena itu untuk hard test set saya laporkan **accuracy**, yaitu 98,52% — 133 dari 135 komentar berhasil dikenali sebagai non-spam, hanya 2 false positive. Metrik itu yang tepat karena tujuannya memang mengukur ketahanan terhadap false positive, bukan kemampuan mendeteksi spam."

Penjelasan lengkapnya ada di [`03-angka-ke-kode.md`](03-angka-ke-kode.md).

---

# Ringkasan satu halaman

Cetak bagian ini saja kalau perlu.

| # | Temuan | Risiko | Bisa diperbaiki sebelum Rabu? |
|---|---|---|---|
| ① | ~~Naskah bilang server di VPS, demo pakai `localhost:8000`~~ | ✅ **SELESAI** | Sudah live di `api-svm.cupsky.my.id`, lihat `10-deployment-vps.md` |
| ② | ~~Ekstensi mendukung Instagram, naskah bilang itu saran~~ | ✅ **SELESAI** | Instagram sudah dihapus total dari kode |
| ③ | Gambar 4.1: "Web Scraping via Node.js" | 🟠 Sedang | ⚠️ Gambar sudah tercetak |
| ④ | Gambar 4.3: "Ekstraksi komentar via YouTube DOM" | 🟠 Sedang | ⚠️ Gambar sudah tercetak |
| ⑤ | Gambar 4.3: slider "0–100%" & izin "scripting" | 🟠 Sedang | ⚠️ Gambar sudah tercetak |
| ⑥ | "0,9741±0,30%" campur satuan | 🟡 Rendah | ❌ Sudah disubmit |
| ⑦ | Kata "scraper" sebagai nama komponen | 🟡 Rendah | — bukan kesalahan |
| ⑧ | F1-macro 0,4963 di berkas laporan | 🟡 Rendah | — naskah sudah benar |

---

## Yang perlu kamu putuskan sekarang

**Untuk ① dan ②** — sudah beres. Server live di VPS, dan Instagram sudah dihapus total dari kode.

**Untuk ③, ④, ⑤** — gambarnya sudah ada di naskah cetak. Yang masih bisa diselamatkan: **versi di PPT**. Slide 13 dan 15 memakai gambar yang sama. Kalau gambarnya diperbaiki di PPT, setidaknya yang diproyeksikan besar-besar di layar sudah benar, dan kamu bisa menyebutnya sendiri:

> "Oh iya Pak, satu koreksi — pada naskah cetak gambar ini masih menulis 'web scraping', dan itu keliru. Yang benar API resmi, seperti yang tampil di slide ini."

💡 **Mengoreksi diri sendiri sebelum ditanya adalah langkah yang kuat.** Itu menunjukkan kamu membaca ulang karyamu dengan kritis, dan menghilangkan kesempatan penguji "menangkap" kesalahan. Yang tadinya temuan penguji berubah jadi bukti ketelitianmu.

Pertimbangkan menyebut nomor ③ dan ④ sendiri saat menjelaskan slide arsitektur.

---

## Yang TIDAK perlu kamu khawatirkan

Supaya proporsional — dari seluruh audit yang sudah dilakukan, ini yang sudah **terverifikasi bersih**:

- ✅ **Seluruh 21 angka empiris** terbukti bisa direproduksi dengan menjalankan ulang kodenya dari nol
- ✅ **30 rujukan** sudah diperiksa satu per satu ke sumber aslinya; 7 kesalahan yang ditemukan sudah diperbaiki sebelum submit
- ✅ **Komposisi hard test set** sudah diungkap dengan jujur di naskah
- ✅ **Dua hasil negatif** (aturan hibrida menurunkan akurasi, stemming tidak signifikan) dilaporkan apa adanya — ini justru nilai plus akademik
- ✅ **Format** sudah sesuai pedoman: penomoran halaman, penempatan keterangan gambar, istilah asing dimiringkan, abstrak sesuai templat

Delapan temuan di atas nyata, tapi tidak satu pun menyangkut **kebenaran hasil penelitianmu**. Semuanya soal keterangan yang tidak sinkron — bukan soal angka yang salah atau metode yang cacat.

Itu perbedaan yang penting, dan layak kamu pegang saat masuk ruang sidang.
