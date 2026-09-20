# Scraper

Pengumpul komentar YouTube yang menghasilkan bahan mentah dataset. Ditulis
dengan Node.js karena tugasnya murni memanggil REST API dan mengolah JSON.

Dua berkas:

| Berkas | Peran |
|---|---|
| [`scraper/index.js`](../scraper/index.js) | Ambil komentar satu video, beri skor heuristik, simpan per kategori |
| [`scraper/filter.js`](../scraper/filter.js) | Gabungkan hasil banyak video jadi berkas agregat, sekalian de-duplikasi |

## Menyiapkan

```bash
cd scraper
npm install
cp .env.example .env
```

Isi `.env` dengan kunci YouTube Data API v3:

| Variabel | Wajib | Bawaan | Keterangan |
|---|---|---|---|
| `YOUTUBE_API_KEY` | ya | — | Kunci API YouTube Data v3 |
| `TARGET_COUNT` | tidak | 100 | Jumlah komentar minimum yang dikumpulkan sebelum berhenti |

## Menjalankan

```bash
node index.js <video_id> [run_mode] [data_mode]
```

| Argumen | Posisi | Wajib | Nilai |
|---|---|---|---|
| `video_id` | ke-1 | ya | ID video YouTube |
| `run_mode` | ke-2 | tidak | `video` (bawaan) atau `live` |
| `data_mode` | ke-3 | tidak | `spam` (bawaan) atau `non_spam` |

```bash
node index.js z-BTQKhWrJc                    # spam dari komentar video
node index.js z-BTQKhWrJc video non_spam     # non-spam dari komentar video
node index.js z-BTQKhWrJc live spam          # spam dari live chat
```

Setelah beberapa video terkumpul, gabungkan hasilnya:

```bash
node filter.js
```

Keluarannya `final_spam.json`, `final_non_spam.json`, dan bila ada,
`final_borderline.json`. Ketiganya sudah dide-duplikasi. Dua yang pertama
inilah yang dibaca [`src/prepare_dataset.py`](../src/prepare_dataset.py).

## Pemberian skor

Setiap komentar diberi skor 0 sampai 100, lalu dikelompokkan ke salah satu
dari tiga kategori.

| Kategori | Kriteria | Disimpan ke |
|---|---|---|
| `spam` | skor minimal 30 **dan** ada minimal satu sinyal primer | `spam_*.json` |
| `non_spam` | skor di bawah 10 **dan** tidak ada sinyal primer | `non_spam_*.json` |
| `borderline` | skor 10 sampai 29 | `borderline_*.json` |

Syarat "harus ada sinyal primer" itu penting. Tanpanya, komentar seperti
`MANTAP BANGET!!!! 🔥🔥🔥` bisa lolos sebagai spam hanya karena kombinasi
kapital dan emoji.

Skor ini hanya penyaring awal, bukan label akhir. Pelabelan sebenarnya terjadi
di `prepare_dataset.py` ditambah koreksi manual, lihat [dataset.md](dataset.md).

### Bobot sinyal

Primer:

| Sinyal | Bobot | Contoh |
|---|---|---|
| Pola nama situs judi | +40 | `SLOT88`, `MAXWIN777`, `BET138` |
| Tautan atau nomor kontak | +40 | `wa.me/628xxx`, `bit.ly/xxx`, `cek profil` |

Sekunder:

| Sinyal | Bobot | Contoh |
|---|---|---|
| Kata kunci yang disamarkan | +30 | `g a c o r`, `m@xw!n`, `z3u5` |
| Kata kunci polos | +20 | `slot`, `depo`, `scatter`, `mahjong` |
| Rasio simbol di atas 15% | +20 | `★彡[ S̤̈L̤̈Ö̤T̤̈ ]彡★` |

Tersier:

| Sinyal | Bobot | Contoh |
|---|---|---|
| Emoji berjejer, minimal dua | +15 | `🔥🎰💰` |
| Kapital lebih dari 50% | +10 | `DAFTAR SEKARANG GRATIS` |

### Normalisasi sebelum penilaian

Teks dinormalisasi lebih dulu supaya penyamaran tidak lolos dari pemeriksaan
regex:

```
𝗦𝗟𝗢𝗧 𝗚𝗔𝗖𝗢𝗥  ->  SLOT GACOR
Ｇａｃｏｒ       ->  Gacor
```

Selain NFKC, `applyHomoglyphMap()` dan `normalizeLeetSpeak()` dijalankan
**sebelum** sinyal regex diperiksa. Urutan ini bukan detail sepele: sebelum
perbaikan 3 Juli 2026, pemeriksaan berjalan di atas teks mentah, dan 61
komentar spam yang menyamar dengan Unicode dekoratif serta leet speak lolos
masuk dataset sebagai non-spam. Lihat
[dataset.md](dataset.md#insiden-kontaminasi-data).

## Kenapa ada kategori borderline

Sebelum 3 Juli 2026, komentar berskor 10 sampai 29 dibuang begitu saja, tanpa
jejak. Rentang ini konsekuensi dari desain dua ambang: terlalu mencurigakan
untuk dianggap non-spam, tapi buktinya belum cukup untuk dilabeli spam.

Masalahnya baru terlihat ketika ditemukan satu komentar spam yang lolos
deteksi model, dan ternyata komentar itu tidak pernah masuk kumpulan data sama
sekali. Nama situs `PBB4D`, yang berupa kapital diikuti digit, memicu pola
nama situs dan mendorong skornya ke zona 10 sampai 29, sehingga dibuang.

Penelusuran lanjutan dengan ambang yang sementara dilebarkan justru menemukan
sesuatu yang lebih berharga: zona itu **mayoritas berisi komentar non-spam
asli**, yaitu cerita dan opini panjang soal judi online yang terganjal semata
karena menyebut `judol`, `slot`, atau `wd` berkali-kali. Itu justru jenis
contoh yang paling dibutuhkan model untuk belajar membedakan kritik dari
promosi.

Sejak `isBorderlineComment()` ditambahkan, komentar zona ini disimpan terpisah
untuk ditinjau manual. Kategori ini sengaja tidak langsung dipakai melatih
model, karena labelnya memang belum tentu benar. Peninjauan manualnya belum
dikerjakan dan tercatat di [roadmap.md](roadmap.md).

## Struktur keluaran

```
scraper/result/
├── scrape_history.json
├── spam_video_<id>_<timestamp>.json
├── non_spam_video_<id>_<timestamp>.json
└── borderline_video_<id>_<timestamp>.json
```

Prefix berkas menentukan kelompok mana yang dipakai `filter.js`. Timestamp
memastikan setiap kali dijalankan hasilnya berkas baru, bukan menimpa yang
lama. `scrape_history.json` mencatat video yang pernah diambil.

Isi `result/` tidak ikut diversikan. Yang masuk repositori hanya hasil
agregatnya, yaitu `final_spam.json` dan `final_non_spam.json`.

Data yang disimpan terbatas pada ID video, waktu pengambilan, dan teks
komentar. Nama pengguna dan ID kanal tidak ikut disimpan.
