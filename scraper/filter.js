const fs = require("fs");
const path = require("path");

const RESULT_DIR = path.join(__dirname, "result");

/**
 * Baca semua file JSON dari result/, kelompokkan berdasarkan label prefix.
 * File dengan prefix "spam_" → kelompok spam
 * File dengan prefix "non_spam_" → kelompok non_spam
 */
function loadByLabel() {
  const files = fs
    .readdirSync(RESULT_DIR)
    .filter((f) => f.endsWith(".json") && f !== "scrape_history.json");

  const groups = { spam: [], non_spam: [], borderline: [] };

  for (const file of files) {
    const filePath = path.join(RESULT_DIR, file);
    let data;
    try {
      data = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    } catch {
      console.warn(`[Warning] Gagal parse ${file}, dilewati.`);
      continue;
    }

    if (!Array.isArray(data)) continue;

    // borderline_ dicek duluan karena juga match prefix "border..." tidak
    // overlap dengan spam_/non_spam_, tapi urutan ini menjaga niat eksplisit.
    if (file.startsWith("borderline_")) {
      groups.borderline.push(...data);
    } else if (file.startsWith("non_spam_")) {
      groups.non_spam.push(...data);
    } else if (file.startsWith("spam_")) {
      groups.spam.push(...data);
    } else {
      console.warn(
        `[Warning] File "${file}" tidak punya prefix yang dikenal (spam_/non_spam_/borderline_), dilewati.`,
      );
    }
  }

  return groups;
}

/**
 * Hapus duplikat berdasarkan normalized_text, terapkan blocklist kata non-judol
 * yang diketahui menghasilkan false positive.
 */
function deduplicateAndFilter(comments, blocklist = []) {
  const seen = new Set();
  return comments.filter((item) => {
    const key = item.normalized_text?.trim().toLowerCase();
    if (!key) return false;
    if (blocklist.some((word) => key.includes(word))) return false;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function aggregate() {
  const groups = loadByLabel();

  // Blocklist hanya relevan untuk spam (false positive judol yang bukan judol)
  const spamBlocklist = ["belibet", "lowbet", "blibet", "dzawin", "kulbet"];

  const cleanSpam = deduplicateAndFilter(groups.spam, spamBlocklist);
  const cleanNonSpam = deduplicateAndFilter(groups.non_spam);
  const cleanBorderline = deduplicateAndFilter(groups.borderline);

  // --- Spam ---
  console.log("\n[Spam]");
  console.log(`  Raw     : ${groups.spam.length}`);
  console.log(
    `  Bersih  : ${cleanSpam.length} (duplikat/false-positive dihapus: ${groups.spam.length - cleanSpam.length})`,
  );

  const spamOutput = path.join(__dirname, "final_spam.json");
  fs.writeFileSync(spamOutput, JSON.stringify(cleanSpam, null, 2), "utf-8");
  console.log(`  Disimpan: ${spamOutput}`);

  // --- Non-Spam ---
  console.log("\n[Non-Spam]");
  console.log(`  Raw     : ${groups.non_spam.length}`);
  console.log(
    `  Bersih  : ${cleanNonSpam.length} (duplikat dihapus: ${groups.non_spam.length - cleanNonSpam.length})`,
  );

  const nonSpamOutput = path.join(__dirname, "final_non_spam.json");
  fs.writeFileSync(
    nonSpamOutput,
    JSON.stringify(cleanNonSpam, null, 2),
    "utf-8",
  );
  console.log(`  Disimpan: ${nonSpamOutput}`);

  // --- Borderline (skor 10-29, belum berlabel, untuk review manual) ---
  if (cleanBorderline.length > 0) {
    console.log("\n[Borderline] (skor 10-29, BELUM berlabel, wajib direview manual)");
    console.log(`  Raw     : ${groups.borderline.length}`);
    console.log(
      `  Bersih  : ${cleanBorderline.length} (duplikat dihapus: ${groups.borderline.length - cleanBorderline.length})`,
    );

    const borderlineOutput = path.join(__dirname, "final_borderline.json");
    fs.writeFileSync(
      borderlineOutput,
      JSON.stringify(cleanBorderline, null, 2),
      "utf-8",
    );
    console.log(`  Disimpan: ${borderlineOutput}`);
  }

  console.log(
    `\n[Total dataset] spam: ${cleanSpam.length} | non_spam: ${cleanNonSpam.length} | borderline (perlu review): ${cleanBorderline.length}`,
  );
}

aggregate();
