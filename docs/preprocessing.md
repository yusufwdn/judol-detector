# Normalisasi Teks

Seluruh pembersihan teks dilakukan oleh `clean_text()` di
[`src/preprocessing.py`](../src/preprocessing.py). Modul ini dipakai bersama
oleh pelatihan dan prediksi, sehingga keduanya selalu menerima masukan dalam
bentuk yang sama. Alasan keputusan itu ada di
[arsitektur.md](arsitektur.md#kenapa-normalisasi-dilakukan-di-python).

Sebagian besar tahapan di bawah ada karena satu alasan praktis: spammer judi
online rutin menyamarkan tulisan agar lolos penyaringan berbasis kata kunci.
Normalisasi mengembalikan teks yang disamarkan itu ke bentuk kanonik sebelum
diubah menjadi fitur.

## Urutan tahapan

Urutannya tidak bisa ditukar. Beberapa tahap bergantung pada hasil tahap
sebelumnya, dan satu tahap khususnya harus berjalan sebelum digit dihapus.

| Tahap | Yang dilakukan | Contoh |
|---|---|---|
| 1 | Membuang karakter tak terlihat (zero-width) | Karakter sisipan yang memecah satu kata menjadi banyak token |
| 2 | Normalisasi Unicode NFKC | `𝑅𝒪𝑀𝒜` menjadi `ROMA`, `Ｄ` menjadi `D` |
| 2b | Membuang tanda diakritik penggabung | `P͟U͟L͟A͟U͟` menjadi `PULAU` |
| 2c | Membuka karakter yang dibungkus kurung | `[P][U][L][A][U]` menjadi `PULAU` |
| 3 | Substitusi homoglif Sirilik, Yunani, dan Thai | Huruf mirip dari aksara lain menjadi padanan Latinnya |
| 4 | Mengubah emoji menjadi token teks | 🎰 menjadi `slot_machine` |
| 5 | Huruf kecil semua | `Daftar` dan `daftar` menjadi token yang sama |
| 5b-i | Normalisasi leet speak | `H0KI777` menjadi `HOKI777` |
| 5b | Kanonikalisasi nama situs | `keju4d`, `hobiqq` menjadi `judolbrand` |
| 6 | Membuang URL dan karakter non-alfabet | Digit dan tanda baca hilang |
| 7 | Membuang stopword dan token satu huruf | Kata umum seperti `yang`, `di` dihilangkan |

## Tahap yang perlu penjelasan tambahan

### Kenapa NFKC saja tidak cukup

NFKC merapikan variasi dekoratif dalam satu aksara, misalnya huruf tebal
matematis atau huruf lebar penuh, menjadi padanan ASCII-nya. Yang tidak bisa
dilakukannya adalah melintasi batas aksara. Huruf Sirilik `а` terlihat persis
seperti `a` Latin tetapi merupakan karakter yang sepenuhnya berbeda, dan NFKC
membiarkannya apa adanya. Tahap 3 menangani kasus itu lewat pemetaan homoglif
yang disusun manual.

### Kenapa emoji tidak dibuang

Emoji membawa sinyal, bukan derau. Lambang mesin slot dan uang sering muncul
di komentar promosi, sementara jempol cenderung netral. Membuang emoji berarti
membuang informasi itu. Dengan mengubahnya menjadi token teks, model belajar
sendiri bahwa `slot_machine` berkorelasi dengan spam, tanpa aturan manual.

### Kenapa kanonikalisasi nama situs harus sebelum tahap 6

Hampir semua nama situs judi online di Indonesia mengikuti pola nama bebas
ditambah akhiran khas, entah numerik seperti `4D`, `88`, `777`, atau kata
seperti `QQ`.

Tahap 6 membuang semua digit. Tanpa penanganan khusus, `keju4d` akan menjadi
`keju`, yang merupakan kata makanan biasa dan justru menyesatkan model.

Karena itu, sebelum digit dibuang, pola nama situs dideteksi dan diganti
dengan satu token universal `judolbrand`. Satu token ini menggantikan
kebutuhan mendaftarkan setiap nama situs satu per satu, sehingga situs baru
yang mengikuti pola yang sama tetap tertangkap tanpa perlu memperbarui daftar.

Normalisasi leet speak dijalankan tepat sebelumnya agar nama yang memakai
angka sebagai pengganti huruf, seperti `H0KI777`, ikut cocok dengan pola
tersebut.

Keterbatasan pendekatan ini dibahas di
[evaluasi.md](evaluasi.md#keterbatasan).

## Daftar stopword

Daftar stopword bahasa Indonesia didefinisikan langsung di
`preprocessing.py` sebagai `STOPWORDS_ID`, bukan diambil dari pustaka luar,
supaya isinya bisa ditinjau dan diubah tanpa ketergantungan tambahan.

Stopword khusus domain seperti sapaan `kak`, `bang`, dan `min` sempat
dipertimbangkan tetapi tidak jadi ditambahkan. Inspeksi bobot fitur
menunjukkan `bang` dan `dok` justru merupakan penanda non-spam yang kuat,
dengan bobot negatif masing-masing 1,55 dan 1,39, sehingga membuangnya
kemungkinan besar menurunkan performa. Lihat
[roadmap.md](roadmap.md).

## Menguji sendiri

`preprocessing.py` bisa dijalankan langsung untuk melihat hasil normalisasi
pada sejumlah kasus uji yang sudah disiapkan, termasuk contoh penyamaran nyata
yang ditemukan selama pengumpulan data:

```bash
python src/preprocessing.py
```
