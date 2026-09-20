# Ekstensi Chrome

Ekstensi memakai **Manifest V3**, standar yang berlaku untuk ekstensi Chrome
saat ini. Seluruh penyaringan terjadi di sisi klien, karena pihak ketiga tidak
punya akses ke server YouTube. Konsekuensinya, tidak ada data YouTube yang
diubah dan tidak ada beban tambahan pada servernya.

## Berkas

| Berkas | Peran |
|---|---|
| [`manifest.json`](../extension/manifest.json) | Izin, pencocokan URL, dan pendaftaran content script |
| [`content.js`](../extension/content.js) | Disuntikkan ke halaman YouTube, membaca dan menyembunyikan komentar |
| [`popup.js`](../extension/popup.js) | Panel pengaturan yang muncul saat ikon ekstensi diklik |
| [`popup.html`](../extension/popup.html) | Tampilan panel pengaturan |

## Izin yang diminta

```json
"permissions": ["storage"],
"host_permissions": [
  "https://api-svm.cupsky.my.id/*",
  "https://www.youtube.com/*"
]
```

Hanya `storage`, dipakai untuk menyimpan preferensi pengguna. Ekstensi tidak
meminta akses riwayat, tab, maupun identitas.

## Alur kerja

1. Saat halaman YouTube dimuat, `content.js` memeriksa `GET /health` untuk
   memastikan server siap.
2. Komentar yang terlihat dikumpulkan dari DOM, lalu dikirim ke
   `POST /predict/batch` dalam kelompok maksimal 50 teks per permintaan.
3. Komentar yang diklasifikasikan spam dengan kepercayaan di atas ambang akan
   disembunyikan sesuai mode yang dipilih pengguna.
4. `MutationObserver` memantau penambahan node baru, sehingga komentar yang
   muncul saat pengguna menggulir ikut diproses.

Elemen yang sudah diproses dicatat agar tidak dikirim dua kali.

Pengiriman dilakukan per kelompok, bukan satu permintaan per komentar, supaya
satu halaman komentar selesai dalam satu perjalanan jaringan. Saat terjadi
kegagalan jaringan, pemeriksaan kesehatan server dipicu ulang sehingga
pemindaian berikutnya tidak terus mencoba menghubungi server yang mati.

## Mode penyembunyian

Pengguna memilih salah satu dari dua mode lewat panel pengaturan.

**Redupkan.** Komentar tetap berada di DOM dengan opasitas rendah dan diberi
lencana kecil bertuliskan tingkat kepercayaan. Lencana itu bisa diklik untuk
menampilkan kembali komentarnya. Mode ini bawaan karena keputusan model tetap
bisa ditinjau pengguna.

**Hilangkan.** Komentar disembunyikan sepenuhnya tanpa lencana.

## Ambang kepercayaan

Nilai bawaannya 0,75 dan bisa diatur lewat penggeser di panel pengaturan pada
rentang 50% sampai 95%. Perubahannya tersimpan di `chrome.storage` dan langsung
berlaku tanpa memuat ulang halaman.

Ambang ini ada karena keseimbangan antara komentar yang lolos dan komentar sah
yang ikut tersembunyi bersifat subjektif. Menaikkannya membuat ekstensi lebih
konservatif, menurunkannya membuatnya lebih agresif.

## Penghitung statistik

Jumlah komentar yang dipindai dan disembunyikan disimpan di memori tab yang
bersangkutan, bukan di `chrome.storage`. Penyimpanan itu dipakai bersama oleh
semua tab, sehingga tab mana pun yang menulis ke sana akan menimpa angka milik
tab lain. Panel pengaturan menanyakan angkanya langsung ke tab yang sedang
aktif.

## ID ekstensi yang dipatok

`manifest.json` memuat medan `key` berisi kunci publik RSA.

Untuk ekstensi yang dimuat lewat Load unpacked, Chrome biasanya menghitung ID
ekstensi dari lokasi foldernya di disk. Artinya ID berubah jika ekstensi dimuat
dari komputer atau folder yang berbeda. Karena server membatasi CORS
berdasarkan ID tersebut, perubahan ID membuat semua permintaan ditolak.

Dengan medan `key`, Chrome menghitung ID secara deterministik dari kunci itu,
sehingga ID-nya tetap sama di komputer mana pun selama `manifest.json` yang
dipakai sama.

## Endpoint pelaporan

Terdapat tombol untuk menandai komentar yang salah disembunyikan, yang
mengirim teksnya ke `POST /report`. Tombol ini hanya muncul saat `DEV_MODE`
bernilai `true` di `content.js`, dan nilai itu tidak dibaca dari
`chrome.storage` sehingga pengguna akhir tidak punya cara mengaktifkannya.

Konstanta `REPORT_TOKEN` di `content.js` sengaja dibiarkan kosong. Berkas ini
ikut terdistribusi ke setiap pengguna dan bisa dibaca siapa pun yang membongkar
ekstensinya, sehingga token yang ditulis di sini tidak memberi perlindungan
apa pun. Untuk mengumpulkan koreksi secara lokal, isi nilainya di salinan
kerja sendiri tanpa ikut diversikan.
