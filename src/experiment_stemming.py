"""
experiment_stemming.py
======================
Eksperimen: apakah menambahkan stemming meningkatkan performa model?

Stemming = proses memotong kata ke bentuk dasarnya.
Contoh: "mendaftar", "terdaftar", "pendaftaran" → semua jadi "daftar"

Script ini melatih DUA model dengan data dan pengaturan yang sama persis,
satu-satunya perbedaan adalah ada/tidaknya stemming di preprocessing:

  Model A: pipeline biasa (tanpa stemming) ← ini yang sudah ada
  Model B: pipeline + stemming di setiap token

Tujuan: membuktikan secara empiris apakah stemming membantu atau justru
menurunkan performa. Hasilnya bisa langsung dikutip di bab metodologi skripsi.

Run setelah train.py selesai (tidak perlu model tersimpan, tapi butuh dataset):
    python src/experiment_stemming.py

Output:
- Tabel perbandingan di console
- reports/experiment_stemming.png — grafik perbandingan F1-score per kelas
"""

import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.pipeline import Pipeline
from scipy import stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "comments.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, BASE_DIR)
from src.preprocessing import preprocess_batch

# Pengaturan TF-IDF dan SVM harus sama persis dengan train.py agar
# perbandingannya adil — yang berubah HANYA preprocessing-nya.
TFIDF_PARAMS = dict(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True,
)
SVM_PARAMS = dict(
    C=1,
    kernel="linear",
    class_weight="balanced",
    probability=True,
    random_state=42,
)

# ---------------------------------------------------------------------------
# STEMMER SETUP
# ---------------------------------------------------------------------------
# StemmerFactory() membaca kamus Sastrawi dan membuat objek stemmer.
# Proses ini bisa memakan 1-2 detik karena kamus cukup besar.
# Kita buat stemmer sekali di sini (modul level) supaya tidak dibuat ulang
# setiap kali fungsi dipanggil.
print("Memuat stemmer Sastrawi... ", end="", flush=True)
_stemmer = StemmerFactory().create_stemmer()
print("siap.")


def stem_text(text: str) -> str:
    """
    Terapkan stemming Sastrawi ke satu string teks yang sudah dibersihkan.

    Stemming dilakukan SETELAH clean_text() karena:
    - clean_text() sudah menghapus stopwords, URL, emoji, dll.
    - Sastrawi bekerja paling baik pada teks bersih berbahasa Indonesia
    - Urutan ini menghindari stemmer memproses noise yang tidak perlu

    Contoh:
        Input  : "mendaftar sekarang dapat bonus besar"
        Output : "daftar sekarang dapat bonus besar"

    Args:
        text: String yang sudah diproses oleh clean_text().

    Returns:
        String dengan setiap kata di-stem ke bentuk dasarnya.
    """
    if not text.strip():
        return text
    return _stemmer.stem(text)


def preprocess_with_stemming(texts: list) -> list:
    """
    Jalankan pipeline preprocessing standar, lalu tambahkan stemming.

    Alur:
      raw text → clean_text() → stem_text() → hasil akhir

    Args:
        texts: List string mentah dari dataset.

    Returns:
        List string yang sudah bersih dan di-stem.
    """
    cleaned = preprocess_batch(texts)           # 7 langkah standar
    stemmed = [stem_text(t) for t in cleaned]   # tambah stemming
    return stemmed


def load_data() -> tuple:
    """Muat dataset dan bagi jadi train/test dengan split yang sama dengan train.py."""
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)
    return df["text"].tolist(), df["label"].tolist()


def build_pipeline() -> Pipeline:
    """Buat pipeline TF-IDF + SVM dengan pengaturan standar."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
        ("svm", SVC(**SVM_PARAMS)),
    ])


def run_experiment(X_train, X_test, y_train, y_test, label: str) -> dict:
    """
    Latih satu pipeline dan evaluasi di test set.

    Args:
        label: Nama eksperimen, untuk ditampilkan di output.

    Returns:
        Dict berisi label, accuracy, f1 per kelas, dan classification report.
    """
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    f1_spam = f1_score(y_test, y_pred, pos_label="spam", average="binary")
    f1_non = f1_score(y_test, y_pred, pos_label="non_spam", average="binary")
    f1_macro = f1_score(y_test, y_pred, average="macro")
    report = classification_report(y_test, y_pred)

    return {
        "label": label,
        "accuracy": acc,
        "f1_spam": f1_spam,
        "f1_non_spam": f1_non,
        "f1_macro": f1_macro,
        "report": report,
    }


def save_comparison_chart(results: list) -> str:
    """
    Simpan bar chart perbandingan F1-score dua model ke reports/.

    Chart ini memperlihatkan tiga metrik berdampingan:
    - F1 class spam
    - F1 class non_spam
    - F1 macro (rata-rata keduanya)

    Memudahkan pembaca skripsi melihat perbedaan dampak stemming
    per kelas secara sekilas.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    labels = [r["label"] for r in results]
    f1_spam = [r["f1_spam"] for r in results]
    f1_non = [r["f1_non_spam"] for r in results]
    f1_macro = [r["f1_macro"] for r in results]

    x = range(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(9, 5))
    bars1 = ax.bar([i - width for i in x], f1_spam, width, label="F1 — spam", color="#e74c3c", alpha=0.85)
    bars2 = ax.bar(x, f1_non, width, label="F1 — non_spam", color="#2980b9", alpha=0.85)
    bars3 = ax.bar([i + width for i in x], f1_macro, width, label="F1 — macro avg", color="#27ae60", alpha=0.85)

    # Tambahkan nilai di atas tiap batang
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(
                f"{h:.4f}",
                xy=(bar.get_x() + bar.get_width() / 2, h),
                xytext=(0, 3), textcoords="offset points",
                ha="center", va="bottom", fontsize=8,
            )

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0.85, 1.01)
    ax.set_ylabel("F1-Score", fontsize=11)
    ax.set_title("Eksperimen Stemming: Dengan vs Tanpa Stemming\n(data, split, dan hyperparameter identik)", fontsize=12)
    ax.legend(fontsize=10)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, "experiment_stemming.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def run_cv_comparison(X_no_stem: list, X_with_stem: list, y: list) -> dict:
    """
    Compare stemming vs no-stemming using 5-fold CV instead of a single
    80/20 split, with a paired t-test on the per-fold scores.

    WHY THIS IS MORE RELIABLE THAN THE SINGLE-SPLIT COMPARISON ABOVE:
    A single split's delta can be an artifact of which rows happened to
    land in the test set — especially after the dataset changes size/
    composition between experiment runs (see DATASET_LOG.md). Averaging
    over 5 folds is more stable, and because cv=5 (an integer) uses an
    UNSHUFFLED (Stratified)KFold, the fold assignment depends only on
    label order — which is IDENTICAL for X_no_stem and X_with_stem (same
    rows, same order, only the text content differs). That means fold i
    of "no stemming" and fold i of "with stemming" test on the exact same
    samples, so the per-fold DIFFERENCE is a valid paired comparison, not
    just two independent averages.

    A paired t-test on those 5 differences answers the actual question:
    "is stemming consistently better across different data subsets, or
    did it only win by chance on one particular split?"

    Returns:
        dict with per-fold scores for both variants and the p-value.
    """
    print("\n[CV] Menjalankan 5-fold cross-validation untuk kedua varian...")
    print("    (dipakai untuk uji signifikansi, bukan cuma satu angka split)")

    scores_no_stem = cross_val_score(
        build_pipeline(), X_no_stem, y, cv=5, scoring="f1_macro", n_jobs=-1
    )
    scores_with_stem = cross_val_score(
        build_pipeline(), X_with_stem, y, cv=5, scoring="f1_macro", n_jobs=-1
    )
    deltas = scores_with_stem - scores_no_stem
    t_stat, p_value = stats.ttest_rel(scores_with_stem, scores_no_stem)

    print(f"\n  {'Fold':<6} {'Tanpa Stemming':>16} {'Dengan Stemming':>18} {'Delta':>10}")
    for i, (a, b) in enumerate(zip(scores_no_stem, scores_with_stem), start=1):
        print(f"  {i:<6} {a:>16.4f} {b:>18.4f} {b - a:>+10.4f}")

    print(f"\n  Mean (tanpa stemming) : {scores_no_stem.mean():.4f} ± {scores_no_stem.std():.4f}")
    print(f"  Mean (dengan stemming): {scores_with_stem.mean():.4f} ± {scores_with_stem.std():.4f}")
    print(f"  Mean delta            : {deltas.mean():+.4f} ± {deltas.std():.4f}")
    print(f"  Paired t-test         : t={t_stat:.3f}, p={p_value:.4f}")

    print("\n" + "=" * 65)
    print("INTERPRETASI (CV, 5 fold berpasangan)")
    print("=" * 65)
    if p_value < 0.05:
        print(f"""
  Selisih SIGNIFIKAN secara statistik (p={p_value:.4f} < 0.05).
  Stemming konsisten {"lebih baik" if deltas.mean() > 0 else "lebih buruk"}
  di 5 subset data yang berbeda-beda, bukan cuma menang di satu split
  tertentu. Ini memperkuat (atau membantah, tergantung arah) hasil
  single-split di atas dengan bukti yang lebih robust.""")
    else:
        print(f"""
  Selisih TIDAK signifikan secara statistik (p={p_value:.4f} >= 0.05).
  Meski single-split di atas menunjukkan delta positif/negatif, setelah
  diuji di 5 subset data berbeda selisihnya tidak konsisten arahnya —
  kemungkinan besar itu adalah noise dari komposisi split tertentu, BUKAN
  efek stemming yang bisa diandalkan. Untuk skripsi, ini justifikasi yang
  lebih kuat untuk TETAP TIDAK mengintegrasikan stemming ke produksi,
  walau angka single-split terlihat menjanjikan.""")
    print("=" * 65)

    chart_path = save_cv_comparison_chart(scores_no_stem, scores_with_stem, p_value)
    print(f"\n  Grafik CV comparison tersimpan: {chart_path}")

    return {
        "scores_no_stem": scores_no_stem,
        "scores_with_stem": scores_with_stem,
        "p_value": p_value,
    }


def save_cv_comparison_chart(scores_no_stem, scores_with_stem, p_value: float) -> str:
    """
    Save a grouped bar chart of per-fold F1-macro for both variants,
    annotated with the paired t-test p-value.

    Returns:
        str: Path to the saved PNG file.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    folds = [f"Fold {i + 1}" for i in range(len(scores_no_stem))]
    x = list(range(len(folds)))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar([i - width / 2 for i in x], scores_no_stem, width,
                    label="Tanpa Stemming", color="#2980b9", alpha=0.85)
    bars2 = ax.bar([i + width / 2 for i in x], scores_with_stem, width,
                    label="Dengan Stemming", color="#e67e22", alpha=0.85)

    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f"{h:.4f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(folds)
    y_min = min(scores_no_stem.min(), scores_with_stem.min()) - 0.01
    ax.set_ylim(y_min, 1.0)
    ax.set_ylabel("F1-macro", fontsize=11)
    sig_label = "signifikan" if p_value < 0.05 else "tidak signifikan"
    ax.set_title(
        f"Eksperimen Stemming — 5-Fold CV Berpasangan\n"
        f"(paired t-test: p={p_value:.4f}, {sig_label})",
        fontsize=12,
    )
    ax.legend(fontsize=10)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    plt.tight_layout()

    path = os.path.join(REPORTS_DIR, "experiment_stemming_cv.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def print_results(results: list) -> None:
    """Cetak tabel perbandingan dan classification report lengkap."""
    print("\n" + "=" * 65)
    print("HASIL EKSPERIMEN STEMMING")
    print("=" * 65)
    print(f"\n  {'Model':<30} {'Accuracy':>10} {'F1-spam':>9} {'F1-non':>9} {'F1-macro':>10}")
    print(f"  {'-'*30} {'-'*10} {'-'*9} {'-'*9} {'-'*10}")

    for r in results:
        print(
            f"  {r['label']:<30} {r['accuracy']:>10.2%} "
            f"{r['f1_spam']:>9.4f} {r['f1_non_spam']:>9.4f} {r['f1_macro']:>10.4f}"
        )

    print("\n\nClassification report lengkap:")
    for r in results:
        print(f"\n--- {r['label']} ---")
        print(r["report"])


def interpret_result(results: list) -> None:
    """
    Cetak interpretasi otomatis berdasarkan selisih F1-macro.

    Ini bukan pengganti analisis manual — tapi bisa jadi titik awal
    untuk kalimat interpretasi di bab pembahasan skripsi.
    """
    base = next(r for r in results if "Tanpa" in r["label"])
    stem = next(r for r in results if "Dengan" in r["label"])
    delta = stem["f1_macro"] - base["f1_macro"]

    print("\n" + "=" * 65)
    print("INTERPRETASI")
    print("=" * 65)

    if abs(delta) < 0.002:
        print(f"\n  Perbedaan F1-macro: {delta:+.4f} (sangat kecil, tidak signifikan)")
        print("""
  Kesimpulan: stemming TIDAK memberikan perbedaan yang berarti.

  Mengapa bisa terjadi?
  - Komentar spam banyak mengandung nama brand (ROMA4D, WIFI4D) yang
    memang sudah dalam bentuk dasar — stemming tidak mengubahnya.
  - TF-IDF dengan bigram sudah cukup menangkap variasi kata (misalnya
    "daftar sekarang" dan "mendaftar sekarang" menjadi dua fitur berbeda,
    tapi keduanya tetap bisa dikenali polanya).
  - Dataset komentar YouTube banyak berisi bahasa informal/slang yang
    tidak selalu mengikuti aturan morfologi yang ditangani Sastrawi.

  Rekomendasi untuk skripsi:
  Gunakan model tanpa stemming (lebih sederhana, performa sama). Jelaskan
  di bab pembahasan bahwa stemming diuji tapi tidak memberikan peningkatan
  signifikan, dan berikan penjelasan mengapa (poin-poin di atas).""")

    elif delta > 0:
        print(f"\n  Perbedaan F1-macro: {delta:+.4f} (stemming lebih baik)")
        print(f"""
  Kesimpulan: stemming MENINGKATKAN performa sebesar {delta:.4f} F1-macro.

  Rekomendasi untuk skripsi:
  Pertimbangkan untuk mengintegrasikan stemming ke preprocessing.py dan
  retrain model produksi. Jelaskan di bab metodologi bahwa stemming
  dipilih berdasarkan hasil eksperimen komparatif ini.""")

    else:
        print(f"\n  Perbedaan F1-macro: {delta:+.4f} (stemming lebih buruk)")
        print(f"""
  Kesimpulan: stemming MENURUNKAN performa sebesar {abs(delta):.4f} F1-macro.

  Mengapa bisa terjadi?
  - Stemming Sastrawi bisa over-stem: kata yang tidak perlu dipotong
    jadi terpotong dan kehilangan maknanya (misalnya "hoki" bisa salah
    di-stem menjadi bentuk lain).
  - Untuk teks informal/slang YouTube, stemmer berbasis aturan morfologi
    formal kurang akurat.

  Rekomendasi untuk skripsi:
  Tetap gunakan model tanpa stemming. Jelaskan di bab pembahasan bahwa
  stemming diuji dan terbukti tidak cocok untuk domain ini.""")

    print("=" * 65)


def main():
    print("=" * 65)
    print("EKSPERIMEN STEMMING — JUDOL SPAM DETECTOR")
    print("=" * 65)

    # --- Muat data ---
    print("\n[1/4] Memuat dataset...")
    texts, labels = load_data()
    print(f"    Total: {len(texts)} sampel")

    # --- Preprocessing dua versi ---
    print("\n[2/4] Preprocessing (dua versi)...")
    print("    Tanpa stemming...", end=" ", flush=True)
    X_no_stem = preprocess_batch(texts)
    print("selesai.")

    print("    Dengan stemming... ", end="", flush=True)
    X_with_stem = preprocess_with_stemming(texts)
    print("selesai.")

    # Tunjukkan contoh perbedaannya
    print("\n    Contoh perbedaan stemming:")
    for i in range(3):
        if X_no_stem[i] != X_with_stem[i]:
            print(f"      Tanpa : {X_no_stem[i][:80]}")
            print(f"      Dengan: {X_with_stem[i][:80]}")
            print()
            break

    # --- Split data (random_state=42, sama dengan train.py) ---
    print("[3/4] Melatih dan mengevaluasi kedua model...")
    results = []

    for label, X in [
        ("Tanpa Stemming (baseline)", X_no_stem),
        ("Dengan Stemming (Sastrawi)", X_with_stem),
    ]:
        X_train, X_test, y_train, y_test = train_test_split(
            X, labels, test_size=0.2, random_state=42, stratify=labels
        )
        print(f"    Melatih: {label}...", end=" ", flush=True)
        result = run_experiment(X_train, X_test, y_train, y_test, label)
        results.append(result)
        print(f"F1-macro = {result['f1_macro']:.4f}")

    # --- Output ---
    print_results(results)

    print("\n[4/4] Menyimpan grafik perbandingan...")
    chart_path = save_comparison_chart(results)
    print(f"    Tersimpan: {chart_path}")

    interpret_result(results)

    # --- CV-based comparison (lebih robust dari single-split di atas) ---
    run_cv_comparison(X_no_stem, X_with_stem, labels)


if __name__ == "__main__":
    main()
