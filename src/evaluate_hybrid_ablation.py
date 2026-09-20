"""Ukur dampak aturan heuristik tambahan terhadap akurasi.

Menjalankan model yang sama dua kali per data uji, sekali memakai prediksi SVM
apa adanya dan sekali dengan aturan heuristik diterapkan, lalu membandingkan
akurasi dan F1-macro keduanya.

Hasilnya menunjukkan aturan itu merugikan, dan itu sebabnya
ENABLE_HYBRID_RULES di src/server.py bernilai False. Lihat docs/eksperimen.md.

    python src/evaluate_hybrid_ablation.py
"""

import os
import sys
import csv
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "comments.csv")
HARD_TEST_PATH = os.path.join(BASE_DIR, "data", "hard_test_set.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "svm_model.joblib")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, BASE_DIR)
from src.preprocessing import clean_text, preprocess_batch

# Sama persis dengan HARD_SPAM_SIGNALS di server.py, wajib disinkronkan manual
# kalau daftar di server.py berubah.
HARD_SPAM_SIGNALS = {
    "gacor", "scatter", "jackpot", "maxwin", "togel", "toto", "rtp",
    "withdraw",
    "pstoto", "jptogel", "supermoney", "xuxu", "bardi",
    "bukit", "dora", "pluto", "jalak",
    "pangeran", "kyt",
    "pulauwin",
    "judolbrand",
}


def has_hard_spam_signal(cleaned_text: str) -> bool:
    return bool(set(cleaned_text.split()) & HARD_SPAM_SIGNALS)


def apply_hybrid(svm_label: str, cleaned_text: str) -> str:
    """Reproduksi logika hybrid rule A & B dari server.py (label saja, tanpa confidence)."""
    has_signal = has_hard_spam_signal(cleaned_text)
    if svm_label == "spam" and not has_signal:
        return "non_spam"
    if svm_label == "non_spam" and has_signal:
        return "spam"
    return svm_label


def evaluate(name: str, model, texts_cleaned: list, y_true: list) -> dict:
    """Hitung metrik untuk SVM-only vs SVM+Hybrid pada satu dataset evaluasi."""
    y_svm = list(model.predict(texts_cleaned))
    y_hybrid = [apply_hybrid(svm_label, c) for svm_label, c in zip(y_svm, texts_cleaned)]

    def metrics(y_pred):
        acc = accuracy_score(y_true, y_pred)
        f1m = f1_score(y_true, y_pred, average="macro", zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=["non_spam", "spam"])
        fp = int(cm[0][1])  # non_spam salah -> spam
        fn = int(cm[1][0])  # spam salah -> non_spam
        return {"accuracy": acc, "f1_macro": f1m, "fp": fp, "fn": fn}

    svm_metrics = metrics(y_svm)
    hybrid_metrics = metrics(y_hybrid)

    print(f"\n{'='*70}")
    print(f"DATASET: {name}  (n={len(y_true)})")
    print(f"{'='*70}")
    print(f"{'Mode':<18}{'Accuracy':>10}{'F1-macro':>10}{'FP':>8}{'FN':>8}")
    print(f"{'SVM murni':<18}{svm_metrics['accuracy']:>10.2%}{svm_metrics['f1_macro']:>10.4f}"
          f"{svm_metrics['fp']:>8}{svm_metrics['fn']:>8}")
    print(f"{'SVM + Hybrid':<18}{hybrid_metrics['accuracy']:>10.2%}{hybrid_metrics['f1_macro']:>10.4f}"
          f"{hybrid_metrics['fp']:>8}{hybrid_metrics['fn']:>8}")

    delta_acc = hybrid_metrics["accuracy"] - svm_metrics["accuracy"]
    delta_f1 = hybrid_metrics["f1_macro"] - svm_metrics["f1_macro"]
    print(f"\nDelta (Hybrid - SVM murni): accuracy {delta_acc:+.2%}, F1-macro {delta_f1:+.4f}")

    return {
        "dataset": name,
        "n": len(y_true),
        "svm": svm_metrics,
        "hybrid": hybrid_metrics,
        "delta_accuracy": delta_acc,
        "delta_f1_macro": delta_f1,
    }


def main():
    print("=" * 70)
    print("ABLATION STUDY: SVM MURNI vs SVM + HYBRID RULES")
    print("=" * 70)

    model = joblib.load(MODEL_PATH)
    print(f"[OK] Model loaded: {MODEL_PATH}")

    results = []

    # --- Dataset 1: train-test split, SAMA dengan train.py ---
    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "label"])
    texts = df["text"].astype(str).tolist()
    labels = df["label"].tolist()
    cleaned_all = preprocess_batch(texts)
    _, X_test, _, y_test = train_test_split(
        cleaned_all, labels, test_size=0.2, random_state=42, stratify=labels
    )
    results.append(evaluate("Train-test split (20% holdout, n=test set)", model, X_test, y_test))

    # --- Dataset 2: hard test set ---
    with open(HARD_TEST_PATH, encoding="utf-8") as f:
        hard_entries = list(csv.DictReader(f))
    hard_cleaned = [clean_text(e["text"]) for e in hard_entries]
    hard_labels = [e["label"] for e in hard_entries]
    results.append(evaluate("Hard test set (141 kasus ambigu)", model, hard_cleaned, hard_labels))

    # --- Simpan laporan ---
    out_path = os.path.join(REPORTS_DIR, "hybrid_ablation.txt")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("ABLATION STUDY: SVM MURNI vs SVM + HYBRID RULES\n")
        f.write(f"Model: {MODEL_PATH}\n\n")
        for r in results:
            f.write(f"{'='*70}\n")
            f.write(f"Dataset: {r['dataset']} (n={r['n']})\n")
            f.write(f"{'='*70}\n")
            f.write(f"{'Mode':<18}{'Accuracy':>10}{'F1-macro':>10}{'FP':>8}{'FN':>8}\n")
            f.write(f"{'SVM murni':<18}{r['svm']['accuracy']:>10.2%}{r['svm']['f1_macro']:>10.4f}"
                    f"{r['svm']['fp']:>8}{r['svm']['fn']:>8}\n")
            f.write(f"{'SVM + Hybrid':<18}{r['hybrid']['accuracy']:>10.2%}{r['hybrid']['f1_macro']:>10.4f}"
                    f"{r['hybrid']['fp']:>8}{r['hybrid']['fn']:>8}\n")
            f.write(f"Delta: accuracy {r['delta_accuracy']:+.2%}, F1-macro {r['delta_f1_macro']:+.4f}\n\n")

    print(f"\n[OK] Laporan tersimpan: {out_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
