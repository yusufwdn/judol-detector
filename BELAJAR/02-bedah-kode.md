# 02 — Bedah Kode

> Berkas per berkas: apa isinya, kenapa ada, dan keputusan pentingnya di baris berapa.

Dibaca terbagi tiga hari:
- **Hari 2** — Bagian A (data): scraper → pelabelan → prapemrosesan
- **Hari 3** — Bagian B (model): pelatihan
- **Hari 5** — Bagian C (sistem): server → ekstensi

Semua nomor baris diverifikasi pada 1 Agustus 2026. Kalau nanti kodenya berubah, nomornya bisa bergeser — tapi nama fungsinya tetap.

---

# BAGIAN A — Data

## A1. `scraper/index.js` (550 baris)

🎯 **Perannya:** mengambil komentar dari YouTube dan memberi skor awal seberapa mirip spam.

📄 **Di skripsi:** Sub-bab 1.4.2 dan 4.3

### Yang dilakukan

1. Memanggil YouTube Data API v3 untuk mengambil komentar dari daftar video.
2. Menormalkan teksnya untuk keperluan penilaian.
3. Memberi **skor heuristik** berdasarkan sinyal-sinyal kecurigaan.
4. Menyimpan hasilnya ke `final_spam.json` dan `final_non_spam.json`.

📍 **Titik penting:**
- Baris **348** — panggilan `commentThreads` untuk mengambil komentar
- Baris **453** — panggilan `videos` untuk metadata
- Baris **476** — panggilan `liveChatMessages` untuk komentar siaran langsung

🔍 **Kenapa hanya butuh `dotenv`?** Karena panggilan API-nya memakai `fetch` bawaan Node.js, bukan SDK Google. `dotenv` cuma dipakai membaca kunci API dari berkas `.env` supaya tidak tertulis di kode. Ini praktik keamanan standar — dan layak disebut kalau ditanya soal pengelolaan kredensial.

⚠️ **Yang harus kamu pahami:** skor dari scraper **bukan label akhir**. Dia cuma tebakan awal. Penentuan label sebenarnya terjadi di berkas berikutnya.

❓ **Kalau ditanya "bagaimana Anda mengambil datanya?"**
> "Lewat YouTube Data API v3 resmi dengan kunci API terdaftar, Pak. Skripnya memanggil endpoint commentThreads untuk mengambil komentar dari video yang dipilih, lalu memberi skor heuristik awal berdasarkan sinyal kecurigaan seperti pola nama situs judi. Skor ini belum jadi label final — masih disaring lagi di tahap berikutnya."

---

## A2. `src/prepare_dataset.py` (357 baris)

🎯 **Perannya:** mengubah hasil mentah scraper jadi dataset berlabel yang siap dilatih.

📄 **Di skripsi:** Sub-bab 4.3.4 (Tabel 4.4 Komposisi Dataset)

### Penyaringan dua tahap

Ini bagian yang **wajib kamu pahami** karena menyangkut kualitas label, dan penguji bisa mempertanyakannya.

**Tahap 1 — ambang skor** 📍 baris 155
```python
if score >= threshold:
    spam_entries.append({"text": text, "label": "spam", ...})
```
Komentar dengan skor di atas ambang (80) langsung ditandai spam.

**Tahap 2 — penyelamatan brand** 📍 baris 177–181
```python
if (BRAND_RESCUE_PATTERN.search(normalized)
        or BRAND_SUFFIX_PATTERN.search(normalized)):
    spam_entries.append({"text": text, "label": "spam", ...})
    rescued += 1
```

🔍 **Kenapa perlu tahap kedua?** Karena banyak spam asli hanya memicu **satu** sinyal saja, yaitu nama brand-nya, sehingga skornya rendah (sekitar 40–75) dan lolos dari tahap 1.

Dua polanya 📍 baris 106 dan 127:
- `BRAND_RESCUE_PATTERN` → huruf kapital semua diikuti angka: `WIFI4D`, `ROMA4D`
- `BRAND_SUFFIX_PATTERN` → 3+ huruf diikuti akhiran khas: `NAGAMASTOTO`, `MANJURBET`, `PULAUWIN`

**Analogi SE:** ini seperti aturan penyaringan berlapis. Lapis pertama menangkap yang jelas, lapis kedua menangkap kasus tepi yang lolos karena skornya tidak cukup tinggi walau sebenarnya jelas spam.

⚠️ **Ini titik rawan pertanyaan.** Penguji bisa bertanya: *"kalau labelnya dari aturan buatan Anda sendiri, bukankah modelnya cuma meniru aturan itu?"*

Jawabannya ada dua lapis:
1. Aturan itu hanya untuk **melabeli**, bukan untuk mendeteksi. Model belajar dari **teks lengkapnya**, bukan dari skornya.
2. Buktinya, ketika aturan heuristik dipasang langsung sebagai pendeteksi (ablation study), hasilnya **jauh lebih buruk** dari model — turun 7,32 sampai 16,30 poin. Artinya model mempelajari sesuatu yang lebih dari sekadar aturan tersebut.

Poin kedua itu **kuat sekali**. Kamu punya bukti empiris bahwa model bukan sekadar meniru aturan pelabelnya.

📍 **Koreksi manual** ada di baris 238 (`apply_manual_overrides`) — membaca `data/manual_overrides.csv` untuk membetulkan label yang salah. Tercatat di kolom `source` sebagai `manual_override`.

---

## A3. `src/preprocessing.py` (366 baris) ⭐

🎯 **Perannya:** membersihkan teks yang disamarkan. **Ini berkas terpenting dalam skripsimu** karena di sinilah "String Normalization" yang ada di judul benar-benar terjadi.

📄 **Di skripsi:** Sub-bab 2.4 (teori) dan 4.3 (penerapan)

### Kenapa berkas ini istimewa

Berkas ini dipakai **dua kali dalam konteks berbeda**:
- Saat pelatihan, dipanggil `src/train.py`
- Saat prediksi, dipanggil `src/server.py`

Itu disengaja, dan alasannya ada di komentar baris **16–29**: menjamin teks yang dilihat model saat prediksi diproses persis sama seperti saat pelatihan. Kalau berbeda, terjadi *training-serving skew*.

### Tujuh tahap dalam `clean_text()` 📍 baris 182

| Tahap | Baris | Yang dilakukan | Contoh |
|---|---|---|---|
| 1 | 205–215 | Buang karakter tak terlihat | `d​a​f​t​a​r` → `daftar` |
| 2 | 224 | Normalisasi Unicode NFKC | `𝑅𝒪𝑀𝒜` → `ROMA` |
| 2b | 237 | Buang tanda diakritik | `P͟U͟L͟A͟U͟` → `PULAU` |
| 2c | 249 | Buka kurung per huruf | `[P][U][L][A][U]` → `PULAU` |
| 3 | 255 | Ganti homoglyph | `dаftаr` (Cyrillic) → `daftar` |
| 4 | 265–266 | Emoji jadi teks | `🎰` → `slot_machine` |
| 5 | 269 | Huruf kecil semua | `DAFTAR` → `daftar` |
| 5b-i | 288–292 | Normalisasi leet speak | `s1tus` → `situs` |
| 5b | 297 | Samakan nama brand | `keju4d` → `judolbrand` |
| 6 | 303–304 | Buang URL & non-huruf | — |
| 7 | 307–311 | Buang stopword & huruf tunggal | — |

### Tiga bagian yang paling menarik untuk diceritakan

**① Urutannya tidak boleh diacak.** 📍 Baris 294–296

Kanonikalisasi brand (5b) **harus** dijalankan **sebelum** penghapusan digit (6). Kalau dibalik, `keju4d` sudah kehilangan angkanya jadi `keju` — dan `keju` itu makanan, bukan judol. Model akan belajar bahwa "keju" adalah penanda spam, dan komentar tentang kuliner ikut tertuduh.

Alasan ini tertulis lengkap di komentar baris 58–75. **Ini contoh bagus untuk ditunjukkan saat sidang** — bukti bahwa urutan pipeline dipikirkan, bukan asal tumpuk.

**② `judolbrand` — satu token untuk semua nama situs.** 📍 Baris 107–109

```python
JUDOL_BRAND_PATTERN = re.compile(
    rf'\b(?!(?:{_EXCL})\d)[a-z]{{2,}}(?:4d|3d|2d|88|99|77|69|138|388|303|777|888|qq)\b'
)
```

Semua nama situs judi yang mengikuti pola *[nama bebas] + [akhiran khas]* diganti jadi satu kata: `judolbrand`.

🔍 **Kenapa cerdas?** Karena model tidak perlu menghafal ribuan nama situs. Dia cukup belajar bahwa `judolbrand` = penanda spam. **Nama situs baru yang belum pernah ada pun langsung tertangkap** selama mengikuti pola yang sama.

**Analogi SE:** seperti mengganti nilai yang bervariasi dengan satu penanda umum sebelum dicocokkan — mengurangi ragam masukan tanpa kehilangan maknanya.

**③ Daftar pengecualian.** 📍 Baris 101–104

```python
_JUDOL_EXCLUDE_PREFIXES = (
    "level", "rank", "stage", "episode", "part", "seri", "versi",
    "chapter", "season", "round", "wave", "fase", "lv",
)
```

`level99` cocok polanya, tapi itu konteks gim, bukan judol. Jadi dikecualikan lewat *negative lookbehind* di regex.

Ini menunjukkan pola dasarnya diuji dan diperbaiki setelah ditemukan kasus salah tangkap — bukan ditulis sekali lalu ditinggal.

**④ Leet speak sengaja dibatasi.** 📍 Baris 280–284

Hanya `0 → o` dan `1 → i`. Tidak `3 → e` atau `4 → a`.

🔍 **Kenapa?** Karena substitusi yang lebih agresif berisiko merusak angka yang sah. Kalau `3 → e` diterapkan, skor "354" berubah jadi "ses". Ini **pertukaran yang disengaja** dan alasannya tertulis di kode.

❓ **Kalau ditanya "kenapa tidak semua angka dinormalkan?"**
> "Karena berisiko merusak angka yang memang angka, Pak. Kalau 3 diubah jadi e dan 4 jadi a, maka angka seperti 354 berubah jadi kata yang tidak bermakna. Saya batasi hanya pada 0 dan 1 karena keduanya paling umum dipakai sebagai pengganti huruf o dan i dalam spam judol Indonesia, sementara risikonya paling kecil."

### Cara mencobanya sendiri

Berkas ini bisa dijalankan langsung dan punya kasus uji bawaan 📍 baris 333:
```bash
python src/preprocessing.py
```
Akan menampilkan 10 contoh teks tersamar beserta hasil pembersihannya. **Ini demo yang bagus untuk sidang** — visual, cepat, dan langsung membuktikan klaim di judul skripsimu.

---

# BAGIAN B — Model

## B1. `src/train.py` (475 baris) ⭐

🎯 **Perannya:** melatih model, mengevaluasinya, dan menyimpan hasilnya.

📄 **Di skripsi:** Sub-bab 4.4.1 (Gambar 4.1) dan seluruh Sub-bab 4.10

### Tujuh tahap yang dijalankan

Kalau kamu menjalankan berkas ini, keluarannya diberi penanda `[1/7]` sampai `[7/7]`:

| Tahap | Fungsi | Baris |
|---|---|---|
| 1 | Muat dataset | 71 |
| 2 | Bersihkan teks | 95 |
| 3 | Cross-validation | 105 |
| 4 | Bagi data latih/uji | 184 |
| 5 | Cari nilai C terbaik | 229 |
| 6 | Latih model final | 323 |
| 7 | Evaluasi & simpan | 409, 439 |

### Baris yang menghasilkan angka di skripsimu

| Baris | Menghasilkan |
|---|---|
| 63–68 | Empat pengaturan TF-IDF |
| 128 | CV 0,9741 ± 0,0030 |
| 197–201 | Pembagian 5.352 / 1.338 |
| 233 | Kandidat C: 0,01 / 0,1 / 1 / 10 / 100 |
| 255 | C terbaik = 1 |
| 409 | Akurasi 97,53% |
| 410 | F1-macro 0,9726 |
| 415 | Tabel presisi/recall/F1 |
| 418 | Confusion matrix 863/9/24/442 |
| 439 | Simpan model ke `.joblib` |

### Konsep Pipeline — penting untuk dipahami

📍 Baris 123–126, 334–341:

```python
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
    ("svm", SVC(kernel="linear", class_weight="balanced", random_state=42))
])
```

🔍 `Pipeline` merangkai TF-IDF dan SVM jadi **satu objek**. Kenapa penting?

Karena yang disimpan ke `.joblib` adalah **seluruh pipeline**, bukan cuma SVM-nya. Di dalamnya termasuk kamus kata hasil pelatihan TF-IDF.

Kalau yang disimpan hanya SVM-nya, saat prediksi kamu tidak punya kamus kata yang sama — kata ke-500 saat pelatihan bisa jadi kata ke-3000 saat prediksi, dan hasilnya kacau total.

**Analogi SE:** seperti mengemas aplikasi beserta seluruh dependensinya, bukan cuma berkas biner utamanya.

### Satu detail yang sering ditanya

📍 Baris 105–119: cross-validation dijalankan pada **seluruh data** (6.690), bukan hanya data latih.

Alasannya tertulis di komentar: tujuan CV adalah menaksir kemampuan generalisasi, dan makin banyak data yang dilipat makin stabil taksirannya. Ini **terpisah** dari pembagian 80:20 yang tujuannya berbeda — memberi rincian per kelas dan confusion matrix.

⚠️ Sementara pencarian nilai C 📍 baris 245 dijalankan **hanya pada data latih**, supaya data uji tidak bocor mempengaruhi pemilihan parameter.

Dua perlakuan berbeda dengan alasan berbeda. Kalau kamu paham bedanya, itu tanda kamu benar-benar mengerti alurnya.

---

## B2. Berkas eksperimen

Lima berkas yang **tidak ikut berjalan di runtime**, tapi menghasilkan angka-angka yang kamu kutip.

| Berkas | Menghasilkan | Di skripsi |
|---|---|---|
| `compare_baselines.py` | SVM 97,53% · LogReg 97,09% · NB 93,95% | Tabel 4.12 |
| `evaluate_hard_set.py` | 135 kasus · 98,52% · 2 FP | Sub-bab 4.10.5 |
| `evaluate_hybrid_ablation.py` | −7,32 dan −16,30 poin | Tabel 4.13 |
| `experiment_stemming.py` | p-value 0,3575 | Gambar 4.10 |
| `experiment_features.py` | Perbandingan N-gram | Sub-bab 4.3 |

📍 **Yang membuat perbandingan di `compare_baselines.py` sah** — baris 121 dan 125: ketiga algoritma memakai `TFIDF_PARAMS` dan pembagian data yang sama persis. Yang berbeda hanya klasifikatornya. Kalau fiturnya berbeda, perbandingannya tidak adil.

📍 **`evaluate_hard_set.py` baris 34** memuat keterangan penting: *"135 entri, semua berlabel non_spam"*. Inilah sumber angka F1-macro 0,4963 yang menyesatkan itu — lihat penjelasannya di `03-angka-ke-kode.md`.

---

# BAGIAN C — Sistem

## C1. `src/server.py` (458 baris)

🎯 **Perannya:** menyajikan model lewat REST API.

📄 **Di skripsi:** Sub-bab 2.14 dan 4.6

### Empat endpoint

| Endpoint | Baris | Fungsi |
|---|---|---|
| `GET /` | 261 | Info dasar |
| `GET /health` | 270 | Cek server hidup & model termuat |
| `POST /predict` | 279 | Klasifikasi satu komentar |
| `POST /predict/batch` | 336 | Klasifikasi banyak sekaligus (maks 50) |
| `POST /report` | 391 | Lapor salah klasifikasi (mode pengembangan) |

### Alur `/predict` 📍 baris 279–330

```
terima {"text": "..."}
   ↓
cek model sudah termuat                    (baris 294)
   ↓
clean_text(request.text)                   (baris 298)  ← berkas yang SAMA dengan pelatihan
   ↓
model.predict_proba(...)                   (baris 307)  ← Platt Scaling di sini
   ↓
kembalikan {"label", "confidence", "is_spam"}
```

⚠️ **Baris 298 itu inti argumen konsistensi.** Server memanggil `clean_text` yang sama persis dengan yang dipakai `train.py`. Kalau penguji menanyakan konsistensi pelatihan-prediksi, tunjuk baris ini.

📍 **Model dimuat sekali saat server menyala** — baris 80 (`load_model`) dipanggil dari baris 92–93 (`@app.on_event("startup")`).

🔍 **Kenapa tidak dimuat tiap permintaan?** Karena membaca berkas model dari cakram itu mahal. Dimuat sekali ke memori, lalu dipakai berulang. **Analogi SE:** seperti *connection pooling* — sumber daya mahal disiapkan di awal, bukan tiap permintaan.

📍 **Validasi masukan** ada di baris 108 (`text_must_not_be_empty`) dan 245 (`label_must_be_valid`). Ditulis sebagai aturan Pydantic, jadi permintaan yang melanggar otomatis ditolak tanpa perlu pengecekan manual di tiap endpoint.

---

## C2. `extension/content.js` (540 baris)

🎯 **Perannya:** disuntikkan ke halaman YouTube; membaca komentar, bertanya ke server, menyembunyikan yang spam.

📄 **Di skripsi:** Sub-bab 4.11

### Empat mekanisme yang perlu kamu pahami

**① MutationObserver** 📍 sekitar baris 76 dan seterusnya

YouTube memuat komentar secara bertahap saat pengguna menggulir. Kalau ekstensi cuma memindai sekali saat halaman terbuka, komentar berikutnya tidak akan tersentuh.

`MutationObserver` adalah mekanisme bawaan peramban yang memantau perubahan struktur halaman. Setiap kali komentar baru muncul, ekstensi langsung tahu.

**Analogi SE:** ini pola *observer* / *event listener*, bukan *polling*. Lebih efisien karena tidak perlu memeriksa berulang-ulang.

**② WeakSet untuk mencegah pemrosesan ulang** 📍 baris 76

```javascript
let processedComments = new WeakSet();
```

Komentar yang sudah diproses dicatat supaya tidak dikirim ulang ke server.

🔍 **Kenapa `WeakSet`, bukan `Set` biasa?** Karena `WeakSet` menyimpan rujukan lemah — ketika elemen komentar dihapus dari halaman, entrinya otomatis bisa dibersihkan pemulung memori. Dengan `Set` biasa, rujukannya tertahan dan memori terus bertambah selama halaman dibuka.

**Ini detail yang bagus untuk disebut** kalau ditanya soal efisiensi — menunjukkan pertimbangan pengelolaan memori.

**③ Pengiriman berkelompok** 📍 baris 380–381

```javascript
const BATCH_SIZE = 50;
for (let i = 0; i < toProcess.length; i += BATCH_SIZE) {
```

Komentar dikirim 50 sekaligus, bukan satu per satu. Mengurangi jumlah permintaan HTTP secara drastis.

**Analogi SE:** *batching* untuk mengurangi beban jaringan — sama seperti *bulk insert* ketimbang menyisipkan baris satu per satu.

**④ Dua mode penyembunyian** 📍 baris 281 dan 287–288

```javascript
element.style.display = "none";        // mode Hilangkan
...
element.style.opacity = "0.15";        // mode Redupkan
```

- **Hilangkan** → komentar hilang sepenuhnya
- **Redupkan** → komentar diburamkan sampai transparansi 15%, disertai badge persentase keyakinan, dan bisa diklik untuk ditampilkan kembali

📍 Baris 314 (`element.style.opacity = "1"`) adalah pengembaliannya saat badge diklik.

🔍 **Kenapa disediakan dua mode?** Karena ada pertukaran antara kenyamanan dan kendali. Mode Redupkan lebih aman — kalau model salah tuduh, pengguna masih bisa melihat komentarnya. Mode Hilangkan lebih bersih tapi tidak memberi kesempatan koreksi.

⚠️ **Penting:** penyembunyian ini hanya terjadi di **tampilan peramban pengguna sendiri**. Tidak ada data YouTube yang diubah. Ini argumen kunci untuk pertanyaan kelayakan hukum.

---

## C3. `extension/popup.js` (198 baris) dan `manifest.json`

🎯 **`popup.js`** menangani panel pengaturan: pemilihan mode, penggeser ambang batas (50–95%), statistik deteksi, dan tombol cek status server.

🎯 **`manifest.json`** adalah berkas konfigurasi wajib ekstensi Chrome. Yang perlu kamu tahu:
- `"manifest_version": 3` → standar terbaru yang diwajibkan Google
- `permissions: ["storage", "activeTab"]` → izin minimal. `storage` untuk menyimpan pengaturan pengguna, `activeTab` untuk mengakses tab yang sedang dibuka
- `run_at: "document_idle"` → skrip dijalankan setelah halaman selesai dimuat, supaya tidak memperlambat pemuatan awal

🔍 **Prinsip izin minimal itu layak disebut** kalau ditanya soal keamanan: ekstensi ini tidak meminta izin membaca seluruh riwayat peramban atau data di situs lain.

✅ Entri Instagram yang dulu ada di `host_permissions`/`content_scripts` sudah dihapus — ekstensi ini sekarang murni YouTube-only, konsisten dengan judul skripsi. Lihat `04-kenapa-a-bukan-b.md` bagian 7 untuk riwayat keputusannya.

---

# Peta cepat: kalau ditanya X, buka berkas Y

| Pertanyaan penguji | Berkas | Baris |
|---|---|---|
| "Mana normalisasi teksnya?" | `src/preprocessing.py` | 182 (`clean_text`) |
| "Mana penanganan homoglyph?" | `src/preprocessing.py` | 148–175 |
| "Mana penanganan leet speak?" | `src/preprocessing.py` | 288–292 |
| "Mana pengaturan TF-IDF?" | `src/train.py` | 63–68 |
| "Mana pembagian data?" | `src/train.py` | 197–201 |
| "Mana pencarian parameter C?" | `src/train.py` | 233, 255 |
| "Mana perhitungan akurasi?" | `src/train.py` | 409 |
| "Mana confusion matrix-nya?" | `src/train.py` | 418 |
| "Mana penyimpanan model?" | `src/train.py` | 439 |
| "Mana endpoint API?" | `src/server.py` | 279, 336 |
| "Mana pemuatan model?" | `src/server.py` | 80, 92 |
| "Mana penyembunyian komentarnya?" | `extension/content.js` | 281, 287 |
| "Mana pemantauan komentar baru?" | `extension/content.js` | ~76 (MutationObserver) |
| "Mana pelabelan datanya?" | `src/prepare_dataset.py` | 155, 177 |
| "Mana pengambilan datanya?" | `scraper/index.js` | 348 |

Cetak tabel ini dan bawa ke sidang. Tidak ada salahnya membuka berkas di depan penguji — yang penting kamu tahu **harus membuka yang mana**.

---

## Selanjutnya

Lanjut ke `LAB-praktik.md` untuk mencoba menjalankan sendiri, atau `05-instalasi.md` kalau ingin menyiapkan dari nol.
