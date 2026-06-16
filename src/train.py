"""
train.py
========
Trains the SVM spam classifier pipeline and saves the model to disk.

ML PIPELINE OVERVIEW
---------------------
Training runs through these stages:

1. TF-IDF (Term Frequency - Inverse Document Frequency)
   Converts text into numeric feature vectors.
   - Words frequent in one document but rare across others get high weight.
   - Example: "daftar" appears often in spam but rarely in normal comments
     -> high IDF -> high weight -> useful discriminative feature.

2. Hyperparameter Tuning (GridSearchCV)
   Automatically searches for the best C value via 5-fold cross-validation
   on the training set. This replaces the previous "C=1.0 as default" approach
   with an empirically selected value — stronger justification for the thesis.

3. SVM (Support Vector Machine)
   Finds the optimal hyperplane separating the two classes.
   "Optimal" means the widest possible margin to the nearest data points
   (the support vectors) on each side.
   Key parameters:
   - C      : regularization strength (lower = more generalization)
   - kernel : decision boundary shape ('linear' is best for high-dim text)

4. Evaluation
   - K-fold cross-validation (cv=5) on full data: average ± std deviation
   - Train/test split (80/20): detailed per-class metrics and confusion matrix
   - Baseline comparison: SVM vs Naive Bayes vs Logistic Regression
"""

import os
import sys
import pandas as pd
import joblib
import matplotlib
matplotlib.use("Agg")   # non-interactive backend — safe for Windows terminal
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

# Shared TF-IDF params — same settings used in SVM pipeline and baselines
# so the comparison is fair (same features, different classifiers).
TFIDF_PARAMS = dict(
    max_features=10000,
    ngram_range=(1, 2),
    min_df=2,
    sublinear_tf=True,
)


def load_data(path: str) -> tuple:
    """
    Load and validate the training dataset from CSV.

    Returns:
        tuple: (X, y) where X is a list of text strings and y is a list of labels.
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
    """
    Run 5-fold cross-validation on the FULL dataset.

    Why on full data (not just X_train)?
    Cross-validation's purpose is to estimate how well the model generalizes
    to unseen data. Using all available data gives the most stable estimate —
    the more data we fold over, the lower the variance of the estimate.

    This is separate from the 80/20 split: k-fold gives the average score,
    the split gives the detailed per-class breakdown and confusion matrix.

    The mean ± std output is what you cite in the thesis as the cross-validated
    F1-score — more credible than a single split's number.
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


def split_data(X: list, y: list) -> tuple:
    """
    Split the dataset into training and test sets.

    Why split at all? To measure model performance on data it has NEVER seen
    during training. Evaluating on training data would give inflated scores
    that do not reflect real-world behavior.

    test_size=0.2   -> 20% held out for testing, 80% used for training
    random_state=42 -> fixed seed ensures the split is reproducible
    stratify=y      -> preserves the spam/non-spam ratio in both splits
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
    """
    Use GridSearchCV to find the optimal C value for the SVM.

    What is C?
    C is the "regularization parameter" — it controls the trade-off between:
    - Low C  : the model accepts more misclassifications to get a wider margin
               (more generalization, less overfitting)
    - High C : the model tries to classify every training point correctly
               (tighter fit, more risk of overfitting)

    GridSearchCV trains and evaluates the model for each candidate C value
    using 5-fold cross-validation on the training set. It picks the C that
    gives the highest average F1-macro score.

    This is run on X_train only (not the full dataset) to prevent data leakage
    — the test set must stay completely unseen during all model decisions.

    Returns:
        dict with 'best_C' and 'best_score'.
    """
    print("\n[5/6] Hyperparameter tuning via GridSearchCV...")
    print("    Searching C in [0.01, 0.1, 1, 10, 100]...")
    print("    (5-fold CV on training set for each value — ini bisa 1-2 menit)")

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

    return {"best_C": best_C, "best_score": best_score}


def build_and_train_pipeline(X_train: list, y_train: list, best_C: float) -> Pipeline:
    """
    Build and train the final SVM pipeline using the best C from GridSearchCV.

    Why use Pipeline instead of separate steps?
    Pipeline ensures the TF-IDF vectorizer is fitted ONLY on training data.
    If fitted separately on the full dataset before splitting, it would
    inadvertently leak information from the test set — a subtle but critical
    mistake called data leakage.
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
    """
    Save confusion matrix as a heatmap PNG file.

    The plot uses color intensity to show the magnitude of each cell:
    darker blue = more samples. This is easier to read at a glance than a
    plain table of numbers, and can be directly embedded in the thesis.

    Returns:
        str: Path to the saved PNG file.
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
    ax.set_title("Confusion Matrix — SVM Judol Detector", fontsize=13, pad=12)
    ax.set_ylabel("Aktual", fontsize=11)
    ax.set_xlabel("Prediksi", fontsize=11)
    plt.tight_layout()

    output_path = os.path.join(output_dir, "confusion_matrix_svm.png")
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def evaluate_model(pipeline: Pipeline, X_test: list, y_test: list) -> None:
    """
    Evaluate model performance, print a detailed report, and save confusion
    matrix plot.

    Confusion Matrix layout:

                      Predicted: non_spam | Predicted: spam
    Actual: non_spam |   TN (correct)     |  FP (false alarm)
    Actual: spam     |   FN (missed)      |  TP (correct)

    TN = True Negative  : non-spam correctly identified
    TP = True Positive  : spam correctly identified
    FP = False Positive : non-spam wrongly flagged as spam
    FN = False Negative : spam that slipped through (most dangerous)
    """
    print("\n[6/6] Evaluating model...")
    y_pred = pipeline.predict(X_test)

    print("\n" + "=" * 60)
    print("MODEL EVALUATION REPORT — SVM")
    print("=" * 60)

    acc = accuracy_score(y_test, y_pred)
    f1_macro = f1_score(y_test, y_pred, average="macro")
    print(f"\nOverall Accuracy : {acc:.2%}")
    print(f"F1-score (macro) : {f1_macro:.4f}")

    print("\nPer-class Report:")
    print(classification_report(y_test, y_pred))

    labels = ["non_spam", "spam"]
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print("Confusion Matrix:")
    print(f"{'':20} {'Prediksi non_spam':>18} {'Prediksi spam':>14}")
    print(f"{'Aktual non_spam':20} {cm[0][0]:>18} {cm[0][1]:>14}")
    print(f"{'Aktual spam':20} {cm[1][0]:>18} {cm[1][1]:>14}")

    print("\nBreakdown:")
    print(f"  TN (non-spam correctly identified) : {cm[0][0]}")
    print(f"  FP (non-spam wrongly flagged)       : {cm[0][1]}")
    print(f"  FN (spam that slipped through)      : {cm[1][0]}")
    print(f"  TP (spam correctly detected)        : {cm[1][1]}")

    plot_path = save_confusion_matrix_plot(y_test, y_pred, REPORTS_DIR)
    print(f"\n  Confusion matrix plot saved: {plot_path}")
    print("=" * 60)



def save_model(pipeline: Pipeline, path: str) -> None:
    """Serialize the trained pipeline to disk using joblib."""
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

    # 3. K-fold cross-validation (on full data — for thesis reporting)
    run_cross_validation(cleaned_texts, labels)

    # 4. Split into train and test sets
    X_train, X_test, y_train, y_test = split_data(cleaned_texts, labels)

    # 5. Find best C via GridSearchCV (on X_train only — no data leakage)
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
