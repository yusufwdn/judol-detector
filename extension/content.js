/**
 * Content script yang disuntikkan ke halaman YouTube. Membaca komentar dari
 * DOM, mengirimnya ke API, lalu menyembunyikan yang terdeteksi spam.
 *
 * Teks dikirim apa adanya tanpa dinormalisasi di sini. Seluruh normalisasi
 * dikerjakan Python supaya pelatihan dan prediksi memakai perlakuan yang sama.
 * Lihat src/preprocessing.py.
 */

const API_BASE = "https://api-svm.cupsky.my.id";
const API_URL = `${API_BASE}/predict`;
const BATCH_API_URL = `${API_BASE}/predict/batch`;
// Sengaja dikosongkan. /report menulis langsung ke dataset pelatihan, dan
// berkas ini terdistribusi ke setiap pengguna, jadi token yang ditulis di sini
// bisa dibaca siapa pun dan tidak melindungi apa-apa.
//
// Endpoint-nya cuma dipanggil kalau DEV_MODE di bawah bernilai true. Untuk
// mengumpulkan koreksi secara lokal, isi token di salinan kerja sendiri dan
// jangan ikut di-commit.
const REPORT_TOKEN = "";

// Nilai bawaan, ditimpa oleh nilai dari chrome.storage saat inisialisasi.
// Pengguna mengubahnya lewat penggeser di popup.
let confidenceThreshold = 0.75;

// Cara komentar spam ditangani secara visual, dipilih lewat popup.
// "dim": diredupkan, diberi lencana yang bisa diklik untuk menampilkannya lagi.
// "remove": disembunyikan sepenuhnya, tanpa lencana.
let hideMode = "dim";

// Saklar khusus pengembang: diubah manual di berkas ini sebelum menjalankan
// secara lokal, lalu dikembalikan sebelum dirilis. Tidak pernah muncul di
// popup dan tidak dibaca dari chrome.storage, jadi pengguna akhir tidak punya
// cara mengaktifkannya.
// Kalau true, tombol "Bukan spam?" muncul di tiap komentar yang disembunyikan.
const DEV_MODE = false;

/**
 * Hanya mencatat log saat mode pengembangan, supaya konsol pengguna akhir
 * tetap bersih. console.warn dibiarkan apa adanya karena berguna bagi siapa
 * pun yang sedang menelusuri server yang mati.
 */
function devLog(...args) {
  if (DEV_MODE) console.log(...args);
}

// Selektor elemen komentar YouTube. Ini bagian yang paling mungkin rusak
// kalau YouTube mengubah tampilannya.
const SELECTORS = {
  commentContainer: "ytd-comment-thread-renderer", // satu utas komentar utuh
  commentText: "#content-text", // simpul teks komentarnya
};

// Status runtime

let processedComments = new WeakSet(); // elemen yang sudah diproses
let hiddenCount = 0;
let scannedCount = 0;
let isServerAvailable = false;

// Pemeriksaan kesehatan server

/**
 * Periksa apakah server hidup dan modelnya sudah dimuat. Dipanggil sekali saat
 * inisialisasi, dan otomatis lagi setiap permintaan batch gagal, supaya
 * ekstensi pulih sendiri kalau server sempat restart.
 *
 * @returns {Promise<boolean>}
 */
async function checkServerHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`, {
      method: "GET",
      signal: AbortSignal.timeout(2000),
    });
    const data = await response.json();
    isServerAvailable = data.model_loaded === true;

    if (!isServerAvailable) {
      console.warn(
        "[Judol Detector] Server is running but model is not loaded yet.",
      );
    }
  } catch {
    isServerAvailable = false;
    console.warn(`[Judol Detector] API server not found at ${API_BASE}`);
  }

  // Simpan status server supaya popup bisa menampilkannya
  if (typeof chrome !== "undefined" && chrome.storage) {
    chrome.storage.local.set({ isServerAvailable });
  }

  return isServerAvailable;
}

// Pemanggilan API

/**
 * Kirim satu komentar ke API prediksi.
 *
 * @param {string} text - teks komentar mentah
 * @returns {Promise<{is_spam: boolean, confidence: number, label: string} | null>}
 */
async function predictComment(text) {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
      signal: AbortSignal.timeout(5000),
    });

    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

/**
 * Kirim banyak komentar sekaligus dalam satu permintaan.
 *
 * Kalau gagal karena jaringan atau server mati, kesehatan server diperiksa
 * ulang supaya pemindaian berikutnya berhenti mencoba, bukan gagal diam-diam
 * setiap kali.
 *
 * @param {string[]} texts - array teks komentar mentah
 * @returns {Promise<Array | null>}
 */
async function predictBatch(texts) {
  try {
    const response = await fetch(BATCH_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texts }),
      signal: AbortSignal.timeout(10000),
    });

    if (!response.ok) return null;
    const data = await response.json();
    return data.results;
  } catch {
    // Server mungkin mati setelah pemeriksaan awal. Periksa ulang supaya
    // isServerAvailable ikut diperbarui.
    console.warn(
      "[Judol Detector] Batch request failed, re-checking server...",
    );
    await checkServerHealth();
    return null;
  }
}

// Manipulasi DOM

/**
 * Pasang tombol "Bukan spam?" pada komentar yang sudah disembunyikan.
 * Aman dipanggil berkali-kali karena memeriksa dulu apakah tombolnya sudah ada.
 *
 * @param {Element} element      - wadah komentar yang disembunyikan
 * @param {string}  originalText - teks mentah yang dikirim ke /report
 */
function attachReportButton(element, originalText) {
  if (element.querySelector("[data-judol-report]")) return; // sudah terpasang

  const reportBtn = document.createElement("div");
  reportBtn.dataset.judolReport = "true";
  reportBtn.style.cssText = `
    position: absolute;
    top: 4px;
    right: 70px;
    background: #1565c0;
    color: white;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 10px;
    font-family: sans-serif;
    z-index: 9999;
    cursor: pointer;
  `;
  reportBtn.textContent = "Bukan spam?";
  reportBtn.title = "[Dev] Laporkan ke dataset sebagai false positive";

  reportBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    reportFalsePositive(originalText, reportBtn);
  });

  element.appendChild(reportBtn);
}

async function reportFalsePositive(text, reportBtn) {
  reportBtn.textContent = "Mengirim...";
  reportBtn.style.cursor = "not-allowed";
  reportBtn.style.pointerEvents = "none";

  try {
    const res = await fetch(`${API_BASE}/report`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Report-Token": REPORT_TOKEN,
      },
      body: JSON.stringify({ text, label: "non_spam" }),
      signal: AbortSignal.timeout(5000),
    });
    const data = await res.json();

    if (data.duplicate) {
      reportBtn.textContent = "Sudah tercatat";
      reportBtn.style.background = "#607d8b";
    } else {
      reportBtn.textContent = "✓ Dilaporkan";
      reportBtn.style.background = "#388e3c";
      devLog(
        `[Judol Detector][DEV] Reported false positive: "${text.slice(0, 60)}..."`,
      );
    }
  } catch {
    reportBtn.textContent = "Gagal";
    reportBtn.style.background = "#555";
    console.warn("[Judol Detector][DEV] Failed to send report to server.");
  }
}

/**
 * Sembunyikan komentar spam sesuai hideMode yang dipilih pengguna.
 *
 * Tombol laporan hanya dipasang di mode "dim", karena elemen yang sudah
 * di-display:none tidak punya permukaan untuk menempelkannya.
 *
 * @param {Element} element     - wadah komentar di DOM
 * @param {number} confidence   - nilai kepercayaan model, 0 sampai 1
 * @param {string} originalText - teks mentah, dibutuhkan /report
 */
function hideSpamComment(element, confidence, originalText) {
  element.dataset.judolDetected = "spam";
  element.dataset.judolConfidence = confidence.toFixed(2);
  element.dataset.judolText = originalText;

  if (hideMode === "remove") {
    element.style.display = "none";
    hiddenCount++;
    persistStats();
    return;
  }

  element.style.transition = "opacity 0.3s ease, max-height 0.5s ease";
  element.style.opacity = "0.15";
  element.style.border = "1px solid #ff4444";
  element.style.borderRadius = "4px";
  element.style.position = "relative";

  // Lencana kecil berisi nilai kepercayaan, bisa diklik untuk menampilkan
  const badge = document.createElement("div");
  badge.style.cssText = `
    position: absolute;
    top: 4px;
    right: 4px;
    background: #ff4444;
    color: white;
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 10px;
    font-family: sans-serif;
    z-index: 9999;
    cursor: pointer;
  `;
  badge.textContent = `Spam ${Math.round(confidence * 100)}%`;
  badge.title = "Klik untuk menampilkan komentar ini";

  badge.addEventListener("click", (e) => {
    e.stopPropagation();
    element.style.opacity = "1";
    element.style.border = "none";
    badge.remove();
  });

  element.appendChild(badge);

  // Mode pengembangan: tombol untuk melaporkan false positive
  if (DEV_MODE) {
    attachReportButton(element, originalText);
  }

  hiddenCount++;
  persistStats();
}

/**
 * hiddenCount dan scannedCount hanya hidup di memori tab ini, tidak pernah
 * ditulis ke chrome.storage. Storage itu dipakai bersama semua tab, jadi tab
 * mana pun yang menulis akan menimpa angka milik tab lain. Popup menanyakan
 * angkanya langsung ke tab aktif lewat pesan "getStats" di bawah.
 */
function persistStats() {}

// Pemindaian komentar

/**
 * Kumpulkan komentar yang belum diproses lalu kirim ke API per 50 teks.
 */
async function scanComments() {
  if (!isServerAvailable) return;

  const commentElements = document.querySelectorAll(SELECTORS.commentContainer);

  // Kumpulkan elemen yang belum pernah diproses
  const toProcess = [];
  commentElements.forEach((el) => {
    if (!processedComments.has(el)) {
      const textEl = el.querySelector(SELECTORS.commentText);
      if (textEl && textEl.textContent.trim().length > 0) {
        toProcess.push({ element: el, text: textEl.textContent.trim() });
        processedComments.add(el); // ditandai langsung supaya pemindaian ulang melewatinya
      }
    }
  });

  if (toProcess.length === 0) return;

  // Dihitung sebelum dikirim, karena komentar ini tetap terpindai terlepas
  // dari hasil klasifikasinya.
  scannedCount += toProcess.length;
  persistStats();

  devLog(
    `[Judol Detector] Scanning ${toProcess.length} new comment(s)... (total scanned: ${scannedCount})`,
  );

  // Ukuran batch mengikuti batas maksimum di sisi API
  const BATCH_SIZE = 50;
  for (let i = 0; i < toProcess.length; i += BATCH_SIZE) {
    const batch = toProcess.slice(i, i + BATCH_SIZE);
    const texts = batch.map((item) => item.text);

    const results = await predictBatch(texts);
    if (!results) continue;

    results.forEach((result, idx) => {
      if (result.is_spam && result.confidence >= confidenceThreshold) {
        hideSpamComment(batch[idx].element, result.confidence, batch[idx].text);
      }
    });
  }
}

// Pengaturan

/**
 * Muat ambang kepercayaan yang disimpan pengguna lewat penggeser di popup.
 * Kembali ke 0,75 kalau belum ada yang tersimpan.
 */
async function loadSettings() {
  if (typeof chrome === "undefined" || !chrome.storage) return;

  return new Promise((resolve) => {
    chrome.storage.local.get(
      ["confidenceThreshold", "hideMode"],
      (data) => {
        if (data.confidenceThreshold !== undefined) {
          confidenceThreshold = data.confidenceThreshold;
        }
        hideMode = data.hideMode === "remove" ? "remove" : "dim";

        devLog(
          `[Judol Detector] Threshold loaded from storage: ${Math.round(confidenceThreshold * 100)}%`,
        );
        if (DEV_MODE) {
          devLog(
            "[Judol Detector][DEV] Dev mode is ON, 'Bukan spam?' button enabled.",
          );
        }
        resolve();
      },
    );
  });
}

/**
 * Tanpa pendengar ini, perubahan ambang di popup baru berlaku setelah halaman
 * dimuat ulang.
 */
if (typeof chrome !== "undefined" && chrome.storage) {
  chrome.storage.onChanged.addListener((changes) => {
    if (changes.confidenceThreshold) {
      confidenceThreshold = changes.confidenceThreshold.newValue;
      devLog(
        `[Judol Detector] Threshold updated to: ${Math.round(confidenceThreshold * 100)}%`,
      );
    }
    if (changes.hideMode !== undefined) {
      hideMode = changes.hideMode.newValue === "remove" ? "remove" : "dim";
      devLog(`[Judol Detector] Hide mode updated to: ${hideMode}`);
    }
  });
}

// Pesan antar-komponen

/**
 * Popup tidak punya cara tahu angka tab mana yang sedang dilihatnya kecuali
 * bertanya langsung. Ia mengirim "getStats" atau "resetStats" ke content
 * script tab aktif, dan dijawab dengan penghitung milik tab ini sendiri.
 */
if (
  typeof chrome !== "undefined" &&
  chrome.runtime &&
  chrome.runtime.onMessage
) {
  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message?.type === "getStats") {
      sendResponse({ hiddenCount, scannedCount });
    } else if (message?.type === "resetStats") {
      hiddenCount = 0;
      scannedCount = 0;
      sendResponse({ hiddenCount, scannedCount });
    }
  });
}

// Pemantau DOM

/**
 * YouTube memuat komentar sambil pengguna menggulir, jadi penambahan simpul
 * DOM dipakai sebagai pemicu pemindaian ulang.
 *
 * Diberi jeda satu detik setelah perubahan terakhir supaya tidak memanggil
 * API berkali-kali saat halaman masih sibuk memuat.
 */
let scanTimeout = null;

const observer = new MutationObserver(() => {
  clearTimeout(scanTimeout);
  scanTimeout = setTimeout(scanComments, 1000);
});

// Inisialisasi

async function init() {
  // Pengaturan dimuat lebih dulu sebelum apa pun dikerjakan.
  await loadSettings();
  devLog("[Judol Detector] Extension loaded...");

  const serverOk = await checkServerHealth();
  if (!serverOk) {
    console.warn("[Judol Detector] Server unavailable, extension is inactive.");
    console.warn(
      "[Judol Detector] Make sure the Python server is running: python src/server.py",
    );
    return;
  }

  devLog(
    `[Judol Detector] Server OK · threshold: ${Math.round(confidenceThreshold * 100)}% · starting comment monitoring...`,
  );

  // Pindai komentar yang sudah ada saat halaman selesai dimuat
  await scanComments();

  // Watch for new comments added via infinite scroll
  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

// Jalankan ekstensi
init();
