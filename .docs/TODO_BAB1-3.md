# To-Do Revisi BAB I - III

Dibuat 2026-07-09 berdasarkan cross-check antara draft skripsi (`[DRAFT] 221232017.pdf`), pedoman resmi (`PEDOMAN_SKRIPSI_TEKNIK_INFORMATIKA.pdf`), analisa DeepSeek (`deepseek_markdown_20260708_664b8b.md`), dan kondisi kode aktual di repo.

## BAB I

- [x] 1. Gabungkan **Tujuan Penelitian (1.3.1)** jadi 1 paragraf naratif — saat ini masih list bernomor 1/2/3. Revisi dosen poin 1. Contoh kalimat siap pakai ada di `deepseek_markdown_20260708_664b8b.md` bagian 6.
- [x] 2. Perbaiki **Daftar Isi** — ada teks literal `Error! Bookmark not defined.` di baris BAB II dan BAB III. Fix: klik kanan di Daftar Isi (Word) → *Update Field* → *Update entire table*.

## BAB II

### Struktur final setelah restrukturisasi (3p/3q/3r) — pakai peta ini sebagai acuan nomor

Karena satu section top-level dibuang (N-gram lama gabung ke 2.5.1) dan satu section top-level ditambah (Evaluasi Model naik jadi 2.8), nomor 2.9 sampai 2.18 **tidak berubah**. Yang berubah cuma di dalam 2.5-2.8:

```
2.5 TF-IDF
  2.5.1 N-gram                                     ← pindahan dari 2.8 lama
2.6 SVM
  2.6.1 Estimasi Probabilitas SVM (Platt Scaling)  ← BARU
2.7 Algoritma Pembanding
  2.7.1 Naive Bayes
  2.7.2 Logistic Regression
2.8 Evaluasi Model Klasifikasi                     ← pindahan dari 2.6.1 lama
2.9 Metode Waterfall                               ← nomor tetap sama
2.10 - 2.18                                        ← semua tetap sama
```

- [ ] 3p. **Pindahin Evaluasi Model Klasifikasi** dari 2.6.1 (anak SVM) jadi **2.8** (top-level, setelah Algoritma Pembanding) — isinya metrik universal (confusion matrix, accuracy/precision/recall/F1) yang dipakai buat menilai SVM, Naive Bayes, DAN Logistic Regression sekaligus, jadi janggal kalau nempel di bawah SVM doang.
- [ ] 3q. **Gabungin N-gram** dari 2.8 lama jadi **2.5.1** (anak TF-IDF) — N-gram itu parameter dari TF-IDF (`ngram_range`), bukan topik berdiri sendiri.
- [ ] 3r. **Tambah sub-bab baru 2.6.1: Estimasi Probabilitas pada SVM (Platt Scaling)** — sistem pakai *confidence threshold* (default 0,75) sebagai fitur inti (popup, badge, mode Redupkan/Hilangkan), tapi BAB 2.6 SVM cuma jelasin hyperplane & margin, nggak pernah jelasin dari mana angka confidence/probability berasal. Wajib ada karena bakal ditanya pas sidang ("confidence 0.75 itu dari mana asalnya secara matematis?").

### Kesimpulan tiap sub-bab teori (dosen poin 4)

Tambahkan kalimat kesimpulan di akhir tiap sub-bab (variasikan pembukanya, jangan semua "Berdasarkan uraian di atas..." — draft kalimat sudah ada di riwayat chat, tinggal disalin ke Word). Yang **sudah ada** kesimpulan (skip): 2.6 SVM, 2.12 Spam Komentar, 2.13 Chrome Extension, 2.17 Studi Terdahulu.
  - [x] 3a. 2.1 Natural Language Processing — SUDAH DISISIPKAN
  - [x] 3b. 2.2 Text Preprocessing — SUDAH DISISIPKAN
  - [x] 3c. 2.3 Stemming Sastrawi — SUDAH DISISIPKAN
  - [x] 3d. 2.4 String Normalization (versi ringkas/konseptual) — SUDAH DISISIPKAN
  - [x] 3e. 2.5 TF-IDF (termasuk perbaikan "Bab 3" → "Bab 4") — SUDAH DISISIPKAN
  - [x] 3e-i. 2.5.1 N-gram (kalimat penutup) — SUDAH DISISIPKAN
  - [x] 3r-i. 2.6.1 Estimasi Probabilitas SVM (Platt Scaling) — SUDAH DITULIS (terverifikasi valid vs train.py: SVC probability=True → Platt scaling)
  - [x] 3f. 2.8 Evaluasi Model Klasifikasi (nomor baru) — SUDAH DISISIPKAN
  - [x] 3g. 2.7.1 Naive Bayes — SUDAH DISISIPKAN
  - [x] 3h. 2.7.2 Logistic Regression — SUDAH DISISIPKAN
  - [x] 3j. 2.9 Metode Waterfall — SUDAH DISISIPKAN
  - [x] 3k. 2.10 Perbandingan ML vs DL — SUDAH DISISIPKAN
  - [x] 3l. 2.11 Web Scraping & Analisis Heuristik — SUDAH DISISIPKAN
  - [x] 3m. 2.14 REST API & FastAPI — SUDAH DISISIPKAN
  - [x] 3n. 2.15 UML (+ subbab 2.15.1-2.15.3) — SUDAH DISISIPKAN (kesimpulan dikonsolidasi jadi 1 di akhir 2.15, bukan per-subbab)
  - [x] 3o. 2.16 PIECES — SUDAH DISISIPKAN

  > Semua di atas sudah ada di `.docs/BAB_2_FULL.md`. Yang masih perlu dikerjakan manual: (a) copas ke Word, (b) italic istilah asing (poin 9), (c) bangun ulang rumus di Equation Editor, (d) pindahkan detail implementasi String Normalization ke BAB IV (poin 4c).

- [ ] 4. Lengkapi **BAB 2.4 (String Normalization)** — versi KONSEPTUAL saja (kategori umum obfuscation: homoglyph substitution, combining diacritics, character separation, leet speak, canonicalization), draft sudah ada di chat. **JANGAN** taruh detail implementasi (regex, kategori Unicode "Mn", contoh kode `keju4d`→`judolbrand`) di sini — itu levelnya BAB IV, bukan Landasan Teori.
  - [ ] 4b. Sekalian jelasin **Unicode Normalization Form (NFKC)** secara konseptual di 2.4 — istilah ini dipakai di BAB III (tabel PIECES) dan BAB IV tapi belum pernah dijelasin teorinya di BAB II manapun.
  - [ ] 4c. Pindahkan detail implementasi (diacritics-stripping, bracket-unwrapping, leet speak, brand canonicalization dengan contoh kode nyata dari `preprocessing.py`) ke **BAB IV** (4.4.1 Training Pipeline atau tambahan sub-bab baru di 4.5.x Perancangan Model) — bukan ke BAB II.

## BAB III

- [x] 5. **JANGAN ganti judul BAB III** ("OBJEK PENELITIAN") tanpa konfirmasi dosen — struktur saat ini sudah sesuai contoh resmi lampiran pedoman (L-10/11). Tapi tetap tanyakan langsung ke dosen kata-kata persis yang dia maksud saat bilang "salah", karena instruksi verbal dosen menang di atas pedoman tertulis.
> Draft lengkap BAB III sudah ada di `.docs/BAB_3_FULL.md`.

- [x] 6. Kalimat pengantar sebelum flowchart sistem berjalan — SUDAH DITULIS. ⚠️ Nomor gambar berubah jadi **Gambar 3.2** (karena bagan struktur organisasi baru jadi Gambar 3.1).
- [x] 7. Kalimat pengantar sebelum Tabel 3.1 (Ringkasan PIECES) — SUDAH DITULIS.
- [x] 8. Struktur organisasi YouTube — SUDAH DITULIS sebagai 3.1.3 (Profil Perusahaan) + 3.1.4 (Struktur Organisasi, dianchor ke divisi Trust & Safety). Dosen minta YouTube diperlakukan sebagai perusahaan.
  - [ ] ⚠️ VERIFIKASI semua fakta perusahaan bertanda `[VERIFIKASI]` (tahun berdiri, nilai akuisisi, CEO saat ini) + kasih sitasi sebelum final.
  - [ ] Gambar bagan struktur organisasi (hitam-putih) belum dibuat — panduan pohonnya ada di file.
  - [ ] Update Daftar Gambar & referensi silang karena penomoran gambar BAB III bergeser (org chart = 3.1, flowchart = 3.2).
  - [ ] Opsional: kalau dosen mau, pisahkan "Wewenang dan Tanggung Jawab" jadi sub-bab sendiri (sekarang digabung ke deskripsi divisi). Urutan 3.1.3/3.1.4 juga bisa dipindah ke depan kalau dosen mau profil perusahaan tampil duluan.

## Berlaku ke semua bab (I-III) — perlu cek manual, tidak bisa diverifikasi otomatis

- [ ] 9. **Italic untuk istilah asing** — ekstraksi teks PDF menghilangkan info font style, jadi tidak bisa dicek otomatis. Cek manual tiap istilah seperti *Machine Learning*, *Support Vector Machine*, *Chrome Extension*, *FastAPI*, *DOM*, *REST API*, dll — pastikan semua miring (dosen poin 2).
- [ ] 10. **Warna diagram** — kalau Gambar 3.1 berwarna, ubah ke hitam-putih/grayscale (dosen poin 10).
