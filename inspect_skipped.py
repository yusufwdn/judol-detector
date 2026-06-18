"""
inspect_skipped.py
==================
Dump semua entry dari final_spam.json yang TIDAK masuk ke dataset,
beserta alasan kenapa di-skip.

Run:
    python inspect_skipped.py

Output:
    data/skipped_entries.json  — buka di VS Code untuk review manual
"""

import json
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON = os.path.join(BASE_DIR, "scraper", "final_spam.json")
OUTPUT_JSON = os.path.join(BASE_DIR, "data", "skipped_entries.json")

SPAM_SCORE_THRESHOLD = 80

BRAND_RESCUE_PATTERN = re.compile(r'\b[A-Z]{2,}\d+[A-Z0-9]*\b')
BRAND_SUFFIX_PATTERN  = re.compile(r'\b[A-Z]{4,}(?:TOTO|BET|WIN|QQ)\b')

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

passed_threshold = 0
rescued = 0
skipped = []

for entry in raw_data:
    score      = entry.get("spam_score", 0)
    text       = entry.get("original_text", "").strip()
    normalized = entry.get("normalized_text", "").strip()
    signals    = entry.get("active_signals", [])

    if not text:
        continue

    if score >= SPAM_SCORE_THRESHOLD:
        passed_threshold += 1
        continue

    if "brand_pattern" in signals and (
        BRAND_RESCUE_PATTERN.search(normalized)
        or BRAND_SUFFIX_PATTERN.search(normalized)
    ):
        rescued += 1
        continue

    # Ini yang di-skip — catat alasannya
    if "brand_pattern" in signals:
        reason = f"brand_pattern hadir tapi normalized_text tidak cocok BRAND_RESCUE/SUFFIX. score={score}"
    else:
        reason = f"score rendah ({score}), tidak ada brand_pattern. signals={signals}"

    skipped.append({
        "score"          : score,
        "signals"        : signals,
        "reason_skipped" : reason,
        "original_text"  : text,
        "normalized_text": normalized,
    })

# Urutkan: brand_pattern dulu (paling mungkin ada spam nyata), lalu sisanya
skipped.sort(key=lambda x: ("brand_pattern" not in x["signals"], -x["score"]))

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(skipped, f, ensure_ascii=False, indent=2)

print(f"Total di JSON          : {len(raw_data)}")
print(f"Lolos threshold >=80   : {passed_threshold}")
print(f"Diselamatkan brand regex: {rescued}")
print(f"Di-skip (disimpan)     : {len(skipped)}")
print(f"\nOutput: {OUTPUT_JSON}")
print("\n--- PREVIEW 5 ENTRY PERTAMA ---")
for i, e in enumerate(skipped[:5], 1):
    text_safe = e['original_text'][:120].encode('ascii', 'replace').decode()
    norm_safe = e['normalized_text'][:120].encode('ascii', 'replace').decode()
    print(f"\n[{i}] score={e['score']} | signals={e['signals']}")
    print(f"     SKIP REASON: {e['reason_skipped']}")
    print(f"     TEXT: {text_safe}")
    print(f"     NORM: {norm_safe}")
