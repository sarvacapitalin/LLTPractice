// js/i18n.js - Trilingual Internationalization Manager (English active; Telugu & Hindi temporarily disabled)
import { storage } from "./storage-engine.js";

// Force English exclusively while regional language datasets undergo authentic review
let currentLang = "en";
storage.setPreference("language", "en");

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
  } catch (e) {
    console.warn("Could not load i18n JSON files:", e);
  }
}

export function setLanguage(lang) {
  // Telugu and Hindi exams are temporarily disabled pending authentic official translation
  currentLang = "en";
  storage.setPreference("language", "en");
  document.documentElement.lang = "en";
  updateDomTranslations();
  window.dispatchEvent(new CustomEvent("languageChanged", { detail: "en" }));
}

export function getCurrentLang() {
  return "en";
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
