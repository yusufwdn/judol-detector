# Instalasi dan Cara Menjalankan

## Prasyarat

| Perangkat lunak | Versi minimum |
|---|---|
| Python | 3.10 |
| Google Chrome | Terbaru |
| Node.js | 18, hanya jika ingin menjalankan scraper |

## Menyiapkan environment

```bash
git clone https://github.com/yusufwdn/judol-detector.git
cd judol-detector
python -m venv env
```

Aktifkan virtual environment sesuai terminal yang dipakai:

| Terminal | Perintah |
|---|---|
| PowerShell | `.\env\Scripts\Activate.ps1` |
| Command Prompt | `env\Scripts\activate.bat` |
| Git Bash | `source env/Scripts/activate` |
| bash atau zsh | `source env/bin/activate` |

Jika PowerShell menolak menjalankan skrip aktivasi, jalankan perintah berikut
sekali sebagai Administrator lalu ulangi:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Lalu pasang dependensinya:

```bash
pip install -r requirements.txt
```

## Menjalankan server

Repositori ini sudah menyertakan `model/svm_model.joblib`, jadi server bisa
langsung dijalankan tanpa melatih ulang.

```bash
python src/server.py
```

Server berjalan di `http://localhost:8000`. Dokumentasi interaktif yang
dihasilkan FastAPI tersedia di `http://localhost:8000/docs`, dan bisa dipakai
untuk mencoba setiap endpoint tanpa alat tambahan.

Untuk mencoba lewat baris perintah:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Daftar sekarang bonus 100% slot gacor!"}'
```

Referensi lengkap tiap endpoint ada di [api.md](api.md).

## Memasang ekstensi

1. Buka `chrome://extensions`
2. Aktifkan **Developer mode**
3. Klik **Load unpacked**
4. Pilih folder `extension/`

Secara bawaan ekstensi menunjuk ke server publik yang tercantum di
`extension/content.js`. Untuk memakai server lokal, ubah `API_BASE` di
[`extension/content.js`](../extension/content.js) dan
[`extension/popup.js`](../extension/popup.js) menjadi `http://localhost:8000`,
lalu tambahkan origin tersebut ke `allow_origins` di
[`src/server.py`](../src/server.py).

## Melatih ulang model

Dua langkah, selalu berurutan:

```bash
python src/prepare_dataset.py
python src/train.py
```

`prepare_dataset.py` membaca `scraper/final_spam.json` dan
`scraper/final_non_spam.json`, menerapkan penyaringan dua tahap dan koreksi
manual, lalu menulis `data/comments.csv`. Keluarannya kurang lebih seperti ini:

```
[1/4] Loading spam data (threshold >= 80)...
  Total entries in JSON        : 2324
  Passed primary threshold     : 138
  Rescued via brand regex      : 1947
  Skipped (low score / noisy)  : 239
  Total spam collected         : 2085

[2/4] Loading non-spam data...
  Loaded                : 4095

[3/4] Applying manual overrides (data/manual_overrides.csv)...
  Loaded 592 manual overrides

[4/4] Merging, shuffling, and saving dataset...
  Spam samples    : 2332
  Non-spam samples: 4358
  Total           : 6690
```

`train.py` melatih model, menjalankan cross-validation dan pencarian
hyperparameter, menyimpan grafik ke `reports/`, lalu menulis
`model/svm_model.joblib`.

Setiap kali [`src/preprocessing.py`](../src/preprocessing.py) diubah, kedua
langkah di atas harus dijalankan ulang. Melewatkannya membuat model produksi
memakai kamus fitur dari aturan normalisasi yang lama. Alasannya dijelaskan di
[arsitektur.md](arsitektur.md#kenapa-normalisasi-dilakukan-di-python).

## Menambah atau mengoreksi data

`data/comments.csv` ditulis ulang setiap kali `prepare_dataset.py` dijalankan,
jadi jangan menyuntingnya langsung. Perubahan yang hanya ada di berkas itu akan
hilang pada rebuild berikutnya.

| Kebutuhan | Berkas yang diubah |
|---|---|
| Mengoreksi label satu komentar | `data/manual_overrides.csv` |
| Menambah banyak data spam baru | `scraper/final_spam.json` |
| Menambah banyak data non-spam baru | `scraper/final_non_spam.json` |

Koreksi label ditulis dalam dua kolom:

```csv
text,label
"teks komentar yang mau dikoreksi",non_spam
```

Lalu jalankan ulang `prepare_dataset.py` dan `train.py`.

## Menjalankan scraper

Scraper membutuhkan kunci YouTube Data API v3 di berkas `.env`:

```
YOUTUBE_API_KEY=kunci_api_kamu
```

```bash
node scraper/index.js <VIDEO_ID>                    # mode spam
node scraper/index.js <VIDEO_ID> video non_spam     # mode non-spam
```

Keluaran mentah tersimpan di `scraper/result/` dan tidak ikut diversikan.
Tahap agregasi yang menggabungkan hasil per video menjadi `final_spam.json`
dan `final_non_spam.json` dikerjakan oleh repositori terpisah, lihat
[dataset.md](dataset.md#pengumpulan-data).
