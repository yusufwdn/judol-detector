# Deployment

Server API dijalankan di VPS Ubuntu 24.04 LTS, di belakang Nginx sebagai
reverse proxy dengan sertifikat TLS dari Let's Encrypt.

Spesifikasi yang dipakai: 2 vCPU, RAM 2 GB, penyimpanan 40 GB.

## Kenapa perlu HTTPS

YouTube berjalan di HTTPS. Jika ekstensi melakukan fetch ke alamat HTTP biasa,
Chrome memblokirnya sebagai mixed content, karena halaman aman tidak boleh
memuat sumber daya yang tidak aman.

Karena itu nama domain dan sertifikat TLS bukan pelengkap, melainkan syarat
agar ekstensi bisa berfungsi sama sekali.

## Komponen

| Komponen | Peran |
|---|---|
| Uvicorn | Menjalankan aplikasi FastAPI, mendengarkan di `127.0.0.1:8000` |
| systemd | Menyalakan Uvicorn saat boot dan menjalankannya ulang jika proses mati |
| Nginx | Menerima trafik dari internet dan meneruskannya ke Uvicorn |
| Certbot | Menerbitkan dan memperpanjang sertifikat TLS |

Uvicorn sengaja hanya mendengarkan di alamat loopback, sehingga aplikasi Python
tidak pernah terekspos langsung ke internet. Seluruh trafik masuk melewati
Nginx.

Tanpa systemd, proses akan mati begitu sesi SSH ditutup.

## Berkas konfigurasi

| Berkas | Isi |
|---|---|
| [`deploy/judol-api.service`](../deploy/judol-api.service) | Unit systemd |
| [`deploy/nginx-judol-api.conf`](../deploy/nginx-judol-api.conf) | Blok server Nginx |
| [`deploy/requirements-serve.txt`](../deploy/requirements-serve.txt) | Dependensi minimal untuk menjalankan server saja |
| [`deploy/privacy-policy.html`](../deploy/privacy-policy.html) | Halaman kebijakan privasi, disajikan lewat `GET /privacy` |

`requirements-serve.txt` dipisahkan dari `requirements.txt` karena server tidak
membutuhkan pustaka pelatihan dan pembuatan grafik.

Berkas Nginx yang disertakan hanya memuat blok port 80. Certbot menyisipkan
sendiri blok TLS-nya saat dijalankan dengan `certbot --nginx`.

## Langkah pemasangan

```bash
git clone https://github.com/yusufwdn/svm-judol-spam.git
cd svm-judol-spam
python3 -m venv venv
venv/bin/pip install -r deploy/requirements-serve.txt

sudo cp deploy/judol-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now judol-api

sudo cp deploy/nginx-judol-api.conf /etc/nginx/sites-available/judol-api
sudo ln -s /etc/nginx/sites-available/judol-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

sudo certbot --nginx -d <nama-domain>
```

Sesuaikan `User`, `WorkingDirectory`, dan `ExecStart` di berkas unit systemd
dengan lokasi pemasangan yang dipakai.

## Token pelaporan

`REPORT_TOKEN` tidak ditulis di berkas unit systemd, karena berkas itu ikut
diversikan. Nilainya dibaca dari berkas environment terpisah:

```bash
echo "REPORT_TOKEN=$(openssl rand -hex 32)" | sudo tee /etc/judol-api.env
sudo chown root:root /etc/judol-api.env
sudo chmod 600 /etc/judol-api.env
sudo systemctl restart judol-api
```

Berkas unit merujuknya dengan awalan tanda minus:

```
EnvironmentFile=-/etc/judol-api.env
```

Awalan itu membuat systemd tetap menjalankan layanan meskipun berkasnya tidak
ada. Tanpa berkas tersebut `REPORT_TOKEN` kosong dan endpoint `/report`
otomatis menolak semua permintaan, yang memang kondisi bawaan yang diinginkan.

## CORS

```python
allow_origins=[
    "chrome-extension://<ID ekstensi>",
    "https://www.youtube.com",
]
```

Dua origin, bukan satu, dan perbedaannya tidak kentara.

`popup.js` berjalan di konteks ekstensi sendiri, sehingga fetch darinya membawa
`Origin` berupa `chrome-extension://<ID>`. Sementara `content.js` disuntikkan
ke dalam halaman YouTube, sehingga fetch darinya membawa `Origin` milik halaman
itu, yaitu `https://www.youtube.com`.

Membatasi CORS hanya ke ID ekstensi membuat permintaan dari `content.js`
ditolak, padahal `popup.js` berjalan normal. Kedua origin harus disebutkan.

Origin tidak dibiarkan `*` agar situs mana pun tidak bisa memanggil API ini
lewat peramban pengunjungnya.

## Pemeriksaan saat bermasalah

| Gejala | Kemungkinan penyebab | Pemeriksaan |
|---|---|---|
| Ekstensi tidak terhubung | Layanan berhenti | `sudo systemctl status judol-api` |
| Galat CORS dari `content.js` | `https://www.youtube.com` belum ada di `allow_origins` | Periksa `src/server.py` |
| Sertifikat kedaluwarsa | Perpanjangan otomatis gagal | `sudo certbot renew --dry-run` |
| ID ekstensi berubah | Medan `key` hilang dari `manifest.json` | Bandingkan dengan versi di repositori |
| `/report` membalas 401 | Token tidak cocok | Periksa `/etc/judol-api.env` |
| `/report` membalas 503 | Server berjalan tanpa `REPORT_TOKEN` | Buat berkas environment lalu muat ulang layanan |
