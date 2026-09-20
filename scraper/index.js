const fs = require("fs");
require("dotenv").config();

// Penguraian argumen

// Cara pakai:
//   node index.js <video_id> [run_mode] [data_mode]
//
// Contoh:
//   node index.js z-BTQKhWrJc                        → scrape spam dari komentar video (default)
//   node index.js z-BTQKhWrJc video spam             → sama seperti di atas (eksplisit)
//   node index.js z-BTQKhWrJc video non_spam         → scrape komentar NON-spam dari video
//   node index.js z-BTQKhWrJc live spam              → scrape spam dari live chat
//   node index.js z-BTQKhWrJc live non_spam          → scrape non-spam dari live chat

const VIDEO_ID = process.argv[2];
const RUN_MODE = process.argv[3] || "video";
const DATA_MODE = process.argv[4] || "spam";

if (!VIDEO_ID) {
  console.error(
    "[Config Error] Video ID wajib diisi sebagai argumen pertama.\n" +
      "Contoh: node index.js z-BTQKhWrJc\n" +
      "        node index.js z-BTQKhWrJc video non_spam",
  );
  process.exit(1);
}

if (!["video", "live"].includes(RUN_MODE)) {
  console.error(
    `[Config Error] run_mode tidak valid: "${RUN_MODE}".\n` +
      `Mode yang tersedia: "video" (default) atau "live".`,
  );
  process.exit(1);
}

if (!["spam", "non_spam"].includes(DATA_MODE)) {
  console.error(
    `[Config Error] data_mode tidak valid: "${DATA_MODE}".\n` +
      `Mode yang tersedia: "spam" (default) atau "non_spam".`,
  );
  process.exit(1);
}

// Konfigurasi

const API_KEY = process.env.YOUTUBE_API_KEY;
if (!API_KEY) {
  console.error(
    "[Config Error] YOUTUBE_API_KEY belum di-set.\n" +
      "Tambahkan baris berikut ke file .env di root project:\n" +
      "  YOUTUBE_API_KEY=isi_api_key_kamu",
  );
  process.exit(1);
}

// Minimum jumlah komentar yang ingin dikumpulkan sebelum script berhenti
const TARGET_COUNT = parseInt(process.env.TARGET_COUNT || "100", 10);

// Threshold skor heuristik untuk klasifikasi:
// - Komentar dengan skor >= SPAM_SCORE_THRESHOLD + hasPrimarySignal → spam
// - Komentar dengan skor < NON_SPAM_SCORE_THRESHOLD + tidak ada primarySignal → non_spam
const SPAM_SCORE_THRESHOLD = 30;
const NON_SPAM_SCORE_THRESHOLD = 10;

// Penyiapan direktori keluaran

const OUTPUT_DIR = "./result";
const HISTORY_FILE = `${OUTPUT_DIR}/scrape_history.json`;

// Buat folder /result jika belum ada
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  console.log(`[Setup] Folder output dibuat: ${OUTPUT_DIR}`);
}

// Riwayat pengambilan

/**
 * Membaca riwayat scraping dari file JSON.
 * Mengembalikan objek kosong jika file belum ada.
 *
 * @returns {Record<string, { mode: string, timestamp: string }[]>}
 */
function loadScrapeHistory() {
  if (!fs.existsSync(HISTORY_FILE)) return {};
  return JSON.parse(fs.readFileSync(HISTORY_FILE, "utf-8"));
}

/**
 * Menambahkan entri baru ke riwayat scraping dan menyimpannya ke file.
 *
 * @param {string} videoId - ID video yang baru selesai di-scrape
 * @param {string} mode - Mode scraping: "video" atau "live"
 */
function recordScrapeHistory(videoId, mode) {
  const history = loadScrapeHistory();
  if (!history[videoId]) history[videoId] = [];
  history[videoId].push({
    mode,
    timestamp: new Date().toISOString(),
  });
  fs.writeFileSync(HISTORY_FILE, JSON.stringify(history, null, 2));
}

/**
 * Mengecek apakah video ID sudah pernah di-scrape sebelumnya.
 * Jika iya, tampilkan warning ke console (scraping tetap dilanjutkan).
 *
 * @param {string} videoId
 */
function warnIfAlreadyScraped(videoId) {
  const history = loadScrapeHistory();
  if (!history[videoId]) return;

  const runs = history[videoId];
  const lastRun = runs.at(-1);

  console.warn(
    `[Warning] Video ID "${videoId}" sudah pernah di-scrape sebelumnya.\n` +
      `          Terakhir : mode=${lastRun.mode}, waktu=${lastRun.timestamp}\n` +
      `          Total run: ${runs.length}x, scraping tetap dilanjutkan.\n`,
  );
}

// Pembantu normalisasi Unicode
//
// KENAPA INI ADA DI SINI?
// NFKC saja (dipakai di analyzeSpamScore sejak awal) hanya membereskan
// varian Unicode dekoratif dalam BLOK yang sama (mathematical bold,
// full-width, dll). Ia TIDAK bisa menerjemahkan lintas SCRIPT, misalnya
// Cyrillic 'а' (U+0430) tidak pernah dianggap "sama" dengan Latin 'a'
// oleh algoritma NFKC, walau bentuknya identik secara visual. Karena itu
// kampanye yang memakai homoglyph Cyrillic/Greek/Thai bisa lolos scoring
// tanpa terdeteksi brand_pattern/contact_link/keyword sama sekali.
//
// Begitu juga leet-speak (H0KI777, s1tus, d3p0s1t), digit yang dipakai
// menggantikan huruf membuat regex huruf-only (mis. brandPattern
// `[a-z]{3,}...`) gagal cocok, karena digit memutus rangkaian huruf.
//
// Kedua map ini adalah PORT dari HOMOGLYPH_MAP dan leet normalization di
// `src/preprocessing.py` (proyek utama), bukan salinan penuh pipeline 7
// langkah di sana (yang untuk training model), hanya bagian yang relevan
// supaya scoring heuristik scraper tidak lagi buta terhadap trik yang
// sama. Root cause insiden Mantulhoki/Hoki777 (lihat TODO.md Fase 1).

const HOMOGLYPH_MAP = new Map(
  Object.entries({
    // Cyrillic → Latin
    а: "a",
    е: "e",
    о: "o",
    р: "p",
    с: "c",
    х: "x",
    і: "i",
    ѕ: "s",
    є: "e",
    А: "A",
    Е: "E",
    О: "O",
    Р: "P",
    С: "C",
    Т: "T",
    Х: "X",
    // Greek → Latin
    ν: "v",
    ο: "o",
    α: "a",
    ρ: "p",
    // Thai → Latin (bentuk mirip, contoh "ro๓a" → Thai ๓ mirip huruf m)
    "๓": "m",
  }),
);

const HOMOGLYPH_REGEX = new RegExp(
  `[${[...HOMOGLYPH_MAP.keys()].join("")}]`,
  "g",
);

/**
 * Ganti karakter homoglyph (Cyrillic/Greek/Thai yang bentuknya mirip Latin)
 * dengan padanan Latin-nya. Lihat komentar HOMOGLYPH_MAP di atas.
 *
 * @param {string} text
 * @returns {string}
 */
function applyHomoglyphMap(text) {
  return text.replace(HOMOGLYPH_REGEX, (ch) => HOMOGLYPH_MAP.get(ch));
}

/**
 * Normalisasi leet-speak dalam kata alphanumeric: 0→o, 1→i.
 * Hanya 2 substitusi ini (sama seperti preprocessing.py) karena keduanya
 * paling umum dipakai spam judol Indonesia (H0KI777, s1tus) dan cukup
 * tidak ambigu, 3/4/5 sengaja tidak disentuh karena berisiko memutilasi
 * angka yang legitimate.
 *
 * @param {string} text - Teks yang SUDAH di-lowercase
 * @returns {string}
 */
function normalizeLeetSpeak(text) {
  return text.replace(/\b[a-z0-9]*[0-9][a-z0-9]*\b/g, (word) =>
    word.replace(/0/g, "o").replace(/1/g, "i"),
  );
}

// SPAM SCORING ENGINE (HEURISTIC-BASED)

/**
 * Menganalisis teks komentar dan mengembalikan skor probabilitas spam (0-100).
 *
 * Logika skoring menggunakan sistem bobot berlapis:
 * - Sinyal Primer (bobot tinggi): Pola brand judol + link/kontak
 * - Sinyal Sekunder (bobot sedang): Kata kunci obfuscation + rasio simbol
 * - Sinyal Tersier (bobot rendah): Emoji berjejer + capslock berlebihan
 *
 * Komentar hanya disimpan jika ada minimal 1 sinyal primer yang aktif
 * untuk menghindari false positive dari komentar normal yang kebetulan
 * menggunakan banyak emoji atau huruf kapital.
 *
 * @param {string} rawText - Teks komentar asli (belum dinormalisasi)
 * @returns {{ score: number, normalizedText: string, activeSignals: string[], hasPrimarySignal: boolean }}
 */
function analyzeSpamScore(rawText) {
  let score = 0;
  const activeSignals = [];

  // Normalisasi NFKC: menghancurkan font unicode estetik yang sering dipakai spammer
  // Contoh: "𝗦𝗟𝗢𝗧" → "SLOT", "Ｇａｃｏｒ" → "Gacor"
  //
  // Lalu homoglyph substitution: NFKC tidak menjangkau lintas script, jadi
  // Cyrillic/Greek/Thai lookalike (dаftаr, ro๓a) perlu map terpisah.
  // `normalizedText` yang disimpan ke dataset SUDAH termasuk substitusi ini,
  // supaya nilai `normalized_text` di output konsisten dengan skor yang dihitung.
  const normalizedText = applyHomoglyphMap(rawText.normalize("NFKC"));

  // Leet-speak (H0KI777 → hoki777) dinormalisasi SETELAH lowercase, sama
  // seperti urutan di preprocessing.py, supaya brandPattern/keyword regex
  // di bawah bisa mengenali kata yang sebelumnya terputus oleh digit.
  const lowerText = normalizeLeetSpeak(normalizedText.toLowerCase());

  // --- SINYAL PRIMER ---

  // [+40] Pola brand judol: kombinasi nama + angka khas (88, 99, 777, dll)
  // Contoh: "MAXWIN88", "SLOT777", "BET138"
  const brandPattern =
    /[a-z]{3,}(88|99|77|69|138|388|777|888|4d|toto|bet|win)\b/i;
  if (brandPattern.test(lowerText)) {
    score += 40;
    activeSignals.push("brand_pattern");
  }

  // [+40] Link atau nomor kontak yang mengarahkan ke situs/WA
  // Contoh: "wa.me/628xxx", "bit.ly/xxx", "cek profil", "link di bio"
  const contactPattern =
    /(wa\.me|08[0-9]{8,11}|\+62[0-9]{9,12}|bit\.ly|s\.id|link\s?di|cek\s?profil|kunjungi|situs)/;
  if (contactPattern.test(lowerText)) {
    score += 40;
    activeSignals.push("contact_link");
  }

  // --- SINYAL SEKUNDER ---

  // [+30] Kata kunci judol dengan teknik obfuscation (karakter/spasi disisipkan)
  // Contoh: "g a c o r", "m@xw!n", "z3u5"
  const obfuscatedGacor = /g[\s\W]*[a4@][\s\W]*c[\s\W]*[o0][\s\W]*r/i;
  const obfuscatedMaxwin = /m[\s\W]*[a4@][\s\W]*x[\s\W]*w[\s\W]*[i1!][\s\W]*n/i;
  const obfuscatedZeus = /z[\s\W]*[e3][\s\W]*u[\s\W]*[s5$]/i;
  const obfuscatedJP = /j[\s\W]*[e3][\s\W]*p/i; // J3p, J e p, dll

  if (
    obfuscatedGacor.test(lowerText) ||
    obfuscatedMaxwin.test(lowerText) ||
    obfuscatedZeus.test(lowerText) ||
    obfuscatedJP.test(lowerText)
  ) {
    score += 30;
    activeSignals.push("obfuscated_keyword");
  }
  // [+20] Kata kunci judol standar (tanpa obfuscation)
  // Hanya aktif jika tidak ada obfuscation yang sudah terdeteksi di atas
  else {
    const plainKeywords =
      /(depo|wd|sl[o0]t|scatter|rungkad|mahjong|situs|poker|judi|jp|jepe\b)/;
    if (plainKeywords.test(lowerText)) {
      score += 20;
      activeSignals.push("plain_keyword");
    }
  }

  // [+20] Rasio simbol aneh tinggi (>15% dari total karakter)
  // Spammer sering pakai simbol untuk menghindari filter teks biasa
  const symbolCount = (normalizedText.match(/[^a-zA-Z0-9\s]/g) || []).length;
  if (normalizedText.length > 0 && symbolCount / normalizedText.length > 0.15) {
    score += 20;
    activeSignals.push("high_symbol_ratio");
  }

  // --- SINYAL TERSIER ---

  // [+15] Emoji berjejer (2 atau lebih emoji berurutan)
  // Pola "emoji sandwich" sering dipakai untuk menarik perhatian di spam
  const consecutiveEmojiPattern = /(\p{Emoji_Presentation}){2,}/gu;
  if (consecutiveEmojiPattern.test(normalizedText)) {
    score += 15;
    activeSignals.push("emoji_spam");
  }

  // [+10] Capslock berlebihan (>50% dari teks adalah huruf kapital)
  const uppercaseCount = (normalizedText.match(/[A-Z]/g) || []).length;
  if (
    normalizedText.length > 10 &&
    uppercaseCount / normalizedText.length > 0.5
  ) {
    score += 10;
    activeSignals.push("excessive_caps");
  }

  // [+35] Pola "soft brand", nama + angka 2 digit arbitrary + framing testimoni
  // Contoh: "ALEXIS17 sukses bantu", "HOKI99 nggak pernah kecewa"
  // Logika: brand judol soft sering pakai nama latin + 2 digit + kalimat endorse
  const softBrandPattern = /\b[a-z]{4,10}\d{2,3}\b/i;
  const testimonialPattern =
    /(sukses\s*bantu|nggak\s*salah|tidak\s*salah|terbukti|terpercaya|rekomen|recommended|banyak\s*orang|sudah\s*terbukti|membantu\s*banyak)/i;

  if (
    softBrandPattern.test(normalizedText) &&
    testimonialPattern.test(lowerText)
  ) {
    score += 35;
    activeSignals.push("soft_brand_testimonial");
  }

  // Tandai apakah ada sinyal primer (brand atau link) yang aktif.
  // Digunakan di luar fungsi ini untuk mencegah false positive dari sinyal sekunder saja.
  const hasPrimarySignal =
    activeSignals.includes("brand_pattern") ||
    activeSignals.includes("contact_link") ||
    activeSignals.includes("soft_brand_testimonial");

  return {
    score: Math.min(score, 100),
    normalizedText,
    activeSignals,
    hasPrimarySignal,
  };
}

// UTILITY: HTTP FETCH WITH RETRY

/**
 * Wrapper fetch dengan mekanisme retry dan exponential backoff.
 * Menangani HTTP 429 (Rate Limit) dan error jaringan sementara
 * agar scraping tidak langsung berhenti saat terkena throttling.
 *
 * @param {string} url - URL yang akan di-fetch
 * @param {number} [maxRetries=3] - Jumlah maksimum percobaan ulang
 * @returns {Promise<object>} - Parsed JSON response
 */
async function fetchWithRetry(url, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await fetch(url);

    if (response.status === 429) {
      // Exponential backoff: tunggu 1s, 2s, 4s sebelum retry
      const waitMs = Math.pow(2, attempt) * 1000;
      console.warn(
        `[Rate Limit] Terkena HTTP 429. Retry ke-${attempt + 1} dalam ${waitMs / 1000}s...`,
      );
      await sleep(waitMs);
      continue;
    }

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  throw new Error(`[Fetch Error] Gagal setelah ${maxRetries} kali percobaan.`);
}

/**
 * Helper: Jeda eksekusi selama N milidetik.
 * @param {number} ms
 */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// OUTPUT: SAVE RESULTS TO JSON FILE

/**
 * Menyimpan array hasil komentar spam ke file JSON di dalam folder /result.
 * Nama file menyertakan timestamp untuk mencegah overwrite pada run berulang.
 *
 * @param {object[]} results - Array objek komentar yang sudah dianalisis
 * @param {string} prefix - Prefix nama file (contoh: "spam_video", "spam_livechat")
 */
function saveResults(results, prefix) {
  const now = new Date();
  const timestamp =
    now.getFullYear().toString() +
    String(now.getMonth() + 1).padStart(2, "0") +
    String(now.getDate()).padStart(2, "0") +
    String(now.getHours()).padStart(2, "0") +
    String(now.getMinutes()).padStart(2, "0") +
    String(now.getSeconds()).padStart(2, "0");

  const filename = `${OUTPUT_DIR}/${prefix}_${timestamp}_${VIDEO_ID}.json`;
  fs.writeFileSync(filename, JSON.stringify(results, null, 2));
  console.log(`\n[Output] Dataset tersimpan di: ${filename}`);
  return filename;
}

// SCRAPER MODE 1: VIDEO COMMENTS

/**
 * Mengecek apakah suatu komentar lolos filter berdasarkan DATA_MODE aktif.
 *
 * - "spam"     : skor >= SPAM_SCORE_THRESHOLD DAN ada primary signal
 * - "non_spam" : skor < NON_SPAM_SCORE_THRESHOLD DAN tidak ada primary signal
 *                DAN panjang teks minimal 10 karakter (hindari komentar kosong/pendek)
 *
 * @param {{ score: number, hasPrimarySignal: boolean, normalizedText: string }} analysis
 * @returns {boolean}
 */
function isTargetComment(analysis) {
  if (DATA_MODE === "spam") {
    return analysis.score >= SPAM_SCORE_THRESHOLD && analysis.hasPrimarySignal;
  }
  // non_spam: skor rendah, tidak ada sinyal primer, dan cukup panjang
  return (
    analysis.score < NON_SPAM_SCORE_THRESHOLD &&
    !analysis.hasPrimarySignal &&
    analysis.normalizedText.trim().length >= 10
  );
}

/**
 * Komentar dengan skor 10-29 ("dead zone") tidak cukup tinggi untuk masuk
 * spam (>=30) tapi juga tidak cukup rendah untuk masuk non_spam (<10) -
 * sebelumnya rentang ini dibuang total tanpa jejak. Kasus FN "PBB4D"
 * (lihat DATASET_LOG.md Versi 11) berasal dari sini: komentar kritik/korban
 * yang menyebut brand ALL-CAPS+digit memicu brand_pattern, tapi tidak
 * cukup untuk lolos threshold spam karena tidak ada sinyal primer lain.
 * Rentang ini kemungkinan besar berisi banyak contoh "kritik + sebut brand"
 * yang justru paling dibutuhkan model, jadi disimpan terpisah untuk
 * direview manual, bukan dibuang. Lihat TODO.md Fase 1.
 *
 * @param {{ score: number }} analysis
 * @returns {boolean}
 */
function isBorderlineComment(analysis) {
  return (
    analysis.score >= NON_SPAM_SCORE_THRESHOLD &&
    analysis.score < SPAM_SCORE_THRESHOLD
  );
}

/**
 * Mengambil komentar dari video YouTube biasa (bukan live) menggunakan
 * YouTube Data API v3 endpoint `commentThreads`.
 *
 * Scraping berhenti jika:
 * - Jumlah komentar terkumpul sudah memenuhi TARGET_COUNT
 * - Tidak ada halaman komentar berikutnya (nextPageToken habis)
 * - Terjadi error dari API
 */
async function scrapeVideoComments() {
  warnIfAlreadyScraped(VIDEO_ID);

  const results = [];
  const borderlineResults = [];
  let nextPageToken = "";
  let totalScanned = 0;

  const label = DATA_MODE === "spam" ? "spam" : "non_spam";
  const filePrefix = `${label}_video`;

  const commentOrder = process.env.COMMENT_ORDER || "relevance";
  const baseUrl =
    `https://www.googleapis.com/youtube/v3/commentThreads` +
    `?part=snippet&videoId=${VIDEO_ID}&key=${API_KEY}&maxResults=100&order=${commentOrder}`;

  console.log(`[Video Mode] Mulai scraping komentar dari video: ${VIDEO_ID}`);
  console.log(
    `[Config] Data mode: ${DATA_MODE} | Target: ${TARGET_COUNT} komentar | ` +
      `Threshold spam: >=${SPAM_SCORE_THRESHOLD} | Threshold non-spam: <${NON_SPAM_SCORE_THRESHOLD}\n`,
  );

  try {
    while (results.length < TARGET_COUNT) {
      const requestUrl = nextPageToken
        ? `${baseUrl}&pageToken=${nextPageToken}`
        : baseUrl;

      const data = await fetchWithRetry(requestUrl);

      if (data.error) {
        console.error("[API Error]", data.error.message);
        break;
      }

      const items = data.items || [];

      for (const item of items) {
        totalScanned++;

        // Ambil teks original agar struktur karakter unicode tidak terpengaruh
        // oleh encoding HTML yang bisa ada di `textDisplay`
        const rawText = item.snippet.topLevelComment.snippet.textOriginal;

        // Hilangkan newline agar data JSON lebih bersih di satu baris
        const singleLineText = rawText.replace(/(\r\n|\n|\r)/gm, " ");

        const analysis = analyzeSpamScore(singleLineText);

        if (isTargetComment(analysis)) {
          results.push({
            video_id: VIDEO_ID,
            timestamp: new Date().toISOString(),
            original_text: singleLineText,
            normalized_text: analysis.normalizedText,
            spam_score: analysis.score,
            active_signals: analysis.activeSignals,
            label, // "spam" atau "non_spam", perlu diverifikasi manual sebelum masuk dataset
          });
        } else if (isBorderlineComment(analysis)) {
          // Skor 10-29, tidak dibuang, disimpan terpisah untuk review manual.
          borderlineResults.push({
            video_id: VIDEO_ID,
            timestamp: new Date().toISOString(),
            original_text: singleLineText,
            normalized_text: analysis.normalizedText,
            spam_score: analysis.score,
            active_signals: analysis.activeSignals,
            label: "borderline",
          });
        }
      }

      console.log(
        `[Scan] Dicek: ${totalScanned} | Terkumpul (${label}): ${results.length}/${TARGET_COUNT} | Borderline: ${borderlineResults.length}`,
      );

      nextPageToken = data.nextPageToken;
      if (!nextPageToken) {
        console.log("[Info] Semua halaman komentar sudah dipindai.");
        break;
      }

      // Jeda 500ms antar request untuk menghindari rate limit
      await sleep(500);
    }

    console.log(
      `\n[Selesai] Terkumpul ${results.length} komentar "${label}" dan ${borderlineResults.length} komentar borderline dari ${totalScanned} komentar.`,
    );

    saveResults(results, filePrefix);
    if (borderlineResults.length > 0) {
      saveResults(borderlineResults, "borderline_video");
    }
    recordScrapeHistory(VIDEO_ID, "video");
  } catch (error) {
    console.error("[Fatal Error]", error.message);
  }
}

// SCRAPER MODE 2: LIVE CHAT

/**
 * Memantau dan mengambil pesan spam dari live chat YouTube secara real-time.
 * Menggunakan polling sesuai interval yang ditetapkan YouTube API (`pollingIntervalMillis`).
 *
 * Proses dua tahap:
 * 1. Ambil `activeLiveChatId` dari data video
 * 2. Lakukan polling berkala ke endpoint `liveChatMessages`
 *
 * @param {string} liveVideoId - ID video YouTube yang sedang live
 */
async function scrapeLiveChat(liveVideoId) {
  warnIfAlreadyScraped(liveVideoId);

  const results = [];
  const borderlineResults = [];
  const label = DATA_MODE === "spam" ? "spam" : "non_spam";
  const filePrefix = `${label}_livechat`;

  console.log(
    `[Live Mode] Mencari live chat ID untuk video: ${liveVideoId}...`,
  );

  // --- TAHAP 1: Ambil Live Chat ID ---
  const videoDetailUrl =
    `https://www.googleapis.com/youtube/v3/videos` +
    `?part=liveStreamingDetails&id=${liveVideoId}&key=${API_KEY}`;

  const videoData = await fetchWithRetry(videoDetailUrl);

  const liveChatId =
    videoData.items?.[0]?.liveStreamingDetails?.activeLiveChatId;

  if (!liveChatId) {
    console.error(
      "[Error] Video ini tidak sedang live atau live chat-nya dinonaktifkan.",
    );
    return;
  }

  console.log(`[Live Mode] Live Chat ID ditemukan: ${liveChatId}`);
  console.log(
    `[Config] Data mode: ${DATA_MODE} | Target: ${TARGET_COUNT} | Mulai memantau...\n`,
  );

  // --- TAHAP 2: Polling Live Chat ---
  let nextPageToken = "";
  const chatBaseUrl =
    `https://www.googleapis.com/youtube/v3/liveChatMessages` +
    `?liveChatId=${liveChatId}&part=snippet&key=${API_KEY}`;

  try {
    while (results.length < TARGET_COUNT) {
      const requestUrl = nextPageToken
        ? `${chatBaseUrl}&pageToken=${nextPageToken}`
        : chatBaseUrl;

      const chatData = await fetchWithRetry(requestUrl);

      if (chatData.error) {
        console.error("[API Error]", chatData.error.message);
        break;
      }

      const items = chatData.items || [];

      for (const item of items) {
        const messageText = item.snippet.displayMessage;
        const analysis = analyzeSpamScore(messageText);

        if (isTargetComment(analysis)) {
          results.push({
            video_id: liveVideoId,
            timestamp: new Date().toISOString(),
            original_text: messageText,
            normalized_text: analysis.normalizedText,
            spam_score: analysis.score,
            active_signals: analysis.activeSignals,
            label,
          });
        } else if (isBorderlineComment(analysis)) {
          borderlineResults.push({
            video_id: liveVideoId,
            timestamp: new Date().toISOString(),
            original_text: messageText,
            normalized_text: analysis.normalizedText,
            spam_score: analysis.score,
            active_signals: analysis.activeSignals,
            label: "borderline",
          });
        }
      }

      console.log(
        `[Live Scan] Terkumpul (${label}): ${results.length}/${TARGET_COUNT} | Borderline: ${borderlineResults.length}`,
      );

      nextPageToken = chatData.nextPageToken;

      if (!nextPageToken) {
        console.log("[Info] Live stream telah berakhir atau chat tidak aktif.");
        break;
      }

      // YouTube mewajibkan kita menunggu sesuai pollingIntervalMillis
      // agar tidak dianggap abuse dan API key tidak diblokir
      const pollingIntervalMs = chatData.pollingIntervalMillis || 3000;
      await sleep(pollingIntervalMs);
    }

    console.log(
      `\n[Selesai] Terkumpul ${results.length} pesan "${label}" dan ${borderlineResults.length} pesan borderline dari live chat.`,
    );

    saveResults(results, filePrefix);
    if (borderlineResults.length > 0) {
      saveResults(borderlineResults, "borderline_livechat");
    }
    recordScrapeHistory(liveVideoId, "live");
  } catch (error) {
    console.error("[Fatal Error]", error.message);
  }
}

// Titik masuk

if (RUN_MODE === "live") {
  scrapeLiveChat(VIDEO_ID);
} else {
  scrapeVideoComments();
}
