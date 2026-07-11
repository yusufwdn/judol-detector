# BAB II — LANDASAN TEORI (Draft Lengkap Revisi)

> **Catatan penggunaan:**
> - File ini adalah teks lengkap BAB II yang sudah mencakup: (a) teks asli yang dipertahankan, (b) kalimat kesimpulan baru di tiap sub-bab (dosen poin 4, pembukanya divariasikan), (c) restrukturisasi 2.5.1 / 2.6.1 / 2.8, dan (d) perbaikan referensi silang "Bab 3" → "Bab 4".
> - **Italic istilah asing (dosen poin 2) BELUM diterapkan di sini** — itu tahap manual terpisah (poin 9 di TODO). Sengaja teks dibiarkan polos biar gampang di-copas; italic-kan di Word setelah tempel.
> - Rumus matematika ditulis sebagai teks biasa — bangun ulang pakai Equation Editor Word setelah tempel.
> - Penanda `[GAMBAR ...]` = posisi gambar yang sudah ada di draft, jangan dihapus.

---

## 2.1 Pemrosesan Bahasa Alami (Natural Language Processing)

Natural Language Processing (NLP) merupakan cabang dari kecerdasan buatan (Artificial Intelligence) yang secara spesifik berfokus pada interaksi antara sistem komputer dan bahasa manusia. Teknologi ini dirancang agar komputer memiliki kemampuan untuk mengolah, memahami, menginterpretasikan, hingga menganalisis makna dari data teks atau bahasa alami secara efektif (Oktavia, 2024). Melalui pendekatan NLP, pemrosesan informasi dari opini atau teks masukan berskala besar dapat diekstraksi menjadi sebuah pengetahuan dan kesimpulan yang valid untuk kebutuhan analisis lanjutan (Pratama, 2026).

Namun, tantangan terbesar dalam penerapan NLP pada data media sosial adalah karakteristik teks yang sangat dinamis dan tidak terstruktur. Komentar pada platform seperti YouTube sering kali dipenuhi dengan variasi bahasa yang tidak baku, penggunaan slang (bahasa gaul), singkatan, hingga manipulasi teks (obfuscation). Dalam kondisi ini, kualitas tahap prapemrosesan teks (text preprocessing) secara langsung memengaruhi tingkat akurasi klasifikasi. Tanpa adanya prapemrosesan dan normalisasi yang memadai, sistem tidak akan mampu mengenali karakter yang telah dimanipulasi oleh pengguna (Khairunnisa & Adiwijaya, 2021).

Tahapan prapemrosesan ini sangat krusial dalam mengubah data teks yang kotor menjadi representasi numerik yang valid untuk diproses oleh algoritma Machine Learning seperti Support Vector Machine (SVM). Oleh karena itu, penerapan teknik NLP yang presisi menjadi fondasi mutlak dalam menangani dataset dengan tingkat noise yang tinggi, memastikan algoritma tidak gagal saat mengekstraksi fitur teks dari komentar yang tidak baku.

Dengan demikian, Natural Language Processing dapat dipahami sebagai fondasi teoritis yang esensial dalam penelitian ini, karena kemampuannya mengolah dan menginterpretasikan teks berbahasa alami menjadi dasar bagi seluruh tahapan pemrosesan komentar YouTube yang bersifat dinamis, tidak baku, dan rawan dimanipulasi, sebelum data tersebut dapat diklasifikasikan oleh algoritma Machine Learning.

## 2.2 Prapemrosesan Teks (Text Preprocessing)

Prapemrosesan teks merupakan tahap awal yang krusial dalam pipeline Natural Language Processing sebelum data teks dapat diproses oleh algoritma Machine Learning. Tujuan utama dari tahap ini adalah mengubah teks mentah yang tidak terstruktur dan penuh noise menjadi representasi yang bersih dan seragam sehingga algoritma ekstraksi fitur dapat bekerja secara optimal (Khairunnisa dkk., 2021). Tantangan prapemrosesan menjadi lebih kompleks pada data teks media sosial seperti komentar YouTube, yang sering mengandung singkatan tidak standar, bahasa gaul, dan manipulasi karakter yang disengaja untuk menghindari moderasi otomatis. Kondisi ini mengharuskan pipeline prapemrosesan yang lebih komprehensif dibandingkan teks formal.

Tahapan prapemrosesan teks umumnya meliputi case folding untuk menyeragamkan kapitalisasi, normalisasi Unicode untuk mengonversi karakter dekoratif atau manipulatif ke bentuk standar, konversi emoji menjadi token teks yang informatif, penghapusan karakter tidak relevan seperti URL dan simbol, serta penghapusan stopword untuk mereduksi kata-kata fungsional yang tidak memiliki nilai diskriminatif. Dalam konteks deteksi spam judi online, dua tahap tambahan juga relevan: normalisasi leet speak yang mengonversi penggantian huruf dengan angka seperti "s1tus" kembali menjadi "situs", dan kanonisasi nama brand yang menyeragamkan pola penamaan situs judi online menjadi satu token representatif.

Hasil akhir dari seluruh tahapan ini adalah teks yang bersih dan siap diproses pada tahap ekstraksi fitur. Penjelasan teknis mengenai implementasi setiap tahap dibahas lebih lanjut pada Bab 4.

Uraian tersebut menegaskan bahwa tahap prapemrosesan teks merupakan langkah yang tidak dapat diabaikan dalam pipeline klasifikasi, sebab kualitas representasi teks yang dihasilkan pada tahap ini secara langsung menentukan efektivitas algoritma ekstraksi fitur dan klasifikasi pada tahap berikutnya, terutama ketika berhadapan dengan data komentar media sosial yang penuh noise dan manipulasi karakter.

## 2.3 Stemming Bahasa Indonesia (Sastrawi)

Stemming adalah proses mengubah kata berimbuhan menjadi kata dasarnya dengan menghilangkan imbuhan yang melekat, sehingga kata-kata yang secara semantis sama namun berbeda bentuk morfologisnya dapat dikenali sebagai satu entitas yang identik oleh model klasifikasi (Sinaga & Nainggolan, 2023). Bahasa Indonesia memiliki sistem afiksasi yang kompleks mencakup awalan, akhiran, sisipan, dan kombinasi keduanya, sehingga dibutuhkan algoritma stemming yang dirancang khusus untuk kaidah morfologi bahasa Indonesia.

Sastrawi adalah pustaka Python yang mengimplementasikan algoritma Nazief-Adriani dengan kamus kata dasar bahasa Indonesia. Algoritma ini secara iteratif mencoba melepaskan imbuhan hingga ditemukan kata dasar yang valid, dan telah terbukti mencapai akurasi rata-rata 97,73% pada dokumen teks berbahasa Indonesia (Sinaga & Nainggolan, 2023). Meskipun demikian, efektivitas stemming pada teks komentar media sosial yang pendek dan informal tidak selalu menghasilkan peningkatan performa yang signifikan dibandingkan teks formal. Pertimbangan empiris mengenai penerapan stemming dalam penelitian ini dibahas pada Bab 4.

Merujuk pada penjelasan di atas, terlihat bahwa meskipun algoritma stemming Nazief-Adriani melalui pustaka Sastrawi terbukti akurat pada dokumen teks formal berbahasa Indonesia, efektivitasnya tidak dapat diasumsikan berlaku sama pada teks komentar media sosial yang pendek dan informal, sehingga keputusan penerapannya dalam penelitian ini perlu didasarkan pada pengujian empiris, bukan sekadar asumsi teoritis.

## 2.4 String Normalization dan Penanganan Obfuscation

String Normalization adalah teknik krusial dalam prapemrosesan teks yang bertujuan untuk menangani anomali penulisan atau penyamaran teks (obfuscation). Secara lengkap, obfuscation merupakan teknik penyamaran kata dengan cara memodifikasi karakter, seperti penggantian huruf dengan angka atau simbol (contohnya penggunaan homoglyphs atau variasi font Unicode khusus), yang bertujuan untuk menghindari sistem deteksi otomatis. Teknik obfuscation seperti substitusi karakter ini membuat sistem filtrasi berbasis kata kunci (keyword-based filtering) konvensional menjadi tidak efektif, khususnya dalam menangkal penyebaran promosi judi online di platform YouTube (Angelo dkk., 2025).

Dalam pemrosesan klasifikasi berbasis Machine Learning, tingkat akurasi sangat bergantung pada konsistensi kamus data (vocabulary). Apabila data mentah dipenuhi dengan noise atau karakter manipulatif, algoritma akan mengalami penurunan performa secara drastis. Jika proses prapemrosesan dan normalisasi teks tidak dilakukan secara maksimal, kinerja metode klasifikasi apa pun tidak akan cukup kuat dalam menentukan kelas kata karena kamus sistem akan menganggap karakter manipulatif tersebut sebagai kosakata baru yang tidak memiliki makna (Abdillah dkk., 2021).

Oleh karena itu, String Normalization berfungsi sebagai lapisan pembersih yang menyetarakan dan memetakan kembali berbagai variasi karakter Unicode manipulatif tersebut ke dalam bentuk teks ASCII standar. Melalui tahapan normalisasi ini, karakter teks yang telah diobfuskasi dikembalikan ke bentuk aslinya, sehingga mencegah kegagalan algoritma klasifikasi akibat ketidakmampuan mesin dalam membaca teks spam yang dimanipulasi.

Salah satu fondasi dari proses normalisasi ini adalah standar Unicode Normalization Form, khususnya bentuk NFKC (Normalization Form Compatibility Composition). NFKC bekerja dengan mengurai karakter dekoratif atau varian bentuk (seperti huruf dengan gaya bold, italic, atau lebar penuh/full-width) menjadi karakter kanonik yang setara, lalu menyusunnya kembali ke bentuk baku. Dengan standar ini, beragam variasi visual dari sebuah huruf yang secara makna identik dapat disatukan menjadi satu representasi standar, sehingga model tidak memperlakukannya sebagai karakter yang berbeda-beda.

Secara umum, teknik obfuscation yang perlu ditangani oleh String Normalization dapat dikelompokkan ke dalam beberapa kategori. Pertama, substitusi karakter dengan bentuk serupa (homoglyph substitution), yaitu penggantian huruf Latin dengan karakter dari blok Unicode lain yang secara visual identik namun berbeda secara biner, seperti huruf Cyrillic atau Yunani. Kedua, penyisipan tanda diakritik gabungan (combining diacritical marks) di antara huruf-huruf sebuah kata untuk memecah pola pencocokan. Ketiga, pemisahan huruf menggunakan tanda baca atau tanda kurung (character separation), yang memecah satu kata menjadi rangkaian karakter tunggal yang terisolasi. Keempat, substitusi huruf dengan angka yang memiliki kemiripan visual (leet speak), seperti penggantian huruf "O" dengan angka "0". Kelima, variasi penamaan entitas atau brand yang terus berganti untuk menghindari pencocokan kata kunci statis, yang menuntut pendekatan kanonisasi (canonicalization) agar seluruh variasi tersebut dikenali sebagai satu entitas yang sama oleh model klasifikasi.

Dari pemaparan tersebut, dapat ditarik kesimpulan bahwa efektivitas String Normalization sangat bergantung pada kemampuannya menangani beragam kategori obfuscation secara berlapis, bukan hanya mengandalkan satu metode normalisasi tunggal, mengingat setiap kategori memerlukan pendekatan penanganan yang berbeda. Implementasi teknis dari setiap kategori pada sistem yang dibangun diuraikan lebih lanjut pada Bab 4.

## 2.5 Ekstraksi Fitur Term Frequency-Inverse Document Frequency

Ekstraksi fitur merupakan salah satu tahapan krusial dalam klasifikasi teks yang berfungsi untuk mengonversi data tekstual mentah menjadi bentuk representasi vektor numerik. Data komentar YouTube yang telah melalui tahap prapemrosesan dan normalisasi string tidak dapat diproses secara langsung oleh algoritma komputasi berbasis Machine Learning, karena sistem tersebut membutuhkan masukan (input) berupa matriks angka. Salah satu metode ekstraksi fitur yang umum digunakan dan terbukti efektif dalam klasifikasi teks berbahasa Indonesia adalah Term Frequency-Inverse Document Frequency (TF-IDF) (Arrayyan dkk., 2025).

Metode TF-IDF bekerja dengan cara memberikan pembobotan statistik pada setiap kata yang terdapat di dalam suatu dokumen atau komentar. Bobot ini dihitung berdasarkan dua metrik utama, yaitu seberapa sering sebuah kata muncul di dalam satu komentar spesifik (Term Frequency), dan seberapa langka atau umum kata tersebut jika dibandingkan dengan keseluruhan komentar yang ada di dalam himpunan data (Inverse Document Frequency). Dibandingkan metode representasi teks lain seperti Bag of Words (BoW), Doc2Vec, dan Word2Vec, TF-IDF secara konsisten menunjukkan performa kompetitif ketika dikombinasikan dengan algoritma machine learning seperti SVM (Efrizoni dkk., 2022).

Secara matematis, kalkulasi nilai TF-IDF diformulasikan dalam persamaan berikut:

    W(t,d) = tf(t,d) × idf(t)

Nilai idf(t) sendiri didapatkan melalui perhitungan logaritmik dengan persamaan:

    idf(t) = log ( N / df(t) )

Keterangan variabel:

1. W(t,d) (Bobot Akhir): Merupakan nilai metrik akhir dari sebuah kata (t) di dalam satu komentar tertentu (d). Semakin tinggi nilai ini, berarti kata tersebut semakin penting dan menjadi ciri khas kuat dari komentar tersebut.
2. tf(t,d) (Term Frequency): Merupakan jumlah atau frekuensi kemunculan kata (t) di dalam satu komentar (d). Jika kata "slot" muncul 3 kali dalam satu kalimat komentar, maka nilai tf untuk kata tersebut adalah 3.
3. N (Total Dokumen): Merupakan jumlah keseluruhan komentar YouTube yang ada di dalam dataset latih.
4. df(t) (Document Frequency): Merupakan jumlah komentar (dari total N) yang mengandung kata (t). Jika ada 10.000 komentar, dan kata "slot" muncul di 500 komentar, maka nilai df adalah 500.

Sebagai ilustrasi bagaimana TF-IDF menyaring kata-kata spam perjudian, asumsikan bahwa terdapat sebuah dataset mini yang hanya berisi 3 komentar YouTube (N = 3):

1. Komentar 1 (d1): "link slot paling gacor hari ini"
2. Komentar 2 (d2): "video edukasi ini sangat bermanfaat"
3. Komentar 3 (d3): "depo slot anti rungkad di sini"

Sistem akan menghitung bobot untuk kata target, misalnya kata "slot" pada Komentar 1 (d1):

1. Hitung TF (tf): Kata "slot" muncul sebanyak 1 kali di Komentar 1, maka variabel tf = 1.
2. Hitung IDF (idf): Total komentar (N) adalah 3. Kata "slot" muncul di 2 komentar (1 dan 3), maka df = 2. Nilai idf = log(3/2) = log(1.5) ≈ 0.176.
3. Hitung Bobot Akhir (W): W = 1 × 0.176 = 0.176, yang artinya kata "slot" pada Komentar 1 memiliki bobot 0.176.

Sebagai perbandingan, hitung juga kata hubung umum yang sering muncul seperti "ini" pada Komentar 1 (d1):

1. Hitung TF (tf): Kata "ini" muncul sebanyak 1 kali di Komentar 1, maka variabel tf = 1.
2. Hitung IDF (idf): Misalkan kata "ini" kebetulan muncul di seluruh komentar (Komentar 1, 2, dan 3), maka df = 3. Jadi nilai dari variabel idf = log(3/3) = log(1) = 0.
3. Hitung Bobot Akhir (W): W = 1 × 0 = 0. Kata "ini" memiliki bobot 0.

Dari perbandingan di atas, terbukti bahwa TF-IDF secara otomatis memberikan bobot 0 pada kata-kata umum yang muncul di semua konteks, dan memberikan bobot tinggi pada kata-kata spesifik yang menjadi ciri khas promosi judi online (seperti "slot" dan "gacor"). Hasil matriks bobot inilah yang kemudian menjadi variabel masukan utama bagi algoritma klasifikasi Support Vector Machine (SVM) (Ardiansyah dkk., 2025).

> **[GAMBAR 2.1: Contoh Matriks Bobot TF-IDF pada Komentar YouTube]**

Perlu dicatat bahwa formula yang dijelaskan di atas merupakan bentuk dasar TF-IDF yang digunakan untuk membangun pemahaman konseptual. Pada implementasi sistem dalam penelitian ini, TF-IDF diterapkan menggunakan pustaka Scikit-learn dengan beberapa penyesuaian parameter. Salah satunya adalah sublinear_tf=True, yaitu pengaturan yang membuat perhitungan Term Frequency tidak dihitung secara linear berdasarkan jumlah kemunculan kata apa adanya, melainkan diubah menggunakan fungsi logaritma menjadi 1 + log(tf). Tujuannya adalah untuk meredam dominasi kata yang muncul berulang kali dalam satu komentar, sehingga sebuah kata yang muncul 20 kali tidak dianggap 20 kali lebih penting dibandingkan kata yang hanya muncul sekali, melainkan hanya sedikit lebih penting. Selain itu, pustaka Scikit-learn secara bawaan (tanpa perlu diatur secara eksplisit) juga menerapkan teknik smoothing pada perhitungan IDF, yaitu menambahkan angka 1 pada pembilang dan penyebut rumus IDF. Tujuannya adalah untuk mencegah kemungkinan pembagian dengan angka nol apabila terdapat kata yang tidak muncul sama sekali pada data latih. Penjelasan lebih lanjut mengenai konfigurasi parameter ini beserta justifikasi pemilihannya dibahas secara rinci pada Bab 4.

Secara keseluruhan, pembahasan di atas menunjukkan bahwa TF-IDF merupakan metode ekstraksi fitur yang tepat digunakan dalam penelitian ini, karena kemampuannya memberi bobot lebih tinggi pada kata-kata yang menjadi penciri khas komentar promosi judi online, sekaligus menekan pengaruh kata-kata umum yang tidak informatif bagi proses klasifikasi.

### 2.5.1 N-gram

N-gram adalah teknik ekstraksi fitur dalam pemrosesan teks yang menghasilkan urutan berkesinambungan sebanyak n token dari sebuah teks. Setiap n-gram merepresentasikan satu unit fitur yang dapat digunakan sebagai masukan bagi algoritma klasifikasi. Ketika n bernilai 1, teknik ini disebut unigram dan setiap kata diperlakukan sebagai fitur tersendiri. Ketika n bernilai 2, disebut bigram dan setiap pasangan kata yang berurutan diperlakukan sebagai satu fitur. Ketika n bernilai 3, disebut trigram yang mencakup tiga kata berurutan sebagai satu unit fitur (Iriananda dkk., 2024).

Keunggulan utama penggunaan n-gram di atas unigram terletak pada kemampuannya menangkap konteks dan makna yang lebih kaya dari sebuah teks. Beberapa konsep dalam bahasa memiliki makna yang berbeda ketika berdiri sendiri dibandingkan ketika dikombinasikan, sehingga bigram dan trigram mampu merepresentasikan informasi semantik yang hilang apabila hanya menggunakan unigram. Sebagai contoh, frasa "slot gacor" atau "depo sekarang" dalam konteks komentar judi online memiliki makna yang jauh lebih spesifik sebagai satu kesatuan dibandingkan kata "slot" atau "depo" secara terpisah.

Namun, peningkatan nilai n juga membawa konsekuensi berupa pertumbuhan dimensi ruang fitur yang eksponensial. Semakin besar nilai n, semakin banyak kombinasi fitur yang dihasilkan, sehingga meningkatkan kebutuhan memori dan waktu komputasi. Selain itu, n-gram dengan nilai besar cenderung menghasilkan fitur yang sangat jarang (sparse) karena kombinasi kata tertentu mungkin hanya muncul sekali atau tidak sama sekali dalam dataset, yang dapat menurunkan kemampuan generalisasi model. Oleh karena itu, pemilihan nilai n yang optimal perlu dilakukan melalui eksperimen empiris untuk menemukan keseimbangan antara kekayaan representasi fitur dan efisiensi komputasi (Iriananda dkk., 2024).

Hal ini menegaskan bahwa penerapan ngram_range=(1,2) pada penelitian ini dipilih sebagai titik keseimbangan antara kekayaan representasi fitur dan efisiensi komputasi, karena unigram saja tidak cukup menangkap frasa spesifik seperti "slot gacor", sementara trigram ke atas berisiko menghasilkan fitur yang terlalu jarang (sparse) mengingat ukuran dataset penelitian ini.

## 2.6 Algoritma Support Vector Machine (SVM)

Support Vector Machine (SVM) merupakan algoritma pembelajaran mesin berbasis supervised learning yang bekerja dengan cara mencari bidang pemisah terbaik (hyperplane) untuk membagi data ke dalam dua kelas yang berbeda. Secara matematis, hyperplane pemisah pada Linear SVM didefinisikan sebagai:

    w · x + b = 0

di mana w merupakan vektor bobot (weight vector) yang tegak lurus terhadap hyperplane, x merupakan vektor fitur dari data masukan, dan b merupakan bias. Tujuan utama SVM adalah menemukan nilai w dan b yang memaksimalkan margin, yaitu jarak antara hyperplane dengan titik data terdekat dari masing-masing kelas (support vector). Lebar margin tersebut diformulasikan sebagai:

    margin = 2 / ||w||

> **[GAMBAR 2.2: Ilustrasi Hyperplane dan Margin pada Algoritma Linear SVM]**

Memaksimalkan margin ekuivalen dengan meminimalkan ||w||, sehingga permasalahan ini diselesaikan sebagai optimasi kuadratik. Algoritma ini sangat efektif dalam menangani klasifikasi teks karena kemampuannya dalam melakukan pemetaan data ke ruang dimensi yang sangat tinggi. Untuk data teks berdimensi tinggi seperti hasil ekstraksi TF-IDF, kernel linear terbukti lebih efisien dan tidak rentan terhadap overfitting dibandingkan kernel non-linear seperti RBF, karena data teks pada ruang TF-IDF umumnya sudah dapat dipisahkan secara linear. Penggunaan Linear SVM terbukti mampu mencapai tingkat akurasi hingga 95% dalam mendeteksi spam pada komentar YouTube, yang menunjukkan performa stabil pada data teks media sosial (Airlangga, 2024a).

Selain ketangguhannya pada data berdimensi tinggi, SVM juga dikenal andal dalam memproses teks bahasa alami yang kompleks. Penggabungan metode ekstraksi fitur seperti TF-IDF dengan algoritma SVM mampu menghasilkan akurasi di atas 96% dalam mengklasifikasikan komentar spam judi online berbahasa Indonesia di platform YouTube (Ardiansyah dkk., 2025). Keunggulan ini menjadikan SVM pilihan yang tepat untuk klasifikasi teks dengan variasi penulisan tinggi, seperti komentar pada platform YouTube yang kerap menggunakan singkatan, eufemisme, dan karakter non-standar.

Berdasarkan uraian di atas, algoritma SVM merupakan metode klasifikasi yang andal untuk menangani data teks berdimensi tinggi. Kemampuannya dalam menemukan hyperplane optimal menjadikannya solusi yang relevan untuk diimplementasikan dalam sistem deteksi spam, terutama ketika dikombinasikan dengan teknik prapemrosesan dan ekstraksi fitur yang kuat.

### 2.6.1 Estimasi Probabilitas pada SVM (Platt Scaling)

Algoritma SVM pada dasarnya merupakan pengklasifikasi yang bersifat deterministik, artinya keluaran alami dari model ini hanya berupa keputusan kelas berdasarkan posisi suatu titik data terhadap hyperplane, yakni apakah titik tersebut berada di sisi positif atau negatif bidang pemisah. Nilai yang dihasilkan oleh fungsi keputusan (decision function) bukanlah probabilitas, melainkan jarak bertanda (signed distance) antara titik data dengan hyperplane. Nilai ini tidak terbatas pada rentang tertentu, sehingga tidak dapat langsung diinterpretasikan sebagai tingkat keyakinan (confidence) yang bermakna bagi pengguna.

Untuk mengatasi keterbatasan tersebut, digunakan teknik kalibrasi probabilitas yang dikenal sebagai Platt Scaling (Géron, 2022). Metode ini bekerja dengan memetakan nilai keluaran fungsi keputusan SVM ke dalam rentang probabilitas antara 0 dan 1 menggunakan fungsi sigmoid, yang secara matematis diformulasikan sebagai berikut:

    P(y = 1 | f(x)) = 1 / (1 + exp(A · f(x) + B))

di mana f(x) merupakan nilai fungsi keputusan (jarak bertanda) dari titik data terhadap hyperplane, sedangkan A dan B adalah dua parameter skalar yang dipelajari melalui metode maximum likelihood pada data kalibrasi. Secara konseptual, teknik ini setara dengan melatih sebuah model regresi logistik sederhana di atas nilai keluaran decision function SVM, sehingga jarak mentah terhadap hyperplane dapat dikonversi menjadi estimasi probabilitas yang terkalibrasi.

Dalam implementasinya pada pustaka Scikit-learn, proses kalibrasi ini diaktifkan melalui parameter probability=True pada model SVM. Estimasi parameter A dan B dilakukan menggunakan cross-validation internal pada data latih, yaitu terpisah dari proses pembentukan hyperplane utama, guna menghindari estimasi probabilitas yang bias akibat pemakaian data yang sama (Géron, 2022). Skor probabilitas hasil kalibrasi inilah yang kemudian menjadi dasar dari mekanisme confidence threshold pada sistem yang dibangun, di mana pengguna dapat menyesuaikan ambang batas keyakinan minimum sebelum sebuah komentar dianggap sebagai spam dan disembunyikan.

Sebagai rangkuman, dapat dinyatakan bahwa estimasi probabilitas melalui Platt Scaling menjadi jembatan yang menghubungkan hasil klasifikasi biner SVM yang bersifat deterministik dengan kebutuhan sistem akan skor kepercayaan yang dapat disesuaikan pengguna, sehingga keputusan penyembunyian komentar tidak bersifat kaku, melainkan dapat dikendalikan sesuai tingkat toleransi masing-masing pengguna terhadap risiko false positive maupun false negative.

## 2.7 Algoritma Pembanding

Selain algoritma SVM sebagai model utama, penelitian ini juga mengimplementasikan dua algoritma pembanding dalam proses komparasi performa, yaitu Multinomial Naive Bayes dan Logistic Regression. Komparasi ini dilakukan untuk membuktikan secara empiris bahwa pemilihan SVM sebagai algoritma inti bukan sekadar asumsi, melainkan didasarkan pada hasil evaluasi kuantitatif terhadap data yang sama.

### 2.7.1 Multinomial Naive Bayes

Naive Bayes merupakan algoritma klasifikasi probabilistik yang bekerja berdasarkan teorema Bayes dengan asumsi independensi kondisional antar fitur. Algoritma ini menghitung probabilitas suatu dokumen teks masuk ke dalam kelas tertentu berdasarkan frekuensi kemunculan setiap kata di dalam dokumen tersebut. Varian Multinomial Naive Bayes secara khusus dirancang untuk data yang berbentuk frekuensi atau hitungan, sehingga sangat sesuai untuk dipadukan dengan representasi fitur TF-IDF dalam klasifikasi teks (Apricia dkk., 2024).

Keunggulan utama algoritma ini terletak pada kesederhanaan komputasinya. Multinomial Naive Bayes memiliki waktu pelatihan yang sangat cepat dan kebutuhan memori yang rendah karena hanya perlu menghitung probabilitas kata per kelas selama pelatihan. Karakteristik ini menjadikannya pilihan populer sebagai baseline dalam penelitian klasifikasi teks. Namun, asumsi independensi antar fitur yang dipegang algoritma ini dalam praktiknya jarang terpenuhi pada teks alami, sehingga performa aktualnya sering lebih rendah dibandingkan model yang tidak membuat asumsi tersebut.

Oleh karena itu, dapat dinyatakan bahwa Multinomial Naive Bayes berperan sebagai baseline yang tepat dalam penelitian ini, karena kesederhanaan dan kecepatannya memberikan titik acuan performa minimum yang wajar, sekaligus keterbatasan asumsi independensinya menjadi dasar pembanding untuk membuktikan keunggulan model utama yang dipilih.

### 2.7.2 Logistic Regression

Logistic Regression adalah algoritma klasifikasi berbasis model linear yang menggunakan fungsi sigmoid untuk memetakan kombinasi linear dari fitur-fitur masukan ke dalam nilai probabilitas antara 0 dan 1. Dalam konteks klasifikasi biner spam, algoritma ini mempelajari bobot (weight) untuk setiap fitur TF-IDF sehingga dapat memperkirakan probabilitas sebuah komentar termasuk kelas spam atau ham (Maulana, 2025). Kelas akhir ditentukan berdasarkan nilai ambang batas (threshold) yang umumnya ditetapkan pada 0,5.

Dibandingkan Naive Bayes, Logistic Regression tidak membuat asumsi independensi antar fitur sehingga lebih mampu menangkap hubungan kompleks antar kata dalam teks. Algoritma ini juga relatif mudah diinterpretasikan karena bobot setiap fitur dapat diperiksa langsung untuk mengetahui kata-kata mana yang paling berpengaruh terhadap keputusan klasifikasi. Namun demikian, Logistic Regression cenderung kurang optimal pada data berdimensi sangat tinggi dengan batas pemisah kelas yang tidak bersifat linear, kondisi yang justru menjadi kekuatan utama SVM.

Berangkat dari penjelasan di atas, Logistic Regression menempati posisi sebagai pembanding yang lebih kuat dibandingkan Naive Bayes karena tidak terbebani asumsi independensi antar fitur, namun tetap menjadi tolok ukur yang relevan untuk menegaskan bahwa SVM lebih unggul dalam menangani karakteristik data teks TF-IDF yang berdimensi tinggi.

## 2.8 Evaluasi Model Klasifikasi

Evaluasi model merupakan tahap yang tidak terpisahkan dari proses pengembangan sistem klasifikasi berbasis machine learning. Tujuan utama dari evaluasi adalah mengukur sejauh mana model yang telah dilatih mampu melakukan prediksi yang benar terhadap data yang belum pernah dilihat sebelumnya, sehingga memberikan gambaran objektif tentang performa model di dunia nyata (Helmiyah & Pramestiawan, 2025). Tanpa evaluasi yang tepat, sebuah model yang tampak baik pada data latih bisa jadi gagal total ketika dihadapkan pada data baru akibat fenomena overfitting.

Alat utama yang digunakan dalam evaluasi model klasifikasi biner adalah confusion matrix. Confusion matrix adalah sebuah tabel yang merangkum hasil prediksi model dengan membandingkannya terhadap label sebenarnya, menghasilkan empat komponen utama. True Positive (TP) adalah jumlah data yang benar-benar berlabel positif dan diprediksi benar sebagai positif. True Negative (TN) adalah jumlah data yang benar-benar berlabel negatif dan diprediksi benar sebagai negatif. False Positive (FP) adalah jumlah data negatif yang keliru diprediksi sebagai positif. False Negative (FN) adalah jumlah data positif yang keliru diprediksi sebagai negatif. Dalam konteks sistem ini, kelas positif merujuk pada komentar spam dan kelas negatif merujuk pada komentar normal (ham).

Berdasarkan keempat komponen confusion matrix tersebut, terdapat empat metrik evaluasi utama yang lazim digunakan dalam klasifikasi teks. Pertama, akurasi (accuracy) mengukur proporsi keseluruhan prediksi yang benar terhadap total data uji, dan dirumuskan sebagai berikut:

    Accuracy = (TP + TN) / (TP + TN + FP + FN)

Kedua, presisi (precision) mengukur seberapa tepat model ketika memberikan prediksi positif, yaitu berapa banyak dari semua komentar yang diprediksi spam yang memang benar-benar spam:

    Precision = TP / (TP + FP)

Ketiga, recall mengukur kemampuan model dalam menemukan seluruh komentar spam yang sebenarnya ada di dalam data, yaitu berapa banyak spam yang berhasil terdeteksi dari total spam yang ada:

    Recall = TP / (TP + FN)

Keempat, F1-Score merupakan rata-rata harmonik antara presisi dan recall yang memberikan keseimbangan antara keduanya. Metrik ini sangat berguna ketika distribusi kelas tidak seimbang karena tidak mudah dipengaruhi oleh kelas mayoritas:

    F1-Score = 2 × (Precision × Recall) / (Precision + Recall)

Dalam konteks deteksi spam komentar judi online, metrik recall mendapat perhatian khusus karena konsekuensi dari False Negative yakni komentar spam yang lolos dari deteksi jauh lebih merugikan pengguna dibandingkan False Positive yakni komentar normal yang keliru disembunyikan. Oleh karena itu, F1-Score digunakan sebagai metrik evaluasi utama untuk memastikan keseimbangan antara ketepatan dan kelengkapan deteksi.

Hal ini mengindikasikan bahwa pemilihan metrik evaluasi harus disesuaikan dengan karakteristik dan konsekuensi dari kesalahan klasifikasi pada domain yang diteliti; dalam konteks deteksi spam judi online, F1-Score dipilih sebagai metrik evaluasi utama karena mampu menjaga keseimbangan antara presisi dan recall, sekaligus tidak mudah bias oleh ketimpangan jumlah data antara kelas spam dan non-spam.

## 2.9 Metode Pengembangan Perangkat Lunak (Waterfall)

Pengembangan perangkat lunak memerlukan pendekatan metodologis yang terstruktur agar proses pembangunan sistem dapat berjalan secara sistematis dan menghasilkan produk yang sesuai dengan kebutuhan yang telah ditetapkan. Salah satu metode yang paling banyak digunakan adalah metode Waterfall. Metode ini bekerja secara linear dan sekuensial, di mana setiap tahap harus diselesaikan secara tuntas sebelum dapat melanjutkan ke tahap berikutnya (Anis dkk., 2024).

Metode Waterfall dipilih dalam situasi di mana kebutuhan sistem telah terdefinisi dengan jelas sejak awal dan tidak memerlukan perubahan spesifikasi secara berulang di tengah proses pengembangan. Karakteristik ini berbeda dengan metode Agile yang bersifat iteratif dan fleksibel terhadap perubahan kebutuhan. Metode Waterfall terdiri dari lima tahap utama yang dilaksanakan secara berurutan, yaitu analisis kebutuhan, perancangan sistem, implementasi, pengujian, dan pemeliharaan (Anis dkk., 2024).

> **[GAMBAR 2.3: Tahapan Metode Waterfall]**

Tahap pertama adalah analisis kebutuhan (requirements analysis), yaitu proses identifikasi dan pendokumentasian seluruh kebutuhan fungsional dan non-fungsional sistem. Tahap kedua adalah perancangan sistem (system design), di mana arsitektur sistem, alur kerja, dan antarmuka dirancang secara menyeluruh. Tahap ketiga adalah implementasi (implementation), yaitu penerjemahan rancangan ke dalam kode program. Tahap keempat adalah pengujian (testing), di mana sistem diuji untuk memastikan tidak ada kesalahan dan berjalan sesuai kebutuhan. Tahap kelima adalah pemeliharaan (maintenance), yaitu proses perbaikan dan pengembangan lanjutan setelah sistem digunakan.

Dengan demikian, metode Waterfall relevan dipilih sebagai kerangka pengembangan dalam penelitian ini karena kebutuhan sistem deteksi spam sudah terdefinisi jelas sejak awal, sehingga alur pengerjaan yang linear dan bertahap dapat memastikan setiap fase — dari analisis hingga pemeliharaan — diselesaikan secara sistematis dan terdokumentasi.

## 2.10 Perbandingan Metode Machine Learning dan Deep Learning

Perkembangan metode klasifikasi teks dalam beberapa tahun terakhir menunjukkan adanya pergeseran dari pendekatan Machine Learning tradisional menuju metode Deep Learning. Algoritma Machine Learning seperti Support Vector Machine (SVM) umumnya mengandalkan fitur hasil ekstraksi manual seperti Term Frequency-Inverse Document Frequency (TF-IDF), yang relatif ringan secara komputasi namun tetap efektif untuk dataset berukuran kecil hingga menengah. Sebaliknya, pendekatan Deep Learning mampu mempelajari representasi teks secara otomatis tanpa memerlukan rekayasa fitur secara manual. Model berbasis Deep Learning seperti LSTM mampu mencapai tingkat akurasi tertinggi sebesar 95,65% dalam mendeteksi spam komentar YouTube, namun hal tersebut berbanding lurus dengan kebutuhan sumber daya komputasi yang lebih besar (Airlangga, 2024b).

Meskipun menawarkan akurasi yang tinggi, model Deep Learning menuntut kompleksitas implementasi yang lebih tinggi serta waktu pelatihan yang lebih lama dibandingkan metode tradisional. Sebaliknya, metode Machine Learning seperti SVM mampu memberikan performa klasifikasi yang kompetitif dengan beban komputasi yang jauh lebih ringan, sehingga lebih praktis untuk diimplementasikan pada sistem dengan keterbatasan sumber daya (Airlangga, 2024a).

Poin penting yang dapat diambil dari perbandingan ini adalah bahwa keunggulan akurasi Deep Learning tidak serta-merta menjadikannya pilihan terbaik untuk penelitian ini, sebab kebutuhan sistem akan deteksi real-time yang ringan dan hemat sumber daya justru lebih terpenuhi oleh Machine Learning berbasis SVM yang tetap kompetitif namun jauh lebih efisien secara komputasi.

## 2.11 Pengumpulan Data Komentar dan Analisis Heuristik

Dalam pengembangan kecerdasan buatan, ketersediaan himpunan data (dataset) yang melimpah dan relevan menjadi syarat mutlak. Salah satu teknik yang umum digunakan untuk mengumpulkan data dari internet adalah web scraping, yaitu teknik mengekstrak data dalam jumlah besar secara cepat dan otomatis dari halaman web dengan cara memuat struktur kode HTML suatu situs dan mem-parsing elemen-elemen spesifik di dalamnya (Koprawi & Putra, 2023). Meskipun efektif, pendekatan ini memiliki keterbatasan, yaitu rentan melanggar ketentuan layanan (terms of service) platform serta mudah rusak apabila struktur halaman web mengalami perubahan.

Oleh karena itu, penelitian ini tidak menggunakan web scraping berbasis HTML, melainkan memanfaatkan YouTube Data API v3, yaitu antarmuka pemrograman aplikasi resmi yang disediakan oleh YouTube untuk mengakses data publik seperti komentar secara terstruktur. YouTube Data API v3 merupakan layanan berbasis REST API (sebagaimana dijelaskan pada Sub-bab 2.14) yang mengembalikan data dalam format JSON melalui permintaan HTTP terotorisasi menggunakan kunci API (API key). Pendekatan ini dipilih karena bersifat legal dan sesuai ketentuan platform, memberikan data yang terstruktur dan konsisten, serta lebih stabil dibandingkan scraping HTML yang bergantung pada struktur tampilan halaman. Pada penelitian ini, pengambilan data melalui API tersebut diotomatisasi menggunakan skrip berbasis Node.js.

Lebih lanjut, untuk memastikan tingkat validitas data yang dikumpulkan, proses pengambilan data ini dikombinasikan dengan metode analisis heuristik. Dalam konteks ilmu komputer, pendekatan heuristik merupakan teknik pemecahan masalah berbasis aturan praktis (rule-based) yang memanfaatkan pengetahuan domain untuk menghasilkan keputusan secara efisien, meskipun tidak selalu menjamin solusi yang optimal (Kaddoura dkk., 2022). Dalam penelitian ini, heuristik diimplementasikan sebagai algoritma penyaringan (filter) yang memberikan parameter pembobotan (scoring) otomatis pada setiap komentar yang diperoleh. Sistem akan mendeteksi kepadatan anomali karakter (seperti manipulasi Unicode) atau kata kunci spesifik (keywords), sehingga proses pengumpulan data latih promosi perjudian menjadi jauh lebih presisi dan terstruktur sebelum diteruskan ke model pelatihan SVM.

Ringkasnya, kombinasi pemanfaatan YouTube Data API v3 dan analisis heuristik dalam penelitian ini tidak hanya berfungsi mengumpulkan data secara otomatis dan legal dalam jumlah besar, tetapi juga menyaring kualitasnya sejak tahap awal, sehingga dataset yang dihasilkan lebih relevan dan minim noise sebelum digunakan untuk melatih model klasifikasi.

## 2.12 Spam Komentar pada Media Sosial (YouTube)

Spam komentar pada media sosial merupakan salah satu bentuk penyalahgunaan platform digital yang dilakukan dengan tujuan tertentu, seperti promosi, penyebaran informasi yang tidak relevan, maupun aktivitas penipuan. Pada platform berbagi video seperti YouTube, aktivitas ini umumnya dihasilkan oleh bot atau akun otomatis yang memposting pesan secara berulang dengan pola tertentu. Spam pada YouTube sering kali berasal dari sistem otomatis yang dirancang untuk menyebarkan tautan berbahaya atau promosi massal yang mengganggu kualitas interaksi pengguna (Khan, 2018).

Fenomena ini telah berkembang menjadi ancaman yang lebih serius di Indonesia, khususnya terkait penyebaran konten ilegal. Penyebaran promosi judi online di media sosial telah menjadi krisis siber yang mengancam ketahanan nasional, di mana para pelaku memanfaatkan kolom komentar platform besar seperti YouTube untuk menjangkau masyarakat secara masif (Herawati dkk., 2025). Hal ini menyebabkan penurunan kualitas ekosistem digital dan berpotensi menjerumuskan pengguna ke dalam risiko finansial.

Berdasarkan uraian di atas, spam pada platform YouTube telah bertransformasi dari sekadar gangguan teknis menjadi sarana penyebaran konten ilegal yang terorganisir melalui bantuan bot. Oleh karena itu, diperlukan sistem perlindungan yang mampu mendeteksi pola otomatisasi tersebut guna menjaga keamanan dan kenyamanan pengguna dalam berinteraksi di ruang publik digital.

## 2.13 Arsitektur Chrome Extension (Manifest V3)

Ekstensi Google Chrome adalah perangkat lunak tambahan yang memperluas fungsionalitas peramban dengan beroperasi pada sisi klien (client-side). Berdasarkan standar terbaru yakni Manifest V3, ekstensi memiliki kemampuan untuk membaca dan memodifikasi Document Object Model (DOM) pada halaman web secara dinamis melalui Content Scripts (Ramadhan & Fauzan, 2023). Penggunaan ekstensi pada peramban Chrome sangat efektif untuk melakukan pembatasan atau penyaringan konten secara langsung di sisi pengguna dengan cara memanipulasi elemen halaman web yang sedang dibuka.

Selain untuk fungsi penapisan, arsitektur ekstensi juga mendukung proses pengolahan data yang efisien. Fleksibilitas ini memungkinkan pengembang untuk mengintegrasikan model cerdas ke dalam peramban guna mengeksekusi instruksi tertentu, seperti menyembunyikan elemen komentar yang terdeteksi sebagai konten terlarang secara real-time.

Dengan demikian, arsitektur Chrome Extension berbasis Manifest V3 merupakan platform yang tepat untuk mengimplementasikan sistem filtrasi cerdas. Kemampuannya dalam berinteraksi langsung dengan DOM dan menjalankan skrip secara asynchronous menjadikannya solusi yang efisien untuk melindungi pengguna dari paparan konten spam tanpa membebani performa perangkat secara berlebihan.

## 2.14 REST API dan Lingkungan FastAPI (Python)

Integrasi arsitektur perangkat lunak antara ekstensi peramban di sisi klien (client-side) dengan mesin Machine Learning di sisi peladen (server-side) memerlukan jalur komunikasi data yang stabil. Konsep Representational State Transfer Application Programming Interface (REST API) digunakan sebagai jembatan pertukaran data ringan berbasis format JSON melalui protokol HTTP. Agar layanan REST API ini dapat melayani permintaan deteksi teks secara instan, diperlukan kerangka kerja (framework) yang memiliki kecepatan eksekusi tinggi.

FastAPI merupakan kerangka kerja modern berbasis bahasa pemrograman Python yang dirancang khusus untuk membangun layanan web service dengan tingkat performa tinggi (Azhari, 2022). Berbeda dengan Flask yang bersifat general purpose, FastAPI dirancang secara eksklusif sebagai web service dan mengadopsi mekanisme pemrograman asynchronous sehingga mampu memproses permintaan tanpa harus menunggu setiap proses selesai secara berurutan. FastAPI juga memiliki sistem validasi tipe data bawaan yang ketat melalui pustaka Pydantic, yang memastikan setiap data masukan telah tervalidasi sebelum diproses lebih lanjut.

Berdasarkan uraian tersebut, dapat disimpulkan bahwa REST API dengan kerangka kerja FastAPI merupakan pilihan yang sesuai untuk menjembatani komunikasi antara ekstensi dan model klasifikasi, karena kombinasi mekanisme asynchronous dan validasi tipe data ketat memungkinkan layanan deteksi berjalan cepat, stabil, dan aman terhadap masukan yang tidak valid.

## 2.15 Unified Modeling Language (UML)

Dalam merancang perangkat lunak yang kompleks, dibutuhkan sebuah pemodelan visual untuk memastikan seluruh alur sistem terekam secara komprehensif sebelum tahapan pengkodean (coding) dilakukan. UML (Unified Modeling Language) adalah standar bahasa pemodelan berbasis grafik yang digunakan untuk mengidentifikasi kebutuhan sistem (requirement), merancang arsitektur analitis, serta mendokumentasikan spesifikasi perangkat lunak yang berorientasi objek (Rosa & Shalahuddin, 2019). Dalam penelitian ini, tiga jenis diagram UML digunakan untuk memodelkan sistem secara komprehensif, yaitu use case diagram, activity diagram, dan sequence diagram.

### 2.15.1 Use Case Diagram

Use case diagram merupakan bagian dari UML yang merepresentasikan fungsionalitas sistem dari perspektif pengguna (actor). Diagram ini tidak menjelaskan secara teknis bagaimana sistem bekerja di balik layar, melainkan menjabarkan batasan sistem (system boundary) serta mendeskripsikan operasi dan skenario layanan yang dapat dilakukan aktor terhadap sistem. Komponen utama use case diagram terdiri dari actor yang digambarkan sebagai ikon manusia, use case yang digambarkan sebagai elips berisi nama fungsionalitas, system boundary berupa kotak persegi yang membatasi cakupan sistem, serta relasi association, include, dan extend yang menghubungkan komponen-komponen tersebut.

> **[GAMBAR 2.4: Simbol-Simbol Use Case Diagram]**

### 2.15.2 Activity Diagram

Activity diagram adalah diagram pemodelan dinamis yang menggambarkan alur kerja prosedural (workflow) dari setiap proses bisnis di dalam sistem. Diagram ini secara kronologis memetakan transisi eksekusi kontrol sistem, mulai dari inisialisasi awal, pengambilan keputusan di setiap percabangan kondisi, hingga alur penyelesaian akhir. Komponen utama activity diagram meliputi initial node berupa lingkaran hitam penuh sebagai titik awal, action node berupa persegi panjang berisi nama aksi, decision node berupa belah ketupat untuk percabangan kondisi, fork/join node berupa garis horizontal untuk alur paralel, serta activity final node berupa lingkaran hitam bertepi sebagai titik akhir.

> **[GAMBAR 2.5: Simbol-Simbol Activity Diagram]**

### 2.15.3 Sequence Diagram

Sequence diagram adalah diagram UML yang menggambarkan interaksi antar objek atau komponen sistem berdasarkan urutan waktu (time-ordered). Diagram ini sangat efektif untuk memodelkan komunikasi antar lapisan sistem (layer) yang berbeda, seperti interaksi antara ekstensi peramban, server API, dan model klasifikasi. Komponen utama sequence diagram meliputi lifeline berupa garis putus-putus vertikal yang merepresentasikan objek atau komponen, activation bar berupa persegi panjang tipis di atas lifeline yang menunjukkan periode aktif suatu objek, serta message berupa anak panah horizontal yang merepresentasikan komunikasi antar lifeline, baik berupa synchronous message (panah penuh), return message (panah putus-putus), maupun asynchronous message (panah terbuka).

> **[GAMBAR 2.6: Simbol-Simbol Sequence Diagram]**

Secara keseluruhan, ketiga diagram UML tersebut saling melengkapi dalam memodelkan sistem: use case diagram menggambarkan apa yang dapat dilakukan pengguna, activity diagram memetakan bagaimana alur kerja berlangsung, dan sequence diagram merinci urutan interaksi antar komponen dari waktu ke waktu, sehingga rancangan sistem dapat dipahami secara menyeluruh sebelum tahap implementasi.

## 2.16 Metode Analisis Sistem (PIECES)

Untuk mengukur tingkat kelayakan sistem yang dikembangkan, digunakan kerangka kerja analisis PIECES. Menurut Kinanti & Indriyanti (2021), analisis PIECES adalah metode evaluasi sistem yang meninjau permasalahan dan peluang perbaikan dari enam aspek utama, yaitu Performance (Kinerja), Information (Informasi), Economics (Ekonomi), Control (Pengendalian), Efficiency (Efisiensi), dan Service (Pelayanan). Keenam aspek tersebut dijabarkan pada tabel berikut.

**Tabel 2.1 Aspek-Aspek Analisis PIECES**

| Aspek | Penjelasan |
|-------|------------|
| Performance (Kinerja) | Mengukur kemampuan sistem dalam memproses sejumlah pekerjaan dalam satuan waktu tertentu. Kinerja diukur melalui dua parameter utama: throughput, yaitu jumlah pekerjaan yang berhasil diselesaikan sistem dalam periode tertentu, dan response time, yaitu rata-rata waktu yang dibutuhkan sistem untuk merespons sebuah permintaan. |
| Information (Informasi) | Mengevaluasi kualitas informasi yang dihasilkan sistem dari tiga dimensi utama: akurasi (accurate), yang berarti informasi bebas dari kesalahan; ketepatan waktu (timely), yang berarti informasi tersedia saat dibutuhkan; dan relevansi (relevant), yang berarti informasi sesuai dengan kebutuhan pengguna. |
| Economics (Ekonomi) | Menilai efisiensi biaya operasional sistem, mencakup analisis pengurangan pengeluaran yang tidak perlu dan peningkatan manfaat yang diperoleh dari sistem yang dikembangkan dibandingkan dengan kondisi sebelumnya. |
| Control (Pengendalian) | Menilai kemampuan sistem dalam mencegah atau mendeteksi kesalahan operasional, menjaga keamanan data dari akses yang tidak sah, serta memastikan keandalan sistem dalam menghadapi potensi gangguan atau kerusakan. |
| Efficiency (Efisiensi) | Mengukur sejauh mana sistem dapat memaksimalkan keluaran (output) dengan menggunakan sumber daya masukan (input) seminimal mungkin, sehingga tidak terjadi pemborosan waktu, tenaga, maupun biaya operasional. |
| Service (Pelayanan) | Menilai kemudahan dan kenyamanan yang diberikan sistem kepada pengguna dalam menyelesaikan tugasnya, termasuk keramahan antarmuka, keandalan layanan, serta kemampuan sistem dalam memenuhi kebutuhan pengguna secara konsisten. |

Kesimpulannya, kerangka PIECES dipilih dalam penelitian ini karena keenam aspeknya menyediakan sudut pandang yang menyeluruh untuk mendiagnosis kelemahan sistem penyaringan komentar yang berjalan saat ini, sekaligus menjadi dasar terstruktur untuk merumuskan solusi perbaikan yang ditawarkan oleh sistem usulan.

## 2.17 Studi Penelitian Terdahulu

Kajian terhadap studi penelitian terdahulu dilakukan untuk mengetahui perkembangan penelitian yang telah ada, mengidentifikasi celah penelitian (research gap), serta menjadi landasan bagi pengembangan sistem yang diusulkan. Penelitian ini merujuk pada dua studi penelitian terdahulu yang memiliki tingkat relevansi paling tinggi terhadap deteksi komentar spam promosi judi online di platform YouTube menggunakan Machine Learning. Berikut adalah uraian dari kedua penelitian tersebut:

1. Angelo, Robet & Hendrik (2025), Comparative Performance of Machine Learning Algorithms for Detecting Online Gambling Promotional Comments on YouTube.
   - a. Input: Dataset komentar YouTube yang mengandung promosi judi online berbahasa Indonesia, termasuk komentar yang menggunakan teknik obfuscation seperti karakter Unicode, emoji, spasi tidak beraturan, dan simbol untuk menghindari moderasi otomatis. Dataset diperluas menggunakan teknik semi-supervised pseudo-labelling dari 1.648 menjadi 9.111 komentar.
   - b. Proses: Membandingkan performa empat algoritma Machine Learning Multinomial Naive Bayes, Logistic Regression, Random Forest, dan SVM menggunakan pipeline TF-IDF dengan normalisasi karakter khusus, stopword removal, dan stemming Nazief–Adriani. Optimasi hiperparameter dan penyeimbangan kelas dilakukan melalui SMOTE.
   - c. Output: Seluruh model mencapai akurasi di atas 98% pada set pengujian. SVM memberikan performa paling seimbang dengan F1-score tertinggi sebesar 0,9908 untuk kelas promosi, sehingga direkomendasikan untuk deployment operasional dalam moderasi otomatis komentar judi online.
2. Airlangga (2024a), Spam Detection on YouTube Comments Using Advanced Machine Learning Models: A Comparative Study
   - a. Input: Himpunan data (dataset) komentar YouTube yang telah dikategorikan secara manual ke dalam dua kelas utama, yaitu spam dan ham (normal).
   - b. Proses: Menjalankan studi perbandingan performa klasifikasi menggunakan model Machine Learning tingkat lanjut, yang meliputi algoritma Linear SVM, Random Forest, dan XGBoost.
   - c. Output: Hasil evaluasi membuktikan bahwa algoritma Linear SVM memberikan performa yang paling stabil dan unggul dengan tingkat akurasi klasifikasi mencapai 95%.

Berdasarkan kedua penelitian terdahulu di atas, dapat disimpulkan bahwa algoritma SVM secara konsisten menunjukkan performa terbaik dalam mendeteksi komentar spam dan promosi judi online di YouTube. Namun demikian, kedua penelitian tersebut menghasilkan model yang beroperasi secara offline model hanya dapat digunakan melalui skrip atau antarmuka terpisah, bukan langsung terintegrasi ke dalam pengalaman berselancar pengguna. Oleh karena itu, terdapat celah penelitian berupa kebutuhan akan sistem yang mampu menjalankan deteksi spam secara real-time langsung di peramban pengguna, tanpa memerlukan intervensi manual, melalui implementasi model SVM pada arsitektur Chrome Extension.

## 2.18 Persyaratan Sistem Konseptual

Berdasarkan hasil analisis terhadap studi penelitian terdahulu, sistem yang dirancang dalam penelitian ini harus memenuhi persyaratan konseptual tertentu guna menutupi celah kekurangan pada penelitian sebelumnya. Berikut adalah rincian persyaratan sistem konseptual tersebut:

1. **Modul Prapemrosesan Teks dengan Teknik String Normalization**
   - a. Input: Data teks komentar dari platform YouTube yang mengandung berbagai variasi penyamaran karakter (obfuscation), seperti penggunaan homoglyphs, simbol Unicode khusus, dan karakter non-standar yang digunakan untuk menghindari moderasi otomatis.
   - b. Proses: Mendeteksi karakter non-ASCII dan melakukan konversi teks menggunakan teknik string normalization untuk mengembalikan karakter manipulatif ke bentuk teks standar sebelum diteruskan ke tahap ekstraksi fitur.
   - c. Output: Teks komentar yang bersih dan ternormalisasi, siap diproses oleh tahap ekstraksi fitur TF-IDF dan klasifikasi SVM.
   - d. Pengembangan (Improvement): Angelo dkk. (2025) menunjukkan bahwa komentar promosi judi online di YouTube secara aktif menggunakan teknik obfuscation berbasis Unicode untuk menghindari deteksi. Penelitian ini mengadopsi pendekatan normalisasi karakter serupa dan mengintegrasikannya ke dalam pipeline prapemrosesan yang berjalan secara otomatis di sisi klien.
2. **Modul Deteksi Real-Time Berbasis Chrome Extension**
   - a. Input: Elemen Document Object Model (DOM) pada halaman YouTube yang memuat teks komentar pengguna secara dinamis.
   - b. Proses: Menggunakan content script untuk membaca teks komentar secara asynchronous, mengirimkannya ke model SVM melalui REST API FastAPI, dan menerima hasil klasifikasi untuk diterapkan pada tampilan halaman.
   - c. Output: Perubahan status tampilan pada elemen komentar yang teridentifikasi sebagai spam judi online melalui manipulasi CSS (display: none), sehingga komentar tersebut tersembunyi secara visual tanpa mengganggu konten lainnya.
   - d. Pengembangan (Improvement): Airlangga (2024a) membuktikan akurasi Linear SVM mencapai 95% dalam klasifikasi komentar spam YouTube, namun implementasinya terbatas pada evaluasi data secara offline. Penelitian ini mengembangkan sistem tersebut dengan mengintegrasikan model SVM ke dalam arsitektur Chrome Extension sehingga perlindungan dapat dirasakan langsung oleh pengguna secara real-time tanpa intervensi manual.
3. **Keandalan Klasifikasi dengan Algoritma SVM**
   - a. Input: Fitur numerik hasil ekstraksi Term Frequency-Inverse Document Frequency (TF-IDF) dari teks komentar yang telah melalui tahap normalisasi.
   - b. Proses: Melakukan pemisahan data menggunakan hyperplane optimal yang dibentuk oleh algoritma Linear SVM untuk menentukan label akhir setiap komentar.
   - c. Output: Keputusan klasifikasi biner berupa label "Spam" atau "Ham" (normal) dengan tingkat presisi dan recall yang tinggi.
   - d. Pengembangan (Improvement): Sistem yang dibangun secara khusus menargetkan komentar promosi judi online berbahasa Indonesia sebuah domain yang belum menjadi fokus utama penelitian Airlangga (2024a) maupun penelitian sebelumnya sehingga model dilatih menggunakan dataset yang dikumpulkan dan dilabeli secara manual dari platform YouTube untuk memastikan relevansi terhadap konteks bahasa dan konten yang spesifik.
