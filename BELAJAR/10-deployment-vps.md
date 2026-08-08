# 10 — Deployment ke VPS

> Sistem sekarang **beneran** jalan di server publik, bukan cuma klaim di naskah. Dokumen ini menjelaskan apa yang di-deploy, kenapa tiap bagiannya ada, dan cara menjawab kalau penguji nanya soal ini.

---

## 🎯 Intinya

Server API (`src/server.py`) di-deploy ke VPS Sumopod (Ubuntu 24.04 LTS, 2 vCPU, RAM 2 GB, 40 GB SSD, region Jakarta), diakses lewat `https://api-svm.cupsky.my.id` dengan HTTPS asli dari Let's Encrypt. Ekstensi Chrome sekarang bicara ke domain itu, bukan `localhost:8000` lagi. Konsekuensi paling penting buat sidang: **kamu tidak perlu lagi membuka terminal dan menjalankan `python src/server.py` sebelum demo** — server-nya sudah menyala 24 jam di VPS, dikelola `systemd` yang otomatis restart kalau crash.

---

## 🔍 Penjelasan

### Kenapa butuh VPS, bukan cuma localhost?

`localhost:8000` cuma bisa diakses dari komputer yang sama dengan yang menjalankan server. Itu cukup buat pengembangan, tapi tidak cocok dengan klaim di naskah ("server dapat diakses melalui jaringan internet") dan bikin demo rapuh — kalau laptop yang dipakai demo bukan laptop pengembangan, servernya tidak ada.

### Komponen yang dipasang di VPS

| Komponen | Fungsi |
|---|---|
| **Uvicorn** | Menjalankan aplikasi FastAPI-nya sendiri (sama seperti di lokal) |
| **systemd** (`judol-api.service`) | "Penjaga" yang menyalakan Uvicorn saat VPS boot dan otomatis me-restart-nya kalau proses itu mati. Tanpa ini, proses mati begitu sesi SSH ditutup |
| **Nginx** | *Reverse proxy* — menerima request dari internet di port 443 (HTTPS), meneruskannya ke Uvicorn yang cuma dengar di `127.0.0.1:8000` (tidak diekspos langsung ke internet) |
| **Certbot / Let's Encrypt** | Menerbitkan sertifikat SSL gratis dan otomatis memperpanjangnya sebelum kedaluwarsa |

**Analogi SE:** ini pola yang sama dengan deploy aplikasi Node.js/Express di production — jarang sekali Express listen langsung di port 443 dengan sertifikat sendiri. Biasanya ada Nginx/Caddy di depannya yang urus HTTPS dan diteruskan ke port internal aplikasi lewat HTTP biasa. `systemd` di sini perannya mirip `pm2` atau `docker restart: always` di ekosistem Node.

### Kenapa harus HTTPS, tidak bisa HTTP + IP saja?

YouTube berjalan di `https://`. Kalau ekstensi men-*fetch* ke `http://` (bukan `https://`), Chrome memblokirnya sebagai **mixed content** — halaman aman (HTTPS) tidak boleh memuat resource tidak aman (HTTP). Ini alasan kenapa domain (bukan cuma IP) dan sertifikat SSL itu wajib, bukan sekadar bagus-bagusan.

### Kenapa Origin *pinned* di `manifest.json`?

Untuk ekstensi yang dimuat lewat "Load unpacked" (mode developer), Chrome biasanya menghitung ID ekstensi dari **path folder di disk**. Artinya kalau ekstensi dimuat dari device lain atau folder dengan path berbeda, ID-nya berubah.

Ini berbahaya untuk sidang: kalau demo memakai laptop lain, ID ekstensi berubah, dan server yang membatasi CORS ke ID lama akan menolak semua request — ekstensi terlihat "tidak konek" persis di depan penguji.

Solusinya: field `"key"` di `manifest.json` — sebuah public key RSA yang membuat Chrome menghitung ID secara **deterministik** dari key itu, bukan dari path. Selama file `manifest.json` yang dipakai sama, ID-nya selalu sama: `digamkbgoiiallgimhmhmgkaddliaafg`, di device manapun.

### CORS: kenapa dua origin, bukan satu?

Awalnya CORS cuma diizinkan untuk `chrome-extension://<ID>` — logikanya "yang boleh akses cuma ekstensi ini". Tapi begitu dites langsung di YouTube, request dari `content.js` malah kena CORS block, padahal `popup.js` baik-baik saja.

**Penyebabnya:** `content.js` disuntikkan (*injected*) ke dalam halaman YouTube, sehingga *fetch*-nya membawa header `Origin` milik halaman itu (`https://www.youtube.com`), **bukan** `chrome-extension://<ID>`. Ini kuirk level browser, bukan bug di kode — `popup.js` beda karena dia jalan di context ekstensi sendiri (bukan halaman web), jadi Origin-nya memang `chrome-extension://...`.

Solusi finalnya membatasi CORS ke dua origin, konsisten dengan `host_permissions` yang memang cuma satu domain itu:
```python
allow_origins=[
    "chrome-extension://digamkbgoiiallgimhmhmgkaddliaafg",  # popup.js
    "https://www.youtube.com",                               # content.js di YouTube
]
```

### Kenapa `/report` butuh token?

Endpoint ini menulis langsung ke `data/comments.csv` — dataset yang dipakai untuk melatih model berikutnya. Selama server cuma jalan di `localhost`, tidak masalah karena cuma pemilik komputer yang bisa memanggilnya. Begitu server publik, siapa pun yang tahu URL-nya bisa mengirim `POST /report` lewat `curl`/Postman dan menyuntikkan baris sembarangan ke dataset (**data poisoning**).

Solusinya token sederhana di header `X-Report-Token`, dicek server sebelum menulis apa pun. Ini bukan proteksi sempurna — token itu ikut ter-*hardcode* di `content.js` yang bisa dibaca siapa pun yang membongkar ekstensinya — tapi cukup untuk menyaring bot/scanner otomatis yang asal menembak endpoint tanpa membaca kode ekstensinya dulu.

---

## 📍 Di kode

| Apa | Lokasi |
|---|---|
| URL API di ekstensi | `extension/content.js:29-31` (`API_BASE`, `API_URL`, `BATCH_API_URL`) |
| Token laporan di ekstensi | `extension/content.js:34` (`REPORT_TOKEN`), dikirim di `extension/content.js:240` |
| URL API di popup | `extension/popup.js:8` |
| Domain yang diizinkan ekstensi akses | `extension/manifest.json:13` (`host_permissions`) |
| Public key untuk pin ID ekstensi | `extension/manifest.json:6` (`key`) |
| Pembatasan CORS di server | `src/server.py:69-73` (`allow_origins`) |
| Token wajib untuk `/report` | `src/server.py:93` (`REPORT_TOKEN`), dicek di `src/server.py:421` |
| Konfigurasi systemd | `deploy/judol-api.service` |
| Konfigurasi Nginx | `deploy/nginx-judol-api.conf` |
| Dependency minimal untuk server (bukan `requirements.txt` penuh) | `deploy/requirements-serve.txt` |

---

## 📄 Di skripsi

Sub-bab yang mengklaim deployment VPS (sebelumnya ditandai bermasalah di `08-daftar-kesalahan.md` finding ①, sekarang **sudah benar secara faktual**):

- Sub-bab 3 (batasan): "Server API di-deploy pada infrastruktur Virtual Private Server (VPS)..."
- Tahap Waterfall & alur pelatihan: "...untuk di-deploy ke VPS"
- 4.x Komponen Server: "di-deploy pada VPS berbasis Ubuntu Server 24.04 LTS dan dapat diakses melalui jaringan internet"
- 4.12 Kelayakan Teknologi: "VPS dengan spesifikasi minimum 2 vCPU, RAM 2 GB, penyimpanan 40 GB"

Semua angka spek itu sekarang **sesuai VPS yang beneran jalan** — tidak perlu direvisi.

---

## ❓ Kalau ditanya

**"Kenapa pakai VPS mentah, bukan platform managed seperti Heroku/Railway?"**
> "VPS memberi kontrol penuh atas environment-nya, Pak — penting karena model yang dipakai butuh versi scikit-learn yang persis sama dengan saat pelatihan. Platform managed juga sering mem-*'*tidur*'-kan aplikasi kalau idle di tier gratis, yang berisiko bikin cold-start lambat saat didemokan."

**"Apa itu reverse proxy dan kenapa dibutuhkan?"**
> "Nginx menerima trafik HTTPS dari internet dan meneruskannya ke aplikasi Python yang jalan di port internal. Ini memisahkan urusan sertifikat SSL dari logika aplikasi, dan aplikasi Python-nya sendiri tidak pernah langsung terekspos ke internet."

**"Kenapa CORS dibatasi, bukan `*` (semua origin) saja?"**
> "Kalau `allow_origins` dibiarkan `*`, situs web mana pun bisa memanggil API ini langsung dari browser pengunjungnya. Saya batasi ke domain ekstensi ini plus YouTube — sesuai `host_permissions` yang memang cuma situs itu yang didukung ekstensinya."

**"Bagaimana kalau server di VPS mati pas sidang?"**
> "Prosesnya dikelola `systemd` dengan `Restart=on-failure`, jadi kalau crash dia otomatis nyala lagi. Tapi kalau memang seluruh VPS atau koneksi internet ruangan bermasalah, saya juga tetap bisa menjalankan server yang sama secara lokal sebagai cadangan — arsitekturnya identik, cuma beda alamat."

**"Apa risiko keamanan yang dipertimbangkan?"**
> "Tiga hal, Pak: pertama, CORS dibatasi supaya bukan sembarang situs bisa memanggil API. Kedua, komunikasinya HTTPS supaya tidak bisa disadap di jaringan publik. Ketiga, endpoint `/report` — yang menulis ke dataset pelatihan — saya kunci dengan token supaya tidak bisa disalahgunakan orang luar untuk meracuni data pelatihan (*data poisoning*)."

---

## Kalau ada masalah

| Gejala | Kemungkinan penyebab | Solusi |
|---|---|---|
| Ekstensi tidak connect ke server | VPS mati / systemd berhenti | SSH masuk, `sudo systemctl status judol-api` |
| Galat CORS di konsol browser, sumbernya `content.js` | Origin dari content script itu URL halaman (`youtube.com`), bukan `chrome-extension://` | Pastikan `allow_origins` di `server.py` juga memuat `https://www.youtube.com`, bukan cuma ID ekstensi |
| Sertifikat HTTPS expired | Certbot renewal gagal jalan | `sudo certbot renew --dry-run` untuk cek, lalu `sudo certbot renew` |
| ID ekstensi berubah setelah reinstall di device lain | Field `"key"` hilang dari `manifest.json` yang dipakai | Pastikan `manifest.json` yang dimuat masih punya field `key` yang sama |
| `/report` selalu balas 401 | Token di `content.js` dan `server.py` tidak sama | Bandingkan `REPORT_TOKEN` di kedua file, harus identik |
