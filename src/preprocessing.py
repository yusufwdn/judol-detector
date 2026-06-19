"""
preprocessing.py
================
Cleans and normalizes raw comment text before it is fed into the SVM model.

WHY PREPROCESSING MATTERS
--------------------------
The SVM model operates on numbers, not words. Before conversion, text must be
cleaned so that:
1. Case differences are eliminated  ("Daftar" vs "daftar" → same token)
2. Unicode obfuscation is reversed   (𝑅𝒪𝑀𝒜 → ROMA, Ｄ → D)
3. Emojis contribute signal, not noise (🎰 → slot_machine)
4. Invisible characters don't corrupt tokenization
5. Stopwords don't dilute discriminative features

WHY NORMALIZATION RUNS HERE (NOT IN THE EXTENSION)
----------------------------------------------------
The browser extension sends raw comment text directly to the server — no
pre-processing is done in JavaScript. This is a deliberate architecture
decision to enforce training-serving consistency:

  Training : raw text → clean_text() → TF-IDF → SVM learns from this
  Inference: raw text → clean_text() → TF-IDF → SVM predicts from this

If normalization were split between JS (extension) and Python (server),
any subtle difference in how each environment handles Unicode would cause
the model to receive inputs that look slightly different from what it was
trained on — a problem known as training-serving skew — degrading accuracy
in production. Keeping the full pipeline in Python eliminates this risk.

PIPELINE ORDER (7 STEPS + 3 SUB-STEPS)
-----------------------------------------
Step 1 : Strip zero-width characters  — invisible chars that break tokenization
Step 2 : NFKC Unicode normalization   — collapse decorative Unicode to ASCII
Step 2b: Strip combining diacriticals — spammer trick: P͟U͟L͟A͟U͟ → PULAU
Step 2c: Unwrap bracketed chars       — spammer trick: [P][U][L][A][U] → PULAU
Step 3 : Cyrillic/Greek/Thai homoglyph — NFKC cannot cross script boundaries
Step 4 : Emoji demojize               — convert emoji to descriptive text tokens
Step 5 : Lowercase
Step 5b: Brand canonicalization       — keju4d/hobiqq → judolbrand (before digits stripped)
Step 6 : Remove URLs and non-alpha characters
Step 7 : Remove stopwords
"""

import re
import unicodedata
import emoji

# ---------------------------------------------------------------------------
# JUDOL BRAND CANONICALIZATION PATTERN (Step 5b)
# ---------------------------------------------------------------------------
# Hampir semua nama situs judi online Indonesia mengikuti pola:
#   [nama bebas] + [suffix numerik atau khas judol]
#
# Contoh suffix numerik: 4D/3D/2D (togel), 88/99/77/69 (slot), 777/888/303
# Contoh suffix kata   : QQ (poker/domino online: BandarQQ, HobiQQ, DominoQQ)
#
# MASALAH TANPA STEP INI:
#   Step 6 menghapus semua digit → suffix numerik brand ikut terhapus:
#     keju4d   → keju   (keju = makanan, bukan judol)
#     betawi77 → betawi (suku Betawi, bukan judol)
#     slot888  → slot   (kata slot ada di HARD_SPAM_SIGNALS, jadi masih ok —
#                        tapi tidak lagi menjadi fitur brand spesifik)
#
#   Akibatnya model dilatih dengan fitur "keju" yang salah label, lama-lama
#   meningkatkan risiko false positive di komentar kuliner atau non-judi.
#
# SOLUSI:
#   Sebelum digit dihapus (Step 6), deteksi pola brand lalu GANTI dengan token
#   universal "judolbrand". Token ini:
#     1. Tidak dibuang oleh Step 6 (huruf semua, bukan digit/simbol)
#     2. Tersimpan sebagai fitur TF-IDF yang kuat — model belajar bahwa
#        "judolbrand" = sinyal spam tanpa perlu menghafal tiap nama brand
#     3. Generalisasi otomatis — brand baru yang belum pernah dilihat tapi
#        mengikuti pola yang sama langsung tertangkap
#
# KENAPA SETELAH LOWERCASE (STEP 5)?
#   Agar regex cukup ditulis lowercase saja (tidak perlu flag IGNORECASE
#   yang memperlambat, atau menduplikasi pattern untuk huruf kapital).
#
# TRADE-OFF (diterima):
#   Brand yang pakai karakter non-ASCII (𝓇𝐀๓𝓐 ４𝓓) melewati Step 2 NFKC
#   tapi kegagalan charset campur (Thai ๓) membuat patternnya tidak terbentuk
#   sempurna. Kasus ini sudah dicatat sebagai "keterbatasan" skripsi.
#
# CONTOH:
#   Input (setelah lowercase)  →  Output (setelah Step 5b)
#   keju4d                     →  judolbrand
#   betawi77                   →  judolbrand
#   slot777                    →  judolbrand
#   hobiqq                     →  judolbrand
#   bandarqq                   →  judolbrand
#   hana303                    →  judolbrand
#   gacor                      →  gacor  (tidak cocok, tetap apa adanya)
#   kecoa99                    →  judolbrand (jika suatu saat dipakai spammer)

# Kata-kata yang TIDAK boleh dikanonikalisasi meski cocok secara pola.
# Contoh: "level99" cocok pola tapi ini konteks gaming, bukan judol.
# Diimplementasikan sebagai negative lookbehind di regex agar tidak perlu
# post-filter terpisah.
_JUDOL_EXCLUDE_PREFIXES = (
    "level", "rank", "stage", "episode", "part", "seri", "versi",
    "chapter", "season", "round", "wave", "fase", "lv",
)
_EXCL = "|".join(_JUDOL_EXCLUDE_PREFIXES)

JUDOL_BRAND_PATTERN = re.compile(
    rf'\b(?!(?:{_EXCL})\d)[a-z]{{2,}}(?:4d|3d|2d|88|99|77|69|138|388|303|777|888|qq)\b'
)


# ---------------------------------------------------------------------------
# INDONESIAN STOPWORDS
# ---------------------------------------------------------------------------
# Stopwords are high-frequency words that carry no discriminative signal.
# Words like "yang", "dan", "di" appear in virtually every comment — spam
# and non-spam alike — so they add noise rather than information.
#
# This list covers common Indonesian stopwords plus informal variants
# (gua, gue, kalo, udah, tp, dgn, etc.) that dominate YouTube comments.
# For production use, consider augmenting with the Sastrawi stopword list.

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

# ---------------------------------------------------------------------------
# HOMOGLYPH MAP — Cyrillic and Greek characters that look like Latin
# ---------------------------------------------------------------------------
# NFKC normalization handles decorative Unicode (mathematical bold, full-width,
# enclosed alphanumerics, etc.) but it does NOT transliterate across different
# Unicode scripts. A spammer can write "dаftаr" using Cyrillic 'а' (U+0430)
# instead of Latin 'a' (U+0061) — visually identical, but NFKC won't touch it.
#
# This mapping covers the most commonly abused homoglyphs found in Indonesian
# online gambling spam comments.

HOMOGLYPH_MAP = str.maketrans({
    # Cyrillic → Latin
    "\u0430": "a",  # а → a
    "\u0435": "e",  # е → e
    "\u043E": "o",  # о → o
    "\u0440": "p",  # р → p  (looks like 'p', not 'r')
    "\u0441": "c",  # с → c
    "\u0445": "x",  # х → x
    "\u0456": "i",  # і → i  (Ukrainian)
    "\u0455": "s",  # ѕ → s
    "\u0454": "e",  # є → e
    "\u0410": "A",  # А → A
    "\u0415": "E",  # Е → E
    "\u041E": "O",  # О → O
    "\u0420": "P",  # Р → P
    "\u0421": "C",  # С → C
    "\u0422": "T",  # Т → T  (rotated, sometimes used)
    "\u0425": "X",  # Х → X
    # Greek → Latin
    "\u03BD": "v",  # ν → v
    "\u03BF": "o",  # ο → o
    "\u03B1": "a",  # α → a
    "\u03C1": "p",  # ρ → p
    # Thai / lain-lain → Latin (huruf script lain yang BENTUKNYA mirip Latin)
    # Spammer memilih huruf dari script lain yang mirip huruf Latin untuk
    # memecah deteksi kata kunci, contoh "ro๓a" (Thai ๓ mirip huruf m).
    "\u0E53": "m",  # ๓ (angka Thai 3) → m  (bentuknya mirip huruf m)
})


# ---------------------------------------------------------------------------
# CORE CLEANING FUNCTION
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Run a raw comment string through the full 7-step preprocessing pipeline.

    This function is called identically during both training (on the dataset)
    and inference (on live comments from the extension). Using the same
    function in both contexts is what guarantees training-serving consistency.

    Args:
        text: Raw comment text, potentially containing Unicode decorative
              fonts, emojis, zero-width characters, or Cyrillic homoglyphs.

    Returns:
        Cleaned string ready for TF-IDF vectorization.
        Returns an empty string if input is invalid or becomes empty after cleaning.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Step 1: Strip zero-width and invisible characters
    # These characters (zero-width space, BOM, zero-width non-joiner, etc.)
    # are invisible in any text editor but can silently break tokenization.
    # Example: "d​a​f​t​a​r" with zero-width spaces → "daftar" after stripping.
    zero_width_chars = (
        "\u200B"  # Zero-width space
        "\u200C"  # Zero-width non-joiner
        "\u200D"  # Zero-width joiner
        "\uFEFF"  # Byte order mark (BOM)
        "\u00AD"  # Soft hyphen
        "\u200E"  # Left-to-right mark
        "\u200F"  # Right-to-left mark
    )
    for char in zero_width_chars:
        text = text.replace(char, "")

    # Step 2: NFKC Unicode normalization
    # NFKC (Normalization Form Compatibility Decomposition + Canonical Composition)
    # collapses decorative Unicode variants back to standard ASCII characters.
    # This handles the majority of spammer font tricks:
    #   𝑅𝒪𝑀𝒜𝟦𝒟  →  ROMA4D   (Mathematical Italic / Bold)
    #   Ｄａｆｔａｒ →  Daftar   (Full-width Latin)
    #   🅓🅐🅕🅣🅐🅡  →  DAFTAR  (Enclosed Alphanumeric Supplement)
    text = unicodedata.normalize("NFKC", text)

    # Step 2b: Strip combining diacritical marks (Unicode category "Mn")
    # NFKC normalization does NOT remove combining marks — it only collapses
    # decorative font variants. Spammers exploit this by inserting combining
    # characters (e.g. U+0332 COMBINING LOW LINE) between or after letters
    # to break keyword detection:
    #   P͟U͟L͟A͟U͟W͟I͟N  →  tanpa step ini, tiap ͟ diganti spasi oleh Step 6
    #                      → tiap huruf jadi token sendiri → semua dihapus len<=1
    #                      → string kosong → false non_spam
    #
    # unicodedata.category(c) == "Mn" menangkap semua "Mark, Nonspacing" —
    # termasuk combining underline, combining accent, dan trik serupa.
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    # Step 2c: Unwrap karakter tunggal yang dibungkus kurung / tanda baca.
    # Spammer memecah brand jadi per-huruf dengan membungkus tiap karakter:
    #   [P][U][L][A][U][7][7][7]  →  tanpa step ini, Step 6 mengubah tiap
    #     kurung jadi spasi → tiap huruf jadi token tunggal → semua dibuang
    #     (len<=1) → string kosong → false non_spam.
    #
    # Regex hanya membuka kurung yang membungkus TEPAT satu karakter word
    # (huruf/angka), jadi kalimat normal dalam kurung — misal "(lihat di sini)"
    # — tidak ikut terpengaruh karena isinya lebih dari satu karakter.
    #   [P] → P   (X) → X   {7} → 7
    text = re.sub(r"[\[(\{]\s*(\w)\s*[\])\}]", r"\1", text)

    # Step 3: Apply homoglyph substitution for Cyrillic/Greek lookalikes
    # NFKC only normalizes within the same Unicode block. It cannot map
    # Cyrillic 'а' to Latin 'a' because they are considered different scripts.
    # The HOMOGLYPH_MAP handles the characters most frequently seen in spam.
    text = text.translate(HOMOGLYPH_MAP)

    # Step 4: Demojize — convert emoji to descriptive text tokens
    # Rather than deleting emojis, we convert them to their text description.
    # This preserves the semantic signal they carry:
    #   🎰 → slot_machine   (strong spam indicator)
    #   💰 → money_bag      (strong spam indicator)
    #   👍 → thumbs_up      (neutral / non-spam indicator)
    # After demojize, strip the surrounding colons so "slot_machine" becomes
    # a clean token that TF-IDF can work with.
    text = emoji.demojize(text, language="en")
    text = re.sub(r":([a-zA-Z0-9_]+):", r" \1 ", text)

    # Step 5: Lowercase
    text = text.lower()

    # Step 5b-i: Leet speak normalization — ganti digit yang dipakai sebagai huruf
    # Spammer sering mengganti huruf dengan angka yang mirip secara visual (leet speak)
    # untuk menghindari deteksi kata kunci:
    #   H0KI777 → HOKI777,  s1tus → situs,  d3p0s1t → deposit
    #
    # Substitusi ini HANYA berlaku dalam konteks alphanumeric (digit diapit huruf).
    # Regex \b[a-z0-9]+\b menarget "kata" yang berisi campuran huruf + digit,
    # lalu mengganti digit tertentu dengan padanan huruf.
    #
    # Kenapa hanya 0→o dan 1→i?
    # - '0' (nol) sebagai 'O' adalah substitusi paling umum di spam judol Indonesia
    # - '1' sebagai 'I' atau 'L' juga sering (s1tus, dep0s1t)
    # - '3'→'e', '4'→'a', '5'→'s' jarang cukup ambigu di konteks ini dan berisiko
    #   memutilasi angka legitimate (skor 354, dsb)
    #
    # Substitusi dilakukan SETELAH lowercase agar regex cukup satu bentuk, dan
    # SEBELUM Step 5b agar brand yang memakai leet speak terdeteksi pola brand.
    def _normalize_leet(m):
        word = m.group(0)
        word = word.replace("0", "o").replace("1", "i")
        return word
    text = re.sub(r'\b[a-z0-9]*[0-9][a-z0-9]*\b', _normalize_leet, text)

    # Step 5b: Brand canonicalization — ganti pola brand judol dengan token universal
    # Harus dilakukan SETELAH lowercase (Step 5) dan SEBELUM hapus digit (Step 6).
    # Lihat komentar JUDOL_BRAND_PATTERN di atas untuk penjelasan lengkap.
    text = JUDOL_BRAND_PATTERN.sub("judolbrand", text)

    # Step 6: Remove URLs and all non-alphabetic characters
    # URLs are removed first as a named pattern; then everything that isn't
    # a plain ASCII letter or whitespace is stripped. This removes punctuation,
    # digits, and any remaining exotic characters in a single pass.
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)

    # Step 7: Collapse whitespace, remove stopwords, drop single-char tokens
    text = re.sub(r"\s+", " ", text).strip()
    tokens = [
        word for word in text.split()
        if word not in STOPWORDS_ID and len(word) > 1
    ]

    return " ".join(tokens)


def preprocess_batch(texts) -> list:
    """
    Apply clean_text() to a list or pandas Series of strings.

    Args:
        texts: Iterable of raw text strings.

    Returns:
        List of cleaned strings, one per input.
    """
    return [clean_text(t) for t in texts]


# ---------------------------------------------------------------------------
# MANUAL TEST — runs only when this file is executed directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_cases = [
        # Unicode decorative font (Mathematical Italic)
        "𝑅𝒪𝑀𝒜𝟦𝒟 daftar sekarang bonus gede!",
        # Cyrillic homoglyphs mixed into Latin text
        "dаftаr sekаrаng dаpаt bоnus 100%",
        # Full-width + circled characters (PULAU777 brand obfuscation)
        "ＰⓤＬＡＵ777, tempatnya peluang besar",
        # Combining underline trick (PULAUWIN brand) — Step 2b fix
        # Tanpa Step 2b: tiap huruf jadi token sendiri, semua terhapus (len<=1) → empty string
        # Dengan Step 2b: U+0332 dihapus → PULAUWIN bertahan sebagai satu token
        "Bukan ngebet, tapi nyaman di P̲̲U̲̲L̲̲A̲̲U̲̲W̲̲I̲̲N̲̲?",
        # Emoji-heavy spam
        "🎰💰 slot gacor hari ini, WD cepat, daftar gratis 🎁🔥",
        # Normal non-spam comment
        "Video ini sangat membantu buat gua yang lagi belajar. Terimakasih kak!",
        # Zero-width spaces between letters
        "d\u200ba\u200bf\u200bt\u200ba\u200br sekarang bonus member baru",
        # Brand canonicalization (Step 5b) \u2014 digit suffix
        "kalau udah masakan nusantara pasti buat ngiler, salam Jp KEJU4D",
        # Brand canonicalization (Step 5b) \u2014 angka 2-digit
        "memang bikin selera naik, seperti di BETAWI77 bikin naik terus",
        # Brand canonicalization (Step 5b) \u2014 suffix QQ (poker/domino)
        "bikin mood gw balik lagi, salam sukses dari HOBIQQ",
    ]

    print("=" * 65)
    print("PREPROCESSING PIPELINE TEST")
    print("=" * 65)
    for i, text in enumerate(test_cases, 1):
        cleaned = clean_text(text)
        print(f"\n[{i}] INPUT  : {text}")
        print(f"    OUTPUT : {cleaned}")
    print("\n" + "=" * 65)
