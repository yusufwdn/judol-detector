/**
 * content.js
 * ==========
 * Injected into YouTube/Instagram pages.
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

const API_URL = "http://localhost:8000/predict";
const BATCH_API_URL = "http://localhost:8000/predict/batch";

// Default threshold — will be overridden by value from chrome.storage on init.
// Users can change this via the slider in the popup.
let confidenceThreshold = 0.75;

// CSS selectors for comment elements on each supported platform.
// These are the most likely to break when platforms update their UI.
const SELECTORS = {
  youtube: {
    commentContainer: "ytd-comment-thread-renderer", // One full comment thread
    commentText: "#content-text", // The comment text node
  },
  instagram: {
    commentContainer: "ul._a9ym li", // May change with Instagram UI updates
    commentText: "span._aacl",
  },
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
    const response = await fetch("http://localhost:8000/health", {
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
    console.warn("[Judol Detector] API server not found at localhost:8000");
    console.warn(
      "[Judol Detector] Start the server with: python src/server.py",
    );
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
    console.warn("[Judol Detector] Batch request failed, re-checking server...");
    await checkServerHealth();
    return null;
  }
}

// ---------------------------------------------------------------------------
// DOM MANIPULATION
// ---------------------------------------------------------------------------

/**
 * Visually hide a spam comment with a semi-transparent overlay and badge.
 * The comment is NOT removed from the DOM — just visually suppressed.
 * Users can click the badge to reveal the comment if they choose.
 *
 * @param {Element} element  - The comment container DOM element
 * @param {number} confidence - Model confidence score (0-1)
 */
function hideSpamComment(element, confidence) {
  element.dataset.judolDetected = "spam";
  element.dataset.judolConfidence = confidence.toFixed(2);

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

  hiddenCount++;
  persistStats();
}

/**
 * Persist the current hiddenCount and scannedCount to chrome.storage
 * so the popup can read up-to-date numbers whenever it opens.
 */
function persistStats() {
  if (typeof chrome !== "undefined" && chrome.storage) {
    chrome.storage.local.set({ hiddenCount, scannedCount });
  }
}

// ---------------------------------------------------------------------------
// COMMENT SCANNING
// ---------------------------------------------------------------------------

/**
 * Scan all visible comment elements, collect unprocessed ones, and
 * send them to the API in batches of up to 50.
 */
async function scanComments() {
  if (!isServerAvailable) return;

  const platform = detectPlatform();
  if (!platform) return;

  const selector = SELECTORS[platform];
  const commentElements = document.querySelectorAll(selector.commentContainer);

  // Collect elements that haven't been processed yet
  const toProcess = [];
  commentElements.forEach((el) => {
    if (!processedComments.has(el)) {
      const textEl = el.querySelector(selector.commentText);
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

  console.log(
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
        hideSpamComment(batch[idx].element, result.confidence);
      }
    });
  }
}

/**
 * Detect the current platform based on the page hostname.
 *
 * @returns {"youtube" | "instagram" | null}
 */
function detectPlatform() {
  const url = window.location.hostname;
  if (url.includes("youtube.com")) return "youtube";
  if (url.includes("instagram.com")) return "instagram";
  return null;
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
    chrome.storage.local.get(["confidenceThreshold"], (data) => {
      if (data.confidenceThreshold !== undefined) {
        confidenceThreshold = data.confidenceThreshold;
        console.log(
          `[Judol Detector] Threshold loaded from storage: ${Math.round(confidenceThreshold * 100)}%`,
        );
      }
      resolve();
    });
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
      console.log(
        `[Judol Detector] Threshold updated to: ${Math.round(confidenceThreshold * 100)}%`,
      );
    }
  });
}

// ---------------------------------------------------------------------------
// MUTATION OBSERVER — Watch for dynamically loaded comments
// ---------------------------------------------------------------------------

/**
 * YouTube and Instagram load comments lazily as the user scrolls.
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
  console.log("[Judol Detector] Extension loaded...");

  // Load user settings before doing anything else
  await loadSettings();

  const serverOk = await checkServerHealth();
  if (!serverOk) {
    console.warn("[Judol Detector] Server unavailable, extension is inactive.");
    console.warn(
      "[Judol Detector] Make sure the Python server is running: python src/server.py",
    );
    return;
  }

  console.log(
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
