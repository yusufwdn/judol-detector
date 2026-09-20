"""Latih pipeline TF-IDF + SVM lalu simpan ke model/svm_model.joblib.

Dijalankan setelah prepare_dataset.py. Selain melatih, skrip ini juga
menjalankan 5-fold cross-validation, mencari nilai C lewat GridSearchCV, dan
menyimpan grafik evaluasi ke reports/.

Yang diserialisasi adalah seluruh pipeline, termasuk TF-IDF yang sudah
terlatih, bukan hanya SVM-nya. TF-IDF menyimpan kamus kata beserta bobot IDF,
jadi tanpa itu nomor fitur saat prediksi tidak merujuk kata yang sama.

Penjelasan pilihan parameter ada di docs/model.md.
"""

import os
import sys
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")   # backend non-interaktif, aman dipanggil dari terminal
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score, f1_score
)
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "comments.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "svm_model.joblib")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, BASE_DIR)
from src.preprocessing import preprocess_batch

# Dipakai bersama oleh pipeline SVM dan skrip pembanding, supaya semua
# algoritma dibandingkan di atas himpunan fitur yang sama.
TFIDF_PARAMS = dict(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True,
)


def load_data(path: str) -> tuple:
    """Baca dan validasi dataset dari CSV.

    Returns:
        tuple: (X, y), X berisi teks dan y berisi labelnya.
    """
    print(f"[1/7] Loading dataset from: {path}")
    df = pd.read_csv(path)

    required_cols = {"text", "label"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)

    print(f"    Total rows  : {len(df)}")
    print(f"    Label distribution:")
    print(df["label"].value_counts().to_string())

    return df["text"].tolist(), df["label"].tolist()


def preprocess_data(texts: list) -> list:
    """Run the preprocessing pipeline on all texts in the dataset."""
    print("\n[2/7] Preprocessing texts...")
    cleaned = preprocess_batch(texts)
    print(f"    Done. Sample result:")
    print(f"    Raw    : {texts[0][:80]}...")
    print(f"    Cleaned: {cleaned[0][:80]}...")
    return cleaned


def run_cross_validation(X: list, y: list) -> None:
    """Jalankan 5-fold cross-validation pada seluruh dataset.

    Dipakai seluruh data, bukan hanya bagian latih, karena tujuannya menaksir
    kemampuan generalisasi dan semakin banyak data yang dilipat semakin kecil
    ragam taksirannya.

    Terpisah dari pembagian 80/20: cross-validation memberi skor rata-rata,
    sedangkan pembagian memberi rincian per kelas dan confusion matrix.
    """
    print("\n[3/7] K-Fold Cross-Validation (cv=5)...")
    print("    Training a temporary pipeline (not the final model)...")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
        ("svm", SVC(kernel="linear", class_weight="balanced", random_state=42))
    ])

    scores = cross_val_score(pipeline, X, y, cv=5, scoring="f1_macro", n_jobs=-1)

    print(f"\n    Fold scores (F1-macro): {[f'{s:.4f}' for s in scores]}")
    print(f"    Mean  : {scores.mean():.4f}")
    print(f"    Std   : {scores.std():.4f}")
    print(f"\n    Interpretasi: model mencapai F1-macro rata-rata "
          f"{scores.mean():.2%} +/- {scores.std():.2%} "
          f"di 5 fold berbeda.")

    plot_path = save_cv_fold_plot(scores, REPORTS_DIR)
    print(f"\n    5-fold CV plot saved: {plot_path}")


def save_cv_fold_plot(scores, output_dir: str) -> str:
    """Simpan diagram batang skor tiap fold beserta pita rata-rata dan
    simpangan bakunya.

    Satu baris "96,61% +/- 0,59%" tidak menunjukkan apakah ragamnya berasal
    dari satu fold yang lemah atau tersebar merata. Grafiknya membuat itu
    terlihat langsung.

    Returns:
        str: lokasi berkas PNG yang disimpan.
    """
    os.makedirs(output_dir, exist_ok=True)
    mean = scores.mean()
    std = scores.std()

    fig, ax = plt.subplots(figsize=(7, 5))
    fold_labels = [f"Fold {i + 1}" for i in range(len(scores))]
    bars = ax.bar(fold_labels, scores, color="#1565c0", alpha=0.85)

    ax.axhline(mean, color="#d32f2f", linestyle="--", linewidth=1.5,
               label=f"Mean = {mean:.4f}")
    ax.axhspan(mean - std, mean + std, color="#d32f2f", alpha=0.1,
               label=f"+/- Std = {std:.4f}")

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                 f"{score:.4f}", ha="center", fontsize=9)

    ax.set_ylim(min(scores) - 0.02, 1.0)
    ax.set_ylabel("F1-macro", fontsize=11)
    ax.set_title("5-Fold Cross-Validation, F1-macro per Fold", fontsize=13, pad=12)
    ax.legend(loc="lower right")
    plt.tight_layout()

    output_path = os.path.join(output_dir, "cv_5fold_scores.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def split_data(X: list, y: list) -> tuple:
    """Bagi dataset menjadi bagian latih dan bagian uji.

    test_size=0.2   -> 20% disisihkan untuk pengujian
    random_state=42 -> pengacakan dikunci supaya pembagiannya bisa diulang
    stratify=y      -> proporsi spam terhadap non-spam dijaga sama di keduanya
    """
    print("\n[4/7] Splitting data (80% train / 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    print(f"    Training set: {len(X_train)} samples")
    print(f"    Test set    : {len(X_test)} samples")
    return X_train, X_test, y_train, y_test


def find_best_hyperparams(X_train: list, y_train: list) -> dict:
    """Cari nilai C terbaik lewat GridSearchCV.

    C mengatur seberapa keras model menghukum kesalahan pada data latih. Nilai
    kecil menghasilkan margin lebih lebar dan model yang lebih toleran, nilai
    besar memaksa model mengikuti data latih lebih rapat dengan risiko
    overfitting.

    Dijalankan hanya pada bagian latih, bukan seluruh dataset. Data uji harus
    tetap tidak tersentuh selama seluruh pengambilan keputusan soal model,
    kalau tidak taksiran performanya jadi terlalu optimistis.

    Returns:
        dict berisi 'best_C' dan 'best_score'.
    """
    print("\n[5/6] Hyperparameter tuning via GridSearchCV...")
    print("    Searching C in [0.01, 0.1, 1, 10, 100]...")
    print("    (5-fold CV on training set for each value, ini bisa 1-2 menit)")

    param_grid = {"svm__C": [0.01, 0.1, 1, 10, 100]}

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
        ("svm", SVC(
            kernel="linear",
            class_weight="balanced",
            probability=True,
            random_state=42
        ))
    ])

    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        scoring="f1_macro",
        n_jobs=-1,
        verbose=0,
    )
    grid_search.fit(X_train, y_train)

    best_C = grid_search.best_params_["svm__C"]
    best_score = grid_search.best_score_

    print(f"\n    Grid search results:")
    for params, mean_score in zip(
        grid_search.cv_results_["params"],
        grid_search.cv_results_["mean_test_score"]
    ):
        marker = " <-- terpilih" if params["svm__C"] == best_C else ""
        print(f"      C={params['svm__C']:<6}  F1-macro CV = {mean_score:.4f}{marker}")

    print(f"\n    Best C    : {best_C}")
    print(f"    Best F1   : {best_score:.4f}")

    plot_path = save_gridsearch_plot(grid_search, REPORTS_DIR)
    print(f"\n    GridSearchCV plot saved: {plot_path}")

    return {"best_C": best_C, "best_score": best_score}


def save_gridsearch_plot(grid_search: GridSearchCV, output_dir: str) -> str:
    """Simpan kurva skor terhadap nilai C dalam skala logaritmik, lengkap
    dengan galat antar fold dan penanda nilai yang terpilih.

    Angka tunggal tidak menunjukkan bentuk pertukarannya. Kurva ini
    memperlihatkan sisi mana yang underfitting dan mana yang overfitting,
    sehingga pilihan C terlihat berdasar.

    Returns:
        str: lokasi berkas PNG yang disimpan.
    """
    os.makedirs(output_dir, exist_ok=True)
    cv_results = grid_search.cv_results_
    C_values = [p["svm__C"] for p in cv_results["params"]]
    means = cv_results["mean_test_score"]
    stds = cv_results["std_test_score"]
    best_C = grid_search.best_params_["svm__C"]
    best_idx = C_values.index(best_C)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.errorbar(
        C_values, means, yerr=stds,
        fmt="-o", color="#1565c0", ecolor="#90caf9",
        capsize=4, linewidth=2, markersize=7, label="F1-macro CV (mean +/- std)",
    )
    ax.scatter(
        [best_C], [means[best_idx]],
        color="#d32f2f", s=140, zorder=5, label=f"C terpilih = {best_C}",
    )
    ax.set_xscale("log")
    ax.set_xlabel("Nilai C (skala log)", fontsize=11)
    ax.set_ylabel("F1-macro (rata-rata 5-fold CV)", fontsize=11)
    ax.set_title("GridSearchCV, Pencarian Nilai C Terbaik", fontsize=13, pad=12)
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    plt.tight_layout()

    output_path = os.path.join(output_dir, "gridsearch_c_sweep.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def build_and_train_pipeline(X_train: list, y_train: list, best_C: float) -> Pipeline:
    """Bangun dan latih pipeline final memakai C hasil GridSearchCV.

    Dibungkus Pipeline, bukan dikerjakan bertahap secara terpisah, supaya
    TF-IDF dipasang hanya pada data latih. Memasangnya pada seluruh dataset
    sebelum pembagian akan membocorkan informasi dari data uji ke dalam kamus
    fitur, dan hasil evaluasinya jadi tidak sah.
    """
    print(f"\n  Training final SVM model (C={best_C})...")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
        ("svm", SVC(
            C=best_C,
            kernel="linear",
            class_weight="balanced",
            probability=True,
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)
    print("    Model trained successfully.")
    return pipeline


def save_confusion_matrix_plot(y_test: list, y_pred: list, output_dir: str) -> str:
    """Simpan confusion matrix sebagai heatmap.

    Returns:
        str: lokasi berkas PNG yang disimpan.
    """
    os.makedirs(output_dir, exist_ok=True)
    labels = ["non_spam", "spam"]
    cm = confusion_matrix(y_test, y_pred, labels=labels)

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        linewidths=0.5,
        ax=ax
    )
    ax.set_title("Confusion Matrix, SVM Judol Detector", fontsize=13, pad=12)
    ax.set_ylabel("Aktual", fontsize=11)
    ax.set_xlabel("Prediksi", fontsize=11)
    plt.tight_layout()

    output_path = os.path.join(output_dir, "confusion_matrix_svm.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def evaluate_model(pipeline: Pipeline, X_test: list, y_test: list) -> None:
    """Evaluasi model, cetak laporan rinci, dan simpan confusion matrix.

    Susunan confusion matrix:

                      Prediksi non_spam | Prediksi spam
    Aktual non_spam  |       TN         |      FP
    Aktual spam      |       FN         |      TP

    FP berarti komentar wajar ikut disembunyikan, FN berarti spam lolos.
    Untuk kasus ini FP lebih merugikan karena menyembunyikan komentar yang sah
    dari pengguna.
    """
    print("\n[6/6] Evaluating model...")
    y_pred = pipeline.predict(X_test)

    print("\n" + "=" * 60)
    print("LAPORAN EVALUASI MODEL, SVM")
    print("=" * 60)

    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    print(f"\nAkurasi keseluruhan : {acc:.2%}")
    print(f"F1-score (macro)    : {f1_macro:.4f}")

    print("\nLaporan per kelas:")
    print(classification_report(y_test, y_pred))

    labels = ["non_spam", "spam"]
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print("Confusion Matrix:")
    print(f"{'':20} {'Prediksi non_spam':>18} {'Prediksi spam':>14}")
    print(f"{'Aktual non_spam':20} {cm[0][0]:>18} {cm[0][1]:>14}")
    print(f"{'Aktual spam':20} {cm[1][0]:>18} {cm[1][1]:>14}")

    print("\nRincian:")
    print(f"  TN (non-spam terdeteksi benar)  : {cm[0][0]}")
    print(f"  FP (non-spam salah ditandai)    : {cm[0][1]}")
    print(f"  FN (spam yang lolos)            : {cm[1][0]}")
    print(f"  TP (spam terdeteksi benar)      : {cm[1][1]}")

    plot_path = save_confusion_matrix_plot(y_test, y_pred, REPORTS_DIR)
    print(f"\n  Confusion matrix plot saved: {plot_path}")
    print("=" * 60)


def save_model(pipeline: Pipeline, path: str) -> None:
    """Simpan pipeline terlatih ke disk memakai joblib."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(pipeline, path)
    size_kb = os.path.getsize(path) / 1024
    print(f"\nModel saved: {path} ({size_kb:.1f} KB)")


def main():
    print("=" * 60)
    print("SVM TRAINING - JUDOL SPAM DETECTOR")
    print("=" * 60 + "\n")

    # 1. Load raw data
    texts, labels = load_data(DATA_PATH)

    # 2. Preprocess
    cleaned_texts = preprocess_data(texts)

    # 3. K-fold cross-validation (on full data, for thesis reporting)
    run_cross_validation(cleaned_texts, labels)

    # 4. Split into train and test sets
    X_train, X_test, y_train, y_test = split_data(cleaned_texts, labels)

    # 5. Find best C via GridSearchCV (on X_train only, no data leakage)
    best_params = find_best_hyperparams(X_train, y_train)

    # 6. Train final model with best C, evaluate, save
    pipeline = build_and_train_pipeline(X_train, y_train, best_params["best_C"])
    evaluate_model(pipeline, X_test, y_test)
    save_model(pipeline, MODEL_PATH)

    print("\nTraining complete.")
    print("  To compare against baselines: python src/compare_baselines.py")
    print("  To start the API server     : python src/server.py")


if __name__ == "__main__":
    main()
