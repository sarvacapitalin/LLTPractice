// js/i18n.js - Trilingual Internationalization Manager (English, Telugu & Hindi)
import { storage } from "./storage-engine.js";

const SUPPORTED_LANGS = ["en", "te", "hi"];
let currentLang = storage.getPreference("language", "en");
if (!SUPPORTED_LANGS.includes(currentLang)) {
  currentLang = "en";
}

let translations = {
  en: {},
  te: {},
  hi: {}
};

export async function initI18n() {
  try {
    const [enRes, teRes, hiRes] = await Promise.all([
      fetch("data/i18n/en.json").then(r => r.json()).catch(() => ({})),
      fetch("data/i18n/te.json").then(r => r.json()).catch(() => ({})),
      fetch("data/i18n/hi.json").then(r => r.json()).catch(() => ({}))
    ]);

    translations.en = enRes;
    translations.te = teRes;
    translations.hi = hiRes;

    document.documentElement.lang = currentLang;
    updateDomTranslations();
  } catch (e) {
    console.warn("Could not load i18n JSON files:", e);
  }
}

export function setLanguage(lang) {
  if (SUPPORTED_LANGS.includes(lang)) {
    currentLang = lang;
    storage.setPreference("language", lang);
    document.documentElement.lang = lang;
    updateDomTranslations();
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: lang }));
  }
}

export function getCurrentLang() {
  return currentLang;
}

export function t(key, fallback = "") {
  const table = translations[currentLang] || translations.en || {};
  return table[key] || fallback || key;
}

export function updateDomTranslations() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    const translated = t(key);
    if (translated) {
      if (el.tagName === "INPUT" && el.placeholder) {
        el.placeholder = translated;
      } else {
        el.textContent = translated;
      }
    }
  });
}
