"""
verifikasi_angka.py
===================
Menghitung ulang SELURUH angka empiris skripsi dari nol, lalu membandingkannya
dengan angka yang tertulis di skripsi.

Skrip ini tidak mengubah apa pun — hanya membaca dan mencetak.

Cara menjalankan (dari akar repositori):
    python BELAJAR/verifikasi_angka.py

Perkiraan waktu: 3-8 menit, tergantung kecepatan komputer.
Bagian paling lama adalah GridSearchCV yang menguji 5 nilai C secara berulang.
"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import pandas as pd
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from src.preprocessing import preprocess_batch

# Pengaturan yang sama persis dengan src/train.py baris 63-68
TFIDF = dict(max_features=10000, ngram_range=(1, 2), min_df=2, sublinear_tf=True)


def cek(nama, dihitung, di_skripsi, toleransi=0.0001):
    """Bandingkan hasil hitung ulang dengan angka yang tertulis di skripsi."""
    if isinstance(dihitung, float):
        cocok = abs(dihitung - di_skripsi) <= toleransi
        tampil = f"{dihitung:.4f}"
    else:
        cocok = dihitung == di_skripsi
        tampil = str(dihitung)
    tanda = "COCOK  " if cocok else "BEDA!! "
    print(f"  [{tanda}] {nama:34s} hitung={tampil:10s} skripsi={di_skripsi}")
    return cocok


print("=" * 72)
print("VERIFIKASI ANGKA SKRIPSI")
print("=" * 72)

# ---------------------------------------------------------------- 1. dataset
df = pd.read_csv(os.path.join(BASE, 'data', 'comments.csv'))
dist = df['label'].value_counts().to_dict()

print("\n[1/6] DATASET")
hasil = []
hasil.append(cek("Total komentar", len(df), 6690))
hasil.append(cek("Jumlah spam", dist.get('spam', 0), 2332))
hasil.append(cek("Jumlah non-spam", dist.get('non_spam', 0), 4358))

# ------------------------------------------------------------- 2. pembagian
X = preprocess_batch(df['text'].astype(str).tolist())
y = df['label'].tolist()
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("\n[2/6] PEMBAGIAN DATA")
hasil.append(cek("Data latih", len(Xtr), 5352))
hasil.append(cek("Data uji", len(Xte), 1338))


def pipe(clf):
    return Pipeline([('tfidf', TfidfVectorizer(**TFIDF)), ('clf', clf)])


# ------------------------------------------------------- 3. cross-validation
print("\n[3/6] CROSS-VALIDATION (agak lama, sabar...)")
cv = cross_val_score(
    pipe(SVC(kernel='linear', class_weight='balanced', random_state=42)),
    X, y, cv=5, scoring='f1_macro', n_jobs=-1)
print(f"       Skor tiap fold: {[f'{s:.4f}' for s in cv]}")
hasil.append(cek("CV rata-rata", cv.mean(), 0.9741, 0.001))
hasil.append(cek("CV simpangan baku", cv.std(), 0.0030, 0.001))

# ----------------------------------------------------------- 4. pencarian C
print("\n[4/6] PENCARIAN NILAI C (paling lama...)")
gs = GridSearchCV(
    pipe(SVC(kernel='linear', class_weight='balanced', probability=True, random_state=42)),
    {'clf__C': [0.01, 0.1, 1, 10, 100]}, cv=5, scoring='f1_macro', n_jobs=-1)
gs.fit(Xtr, ytr)
hasil.append(cek("Nilai C terbaik", gs.best_params_['clf__C'], 1))

# -------------------------------------------------------- 5. model utama SVM
print("\n[5/6] HASIL MODEL SVM")
svm = pipe(SVC(kernel='linear', C=gs.best_params_['clf__C'],
               class_weight='balanced', probability=True, random_state=42))
svm.fit(Xtr, ytr)
pred = svm.predict(Xte)

acc = accuracy_score(yte, pred)
f1m = f1_score(yte, pred, average='macro')
cm = confusion_matrix(yte, pred, labels=sorted(set(y)))
tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

hasil.append(cek("Akurasi", acc, 0.9753, 0.0001))
hasil.append(cek("F1-macro", f1m, 0.9726, 0.0001))
hasil.append(cek("TN (non-spam benar)", int(tn), 863))
hasil.append(cek("FP (salah tuduh)", int(fp), 9))
hasil.append(cek("FN (spam lolos)", int(fn), 24))
hasil.append(cek("TP (spam benar)", int(tp), 442))

pre = tp / (tp + fp)
rec = tp / (tp + fn)
f1s = 2 * pre * rec / (pre + rec)
hasil.append(cek("Presisi kelas spam", pre, 0.9800, 0.0001))
hasil.append(cek("Recall kelas spam", rec, 0.9485, 0.0001))
hasil.append(cek("F1 kelas spam", f1s, 0.9640, 0.0001))

print("\n       Rumus yang baru saja dihitung:")
print(f"         Akurasi  = ({tp} + {tn}) / {len(yte)} = {acc:.5f}")
print(f"         Presisi  = {tp} / ({tp} + {fp}) = {pre:.5f}")
print(f"         Recall   = {tp} / ({tp} + {fn}) = {rec:.5f}")
print(f"         F1       = 2 x P x R / (P + R)  = {f1s:.5f}")

# ------------------------------------------------------------ 6. pembanding
print("\n[6/6] ALGORITMA PEMBANDING")
for nama, clf, acc_skripsi, f1_skripsi in [
    ("Logistic Regression", LogisticRegression(max_iter=1000, class_weight='balanced',
                                               random_state=42), 0.9709, 0.9675),
    ("Multinomial NB", MultinomialNB(), 0.9395, 0.9313),
]:
    m = pipe(clf)
    m.fit(Xtr, ytr)
    p = m.predict(Xte)
    hasil.append(cek(f"{nama} - akurasi", accuracy_score(yte, p), acc_skripsi, 0.0001))
    hasil.append(cek(f"{nama} - F1-macro", f1_score(yte, p, average='macro'), f1_skripsi, 0.0001))

# ------------------------------------------------------------------ ringkas
print("\n" + "=" * 72)
cocok = sum(hasil)
total = len(hasil)
if cocok == total:
    print(f"SELURUH {total} ANGKA COCOK dengan yang tertulis di skripsi.")
    print("Angka di skripsi terbukti dapat direproduksi.")
else:
    print(f"{cocok} dari {total} angka cocok. Periksa yang bertanda BEDA di atas.")
    print("Kalau ada yang beda, kemungkinan data/comments.csv sudah berubah.")
print("=" * 72)
