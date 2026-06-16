"""
train.py
========
Trains the SVM spam classifier pipeline and saves the model to disk.

ML PIPELINE OVERVIEW
---------------------
Training runs through three main stages:

1. TF-IDF (Term Frequency - Inverse Document Frequency)
   Converts text into numeric feature vectors.
   - Words frequent in one document but rare across others get high weight.
   - Example: "daftar" appears often in spam but rarely in normal comments
     -> high IDF -> high weight -> useful discriminative feature.

2. SVM (Support Vector Machine)
   Finds the optimal hyperplane separating the two classes.
   "Optimal" means the widest possible margin to the nearest data points
   (the support vectors) on each side.
   Key parameters:
   - C      : regularization strength (lower = more generalization)
   - kernel : decision boundary shape ('linear' is best for high-dim text)

3. Evaluation
   - Accuracy  : overall correct prediction rate
   - Precision : of all predicted spam, how many are actually spam?
   - Recall    : of all actual spam, how many did the model catch?
   - F1-Score  : harmonic mean of precision and recall (primary metric)
"""

import os
import pandas as pd
import joblib
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "comments.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "svm_model.joblib")

import sys
sys.path.insert(0, BASE_DIR)
from src.preprocessing import preprocess_batch


def load_data(path: str) -> tuple:
    """
    Load and validate the training dataset from CSV.

    Returns:
        tuple: (X, y) where X is a list of text strings and y is a list of labels.
    """
    print(f"[1/5] Loading dataset from: {path}")
    df = pd.read_csv(path)

    # Ensure required columns are present
    required_cols = {"text", "label"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_cols}")

    # Drop rows with missing values
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)

    print(f"    Total rows  : {len(df)}")
    print(f"    Label distribution:")
    print(df['label'].value_counts().to_string())

    return df["text"].tolist(), df["label"].tolist()


def preprocess_data(texts: list) -> list:
    """Run the preprocessing pipeline on all texts in the dataset."""
    print("\n[2/5] Preprocessing texts...")
    cleaned = preprocess_batch(texts)
    print(f"    Done. Sample result:")
    print(f"    Raw    : {texts[0][:80]}...")
    print(f"    Cleaned: {cleaned[0][:80]}...")
    return cleaned


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
    print("\n[3/5] Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )
    print(f"    Training set: {len(X_train)} samples")
    print(f"    Test set    : {len(X_test)} samples")
    return X_train, X_test, y_train, y_test


def build_and_train_pipeline(X_train: list, y_train: list) -> Pipeline:
    """
    Build and train a scikit-learn Pipeline: TF-IDF -> SVM.

    Why use Pipeline instead of separate steps?
    Pipeline ensures the TF-IDF vectorizer is fitted ONLY on training data.
    If fitted separately on the full dataset before splitting, it would
    inadvertently leak information from the test set -- a subtle but critical
    mistake called data leakage.

    TF-IDF parameters:
    - max_features=10000 : keep the 10,000 highest-weighted terms
    - ngram_range=(1,2)  : use single words AND consecutive word pairs
                           e.g. "daftar sekarang" as one bigram feature
    - min_df=2           : ignore terms that appear in fewer than 2 documents
    - sublinear_tf=True  : apply log(TF) to dampen very frequent terms

    SVM parameters:
    - kernel='linear'        : best choice for high-dimensional text features
    - C=1.0                  : regularization; lower = more generalization
    - class_weight='balanced': auto-adjusts weights for imbalanced classes
    - probability=True       : enables confidence scores (required by the API)
    """
    print("\n[4/5] Training SVM model...")

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            min_df=2,
            sublinear_tf=True
        )),
        ("svm", SVC(
            C=1.0,
            kernel="linear",
            class_weight="balanced",
            probability=True,
            random_state=42
        ))
    ])

    pipeline.fit(X_train, y_train)
    print("    Model trained successfully.")
    return pipeline


def evaluate_model(pipeline: Pipeline, X_test: list, y_test: list) -> None:
    """
    Evaluate model performance and print a detailed report.

    Confusion Matrix layout:

                      Predicted: non_spam | Predicted: spam
    Actual: non_spam |   TN (correct)     |  FP (false alarm)
    Actual: spam     |   FN (missed)      |  TP (correct)

    TN = True Negative  : non-spam correctly identified
    TP = True Positive  : spam correctly identified
    FP = False Positive : non-spam wrongly flagged as spam
    FN = False Negative : spam that slipped through (most dangerous)
    """
    print("\n[5/5] Evaluating model...")

    y_pred = pipeline.predict(X_test)

    print("\n" + "=" * 60)
    print("MODEL EVALUATION REPORT")
    print("=" * 60)

    acc = accuracy_score(y_test, y_pred)
    print(f"\nOverall Accuracy: {acc:.2%}")

    print("\nPer-class Report:")
    print(classification_report(y_test, y_pred))

    print("Confusion Matrix:")
    labels = sorted(set(y_test))
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print(f"Labels: {labels}")
    print(cm)
    print("\nBreakdown:")
    print(f"  TN (non-spam correctly identified) : {cm[0][0]}")
    print(f"  FP (non-spam wrongly flagged)       : {cm[0][1]}")
    print(f"  FN (spam that slipped through)      : {cm[1][0]}")
    print(f"  TP (spam correctly detected)        : {cm[1][1]}")
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

    texts, labels = load_data(DATA_PATH)
    cleaned_texts = preprocess_data(texts)
    X_train, X_test, y_train, y_test = split_data(cleaned_texts, labels)
    pipeline = build_and_train_pipeline(X_train, y_train)
    evaluate_model(pipeline, X_test, y_test)
    save_model(pipeline, MODEL_PATH)

    print("\nTraining complete. Start the API server with:")
    print("  python src/server.py")


if __name__ == "__main__":
    main()
