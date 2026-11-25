// js/i18n.js - Trilingual Internationalization Manager (English, Telugu & Hindi)
import { storage } from "./storage-engine.js";

const SUPPORTED_LANGS = ["en", "te", "hi"];
let urlLang = null;
if (typeof window !== "undefined" && window.location) {
  try {
    const paramLang = new URLSearchParams(window.location.search).get("lang");
    if (SUPPORTED_LANGS.includes(paramLang)) {
      urlLang = paramLang;
      storage.setPreference("language", paramLang);
    }
  } catch (e) {
    // Ignore malformed search query
  }
}

let currentLang = urlLang || storage.getPreference("language", "en");
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

export function setLanguage(lang, { updateUrl = true } = {}) {
  if (SUPPORTED_LANGS.includes(lang)) {
    currentLang = lang;
    storage.setPreference("language", lang);
    document.documentElement.lang = lang;
    const select = document.getElementById("select-language");
    if (select && select.value !== lang) {
      select.value = lang;
    }
    updateDomTranslations();
    if (updateUrl && typeof window !== "undefined" && window.history && window.location) {
      try {
        const url = new URL(window.location.href);
        if (lang === "en") {
          url.searchParams.delete("lang");
        } else {
          url.searchParams.set("lang", lang);
        }
        const nextUrl = url.pathname + (url.searchParams.toString() ? `?${url.searchParams.toString()}` : "");
        const currentUrl = window.location.pathname + window.location.search;
        if (nextUrl !== currentUrl) {
          const currentTab = (window.history.state && window.history.state.tab) || undefined;
          window.history.pushState({ tab: currentTab, lang }, "", nextUrl);
        }
      } catch (e) {
        // Ignore history errors in restricted contexts
      }
    }
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
