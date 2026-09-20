# Dataset

Dataset akhir berisi **6.690 komentar** berbahasa Indonesia: 2.332 spam dan
4.358 non-spam. Tersimpan di `data/comments.csv` dengan tiga kolom.

| Kolom | Isi |
|---|---|
| `text` | Teks komentar apa adanya, belum dinormalisasi |
| `label` | `spam` atau `non_spam` |
| `source` | ID video YouTube asalnya, atau `manual_override` jika labelnya dikoreksi manual |

Kolom `source` ada supaya setiap baris bisa ditelusuri kembali ke asalnya.

Ketimpangan antara kedua kelas disengaja dan tidak diratakan. Di kolom
komentar, spam memang minoritas, dan meratakannya secara artifisial akan
membuat evaluasi kurang mencerminkan keadaan sebenarnya. Penanganannya
dilakukan di sisi model lewat `class_weight="balanced"` dan pemilihan F1-macro
sebagai metrik utama.

## Pengumpulan data

Data diambil lewat **YouTube Data API v3**, bukan dengan mengikis HTML.

| Aspek | API resmi | Mengikis HTML |
|---|---|---|
| Ketentuan layanan | Sesuai | Berpotensi melanggar |
| Stabilitas | Terjaga oleh kontrak API | Rusak setiap kali tampilan berubah |
| Format | JSON terstruktur | Perlu penguraian yang rapuh |
| Batasan | Kuota terdokumentasi | Berisiko diblokir |

[`scraper/index.js`](../scraper/index.js) memanggil endpoint `commentThreads`,
lalu memberi setiap komentar `spam_score` 0 sampai 100 berdasarkan sinyal
heuristik seperti kemunculan pola nama situs, tautan kontak, dan kata kunci
yang disamarkan. Skor ini hanya penyaring awal, bukan label akhir.

Keluaran mentah per video tersimpan di `scraper/result/` dan tidak ikut
diversikan. Tahap agregasi yang menggabungkannya menjadi
`scraper/final_spam.json` dan `scraper/final_non_spam.json` dikerjakan oleh
repositori scraper terpisah.

Data yang disimpan hanya ID video, waktu pengambilan, dan teks komentar. Nama
pengguna, ID kanal, dan identitas pengomentar lainnya tidak ikut disimpan.

## Penyaringan dua tahap

[`src/prepare_dataset.py`](../src/prepare_dataset.py) mengubah keluaran scraper
menjadi dataset berlabel. Penyaringannya berjalan dua tahap, bukan satu ambang
tunggal.

**Tahap pertama** mengambil entri dengan `spam_score` minimal 80. Hasilnya
hanya sekitar 138 entri, terlalu sedikit untuk melatih model.

**Tahap kedua** meninjau ulang entri berskor rendah yang mengandung sinyal
pola nama situs. Jika teks yang sudah dinormalisasi mengandung pola nama situs
judi yang jelas, misalnya huruf kapital diikuti angka seperti `WIFI4D`, atau
akhiran khas seperti `TOTO`, `BET`, `WIN`, dan `QQ`, entri itu diambil sebagai
spam. Tahap ini menyelamatkan 1.947 entri.

Sisanya, 239 entri, dibuang karena skornya rendah dan tidak cocok pola apa pun.

## Koreksi manual

`data/manual_overrides.csv` berisi koreksi label yang diterapkan di setiap
rebuild. Berkas ini yang membuat koreksi bertahan, karena `comments.csv`
ditulis ulang setiap kali `prepare_dataset.py` dijalankan.

Koreksi diperlukan karena heuristik scraper tidak sempurna di kedua arah.
Komentar yang mengkritik judi online sering memuat nama situs dan kata kunci
yang sama dengan komentar promosi, sehingga mudah ter-flag keliru. Sebaliknya,
sebagian spam berhasil lolos karena penyamarannya belum dikenali.

## Insiden kontaminasi data

Selama pengumpulan data ditemukan 61 komentar spam yang salah masuk sebagai
non-spam. Ketiganya berasal dari kampanye yang menyamarkan tulisan dengan
Unicode dekoratif dan leet speak, sehingga lolos pemeriksaan regex scraper
yang saat itu berjalan pada teks mentah.

Penanganannya dilakukan di dua tempat:

1. Entri yang terlanjur salah **dilabeli ulang menjadi spam**, bukan dibuang.
   Membuangnya akan menghilangkan contoh penyamaran yang justru berharga.
2. Penyebabnya diperbaiki di scraper, dengan menjalankan pemetaan homoglif dan
   normalisasi leet speak **sebelum** sinyal regex diperiksa, supaya
   penyamaran serupa tidak lolos lagi.

Akurasi sempat turun setelah perbaikan ini. Penurunan tersebut disengaja:
model sebelumnya sebagian menghafal label yang salah, sehingga angkanya
terinflasi. Rinciannya ada di [riwayat-dataset.md](riwayat-dataset.md).

## Kumpulan kasus ambigu

`data/hard_test_set.csv` berisi 135 komentar yang sengaja dipilih karena sulit.
Sebagian besar adalah komentar yang **menyebut nama situs judi tetapi bukan
promosi**, misalnya laporan penipuan, keluhan korban, atau permintaan
pemblokiran.

| Kolom | Isi |
|---|---|
| `text` | Teks komentar |
| `label` | Label sebenarnya |
| `source_video` | Video asalnya |
| `note` | Alasan kasus ini dianggap sulit |

Kumpulan ini tidak ikut dilatih dan dipakai sebagai pengujian terpisah. Lihat
[evaluasi.md](evaluasi.md#pengujian-pada-kasus-ambigu).

## Zona abai scraper

Komentar dengan skor 10 sampai 29 semula dibuang tanpa jejak. Rentang ini
ternyata berisi banyak komentar non-spam bertema judi, yaitu justru jenis
contoh yang paling dibutuhkan model untuk belajar membedakan kritik dari
promosi.

Scraper kini menyimpan rentang tersebut ke berkas terpisah untuk ditinjau.
Peninjauan manualnya belum dikerjakan dan tercatat di
[roadmap.md](roadmap.md).
