"""Normalisasi teks komentar sebelum masuk ke TF-IDF.

Modul ini dipakai dua tempat: saat membangun dataset latih, dan saat server
memprediksi komentar baru. Harus tetap satu modul supaya keduanya menerima
bentuk masukan yang sama. Kalau normalisasi dipecah (misalnya sebagian
dikerjakan di JavaScript sisi ekstensi), perbedaan kecil dalam penanganan
Unicode bikin model menerima input yang tidak sama dengan saat dilatih, dan
akurasinya turun tanpa gejala yang kelihatan.

Konsekuensinya: setiap kali file ini diubah, jalankan ulang
prepare_dataset.py lalu train.py.

Urutan tahapannya ada di clean_text(). Urutan itu tidak bisa ditukar.
"""

import re
import unicodedata
import emoji

# Hampir semua nama situs judol Indonesia berpola [nama bebas] + [suffix].
# Suffix numerik: 4D/3D/2D (togel), 88/99/77/69, 777/888/303.
# Suffix kata: QQ (BandarQQ, HobiQQ, DominoQQ).
#
# Masalahnya Step 6 membuang semua digit, jadi keju4d jadi "keju" dan
# betawi77 jadi "betawi", kata biasa yang lalu dilatih dengan label spam.
# Lama-lama itu menaikkan false positive di komentar kuliner atau non-judi.
#
# Solusinya: deteksi polanya sebelum digit dibuang, lalu ganti dengan satu
# token "judolbrand". Token itu selamat dari Step 6 karena huruf semua, dan
# berlaku untuk nama situs baru yang belum pernah dilihat asal polanya sama.
#
# Yang tidak tertangani: nama yang memakai charset campur (misalnya angka
# Thai di tengah nama) tidak membentuk pola dengan utuh. Ini keterbatasan
# yang diketahui, lihat docs/evaluasi.md.

# "level99" cocok pola tapi konteksnya gaming, bukan judol. Dikecualikan lewat
# negative lookbehind supaya tidak perlu filter terpisah setelahnya.
_JUDOL_EXCLUDE_PREFIXES = (
    "level", "rank", "stage", "episode", "part", "seri", "versi",
    "chapter", "season", "round", "wave", "fase", "lv",
)
_EXCL = "|".join(_JUDOL_EXCLUDE_PREFIXES)

JUDOL_BRAND_PATTERN = re.compile(
    rf'\b(?!(?:{_EXCL})\d)[a-z]{{2,}}(?:4d|3d|2d|88|99|77|69|138|388|303|777|888|qq)\b'
)


# Kata berfrekuensi tinggi yang tidak membedakan spam dari non-spam. Ditulis
# manual, bukan diambil dari pustaka, supaya isinya gampang ditinjau. Varian
# informal (gua, kalo, udah, tp) ikut dimasukkan karena mendominasi komentar
# YouTube.
STOPWORDS_ID = {
    "yang", "dan", "di", "ke", "dari", "untuk", "ini", "itu", "dengan",
    "adalah", "dalam", "pada", "atau", "juga", "sudah", "ada", "bisa",
    "akan", "tidak", "lebih", "kami", "kita", "anda", "saya", "gua", "gue",
    "kamu", "dia", "mereka", "sini", "sana", "bila", "jika", "maka",
    "karena", "tapi", "namun", "tetapi", "oleh", "agar", "supaya",
    "bahwa", "saat", "saja", "pun", "lagi", "ya", "yg", "yuk", "dong",
    "nih", "deh", "lah", "kan", "nya", "si", "para", "sekali", "sangat",
    "banget", "amat", "kalau", "kalo", "gimana", "gitu", "tuh",
    "udah", "belum", "sdh", "dgn", "utk", "krn", "jd",
    "tp", "dr", "pd", "sama", "seperti", "jadi", "baru", "masih",
    "terus", "buat", "bikin", "kasih", "mau", "tau", "tahu"
}

# NFKC merapikan variasi dekoratif dalam satu aksara, tapi tidak bisa
# menyeberang antar aksara. Sirilik 'а' (U+0430) terlihat persis seperti 'a'
# Latin dan dibiarkan apa adanya oleh NFKC. Peta ini menutup celah itu untuk
# karakter yang paling sering dipakai di spam judol.
HOMOGLYPH_MAP = str.maketrans({
    # Sirilik
    "а": "a",
    "е": "e",
    "о": "o",
    "р": "p",  # mirip 'p', bukan 'r'
    "с": "c",
    "х": "x",
    "і": "i",
    "ѕ": "s",
    "є": "e",
    "А": "A",
    "Е": "E",
    "О": "O",
    "Р": "P",
    "С": "C",
    "Т": "T",
    "Х": "X",
    # Yunani
    "ν": "v",
    "α": "a",
    "ο": "o",
    "ρ": "p",
    # Angka Thai 3, bentuknya mirip huruf m. Dipakai di nama seperti "ro๓a".
    "๓": "m",
})


def clean_text(text: str) -> str:
    """Jalankan satu komentar mentah melalui seluruh tahap normalisasi.

    Dipanggil dengan cara yang sama saat pelatihan maupun saat prediksi.
    Mengembalikan string kosong kalau input tidak valid atau habis setelah
    dibersihkan.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Step 1: buang karakter tak terlihat. Tidak kelihatan di editor mana pun,
    # tapi memecah "daftar" jadi enam token satu huruf yang lalu terbuang.
    zero_width_chars = (
        "\u200B"  # zero-width space
        "\u200C"  # zero-width non-joiner
        "\u200D"  # zero-width joiner
        "\uFEFF"  # byte order mark
        "\u00AD"  # soft hyphen
        "\u200E"  # left-to-right mark
        "\u200F"  # right-to-left mark
    )
    for char in zero_width_chars:
        text = text.replace(char, "")

    # Step 2: NFKC. Menangani sebagian besar trik font:
    #   𝑅𝒪𝑀𝒜𝟦𝒟  -> ROMA4D
    #   Ｄａｆｔａｒ -> Daftar
    #   🅓🅐🅕🅣🅐🅡  -> DAFTAR
    text = unicodedata.normalize("NFKC", text)

    # Step 2b: buang combining mark. NFKC tidak menyentuhnya, padahal spammer
    # menyisipkan U+0332 dan sejenisnya di antara huruf. Tanpa tahap ini,
    # P͟U͟L͟A͟U͟W͟I͟N jadi deretan token satu huruf dan habis di Step 7.
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    # Step 2c: buka kurung yang membungkus tepat satu karakter, trik [P][U][L].
    # Dibatasi satu karakter supaya kalimat normal dalam kurung tidak ikut.
    text = re.sub(r"[\[(\{]\s*(\w)\s*[\])\}]", r"\1", text)

    text = text.translate(HOMOGLYPH_MAP)

    # Step 4: emoji jadi token teks, bukan dibuang. 🎰 dan 💰 penanda spam yang
    # kuat, 👍 netral. Membuangnya berarti membuang sinyal itu.
    text = emoji.demojize(text, language="en")
    text = re.sub(r":([a-zA-Z0-9_]+):", r" \1 ", text)

    text = text.lower()

    # Step 5b-i: leet speak, H0KI777 -> HOKI777, s1tus -> situs.
    # Hanya 0->o dan 1->i. Substitusi lain (3->e, 4->a, 5->s) terlalu sering
    # merusak angka yang memang angka, misalnya skor atau harga.
    # Harus sebelum Step 5b supaya nama situs ber-leet ikut cocok pola.
    def _normalize_leet(m):
        word = m.group(0)
        return word.replace("0", "o").replace("1", "i")

    text = re.sub(r'\b[a-z0-9]*[0-9][a-z0-9]*\b', _normalize_leet, text)

    # Step 5b: harus setelah lowercase dan sebelum digit dibuang. Lihat catatan
    # di JUDOL_BRAND_PATTERN.
    text = JUDOL_BRAND_PATTERN.sub("judolbrand", text)

    # Step 6: URL dulu sebagai pola bernama, lalu sisakan huruf dan spasi saja.
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)

    # Step 7: rapikan spasi, buang stopword dan token satu huruf.
    text = re.sub(r"\s+", " ", text).strip()
    tokens = [
        word for word in text.split()
        if word not in STOPWORDS_ID and len(word) > 1
    ]

    return " ".join(tokens)


def preprocess_batch(texts) -> list:
    """Terapkan clean_text() ke list atau Series berisi string."""
    return [clean_text(t) for t in texts]


if __name__ == "__main__":
    # Konsol Windows default ke cp1252 dan gagal mencetak emoji serta aksara
    # non-Latin di kasus uji bawah ini.
    import sys

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Kasus uji diambil dari penyamaran yang benar-benar ditemukan saat
    # mengumpulkan data, bukan contoh karangan.
    test_cases = [
        "𝑅𝒪𝑀𝒜𝟦𝒟 daftar sekarang bonus gede!",
        "dаftаr sekаrаng dаpаt bоnus 100%",
        "ＰⓤＬＡＵ777, tempatnya peluang besar",
        "Bukan ngebet, tapi nyaman di P̲̲U̲̲L̲̲A̲̲U̲̲W̲̲I̲̲N̲̲?",
        "🎰💰 slot gacor hari ini, WD cepat, daftar gratis 🎁🔥",
        "Video ini sangat membantu buat gua yang lagi belajar. Terimakasih kak!",
        "d\u200ba\u200bf\u200bt\u200ba\u200br sekarang bonus member baru",
        "kalau udah masakan nusantara pasti buat ngiler, salam Jp KEJU4D",
        "memang bikin selera naik, seperti di BETAWI77 bikin naik terus",
        "bikin mood gw balik lagi, salam sukses dari HOBIQQ",
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n[{i}] input  : {text}")
        print(f"    output : {clean_text(text)}")
