"""
server.py
=========
FastAPI server that exposes the trained SVM model as a REST API.

WHY AN API?
-----------
A browser extension (JavaScript) cannot directly import Python libraries.
The solution is a lightweight HTTP server that acts as a bridge:

  JS Extension  ->  POST /predict  ->  Python Server  ->  returns JSON prediction

When the extension finds a comment on YouTube/Instagram:
  1. It sends the raw comment text to localhost:8000/predict
  2. The server runs the preprocessing pipeline + SVM prediction
  3. The server returns {"label": "spam", "confidence": 0.94, "is_spam": true}
  4. The extension hides the comment if is_spam == true and confidence >= 0.75

WHY PREPROCESSING RUNS IN PYTHON, NOT IN THE EXTENSION
-------------------------------------------------------
See preprocessing.py for the full explanation. Short version:
Training and inference MUST apply identical transformations to the text.
Doing normalization in JavaScript introduces subtle differences in how
unicode and regex are handled compared to Python, which degrades accuracy.
Keeping everything in the Python server eliminates this risk entirely.
"""

import csv
import os
import sys
import joblib
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# Add project root to path so src.preprocessing can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.preprocessing import clean_text

# ---------------------------------------------------------------------------
# APPLICATION SETUP
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Judol Spam Detector API",
    description="Detects online gambling spam comments in YouTube/Instagram using SVM",
    version="1.0.0"
)

# CORS (Cross-Origin Resource Sharing)
# ---------------------------------------------------------------------------
# Required so the browser extension can communicate with the local server.
# Without this header, browsers block cross-origin requests.
#
# SECURITY NOTE: In production (hosted server), restrict this to the
# specific extension ID:
#   allow_origins=["chrome-extension://YOUR_EXTENSION_ID"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# MODEL LOADING
# ---------------------------------------------------------------------------
# Load the model once at startup, not on every request.
# Loading from disk on every request would make the API extremely slow.

MODEL_PATH = os.path.join(BASE_DIR, "model", "svm_model.joblib")
DATA_PATH  = os.path.join(BASE_DIR, "data", "comments.csv")
model = None


def load_model():
    """Load the serialized Pipeline from disk. Called once at server startup."""
    global model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}\n"
            f"Run training first: python src/train.py"
        )
    model = joblib.load(MODEL_PATH)
    print(f"[OK] Model loaded from: {MODEL_PATH}")


@app.on_event("startup")
async def startup_event():
    load_model()


# ---------------------------------------------------------------------------
# REQUEST / RESPONSE SCHEMAS
# ---------------------------------------------------------------------------
# Pydantic validates all incoming request data before it reaches the handler.
# This prevents crashes from unexpected or malformed input.

class PredictRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Text must not be empty")
        if len(v) > 5000:
            raise ValueError("Text too long (maximum 5000 characters)")
        return v


class PredictResponse(BaseModel):
    label: str        # "spam" or "non_spam"
    confidence: float # 0.0 - 1.0, model certainty
    is_spam: bool     # convenience boolean for the extension


class BatchPredictRequest(BaseModel):
    texts: list[str]


class BatchPredictResponse(BaseModel):
    results: list[PredictResponse]


# ---------------------------------------------------------------------------
# HYBRID RULE — Hard Spam Signal Check
# ---------------------------------------------------------------------------
#
# MASALAH YANG DISELESAIKAN:
# SVM (Bag of Words) memberi bobot spam kepada kata-kata yang sering muncul
# di data training spam, termasuk kata ambigu seperti "hoki", "serius", "keren".
# Tanpa pemahaman konteks, kata-kata itu bisa sebabkan false positive di komentar
# yang sama sekali tidak berhubungan dengan judi.
#
# SOLUSI:
# Setelah SVM memprediksi "spam", kita verifikasi apakah teks mengandung minimal
# satu kata yang secara PASTI berhubungan dengan judi online. Jika tidak ada,
# prediksi di-override ke "non_spam".
#
# TRADE-OFF (disadari dan diterima):
# Spam yang sengaja menghindari semua kata keras (misal spam memakai kalimat
# puitis tanpa kata judi eksplisit) akan lolos sebagai non_spam. Ini dianggap
# lebih baik daripada terus-menerus menyembunyikan komentar normal yang kebetulan
# mengandung kata berbobot spam.
#
# MAINTENANCE:
# Daftar ini perlu diperbarui jika spammer mulai menggunakan kata/brand baru
# yang belum terdaftar. Ini adalah keterbatasan utama pendekatan berbasis aturan.

HARD_SPAM_SIGNALS = {
    # Istilah judi yang tidak punya makna lain dalam percakapan sehari-hari
    "gacor",      # slang: slot dengan RTP tinggi / sering keluar jackpot
    "scatter",    # simbol bonus di mesin slot
    "jackpot",    # kemenangan besar di mesin judi
    "maxwin",     # kemenangan maksimum di slot
    "togel",      # lotere ilegal
    "toto",       # lotere / situs judi
    "rtp",        # Return to Player — persentase payout slot
    "slot",       # mesin slot
    "situs",      # "situs judi" — hampir selalu dipakai dalam konteks spam
    "withdraw",   # tarik dana kemenangan
    "deposit",    # setor dana ke akun judi
    # Nama brand / situs yang diketahui (angka dihapus preprocessing: PSTOTO99 → pstoto)
    "pstoto", "jptogel", "supermoney", "xuxu", "bardi",
    "bukit", "dora", "pluto", "jalak",
    "pangeran", "kyt",
    # CATATAN: "bambu" dan "giat" dihapus karena terlalu generik — keduanya adalah
    # kata Indonesia biasa (tanaman bambu, kata sifat rajin) yang muncul di komentar
    # normal non-judi. Brand yang pakai nama ini + suffix angka (bambu88, giat777)
    # sudah tertangkap via Step 5b → judolbrand.
    # Brand yang pakai kata umum + suffix → compound spesifik yang tidak ambigu
    # "pulau" sendiri terlalu umum (Pulau Bali, Pulau Jawa), tapi "pulauwin"
    # adalah compound khusus situs judi yang tidak akan muncul di konteks lain.
    "pulauwin",
    # Token universal hasil kanonikalisasi brand (Step 5b di preprocessing.py).
    # Semua brand judol yang cocok dengan JUDOL_BRAND_PATTERN (keju4d, betawi77,
    # hobiqq, slot777, dll) dikonversi ke token ini sebelum masuk ke model.
    # Satu entri ini menggantikan perlunya mendaftarkan tiap nama brand secara manual.
    "judolbrand",
}


def has_hard_spam_signal(cleaned_text: str) -> bool:
    """
    Return True jika teks (sudah dipreprocessing) mengandung minimal satu kata
    dari HARD_SPAM_SIGNALS — kata yang secara pasti berhubungan dengan judi online
    dan tidak punya interpretasi lain yang masuk akal.

    Menggunakan set intersection untuk efisiensi O(min(n,m)).
    """
    words = set(cleaned_text.split())
    return bool(words & HARD_SPAM_SIGNALS)


class ReportRequest(BaseModel):
    text: str
    label: str = "non_spam"

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Text must not be empty")
        if len(v) > 5000:
            raise ValueError("Text too long (maximum 5000 characters)")
        return v.strip()

    @field_validator("label")
    @classmethod
    def label_must_be_valid(cls, v):
        if v not in ("spam", "non_spam"):
            raise ValueError("Label must be 'spam' or 'non_spam'")
        return v


class ReportResponse(BaseModel):
    success: bool
    message: str
    duplicate: bool = False


# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    """Root endpoint. Confirms the server is running."""
    return {
        "status": "online",
        "message": "Spam Detector API is running. Use POST /predict to classify a comment."
    }


@app.get("/health")
def health():
    """Returns model load status. Useful for the extension to check before sending requests."""
    return {
        "status": "ok" if model is not None else "model_not_loaded",
        "model_loaded": model is not None
    }


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """
    Classify a single comment.

    Request body:
        {"text": "raw comment text here"}

    Response:
        {
            "label": "spam",
            "confidence": 0.94,
            "is_spam": true
        }
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready, try again shortly")

    # Apply the same preprocessing pipeline used during training
    cleaned = clean_text(request.text)

    if not cleaned:
        # Text became empty after cleaning (e.g. pure emoji input)
        return PredictResponse(label="non_spam", confidence=0.5, is_spam=False)

    label = model.predict([cleaned])[0]

    # Retrieve probability score for the predicted label
    proba = model.predict_proba([cleaned])[0]
    classes = model.classes_
    label_idx = list(classes).index(label)
    confidence = float(proba[label_idx])

    # Hybrid rule — dua arah:
    #
    # (A) FP prevention: SVM bilang spam tapi tidak ada sinyal keras judol →
    #     kemungkinan false positive dari kata ambigu (hoki, serius, keren, dll).
    #     Override ke non_spam.
    #
    # (B) FN prevention: SVM bilang non_spam padahal ada sinyal keras judol →
    #     terjadi ketika komentar punya banyak kata normal yang bobotnya mengalahkan
    #     token judolbrand di model linear. Sinyal keras harus menang — override ke spam.
    has_signal = has_hard_spam_signal(cleaned)

    if label == "spam" and not has_signal:
        print(f"[HYBRID] Override spam→non_spam (no hard signal): {cleaned[:60]}")
        return PredictResponse(label="non_spam", confidence=0.5, is_spam=False)

    if label == "non_spam" and has_signal:
        print(f"[HYBRID] Override non_spam→spam (hard signal present): {cleaned[:60]}")
        return PredictResponse(label="spam", confidence=0.9, is_spam=True)

    return PredictResponse(
        label=label,
        confidence=round(confidence, 4),
        is_spam=(label == "spam")
    )


@app.post("/predict/batch", response_model=BatchPredictResponse)
def predict_batch(request: BatchPredictRequest):
    """
    Classify multiple comments in a single request.

    More efficient than calling /predict individually for each comment.
    The extension uses this endpoint to batch-process all visible comments
    on a page in one network round-trip.

    Maximum 50 texts per request.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not ready")

    if len(request.texts) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 texts per request")

    results = []
    for text in request.texts:
        cleaned = clean_text(text)

        if not cleaned:
            results.append(PredictResponse(label="non_spam", confidence=0.5, is_spam=False))
            continue

        label = model.predict([cleaned])[0]
        proba = model.predict_proba([cleaned])[0]
        classes = model.classes_
        label_idx = list(classes).index(label)
        confidence = float(proba[label_idx])

        # Hybrid rule — dua arah, sama seperti di /predict
        has_signal = has_hard_spam_signal(cleaned)

        if label == "spam" and not has_signal:
            print(f"[HYBRID] Override spam→non_spam (no hard signal): {cleaned[:60]}")
            results.append(PredictResponse(label="non_spam", confidence=0.5, is_spam=False))
            continue

        if label == "non_spam" and has_signal:
            print(f"[HYBRID] Override non_spam→spam (hard signal present): {cleaned[:60]}")
            results.append(PredictResponse(label="spam", confidence=0.9, is_spam=True))
            continue

        results.append(PredictResponse(
            label=label,
            confidence=round(confidence, 4),
            is_spam=(label == "spam")
        ))

    return BatchPredictResponse(results=results)


@app.post("/report", response_model=ReportResponse)
def report_false_positive(request: ReportRequest):
    """
    [DEV MODE] Append a comment directly to the training dataset.

    Called by the extension when a user clicks "Bukan spam?" on a hidden
    comment. Only intended for use during development — in production this
    endpoint should sit behind an approval queue so random users cannot
    inject arbitrary data into the training set.

    Deduplication: if the exact text already exists in the CSV, the request
    is rejected to prevent duplicate entries from inflating the dataset.
    """
    # Deduplicate — scan existing rows for an exact text match
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header row
            for row in reader:
                if row and row[0].strip() == request.text:
                    return ReportResponse(
                        success=False,
                        message="Komentar ini sudah ada di dataset — tidak ditambahkan lagi.",
                        duplicate=True,
                    )

    # Append using csv.writer so commas/quotes inside text are escaped correctly
    with open(DATA_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([request.text, request.label])

    print(f"[DEV] Reported as '{request.label}': {request.text[:80]}")
    return ReportResponse(
        success=True,
        message=f"Ditambahkan ke dataset sebagai '{request.label}'.",
        duplicate=False,
    )


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 55)
    print("Judol Spam Detector API Server")
    print("URL  : http://localhost:8000")
    print("Docs : http://localhost:8000/docs")
    print("=" * 55)
    uvicorn.run(
        "src.server:app",
        host="127.0.0.1",  # localhost only, not exposed to the network
        port=8000,
        reload=False,
        app_dir=BASE_DIR
    )
