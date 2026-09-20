/**
 * Panel pengaturan yang muncul saat ikon ekstensi diklik di bilah alat.
 */

const API_BASE = "https://api-svm.cupsky.my.id";

// Rujukan elemen DOM
const statusDot = document.getElementById("statusDot");
const statusLabel = document.getElementById("statusLabel");
const statusSub = document.getElementById("statusSub");
const hiddenCount = document.getElementById("hiddenCount");
const scannedCount = document.getElementById("scannedCount");
const btnCheck = document.getElementById("btnCheck");
const btnReset = document.getElementById("btnReset");
const thresholdSlider = document.getElementById("thresholdSlider");
const thresholdValue = document.getElementById("thresholdValue");
const hideModeDimBtn = document.getElementById("hideModeDimBtn");
const hideModeRemoveBtn = document.getElementById("hideModeRemoveBtn");

/**
 * Periksa kesehatan server lalu perbarui indikator status.
 */
async function checkServer() {
  setStatus("loading", "Checking server...", "Please wait while we check the server status");

  try {
    const res = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(3000),
    });
    const data = await res.json();

    if (data.model_loaded) {
      setStatus("online", "Server Active", "SVM model is ready");
    } else {
      setStatus(
        "offline",
        "Server running, model not loaded",
        "Run: python src/train.py first",
      );
    }
  } catch {
    setStatus("offline", "Server unavailable", "The server is currently offline; please try again later");
  }
}

/**
 * Perbarui titik indikator beserta labelnya.
 *
 * @param {"online" | "offline" | "loading"} state
 * @param {string} label - teks status utama
 * @param {string} sub   - teks keterangan
 */
function setStatus(state, label, sub) {
  statusDot.className = `status-dot ${state}`;
  statusLabel.textContent = label;
  statusSub.textContent = sub;
}

/**
 * Ambil tab yang sedang aktif, supaya angka yang ditampilkan selalu milik
 * halaman yang benar-benar sedang dilihat pengguna.
 *
 * @returns {Promise<chrome.tabs.Tab | null>}
 */
function getActiveTab() {
  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      resolve(tabs[0] || null);
    });
  });
}

/**
 * Muat dan tampilkan statistik deteksi untuk tab aktif.
 *
 * Angkanya hanya hidup di memori content.js tiap tab, bukan di
 * chrome.storage, karena kunci storage yang dipakai bersama akan tertimpa
 * setiap kali tab mana pun memindai komentar. Bertanya langsung ke tab aktif
 * memastikan angkanya selalu cocok dengan yang terlihat di layar.
 */
async function loadStats() {
  const tab = await getActiveTab();
  if (!tab) {
    hiddenCount.textContent = 0;
    scannedCount.textContent = 0;
    return;
  }

  chrome.tabs.sendMessage(tab.id, { type: "getStats" }, (response) => {
    // chrome.runtime.lastError muncul kalau content.js tidak disuntikkan di
    // tab ini, misalnya halamannya bukan YouTube. Tampilkan nol saja.
    if (chrome.runtime.lastError || !response) {
      hiddenCount.textContent = 0;
      scannedCount.textContent = 0;
      return;
    }
    hiddenCount.textContent = response.hiddenCount || 0;
    scannedCount.textContent = response.scannedCount || 0;
  });
}

/**
 * Nolkan penghitung statistik tab aktif lalu segarkan tampilannya.
 */
async function resetStats() {
  const tab = await getActiveTab();
  if (!tab) return;

  chrome.tabs.sendMessage(tab.id, { type: "resetStats" }, (response) => {
    if (chrome.runtime.lastError || !response) return;
    hiddenCount.textContent = response.hiddenCount || 0;
    scannedCount.textContent = response.scannedCount || 0;
  });
}

// Penggeser ambang batas

/**
 * Muat ambang kepercayaan tersimpan lalu setel posisi penggeser.
 * Nilai bawaannya 0,75 kalau pengguna belum pernah mengubahnya.
 */
function loadThreshold() {
  chrome.storage.local.get(["confidenceThreshold"], (data) => {
    const pct = Math.round((data.confidenceThreshold ?? 0.75) * 100);
    thresholdSlider.value = pct;
    thresholdValue.textContent = `${pct}%`;
  });
}

/**
 * Simpan ambang saat penggeser digerakkan.
 *
 * Disimpan sebagai desimal, bukan persen, supaya formatnya sama dengan nilai
 * kepercayaan yang dikembalikan API. Dengan begitu content.js bisa langsung
 * membandingkannya tanpa konversi.
 */
thresholdSlider.addEventListener("input", () => {
  const pct = parseInt(thresholdSlider.value, 10);
  thresholdValue.textContent = `${pct}%`;
  chrome.storage.local.set({ confidenceThreshold: pct / 100 });
});

// Mode penyembunyian

/**
 * Tandai mode yang sedang aktif di tombol pilihan.
 *
 * @param {"dim" | "remove"} mode
 */
function applyHideModeUI(mode) {
  hideModeDimBtn.classList.toggle("active", mode === "dim");
  hideModeRemoveBtn.classList.toggle("active", mode === "remove");
}

/**
 * Muat mode penyembunyian tersimpan. Bawaannya "dim", yaitu komentar
 * diredupkan dan diberi lencana yang bisa diklik untuk menampilkannya lagi.
 */
function loadHideMode() {
  chrome.storage.local.get(["hideMode"], (data) => {
    const mode = data.hideMode === "remove" ? "remove" : "dim";
    applyHideModeUI(mode);
  });
}

/**
 * Simpan mode setiap kali tombolnya diklik. content.js mendengarkan lewat
 * chrome.storage.onChanged dan langsung menyesuaikan.
 */
function setHideMode(mode) {
  chrome.storage.local.set({ hideMode: mode });
  applyHideModeUI(mode);
}

hideModeDimBtn.addEventListener("click", () => setHideMode("dim"));
hideModeRemoveBtn.addEventListener("click", () => setHideMode("remove"));

// Pendengar peristiwa dan inisialisasi

btnCheck.addEventListener("click", checkServer);
btnReset.addEventListener("click", resetStats);

// Dijalankan saat popup dibuka
checkServer();
loadStats();
loadThreshold();
loadHideMode();
