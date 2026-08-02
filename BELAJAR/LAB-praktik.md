# LAB — Sesi Praktik

> Terpisah dari bacaan. Ambil kapan saja kamu punya waktu luang panjang.

Tiga sesi, berdiri sendiri-sendiri. Tidak harus berurutan, tapi kalau waktumu cuma cukup untuk satu, **pilih Sesi 2** — itu yang paling berpengaruh untuk sidang.

| Sesi | Isi | Waktu | Manfaat |
|---|---|---|---|
| 1 | Buktikan normalisasi bekerja | ~30 menit | Paling mudah, hasilnya paling meyakinkan |
| 2 | Verifikasi seluruh angka skripsi | ~15 menit | **Paling penting** — angka jadi benar-benar milikmu |
| 3 | Jalankan sistem utuh sampai demo | ~1 jam | Latihan demo sidang |

---

# SESI 1 — Buktikan normalisasi bekerja

⏱️ ~30 menit · Tanpa persiapan khusus

## Kenapa sesi ini penting

Judul skripsimu memuat "String Normalization". Sesi ini membuktikan bagian itu **benar-benar bekerja**, dan hasilnya bisa langsung kamu tunjukkan saat sidang.

## Langkah

```bash
cd c:\Personal\kulyeah\Skripsi\svm-judol-spam
python src/preprocessing.py
```

Berkas ini punya 10 kasus uji bawaan. Keluarannya menampilkan teks asli dan hasil pembersihannya.

## Yang perlu kamu amati

Perhatikan beberapa pasangan ini:

**① Font Unicode dekoratif**
```
INPUT  : 𝑅𝒪𝑀𝒜𝟦𝒟 daftar sekarang bonus gede!
OUTPUT : judolbrand daftar sekarang bonus gede
```
Perhatikan `𝑅𝒪𝑀𝒜𝟦𝒟` berubah jadi `judolbrand`. Dua hal terjadi berurutan: NFKC mengembalikan huruf dekoratif ke ASCII (`ROMA4D`), lalu pola brand mengubahnya jadi token universal.

**② Homoglyph Cyrillic**
```
INPUT  : dаftаr sekаrаng dаpаt bоnus 100%
```
Huruf `а` di situ **bukan** huruf a Latin — itu Cyrillic. Perhatikan hasilnya tetap terbaca `daftar sekarang`.

**③ Tanda diakritik**
```
INPUT  : Bukan ngebet, tapi nyaman di P̲̲U̲̲L̲̲A̲̲U̲̲W̲̲I̲̲N̲̲?
```
Tanpa penanganan khusus, tiap huruf akan terpisah dan terbuang semua. Perhatikan `PULAUWIN` bertahan utuh.

**④ Emoji**
```
INPUT  : 🎰💰 slot gacor hari ini, WD cepat, daftar gratis 🎁🔥
```
Perhatikan emoji tidak dibuang, melainkan berubah jadi kata seperti `slot_machine` dan `money_bag` — jadi tetap menyumbang sinyal.

## Latihan tambahan

Buka `src/preprocessing.py`, cari daftar `test_cases` di baris 334, lalu **tambahkan contohmu sendiri**. Coba tulis nama situs judi karangan dengan gaya penyamaran, misalnya:

```python
"main di K3JU4D dijamin gacor",
"ayo gabung [B][E][T][A][W][I][7][7]",
```

Jalankan lagi, lihat hasilnya. Kalau ada yang **tidak** tertangkap, itu justru temuan bagus — kamu jadi tahu batas kemampuan sistemmu, dan itu bahan jawaban yang jujur kalau ditanya keterbatasan.

## Setelah sesi ini kamu bisa menjawab

- "Coba tunjukkan bagaimana sistem menangani teks yang disamarkan"
- "Apa yang terjadi kalau spammer memakai huruf Cyrillic?"
- "Kenapa emoji tidak dibuang saja?"

💡 **Untuk sidang:** siapkan terminal dengan perintah ini sudah siap ketik. Kalau penguji bertanya soal normalisasi, kamu bisa menjalankannya langsung. Jauh lebih meyakinkan daripada menjelaskan lisan.

---

# SESI 2 — Verifikasi seluruh angka skripsi ⭐

⏱️ ~15 menit (5 menit siap, 5–8 menit menunggu)

## Kenapa sesi ini yang paling penting

Setelah sesi ini, kamu tidak lagi **mengutip** angka dari skripsi. Kamu **sudah menghitungnya sendiri**. Perbedaan itu terasa saat menjawab penguji — nadanya beda antara orang yang menyalin dan orang yang tahu.

## Langkah

```bash
cd c:\Personal\kulyeah\Skripsi\svm-judol-spam
python BELAJAR/verifikasi_angka.py
```

Skrip ini menghitung ulang **semuanya dari nol** — memuat CSV, membersihkan teks, melatih model, mengevaluasi — lalu membandingkan tiap hasil dengan angka yang tertulis di skripsimu.

Skrip ini **tidak mengubah apa pun**. Hanya membaca dan mencetak.

## Yang akan kamu lihat

```
[5/6] HASIL MODEL SVM
  [COCOK  ] Akurasi                            hitung=0.9753    skripsi=0.9753
  [COCOK  ] F1-macro                           hitung=0.9726    skripsi=0.9726
  [COCOK  ] TN (non-spam benar)                hitung=863       skripsi=863
  ...
       Rumus yang baru saja dihitung:
         Akurasi  = (442 + 863) / 1338 = 0.97534
         Presisi  = 442 / (442 + 9) = 0.98004
```

Di akhir muncul ringkasan: berapa angka yang cocok dari total.

## Kalau ada yang bertanda BEDA

Kemungkinan besar `data/comments.csv` sudah berubah sejak angka di skripsi dihitung. **Kalau itu terjadi, beri tahu — angka di skripsi perlu diperbarui sebelum sidang.** Jangan dibiarkan.

## Latihan berpikir

Sambil menunggu skripnya jalan, coba jawab tanpa melihat catatan:

1. Kenapa `random_state=42` membuat hasilnya bisa sama persis tiap dijalankan?
2. Kenapa cross-validation memakai seluruh data, tapi pencarian nilai C hanya memakai data latih?
3. Kalau `stratify=y` dihapus, apa yang bisa terjadi?

Jawabannya ada di `01-kamus-ml.md` dan `03-angka-ke-kode.md`.

## Setelah sesi ini kamu bisa menjawab

- "Angka 97,53% ini dari mana?" — dengan percaya diri, karena baru saja menghitungnya
- "Apakah hasilnya bisa direproduksi?" — ya, dan kamu sudah membuktikannya
- "Coba jelaskan rumus akurasinya" — sudah tercetak di layar saat verifikasi

---

# SESI 3 — Jalankan sistem utuh

⏱️ ~1 jam · Ini gladi bersih demo sidang

## Langkah 1 — Nyalakan server

```bash
cd c:\Personal\kulyeah\Skripsi\svm-judol-spam
python src/server.py
```

Tunggu sampai muncul keterangan server berjalan di `http://localhost:8000`.

**Biarkan terminal ini terbuka.** Server harus tetap hidup selama demo.

## Langkah 2 — Uji server tanpa ekstensi

Buka peramban ke:
```
http://localhost:8000/docs
```

Ini halaman dokumentasi interaktif bawaan FastAPI. Kamu bisa mencoba tiap endpoint langsung dari sini.

Coba `POST /predict`, klik **Try it out**, lalu isi:
```json
{"text": "daftar sekarang di ROMA4D bonus gacor"}
```

Perhatikan responsnya: label, tingkat keyakinan, dan status spam.

Lalu coba dengan komentar normal:
```json
{"text": "video ini sangat membantu, terima kasih kak"}
```

💡 **Halaman `/docs` ini kartu as untuk sidang.** Kalau demo ekstensi bermasalah karena YouTube atau jaringan, kamu masih bisa menunjukkan sistemnya bekerja lewat halaman ini. Siapkan tab-nya sebelum sidang dimulai.

## Langkah 3 — Pasang ekstensi

1. Buka Chrome → `chrome://extensions`
2. Nyalakan **Developer mode** (sakelar di pojok kanan atas)
3. Klik **Load unpacked**
4. Pilih folder `svm-judol-spam/extension`

Ekstensi muncul di daftar. Sematkan ikonnya di bilah alamat supaya mudah diakses.

## Langkah 4 — Coba di YouTube

Buka video YouTube Indonesia yang kolom komentarnya ramai spam judol. Gulir ke bagian komentar.

Klik ikon ekstensi untuk membuka panel. Yang bisa kamu coba:
- Ganti mode **Redupkan** ↔ **Hilangkan**
- Geser ambang batas, lihat perubahan jumlah komentar yang tersembunyi
- Klik badge persentase pada komentar yang diredupkan untuk memunculkannya kembali
- Perhatikan panel statistik: berapa dipindai, berapa disembunyikan

## Latihan demo

Latih alur ini **sampai lancar tanpa berpikir**, targetnya 3–4 menit:

1. Tunjukkan panel ekstensi, jelaskan singkat tiap bagiannya
2. Gulir ke komentar, tunjukkan spam yang otomatis diredupkan
3. Klik satu badge, tunjukkan komentar aslinya beserta persentase keyakinan
4. Ganti ke mode Hilangkan, tunjukkan bedanya
5. Geser ambang batas ke 50%, tunjukkan lebih banyak yang tersaring
6. Kembalikan ke 75%

Ucapkan penjelasannya dengan suara keras sambil memperagakan. Berbeda rasanya antara membayangkan dan benar-benar mengucapkan.

## Daftar periksa sebelum sidang

- [ ] Server bisa menyala tanpa galat
- [ ] `http://localhost:8000/docs` terbuka dan endpoint-nya berfungsi
- [ ] Ekstensi terpasang dan ikonnya tersemat
- [ ] Sudah menyiapkan **video cadangan** yang komentarnya pasti ada spam
- [ ] Sudah tahu apa yang dikatakan kalau server mati mendadak
- [ ] Sudah merekam video demo sebagai cadangan terakhir

## Kalau demo gagal saat sidang

Ini bisa terjadi dan bukan akhir dunia. Urutan penyelamatan:

1. **Cek server masih hidup** — buka `/health` di tab lain
2. **Kalau server mati** — nyalakan ulang sambil menjelaskan arsitekturnya
3. **Kalau YouTube tidak kooperatif** — beralih ke `/docs`, tunjukkan klasifikasinya langsung
4. **Kalau semuanya gagal** — pakai slide tangkapan layar (slide 27–28 di PPT-mu), dan jelaskan alurnya

Yang dinilai penguji adalah **pemahamanmu**, bukan kelancaran jaringan. Tetap tenang, jelaskan apa yang seharusnya terjadi, lalu lanjutkan.

---

# Kalau cuma sempat satu jam

Prioritaskan:

1. **Sesi 2** (15 menit) — verifikasi angka. Paling berpengaruh.
2. **Sesi 1** (15 menit versi cepat) — jalankan `preprocessing.py`, amati keluarannya.
3. **Sesi 3 langkah 1–2** (30 menit) — pastikan server menyala dan `/docs` berfungsi.

Tiga itu sudah menutup sebagian besar risiko teknis saat sidang.
