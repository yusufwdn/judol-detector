"""
experiment_features.py
Eksperimen: apakah mengubah konfigurasi TF-IDF meningkatkan performa model?

Dua parameter TF-IDF yang diuji:

1. ngram_range, seberapa panjang "potongan kata" yang dijadikan fitur
   - (1,1): hanya kata tunggal    → "daftar", "bonus", "sekarang"
   - (1,2): kata + pasangan kata  → "daftar", "daftar sekarang"  ← baseline
   - (1,3): + tiga kata sekaligus → "daftar", "daftar sekarang", "daftar sekarang bonus"

2. max_features, berapa banyak fitur yang disimpan setelah seleksi
   - 5000  : ambil 5.000 fitur paling informatif
   - 10000 : ambil 10.000 fitur paling informatif  ← baseline
   - 20000 : ambil 20.000 fitur paling informatif

Script ini melatih satu model per konfigurasi dengan data dan SVM identik -
satu-satunya yang berubah adalah pengaturan TF-IDF.

Run setelah train.py selesai (hanya butuh data/comments.csv):
    python src/experiment_features.py

Output:
- Tabel perbandingan di console
- reports/experiment_features.png, grafik perbandingan F1-macro
- reports/experiment_features.csv, tabel lengkap untuk referensi
"""

import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "comments.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, BASE_DIR)
from src.preprocessing import preprocess_batch

# Parameter SVM tetap konstan di semua eksperimen.
# Yang berubah hanya TF-IDF, ini yang membuat perbandingan adil.
SVM_PARAMS = dict(
    C=1,
    kernel="linear",
    class_weight="balanced",
    probability=True,
    random_state=42,
)

# Daftar konfigurasi yang akan diuji.
# Setiap entry adalah satu eksperimen dengan nama dan parameter TF-IDF-nya.
CONFIGS = [
    {
        "name": "Baseline",
        "desc": "ngram=(1,2)  feat=10k",
        "ngram_range": (1, 2),
        "max_features": 10_000,
    },
    {
        "name": "Unigram only",
        "desc": "ngram=(1,1)  feat=10k",
        "ngram_range": (1, 1),
        "max_features": 10_000,
    },
    {
        "name": "Trigram",
        "desc": "ngram=(1,3)  feat=10k",
        "ngram_range": (1, 3),
        "max_features": 10_000,
    },
    {
        "name": "Fewer features",
        "desc": "ngram=(1,2)  feat=5k",
        "ngram_range": (1, 2),
        "max_features": 5_000,
    },
    {
        "name": "More features",
        "desc": "ngram=(1,2)  feat=20k",
        "ngram_range": (1, 2),
        "max_features": 20_000,
    },
]


def load_and_preprocess() -> tuple:
    """Muat dataset, preprocess, dan split, sama persis dengan train.py."""
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)

    texts = df["text"].tolist()
    labels = df["label"].tolist()

    print("    Preprocessing...", end=" ", flush=True)
    cleaned = preprocess_batch(texts)
    print("selesai.")

    X_train, X_test, y_train, y_test = train_test_split(
        cleaned, labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )
    return X_train, X_test, y_train, y_test


def run_one_config(cfg: dict, X_train, X_test, y_train, y_test) -> dict:
    """
    Latih dan evaluasi satu konfigurasi TF-IDF + SVM.

    Returns:
        Dict berisi nama konfigurasi, metrik performa, dan ukuran vocabulary.
    """
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=cfg["ngram_range"],
            max_features=cfg["max_features"],
            min_df=2,
            sublinear_tf=True,
        )),
        ("svm", SVC(**SVM_PARAMS)),
    ])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    # Ukuran vocabulary aktual bisa lebih kecil dari max_features
    # kalau jumlah term unik di corpus memang kurang dari batas itu.
    vocab_size = len(pipeline.named_steps["tfidf"].vocabulary_)

    return {
        "name": cfg["name"],
        "desc": cfg["desc"],
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_spam": f1_score(y_test, y_pred, pos_label="spam", average="binary"),
        "f1_non_spam": f1_score(y_test, y_pred, pos_label="non_spam", average="binary"),
        "f1_macro": f1_score(y_test, y_pred, average="macro"),
        "vocab_size": vocab_size,
    }


def save_bar_chart(results: list) -> str:
    """
    Simpan grafik batang perbandingan F1-macro semua konfigurasi.

    Grafik ini memudahkan pembaca melihat sekilas apakah ada konfigurasi
    yang unggul dari baseline, atau apakah semua hasilnya setara.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    labels = [f"{r['name']}\n({r['desc']})" for r in results]
    f1_macros = [r["f1_macro"] for r in results]
    colors = ["#2ecc71" if r["name"] == "Baseline" else "#3498db" for r in results]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(labels, f1_macros, color=colors, alpha=0.85, edgecolor="white", linewidth=0.5)

    for bar, val in zip(bars, f1_macros):
        ax.annotate(
            f"{val:.4f}",
            xy=(bar.get_x() + bar.get_width() / 2, val),
            xytext=(0, 4), textcoords="offset points",
            ha="center", va="bottom", fontsize=9, fontweight="bold",
        )

    # Garis horizontal baseline untuk perbandingan visual
    baseline_f1 = next(r["f1_macro"] for r in results if r["name"] == "Baseline")
    ax.axhline(baseline_f1, color="#2ecc71", linestyle="--", linewidth=1.2, alpha=0.7, label="Baseline")

    ymin = min(f1_macros) - 0.01
    ax.set_ylim(max(0.85, ymin), min(1.0, max(f1_macros) + 0.015))
    ax.set_ylabel("F1-macro", fontsize=11)
    ax.set_title(
        "Eksperimen Konfigurasi TF-IDF\n(SVM dan data identik, hanya TF-IDF yang berubah)",
        fontsize=12,
    )
    ax.legend(fontsize=9)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    plt.xticks(fontsize=8.5)
    plt.tight_layout()

    path = os.path.join(REPORTS_DIR, "experiment_features.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def save_csv(results: list) -> str:
    """Simpan tabel lengkap hasil eksperimen ke CSV."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    df = pd.DataFrame(results)
    path = os.path.join(REPORTS_DIR, "experiment_features.csv")
    df.to_csv(path, index=False, encoding="utf-8")
    return path


def print_results(results: list) -> None:
    """Cetak tabel perbandingan ke console."""
    print("\n" + "=" * 75)
    print("HASIL EKSPERIMEN KONFIGURASI TF-IDF")
    print("=" * 75)
    print(
        f"\n  {'Konfigurasi':<20} {'Deskripsi':<22} {'Accuracy':>10}"
        f" {'F1-spam':>8} {'F1-non':>8} {'F1-macro':>9} {'Vocab':>7}"
    )
    print(f"  {'-'*20} {'-'*22} {'-'*10} {'-'*8} {'-'*8} {'-'*9} {'-'*7}")

    baseline_f1 = next(r["f1_macro"] for r in results if r["name"] == "Baseline")
    for r in results:
        delta = r["f1_macro"] - baseline_f1
        delta_str = f"({delta:+.4f})" if r["name"] != "Baseline" else "(baseline)"
        print(
            f"  {r['name']:<20} {r['desc']:<22} {r['accuracy']:>10.2%}"
            f" {r['f1_spam']:>8.4f} {r['f1_non_spam']:>8.4f}"
            f" {r['f1_macro']:>9.4f} {r['vocab_size']:>7,}"
            f"  {delta_str}"
        )


def interpret_results(results: list) -> None:
    """
    Cetak interpretasi otomatis tiap konfigurasi dibandingkan baseline.

    Ini titik awal untuk kalimat pembahasan di skripsi, bukan pengganti
    analisis manual, tapi membantu merumuskan argumen yang tepat.
    """
    baseline = next(r for r in results if r["name"] == "Baseline")
    print("\n" + "=" * 75)
    print("INTERPRETASI")
    print("=" * 75)

    for r in results:
        if r["name"] == "Baseline":
            continue
        delta = r["f1_macro"] - baseline["f1_macro"]
        sign = "naik" if delta > 0 else "turun"
        abs_delta = abs(delta)
        significant = abs_delta >= 0.005

        verdict = "SIGNIFIKAN" if significant else "tidak signifikan"
        print(f"\n  [{r['name']}] F1-macro {sign} {abs_delta:.4f}, {verdict}")

    print("\n" + "=" * 75)


def main():
    print("=" * 75)
    print("EKSPERIMEN KONFIGURASI TF-IDF, JUDOL SPAM DETECTOR")
    print("=" * 75)

    print(f"\n[1/3] Memuat dan memproses data...")
    X_train, X_test, y_train, y_test = load_and_preprocess()
    print(f"    Train: {len(X_train)}  |  Test: {len(X_test)}")

    print(f"\n[2/3] Melatih {len(CONFIGS)} konfigurasi...")
    results = []
    for i, cfg in enumerate(CONFIGS, 1):
        print(f"    [{i}/{len(CONFIGS)}] {cfg['name']} ({cfg['desc']})...", end=" ", flush=True)
        result = run_one_config(cfg, X_train, X_test, y_train, y_test)
        results.append(result)
        print(f"F1-macro = {result['f1_macro']:.4f}  |  vocab = {result['vocab_size']:,}")

    print_results(results)
    interpret_results(results)

    print("\n[3/3] Menyimpan output...")
    chart_path = save_bar_chart(results)
    csv_path = save_csv(results)
    print(f"    Grafik : {chart_path}")
    print(f"    CSV    : {csv_path}")
    print("\nSelesai.")


if __name__ == "__main__":
    main()
