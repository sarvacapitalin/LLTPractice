// js/theme-engine.js - System-default (prefers-color-scheme) + persistent Light/Dark/System override

export const THEME_STORAGE_KEY = "TS_LLR_THEME";
const VALID_MODES = ["system", "light", "dark"];

const THEME_LABELS = {
  system: { short: "Auto", icon: "◐", title: "Theme: Auto (matches system). Click to switch to Light" },
  light: { short: "Light", icon: "☀", title: "Theme: Light. Click to switch to Dark" },
  dark: { short: "Dark", icon: "☾", title: "Theme: Dark. Click to switch to Auto (System)" }
};

export function getThemePreference() {
  try {
    const saved = localStorage.getItem(THEME_STORAGE_KEY);
    return VALID_MODES.includes(saved) ? saved : "system";
  } catch (e) {
    return "system";
  }
}

export function resolveTheme(pref = getThemePreference()) {
  if (pref === "light" || pref === "dark") return pref;
  if (typeof window !== "undefined" && window.matchMedia) {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  return "light";
}

export function applyTheme(pref = getThemePreference()) {
  const safePref = VALID_MODES.includes(pref) ? pref : "system";
  const resolved = resolveTheme(safePref);

  if (typeof document !== "undefined") {
    const root = document.documentElement;
    root.dataset.theme = resolved;
    root.dataset.themePreference = safePref;
    root.style.colorScheme = resolved;

    const metaTheme = document.querySelector('meta[name="theme-color"]');
    if (metaTheme) {
      metaTheme.setAttribute("content", resolved === "dark" ? "#0B1220" : "#0B2545");
    }

    const btn = document.getElementById("btn-theme-toggle");
    if (btn) {
      const meta = THEME_LABELS[safePref];
      btn.title = meta.title;
      btn.setAttribute("aria-label", meta.title);
      btn.dataset.mode = safePref;
      const iconEl = btn.querySelector(".theme-icon");
      const textEl = btn.querySelector(".theme-label");
      if (iconEl) iconEl.textContent = meta.icon;
      if (textEl) textEl.textContent = meta.short;
    }
  }
  return resolved;
}

export function setThemePreference(pref) {
  const safePref = VALID_MODES.includes(pref) ? pref : "system";
  try {
    localStorage.setItem(THEME_STORAGE_KEY, safePref);
  } catch (e) {
    // Ignore storage errors in private browsing
  }
  return applyTheme(safePref);
}

export function cycleThemePreference() {
  const current = getThemePreference();
  const next = VALID_MODES[(VALID_MODES.indexOf(current) + 1) % VALID_MODES.length];
  return setThemePreference(next);
}

let initialized = false;
export function initTheme() {
  applyTheme(getThemePreference());
  if (initialized) return;
  initialized = true;

  const btn = document.getElementById("btn-theme-toggle");
  if (btn) {
    btn.addEventListener("click", () => {
      cycleThemePreference();
    });
  }

  if (typeof window !== "undefined" && window.matchMedia) {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = () => {
      if (getThemePreference() === "system") {
        applyTheme("system");
      }
    };
    if (mq.addEventListener) {
      mq.addEventListener("change", onChange);
    } else if (mq.addListener) {
      mq.addListener(onChange);
    }
  }
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTheme);
  } else {
    initTheme();
  }
}
