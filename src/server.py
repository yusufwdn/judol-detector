"""
server.py
=========
FastAPI server that exposes the trained SVM model as a REST API.

WHY AN API?
-----------
A browser extension (JavaScript) cannot directly import Python libraries.
The solution is a lightweight HTTP server that acts as a bridge:

  JS Extension  ->  POST /predict  ->  Python Server  ->  returns JSON prediction

When the extension finds a comment on YouTube:
  1. It sends the raw comment text to POST /predict
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
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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
    description="Detects online gambling spam comments in YouTube using SVM",
    version="1.0.0"
)

# CORS (Cross-Origin Resource Sharing)
# ---------------------------------------------------------------------------
# Required so the browser extension can communicate with the server.
#
# Two allowed origins, not one:
# - chrome-extension://<ID>: requests from popup.js (runs in the extension's
#   own context, pinned via the "key" field in manifest.json).
# - https://www.youtube.com: requests from content.js. Content scripts
#   execute inside the host page's context, so fetch() from them carries
#   the PAGE's origin, not the extension's — this is a browser-level quirk,
#   not something we can change from content.js.
#
# This still blocks arbitrary third-party sites from calling the API; it's
# scoped to the same domain already declared in host_permissions.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://digamkbgoiiallgimhmhmgkaddliaafg",
        "https://www.youtube.com",
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# MODEL LOADING
# ---------------------------------------------------------------------------
# Load the model once at startup, not on every request.
# Loading from disk on every request would make the API extremely slow.

MODEL_PATH           = os.path.join(BASE_DIR, "model", "svm_model.joblib")
DATA_PATH            = os.path.join(BASE_DIR, "data", "comments.csv")
MANUAL_OVERRIDES_CSV = os.path.join(BASE_DIR, "data", "manual_overrides.csv")
PRIVACY_HTML_PATH    = os.path.join(BASE_DIR, "deploy", "privacy-policy.html")

# Shared secret required on /report so it can't be hit by anonymous scripts
# once the server is public. This does NOT hide the token from a determined
# attacker (it also lives in the extension's client-side content.js, which
# anyone can unpack and read) — the goal is only to stop casual/automated
# spam of the training dataset, not to fully secure the endpoint.
REPORT_TOKEN = os.environ.get("REPORT_TOKEN", "3c0c7c4ecb995b550cd603b8e4b3f336")

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
# HYBRID RULE — Hard Spam Signal Check  [DINONAKTIFKAN — lihat catatan di bawah]
# ---------------------------------------------------------------------------
#
# STATUS: DICOBA, DIUKUR, DAN DIMATIKAN (ENABLE_HYBRID_RULES = False)
# ---------------------------------------------------------------------------
# Rule ini awalnya ditambahkan untuk dua alasan:
#   Rule A: SVM bilang "spam" tapi teks tidak punya kata judi pasti → override
#           ke "non_spam" (mencegah false positive dari kata ambigu seperti
#           "hoki", "serius", "keren").
#   Rule B: SVM bilang "non_spam" tapi teks punya kata judi pasti → override
#           ke "spam" (mencegah false negative).
#
# Saat itu kelihatan membantu di `data/hard_test_set.csv` (141 kasus ambigu).
# Tapi setelah model dilatih ulang dengan dataset yang lebih besar (Versi 8,
# 5132 baris) dan diuji dengan ablation study (src/evaluate_hybrid_ablation.py,
# bandingkan SVM murni vs SVM+hybrid di DUA dataset evaluasi), hasilnya:
#
#                         SVM murni      SVM + Hybrid      Delta
#   Train-test split      97.57% acc     91.33% acc        -6.23%
#   Hard test set         92.91% acc     80.14% acc       -12.77%
#
# Breakdown per-rule (lihat reports/hybrid_ablation.txt untuk detail lengkap):
#   Rule A: 66x nyala di train-test split → cuma 4 benar, 62 SALAH (94% salah).
#           Spam asli sering tidak memuat kata persis dari HARD_SPAM_SIGNALS
#           (mis. "daftar sekarang, wd lancar, gabung yuk"), jadi Rule A malah
#           meloloskan spam yang sudah benar dideteksi SVM.
#   Rule B: 0 benar dari 27x nyala TOTAL di kedua dataset (0%). Kata seperti
#           "togel"/"toto" sering muncul di komentar yang justru MENGKRITIK
#           judol, bukan mempromosikannya — Rule B salah paham konteks ini.
#
# KESIMPULAN: begitu model dilatih dengan data yang lebih banyak dan beragam,
# SVM sendiri sudah lebih baik dari override berbasis kata kunci manual.
# Hybrid rule dipertahankan di kode ini (bukan dihapus) sebagai bukti proses
# eksperimen — dimatikan via flag, bukan dihapus, supaya bisa diaktifkan lagi
# dan diuji ulang kalau pola spam baru di masa depan menunjukkan kebutuhan
# yang berbeda. Untuk mengaktifkan kembali, set ENABLE_HYBRID_RULES = True
# lalu jalankan ulang `python src/evaluate_hybrid_ablation.py` untuk
# memverifikasi efeknya sebelum di-deploy.
#
# MAINTENANCE (kalau diaktifkan lagi):
# Daftar HARD_SPAM_SIGNALS perlu diperbarui manual kalau spammer mulai
# menggunakan kata/brand baru yang belum terdaftar — ini keterbatasan utama
# pendekatan berbasis aturan, di luar soal akurasi yang sudah diukur di atas.

ENABLE_HYBRID_RULES = False

HARD_SPAM_SIGNALS = {
    # Istilah judi yang tidak punya makna lain dalam percakapan sehari-hari
    "gacor",      # slang: slot dengan RTP tinggi / sering keluar jackpot — SANGAT spesifik ke promosi
    "scatter",    # simbol bonus di mesin slot — tidak muncul di percakapan normal
    "jackpot",    # kemenangan besar di mesin judi
    "maxwin",     # kemenangan maksimum di slot
    "togel",      # lotere ilegal
    "toto",       # lotere / situs judi
    "rtp",        # Return to Player — istilah teknis slot, tidak wajar di komentar biasa
    # "slot" dihapus — terlalu sering muncul di cerita korban/diskusi anti-judol:
    #   "saya kenal judi slot, hidup berantakan"  → bukan promosi
    #   "blokir situs slot gituan"                → permintaan blokir
    # Spam yang sebut "slot" hampir selalu juga punya "gacor"/judolbrand/brand
    # yang masih tertangkap sinyal lain. SVM kini dilatih cukup membedakan konteks.
    # "situs" dihapus — terlalu generik: "situs darkweb", "situs jembot",
    # "tempat yang dikunjungi" adalah kata wajar tanpa konotasi judi.
    # Brand yang memakai "situs" + nama judol tetap tertangkap via judolbrand.
    "withdraw",   # tarik dana kemenangan — konteks tarik selalu di akun judi
    # "deposit" dihapus — muncul wajar di cerita korban: "dia jual barang buat deposit lagi"
    # Spam yang sebut "deposit" hampir selalu juga punya "gacor"/brand/withdraw
    # yang masih tertangkap sinyal lain. SVM sekarang cukup kuat untuk handle ini.
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


@app.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    """Serves the privacy policy page required for Chrome Web Store publication.

    Google opens this URL during review, so it must be reachable publicly.
    Serving it from FastAPI instead of Nginx keeps things simple: the app
    already sits behind the `location /` proxy, so no extra Nginx block and
    no /var/www directory are needed — the file lives with the code and is
    deployed by the same git pull.
    """
    try:
        with open(PRIVACY_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Privacy policy page not found on this server."
        )


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

    # Hybrid rule — DINONAKTIFKAN (ENABLE_HYBRID_RULES = False).
    # Diukur lewat ablation study (lihat komentar panjang di atas dan
    # reports/hybrid_ablation.txt) dan terbukti net negative setelah model
    # dilatih ulang dengan dataset Versi 8 — SVM murni lebih akurat di kedua
    # dataset evaluasi. Kode tetap di sini, tinggal aktifkan flag-nya kalau
    # suatu saat perlu diuji ulang.
    if ENABLE_HYBRID_RULES:
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

        # Hybrid rule — DINONAKTIFKAN, sama seperti di /predict (lihat penjelasan
        # lengkap + ablation study di atas).
        if ENABLE_HYBRID_RULES:
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
def report_false_positive(request: ReportRequest, x_report_token: str = Header(default=None)):
    """
    Append a comment directly to the training dataset.

    Called by the extension when a user clicks "Bukan spam?" on a hidden
    comment. Requires the X-Report-Token header (see REPORT_TOKEN above) so
    random requests cannot inject arbitrary data into the training set.

    Deduplication: if the exact text already exists in the CSV, the request
    is rejected to prevent duplicate entries from inflating the dataset.
    """
    if x_report_token != REPORT_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Report-Token header")

    # Deduplicate — cek di comments.csv DAN manual_overrides.csv
    for check_path in (DATA_PATH, MANUAL_OVERRIDES_CSV):
        if os.path.exists(check_path):
            with open(check_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header row
                for row in reader:
                    if row and row[0].strip() == request.text:
                        return ReportResponse(
                            success=False,
                            message="Komentar ini sudah ada di dataset — tidak ditambahkan lagi.",
                            duplicate=True,
                        )

    # Append ke comments.csv (efek langsung ke training berikutnya)
    # Kolom ketiga ("source") harus diisi "manual_override" agar selaras dengan
    # skema 3-kolom yang dihasilkan prepare_dataset.py — kalau cuma 2 kolom,
    # baris ini akan misalign saat dibaca ulang sebagai DataFrame.
    with open(DATA_PATH, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([request.text, request.label, "manual_override"])

    # Append ke manual_overrides.csv (persisten saat prepare_dataset.py dijalankan ulang)
    overrides_has_header = os.path.exists(MANUAL_OVERRIDES_CSV) and os.path.getsize(MANUAL_OVERRIDES_CSV) > 0
    with open(MANUAL_OVERRIDES_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not overrides_has_header:
            writer.writerow(["text", "label"])
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
