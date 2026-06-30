"""
prepare_dataset.py
==================
Converts raw scraped JSON into a clean, balanced CSV ready for training.

Steps:
1. Load spam data from scraper/final_spam.json
2. Filter by spam_score >= 80 to reduce label noise
3. Load real non-spam data from scraper/final_non_spam.json (preferred),
   or fall back to synthetic templates if the file is not available
4. Shuffle and save to data/comments.csv

Run this script BEFORE train.py:
    python src/prepare_dataset.py

When to re-run:
- After scraping new spam or non-spam data (run filter.js first, then this)
- After modifying src/preprocessing.py (always re-run to keep pipeline consistent)
"""

import os
import sys
import json
import re
import random
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_SPAM_JSON = os.path.join(BASE_DIR, "scraper", "final_spam.json")
INPUT_NON_SPAM_JSON = os.path.join(BASE_DIR, "scraper", "final_non_spam.json")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "comments.csv")
MANUAL_OVERRIDES_CSV = os.path.join(BASE_DIR, "data", "manual_overrides.csv")

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Minimum spam_score for a scraped entry to be included in training.
#
# Why 80?
# The scraper assigns scores using a heuristic weighted system.
# Entries below 80 may have triggered only weak secondary signals
# (e.g., high emoji ratio alone), which increases the risk of false positives.
# Score >= 80 requires at least one strong primary signal (brand name or
# contact link) plus corroborating secondary signals — a much safer threshold.
#
# Trade-off: raising this value = cleaner data, fewer samples.
#            lowering this value = more samples, more label noise.
SPAM_SCORE_THRESHOLD = 80



def load_spam_data(json_path: str, threshold: int) -> list:
    """
    Load spam entries from the scraped JSON file using a two-pass filter.

    PASS 1 — Primary threshold (score >= threshold):
        High-confidence entries with multiple strong signals. Always included.

    PASS 2 — Brand name rescue (score < threshold, brand_pattern only):
        The scraper's brand_pattern signal matches on substrings, so it fires
        on innocent Indonesian words like "kesambet" (contains "bet") or
        "ribet" — these are false positives that correctly got a low score.

        BUT real gambling brands also sometimes only trigger brand_pattern (score 40)
        when they appear alone without a contact link. Examples:
            WIFI4D, BATRE4D, PELATIH4D, ROMA4D, SBOBET88

        After NFKC normalization (stored in normalized_text), real brand names
        consistently appear as ALL-CAPS words containing digits, e.g. "WIFI4D".
        Natural Indonesian words containing gambling substrings are always
        lowercase and embedded inside a regular sentence.

        The rescue regex targets exactly this pattern:
            \b[A-Z]{2,}\d+[A-Z0-9]*\b  →  "WIFI4D", "BATRE4D", "ROMA4D"
        This pattern is nearly impossible to generate by accident in normal text.

    Uses 'original_text' (not 'normalized_text') for the final dataset.
    See server.py / preprocessing.py for the training-serving consistency rationale.

    Args:
        json_path: Path to the scraped JSON file.
        threshold: Minimum spam_score for the primary pass.

    Returns:
        List of dicts with keys 'text' and 'label'.
    """
    # ---------------------------------------------------------------------------
    # BRAND DETECTION PATTERNS untuk Pass 2 (rescue)
    # ---------------------------------------------------------------------------
    #
    # Pola 1 — huruf (case-insensitive) + digit
    #   Contoh: WIFI4D, freebet88, Koreo138, bbca4d, SlotLions88
    #
    #   Kenapa case-insensitive?
    #   Spammer sering memakai font dekoratif (matematika italic, bold, dll) yang
    #   setelah NFKC normalization di scraper menghasilkan mixed case atau lowercase,
    #   bukan ALL-CAPS:
    #     𝒃𝒃𝒄𝒂4𝒅  →  bbca4d       (math italic → lowercase)
    #     𝐊𝐨𝐫𝐞𝐨𝟏𝟑𝟖 →  Koreo138     (math bold → Title Case)
    #   Dengan flag re.IGNORECASE, brand ini sekarang terdeteksi.
    #
    #   Kenapa aman? Digit tetap WAJIB ada. Kata umum Indonesia seperti
    #   "ribet", "kesambet", "diabet" tidak punya digit → tidak kena.
    BRAND_RESCUE_PATTERN = re.compile(r'\b[A-Z]{2,}\d+[A-Z0-9]*\b', re.IGNORECASE)

    # Pola 2 — Suffix khas brand judi Indonesia TANPA digit
    #   Format: [4+ huruf kapital][TOTO|BET|WIN|QQ]
    #
    #   Kenapa suffix ini aman?
    #   Hampir semua situs judi Indonesia memakai salah satu dari empat suffix ini:
    #     *TOTO  → togel online (NAGAMASTOTO, AGUSTOTO, OMETOTO, ASIKTOTO...)
    #     *BET   → betting/taruhan (MANJURBET, SIAPBET, GONBET...)
    #     *WIN   → slot/menang (PULAUWIN, PUSATWIN, BUAYAWIN, ARJUNAWIN...)
    #     *QQ    → poker/domino online (HOBIQQ, BANDARQQ, DOMINOQQ...)
    #
    #   Kenapa minimum 3 huruf sebelum suffix (diturunkan dari 4)?
    #   Brand pendek seperti OMETOTO (O-M-E = 3 huruf + TOTO) sebelumnya tidak
    #   terdeteksi karena minimum lama adalah 4. Setelah analisis manual 533 entry
    #   yang di-skip, ditemukan banyak brand pendek yang lolos karena aturan ini.
    #   Tetap ALL-CAPS (tidak case-insensitive) untuk mencegah FP dari kata
    #   Indonesia biasa seperti "seribet" atau "ngebet" yang ditulis lowercase.
    #
    #   Contoh yang MATCH  : NAGAMASTOTO, OMETOTO, MANJURBET, PULAUWIN, HOBIQQ
    #   Contoh yang TIDAK  : ngebet (lowercase), seribet (lowercase), MAXWIN (MAX=5? tunggu MAXWIN: M-A-X=3+WIN ✓ sekarang match)
    BRAND_SUFFIX_PATTERN = re.compile(r'\b[A-Z]{3,}(?:TOTO|BET|WIN|QQ)\b')

    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"Scraped JSON not found: {json_path}\n"
            f"Make sure final_spam.json is inside the scraper/ folder."
        )

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    spam_entries = []
    skipped_low_score = 0
    rescued = 0
    false_positive_dropped = 0

    for entry in raw_data:
        score = entry.get("spam_score", 0)
        text = entry.get("original_text", "").strip()
        normalized = entry.get("normalized_text", "").strip()
        signals = entry.get("active_signals", [])
        source = entry.get("video_id", "unknown")

        if not text:
            skipped_low_score += 1
            continue

        # Pass 1: primary threshold — high confidence, always include
        if score >= threshold:
            spam_entries.append({"text": text, "label": "spam", "source": source})

        # Pass 2: rescue entries below threshold that contain a confirmed real
        # gambling brand name in normalized_text.
        #
        # KONDISI LAMA: signals == ["brand_pattern"]  (exact match — hanya 1 sinyal)
        # KONDISI BARU: "brand_pattern" in signals    (membership check — brand bisa hadir
        #               bersamaan dengan sinyal lain seperti emoji_spam / high_symbol_ratio)
        #
        # Kenapa diubah?
        # Spammer yang memakai Unicode obfuscation (𝑅𝒪𝑀𝒜𝟦𝒟, Ｓｌｏｔ, ⓢⓛⓞⓣ) sering juga
        # menggunakan banyak emoji dan simbol sebagai dekorasi. Akibatnya komentar mereka
        # mendapat 2-3 sinyal (brand_pattern + emoji_spam + high_symbol_ratio) sehingga
        # score-nya 60-75, tapi kondisi rescue LAMA mengharuskan tepat 1 sinyal.
        # Mereka ke-skip padahal jelas spam — brand ROMA4D terlihat jelas di normalized_text.
        #
        # Kondisi rescue: brand_pattern sudah terpenuhi dari scraper.
        # Verifikasi tambahan via dua pola brand di normalized_text:
        #   - BRAND_RESCUE_PATTERN : ALL-CAPS + digit  (WIFI4D, ROMA4D)
        #   - BRAND_SUFFIX_PATTERN : [4+huruf]TOTO|BET|WIN  (NAGAMASTOTO, MANJURBET, PULAUWIN)
        elif "brand_pattern" in signals and (
            BRAND_RESCUE_PATTERN.search(normalized)
            or BRAND_SUFFIX_PATTERN.search(normalized)
        ):
            spam_entries.append({"text": text, "label": "spam", "source": source})
            rescued += 1

        else:
            # Could be a false positive like "kesambet" (brand_pattern on "bet"),
            # a soft brand (Miya88 — mixed case, doesn't match ALL-CAPS regex),
            # or genuinely weak signal. Skip either way.
            skipped_low_score += 1
            if "brand_pattern" in signals and score < threshold:
                false_positive_dropped += 1

    print(f"  Total entries in JSON        : {len(raw_data)}")
    print(f"  Passed primary threshold     : {len(spam_entries) - rescued}")
    print(f"  Rescued via brand regex      : {rescued}")
    print(f"  Skipped (low score / noisy)  : {skipped_low_score}")
    print(f"    -> brand_pattern false pos.: {false_positive_dropped}")
    print(f"  Total spam collected         : {len(spam_entries)}")

    return spam_entries


def load_non_spam_data(json_path: str) -> list:
    """
    Load real non-spam entries from scraper/final_non_spam.json.
    Uses 'original_text' for training-serving consistency (same as spam loader).

    Args:
        json_path: Path to final_non_spam.json produced by filter.js.

    Returns:
        List of dicts with keys 'text' and 'label', or empty list if file missing.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(
            f"Non-spam data not found: {json_path}\n"
            f"Scrape non-spam data first:\n"
            f"  node scraper/index.js <VIDEO_ID> video non_spam\n"
            f"  node scraper/filter.js"
        )

    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    entries = []
    for entry in raw_data:
        text = entry.get("original_text", "").strip()
        if text:
            entries.append({"text": text, "label": "non_spam", "source": entry.get("video_id", "unknown")})

    skipped = len(raw_data) - len(entries)
    print(f"  Total entries in JSON : {len(raw_data)}")
    if skipped:
        print(f"  Skipped (empty text)  : {skipped}")
    print(f"  Loaded                : {len(entries)}")
    return entries



def apply_manual_overrides(spam: list, non_spam: list, overrides_path: str):
    """
    Apply manual label corrections from data/manual_overrides.csv.

    KENAPA FUNGSI INI ADA:
    prepare_dataset.py di-generate ulang setiap kali ada scraping baru — artinya
    comments.csv akan ditimpa dan semua koreksi manual (relabeling false positive,
    tambah entry baru) akan hilang. Solusinya: simpan koreksi di file terpisah
    (manual_overrides.csv) yang dibaca setiap kali prepare_dataset.py dijalankan.

    Dua jenis override yang didukung:
    - label=non_spam : hapus entry ini dari daftar spam (false positive)
                       tambahkan sebagai non_spam (jika belum ada)
    - label=spam     : tambahkan entry ini ke daftar spam (jika belum ada)

    Args:
        spam:           List spam dicts dari load_spam_data()
        non_spam:       List non_spam dicts dari load_non_spam_data()
        overrides_path: Path ke data/manual_overrides.csv

    Returns:
        Tuple (spam, non_spam) setelah koreksi diterapkan.
    """
    import csv as csv_module

    if not os.path.exists(overrides_path):
        print("  (tidak ada manual_overrides.csv — dilewati)")
        return spam, non_spam

    with open(overrides_path, "r", encoding="utf-8") as f:
        reader = csv_module.DictReader(f)
        overrides = [(row["text"].strip(), row["label"].strip()) for row in reader]

    fp_texts = {text for text, label in overrides if label == "non_spam"}
    spam_additions = [text for text, label in overrides if label == "spam"]

    # Hapus false positive dari daftar spam
    original_spam_count = len(spam)
    spam = [e for e in spam if e["text"] not in fp_texts]
    removed = original_spam_count - len(spam)

    # Tambahkan false positive sebagai non_spam (hindari duplikat)
    existing_non_spam = {e["text"] for e in non_spam}
    added_non_spam = 0
    for text in fp_texts:
        if text not in existing_non_spam:
            non_spam.append({"text": text, "label": "non_spam", "source": "manual_override"})
            existing_non_spam.add(text)
            added_non_spam += 1

    # Tambahkan spam baru (hindari duplikat)
    existing_spam = {e["text"] for e in spam}
    added_spam = 0
    for text in spam_additions:
        if text not in existing_spam:
            spam.append({"text": text, "label": "spam", "source": "manual_override"})
            existing_spam.add(text)
            added_spam += 1

    print(f"  Loaded {len(overrides)} manual overrides:")
    print(f"    FP dihapus dari spam      : {removed}")
    print(f"    Entry ditambah ke non_spam: {added_non_spam}")
    print(f"    Entry ditambah ke spam    : {added_spam}")
    if removed < len(fp_texts):
        not_found = len(fp_texts) - removed
        print(f"    (FP tidak ditemukan di auto-set: {not_found} — sudah di-skip sebelumnya)")

    return spam, non_spam


def build_and_save_dataset(spam: list, non_spam: list, output_path: str) -> None:
    """
    Merge spam and non-spam lists, shuffle, and save as CSV.

    Args:
        spam: List of spam entry dicts.
        non_spam: List of non-spam entry dicts.
        output_path: Destination CSV path.
    """
    combined = spam + non_spam
    random.shuffle(combined)

    df = pd.DataFrame(combined)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n  Spam samples    : {len(spam)}")
    print(f"  Non-spam samples: {len(non_spam)}")
    print(f"  Total           : {len(combined)}")
    print(f"  Ratio (spam:non): {len(spam)}:{len(non_spam)} "
          f"(~{len(spam)/max(len(non_spam),1):.1f}:1)")
    print(f"\n  Saved to: {output_path}")


def main():
    print("=" * 60)
    print("DATASET PREPARATION")
    print("=" * 60)

    print(f"\n[1/4] Loading spam data (threshold >= {SPAM_SCORE_THRESHOLD})...")
    spam_data = load_spam_data(INPUT_SPAM_JSON, SPAM_SCORE_THRESHOLD)

    print(f"\n[2/4] Loading non-spam data...")
    non_spam_data = load_non_spam_data(INPUT_NON_SPAM_JSON)

    print(f"\n[3/4] Applying manual overrides ({MANUAL_OVERRIDES_CSV})...")
    spam_data, non_spam_data = apply_manual_overrides(spam_data, non_spam_data, MANUAL_OVERRIDES_CSV)

    print("\n[4/4] Merging, shuffling, and saving dataset...")
    build_and_save_dataset(spam_data, non_spam_data, OUTPUT_CSV)

    print("\nDone. Run training next:")
    print("  python src/train.py")
    print("=" * 60)


if __name__ == "__main__":
    random.seed(42)
    main()
