# 05 — Instalasi dan Menjalankan

> Dari nol sampai sistem berjalan, plus penjelasan apa yang terjadi di balik tiap perintah.

Dokumen ini juga menjawab pertanyaan penguji seperti *"apa saja yang dibutuhkan untuk menjalankan sistem ini?"* dan *"pustaka apa saja yang dipakai?"*

---

## Yang dibutuhkan

| Kebutuhan | Versi | Untuk apa |
|---|---|---|
| Python | 3.10+ | Pelatihan model dan server |
| Node.js | 18+ | Pengambil data (hanya kalau ingin mengambil data baru) |
| Google Chrome | 88+ | Menjalankan ekstensi (Manifest V3) |
| Kunci YouTube Data API | — | Hanya kalau ingin mengambil data baru |

⚠️ **Untuk demo sidang, kamu cukup Python dan Chrome.** Node.js dan kunci API hanya diperlukan kalau ingin mengumpulkan data baru — dan itu tidak perlu dilakukan saat sidang karena dataset sudah tersedia.

---

## Langkah 1 — Menyiapkan lingkungan Python

```bash
cd c:\Personal\kulyeah\Skripsi\svm-judol-spam
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

🔍 **Apa yang terjadi:**

`python -m venv env` membuat **lingkungan virtual** — folder terpisah berisi salinan Python beserta pustakanya sendiri.

**Analogi SE:** ini seperti `node_modules` pada proyek JavaScript. Tanpa ini, semua pustaka terpasang secara global dan proyek berbeda bisa saling bentrok kalau butuh versi berbeda.

`env\Scripts\activate` mengaktifkannya. Setelah aktif, prompt terminal berawalan `(env)`. Semua perintah `python` dan `pip` sesudahnya memakai lingkungan tersebut, bukan Python global.

`pip install -r requirements.txt` memasang seluruh pustaka yang tercantum.

---

## Pustaka apa saja dan untuk apa

Ini sering ditanya. Isi `requirements.txt`:

### Inti Machine Learning
| Pustaka | Untuk apa |
|---|---|
| `scikit-learn` | **Yang utama.** Menyediakan TF-IDF, SVM, pembagian data, cross-validation, GridSearchCV, dan seluruh metrik evaluasi |
| `pandas` | Membaca dan mengolah berkas CSV dataset |
| `numpy` | Operasi array numerik, dipakai di balik layar oleh scikit-learn |

### Penyimpanan model
| Pustaka | Untuk apa |
|---|---|
| `joblib` | Menyimpan dan memuat model terlatih. Lebih efisien dari `pickle` bawaan untuk array numerik besar |

### Server
| Pustaka | Untuk apa |
|---|---|
| `fastapi` | Kerangka kerja REST API |
| `uvicorn` | Server yang menjalankan FastAPI |
| `pydantic` | Validasi masukan otomatis — misalnya menolak teks kosong atau batch lebih dari 50 |

### Pemrosesan teks
| Pustaka | Untuk apa |
|---|---|
| `emoji` | Mengubah emoji jadi token teks (🎰 → `slot_machine`) |
| `PySastrawi` | Stemmer Bahasa Indonesia — **hanya dipakai untuk eksperimen**, tidak di pipeline akhir |

### Visualisasi
| Pustaka | Untuk apa |
|---|---|
| `matplotlib` | Membuat grafik untuk skripsi (confusion matrix, grafik per fold, hasil GridSearchCV) |
| `seaborn` | Heatmap confusion matrix (Gambar 4.7) |

❓ **Kalau ditanya "kenapa PySastrawi ada di requirements padahal tidak dipakai?"**
> "Sastrawi dipakai untuk menjalankan eksperimen stemming, Pak, bukan untuk pipeline akhir. Hasil eksperimennya menunjukkan stemming tidak signifikan, jadi tidak dipakai di sistem. Tapi pustakanya tetap dicantumkan supaya eksperimen itu bisa diulang dan diverifikasi orang lain."

❓ **Kalau ditanya "kenapa pakai scikit-learn, bukan menulis SVM sendiri?"**
> "Karena scikit-learn adalah pustaka standar yang sudah teruji luas dan dioptimalkan, Pak. Menulis ulang SVM sendiri berisiko memasukkan galat implementasi, dan hasilnya jadi sulit dibandingkan dengan penelitian lain. Dengan memakai pustaka standar, hasil penelitian ini bisa direproduksi siapa pun."

---

## Langkah 2 — Menjalankan server

> 🌐 **Update:** Server sekarang juga sudah live 24 jam di VPS (`https://api-svm.cupsky.my.id`), dikelola `systemd` — **tidak perlu dijalankan manual untuk demo sidang**, ekstensi sudah diarahkan ke situ langsung. Langkah di bawah tetap berguna untuk pengembangan lokal atau sebagai cadangan kalau internet ruangan sidang bermasalah. Detail arsitektur deployment-nya ada di `10-deployment-vps.md`.

```bash
python src/server.py
```

🔍 **Yang terjadi saat server menyala:**
1. Uvicorn menyalakan server web di `localhost:8000`
2. Peristiwa `startup` terpicu 📍 `src/server.py:92`
3. Model dimuat sekali dari `model/svm_model.joblib` ke memori 📍 baris 80
4. Server siap menerima permintaan

Server siap kalau `http://localhost:8000/health` memberi respons.

⚠️ **Biarkan terminal ini terbuka.** Menutupnya mematikan server.

---

## Langkah 3 — Memasang ekstensi

1. Chrome → `chrome://extensions`
2. Nyalakan **Developer mode** (pojok kanan atas)
3. **Load unpacked** → pilih folder `svm-judol-spam/extension`
4. Sematkan ikonnya di bilah alamat

🔍 **Kenapa "Load unpacked", bukan dipasang dari Chrome Web Store?** Karena ekstensi ini belum dipublikasikan. Mode pengembang memungkinkan memuat ekstensi langsung dari folder — cara standar saat pengembangan.

---

## Melatih ulang model (opsional)

**Tidak perlu dilakukan sebelum sidang** — model sudah ada. Ini hanya kalau dataset berubah.

```bash
python src/train.py
```

Berjalan tujuh tahap, memakan waktu beberapa menit. Keluarannya:
- `model/svm_model.joblib` — model baru
- Beberapa berkas grafik di `reports/`

⚠️ **Kalau kamu melatih ulang, angka-angkanya bisa berubah** dan skripsimu jadi tidak sinkron. Jangan menjalankan ini menjelang sidang kecuali memang perlu.

Kalau ingin sekadar memastikan angkanya masih benar tanpa menimpa model, pakai skrip verifikasi yang aman:
```bash
python BELAJAR/verifikasi_angka.py
```
Skrip itu hanya membaca dan menghitung — tidak menimpa apa pun.

---

## Mengambil data baru (opsional)

Butuh Node.js dan kunci YouTube Data API.

```bash
cd scraper
npm install
# siapkan berkas .env berisi kunci API
node index.js
```

Lalu ubah hasilnya jadi dataset:
```bash
python src/prepare_dataset.py
```

⚠️ Ini akan mengubah `data/comments.csv`, dan setelahnya model harus dilatih ulang. **Jangan dilakukan menjelang sidang.**

🔍 **Soal kunci API:** disimpan di berkas `.env`, tidak ditulis di kode, dan `.env` masuk `.gitignore`. Ini praktik keamanan standar yang layak disebut kalau ditanya soal pengelolaan kredensial.

---

## Kalau ada masalah

| Gejala | Kemungkinan penyebab | Solusi |
|---|---|---|
| `ModuleNotFoundError` | Lingkungan virtual belum aktif | Jalankan `env\Scripts\activate` |
| Server menyala tapi prediksi galat | Berkas model tidak ada | Jalankan `python src/train.py` |
| Ekstensi tidak bereaksi | Server mati | Cek `http://localhost:8000/health` |
| Ekstensi aktif tapi tidak ada yang tersembunyi | Ambang batas terlalu tinggi | Turunkan lewat penggeser di panel |
| Galat CORS di konsol peramban | Alamat tidak cocok dengan `host_permissions` | Cek `extension/manifest.json` |

---

## Ringkasan perintah untuk sidang

Cetak dan bawa:

```bash
# 1. Aktifkan lingkungan
cd c:\Personal\kulyeah\Skripsi\svm-judol-spam
env\Scripts\activate

# 2. Nyalakan server (biarkan terminal terbuka)
python src/server.py

# 3. Kalau diminta menunjukkan normalisasi teks
python src/preprocessing.py

# 4. Kalau diminta membuktikan angkanya
python BELAJAR/verifikasi_angka.py
```

Plus dua alamat yang sebaiknya sudah terbuka di tab peramban sebelum sidang dimulai:
- `http://localhost:8000/docs` — dokumentasi API interaktif
- Video YouTube yang komentarnya dipastikan ada spam judol

---

## Selesai

Ini dokumen terakhir dari rangkaian belajar. Kalau seluruhnya sudah dibaca, langkah berikutnya adalah **latihan simulasi sidang** — minta diuji seperti penguji sungguhan untuk menemukan bagian mana yang masih goyah.
