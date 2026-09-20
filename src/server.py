"""REST API yang menyajikan model SVM terlatih.

Ekstensi peramban tidak bisa memuat pustaka Python, jadi model disajikan
lewat HTTP. Ekstensi mengirim teks komentar apa adanya, server menormalisasi
dan memprediksinya, lalu mengembalikan label beserta nilai kepercayaan.

Normalisasi sengaja dikerjakan di sini, bukan di sisi ekstensi. Alasannya ada
di preprocessing.py.

Endpoint didokumentasikan di docs/api.md.
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

# Akar proyek ditambahkan ke path supaya src.preprocessing bisa diimpor.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from src.preprocessing import clean_text

app = FastAPI(
    title="Judol Spam Detector API",
    description="Deteksi komentar spam promosi judi online di YouTube",
    version="1.0.0"
)

# Dua origin, bukan satu. popup.js berjalan di konteks ekstensi sendiri jadi
# Origin-nya chrome-extension://<ID>, sedangkan content.js disuntikkan ke
# halaman YouTube sehingga fetch darinya membawa Origin milik halaman itu.
# Membatasi ke ID ekstensi saja bikin content.js kena blok CORS padahal
# popup.js jalan normal.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://digamkbgoiiallgimhmhmgkaddliaafg",
        "https://www.youtube.com",
    ],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

MODEL_PATH           = os.path.join(BASE_DIR, "model", "svm_model.joblib")
DATA_PATH            = os.path.join(BASE_DIR, "data", "comments.csv")
MANUAL_OVERRIDES_CSV = os.path.join(BASE_DIR, "data", "manual_overrides.csv")
PRIVACY_HTML_PATH    = os.path.join(BASE_DIR, "deploy", "privacy-policy.html")

# Token untuk /report, yang menulis langsung ke dataset pelatihan. Dibaca dari
# environment saja, tanpa nilai bawaan. Nilai bawaan yang ditulis di sini akan
# terbaca siapa pun karena repositori ini publik, jadi justru lebih buruk
# daripada tidak ada token sama sekali. Tanpa environment, endpoint-nya menolak
# semua permintaan dengan 503.
REPORT_TOKEN = os.environ.get("REPORT_TOKEN")

model = None


def load_model():
    """Muat pipeline dari disk. Dipanggil sekali saat server start, bukan tiap
    permintaan."""
    global model
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Berkas model tidak ditemukan: {MODEL_PATH}\n"
            f"Jalankan pelatihan dulu: python src/train.py"
        )
    model = joblib.load(MODEL_PATH)
    print(f"[OK] Model dimuat dari: {MODEL_PATH}")


@app.on_event("startup")
async def startup_event():
    load_model()


# Pydantic memvalidasi seluruh permintaan sebelum sampai ke handler, jadi tiap
# endpoint tidak perlu memeriksa masukannya sendiri.

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


# Aturan heuristik di atas keputusan SVM. Sudah diukur dan terbukti merugikan,
# jadi dimatikan. Kodenya tidak dihapus supaya hasil ablasinya bisa
# diverifikasi ulang lewat src/evaluate_hybrid_ablation.py.
#
# Aturan A menimpa spam jadi non_spam kalau teks tidak memuat kata judi yang
# pasti. Aturan B menimpa non_spam jadi spam kalau kata itu ada.
#
#                     SVM murni   SVM + aturan   selisih
#   Data uji            97,53%       90,21%       -7,32
#   Kasus ambigu        98,52%       82,22%      -16,30
#
# Aturan A nyala 66 kali di data uji, cuma 4 yang benar. Spam asli sering tidak
# memuat kata persis dari daftar ("daftar sekarang, wd lancar, gabung yuk"),
# jadi aturan ini justru membatalkan deteksi yang sudah benar. Aturan B nyala
# 27 kali dan tidak satu pun benar: "togel" dan "toto" paling sering muncul di
# komentar yang mengkritik judol, bukan mempromosikannya.
#
# Angka di atas dari reports/hybrid_ablation.txt. Kalau flag ini diaktifkan
# lagi, jalankan ulang skrip ablasinya dulu sebelum deploy.

ENABLE_HYBRID_RULES = False

HARD_SPAM_SIGNALS = {
    # Istilah judi yang tidak punya makna lain dalam percakapan sehari-hari
    "gacor",      # slang: slot dengan RTP tinggi / sering keluar jackpot, SANGAT spesifik ke promosi
    "scatter",    # simbol bonus di mesin slot, tidak muncul di percakapan normal
    "jackpot",    # kemenangan besar di mesin judi
    "maxwin",     # kemenangan maksimum di slot
    "togel",      # lotere ilegal
    "toto",       # lotere / situs judi
    "rtp",        # Return to Player, istilah teknis slot, tidak wajar di komentar biasa
    # "slot" dihapus, terlalu sering muncul di cerita korban/diskusi anti-judol:
    #   "saya kenal judi slot, hidup berantakan"  → bukan promosi
    #   "blokir situs slot gituan"                → permintaan blokir
    # Spam yang sebut "slot" hampir selalu juga punya "gacor"/judolbrand/brand
    # yang masih tertangkap sinyal lain. SVM kini dilatih cukup membedakan konteks.
    # "situs" dihapus, terlalu generik: "situs darkweb", "situs jembot",
    # "tempat yang dikunjungi" adalah kata wajar tanpa konotasi judi.
    # Brand yang memakai "situs" + nama judol tetap tertangkap via judolbrand.
    "withdraw",   # tarik dana kemenangan, konteks tarik selalu di akun judi
    # "deposit" dihapus, muncul wajar di cerita korban: "dia jual barang buat deposit lagi"
    # Spam yang sebut "deposit" hampir selalu juga punya "gacor"/brand/withdraw
    # yang masih tertangkap sinyal lain. SVM sekarang cukup kuat untuk handle ini.
    # Nama brand / situs yang diketahui (angka dihapus preprocessing: PSTOTO99 → pstoto)
    "pstoto", "jptogel", "supermoney", "xuxu", "bardi",
    "bukit", "dora", "pluto", "jalak",
    "pangeran", "kyt",
    # CATATAN: "bambu" dan "giat" dihapus karena terlalu generik, keduanya adalah
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
    dari HARD_SPAM_SIGNALS, kata yang secara pasti berhubungan dengan judi online
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


@app.get("/")
def root():
    """Konfirmasi server hidup."""
    return {
        "status": "online",
        "message": "Spam Detector API is running. Use POST /predict to classify a comment."
    }


@app.get("/health")
def health():
    """Status pemuatan model. Dipanggil ekstensi sebelum mulai mengirim komentar."""
    return {
        "status": "ok" if model is not None else "model_not_loaded",
        "model_loaded": model is not None
    }


@app.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    """Halaman kebijakan privasi untuk pengajuan Chrome Web Store.

    Disajikan lewat FastAPI, bukan Nginx, supaya ikut ter-deploy oleh git pull
    yang sama tanpa perlu blok Nginx tambahan atau direktori /var/www.
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
    """Klasifikasi satu komentar."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model belum siap, coba lagi sebentar")

    cleaned = clean_text(request.text)

    if not cleaned:
        # Teks habis setelah normalisasi, misalnya isinya emoji semua.
        return PredictResponse(label="non_spam", confidence=0.5, is_spam=False)

    label = model.predict([cleaned])[0]

    proba = model.predict_proba([cleaned])[0]
    classes = model.classes_
    label_idx = list(classes).index(label)
    confidence = float(proba[label_idx])

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
    # No token configured means this server was not set up to collect
    # corrections. Refuse outright rather than fall back to a shared default.
    if not REPORT_TOKEN:
        raise HTTPException(
            status_code=503,
            detail="Reporting is disabled on this server."
        )

    if x_report_token != REPORT_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Report-Token header")

    # Deduplicate, cek di comments.csv DAN manual_overrides.csv
    for check_path in (DATA_PATH, MANUAL_OVERRIDES_CSV):
        if os.path.exists(check_path):
            with open(check_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header row
                for row in reader:
                    if row and row[0].strip() == request.text:
                        return ReportResponse(
                            success=False,
                            message="Komentar ini sudah ada di dataset, tidak ditambahkan lagi.",
                            duplicate=True,
                        )

    # Append ke comments.csv (efek langsung ke training berikutnya)
    # Kolom ketiga ("source") harus diisi "manual_override" agar selaras dengan
    # skema 3-kolom yang dihasilkan prepare_dataset.py, kalau cuma 2 kolom,
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


# Titik masuk

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
