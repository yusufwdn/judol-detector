# Review Proposal Skripsi — 221232017 (Yusuf Wandana)

**Dokumen ditinjau:** `Skripsi/2-RIWAYAT/proposal/221232017_ProposalSkripsi (SEBELUM revisi 1 Agt).pdf` (40 halaman PDF / 32 halaman isi, tertanggal 7 Juni 2026)
**Dibandingkan terhadap:** `Skripsi/2-RIWAYAT/skripsi/2026-08-01/DRAFT_20260801.pdf` (draft final, 1 Agustus 2026)
**Acuan pedoman:** bagian **3.1 Sistematika Penulisan Proposal Skripsi** (hal. 9-10) + **BAB IV Teknik Penulisan** — ringkasan di `.docs/pedoman/PEDOMAN_RINGKAS.md` bagian **5B**

---

## RINGKASAN EKSEKUTIF

Kerangka proposalnya **sudah benar** — Batasan Sistem dengan Cakupan Modul/User, Tinjauan Pustaka tiga bagian, Metode Penelitian, dan Rencana Kegiatan berupa gantt chart. Itu bagian yang paling sering salah dan lu udah lolos.

Masalahnya ada di dua tempat:

1. **Satu temuan yang harus dibereskan apa pun yang terjadi:** ada placeholder `[Nama Jurnal — harap dilengkapi]` yang kebawa sampai dokumen jadi.
2. **Proposal ini ketinggalan ~2 bulan dari draft final.** Isinya masih mendeskripsikan sistem versi lama — DFD & Kamus Data (yang di skripsi diganti UML), metode *prototyping* (di skripsi jadi Waterfall), dan wawancara (yang di skripsi gak ada sama sekali).

| Prioritas | Jumlah | Perkiraan waktu |
|---|---|---|
| 🔴 Kritis | 5 | ~1 jam |
| 🟠 Penting (keselarasan) | 6 | ~2 jam |
| 🟡 Kosmetik | 7 | ~30 menit |

### Konteks

Dikonfirmasi user (1 Agustus 2026): **proposal ini harus disubmit untuk daftar sidang** — jadi dibaca dan dinilai, bukan arsip. Temuan keselarasan 🟠 karena itu ikut dikerjakan.

---

## STATUS PENGERJAAN (1 Agustus 2026)

Dikerjakan langsung di `Skripsi/1-AKTIF/221232017_ProposalSkripsi.docx`.
Cadangan: `Skripsi/2-RIWAYAT/backup/221232017_ProposalSkripsi (BACKUP asli).docx`.

| Temuan | Status |
|---|---|
| **K1** placeholder `[Nama Jurnal — harap dilengkapi]` | ✅ entri dihapus |
| **K2** 5 referensi yatim | ✅ Harnelia, Oh, Roshini, Samuel, Xiao dihapus |
| **K3** referensi "ResearchGate" & Khan | ✅ Khan diganti versi terverifikasi (2018, LGU Journal), sitasi badan tulisan ikut jadi 2018 |
| **K4** Lembar Persetujuan template skripsi | ✅ judul → "LEMBAR PERSETUJUAN PROPOSAL SKRIPSI", kalimat → "…disetujui untuk dilanjutkan ke tahap penelitian" |
| **K5** caption `Tabel 2II.2` | ✅ akar masalah ditemukan & diperbaiki (lihat catatan teknis di bawah) |
| **P4** label *web scraping* | ✅ judul 3.1.4 → "Pengumpulan Dataset melalui YouTube Data API"; kalimat 2.1.6 dinetralkan |
| **P5** "et al." → "dkk." | ✅ 0 sisa di badan tulisan maupun Daftar Pustaka |
| **P6** data referensi ≠ skripsi | ✅ Rosa 2020→2019 (3 ejaan diseragamkan), Angelo +inisial, Airlangga 2024b + vol/hal, Khairunnisa +Al Faraby, Ramadhan disamakan |
| **C1** judul "Normalisasi Karakter" | ✅ → "Modul Deteksi Real-Time Berbasis Chrome Extension" |
| **C2** rujukan gambar/tabel huruf kecil | ✅ 5 diperbaiki + Gambar 2.3 kini dirujuk bernomor |
| **C3** "Sedangkan" awal kalimat | ✅ → "Adapun" |
| **C4** "dimana" | ✅ kalimat disusun ulang |
| **P3** prototyping → Waterfall | ✅ **SELESAI** — 3.2 disalin dari Sub-bab 4.2 skripsi |
| **P1** wawancara | ✅ **SELESAI** — diverifikasi ke skripsi: 0 kemunculan "wawancara"/"responden"/"question list", jadi tidak pernah dilakukan. Sub-bab 3.1.3 dihapus, kalimat pembuka 3.1 diubah jadi "dua metode" |
| **P2** DFD & Kamus Data → UML | ✅ **SELESAI** — 2.1.7–2.1.10 diganti UML dari Sub-bab 2.15 skripsi |
| C6 Rencana Kegiatan sbg 3.3 · C7 nomor halaman Daftar Isi | ⬜ belum |

---

## SINKRONISASI ISI DENGAN SKRIPSI (1 Agustus 2026)

Atas permintaan user, isi proposal disalin langsung dari skripsi final `Skripsi/1-AKTIF/[DRAFT] 221232017.docx` untuk semua bagian yang punya padanan. **Kerangka proposal tetap dipertahankan** (Batasan Sistem, Tinjauan Pustaka, Metode Penelitian, Rencana Kegiatan) — yang diganti hanya isinya.

Cadangan sebelum sinkronisasi: `Skripsi/2-RIWAYAT/backup/221232017_ProposalSkripsi (BACKUP sebelum sinkron isi).docx`

| Bagian proposal | Disalin dari skripsi | Paragraf |
|---|---|---|
| 1.1 Latar Belakang | 1.1 | 6 → 6 |
| 1.2 Rumusan Masalah | 1.2 | 1 → 1 |
| 1.3 Tujuan dan Kegunaan | 1.3 (+1.3.1, 1.3.2) | 6 → 19 |
| 2.1.1 NLP | 2.1 | 3 → 4 |
| 2.1.2 String Normalization | 2.4 | 3 → 6 |
| 2.1.3 SVM | 2.6 (+ Gambar hyperplane) | 3 → 9 |
| 2.1.4 ML vs Deep Learning | 2.10 | 3 → 3 |
| 2.1.5 Spam Komentar YouTube | 2.12 | 3 → 3 |
| 2.1.6 Chrome Extension | 2.13 | 3 → 3 |
| 2.1.11 PIECES | 2.16 (+ Tabel PIECES) | 16 → 8 |
| 2.2 Studi Penelitian Terdahulu | 2.17 | 12 → 10 |
| 2.3 Persyaratan Sistem Konseptual | 2.18 | 18 → 18 |
| 3.1.1 Studi Pustaka | 1.4.1 | 5 → 6 |
| 3.1.2 Observasi | 1.4.2 | 5 → 10 |
| 3.2 Metode Pengembangan Sistem | 4.2 (Waterfall) | 11 → 13 |

Gambar ikut dimigrasi ke paket dokumen (bukan sekadar tautan), dan seluruh definisi penomoran list sudah tersedia di dokumen target sehingga format daftar bernomor tetap utuh.

**Daftar Pustaka ditulis ulang penuh** dari Daftar Pustaka skripsi (yang sudah diverifikasi satu per satu), berisi tepat sumber yang benar-benar dikutip pada isi baru: **17 entri**, alfabetis, tahun 2018–2026, tanpa yatim dua arah.

Empat entri lama otomatis gugur karena teks yang mengutipnya sudah diganti: Amin dkk. (2024), Jurafsky & Martin (2023), Koprawi & Putra (2023), Munfarida & Astuti (2017). Lima entri baru masuk mengikuti teks skripsi: Ardiansyah dkk. (2025), Kinanti & Indriyanti (2021), Oktavia (2024), Pratama (2026), Sari & Asmendri (2020), Sugiyono (2022).

### Hasil verifikasi keselarasan

| Istilah | Proposal sekarang | Selaras dengan skripsi? |
|---|---|---|
| Waterfall / prototyping | 2 / **0** | ✅ |
| YouTube Data API / web scraping | 3 / **0** | ✅ |
| "dkk." / "et al." | 11 / **0** | ✅ |
| menyembunyikan / memblokir | 6 / **0** | ✅ |
| Manifest V3 | 7 | ✅ |
| DFD / Kamus Data | **0** / 0 | ✅ |
| UML / use case / activity / sequence | 2 / 6 / 6 / 6 | ✅ |
| wawancara / responden / question list | **0** / 0 / 0 | ✅ |

### Penggantian DFD → UML dan penghapusan wawancara

Dua keputusan ini diambil setelah **diverifikasi langsung ke skripsi final**, bukan berdasarkan asumsi:

- **DFD: 0 kemunculan** di skripsi — memang sudah tidak dipakai. *Flowchart* muncul 5×, tetapi semuanya menunjuk ke **3.2.3 Flowchart Sistem Berjalan / Gambar 3.2** di BAB III, yaitu diagram sistem berjalan, **bukan sub-bab teori**. Teori pemodelan di BAB II skripsi adalah **UML** (use case 59×, activity 14×, sequence 14×). Karena 2.1.7–2.1.10 proposal berada di bawah *Tinjauan Teoritis*, padanan yang tepat adalah **Sub-bab 2.15 skripsi**, bukan flowchart.
  Dua sisa frasa "kamus data" di skripsi ternyata hanya istilah umum (*"kamus data (vocabulary)"* dan *"memperbarui kamus data"* soal blacklist), bukan teori Kamus Data ala DFD.
  → 84 elemen (4 sub-bab + 4 gambar simbol DFD + 2 tabel kamus data) diganti 14 elemen UML. Judul UML diturunkan dari Heading 2 → Heading 3 agar penomorannya pas menjadi **2.1.7 UML, 2.1.8 Use Case Diagram, 2.1.9 Activity Diagram, 2.1.10 Sequence Diagram**.

- **Wawancara: 0 kemunculan** di skripsi ("responden" 0, "question list" 0) — tidak pernah dilakukan. Sub-bab 3.1.3 beserta daftar pertanyaannya dihapus (12 elemen), dan kalimat pembuka 3.1 diubah dari *"tiga metode … studi pustaka, observasi, dan wawancara"* menjadi *"dua metode … studi pustaka dan observasi"*.

> Saat menyalin caption UML, field `STYLEREF` ikut dibuang, sehingga bug `Gambar 2II.6` yang masih ada di skripsi **tidak terbawa** ke proposal.

> ⚠️ **WAJIB DI WORD SETELAH INI:** isi berubah banyak, jadi **Daftar Isi, Daftar Gambar, dan Daftar Tabel harus di-refresh** — klik kanan masing-masing → *Update Field* → *Update entire table*. Nomor halaman dan judul sub-bab tidak akan benar sebelum ini dilakukan.

### Hasil verifikasi akhir

| Pemeriksaan | Hasil |
|---|---|
| Sisa "et al." (badan + daftar pustaka) | **0** ✅ |
| Sitasi tanpa entri / entri tanpa sitasi | **0 / 0** ✅ |
| Total entri Daftar Pustaka | **15** (minimum pedoman 15) ✅ |
| Urutan alfabetis | rapi ✅ (Khairunnisa dipindah sebelum Khan) |
| Rentang tahun | 2017–2025 (batas ≥2016) ✅ |
| Caption rusak | 0 ✅ |
| Integritas file | 43 part, 7 gambar, byte identik ✅ |

### Catatan teknis — akar masalah caption `2II.2`

Caption Tabel 2.2 mengandung **dua** sumber nomor sekaligus: teks literal `"2"` **plus** field `STYLEREF 1 \s` yang mengembalikan nomor bab dalam angka Romawi (`II`), lalu diikuti field `SEQ`. Saat Word me-render ulang, hasilnya jadi `Tabel` + `2` + `II` + `.` + `2` = **"Tabel 2II.2"**. Caption lain (Tabel 2.1, Gambar 2.1–2.4) tidak punya STYLEREF sehingga aman.

Perbaikannya: field `STYLEREF` dibuang, field `SEQ` dipertahankan — jadi penomoran otomatis tetap jalan dan bug tidak bisa muncul lagi.

> **Bug yang sama ada di skripsi** (`Gambar 2II.6`, temuan K1 laporan skripsi) dan kemungkinan besar penyebabnya identik.

### Dua referensi yang ternyata bermasalah saat diverifikasi

- **Amin dkk. (2024)** — entri lama hanya menulis `Amin, F., et al.` (APA melarang "et al." di daftar pustaka). Sumber aslinya terverifikasi: **7 penulis**, JTIIK 11(6), 1291–1302. Sudah dilengkapi.

- **Pratama dkk. (2025) — DIHAPUS, atribusinya salah.** Entri lama: *"Pratama, R., et al. (2025). Sistem Rekomendasi Wisata Kuliner di Gunungkidul Menggunakan Metode Content-Based Filtering (Penerapan Web Scraping via Ekstensi Chrome)"*. Verifikasi ke tiga sumber (jurnal JITET, ResearchGate, DOI 10.23960/jitet.v13i1.5955) menunjukkan artikel itu ditulis **L. H. Aljihadu**, bukan Pratama — dan bagian *"(Penerapan Web Scraping via Ekstensi Chrome)"* **bukan bagian dari judul asli**.
  Diganti dengan **Koprawi & Putra (2023)** — sumber *web scraping* yang asli, sudah terverifikasi, dan sudah dipakai di Daftar Pustaka skripsi. Kalimat di 2.1.6 disesuaikan agar cocok dengan isi sumber barunya. Jumlah referensi tetap 15.

---

## ✅ YANG SUDAH SESUAI PEDOMAN

| Aspek | Status |
|---|---|
| Bab I: Latar Belakang → Rumusan Masalah → Tujuan & Kegunaan → **Batasan Sistem** | ✅ sesuai 3.1 poin 3 |
| Batasan Sistem dipecah **Cakupan Modul** (1.4.1) + **Cakupan User** (1.4.2) | ✅ persis template |
| Bab II: Tinjauan Teoritis → Studi Penelitian Terdahulu → Persyaratan Sistem Konseptual | ✅ sesuai 3.1 poin 4 |
| Studi Penelitian Terdahulu: 2 penelitian (Angelo 2025, Airlangga 2024a) | ✅ minimum 2, ≤5 tahun |
| Bab III difokuskan ke metode pengumpulan data | ✅ sesuai 3.1 poin 5 |
| Wawancara dilengkapi **daftar pertanyaan** (5 butir) | ✅ pedoman mewajibkan *question list* |
| Rencana Kegiatan berupa **gantt chart** | ✅ sesuai 3.1 poin 6 |
| Halaman Sampul memuat unsur L-1 lengkap, tanpa kalimat "Diajukan sebagai syarat…" | ✅ benar untuk proposal |
| Tidak ada bullet point | ✅ pedoman 4.2.8 |
| Setiap teori ditutup kalimat kesimpulan | ✅ arahan dosen terpenuhi |
| Judul skripsi identik dengan draft final | ✅ |

---

## 🔴 TEMUAN KRITIS

### K1 — Placeholder belum diisi di Daftar Pustaka
**Lokasi:** Daftar Pustaka, halaman cetak 33

```
Samuel, & Kristiadi. (2025). Deteksi Teks Promosi Judi Online Menggunakan AI
Dengan Kombinasi NLP Dan Deep Learning. [Nama Jurnal — harap dilengkapi].
```

Catatan editorial `[Nama Jurnal — harap dilengkapi]` kebawa sampai dokumen final. Ini jenis temuan yang langsung merusak kesan profesional dokumen.

**Perbaikan:** karena sumber ini **tidak pernah disitasi** di badan tulisan (lihat K2), paling aman **dihapus saja**.

---

### K2 — Lima referensi tidak pernah disitasi (referensi yatim)
**Lokasi:** Daftar Pustaka, halaman cetak 32-33

Pedoman tegas: *"sumber yang ditulis dalam daftar pustaka benar-benar dirujuk dalam tubuh artikel."*

| Referensi | Disitasi di badan tulisan? |
|---|---|
| Harnelia, & Saputra, A. R. (2024) | ❌ tidak pernah |
| Oh, H. (2021) | ❌ tidak pernah |
| Roshini, P. (2022) | ❌ tidak pernah |
| Samuel, & Kristiadi. (2025) | ❌ tidak pernah |
| Xiao, A. S. (2024) | ❌ tidak pernah |

**Perbaikan:** hapus kelimanya. Daftar Pustaka jadi 15 entri — masih memenuhi minimum pedoman 15. Kalau mau lebih aman, sekalian selaraskan dengan Daftar Pustaka skripsi (lihat P1).

---

### K3 — Empat referensi tidak layak kutip secara akademis
**Lokasi:** Daftar Pustaka

| Entri | Masalah |
|---|---|
| Khan, R. A. (2019). … **ResearchGate**. | "ResearchGate" itu repositori, **bukan nama jurnal**. Di skripsi sudah benar: *LGU International Journal for Electronic Crime Investigation, 2(2)*, dan tahunnya **2018** |
| Oh, H. (2021). … **ResearchGate**. | idem — repositori, bukan jurnal |
| Xiao, A. S. (2024). … **ResearchGate**. | idem |
| Roshini, P. (2022). … International Journal of Computer Science. | tanpa volume, nomor, maupun halaman |

Tiga dari empat ini sudah masuk daftar yatim di K2, jadi terhapus sekalian. Yang tersisa **Khan** — wajib diperbaiki karena disitasi di 2.1.5.

**Perbaikan Khan** — pakai versi yang sudah benar di skripsi:
```
Khan, R. A. (2018). Spammer detection: A study of spam filter comments on YouTube
     videos. LGU International Journal for Electronic Crime Investigation, 2(2).
```
Sekaligus ubah sitasi di badan tulisan 2.1.5 dari `(Khan, 2019)` → `(Khan, 2018)`.

---

### K4 — Lembar Persetujuan memakai template SKRIPSI, bukan PROPOSAL
**Lokasi:** halaman ii

Yang tertulis sekarang:
> **LEMBAR PERSETUJUAN DOSEN PEMBIMBING**
> "Telah diperiksa dan disetujui sebuah **skripsi untuk diajukan pada sidang skripsi**, atas nama:"
> … Judul **Skripsi** : …

Ini template **L-5 (skripsi)**. Untuk proposal, pedoman memakai template **L-2** yang bunyinya:
> **Lembar Persetujuan Proposal Skripsi**
> … Nama / NIM …
> "**Proposal Skripsi ini telah disetujui oleh:**"
> (Pembimbing I) (Pembimbing II)
> "Pada Tanggal: …"

Secara logika juga janggal — proposal tidak diajukan ke sidang, melainkan disetujui untuk **dilanjutkan ke tahap penelitian**.

**Perbaikan:** ganti judul halaman jadi **"LEMBAR PERSETUJUAN PROPOSAL SKRIPSI"** dan kalimatnya jadi *"Proposal Skripsi ini telah disetujui oleh:"*. Tanggalnya juga masih kosong (`Jakarta, …………………….`) — isi atau hapus.

---

### K5 — Caption tabel rusak: "Tabel 2II.2"
**Lokasi:** halaman cetak 19

```
Tabel 2II.2 Kode Karakter Kamus Data     ← salah
Tabel 2.2 Kode Karakter Kamus Data       ← benar
```

Persis bug yang sama dengan `Gambar 2II.6` di draft skripsi — *cross-reference field* Word yang rusak. Daftar Tabel sudah menulis "Tabel 2.2" dengan benar.

---

## 🟠 TEMUAN KESELARASAN (proposal vs draft final)

Ini hasil perbandingan istilah antara kedua dokumen:

| Konsep | Proposal | Draft Final | Status |
|---|---|---|---|
| Metode pengembangan | **prototyping** | **Waterfall** (11×) | ❌ bertentangan |
| Pemodelan perancangan | **DFD + Kamus Data** (34×) | **UML**: use case, activity, sequence (26×) | ❌ bertentangan |
| Metode pengumpulan data | studi pustaka + observasi + **wawancara** | studi pustaka + observasi saja | ❌ wawancara hilang |
| Istilah pengambilan data | *web scraping* (5×) | Pengumpulan Data melalui **API** | ❌ sudah diperbaiki di skripsi |
| Gaya sitasi | **"et al."** (10×) | **"dkk."** (21×) | ❌ tidak seragam |
| Kata kerja aksi | mem**blokir** | menyembunyikan | ⚠️ beda makna |
| Sumber teori PIECES | Munfarida & Astuti (2017) | Kinanti & Indriyanti (2021) | ⚠️ beda sumber |
| Server / REST API / FastAPI | — | ada (20×, 9×) | ➕ belum ada di proposal |
| Baseline NB & Logistic Regression | — | ada (17×, 12×) | ➕ |
| Cross-validation, GridSearchCV, hard test set | — | ada (12×, 9×, 13×) | ➕ |
| Platt Scaling, N-gram, Sastrawi | — | ada | ➕ |
| Mode Redupkan/Hilangkan, confidence threshold | — | ada (16×, 13×) | ➕ |
| F1-score sebagai metrik utama | — | ada (36×) | ➕ |

Yang bertanda ➕ **wajar** — itu hasil penelitian yang memang baru ketahuan setelah dikerjakan. Proposal tidak perlu memuatnya. Yang perlu ditangani adalah yang ❌.

---

### P1 — Wawancara: dijanjikan di proposal, tidak ada di skripsi ⚠️ RISIKO SIDANG TERTINGGI
**Lokasi:** proposal Sub-bab 3.1.3, halaman cetak 28-29

Proposal menyatakan dengan sangat spesifik:
> "Penelitian ini menggunakan **tiga** metode pengumpulan data yang saling melengkapi, yaitu studi pustaka, observasi, dan **wawancara**."

Lengkap dengan target responden, teknik *unstructured interview*, dan 5 butir daftar pertanyaan.

**Draft final tidak menyebut wawancara sama sekali** (0 kemunculan). Sub-bab 1.4 skripsi hanya memuat dua metode: Studi Pustaka dan Observasi.

**Kenapa ini berisiko:** kalau penguji memegang proposal, pertanyaan *"mana hasil wawancaranya?"* hampir pasti muncul. Ini pertanyaan yang sulit dijawab kalau wawancaranya memang tidak dilakukan.

**Tiga pilihan — pilih sesuai kenyataan:**

- **(A) Wawancaranya tidak jadi dilakukan** → hapus Sub-bab 3.1.3 dari proposal, ubah kalimat pembuka 3.1 jadi *"dua metode pengumpulan data yang saling melengkapi, yaitu studi pustaka dan observasi."* Ini yang paling jujur dan bikin dua dokumen selaras.
- **(B) Wawancaranya dilakukan tapi tidak ditulis di skripsi** → justru tambahkan ringkasan hasilnya ke skripsi (bisa masuk di 1.4 atau BAB III). Ini malah **memperkuat** skripsi karena menambah justifikasi kebutuhan pengguna secara empiris.
- **(C) Biarkan** → siapkan jawaban lisan: *"Wawancara awalnya direncanakan sebagai data pendukung, namun pada pelaksanaannya justifikasi kebutuhan sudah cukup terpenuhi dari studi pustaka dan observasi empiris terhadap komentar, sehingga tidak dilanjutkan."* Bisa diterima, tapi lebih lemah dari (A).

**Rekomendasi: (A)** kalau memang tidak dilakukan — 5 menit kerja, risiko hilang total.

---

### P2 — DFD & Kamus Data: 8 halaman teori yang tidak dipakai di skripsi
**Lokasi:** proposal Sub-bab 2.1.7 s/d 2.1.10, halaman cetak 12-20

Proposal memuat teori Data Flow Diagram, Kamus Data, Isi Kamus Data, dan Simbol Kamus Data — lengkap dengan 4 gambar simbol DFD dan 2 tabel simbol kamus data. Totalnya **±8 halaman dari 32 halaman isi**, alias seperempat proposal.

Draft final **tidak memakai DFD maupun Kamus Data sama sekali**. Perancangan seluruhnya memakai **UML** (use case diagram, activity diagram, sequence diagram) sesuai jalur *Orientasi Objek* pedoman.

**Perbaikan yang disarankan:** ganti 2.1.7–2.1.10 dengan satu sub-bab **"2.1.7 Unified Modeling Language (UML)"** yang memuat use case, activity, dan sequence diagram. Materinya bisa diambil langsung dari Sub-bab 2.15 skripsi — tinggal salin, sudah rapi dan sudah ada gambar simbolnya.

Kalau tidak sempat, minimal sadari bahwa ini titik lemah: penguji bisa bertanya *"kenapa di proposal DFD tapi di skripsi UML?"* Jawaban yang bisa dipakai: *"Setelah pendalaman perancangan, sistem ini berorientasi objek dan berbasis interaksi antar komponen, sehingga UML lebih tepat daripada DFD yang berorientasi aliran data pada sistem terstruktur."* — itu jawaban yang benar dan defensible.

---

### P3 — Metode pengembangan: prototyping vs Waterfall
**Lokasi:** proposal Sub-bab 3.2, halaman cetak 30

Proposal: *"menggunakan model **prototyping** yang disesuaikan dengan alur kerja pembelajaran mesin."*
Draft final: **Waterfall**, dibahas di 2.9 dan diterapkan penuh di 4.2 dengan kelima tahapannya.

**Perbaikan:** ubah proposal jadi Waterfall agar selaras, atau siapkan jawaban kenapa berubah. Mengubah proposal lebih simpel — cukup ganti nama metode dan sesuaikan penjelasan tahapannya (materi Waterfall sudah tersedia di 4.2 skripsi).

---

### P4 — Istilah "web scraping" (masalah yang sama seperti di skripsi)
**Lokasi:** proposal Sub-bab 3.1.4, halaman cetak 30 — judulnya *"Pengumpulan Dataset Publik (Web Scraping)"*

Isinya sendiri sebenarnya sudah benar: *"memanfaatkan fasilitas YouTube Data API v3 … melalui skrip backend Node.js untuk memanggil endpoint API"*. Jadi cuma **labelnya** yang salah — persis temuan K4 di skripsi yang kemarin sudah diperbaiki.

**Perbaikan:** ubah judul jadi **"3.1.4 Pengumpulan Dataset melalui YouTube Data API"**, dan ganti frasa *"teknik ekstraksi data (web scraping)"* jadi *"teknik ekstraksi data melalui API resmi"*.

Ada juga di 2.1.6 (hal. 11): *"Teknik web scraping melalui ekstensi Chrome merupakan metode yang andal untuk mengekstrak data…"* dengan sitasi (Pratama et al., 2025) — kalimat ini tidak relevan dengan sistem yang dibangun (ekstensinya tidak melakukan scraping, dia mengirim teks ke API). Sebaiknya dihapus.

---

### P5 — Gaya sitasi belum diseragamkan seperti skripsi
**Lokasi:** seluruh badan tulisan

Proposal masih memakai **"et al."** di 10 tempat, sementara skripsi sudah diseragamkan ke **"dkk."** sesuai pedoman.

| Perbaikan | Alasan |
|---|---|
| `(Herawati et al., 2025)` → `(Herawati dkk., 2025)` | 3 penulis |
| `(Angelo et al., 2025)` → `(Angelo dkk., 2025)` | 3 penulis |
| `(Chua et al., 2024)` → `(Chua dkk., 2024)` | 4 penulis |
| `(Nanda et al., 2022)` → `(Nanda dkk., 2022)` | 4 penulis |
| `(Amin et al, 2024)` → `(Amin dkk., 2024)` | catat: kurang titik setelah "al" |
| `(Pratama et al., 2025)` → `(Pratama dkk., 2025)` | (kalau kalimatnya tidak jadi dihapus, lihat P4) |
| `(Khairunnisa & Adiwijaya, 2021)` → `(Khairunnisa dkk., 2021)` | sumbernya **3 penulis** |
| `(Abdillah, Premana & Bhakti, 2021)` → `(Abdillah dkk., 2021)` | 3 penulis, APA tidak mengeja semua |

Di **Daftar Pustaka** juga ada dua entri yang salah kaidah — APA mewajibkan semua penulis dieja, tidak boleh "et al.":
- `Amin, F., et al. (2024).`
- `Pratama, R., et al. (2025).`

---

### P6 — Data referensi berbeda antara proposal dan skripsi
Sumber yang sama tapi ditulis beda di dua dokumen — kalau dibaca berdampingan, kelihatan tidak konsisten:

| Sumber | Proposal | Skripsi (sudah diverifikasi benar) |
|---|---|---|
| Khan | 2019, "ResearchGate" | **2018**, LGU Int. Journal for Electronic Crime Investigation, 2(2) |
| Rosa & Shalahuddin | **2020** | **2019** |
| Airlangga 2024b | tanpa volume/halaman | MALCOM, 4(4), 1533–1538 + subjudul lengkap |
| Angelo | `Robet` (tanpa inisial) | `Robet, R.` |
| Ramadhan & Fauzan | Proceedings Series on Physical & Formal Sciences, 6, 183–190 | Prosiding SENATEK 2023, 6 + DOI |

Nama **Rosa & Shalahuddin** bahkan ditulis **tiga cara berbeda** di dalam proposal sendiri: `Rosa A.S M. Shalahudin, 2020` (hal. 12), `Rosa & Shalahuddin, 2020` (hal. 15), `Rosa dan Shalahudin, 2020` (hal. 16).

**Perbaikan tercepat:** untuk semua sumber yang dipakai di dua dokumen, salin saja entrinya dari Daftar Pustaka skripsi — sudah diverifikasi dan formatnya APA konsisten.

---

## 🟡 TEMUAN KOSMETIK

### C1 — Sub-bab 2.3 poin 2 salah judul
**Lokasi:** halaman cetak 24-25

Judulnya **"2. Normalisasi Karakter"**, tapi isinya seluruhnya tentang pembacaan DOM, *content script*, dan manipulasi CSS — itu **modul Chrome Extension**, bukan normalisasi. Akibatnya poin 1 dan poin 2 sama-sama berjudul soal normalisasi, padahal isinya beda.

Di skripsi sudah benar: *"Modul Deteksi Real-Time Berbasis Chrome Extension"*. Pakai judul itu.

### C2 — Rujukan gambar/tabel huruf kecil
**Lokasi:** halaman 13, 14, 15, 18

Tertulis `gambar 2.1`, `gambar 2.2`, `gambar 2.4`, `tabel 2.1` — huruf kecil. Pedoman meminta penyebutan spesifik dengan kapital (`Gambar 2.1`, `Tabel 2.1`), dan skripsi sudah konsisten kapital.

Selain itu **Gambar 2.3** tidak dirujuk dengan nomornya sama sekali — tertulis *"dapat dilihat pada gambar di bawah ini"*. Ganti jadi *"…dapat dilihat pada Gambar 2.3."*

### C3 — Kalimat diawali "Sedangkan"
Pedoman 4.6.3.a melarang "sehingga" dan "sedangkan" di awal kalimat. Ada 1 kejadian.

### C4 — Kata "dimana"
Pedoman 4.6.3.c menandai "dimana" sebagai bentuk tidak baku (terjemahan harfiah *where*). Ada 1 kejadian — ganti jadi "di mana" (kalau keterangan tempat) atau susun ulang kalimatnya.

### C5 — Kata ganti orang "Anda" di daftar pertanyaan wawancara
**Lokasi:** halaman cetak 29, 6 kemunculan

Pedoman 4.6.2 melarang kata ganti orang. Tapi ini **daftar pertanyaan wawancara** yang justru diwajibkan pedoman untuk dilampirkan, dan pertanyaan wawancara memang ditujukan ke responden.

**Rekomendasi: biarkan.** Ini defensible — kalau ditanya, jawab bahwa itu kutipan verbatim instrumen penelitian, bukan narasi penulis. (Kalau P1 opsi A dipilih, bagian ini terhapus dengan sendirinya.)

### C6 — Rencana Kegiatan sebagai 3.3
Pedoman menempatkan **Rencana Kegiatan** sebagai butir tersendiri (poin 6), sejajar dengan Bab III, bukan sebagai sub-bab 3.3. Template Daftar Isi L-3 juga menampilkannya sejajar.

Prioritas rendah — tapi kalau mau persis template, keluarkan jadi bagian tersendiri setelah Bab III.

### C7 — Daftar Isi tidak memuat nomor halaman Daftar Pustaka & Lampiran
"DAFTAR PUSTAKA" tercantum tanpa nomor halaman, dan "LAMPIRAN" tidak tercantum sama sekali padahal ada halaman L-1 berisi gantt chart. Pedoman 4.3.1.d: penomoran Daftar Pustaka menyambung ke halaman lampiran.

---

## URUTAN KERJA YANG DISARANKAN

**Kalau proposal cuma arsip — kerjakan ini saja (~30 menit):**
1. K1 hapus entri berisi placeholder
2. K2 hapus 5 referensi yatim
3. K3 perbaiki entri Khan + ubah sitasi jadi 2018
4. K5 perbaiki caption `Tabel 2II.2`
5. K4 ganti template Lembar Persetujuan

**Kalau proposal ikut dinilai/dibaca penguji — lanjutkan (~2 jam):**
6. **P1 wawancara** ← paling penting, tentukan (A)/(B)/(C)
7. P4 istilah *web scraping* → API
8. P5 seragamkan "et al." → "dkk."
9. P6 samakan data referensi dengan skripsi
10. P3 prototyping → Waterfall
11. C1 judul "Normalisasi Karakter" → "Modul Deteksi Real-Time Berbasis Chrome Extension"

**Kalau masih ada waktu:**
12. P2 ganti DFD & Kamus Data jadi UML (paling makan waktu, tapi paling besar dampaknya untuk keselarasan)
13. C2, C3, C4, C6, C7

---

## CATATAN TAMBAHAN

1. **Target dataset 5.000 komentar** (hal. 30) — realisasinya **6.690**. Ini bagus, target terlampaui. Tidak perlu diubah, tapi siap-siap kalau ditanya: *"target awal 5.000, realisasi 6.690 karena proses scraping menghasilkan data lebih banyak dari perkiraan."*

2. **Klaim akurasi di 2.1.3** — proposal menulis *"di atas 90%"* mengutip Amin dkk. (2024), skripsi menulis *"di atas 96%"* mengutip Ardiansyah dkk. (2025). Keduanya konsisten dengan sumbernya masing-masing, jadi tidak masalah. Hanya perlu diingat kalau ditanya.

3. **Sumber PIECES berbeda** — proposal pakai Munfarida & Astuti (2017), skripsi pakai Kinanti & Indriyanti (2021). Dua-duanya sah (2017 masih dalam batas 10 tahun). Kalau mau seragam, pakai Kinanti di dua-duanya.

4. **Gantt chart-nya bagus** — periodenya April–Agustus, dan realisasi sidang 11 Agustus 2026 masih masuk kolom terakhir "Persiapan sidang & PPT". Konsisten.

5. **Jumlah referensi** — proposal punya 20 entri. Setelah 5 yatim dihapus jadi **15**, pas di batas minimum pedoman. Kalau mau aman, tambahkan beberapa sumber dari Daftar Pustaka skripsi yang memang relevan dengan teori di proposal (misalnya Kaddoura dkk. 2022 untuk heuristik, atau Koprawi & Putra 2023 untuk pengumpulan data).

---

# AUDIT DAFTAR PUSTAKA — 1 Agustus 2026 (SELESAI)

Pemicu: format Daftar Pustaka proposal terlihat berbeda dari skripsi. Dicek di level XML, plus verifikasi validitas ke-17 rujukan lewat Crossref API dan halaman penerbit.

## A. Temuan format (proposal)

| | Skripsi | Proposal (sebelum) |
|---|---|---|
| Hanging indent | `w:ind left=540 hanging=540` di **31/31** entri | **tidak ada sama sekali**, 0/17 |
| Run kosong sisa | – | 18 run kosong (sebagian ber-flag italic) |

Akar masalahnya: saat sinkronisasi isi 1 Agustus, Daftar Pustaka proposal ditulis ulang sebagai paragraf polos tanpa menyalin `pPr` dari entri skripsi. Sudah diperbaiki — 17/17 entri kini memakai indent yang identik dengan skripsi.

## B. Temuan validitas rujukan (kena SKRIPSI dan PROPOSAL)

Semua 17 rujukan proposal **terbukti nyata** — tidak ada yang halusinasi. Tetapi 6 entri punya data yang salah atau tidak lengkap:

| # | Entri | Masalah | Sumber verifikasi |
|---|---|---|---|
| V1 | Kinanti & Indriyanti (2021) | **Nama penulis salah.** Penulis pertama adalah *Nanda Kinanti Amelia **Putri*** → APA-nya `Putri, N. K. A.` Judul juga terpotong, dan halaman tertulis 1–7 padahal **78–84** | halaman artikel JEISBI 39730 |
| V2 | Oktavia (2024) | Ditulis penulis tunggal, aslinya **5 penulis** (Oktavia, Iqbal, Saputra, Zulfikar, Saifudin) | halaman artikel BIIKMA 1093 |
| V3 | Abdillah dkk. (2021) | Halaman tidak ada → **160–170** | jurnal.umus.ac.id/intech/556 |
| V4 | Ramadhan & Fauzan (2023) | Nama prosiding keliru (SENATEK adalah nama acara, bukan terbitan) → **Proceedings Series on Physical & Formal Sciences**; halaman **192–199** hilang | Crossref 10.30595/pspfs.v6i.869 |
| V5 | Chua dkk. (2024) | DOI hilang → `10.37934/araset.60.2.153164` | Crossref |
| V6 | Sari & Asmendri (2020) | DOI hilang → `10.15548/nsc.v6i1.1555` | ejournal.uinib.ac.id |

Rujukan yang dicek dan **sudah benar apa adanya**: Airlangga 2024a/2024b, Angelo dkk. 2025, Ardiansyah dkk. 2025, Herawati dkk. 2025, Khairunnisa dkk. 2021, Khan 2018, Nanda dkk. 2022, Pratama 2026 (JITET 14(1), terbit 17 Januari 2026 — nyata), Rosa & Shalahuddin 2019, Sugiyono 2022.

## C. Temuan tambahan di SKRIPSI

| # | Masalah |
|---|---|
| V7 | Entri **Arrayyan dkk. (2025) terbelah jadi 2 paragraf** — sisa dari penyisipan K5. Paragraf kedua bahkan indent-nya beda (`left=400050`, tanpa hanging), jadi tampil rusak. Sudah digabung. Jumlah entri sebenarnya **30**, bukan 31. |
| V8 | `Angelo, Robet & Hendrik (2025)` masih tersisa di daftar Studi Penelitian Terdahulu (Bab II) — bentuk yang sudah diseragamkan jadi `dkk.` di tempat lain. Ada di **dua-duanya**. Sudah jadi `Angelo dkk. (2025)`. |

## D. Status akhir (terverifikasi)

| | Skripsi | Proposal |
|---|---|---|
| Jumlah entri | 30 | 17 (min. pedoman 15) |
| Urutan alfabetis | OK | OK |
| Hanging indent | 30/30 | 17/17 |
| Entri terbelah | 0 | 0 |
| Entri tidak dikutip | 0 | 0 |
| Sitasi tanpa entri | 0 | 0 |
| `et al.` | 0 | 0 |
| Integritas file | 66 part / 26 gambar / 5.185.122 byte — identik | 47 part / 11 gambar / 711.655 byte — identik |

Cadangan: `Skripsi/2-RIWAYAT/backup/… (BACKUP sebelum fix daftar pustaka).docx` (dua-duanya).

**Sisa pekerjaan manual:** karena entri Kinanti berubah jadi Putri dan urutannya bergeser, Daftar Isi tidak terpengaruh — tapi kalau Daftar Pustaka pernah dijadikan field/bibliography otomatis, refresh dulu. Nomor halaman Daftar Pustaka skripsi (P1) masih belum diberi nomor.

---

# PERBAIKAN LANJUTAN PROPOSAL — 1 Agustus 2026 (SELESAI)

## E. Penomoran halaman — 3 bug struktural

Pola yang benar (diambil dari skripsi): **satu section per BAB**, `titlePg` aktif, halaman pertama BAB memakai `first_page_footer` (nomor di bawah-tengah), halaman berikutnya memakai `header` (nomor di kanan atas).

| # | Bug | Perbaikan |
|---|---|---|
| N1 | Header **BAB II kosong** (`PAGE=False`) → nomor hilang di halaman ke-2 dst. | Isi header disalin dari BAB I |
| N2 | BAB III punya `<w:pgNumType w:start="1"/>` → **penomoran restart**. Terlihat di Daftar Isi: `BAB III METODE PENELITIAN … 1` | Elemen `pgNumType` dihapus, penomoran mengalir |
| N3 | Ada section break liar sebelum 3.1.3 + 3 paragraf kosong (sisa penghapusan sub-bab wawancara). Karena `titlePg` aktif, halaman itu tampil bergaya "halaman pembuka BAB" di tengah bab. | Break + paragraf kosong dihapus → BAB III jadi satu section |
| N4 | DAFTAR PUSTAKA menumpang di section BAB III sehingga ikut bernomor. | Dibuatkan section sendiri dengan header/footer kosong (meniru sec7 skripsi). Entri di Daftar Isi dipertahankan. |
| N5 | Header LAMPIRAN masih menampilkan nomor biasa di kanan atas padahal footer sudah `L-n`. | Header LAMPIRAN dikosongkan |

Hasil akhir: sec2/sec3/sec4 (BAB I/II/III) `hdr=True ftr1=True start=None`; sec5 (Daftar Pustaka) semua `False`; sec6 (Lampiran) hanya footer `L-n`.

## F. Wording BAB II & III — 6 rujukan nyasar sisa copy-paste

Semua akibat penyalinan isi dari skripsi tanpa penyesuaian konteks proposal.

| Lokasi | Sebelum | Sesudah |
|---|---|---|
| 2.1.2 | "diuraikan lebih lanjut pada **Bab IV**" | "menjadi bagian dari rancangan sistem yang diusulkan dalam penelitian ini" |
| 2.1.11 | "kelemahan sistem berjalan pada **Bab III** … solusi pada **Bab IV**" | "kelemahan sistem yang berjalan saat ini … solusi yang diusulkan dalam penelitian ini" |
| 3.2 | "telah diuraikan pada **sub-bab 2.9**" (penomoran skripsi; proposal **tidak punya teori Waterfall**) | diganti definisi ringkas Waterfall + sitasi Rosa & Shalahuddin (2019) |
| 3.2 | "diuraikan pada **sub-bab 4.1**" | dihapus, kalimat disambung |
| 3.2 | "pada **sub-bab perancangan sistem** di bab ini" | "sebagaimana dijelaskan pada Sub-bab 2.1.7 sampai dengan 2.1.10" |
| 3.2 | "pada **sub-bab pengujian sistem** di bab ini" | "akan dilaporkan secara lengkap dalam laporan skripsi" |

Verifikasi: 0 kemunculan `Bab III/IV/V` maupun `sub-bab X.Y` yang menggantung.

## G. Keselarasan data dengan project

- **Dataset**: proposal menargetkan 5.000 komentar; `data/comments.csv` berisi **6.690** (2.332 spam / 4.358 non-spam). Atas keputusan penulis, angka disamakan jadi 6.690 lengkap dengan komposisi kelasnya.
- **Sudah cocok tanpa perubahan**: YouTube Data API v3 + scraper Node.js, Manifest V3, FastAPI + Scikit-learn, tiga algoritma pembanding (Linear SVM / Multinomial NB / Logistic Regression), eksperimen N-gram & stemming.
- **VPS**: klaim *deploy* ke VPS di 3.2 dipertahankan — penulis menyatakan akan benar-benar melakukan deployment. Konsisten dengan skripsi (K6).

## H. Rujukan gambar

Keempat gambar BAB II sebelumnya **tidak pernah disebut nomornya** di badan teks (melanggar arahan lisan dosen soal kalimat pengantar). Ditambahkan kalimat pengantar untuk semuanya.

Selain itu nilai `SEQ` yang tersimpan di caption masih warisan skripsi (2, 4, 5, 6). Nilai tersimpan ditulis ulang jadi 1, 2, 3, 4 sehingga caption sudah benar **bahkan sebelum** field di-*update*, dan tetap benar sesudahnya.

| Caption sekarang | Dirujuk di |
|---|---|
| Gambar 2.1 Ilustrasi Hyperplane dan Margin pada Algoritma Linear SVM | paragraf baru sebelum gambar |
| Gambar 2.2 Simbol-Simbol Use Case Diagram | akhir 2.1.8 |
| Gambar 2.3 Simbol-Simbol Activity Diagram | akhir 2.1.9 |
| Gambar 2.4 Simbol-Simbol Sequence Diagram | akhir 2.1.10 |
| Tabel 2.1 Aspek-Aspek Analisis PIECES | sudah dirujuk sejak awal |

Integritas file: 7 gambar / 696.953 byte, identik dengan cadangan.
Cadangan: `… (BACKUP sebelum fix nomor halaman).docx` dan `… (BACKUP sebelum rujukan gambar).docx`.
