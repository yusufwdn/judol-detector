/**
 * content.js
 * ==========
 * Injected into YouTube pages.
 * Finds comment elements, sends them to the API, and hides spam results.
 *
 * WHAT IS A CONTENT SCRIPT?
 * --------------------------
 * Browser extensions can inject JavaScript into web pages the user is viewing.
 * This script runs inside the page context, so it can:
 * - Read and modify the DOM (HTML elements on the page)
 * - Fetch to our localhost API
 * - But CANNOT access the page's own JavaScript variables (browser security)
 *
 * WHY RAW TEXT ONLY — NO PRE-PROCESSING IN JS
 * --------------------------------------------
 * This script sends raw, unmodified comment text to the server.
 * All normalization (unicode, emoji, homoglyphs) happens in Python.
 * This is intentional: the training pipeline also processes raw text,
 * so training and inference always use the same transformations.
 * Doing normalization in two different environments (JS + Python) would
 * introduce subtle inconsistencies that silently degrade model accuracy.
 */

// ---------------------------------------------------------------------------
// CONFIGURATION
// ---------------------------------------------------------------------------

const API_BASE = "https://api-svm.cupsky.my.id";
const API_URL = `${API_BASE}/predict`;
const BATCH_API_URL = `${API_BASE}/predict/batch`;
// Left empty on purpose. /report writes straight into the training dataset,
// and this file ships to every user and is published with the thesis source —
// a token written here is readable by anyone, which is no protection at all.
//
// The endpoint is only ever called when DEV_MODE below is true. When you do
// want to collect corrections locally, paste the server's REPORT_TOKEN here in
// your own working copy and flip DEV_MODE — just never commit either change.
const REPORT_TOKEN = "";

// Default threshold — will be overridden by value from chrome.storage on init.
// Users can change this via the slider in the popup.
let confidenceThreshold = 0.75;

// How a detected spam comment is visually handled — set via the popup.
// "dim": semi-transparent overlay + badge the user can click to reveal it.
// "remove": the comment is hidden outright (display: none), no badge.
let hideMode = "dim";

// Dev flag — analogous to NODE_ENV in Node.js. This is a developer-only
// switch: flip it manually in this file before running locally, then flip
// it back before shipping. It is never exposed in the popup UI and never
// read from chrome.storage, so end users have no way to turn it on.
// When true, a "Bukan spam?" button appears on every hidden comment, letting
// whoever is testing report false positives straight into the CSV dataset.
const DEV_MODE = false;

/**
 * Log only when running in development mode — keeps the production
 * console clean for end users while still helping during debugging.
 * console.warn calls (server errors) are left as-is since those are
 * useful to any user troubleshooting a dead server.
 */
function devLog(...args) {
  if (DEV_MODE) console.log(...args);
}

// CSS selectors for comment elements on YouTube.
// Most likely to break when YouTube updates its UI.
const SELECTORS = {
  commentContainer: "ytd-comment-thread-renderer", // One full comment thread
  commentText: "#content-text", // The comment text node
};

// ---------------------------------------------------------------------------
// STATE
// ---------------------------------------------------------------------------

let processedComments = new WeakSet(); // Tracks elements already processed
let hiddenCount = 0;
let scannedCount = 0;
let isServerAvailable = false;

// ---------------------------------------------------------------------------
// SERVER HEALTH CHECK
// ---------------------------------------------------------------------------

/**
 * Check whether the Python API server is running and the model is loaded.
 * Called once at startup AND automatically when a batch request fails,
 * so the extension recovers gracefully if the server restarts mid-session.
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

  // Sync server status to storage so the popup can reflect it
  if (typeof chrome !== "undefined" && chrome.storage) {
    chrome.storage.local.set({ isServerAvailable });
  }

  return isServerAvailable;
}

// ---------------------------------------------------------------------------
// API CALLS
// ---------------------------------------------------------------------------

/**
 * Send a single comment to the prediction API.
 *
 * @param {string} text - Raw comment text
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
 * Send multiple comments in a single batch request (more efficient).
 *
 * If the request fails (network error or server down), automatically
 * re-checks server health so the extension stops trying on the next
 * scan cycle instead of failing silently every time.
 *
 * @param {string[]} texts - Array of raw comment texts
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
    // Batch failed — server may have gone down after the initial health check.
    // Re-check so isServerAvailable is updated and future scans don't keep
    // hitting a dead server.
    console.warn(
      "[Judol Detector] Batch request failed, re-checking server...",
    );
    await checkServerHealth();
    return null;
  }
}

// ---------------------------------------------------------------------------
// DOM MANIPULATION
// ---------------------------------------------------------------------------

/**
 * [DEV MODE] Send a comment text to the server to be saved as non_spam in the dataset.
 * Called when the user clicks "Bukan spam?" on a hidden comment.
 *
 * @param {string} text       - Original raw comment text
 * @param {Element} reportBtn - The button element (updated to show feedback)
 */
/**
 * Attach a "Bukan spam?" report button to an already-hidden comment element.
 * Checks first that a button doesn't already exist (safe to call multiple times).
 *
 * @param {Element} element      - The hidden comment container
 * @param {string}  originalText - Raw comment text to send to /report
 */
function attachReportButton(element, originalText) {
  if (element.querySelector("[data-judol-report]")) return; // already attached

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
 * Hide a spam comment according to the user's chosen hideMode.
 *
 * "dim": semi-transparent overlay + badge — comment stays in the DOM and
 * the user can click the badge to reveal it.
 * "remove": the comment is hidden outright (display: none), no badge.
 *
 * In dev mode, an additional "Bukan spam?" button is shown (dim mode only,
 * since a removed element has no visible surface to attach it to). Clicking
 * it sends the comment text to POST /report so it gets saved as non_spam.
 *
 * @param {Element} element   - The comment container DOM element
 * @param {number} confidence - Model confidence score (0-1)
 * @param {string} originalText - Raw comment text (needed for /report)
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

  // Small badge showing spam confidence, clickable to reveal
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
  badge.title = "Click to reveal this comment";

  // Click the badge to restore the comment
  badge.addEventListener("click", (e) => {
    e.stopPropagation();
    element.style.opacity = "1";
    element.style.border = "none";
    badge.remove();
  });

  element.appendChild(badge);

  // Dev mode: show a "Bukan spam?" button to report this comment as a false positive
  if (DEV_MODE) {
    attachReportButton(element, originalText);
  }

  hiddenCount++;
  persistStats();
}

/**
 * hiddenCount/scannedCount live only in this tab's memory — they are never
 * written to chrome.storage. That storage is shared by every tab, so any
 * tab writing there would clobber the others' numbers (last write wins).
 * Instead the popup asks the active tab directly for its counts, see the
 * "getStats"/"resetStats" message listener below.
 */
function persistStats() {}

// ---------------------------------------------------------------------------
// COMMENT SCANNING
// ---------------------------------------------------------------------------

/**
 * Scan all visible comment elements, collect unprocessed ones, and
 * send them to the API in batches of up to 50.
 */
async function scanComments() {
  if (!isServerAvailable) return;

  const commentElements = document.querySelectorAll(SELECTORS.commentContainer);

  // Collect elements that haven't been processed yet
  const toProcess = [];
  commentElements.forEach((el) => {
    if (!processedComments.has(el)) {
      const textEl = el.querySelector(SELECTORS.commentText);
      if (textEl && textEl.textContent.trim().length > 0) {
        toProcess.push({ element: el, text: textEl.textContent.trim() });
        processedComments.add(el); // Mark as seen immediately so re-scans skip it
      }
    }
  });

  if (toProcess.length === 0) return;

  // Update scannedCount BEFORE sending to API — these comments are "scanned"
  // regardless of whether they turn out to be spam or not.
  scannedCount += toProcess.length;
  persistStats();

  devLog(
    `[Judol Detector] Scanning ${toProcess.length} new comment(s)... (total scanned: ${scannedCount})`,
  );

  // Send in batches matching the API's max batch size
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

// ---------------------------------------------------------------------------
// SETTINGS — Load threshold from storage and listen for changes
// ---------------------------------------------------------------------------

/**
 * Load the confidence threshold saved by the user via the popup slider.
 * Falls back to 0.75 (75%) if nothing is stored yet.
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
            "[Judol Detector][DEV] Dev mode is ON — 'Bukan spam?' button enabled.",
          );
        }
        resolve();
      },
    );
  });
}

/**
 * Listen for threshold changes made by the user in the popup while
 * this content script is already running. Without this listener, a
 * threshold change only takes effect after a full page reload.
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

// ---------------------------------------------------------------------------
// MESSAGING — Let the popup query/reset THIS tab's stats on demand
// ---------------------------------------------------------------------------

/**
 * The popup has no way to know which tab's numbers it's looking at unless
 * it asks the tab directly. It sends "getStats"/"resetStats" to the active
 * tab's content script (chrome.tabs.sendMessage), and we reply with this
 * tab's own in-memory counters instead of a shared/global value.
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

// ---------------------------------------------------------------------------
// MUTATION OBSERVER — Watch for dynamically loaded comments
// ---------------------------------------------------------------------------

/**
 * YouTube loads comments lazily as the user scrolls.
 * MutationObserver fires whenever new nodes are added to the DOM,
 * triggering a fresh scan for unprocessed comments.
 *
 * Debounce: wait 1 second after the last DOM change before scanning.
 * This prevents excessive API calls while the page is still loading.
 */
let scanTimeout = null;

const observer = new MutationObserver(() => {
  clearTimeout(scanTimeout);
  scanTimeout = setTimeout(scanComments, 1000);
});

// ---------------------------------------------------------------------------
// INITIALIZATION
// ---------------------------------------------------------------------------

async function init() {
  // Load user settings (threshold, hideMode) before doing anything else.
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

  // Initial scan for comments already present on page load
  await scanComments();

  // Watch for new comments added via infinite scroll
  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

// Start the extension
init();
