/**
 * popup.js
 * ========
 * Logic for the extension popup UI.
 * The popup appears when the user clicks the extension icon in the browser toolbar.
 */

const API_BASE = "http://localhost:8000";

// DOM element references
const statusDot = document.getElementById("statusDot");
const statusLabel = document.getElementById("statusLabel");
const statusSub = document.getElementById("statusSub");
const hiddenCount = document.getElementById("hiddenCount");
const scannedCount = document.getElementById("scannedCount");
const btnCheck = document.getElementById("btnCheck");
const btnReset = document.getElementById("btnReset");
const thresholdSlider = document.getElementById("thresholdSlider");
const thresholdValue = document.getElementById("thresholdValue");
const devModeToggle = document.getElementById("devModeToggle");
const devModeBox = document.getElementById("devModeBox");
const modeProdBtn = document.getElementById("modeProdBtn");
const modeDevBtn = document.getElementById("modeDevBtn");

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
 * Get the active tab in the current window, so stats always reflect
 * whichever page the user is actually looking at.
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
 * Load and display spam detection statistics for the active tab.
 *
 * Stats live only in each tab's content.js memory (not in chrome.storage),
 * because a shared storage key would get overwritten every time any tab
 * scans comments — the popup would then show whichever tab wrote last
 * instead of the tab the user is currently viewing. Asking the active tab
 * directly guarantees the numbers always match what's on screen.
 */
async function loadStats() {
  const tab = await getActiveTab();
  if (!tab) {
    hiddenCount.textContent = 0;
    scannedCount.textContent = 0;
    return;
  }

  chrome.tabs.sendMessage(tab.id, { type: "getStats" }, (response) => {
    // chrome.runtime.lastError fires when content.js isn't injected on this
    // tab (e.g. not a YouTube/Instagram page) — just show zero in that case.
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
 * Reset the active tab's statistics counters and refresh the UI.
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
    thresholdSlider.value = pct;
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
// DEV MODE TOGGLE
// ---------------------------------------------------------------------------

/**
 * Load the saved dev mode state from chrome.storage and set the toggle.
 * Defaults to false (off) — dev mode is never on by default.
 */
function loadDevMode() {
  chrome.storage.local.get(["devMode"], (data) => {
    devModeToggle.checked = data.devMode === true;
  });
}

/**
 * Save dev mode state whenever the toggle changes.
 * content.js listens via chrome.storage.onChanged and updates immediately.
 */
devModeToggle.addEventListener("change", () => {
  chrome.storage.local.set({ devMode: devModeToggle.checked });
});

// ---------------------------------------------------------------------------
// APP MODE — Production (default) vs Development
// ---------------------------------------------------------------------------

/**
 * Show/hide the Dev Mode box based on the current app mode.
 * Production users should never even see that this feature exists.
 *
 * @param {"production" | "development"} mode
 */
function applyModeUI(mode) {
  modeProdBtn.classList.toggle("active", mode === "production");
  modeDevBtn.classList.toggle("active", mode === "development");
  modeDevBtn.classList.toggle("dev", mode === "development");
  devModeBox.classList.toggle("hidden", mode !== "development");
}

/**
 * Load the saved app mode from chrome.storage. Defaults to "production" —
 * dev-only UI must be opted into explicitly, never on by default.
 */
function loadAppMode() {
  chrome.storage.local.get(["appMode"], (data) => {
    const mode = data.appMode === "development" ? "development" : "production";
    applyModeUI(mode);
  });
}

/**
 * Save the app mode whenever the user clicks a mode button.
 * content.js listens via chrome.storage.onChanged and updates immediately —
 * switching to "production" turns off dev features even if the inner
 * "Bukan spam?" toggle was left on.
 */
function setAppMode(mode) {
  chrome.storage.local.set({ appMode: mode });
  applyModeUI(mode);
}

modeProdBtn.addEventListener("click", () => setAppMode("production"));
modeDevBtn.addEventListener("click", () => setAppMode("development"));

// ---------------------------------------------------------------------------
// EVENT LISTENERS & STARTUP
// ---------------------------------------------------------------------------

btnCheck.addEventListener("click", checkServer);
btnReset.addEventListener("click", resetStats);

// Run on popup open
checkServer();
loadStats();
loadThreshold();
loadDevMode();
loadAppMode();
