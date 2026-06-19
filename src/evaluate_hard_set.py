"""
evaluate_hard_set.py
====================
Evaluasi model terhadap "hard test set" — komentar ambigu yang secara leksikal
mirip spam tapi bukan promosi judi.

KENAPA PERLU EVALUASI TERPISAH?
---------------------------------
Test set biasa (80/20 split dari comments.csv) berisi komentar yang relatif
mudah dibedakan: spam eksplisit vs komentar sehari-hari yang netral. Angka
akurasi dari test set biasa tidak mencerminkan kemampuan model menghadapi
kasus abu-abu:

  "link hondatoto penipu bisa mengubah no rek dana kita secepatny hati2"
  -> Bukan promosi — ini peringatan. Tapi menyebut nama brand judol.
  -> Model (dan hybrid rule) kemungkinan salah klasifikasikan sebagai spam.

Hard test set dirancang khusus untuk mengukur kasus seperti ini. Hasilnya
dilaporkan TERPISAH dari angka evaluasi utama — bukan untuk menggantikannya,
tapi sebagai lapisan analisis tambahan yang jujur tentang batasan model.

SUMBER DATA:
  data/hard_test_set.csv — komentar dari video YouTube bertema judi online
  (ID: kM99uBssHvQ). Awalnya scraper menandai semua sebagai spam, tapi setelah
  review manual 70 di antaranya dikonfirmasi bukan spam (diskusi/kritik/pengalaman
  buruk, bukan promosi).

Jalankan:
    python src/evaluate_hard_set.py
"""

import os
import sys
import csv
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.preprocessing import clean_text

HARD_TEST_PATH = os.path.join(BASE_DIR, "data", "hard_test_set.csv")
MODEL_PATH     = os.path.join(BASE_DIR, "model", "svm_model.joblib")

# Sama persis dengan HARD_SPAM_SIGNALS di server.py
HARD_SPAM_SIGNALS = {
    "gacor", "scatter", "jackpot", "maxwin", "togel", "toto", "rtp",
    "slot", "withdraw", "deposit",
    "pstoto", "jptogel", "supermoney", "xuxu", "bardi",
    "bukit", "dora", "pluto", "jalak",
    "pangeran", "kyt",
    "pulauwin",
    "judolbrand",
}


def has_hard_spam_signal(cleaned_text: str) -> bool:
    words = set(cleaned_text.split())
    return bool(words & HARD_SPAM_SIGNALS)


def predict_with_hybrid(model, text: str) -> dict:
    cleaned = clean_text(text)
    if not cleaned:
        return {"label": "non_spam", "confidence": 0.5, "via": "empty_text"}

    raw_label = model.predict([cleaned])[0]
    proba     = model.predict_proba([cleaned])[0]
    classes   = list(model.classes_)
    confidence = float(proba[classes.index(raw_label)])

    has_signal = has_hard_spam_signal(cleaned)

    if raw_label == "spam" and not has_signal:
        return {"label": "non_spam", "confidence": 0.5, "via": "hybrid_A", "svm": raw_label, "cleaned": cleaned}
    if raw_label == "non_spam" and has_signal:
        return {"label": "spam", "confidence": 0.9, "via": "hybrid_B", "svm": raw_label, "cleaned": cleaned}

    return {"label": raw_label, "confidence": round(confidence, 4), "via": "svm", "cleaned": cleaned}


def main():
    print("=" * 65)
    print("HARD TEST SET EVALUATION")
    print("=" * 65)

    if not os.path.exists(HARD_TEST_PATH):
        print(f"[ERROR] Hard test set not found: {HARD_TEST_PATH}")
        print("Buat dulu dengan mengekstrak komentar ambigu ke data/hard_test_set.csv")
        sys.exit(1)

    model = joblib.load(MODEL_PATH)
    print(f"[OK] Model loaded: {MODEL_PATH}\n")

    with open(HARD_TEST_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        entries = list(reader)

    print(f"Total hard examples: {len(entries)}")
    label_dist = {}
    for e in entries:
        label_dist[e["label"]] = label_dist.get(e["label"], 0) + 1
    for lbl, cnt in label_dist.items():
        print(f"  {lbl}: {cnt}")
    print()

    results = []
    for e in entries:
        pred = predict_with_hybrid(model, e["text"])
        pred["true_label"] = e["label"]
        pred["text"]       = e["text"]
        results.append(pred)

    # Hitung metrik per label
    true_non_spam = [r for r in results if r["true_label"] == "non_spam"]
    true_spam     = [r for r in results if r["true_label"] == "spam"]

    fp = [r for r in true_non_spam if r["label"] == "spam"]   # non_spam -> prediksi spam
    tn = [r for r in true_non_spam if r["label"] == "non_spam"]
    fn = [r for r in true_spam     if r["label"] == "non_spam"]
    tp = [r for r in true_spam     if r["label"] == "spam"]

    print("=" * 65)
    print("HASIL EVALUASI")
    print("=" * 65)
    print(f"\nConfusion Matrix:")
    print(f"                  Prediksi non_spam  Prediksi spam")
    print(f"Aktual non_spam   {len(tn):>16}  {len(fp):>13}")
    print(f"Aktual spam       {len(fn):>16}  {len(tp):>13}")

    total = len(results)
    correct = len(tn) + len(tp)
    accuracy = correct / total if total else 0

    # Per-class metrics
    prec_spam = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    rec_spam  = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1_spam   = 2 * prec_spam * rec_spam / (prec_spam + rec_spam) if (prec_spam + rec_spam) > 0 else 0

    prec_ns = len(tn) / (len(tn) + len(fn)) if (len(tn) + len(fn)) > 0 else 0
    rec_ns  = len(tn) / (len(tn) + len(fp)) if (len(tn) + len(fp)) > 0 else 0
    f1_ns   = 2 * prec_ns * rec_ns / (prec_ns + rec_ns) if (prec_ns + rec_ns) > 0 else 0

    f1_macro = (f1_spam + f1_ns) / 2

    print(f"\nAccuracy  : {accuracy:.2%}  ({correct}/{total} benar)")
    print(f"F1-macro  : {f1_macro:.4f}")
    print(f"\nFP (non_spam salah -> spam) : {len(fp)}  <- ini yang paling penting di hard set")
    print(f"FN (spam lolos -> non_spam) : {len(fn)}")

    # Via breakdown
    via_counts = {}
    for r in results:
        via_counts[r.get("via", "?")] = via_counts.get(r.get("via", "?"), 0) + 1
    print(f"\nKeputusan via:")
    for via, cnt in sorted(via_counts.items()):
        desc = {
            "svm": "SVM langsung",
            "hybrid_A": "Hybrid A: spam->non_spam (tidak ada sinyal keras)",
            "hybrid_B": "Hybrid B: non_spam->spam (ada sinyal keras)",
            "empty_text": "Teks kosong setelah preprocessing",
        }.get(via, via)
        print(f"  {via:12} ({cnt:3}x) — {desc}")

    # Detail false positive
    if fp:
        print(f"\n{'='*65}")
        print(f"FALSE POSITIVE ({len(fp)} komentar non_spam yang salah diklasifikasi spam):")
        print(f"{'='*65}")
        for i, r in enumerate(fp, 1):
            safe_text    = r['text'][:100].encode('ascii', 'replace').decode()
            safe_cleaned = r.get('cleaned', '')[:100].encode('ascii', 'replace').decode()
            print(f"\n[{i}] via={r.get('via')}  conf={r.get('confidence'):.2f}")
            print(f"    TEXT   : {safe_text}")
            print(f"    CLEANED: {safe_cleaned}")

    # Simpan ke file
    out_path = os.path.join(BASE_DIR, "reports", "hard_set_evaluation.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"HARD TEST SET EVALUATION\n")
        f.write(f"Model: {MODEL_PATH}\n")
        f.write(f"Hard set: {HARD_TEST_PATH} ({len(entries)} entries)\n\n")
        f.write(f"Accuracy : {accuracy:.2%}\n")
        f.write(f"F1-macro : {f1_macro:.4f}\n")
        f.write(f"FP       : {len(fp)}\n")
        f.write(f"FN       : {len(fn)}\n\n")
        f.write(f"Confusion Matrix:\n")
        f.write(f"                  Prediksi non_spam  Prediksi spam\n")
        f.write(f"Aktual non_spam   {len(tn):>16}  {len(fp):>13}\n")
        f.write(f"Aktual spam       {len(fn):>16}  {len(tp):>13}\n\n")
        if fp:
            f.write(f"FALSE POSITIVES ({len(fp)}):\n")
            for i, r in enumerate(fp, 1):
                f.write(f"\n[{i}] via={r.get('via')}  conf={r.get('confidence'):.2f}\n")
                f.write(f"    TEXT   : {r['text']}\n")
                f.write(f"    CLEANED: {r.get('cleaned', '')}\n")

    print(f"\n[OK] Laporan disimpan: {out_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
