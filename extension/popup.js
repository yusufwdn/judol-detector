/**
 * popup.js
 * ========
 * Logic for the extension popup UI.
 * The popup appears when the user clicks the extension icon in the browser toolbar.
 */

const API_BASE = "http://localhost:8000";

// DOM element references
const statusDot    = document.getElementById("statusDot");
const statusLabel  = document.getElementById("statusLabel");
const statusSub    = document.getElementById("statusSub");
const hiddenCount  = document.getElementById("hiddenCount");
const scannedCount = document.getElementById("scannedCount");
const btnCheck     = document.getElementById("btnCheck");
const btnReset     = document.getElementById("btnReset");
const thresholdSlider = document.getElementById("thresholdSlider");
const thresholdValue  = document.getElementById("thresholdValue");

/**
 * Check the health of the Python API server and update the status indicator.
 */
async function checkServer() {
  setStatus("loading", "Checking server...", "localhost:8000");

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
    setStatus("offline", "Server unavailable", "Run: python src/server.py");
  }
}

/**
 * Update the status indicator dot and labels.
 *
 * @param {"online" | "offline" | "loading"} state
 * @param {string} label - Primary status text
 * @param {string} sub   - Secondary/detail text
 */
function setStatus(state, label, sub) {
  statusDot.className = `status-dot ${state}`;
  statusLabel.textContent = label;
  statusSub.textContent = sub;
}

/**
 * Load and display spam detection statistics from chrome.storage.
 */
function loadStats() {
  chrome.storage.local.get(["hiddenCount", "scannedCount"], (data) => {
    hiddenCount.textContent  = data.hiddenCount  || 0;
    scannedCount.textContent = data.scannedCount || 0;
  });
}

/**
 * Reset all statistics counters in chrome.storage and the UI.
 */
function resetStats() {
  chrome.storage.local.set({ hiddenCount: 0, scannedCount: 0 }, () => {
    hiddenCount.textContent  = 0;
    scannedCount.textContent = 0;
  });
}

// ---------------------------------------------------------------------------
// THRESHOLD SLIDER
// ---------------------------------------------------------------------------

/**
 * Load the saved confidence threshold from chrome.storage and set the slider.
 * Defaults to 0.75 (75%) if the user hasn't changed it before.
 */
function loadThreshold() {
  chrome.storage.local.get(["confidenceThreshold"], (data) => {
    const pct = Math.round((data.confidenceThreshold ?? 0.75) * 100);
    thresholdSlider.value   = pct;
    thresholdValue.textContent = `${pct}%`;
  });
}

/**
 * Save the threshold to chrome.storage when the user moves the slider.
 *
 * Why save as a decimal (0.0–1.0)?
 * content.js compares threshold against the model's confidence score, which
 * the API always returns as a decimal. Storing as decimal avoids a conversion
 * step in content.js and keeps the format consistent with the API response.
 */
thresholdSlider.addEventListener("input", () => {
  const pct = parseInt(thresholdSlider.value, 10);
  thresholdValue.textContent = `${pct}%`;
  chrome.storage.local.set({ confidenceThreshold: pct / 100 });
});

// ---------------------------------------------------------------------------
// EVENT LISTENERS & STARTUP
// ---------------------------------------------------------------------------

btnCheck.addEventListener("click", checkServer);
btnReset.addEventListener("click", resetStats);

// Run on popup open
checkServer();
loadStats();
loadThreshold();
