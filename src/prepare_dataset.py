"""
prepare_dataset.py
==================
Converts raw scraped JSON into a clean, balanced CSV ready for training.

Steps:
1. Load spam data from scraper/final_spam.json
2. Filter by spam_score >= 80 to reduce label noise
3. Generate synthetic non-spam comments to balance the dataset
4. Shuffle and save to data/comments.csv

Run this script BEFORE train.py:
    python src/prepare_dataset.py

When to re-run:
- After scraping new spam data
- After replacing synthetic non-spam with real scraped non-spam data
"""

import os
import sys
import json
import re
import random
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_JSON = os.path.join(BASE_DIR, "scraper", "final_spam.json")
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

# Target number of non-spam samples to generate.
# Rationale for ~700 with ~1400 spam (2:1 ratio):
#
# A perfectly balanced 1:1 ratio sounds ideal but can mislead the model —
# in real YouTube comment sections, spam is genuinely more frequent on
# certain videos. A 2:1 ratio (spam:non-spam) reflects a realistic
# distribution while still giving the model enough non-spam examples
# to learn from.
#
# IMPORTANT: These are SYNTHETIC samples. Once you have real scraped
# non-spam data from YouTube, replace this generation step by loading
# from a separate JSON file and set this constant to 0.
# Real data will always outperform synthetic data.
NON_SPAM_TARGET = 700

# ---------------------------------------------------------------------------
# SYNTHETIC NON-SPAM DATA
# ---------------------------------------------------------------------------
# These are representative Indonesian YouTube comments from non-spam categories.
# Categories covered: tutorials, gaming, music, general reactions, questions.
#
# Diversity is intentional: varied length, tone, topic, and writing style
# help the model generalize rather than memorize surface patterns.

NON_SPAM_TEMPLATES = [
    # Educational / tutorial reactions
    "Penjelasannya mudah dipahami, makasih sudah berbagi ilmunya",
    "Akhirnya nemu penjelasan yang bener-bener masuk di kepala",
    "Langsung dipraktekin dan berhasil, tutorial ini top banget",
    "Pertama kali nonton langsung subscribe, kualitasnya beda",
    "Konten ini beneran bantu gua yang lagi belajar dari nol",
    "Tolong bikin lanjutan videonya, penasaran sama materi berikutnya",
    "Penjelasannya detail banget, tiap poin dikasih contoh yang jelas",
    "Udah nonton 3 kali masih nemu hal baru yang kelewatan",
    "Ini yang gua cari dari minggu lalu, makasih udah upload",
    "Gua rekomendasiin channel ini ke semua temen yang mau belajar",
    "Cara ngajarnya santai tapi tetep informatif, cocok banget buat pemula",
    "Ada yang tau resource lain yang setara kualitasnya sama channel ini",
    "Konten kayak gini harusnya yang viral bukan yang gimmick doang",
    "Dapet insight baru dari video ini yang belum pernah gua temuin sebelumnya",
    "Makasih udah konsisten upload, channel ini jadi referensi utama gua",
    "Boleh minta source codenya kak? Mau coba modifikasi sendiri",
    "Pertanyaan: kalau datanya beda format apakah langkahnya tetap sama?",
    "Gua share ke grup belajar, semua pada suka dan bilang makasih",
    "Semoga makin banyak yang tau channel ini, kontennya terlalu bagus",
    "Nonton ini sambil ngopi pagi, mood belajar langsung naik drastis",
    "Ini tipe konten yang bikin gua betah di YouTube berjam-jam",
    "Kualitas audio videonya jernih banget, nyaman didengernya",
    "Gua udah ikutin dari episode pertama dan kualitasnya konsisten bagus",
    "Ada kesalahan kecil di menit 8 angkanya harusnya 0.05 bukan 0.5",
    "Pengen ngobrol langsung, ada discord atau komunitas yang bisa diikutin",
    "Semua penjelasan dikemas rapi dan mudah diikuti dari awal sampai akhir",
    "Makasih banyak sudah berbagi ilmu ini secara gratis",

    # Gaming comments
    "Build ini op banget, langsung nyoba di ranked dan langsung menang",
    "Cara mainnya beda banget dari youtuber lain yang pernah gua tonton",
    "Gameplay-nya clean, gak ada momen panik yang bikin malu",
    "Strategi ini cocok buat solo queue, gua udah coba dan lumayan work",
    "Bisa kasih tips buat yang masih di rank bawah? Susah naik sendiri",
    "Map awareness lu bagus banget, jarang ada yang bisa kayak gitu",
    "Gua udah nonton ulang bagian teamfight-nya 5 kali, bener-bener keren",
    "Setting yang lu pake apa? Mouse dan keyboard brand apa yang dipake",
    "Konten gameplay lu selalu chill, cocok ditonton buat relaksasi",
    "GG wp, lawan tim kalian juga main bagus sebenernya",
    "Next video minta yang duo ranked bareng subscriber dong",
    "Rank berapa sekarang? Penasaran udah sampe mana progressnya",
    "Tutorial hero ini paling lengkap yang pernah gua tonton di YouTube",
    "Ini sih bukan luck, emang skillnya udah di atas rata-rata",
    "Mechanical skills lu gila, udah berapa tahun main game ini",

    # Music / entertainment
    "Suaranya merdu banget, langsung masuk playlist favorit gua",
    "Cover ini lebih enak didengernya dari versi originalnya menurut gua",
    "Arrangement musiknya kreatif, aransemennya beda dari yang lain",
    "Kapan rilis single originalnya? Penasaran sama karya originalnya",
    "Udah diputar lebih dari 50 kali masih belum bosen juga",
    "Gua dengerin ini sambil kerja, produktivitas langsung naik",
    "Emosi yang disampaiin lewat suaranya bisa kerasa banget",
    "Teknik vokalnya solid, vibrato dan phrasing-nya bagus",
    "Harusnya lebih banyak yang tau penyanyi sebagus ini",
    "Liriknya relatable banget sama situasi yang lagi gua rasain sekarang",

    # General reactions and questions
    "Setuju banget sama poin ketiga yang disebutkan di video ini",
    "Gua malah baru tau hal ini padahal udah lama ikutin topik ini",
    "Ada yang mau diskusi lebih lanjut soal topik ini di kolom komentar",
    "Perspektifnya menarik, bikin gua mikir dari sudut pandang yang beda",
    "Ini jawaban dari pertanyaan yang udah gua cari dari beberapa bulan lalu",
    "Bahas topik lanjutannya dong, masih banyak yang pengen ditanya",
    "Konten ini relate sama pengalaman gua waktu baru mulai belajar",
    "Gua tunjukin ini ke dosen dan beliau bilang ini penjelasan yang bagus",
    "Jangan berhenti bikin konten, channel ini sumber belajar utama gua",
    "Sarannya masuk akal dan langsung bisa diaplikasikan di kehidupan nyata",
    "Nonton ini sebelum tidur, malah jadi terlalu semangat dan ga bisa tidur",
    "Pengen bisa di level ini, masih jauh tapi semoga bisa tercapai",
    "Ini channel pertama yang bikin gua betah nonton video lebih dari 20 menit",
    "Terus berkarya ya, ilmu yang disebarkan pasti jadi manfaat buat banyak orang",
    "Dari sekian konten yang pernah gua konsumsi ini yang paling berkesan",
    "Waktu nonton berasa cepet banget, ga kerasa udah 1 jam berlalu",
    "Penjelasan step by step kayak gini yang paling gampang diikutin pemula",
    "Gua udah 3 minggu konsisten belajar dari sini dan hasilnya terasa",
    "Subtitle bahasa Indonesia akan sangat membantu yang baru belajar",
    "Gua download videonya buat ditonton offline, sayang kalau kelewatan",
    "Lebih suka format video panjang yang detail daripada yang singkat",
    "Baru subscribe tapi langsung marathon nonton dari video pertama",
    "Ada yang bisa rekomendasiin buku bacaan yang topiknya sejalan sama ini",
    "Kualitas produksi videonya jauh meningkat dibanding beberapa bulan lalu",
    "Tiap kali ada video baru langsung nonton, udah jadi ritual harian",
    "Pengen banget ikut kelas atau workshop kalau ada yang diselenggarakan",
    "Gua bagiin ke komunitas online dan responsnya positif semua",
    "Satu hal yang bikin channel ini beda adalah cara penyampaiannya",
    "Ga nyangka ada yang mau berbagi ilmu seberharga ini secara gratis",
    "Terimakasih atas dedikasinya, pasti banyak effort yang masuk ke tiap video",

    # Short natural reactions
    "Mantap!",
    "Keren banget",
    "Makasih banyak kak",
    "Ditunggu video selanjutnya",
    "Auto subscribe",
    "Top kontennya",
    "Bermanfaat banget ini",
    "Suka sama gayanya ngajar",
    "Ini yang gua butuhin",
    "Wah baru tau nih",
    "Nice, langsung dipraktekin",
    "Sangat membantu, terima kasih",
    "Penjelasan terbaik yang pernah gua denger",
    "GG",
    "Lanjutkan terus kak",
    "Konten berkualitas",
    "Mudah dipahami",
    "Recommended banget",
]


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
    print(f"    ↳ brand_pattern false pos. : {false_positive_dropped}")
    print(f"  Total spam collected         : {len(spam_entries)}")

    return spam_entries


def generate_non_spam_data(target_count: int) -> list:
    """
    Generate synthetic non-spam comments by sampling and lightly varying
    the NON_SPAM_TEMPLATES list.

    Variation techniques applied:
    - Random sampling with replacement
    - Occasionally append filler phrases to create length variation
    - Shuffle word order is intentionally NOT done (would break grammar)

    Args:
        target_count: Number of non-spam samples to produce.

    Returns:
        List of dicts with keys 'text' and 'label'.
    """
    fillers = [
        ", semoga makin berkembang",
        " - terimakasih ya",
        ", keep it up!",
        " btw",
        ", salam dari Surabaya",
        ", salam kenal",
        " hehe",
        ", nunggu video berikutnya",
    ]

    results = []
    templates = NON_SPAM_TEMPLATES.copy()

    for i in range(target_count):
        base = random.choice(templates)
        # Add a filler to ~30% of samples to increase variety
        if random.random() < 0.30:
            base = base + random.choice(fillers)
        results.append({"text": base, "label": "non_spam"})

    return results


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
          f"≈ {len(spam)/max(len(non_spam),1):.1f}:1")
    print(f"\n  Saved to: {output_path}")


def main():
    print("=" * 60)
    print("DATASET PREPARATION")
    print("=" * 60)

    print(f"\n[1/3] Loading spam data (threshold >= {SPAM_SCORE_THRESHOLD})...")
    spam_data = load_spam_data(INPUT_JSON, SPAM_SCORE_THRESHOLD)

    print(f"\n[2/3] Generating {NON_SPAM_TARGET} synthetic non-spam samples...")
    non_spam_data = generate_non_spam_data(NON_SPAM_TARGET)
    print(f"  Generated: {len(non_spam_data)} samples")

    print("\n[3/3] Merging, shuffling, and saving dataset...")
    build_and_save_dataset(spam_data, non_spam_data, OUTPUT_CSV)

    print("\nDone. Run training next:")
    print("  python src/train.py")
    print("=" * 60)


if __name__ == "__main__":
    random.seed(42)
    main()
