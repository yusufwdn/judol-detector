# Panduan Langkah demi Langkah — Publikasi Chrome Web Store

Versi rinci dari checklist. Ditulis untuk dikerjakan sambil dibuka.

---

# LANGKAH 1 — Menaruh kebijakan privasi di internet ("deploy")

## Apa maksudnya dan kenapa perlu

Google akan menanyakan **URL kebijakan privasi** saat Anda mendaftarkan ekstensi.
Mereka benar-benar membukanya untuk diperiksa. Saat ini file
`deploy/privacy-policy.html` masih ada **di laptop Anda saja** — tidak ada orang lain
di internet yang bisa membukanya, termasuk Google.

"Deploy" di sini artinya sesederhana: **memindahkan file itu ke server yang sudah online,
supaya punya alamat yang bisa dibuka siapa saja.**

Analoginya: file itu sekarang seperti dokumen di laci meja Anda. Google minta alamat
supaya bisa datang membacanya. Jadi dokumennya harus dipindah ke tempat yang punya alamat.

Kabar baiknya, **server dan domain Anda sudah ada dan sudah hidup** — yang dipakai API
(`api-svm.cupsky.my.id`). Jadi tinggal menumpang di situ, tidak perlu beli apa pun.

Hasil akhir: `https://api-svm.cupsky.my.id/privacy` bisa dibuka siapa saja.

## Cara A — Lewat FastAPI yang sudah berjalan (disarankan)

**Tidak perlu menyentuh Nginx sama sekali.** Halaman privasi sekarang dilayani
langsung oleh aplikasi FastAPI lewat route `@app.get("/privacy")` di `src/server.py`.
Karena Nginx sudah mem-proxy seluruh `location /` ke aplikasi, alamat
`https://api-svm.cupsky.my.id/privacy` otomatis ikut jalan.

Keuntungannya untuk susunan server Anda (aplikasi berada di `/home/deploy/svm-judol-spam`,
bukan di `/var/www`):
- tidak perlu membuat direktori `/var/www`
- tidak ada masalah izin akses — Nginx tidak perlu membaca isi direktori home
- file kebijakan ikut ter-deploy bersama kode lewat `git pull` yang sama

Sudah diuji lokal: `GET /privacy` → **200**, `content-type: text/html`.

### A1. Kirim perubahan dari laptop

Ada dua berkas yang berubah: `src/server.py` (route baru) dan
`deploy/privacy-policy.html` (halamannya).

```bash
git add src/server.py deploy/privacy-policy.html deploy/nginx-judol-api.conf
git commit -m "feat: serve privacy policy page for Chrome Web Store submission"
git push origin main
```

### A2. Tarik perubahan di server

```bash
ssh deploy@IP_VPS
cd /home/deploy/svm-judol-spam
git pull origin main
sudo systemctl restart judol-api
sudo systemctl status judol-api     # pastikan "active (running)"
```

> **Kalau server bukan hasil git clone** (misalnya dulu diunggah manual), lewati
> `git pull` dan kirim berkasnya langsung dari laptop:
> ```bash
> scp src/server.py deploy/privacy-policy.html \
>     deploy@IP_VPS:/home/deploy/svm-judol-spam/
> ```
> Perhatikan tujuannya: `server.py` harus masuk ke subfolder `src/`, dan
> `privacy-policy.html` ke subfolder `deploy/`. Setelah itu tetap jalankan
> `sudo systemctl restart judol-api`.

### A3. Pastikan berhasil

```bash
curl -I https://api-svm.cupsky.my.id/privacy      # harus HTTP/2 200
curl -s https://api-svm.cupsky.my.id/health       # pastikan API tetap normal
```

Lalu buka di browser: **https://api-svm.cupsky.my.id/privacy** —
harus muncul halaman "Kebijakan Privasi — Judol Spam Detector".

Kalau muncul **404**, berarti `server.py` di server belum yang terbaru atau
layanan belum di-restart. Kalau muncul **502**, aplikasi gagal start —
periksa dengan `sudo journalctl -u judol-api -n 50`.

## Cara B — Kalau akses VPS bermasalah (cadangan, 5 menit)

Pakai GitHub Pages, gratis dan tidak menyentuh server:

1. Buat repository publik baru di GitHub, misal `judol-privacy`
2. Unggah `privacy-policy.html`, **ganti namanya jadi `index.html`**
3. Buka **Settings → Pages**, pada Source pilih branch `main`, folder `/ (root)`, Save
4. Tunggu 1–2 menit. URL Anda jadi:
   `https://USERNAME.github.io/judol-privacy/`
5. Pakai URL itu di form Google

Sama sahnya. Cara A lebih rapi karena satu domain dengan API-nya, tapi kalau mepet
waktu, Cara B tidak apa-apa.

---

# LANGKAH 2 — Menguji ekstensi sebelum diunggah

Wajib, karena permission `activeTab` baru saja dihapus. Sekali saja, 2 menit.

1. Buka Chrome → ketik `chrome://extensions` di address bar → Enter
2. Nyalakan **Developer mode** (sakelar di kanan atas)
3. Klik **Load unpacked**
4. Pilih folder: `svm-judol-spam/dist/store`
5. Buka video YouTube Indonesia yang komentarnya banyak spam judol
6. Periksa tiga hal:
   - [ ] Komentar spam benar-benar diredupkan/disembunyikan
   - [ ] Klik ikon ekstensi → popup terbuka, **penghitung menunjukkan angka** (bukan 0 atau kosong)
   - [ ] Geser slider ambang keyakinan → tampilan komentar berubah

## Uji khusus: dua tab sekaligus (penting)

Ini menguji langsung bug lama "ekstensi tidak jalan di dua tab" — sekaligus membuktikan
penghapusan `activeTab` tidak merusak apa pun.

1. Buka **video YouTube A** di satu tab, tunggu komentar tersaring
2. Buka **video YouTube B** yang berbeda di tab lain, tunggu tersaring juga
3. Kembali ke **tab A** → klik ikon ekstensi → **catat angkanya**
4. Pindah ke **tab B** → klik ikon ekstensi → **catat angkanya**

**Hasil yang benar:** angka di tab A dan tab B **berbeda**, dan masing-masing sesuai
dengan komentar yang tersaring di tab itu sendiri. Angka tab A tidak berubah setelah
tab B ikut memindai.

**Kalau ternyata angkanya sama, atau salah satu jadi 0** — beri tahu saya, `activeTab`
akan saya kembalikan. Tapi berdasarkan pembacaan kode, ini seharusnya tetap berfungsi:
isolasi per-tab berasal dari `persistStats()` yang dikosongkan (`content.js:336`) dan
listener `getStats` (`content.js:459`), bukan dari permission `activeTab`.

---

# LANGKAH 3 — Membuat screenshot

## Kenapa perlu

Dua alasan sekaligus:
1. **Google mewajibkan** minimal 1 screenshot untuk halaman toko. Tanpa itu tidak bisa submit.
2. **Penguji butuh bukti visual** bahwa sistemnya benar-benar jalan, bukan sekadar klaim.

Jadi sekali kerja, dipakai dua tempat.

## Ukuran

Harus **1280×800 piksel** (atau 640×400). Cara paling gampang mendapatkan ukuran persis:

1. Di Chrome tekan `F12` (DevTools terbuka)
2. Tekan `Ctrl+Shift+M` (mode perangkat/device toolbar)
3. Di bagian atas pilih **Responsive**, lalu ketik lebar `1280` dan tinggi `800`
4. Tekan `Ctrl+Shift+P`, ketik `screenshot`, pilih **"Capture screenshot"**

Hasilnya otomatis tersimpan dengan ukuran persis 1280×800, tidak perlu di-crop manual.

## Tiga screenshot yang dibuat

### Screenshot 1 — Perbandingan sebelum & sesudah
**Isi:** kolom komentar YouTube pada video yang sama, dalam dua kondisi.

Cara: buka video dengan banyak spam judol.
- Matikan ekstensi di `chrome://extensions` → refresh → **screenshot** (komentar spam terlihat semua)
- Nyalakan lagi → refresh → **screenshot** (komentar spam sudah tersaring)
- Gabungkan berdampingan pakai aplikasi apa saja (Paint, Canva, PowerPoint)

**Ini screenshot paling penting.** Paling langsung menunjukkan hasil kerja sistem —
untuk calon pengguna maupun untuk penguji.

### Screenshot 2 — Popup ekstensi
**Isi:** popup terbuka, dengan terlihat jelas:
- Slider ambang keyakinan
- Pilihan mode (Redupkan / Hilangkan)
- Penghitung komentar tersaring yang **menunjukkan angka nyata** (jangan 0)
- Indikator status server yang terhubung

Ini menunjukkan pengguna punya kendali, bukan sistem kotak hitam.

### Screenshot 3 — Detail mode Redupkan
**Isi:** perbesar satu komentar spam yang sedang diredupkan, beserta badge-nya.

Menunjukkan sistem tidak menghapus paksa, tapi tetap memberi pengguna pilihan untuk
melihat. Ini poin bagus untuk pertanyaan "bagaimana kalau salah deteksi?"

## Simpan di mana

Buat folder `svm-judol-spam/reports/screenshots-store/` dan simpan semuanya di situ,
supaya gampang dipanggil lagi saat menyusun naskah revisi.

---

# LANGKAH 4 — Submit dan mengabadikan buktinya

## Apa itu "dashboard"

Setelah membayar USD 5 dan mendaftar, Anda mendapat akses ke
**Chrome Web Store Developer Dashboard** — halaman kendali milik pengembang di
https://chrome.google.com/webstore/devconsole

Isinya adalah daftar semua ekstensi Anda, lengkap dengan statusnya. Mirip halaman
"pesanan saya" di toko online: setiap ekstensi punya baris sendiri dengan status
yang berubah seiring proses.

## Apa itu "Item ID"

Setiap ekstensi yang diunggah mendapat **kode unik 32 huruf** dari Google, misalnya:

```
mhjfbmdgcfjbbpaeojofohoefgiehjai
```

Itulah Item ID — nomor identitas resmi ekstensi Anda di sistem Google. Kode ini
juga yang nanti muncul di URL toko:
`https://chromewebstore.google.com/detail/mhjfbmdgcfjbbpaeojofohoefgiehjai`

Letaknya: di dashboard, klik ekstensi Anda, lalu lihat di bawah judul atau di URL
address bar. Bisa juga dari menu **Package**.

## Apa itu "status"

Status menunjukkan sedang di tahap mana ekstensi Anda:

| Status | Artinya |
|---|---|
| **Draft** | Belum disubmit. Google belum melihat apa pun. |
| **Pending review** | Sudah disubmit, sedang diperiksa tim Google. |
| **Published** | Lolos. Sudah bisa dipasang siapa saja dari toko. |
| **Rejected** | Ditolak, disertai alasan yang bisa diperbaiki lalu submit ulang. |

## Kenapa harus di-screenshot

**Ini inti persoalannya untuk Dosen 2.**

Beliau mempertanyakan bagaimana masyarakat bisa memakai sistem Anda kalau masih lokal.
Kalau approval Google **belum turun** sebelum deadline revisi, Anda tidak punya URL toko
untuk ditunjukkan — dan tanpa bukti, pernyataan "sudah saya submit kok" hanyalah klaim
lisan, persis jenis klaim tanpa bukti yang beliau permasalahkan sejak awal.

Screenshot dashboard adalah buktinya. Yang harus terlihat dalam satu gambar:

- [ ] Nama ekstensi: **Judol Spam Detector**
- [ ] **Item ID** (kode 32 huruf itu)
- [ ] **Status**: "Pending review" atau "Published"
- [ ] **Tanggal submit**, kalau ditampilkan

Dengan itu, kalimat di naskah Anda berubah dari klaim menjadi fakta terverifikasi:

> "Ekstensi telah diajukan ke Chrome Web Store pada [tanggal] dengan Item ID [kode]
> dan berstatus menunggu peninjauan, sebagaimana ditunjukkan pada Gambar 4.x."

Penguji bisa mengecek sendiri. Itu yang membedakannya dari "keresahan masyarakat sekitar"
yang kemarin dipertanyakan.

## Catat di sini setelah submit

```
Item ID       : ______________________________
Tanggal submit: ______________________________
Jam submit    : ______________________________
Status        : ______________________________
Berkas bukti  : reports/screenshots-store/dashboard-submit.png
```

---

# Ringkasan urutan

| Urutan | Langkah | Perkiraan waktu | Bisa dilewati? |
|---|---|---|---|
| 1 | Deploy kebijakan privasi | 15 menit | ❌ URL-nya diminta di form |
| 2 | Tes Load unpacked | 2 menit | ❌ `activeTab` baru dihapus |
| 3 | Buat 3 screenshot | 30 menit | ❌ minimal 1 diwajibkan |
| 4 | Daftar + bayar USD 5 | 15 menit | ❌ |
| 5 | Isi form + submit | 30 menit | ❌ teksnya sudah disiapkan di checklist |
| 6 | Screenshot dashboard | 2 menit | ❌ ini bukti untuk penguji |

**Total sekitar 1,5 jam.** Kerjakan sekaligus dalam satu duduk hari ini —
jam peninjauan Google baru mulai berjalan begitu Anda menekan submit, dan durasinya
tidak bisa dikendalikan.
