# Referensi API

Server dibangun dengan FastAPI dan didefinisikan di
[`src/server.py`](../src/server.py). Saat berjalan, dokumentasi interaktif
tersedia otomatis di `/docs` dan bisa dipakai untuk mencoba setiap endpoint
tanpa alat tambahan.

Base URL saat pengembangan lokal adalah `http://localhost:8000`.

## Kenapa FastAPI

Aturan validasi ditulis sebagai model Pydantic, sehingga permintaan yang
melanggar ditolak otomatis dengan pesan yang jelas tanpa pengecekan manual di
tiap endpoint. Aturan yang berlaku di proyek ini: teks tidak boleh kosong,
panjang maksimum 5.000 karakter, dan satu permintaan batch maksimal 50 teks.

Flask tidak menyediakan validasi bawaan, sementara Django membawa ORM, sistem
admin, dan template engine yang tidak terpakai untuk empat endpoint JSON tanpa
basis data.

## GET /

Memastikan server hidup.

```json
{
  "status": "online",
  "message": "Spam Detector API is running. Use POST /predict to classify a comment."
}
```

## GET /health

Status pemuatan model. Ekstensi memanggil endpoint ini sebelum mulai mengirim
komentar, dan memanggilnya lagi saat terjadi kegagalan jaringan supaya tidak
terus mencoba menghubungi server yang mati.

```json
{
  "status": "ok",
  "model_loaded": true
}
```

Jika model gagal dimuat, `status` berisi `model_not_loaded`.

## POST /predict

Mengklasifikasi satu komentar.

Permintaan:

```json
{ "text": "Daftar sekarang bonus 100% slot gacor!" }
```

Tanggapan:

```json
{
  "label": "spam",
  "confidence": 0.94,
  "is_spam": true
}
```

| Medan | Tipe | Keterangan |
|---|---|---|
| `label` | string | `spam` atau `non_spam` |
| `confidence` | float | 0,0 sampai 1,0, dibulatkan empat angka di belakang koma |
| `is_spam` | bool | Turunan dari `label`, disediakan agar ekstensi tidak perlu membandingkan string |

Teks diproses dengan `clean_text()` yang sama dengan yang dipakai saat
pelatihan. Jika teks menjadi kosong setelah normalisasi, misalnya karena
isinya hanya emoji yang tidak punya padanan token, tanggapannya `non_spam`
dengan confidence 0,5.

Kode galat:

| Kode | Sebab |
|---|---|
| 422 | Teks kosong atau melebihi 5.000 karakter |
| 503 | Model belum selesai dimuat |

## POST /predict/batch

Mengklasifikasi banyak komentar dalam satu permintaan. Ekstensi memakai
endpoint ini untuk memproses seluruh komentar yang terlihat di layar dalam satu
perjalanan jaringan, alih-alih satu permintaan per komentar.

Permintaan:

```json
{ "texts": ["komentar pertama", "komentar kedua"] }
```

Tanggapan:

```json
{
  "results": [
    { "label": "non_spam", "confidence": 0.88, "is_spam": false },
    { "label": "spam", "confidence": 0.97, "is_spam": true }
  ]
}
```

Urutan `results` sama dengan urutan `texts`. Maksimal 50 teks per permintaan,
lebih dari itu ditolak dengan kode 400.

## POST /report

Menambahkan satu komentar ke dataset pelatihan. Dipanggil ekstensi saat
pengguna menandai komentar yang salah disembunyikan.

Permintaan:

```json
{ "text": "teks komentar", "label": "non_spam" }
```

Membutuhkan header `X-Report-Token`.

Endpoint ini menulis langsung ke `data/comments.csv` dan
`data/manual_overrides.csv`, yaitu data yang dipakai melatih model berikutnya.
Tanpa pembatasan, siapa pun yang tahu URL-nya bisa menyuntikkan baris
sembarangan ke dataset. Karena itu token wajib, dan jika server dijalankan
tanpa `REPORT_TOKEN` maka endpoint ini menolak semua permintaan dengan kode
503 alih-alih memakai nilai bawaan bersama.

Token dibaca dari environment. Pada deployment VPS, nilainya disimpan di
`/etc/judol-api.env` yang tidak ikut diversikan. Lihat
[deployment.md](deployment.md).

Teks yang sudah ada di salah satu berkas tersebut ditolak sebagai duplikat
dengan `success: false` dan `duplicate: true`.

Kode galat:

| Kode | Sebab |
|---|---|
| 401 | Header `X-Report-Token` salah atau tidak ada |
| 503 | Server dijalankan tanpa `REPORT_TOKEN` |

## GET /privacy

Menyajikan halaman kebijakan privasi dari
[`deploy/privacy-policy.html`](../deploy/privacy-policy.html). Halaman ini
dibutuhkan saat pengajuan ke Chrome Web Store, dan disajikan lewat FastAPI
supaya ikut ter-deploy bersama kode tanpa konfigurasi Nginx tambahan.

## Aturan heuristik yang dinonaktifkan

Terdapat blok `ENABLE_HYBRID_RULES` di `src/server.py` yang secara bawaan
bernilai `False`. Blok ini menimpa keputusan model berdasarkan daftar kata
kunci judi. Pengukuran menunjukkan aturan tersebut menurunkan akurasi, sehingga
dimatikan tetapi tidak dihapus agar hasil eksperimennya bisa diverifikasi
ulang. Rinciannya ada di [eksperimen.md](eksperimen.md#aturan-heuristik-tambahan).
