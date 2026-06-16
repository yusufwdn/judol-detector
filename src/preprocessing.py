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

PIPELINE ORDER (7 STEPS)
--------------------------
Step 1: Strip zero-width characters  — invisible chars that break tokenization
Step 2: NFKC Unicode normalization   — collapse decorative Unicode to ASCII
Step 3: Cyrillic/Greek homoglyph fix — NFKC cannot cross script boundaries
Step 4: Emoji demojize               — convert emoji to descriptive text tokens
Step 5: Lowercase
Step 6: Remove URLs and non-alpha characters
Step 7: Remove stopwords
"""

import re
import unicodedata
import emoji


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
        # Full-width characters
        "Ｄａｆｔａｒ　ｓｅｋａｒａｎｇ　ｂｏｎｕｓ　ｂｅｓａｒ",
        # Emoji-heavy spam
        "🎰💰 slot gacor hari ini, WD cepat, daftar gratis 🎁🔥",
        # Normal non-spam comment
        "Video ini sangat membantu buat gua yang lagi belajar. Terimakasih kak!",
        # Zero-width spaces between letters
        "d\u200ba\u200bf\u200bt\u200ba\u200br sekarang bonus member baru",
    ]

    print("=" * 65)
    print("PREPROCESSING PIPELINE TEST")
    print("=" * 65)
    for i, text in enumerate(test_cases, 1):
        cleaned = clean_text(text)
        print(f"\n[{i}] INPUT  : {text}")
        print(f"    OUTPUT : {cleaned}")
    print("\n" + "=" * 65)
