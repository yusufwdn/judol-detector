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
    # Regex that matches all-caps words containing digits — characteristic of
    # Indonesian gambling brand names after NFKC normalization.
    # Examples that MATCH  : WIFI4D, BATRE4D, PELATIH4D, ROMA4D, GACOR88
    # Examples that DON'T  : kesambet, ribet,abet, sbobet (lowercase)
    BRAND_RESCUE_PATTERN = re.compile(r'\b[A-Z]{2,}\d+[A-Z0-9]*\b')

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

        if not text:
            skipped_low_score += 1
            continue

        # Pass 1: primary threshold — high confidence, always include
        if score >= threshold:
            spam_entries.append({"text": text, "label": "spam"})

        # Pass 2: rescue entries that only triggered brand_pattern at low score
        # but whose normalized text contains a real brand name pattern.
        #
        # Why only brand_pattern entries?
        # If score < threshold AND signals != ['brand_pattern'], the entry
        # triggered only weak secondary signals (emoji spam, high symbol ratio,
        # excessive caps) without any brand or link — too noisy to trust.
        elif signals == ["brand_pattern"] and BRAND_RESCUE_PATTERN.search(normalized):
            spam_entries.append({"text": text, "label": "spam"})
            rescued += 1

        else:
            # Could be a false positive like "kesambet" (brand_pattern on "bet")
            # or genuinely weak signal. Skip either way.
            skipped_low_score += 1
            if signals == ["brand_pattern"] and score < threshold:
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
            entries.append({"text": text, "label": "non_spam"})

    skipped = len(raw_data) - len(entries)
    print(f"  Total entries in JSON : {len(raw_data)}")
    if skipped:
        print(f"  Skipped (empty text)  : {skipped}")
    print(f"  Loaded                : {len(entries)}")
    return entries



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

    print(f"\n[1/3] Loading spam data (threshold >= {SPAM_SCORE_THRESHOLD})...")
    spam_data = load_spam_data(INPUT_SPAM_JSON, SPAM_SCORE_THRESHOLD)

    print(f"\n[2/3] Loading non-spam data...")
    non_spam_data = load_non_spam_data(INPUT_NON_SPAM_JSON)

    print("\n[3/3] Merging, shuffling, and saving dataset...")
    build_and_save_dataset(spam_data, non_spam_data, OUTPUT_CSV)

    print("\nDone. Run training next:")
    print("  python src/train.py")
    print("=" * 60)


if __name__ == "__main__":
    random.seed(42)
    main()
