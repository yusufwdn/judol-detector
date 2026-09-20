"""Tampilkan kata dan bigram paling berpengaruh menurut model.

Pada SVM linear tiap fitur punya koefisien. Koefisien positif besar mendorong
ke arah spam, negatif besar mendorong ke arah non-spam. Membukanya adalah cara
memeriksa bahwa model belajar sinyal yang masuk akal, bukan derau.

Dijalankan setelah train.py.

    python src/inspect_features.py
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "svm_model.joblib")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOP_N = 25   # jumlah fitur teratas yang ditampilkan per kelas


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model tidak ditemukan: {MODEL_PATH}\n"
            f"Jalankan `python src/train.py` terlebih dahulu."
        )
    return joblib.load(MODEL_PATH)


def extract_feature_weights(pipeline) -> pd.DataFrame:
    """
    Ekstrak nama fitur dan bobot (koefisien) dari pipeline TF-IDF + SVM.

    Cara kerjanya:
    1. TF-IDF mengubah teks jadi vektor angka. Setiap dimensi = satu kata/bigram.
       `get_feature_names_out()` mengembalikan nama semua dimensi itu.
    2. SVM linear menyimpan koefisien untuk setiap dimensi di `coef_`.
       Koefisien positif → fitur itu mendorong prediksi ke "spam".
       Koefisien negatif → fitur itu mendorong prediksi ke "non_spam".
    3. Kita gabungkan nama fitur + koefisiennya ke dalam DataFrame,
       lalu urutkan dari yang paling kuat mendorong spam ke non_spam.

    Returns:
        DataFrame dengan kolom 'feature' dan 'weight', diurutkan descending.
    """
    tfidf = pipeline.named_steps["tfidf"]
    svm = pipeline.named_steps["svm"]

    feature_names = tfidf.get_feature_names_out()

    # coef_ adalah sparse matrix dari scipy dengan shape (1, n_features).
    # np.asarray() pada sparse matrix TIDAK menghasilkan dense array -
    # harus pakai .toarray() untuk konversi eksplisit ke numpy 2D array,
    # lalu .ravel() untuk flatten ke 1D.
    weights = svm.coef_.toarray().ravel()

    df = pd.DataFrame({
        "feature": feature_names,
        "weight": weights,
    }).sort_values("weight", ascending=False).reset_index(drop=True)

    return df


def print_top_features(df: pd.DataFrame) -> None:
    """Cetak top N fitur spam dan top N fitur non-spam ke console."""
    top_spam = df.head(TOP_N)
    top_non_spam = df.tail(TOP_N).iloc[::-1]   # balik urutan: paling kuat dulu

    print("\n" + "=" * 60)
    print(f"TOP {TOP_N} FITUR PALING KUAT MENDORONG PREDIKSI: SPAM")
    print("=" * 60)
    print(f"  {'Rank':<5} {'Fitur':<30} {'Bobot':>8}")
    print(f"  {'-'*5} {'-'*30} {'-'*8}")
    for i, row in enumerate(top_spam.itertuples(), 1):
        print(f"  {i:<5} {row.feature:<30} {row.weight:>8.4f}")

    print("\n" + "=" * 60)
    print(f"TOP {TOP_N} FITUR PALING KUAT MENDORONG PREDIKSI: NON-SPAM")
    print("=" * 60)
    print(f"  {'Rank':<5} {'Fitur':<30} {'Bobot':>8}")
    print(f"  {'-'*5} {'-'*30} {'-'*8}")
    for i, row in enumerate(top_non_spam.itertuples(), 1):
        print(f"  {i:<5} {row.feature:<30} {row.weight:>8.4f}")


def save_bar_chart(df: pd.DataFrame) -> str:
    """
    Simpan visualisasi horizontal bar chart ke reports/top_features.png.

    Grafik ini menampilkan dua panel:
    - Kiri : top fitur spam (batang merah/oranye)
    - Kanan: top fitur non-spam (batang biru)

    Panjang batang = nilai absolut koefisien (seberapa kuat pengaruhnya).
    Grafik ini langsung bisa dipakai di skripsi sebagai bukti bahwa model
    belajar pola yang masuk akal.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    n = 20  # tampilkan 20 teratas per panel supaya tidak terlalu penuh
    top_spam = df.head(n)
    top_non_spam = df.tail(n).iloc[::-1]

    fig, (ax_spam, ax_non_spam) = plt.subplots(
        1, 2, figsize=(14, 8), sharey=False
    )

    # Panel kiri: fitur spam
    ax_spam.barh(
        top_spam["feature"],
        top_spam["weight"],
        color="#e74c3c",
        alpha=0.85
    )
    ax_spam.set_title(f"Top {n} Fitur → SPAM", fontsize=12, fontweight="bold", color="#c0392b")
    ax_spam.set_xlabel("Bobot (koefisien SVM)", fontsize=10)
    ax_spam.invert_yaxis()   # fitur terkuat di atas
    ax_spam.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax_spam.tick_params(axis="y", labelsize=9)

    # Panel kanan: fitur non-spam
    ax_non_spam.barh(
        top_non_spam["feature"],
        top_non_spam["weight"].abs(),
        color="#2980b9",
        alpha=0.85
    )
    ax_non_spam.set_title(f"Top {n} Fitur → NON-SPAM", fontsize=12, fontweight="bold", color="#1a5276")
    ax_non_spam.set_xlabel("|Bobot| (koefisien SVM)", fontsize=10)
    ax_non_spam.invert_yaxis()
    ax_non_spam.tick_params(axis="y", labelsize=9)

    fig.suptitle(
        "Fitur Paling Berpengaruh dalam Model SVM\n(TF-IDF bigram, kernel linear)",
        fontsize=13, y=1.01
    )
    plt.tight_layout()

    output_path = os.path.join(REPORTS_DIR, "top_features.png")
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    return output_path


def save_csv(df: pd.DataFrame) -> str:
    """Simpan seluruh daftar fitur + bobotnya ke CSV untuk analisis lebih lanjut."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    output_path = os.path.join(REPORTS_DIR, "feature_weights.csv")
    df.to_csv(output_path, index=False, encoding="utf-8")
    return output_path


def main():
    print("=" * 60)
    print("FEATURE INSPECTION, SVM JUDOL DETECTOR")
    print("=" * 60)

    print("\n[1/3] Memuat model...")
    pipeline = load_model()
    print("    Model berhasil dimuat.")

    print("\n[2/3] Mengekstrak bobot fitur...")
    df = extract_feature_weights(pipeline)
    print(f"    Total fitur dalam model : {len(df)}")
    print(f"    Fitur positif (spam)    : {(df['weight'] > 0).sum()}")
    print(f"    Fitur negatif (non-spam): {(df['weight'] < 0).sum()}")

    print_top_features(df)

    print("\n[3/3] Menyimpan output...")
    chart_path = save_bar_chart(df)
    csv_path = save_csv(df)
    print(f"    Bar chart  : {chart_path}")
    print(f"    CSV lengkap: {csv_path}")

    print("\n" + "=" * 60)
    print("Selesai. File tersimpan di folder reports/")
    print("=" * 60)


if __name__ == "__main__":
    main()
