# Catatan Revisi Sidang Skripsi

**Mahasiswa:** Yusuf Wandana (221232017)
**Tanggal sidang:** ~Agustus 2026 (naskah yang disidangkan: `BERKAS/221232017_SKRIPSI.pdf`, 129 hal)
**Status dokumen ini:** dicatat 2026-08-23, dari penuturan lisan mahasiswa (belum ada lembar revisi resmi)

---

## Acuan file (sudah diverifikasi identik)

| File | Tanggal | Peran |
|---|---|---|
| `1-AKTIF/[DRAFT] 221232017.docx` | 1 Agt 21:32 | **file kerja untuk revisi** |
| `6-FINAL-CLONE/221232017_Skripsi_FINAL.docx` | 1 Agt 22:04 | clone |
| `6-FINAL-CLONE/221232017_Skripsi_FINAL.pdf` | 1 Agt 22:04 | export |
| `BERKAS/221232017_SKRIPSI.pdf` | 11 Agt 14:51 | export ulang (isi sama) |

Verifikasi: MD5 `word/document.xml` kedua docx sama (`76a28edf4d716e2f646952e78b5b69e2`);
diff teks per-halaman kedua PDF = 0 halaman berbeda; keduanya 129 halaman.

Teks lengkap naskah hasil ekstraksi: [`naskah_sidang_extracted.txt`](naskah_sidang_extracted.txt)
(format: `===== HAL PDF n =====` per halaman; nomor halaman PDF, bukan nomor cetak).
Offset: hal PDF 14 = BAB I hal 1. Jadi **hal cetak = hal PDF − 13** (untuk bagian isi).

---

## Catatan Penguji

### Dosen 1 — urgensi & ruang lingkup masalah

Inti keberatan:
- Bingung **kebutuhan/kegunaan** skripsi ini untuk apa.
- Tidak *relate* dengan keberadaan komentar spam judol di YouTube (video reguler,
  livestream, maupun Shorts) — merasa itu bukan masalah yang dia alami.
- Mengalihkan concern ke **iklan judi online**: banyak iklan judol yang visualnya berupa
  permainan, berbahaya kalau dibuka anak-anak. "Kenapa tidak blokir iklannya saja?"

Jawaban lisan mahasiswa saat sidang (sudah benar, tapi **belum ada di naskah**):
- Iklan tidak bisa diblokir karena pengiklan membayar dan YouTube hanya menyediakan slot.
- Memblokir iklan = masuk ranah adblock → berpotensi ilegal / melanggar ToS.

### Dosen 2 — dampak lanjutan & bukti keresahan

Inti keberatan:
- Paham tujuannya (menghilangkan spam promosi judol di komentar YouTube), tapi bingung
  **dampak lanjutannya apa**.
- Naskah mengklaim berguna bagi masyarakat, tapi **bagaimana masyarakat bisa memakainya**
  kalau ekstensi masih dipakai lokal (belum publish ke Chrome Web Store)?
- Mahasiswa menjawab: ada keresahan dari "masyarakat sekitar saya".
  Penguji balik bertanya: **masyarakat mana? ada bukti kuisionernya?**

Jawaban lisan mahasiswa: sistem dipakai untuk demo via localhost; mungkin perlu publish
ke Chrome Web Store sebagai bukti.

---

## Diagnosis (2026-08-23)

**Pola umum:** kedua catatan menyerang **BAB I**, bukan metode/hasil.
Tidak ada satupun penguji yang mempermasalahkan SVM, String Normalization, dataset,
atau angka evaluasi. Revisi ini bersifat **penulisan/justifikasi**, bukan penelitian ulang.

### Temuan A — Bab I tidak punya sub-bab Batasan Masalah

Struktur Bab I saat ini: 1.1 Latar Belakang, 1.2 Rumusan Masalah,
1.3 Tujuan dan Kegunaan, 1.4 Metode Penelitian. **Tidak ada Batasan Masalah / Ruang Lingkup.**

Ini akar pertanyaan Dosen 1. Pertanyaan "kenapa tidak iklannya saja?" adalah pertanyaan
*ruang lingkup*, dan naskah tidak punya tempat manapun yang menyatakan
"penelitian ini terbatas pada komentar, bukan iklan, karena ...".

### Temuan B — Latar belakang kuat secara teknis, lemah secara urgensi manusia

Hal cetak 1–3 langsung masuk ke obfuscation, homoglyph, kelemahan keyword filter.
Framing-nya "masalah teknis yang menarik", bukan "masalah sosial yang mendesak".
Klaim dampak sosial hanya satu kalimat umum tanpa angka:
> "...berpotensi besar menjerumuskan masyarakat ke dalam kejahatan finansial dan
> kecanduan perjudian." (hal cetak 1)

Tidak ada satupun **data kuantitatif** (jumlah takedown, nilai transaksi, jumlah pemain)
yang membuat pembaca merasa ini krisis nyata.

### Temuan C — Overclaim pada Kegunaan Praktis (hal cetak 5)

Naskah menulis:
> "Bagi Masyarakat Umum (Pengguna YouTube): Memberikan solusi perangkat lunak yang
> **dapat diinstal dan digunakan secara langsung** sebagai lapisan perlindungan tambahan
> secara mandiri."

Ini yang ditembak Dosen 2. Klaim "dapat diinstal dan digunakan langsung" tidak terpenuhi
selama ekstensi belum terdistribusi. Gap antara klaim dan realita = temuan yang sah.

### Temuan D — "keresahan masyarakat sekitar" adalah jawaban lisan, BUKAN klaim naskah

Penting: naskah **tidak pernah** mengklaim data lapangan/wawancara warga.
Urgensi di naskah bersumber dari sitasi (Herawati dkk., 2025). Jadi pertanyaan
"masyarakat mana? ada kuisioner?" muncul **karena jawaban lisan saat sidang**, bukan
karena isi tulisan.

**Konsekuensi:** tidak wajib bikin kuisioner. Yang perlu diperbaiki adalah konsistensi —
jangan mengklaim data primer yang tidak dikumpulkan. Ganti landasan urgensi ke data
sekunder yang bisa disitasi.

Menambah kuisioner untuk latar belakang = mengubah desain penelitian (butuh instrumen,
uji validitas/reliabilitas, populasi-sampel, Bab III berubah). **Tidak direkomendasikan**
kecuali penguji secara eksplisit mewajibkan.

### Temuan E — backend SUDAH production, naskah/jawaban lisan masih bilang "localhost"

Diverifikasi 2026-08-23:

```
$ curl https://api-svm.cupsky.my.id/health
HTTP 200 in 0.178s
{"status":"ok","model_loaded":true}
```

`extension/content.js:29` → `const API_BASE = "https://api-svm.cupsky.my.id";`
`extension/manifest.json` → host_permissions sudah ke domain produksi.
Folder `deploy/` berisi `judol-api.service` (systemd) + `nginx-judol-api.conf`.

Artinya sistem **sudah tidak localhost** sejak 8 Agustus — sebelum sidang.
Jawaban "ini cuma demo pakai localhost" saat sidang justru **merugikan diri sendiri**
dan tidak akurat. Ini poin kuat yang bisa dipakai saat menyerahkan revisi.

Yang tersisa untuk benar-benar "bisa dipakai masyarakat" hanyalah distribusi ekstensinya
(Chrome Web Store), karena backend-nya sudah publik dan hidup.

---

## Rencana revisi (draft — menunggu konfirmasi mahasiswa)

### Wajib (murni penulisan, risiko rendah)

| # | Aksi | Lokasi | Menjawab | Status |
|---|---|---|---|---|
| ~~R1~~ | ~~Tambah sub-bab **Batasan Masalah**~~ → **DIBATALKAN**, lihat catatan di bawah | — | — | ❌ Batal |
| R1′ | Batasan ruang lingkup ditulis sebagai **paragraf penutup Latar Belakang**, tanpa sub-bab baru | Bab I par. 9 | Dosen 1 | ✅ 23 Agt |
| R2 | Perkuat paragraf urgensi dengan **data kuantitatif tersitasi** (PPATK + Komdigi) | Bab I par. 2 & 3 | Dosen 1 & 2 | ✅ 23 Agt |
| R3 | Paragraf **mengapa komentar, bukan iklan** — tiga pertimbangan | Bab I par. 8 | Dosen 1 | ✅ 23 Agt |
| R4 | Revisi klaim Kegunaan Praktis: ganti "dapat diinstal dan digunakan secara langsung" jadi klaim yang jujur + tambahkan status distribusi | Bab I 1.3.2 | Dosen 2 | ✅ 23 Agt |
| R5 | Perjelas **rantai dampak** (spam tersaring → paparan promosi judol turun → risiko keterpaparan judi menurun), jangan berhenti di "nyaman" | Bab I 1.3.2 | Dosen 2 | ✅ 23 Agt |
| R6a | Cantumkan alamat produksi `https://api-svm.cupsky.my.id` di Bab IV | Bab IV komponen server | Dosen 2 | ✅ 25 Agt |
| R6b | Bukti submission Chrome Web Store + Gambar 4.16 di Kelayakan Operasional | Bab IV, Kelayakan Operasional | Dosen 2 | ✅ 26 Agt |
| R6c | Lengkapi butir kesimpulan kelayakan dengan status operasional | Bab V 5.1 butir 6 | Dosen 2 | ✅ 26 Agt |
| R7 | Nyatakan **keterbatasan penelitian** eksplisit + butir saran baru | Bab V 5.2 | Dosen 2 | ✅ 23 Agt |

### Rincian R4/R5/R7 (23 Agustus 2026)

**R4 + R5 — Bab I, Kegunaan Praktis bagi Masyarakat Umum.** Kalimat lama
*"Memberikan solusi perangkat lunak yang dapat diinstal dan digunakan secara langsung…"*
diganti seluruhnya. Versi baru: (a) menyebut peladen klasifikasi sudah dioperasikan publik
dan ekstensi **diajukan** untuk distribusi via Chrome Web Store — kata "diajukan" dipilih
agar tetap akurat baik saat status masih *pending review* maupun sudah *published*;
(b) menguraikan rantai dampak bertingkat: komentar tersaring → keterpaparan ajakan berjudi
menurun → peluang tergiring mencoba judi mengecil; (c) ditutup dengan data 103.100 anak-remaja
(PPATK, 2026b) dan fakta kolom komentar tidak punya pembatasan usia.

**R7 — Bab V, pembuka Saran.** Kalimat pengantar satu baris diganti jadi pernyataan
keterbatasan tiga poin: belum ada pengukuran penerimaan pengguna akhir lewat instrumen formal;
jangkauan pemakaian nyata belum terukur dalam rentang waktu penelitian; dataset statis sehingga
pola penyamaran baru belum teruji. **Tidak dibuat sub-bab 5.3** — pedoman menetapkan Bab V hanya
Kesimpulan dan Saran, dan "hal yang belum ditempuh" memang porsi Saran. Konsisten dengan
keputusan R1.

**R7b — butir Saran baru (nomor 7): "Pengujian Penerimaan Pengguna."** Menyarankan
*user acceptance testing* setelah ekstensi terdistribusi luas. Ini mengubah kritik Dosen 2
menjadi agenda penelitian lanjutan yang terdokumentasi — bukan kelemahan yang disembunyikan.

**Catatan untuk R6:** Kesimpulan (5.1) sengaja **tidak** disentuh. Pedoman melarang kesimpulan
yang tidak ada di pembahasan, jadi klaim soal deployment/distribusi harus masuk Bab IV dulu.
Kerjakan sekaligus saat R6b.

### Rincian R6a (25 Agustus 2026)

**Premis R6 versi awal ternyata keliru sebagian.** Hasil penyisiran naskah: kata "localhost"
maupun "127.0.0.1" **tidak pernah muncul sama sekali**. Naskah sejak awal sudah menyatakan
API di-deploy pada VPS (par. 630, 662, 704, 751, 922). Jadi yang perlu diperbaiki bukan
"localhost → produksi", melainkan dua hal lain:

1. **Alamat produksinya tidak pernah dituliskan.** Sudah diperbaiki — kalimat di komponen
   server kini berbunyi *"…dan dapat diakses secara publik melalui jaringan internet pada
   alamat https://api-svm.cupsky.my.id"*. Klaim "dapat diakses melalui internet" jadi bisa
   diverifikasi sendiri oleh penguji, bukan sekadar pernyataan.
2. **Bukti distribusi belum ada** — ini R6b, menunggu Item ID.

**Pemeriksaan konsistensi angka ambang.** Bab V par. 936 menyatakan *"default 75%"*.
Gambar 4.13 yang sudah terpasang di naskah diperiksa dan memang menampilkan **75%**, sesuai
dengan nilai bawaan di `content.js:38` (`0.75`). **Tidak ada ketidakcocokan.** Screenshot
Chrome Web Store yang baru menampilkan 50% karena preferensi tersimpan saat pengujian, tetapi
gambar-gambar itu **tidak masuk naskah**, jadi tidak menimbulkan konflik.

### Rincian R6b & R6c (26 Agustus 2026)

**Data submission Chrome Web Store — terverifikasi:**

| | |
|---|---|
| Nama | Judol Spam Detector |
| Versi | 1.0.0 |
| Item ID | `djggdnmjmnngdgpbngnpokkdfdigkilo` |
| URL toko (setelah terbit) | https://chromewebstore.google.com/detail/djggdnmjmnngdgpbngnpokkdfdigkilo |
| Dibuat | 23 Agustus 2026 |
| Diajukan | 25 Agustus 2026 |
| Status | Menunggu peninjauan |
| Akun penayang | `39d751d7-df2d-44e6-9202-4907bb28be5a` (bukan Item ID — jangan tertukar) |

Format Item ID Chrome adalah **32 huruf kecil a–p, tanpa angka dan tanpa tanda hubung**.
UUID yang mengandung angka dan tanda hubung adalah ID akun penayang, bukan ID ekstensi.
Keduanya muncul berurutan di URL devconsole.

**R6b** menyisipkan tiga paragraf di sub-bab Kelayakan Operasional, mengikuti pola gambar
yang sudah dipakai naskah: paragraf uraian yang kalimat terakhirnya merujuk gambar (sesuai
arahan pembimbing bahwa gambar harus didahului kalimat pengantar), paragraf rata tengah
berisi gambar selebar 14 cm sama seperti gambar lain, lalu caption. Caption disalin dari
caption Gambar 4.15 supaya **field SEQ ikut terbawa** — penomoran tetap otomatis dan entri
baru masuk ke Daftar Gambar.

**R6c** melengkapi butir kesimpulan tentang kelayakan. Sebelumnya butir itu hanya menyinggung
aspek hukum; kini aspek operasional ikut dinyatakan (peladen publik + pengajuan distribusi).
Baru boleh dilakukan **setelah** R6b, karena pedoman melarang kesimpulan yang tidak ada
dasarnya di pembahasan.

**Gambar 4.16** dibuat dari `reports/screenshots-store/thesis-ready/dashboard-submit.png`
lewat `build_thesis_figure.py`: alamat surel penayang diburamkan (sampul skripsi sudah memuat
identitas penulis, sementara skripsi terjilid bisa masuk repositori yang dibaca jauh lebih luas)
dan area kosong di bawah baris item dipotong (756 → 310 piksel).

**Verifikasi setelah R4/R5/R7:** Bab I tetap 4 sub-bab, Bab V tetap 2 sub-bab, seluruh sitasi
baru (PPATK 2026a/2026b, Komdigi 2025) punya entri daftar pustaka yang cocok.

> **Kenapa R1 dibatalkan.** Pedoman ([`PEDOMAN_RINGKAS.md`](../pedoman/PEDOMAN_RINGKAS.md) baris 163
> dan tabel baris 133) menetapkan Bab I skripsi hanya memuat **4 sub-bab**: Latar Belakang,
> Perumusan Masalah, Tujuan dan Kegunaan Hasil Penelitian, Metode Penelitian. "Batasan Sistem"
> secara eksplisit merupakan milik **proposal**, bukan skripsi. Menambah sub-bab kelima akan
> menyimpang dari pedoman. Isi batasannya tetap ditulis lengkap, hanya wadahnya diubah jadi
> paragraf. Diputuskan bersama mahasiswa, 23 Agustus 2026.

### Rincian yang sudah dikerjakan (23 Agustus 2026)

Backup: `2-RIWAYAT/backup/[DRAFT] 221232017 (BACKUP sebelum revisi sidang).docx`

Latar Belakang: **6 → 9 paragraf**. Struktur Bab I tetap 4 sub-bab (terverifikasi).

| Par. | Isi | Sumber angka |
|---|---|---|
| 2 (lama, diperluas) | Skala nasional: Rp286,84 T, 422,1 juta transaksi, 12,3 juta pemain (4,39% penduduk); 103.100 anak-remaja (36.400 <11 th; 66.700 11–16 th) | PPATK 2026a, 2026b |
| 3 (**baru**) | Komdigi blokir 2.087.109 konten judol; **43.475 dari Google/YouTube** — peringkat 2 medsos setelah Meta (92.322), di atas X (16.526) dan TikTok (1.166) | Komdigi 2025 |
| 8 (**baru**) | Tiga pertimbangan kenapa komentar, bukan iklan: (1) iklan berbayar & dikelola platform, memblokirnya = *ad blocking*, berisiko melanggar ToS; (2) iklan bisa dihindari & bertanda jelas, komentar tidak; (3) komentar = *user-generated content* tanpa kurasi | — |
| 9 (**baru**) | Batasan: hanya komentar berbahasa Indonesia di YouTube; bukan iklan, bukan konten video, bukan platform lain; hanya teks, bukan gambar/video/tautan | — |

Tiga entri daftar pustaka ditambahkan secara alfabetis dengan format *hanging indent* yang sama:
Kementerian Komunikasi dan Digital (2025) setelah Kaddoura; Pusat Pelaporan dan Analisis
Transaksi Keuangan (2026a) dan (2026b) setelah Pratama. Rentang tahun pustaka tetap 2018–2026,
jadi keterangan di Abstrak tidak perlu diubah.

**Belum dikerjakan mahasiswa:** buka di Word → `Ctrl+A` → `F9` → "Update entire table"
untuk memperbarui nomor halaman Daftar Isi.

### Opsional (butuh keputusan mahasiswa)

| # | Aksi | Effort | Catatan |
|---|---|---|---|
| O1 | **Publish ke Chrome Web Store** | biaya USD 5 sekali, review beberapa hari–minggu | Sangat layak karena backend sudah live. Bukti paling telak untuk Dosen 2. Risiko: waktu review tidak bisa dikontrol vs deadline revisi. |
| O2 | **UAT / kuisioner kepuasan pengguna** (10–30 responden pakai ekstensi lalu isi kuisioner singkat) | 1–2 minggu | Masuk sebagai *pengujian penerimaan* di Bab IV, BUKAN sebagai dasar latar belakang. Tidak mengubah desain penelitian. Menjawab "dampak lanjutan" + "masyarakat mana" sekaligus. |
| O3 | Kuisioner keresahan masyarakat untuk latar belakang | tinggi | **Tidak disarankan** — mengubah desain penelitian pasca-sidang. Hanya lakukan bila diwajibkan tertulis. |

---

## Hal yang masih perlu dikonfirmasi

1. Ada **lembar revisi resmi** yang harus ditandatangani penguji? Kalau ada, isinya harus
   jadi sumber kebenaran, menggantikan catatan lisan di dokumen ini.
2. **Deadline** revisi.
3. Keputusan atas O1 (publish store) dan O2 (UAT).
4. Apakah ada penguji ke-3 / catatan dari pembimbing yang belum tercatat.
