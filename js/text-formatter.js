// js/text-formatter.js - Readability formatting & consistent SVG UI icons

const PRESERVED_TOKENS = {
  rta: "RTA",
  rto: "RTO",
  llr: "LLR",
  dl: "DL",
  stall: "STALL",
  lmv: "LMV",
  mcwg: "MCWG",
  mcwog: "MCWOG",
  puc: "PUC",
  pucc: "PUCC",
  rc: "RC",
  abs: "ABS",
  cctv: "CCTV",
  otp: "OTP",
  sms: "SMS",
  pdf: "PDF",
  kmph: "KMPH",
  "km/h": "km/h",
  km: "km",
  kms: "kms",
  bac: "BAC",
  mvi: "MVI",
  ts: "TS",
  tg: "TG",
  ap: "AP",
  nh: "NH",
  sh: "SH",
  atm: "ATM",
  ac: "AC",
  "a.c": "A.C",
  "a.c.": "A.C.",
  rfid: "RFID",
  led: "LED",
  digilocker: "DigiLocker",
  mparivahan: "mParivahan",
  hyderabad: "Hyderabad",
  telangana: "Telangana",
  india: "India",
  "no.": "No.",
  i: "I",
  "u-turn": "U-turn",
  "l-mark": "L-mark",
  "h-track": "H-track",
  "'l'": "'L'",
  '"u"': '"U"',
  "u": "U",
  "50cc": "50cc",
  "10m": "10m",
  "5t": "5T",
  "4t": "4T",
  "3.5m": "3.5m",
  "2m": "2m"
};

/**
 * Collapses stray whitespace from PDF extraction without modifying wording or letter case.
 */
export function cleanPdfText(text) {
  if (typeof text !== "string") return "";
  return text.replace(/\s+/g, " ").trim();
}

/**
 * Converts ALL-CAPS English RTO text to clean Sentence case while preserving traffic acronyms.
 */
export function toEasyReadCase(text, lang = "en") {
  const cleaned = cleanPdfText(text);
  if (!cleaned || lang !== "en") return cleaned;

  const letters = cleaned.replace(/[^A-Za-z]/g, "");
  if (letters.length < 3 || letters !== letters.toUpperCase()) {
    return cleaned;
  }

  let lowered = cleaned.toLowerCase();

  // Capitalize first letter of string and after sentence terminators
  lowered = lowered.replace(/(^|[.!?]\s+)([a-z])/g, (_, prefix, ch) => prefix + ch.toUpperCase());

  // Restore domain acronyms, proper nouns, and unit symbols (without swallowing trailing punctuation)
  lowered = lowered.replace(/(^|[\s("'`])([a-z0-9'/-]+(?:\.[a-z0-9]+)*)(?=[\s)"'`,.:;!?]|$)/g, (full, lead, word) => {
    const key = word.toLowerCase();
    const replacement = PRESERVED_TOKENS[key];
    if (replacement) return lead + replacement;
    return full;
  });

  // Ensure initial letter remains uppercase if not overridden
  return lowered.replace(/^([^a-zA-Z]*)([a-z])/, (_, pre, ch) => pre + ch.toUpperCase());
}

export function formatDisplayText(text, lang = "en", easyRead = false) {
  return easyRead ? toEasyReadCase(text, lang) : cleanPdfText(text);
}

const SVG_PATHS = {
  traffic: '<circle cx="12" cy="6" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="18" r="1.5"/><rect x="7" y="2" width="10" height="20" rx="3"/>',
  book: '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
  cards: '<rect x="3" y="5" width="14" height="14" rx="2"/><path d="M7 2h12a2 2 0 0 1 2 2v12"/>',
  compare: '<path d="M8 3H5a2 2 0 0 0-2 2v14c0 1.1.9 2 2 2h3"/><path d="M16 3h3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-3"/><line x1="12" y1="2" x2="12" y2="22"/>',
  bolt: '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
  building: '<rect x="4" y="2" width="16" height="20" rx="2"/><path d="M9 22v-4h6v4"/><path d="M8 6h.01M16 6h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01"/>',
  speak: '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/>',
  arrowLeft: '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
  arrowRight: '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
  printer: '<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
  search: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
  check: '<polyline points="20 6 9 17 4 12"/>',
  x: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  info: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
  external: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>'
};

export function svgIcon(name, size = 18, className = "ui-icon") {
  const paths = SVG_PATHS[name];
  if (!paths) return "";
  return `<svg class="${className}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;
}
