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

        results.append(PredictResponse(
            label=label,
            confidence=round(confidence, 4),
            is_spam=(label == "spam")
        ))

    return BatchPredictResponse(results=results)


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
