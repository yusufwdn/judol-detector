"""
compare_baselines.py
====================
One-time experiment script: compare the trained SVM model against simpler
baseline classifiers (Naive Bayes, Logistic Regression) on the same data split.

Run AFTER train.py has been executed (requires model/svm_model.joblib):
    python src/compare_baselines.py

Output:
- Comparison table printed to console
- Confusion matrix PNG for each model saved to reports/
"""

import os
import sys
import shutil
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix, classification_report
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

# PENTING: Parameter TF-IDF ini harus sama persis dengan yang ada di train.py.
# Kalau beda, perbandingannya tidak adil — beda hasilnya bisa dari feature-nya,
# bukan dari algoritmanya.
TFIDF_PARAMS = dict(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True,
)


def load_and_prepare_data() -> tuple:
    """Load, preprocess, and split data — identik dengan train.py."""
    print("[1/3] Loading and preprocessing data...")
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)

    texts = df["text"].tolist()
    labels = df["label"].tolist()

    cleaned = preprocess_batch(texts)

    # random_state dan test_size harus sama dengan train.py supaya split-nya
    # identik — kita membandingkan model di test set yang sama persis.
    X_train, X_test, y_train, y_test = train_test_split(
        cleaned, labels,
        test_size=0.2,
        random_state=42,
        stratify=labels
    )
    print(f"    Train: {len(X_train)}  |  Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test


def save_confusion_matrix_plot(
    y_test: list, y_pred: list, filename: str
) -> str:
    """Save a labeled confusion matrix heatmap as PNG to reports/."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
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
    ax.set_title(f"Confusion Matrix — {filename.replace('_', ' ').title()}", fontsize=12, pad=10)
    ax.set_ylabel("Aktual", fontsize=11)
    ax.set_xlabel("Prediksi", fontsize=11)
    plt.tight_layout()

    path = os.path.join(REPORTS_DIR, f"confusion_matrix_{filename}.png")
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def run_comparison(X_train, X_test, y_train, y_test) -> None:
    """
    Train baseline classifiers and compare with the saved SVM model.

    All three models use the same TF-IDF parameters and the same data split.
    The only variable is the classifier — making the comparison fair.
    """
    print("\n[2/3] Training baseline classifiers...")

    baselines = {
        "svm": None,   # loaded from disk below
        "naive_bayes_multinomialnb": Pipeline([
            ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
            ("clf", MultinomialNB()),
        ]),
        "logistic_regression": Pipeline([
            ("tfidf", TfidfVectorizer(**TFIDF_PARAMS)),
            ("clf", LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42
            )),
        ]),
    }

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}\n"
            f"Run `python src/train.py` first."
        )
    svm = joblib.load(MODEL_PATH)

    results = []

    # Evaluate SVM
    y_pred_svm = svm.predict(X_test)
    results.append({
        "name": "SVM (model utama)",
        "accuracy": accuracy_score(y_test, y_pred_svm),
        "f1_macro": f1_score(y_test, y_pred_svm, average="macro"),
        "slug": "svm",
        "y_pred": y_pred_svm,
    })

    # Train and evaluate baselines
    for slug, pipeline in baselines.items():
        if slug == "svm":
            continue
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        display_name = {
            "naive_bayes_multinomialnb": "Naive Bayes (MultinomialNB)",
            "logistic_regression": "Logistic Regression",
        }.get(slug, slug)
        results.append({
            "name": display_name,
            "accuracy": accuracy_score(y_test, y_pred),
            "f1_macro": f1_score(y_test, y_pred, average="macro"),
            "slug": slug,
            "y_pred": y_pred,
        })

    print("\n[3/3] Results...")
    print("\n" + "=" * 60)
    print("BASELINE COMPARISON")
    print("=" * 60)
    print(f"\n  {'Model':<35} {'Accuracy':>10} {'F1-macro':>10}")
    print(f"  {'-'*35} {'-'*10} {'-'*10}")
    for r in results:
        marker = " (*)" if r["slug"] == "svm" else ""
        print(f"  {r['name']:<35} {r['accuracy']:>10.2%} {r['f1_macro']:>10.4f}{marker}")
    print(f"\n  (*) = model produksi yang disimpan di model/svm_model.joblib")

    print("\nClassification reports:")
    for r in results:
        print(f"\n--- {r['name']} ---")
        print(classification_report(y_test, r["y_pred"]))

    print("\nSaving confusion matrix plots...")
    for r in results:
        path = save_confusion_matrix_plot(y_test, r["y_pred"], r["slug"])
        print(f"  Saved: {path}")

    print("=" * 60)


def main():
    print("=" * 60)
    print("BASELINE COMPARISON — JUDOL SPAM DETECTOR")
    print("=" * 60 + "\n")

    X_train, X_test, y_train, y_test = load_and_prepare_data()
    run_comparison(X_train, X_test, y_train, y_test)

    print("\nDone. Confusion matrix PNGs saved to reports/")


if __name__ == "__main__":
    main()
