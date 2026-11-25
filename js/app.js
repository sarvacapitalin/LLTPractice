// js/app.js - Main Application Coordinator
import { initI18n, setLanguage, getCurrentLang, t } from "./i18n.js";
import { storage } from "./storage-engine.js";
import { sounds } from "./sound-effects.js";
import { speech } from "./speech-engine.js";
import { coverage } from "./coverage-engine.js";
import { exam } from "./exam-engine.js";
import { practice } from "./practice-engine.js";
import { flashcards } from "./flashcards-engine.js";
import { sync } from "./sync-engine.js";
import { formatDisplayText, cleanPdfText, svgIcon } from "./text-formatter.js";
import { adManager } from "./ad-manager.js";

let allQuestions = [];
let roadSigns = [];
let rulesOfRoad = [];
let generalPrinciples = [];
let trickyTwins = [];
let cheatsheet = null;
let rtoGuide = null;
let popularGuides = null;
let currentRenderedQId = null;
let datasetsLoaded = false;
let toastTimer = null;

function showToast(message) {
  const toast = document.getElementById("app-toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

// Initialize on DOM load
window.addEventListener("DOMContentLoaded", async () => {
  await initI18n();
  setupLanguageSelector();
  setupSoundToggle();
  setupTabs();
  setupModals();
  setupKeyboardHotkeys();

  await loadAllDatasets();

  initExamUI();
  initPracticeUI();
  initFlashcardsUI();
  renderTrickyTwins();
  renderCheatsheet();
  renderRtoGuide();
  updateReadinessMeter();
  applyInitialTabFromUrl();
  checkSyncUrlParam();
  adManager.init();

  // Unregister legacy Service Workers to prevent stale module serving
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistrations().then(regs => {
      regs.forEach(reg => reg.unregister());
    });
  }
  if ("caches" in window) {
    caches.keys().then(keys => {
      keys.forEach(k => caches.delete(k));
    });
  }
});

const ASSET_VER = "v=23";

function withAssetVer(url) {
  if (!url) return url;
  return url.includes("?") ? url : `${url}?${ASSET_VER}`;
}

async function loadAllDatasets() {
  try {
    const v = ASSET_VER;
    const [signsRes, rulesRes, gpRes, twinsRes, cheatRes, guideRes, popularRes] = await Promise.all([
      fetch(`data/questions/telangana/road-signs.json?${v}`).then(r => r.json()).catch(() => []),
      fetch(`data/questions/telangana/rules-of-road.json?${v}`).then(r => r.json()).catch(() => []),
      fetch(`data/questions/telangana/general-principles.json?${v}`).then(r => r.json()).catch(() => []),
      fetch(`data/tricky-twins.json?${v}`).then(r => r.json()).catch(() => []),
      fetch(`data/last-minute-cheatsheet.json?${v}`).then(r => r.json()).catch(() => null),
      fetch(`data/rto-guide.json?${v}`).then(r => r.json()).catch(() => null),
      fetch(`data/popular-guides.json?${v}`).then(r => r.json()).catch(() => null)
    ]);

    roadSigns = signsRes;
    rulesOfRoad = rulesRes;
    generalPrinciples = gpRes;
    allQuestions = [...roadSigns, ...rulesOfRoad, ...generalPrinciples];

    trickyTwins = twinsRes;
    cheatsheet = cheatRes;
    rtoGuide = guideRes;
    popularGuides = popularRes;

    coverage.setQuestions(allQuestions);
    practice.setQuestions(allQuestions);
    flashcards.setSigns(roadSigns);

    practice.notifyUpdate();
    flashcards.notifyUpdate();

    datasetsLoaded = true;
  } catch (e) {
    console.error("Error loading question data:", e);
  }
}

// Language Selector Handler
function setupLanguageSelector() {
  const select = document.getElementById("select-language");
  if (!select) return;
  select.value = getCurrentLang();
  select.addEventListener("change", e => {
    setLanguage(e.target.value);
  });

  window.addEventListener("languageChanged", () => {
    updateReadinessMeter();
    currentRenderedQId = null;
    if (exam.isActive || exam.isFinished) exam.notifyUpdate();
    practice.notifyUpdate();
    flashcards.notifyUpdate();
    renderTrickyTwins();
    renderCheatsheet();
    renderRtoGuide();
  });
}

// Sound Toggle Handler
function setupSoundToggle() {
  const btn = document.getElementById("btn-sound-toggle");
  const icon = document.getElementById("sound-icon");
  let enabled = storage.getPreference("soundEnabled", true);
  sounds.toggle(enabled);
  if (icon) icon.textContent = enabled ? "🔔" : "🔕";

  btn?.addEventListener("click", () => {
    enabled = !enabled;
    storage.setPreference("soundEnabled", enabled);
    sounds.toggle(enabled);
    if (enabled) {
      sounds.ensureAudioActive();
      sounds.playSelect();
    }
    if (icon) icon.textContent = enabled ? "🔔" : "🔕";
  });

  const unlockAudio = () => {
    sounds.ensureAudioActive();
    window.removeEventListener("pointerdown", unlockAudio);
    window.removeEventListener("keydown", unlockAudio);
    window.removeEventListener("touchstart", unlockAudio);
  };
  window.addEventListener("pointerdown", unlockAudio, { passive: true });
  window.addEventListener("keydown", unlockAudio, { passive: true });
  window.addEventListener("touchstart", unlockAudio, { passive: true });
}

const TAB_TO_PARAM = {
  "tab-exam": "exam",
  "tab-practice": "practice",
  "tab-flashcards": "flashcards",
  "tab-twins": "twins",
  "tab-cheatsheet": "cheatsheet",
  "tab-guide": "guide"
};

const PARAM_TO_TAB = {
  exam: "tab-exam",
  practice: "tab-practice",
  flashcards: "tab-flashcards",
  twins: "tab-twins",
  cheatsheet: "tab-cheatsheet",
  guide: "tab-guide",
  "rto-guide": "tab-guide"
};

const TAB_TITLES = {
  "tab-exam": "Telangana RTA Learner's Licence Practice 2026 • Official STALL Mock Test Simulator",
  "tab-practice": "Topic Practice (412 Questions) • Telangana RTA LLR Practice 2026",
  "tab-flashcards": "Road Sign Flashcards (94 Signs) • Telangana RTA LLR Practice 2026",
  "tab-twins": "Tricky Twins Sign Comparisons • Telangana RTA LLR Practice 2026",
  "tab-cheatsheet": "Rapid Cheatsheet & Hand Signals • Telangana RTA LLR Practice 2026",
  "tab-guide": "Hyderabad & Telangana RTO Guide, DL Track & Fines • LLR Practice 2026"
};

function activateTab(targetId, { pushHistory = true } = {}) {
  const tabs = document.querySelectorAll(".nav-tab");
  const targetTabBtn = document.querySelector(`.nav-tab[data-tab="${targetId}"]`);
  if (!targetTabBtn) return;

  if (targetId !== "tab-exam" && exam.isActive && !exam.isFinished) {
    exam.pauseTimer();
    document.body.classList.remove("exam-focus-mode");
  } else if (targetId === "tab-exam" && exam.isActive && !exam.isFinished) {
    exam.resumeTimer();
    document.body.classList.add("exam-focus-mode");
  } else {
    document.body.classList.remove("exam-focus-mode");
  }

  tabs.forEach(tab => {
    tab.classList.remove("active");
    tab.setAttribute("aria-selected", "false");
  });
  targetTabBtn.classList.add("active");
  targetTabBtn.setAttribute("aria-selected", "true");

  document.querySelectorAll(".tab-pane").forEach(pane => {
    pane.classList.remove("active");
  });
  const targetPane = document.getElementById(targetId);
  if (targetPane) targetPane.classList.add("active");

  if (targetId === "tab-practice") {
    practice.notifyUpdate();
  } else if (targetId === "tab-flashcards") {
    flashcards.notifyUpdate();
  } else if (targetId === "tab-twins") {
    renderTrickyTwins();
  } else if (targetId === "tab-cheatsheet") {
    renderCheatsheet();
  } else if (targetId === "tab-guide") {
    renderRtoGuide();
  }

  if (TAB_TITLES[targetId]) {
    document.title = TAB_TITLES[targetId];
  }

  if (pushHistory && typeof window !== "undefined" && window.history && window.location) {
    try {
      const url = new URL(window.location.href);
      const paramVal = TAB_TO_PARAM[targetId];
      if (!paramVal || paramVal === "exam") {
        url.searchParams.delete("tab");
      } else {
        url.searchParams.set("tab", paramVal);
      }
      url.hash = "";
      const nextUrl = url.pathname + (url.searchParams.toString() ? `?${url.searchParams.toString()}` : "");
      const currentUrl = window.location.pathname + window.location.search + window.location.hash;
      if (nextUrl !== currentUrl) {
        window.history.pushState({ tab: targetId, lang: getCurrentLang() }, "", nextUrl);
      }
    } catch (e) {
      // Ignore restricted history context
    }
  }

  speech.stop();
  adManager.refreshVisibleSlots();
}

// Navigation Tabs
function setupTabs() {
  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-tab");
      activateTab(targetId, { pushHistory: true });
    });
  });

  window.addEventListener("popstate", event => {
    try {
      const params = new URLSearchParams(window.location.search);
      const stateLang = event.state && event.state.lang;
      const urlLang = params.get("lang") || stateLang;
      if (urlLang && ["en", "te", "hi"].includes(urlLang) && urlLang !== getCurrentLang()) {
        setLanguage(urlLang, { updateUrl: false });
      }
      const rawTab = (params.get("tab") || window.location.hash.replace("#", "") || "exam").toLowerCase();
      const targetId = PARAM_TO_TAB[rawTab] || "tab-exam";
      activateTab(targetId, { pushHistory: false });
    } catch (e) {
      // Ignore malformed URL on popstate
    }
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      if (exam.isActive && !exam.isFinished) {
        exam.pauseTimer();
      }
    } else {
      const examTab = document.getElementById("tab-exam");
      if (examTab && examTab.classList.contains("active") && exam.isActive && !exam.isFinished) {
        exam.resumeTimer();
      }
    }
  });

  document.getElementById("btn-readiness-badge")?.addEventListener("click", () => {
    activateTab("tab-practice", { pushHistory: true });
  });

  document.getElementById("btn-jump-practice-unseen")?.addEventListener("click", () => {
    const stats = coverage.getReadinessStats();
    const targetFilter = stats.unseen > 0 ? "unseen" : (stats.probation > 0 ? "probation" : "all");
    const statusFilter = document.getElementById("practice-status-filter");
    if (statusFilter) statusFilter.value = targetFilter;
    practice.setFilter(targetFilter);
    activateTab("tab-practice", { pushHistory: true });
  });
}

// Readiness Meter & Category Mastery Dashboard Update
function updateReadinessMeter() {
  const stats = coverage.getReadinessStats();
  const badge = document.getElementById("btn-readiness-badge");
  const badgeVal = document.getElementById("header-readiness-val");
  const fill = document.getElementById("header-readiness-fill");

  if (badge) {
    badge.title = `Exam Readiness: ${stats.readinessPercent}% (${stats.mastered}/${stats.total} Mastered) • Click to open Topic Practice`;
  }
  if (badgeVal) badgeVal.textContent = `${stats.readinessPercent}%`;
  if (fill) {
    fill.style.width = `${Math.min(stats.readinessPercent, 100)}%`;
    fill.style.background = stats.isExamReady ? "#22C55E" : "#FFD54F";
  }

  // Update Home Intro Category Mastery Panel
  const introVal = document.getElementById("intro-readiness-val");
  const introCount = document.getElementById("intro-mastered-count");
  const introBadge = document.getElementById("intro-readiness-badge");
  if (introVal) introVal.textContent = `${stats.readinessPercent}%`;
  if (introCount) {
    introCount.textContent = `${stats.mastered} / ${stats.total} ${t("mastered_word", "mastered")}`;
  }
  if (introBadge) {
    introBadge.classList.toggle("ready", stats.isExamReady);
    introBadge.textContent = stats.isExamReady
      ? t("readiness_ready", "EXAM READY (95%+)")
      : t("readiness_goal_tag", "Goal: 391 Qs");
  }

  const updateCatRow = (catKey, countElId, barElId) => {
    const cat = stats.categoryStats[catKey];
    if (!cat) return;
    const countEl = document.getElementById(countElId);
    const barEl = document.getElementById(barElId);
    const pct = cat.total > 0 ? Math.round((cat.mastered / cat.total) * 100) : 0;
    if (countEl) countEl.textContent = `${cat.mastered} / ${cat.total}`;
    if (barEl) barEl.style.width = `${pct}%`;
  };

  updateCatRow("road_signs", "mastery-signs-count", "mastery-signs-bar");
  updateCatRow("rules_of_road", "mastery-rules-count", "mastery-rules-bar");
  updateCatRow("general_principles", "mastery-principles-count", "mastery-principles-bar");
}

function applyInitialTabFromUrl() {
  try {
    if (typeof window === "undefined" || !window.location) return;
    const url = new URL(window.location.href);
    const rawTab = (url.searchParams.get("tab") || url.hash.replace("#", "") || "").toLowerCase();
    const targetId = PARAM_TO_TAB[rawTab];
    if (targetId) {
      activateTab(targetId, { pushHistory: false });
      if (url.hash && !url.searchParams.get("tab")) {
        const paramVal = TAB_TO_PARAM[targetId];
        if (paramVal && paramVal !== "exam") {
          url.searchParams.set("tab", paramVal);
        }
        url.hash = "";
      }
    }
    if (window.history && window.history.replaceState) {
      const normalizedUrl = url.pathname + (url.searchParams.toString() ? `?${url.searchParams.toString()}` : "") + url.hash;
      window.history.replaceState(
        { tab: targetId || "tab-exam", lang: getCurrentLang() },
        document.title,
        normalizedUrl
      );
    }
  } catch (e) {
    // Ignore invalid URL tab param
  }
}

function checkSyncUrlParam() {
  try {
    if (typeof window === "undefined" || !window.location) return;
    const url = new URL(window.location.href);
    const syncParam = url.searchParams.get("sync");
    if (syncParam) {
      let rawJson = syncParam;
      try {
        if (syncParam.startsWith("%") || syncParam.includes("%22") || syncParam.includes("%7B")) {
          rawJson = decodeURIComponent(syncParam);
        }
      } catch (e) {
        rawJson = syncParam;
      }
      const ok = sync.applyCompactPayload(rawJson);
      if (ok) {
        updateReadinessMeter();
        practice.notifyUpdate();
        flashcards.notifyUpdate();
        showToast(t("sync_success", "Progress synchronized successfully!"));
        url.searchParams.delete("sync");
        const cleanUrl = url.pathname + (url.searchParams.toString() ? `?${url.searchParams.toString()}` : "");
        const activeTab = (window.history.state && window.history.state.tab) || PARAM_TO_TAB[url.searchParams.get("tab")] || "tab-exam";
        window.history.replaceState({ tab: activeTab, lang: getCurrentLang() }, document.title, cleanUrl);
      }
    }
  } catch (err) {
    console.error("Failed to process sync query parameter:", err);
  }
}

// Modals Setup (Sync, Reset)
function setupModals() {
  const syncModal = document.getElementById("modal-sync");
  const resetModal = document.getElementById("modal-reset");

  document.getElementById("btn-sync-modal")?.addEventListener("click", () => {
    const qrContainer = document.getElementById("sync-qr-container");
    if (qrContainer) qrContainer.innerHTML = sync.generateSyncQrSvg();
    if (syncModal) syncModal.style.display = "flex";
  });

  document.getElementById("btn-close-sync")?.addEventListener("click", () => {
    if (syncModal) syncModal.style.display = "none";
  });

  document.getElementById("btn-export-backup")?.addEventListener("click", () => {
    sync.exportFile();
  });

  document.getElementById("input-sync-file")?.addEventListener("change", async e => {
    const file = e.target.files[0];
    if (file) {
      try {
        await sync.importFile(file);
        if (syncModal) syncModal.style.display = "none";
        updateReadinessMeter();
        practice.notifyUpdate();
        flashcards.notifyUpdate();
        showToast(t("sync_success", "Progress synchronized successfully!"));
      } catch (err) {
        showToast("Error importing backup file: " + err.message);
      } finally {
        e.target.value = "";
      }
    }
  });

  document.getElementById("btn-reset-readiness-mini")?.addEventListener("click", () => {
    if (resetModal) resetModal.style.display = "flex";
  });

  document.getElementById("btn-cancel-reset")?.addEventListener("click", () => {
    if (resetModal) resetModal.style.display = "none";
  });

  document.getElementById("btn-confirm-reset")?.addEventListener("click", () => {
    storage.resetReadiness();
    if (practice.lastAnswers) practice.lastAnswers = {};
    if (resetModal) resetModal.style.display = "none";
    updateReadinessMeter();
    practice.notifyUpdate();
    flashcards.notifyUpdate();
    showToast(t("reset_done_toast", "Practice progress reset to 0%."));
  });

  [syncModal, resetModal].forEach(modal => {
    modal?.addEventListener("click", e => {
      if (e.target === modal) modal.style.display = "none";
    });
  });

  window.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      if (syncModal && syncModal.style.display !== "none") syncModal.style.display = "none";
      if (resetModal && resetModal.style.display !== "none") resetModal.style.display = "none";
    }
  });
}

// Keyboard shortcuts (Exam 1-4 / Enter / Space; Flashcards Left / Right / Space)
function setupKeyboardHotkeys() {
  window.addEventListener("keydown", e => {
    const activeEl = document.activeElement || e.target;
    const isTyping =
      (activeEl && (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA" || activeEl.tagName === "SELECT" || activeEl.isContentEditable)) ||
      (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT" || e.target.isContentEditable));

    if (isTyping) return;

    const examTab = document.getElementById("tab-exam");
    const isExamTabActive = examTab && examTab.classList.contains("active");

    if (isExamTabActive && exam.isActive && !exam.isFinished) {
      if (["1", "2", "3", "4"].includes(e.key)) {
        exam.selectOption(parseInt(e.key, 10) - 1);
      } else if (e.key === "Enter") {
        if (exam.isRevealed) {
          currentRenderedQId = null;
          exam.continueToNext();
          return;
        }
        const guessBox = document.getElementById("exam-guess-checkbox");
        const isGuessed = guessBox ? guessBox.checked : false;
        if (guessBox) guessBox.checked = false;
        exam.confirmAndSubmit(isGuessed);
      } else if (e.key === " " || e.key === "Spacebar") {
        e.preventDefault();
        exam.readCurrentQuestion();
      }
      return;
    }

    const fcTab = document.getElementById("tab-flashcards");
    if (fcTab && fcTab.classList.contains("active")) {
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        flashcards.prevCard();
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        flashcards.nextCard();
      } else if ((e.key === " " || e.key === "Spacebar") && activeEl?.tagName !== "BUTTON") {
        e.preventDefault();
        flashcards.flipCard();
      }
    }
  });
}

// ==========================================
// 1. STALL MOCK EXAM UI
// ==========================================
function initExamUI() {
  const introCard = document.getElementById("exam-intro-card");
  const activeCard = document.getElementById("exam-active-card");
  const resultCard = document.getElementById("exam-result-card");
  const btnStart = document.getElementById("btn-start-exam-main");
  const btnRetake = document.getElementById("btn-retake-exam");
  const btnExit = document.getElementById("btn-exit-exam");
  const btnConfirm = document.getElementById("btn-confirm-next");
  const btnRead = document.getElementById("btn-read-question");
  const guessCheckbox = document.getElementById("exam-guess-checkbox");
  const optionsContainer = document.getElementById("exam-options-container");
  const tutorToggle = document.getElementById("exam-toggle-tutor-mode");
  const tutorLabel = document.getElementById("tutor-mode-status-label");
  const expBox = document.getElementById("exam-explanation-box");

  // Initialize Tutor Mode preference (Default: OFF)
  const initialTutor = storage.getPreference("tutorMode", false);
  if (tutorToggle) tutorToggle.checked = initialTutor;
  if (tutorLabel) {
    tutorLabel.textContent = initialTutor ? "ON" : "OFF";
    tutorLabel.classList.toggle("on", initialTutor);
  }
  exam.setTutorMode(initialTutor);

  tutorToggle?.addEventListener("change", e => {
    const on = e.target.checked;
    exam.setTutorMode(on);
    storage.setPreference("tutorMode", on);
    if (tutorLabel) {
      tutorLabel.textContent = on ? "ON" : "OFF";
      tutorLabel.classList.toggle("on", on);
    }
  });

  document.getElementById("tutor-toggle-wrapper")?.addEventListener("click", e => {
    if (!e.target.closest("label") && tutorToggle) {
      tutorToggle.checked = !tutorToggle.checked;
      tutorToggle.dispatchEvent(new Event("change"));
    }
  });

  btnStart?.addEventListener("click", () => {
    sounds.ensureAudioActive();
    if (!datasetsLoaded || allQuestions.length === 0) {
      showToast("Questions are still loading. Please wait a moment.");
      return;
    }
    if (guessCheckbox) guessCheckbox.checked = false;
    currentRenderedQId = null;
    exam.startNewExam();
  });

  btnRetake?.addEventListener("click", () => {
    sounds.ensureAudioActive();
    if (guessCheckbox) guessCheckbox.checked = false;
    currentRenderedQId = null;
    exam.startNewExam();
  });

  // Safe two-tap inline confirmation if user has already answered questions
  let exitConfirmTimer = null;
  btnExit?.addEventListener("click", () => {
    if (exam.history.length > 0 && btnExit.dataset.confirming !== "true") {
      btnExit.dataset.confirming = "true";
      btnExit.textContent = t("btn_confirm_exit", "Confirm Exit?");
      clearTimeout(exitConfirmTimer);
      exitConfirmTimer = setTimeout(() => {
        btnExit.dataset.confirming = "false";
        btnExit.innerHTML = `<span data-i18n="btn_exit_exam">${t("btn_exit_exam", "Exit")}</span>`;
      }, 3500);
      return;
    }
    clearTimeout(exitConfirmTimer);
    btnExit.dataset.confirming = "false";
    btnExit.innerHTML = `<span data-i18n="btn_exit_exam">${t("btn_exit_exam", "Exit")}</span>`;
    currentRenderedQId = null;
    exam.abortExam();
  });

  btnConfirm?.addEventListener("click", () => {
    if (exam.isRevealed) {
      currentRenderedQId = null;
      exam.continueToNext();
      return;
    }
    const isGuessed = guessCheckbox ? guessCheckbox.checked : false;
    currentRenderedQId = null;
    exam.confirmAndSubmit(isGuessed);
    if (guessCheckbox) guessCheckbox.checked = false;
  });

  btnRead?.addEventListener("click", () => {
    exam.readCurrentQuestion();
  });

  optionsContainer?.addEventListener("click", e => {
    if (exam.isRevealed) return;
    const card = e.target.closest(".option-card");
    if (card) {
      const idx = parseInt(card.getAttribute("data-option-index"), 10);
      if (!isNaN(idx)) exam.selectOption(idx);
    }
  });

  speech.onStateChange = isReading => {
    [btnRead, document.getElementById("btn-practice-read"), document.getElementById("btn-fc-read")].forEach(el => {
      if (el) el.classList.toggle("reading", isReading);
    });
  };

  exam.onStateUpdate = state => {
    updateReadinessMeter();

    if (!state.isActive && !state.isFinished) {
      document.body.classList.remove("exam-focus-mode");
      if (introCard) introCard.style.display = "block";
      if (activeCard) activeCard.style.display = "none";
      if (resultCard) resultCard.style.display = "none";
      currentRenderedQId = null;
      adManager.refreshVisibleSlots();
      return;
    }

    if (state.isFinished) {
      document.body.classList.remove("exam-focus-mode");
      currentRenderedQId = null;
      if (introCard) introCard.style.display = "none";
      if (activeCard) activeCard.style.display = "none";
      if (resultCard) resultCard.style.display = "block";

      const badge = document.getElementById("result-badge");
      const title = document.getElementById("result-heading");
      const scoreText = document.getElementById("result-score-text");
      const desc = document.getElementById("result-explanation");
      const waBtn = document.getElementById("btn-share-whatsapp");

      const totalQs = state.totalQuestions || 20;
      const attempted = state.history && state.history.length ? state.history.length : totalQs;
      const percent = Math.round((state.correctCount / attempted) * 100);
      const passMark = state.passThreshold || (state.isCustom ? Math.max(1, Math.ceil(totalQs * 0.6)) : 12);

      if (scoreText) {
        if (state.passed && attempted < totalQs) {
          scoreText.textContent = `Score: ${state.correctCount} / ${attempted} (${percent}%) • Early Pass: ${passMark} of ${totalQs} criteria met!`;
        } else if (!state.passed && attempted < totalQs) {
          scoreText.textContent = `Score: ${state.correctCount} / ${attempted} (${percent}%) • Pass Mark: ${passMark} (Attempted: ${attempted}/${totalQs})`;
        } else {
          scoreText.textContent = `Score: ${state.correctCount} / ${totalQs} (${percent}%) • Pass Mark: ${passMark}`;
        }
      }

      if (state.passed) {
        if (badge) { badge.className = "result-badge-big pass"; badge.textContent = "✓"; }
        if (title) { title.className = "result-title pass"; title.textContent = t("result_pass", "CONGRATULATIONS! YOU PASSED"); }
        if (desc) {
          desc.textContent = state.isCustom
            ? `You passed the retry session with ${state.correctCount} out of ${totalQs} correct!`
            : t("result_pass_desc", "You reached the passing mark of 12 correct! You are well prepared for the real RTA exam.");
        }
      } else {
        if (badge) { badge.className = "result-badge-big fail"; badge.textContent = "✗"; }
        if (title) { title.className = "result-title fail"; title.textContent = t("result_fail", "TEST NOT CLEARED"); }
        if (desc) {
          desc.textContent = state.isCustom
            ? `You need at least ${passMark} correct out of ${totalQs} to clear this retry session.`
            : t("result_fail_desc", "You need at least 12 correct answers to pass. Review your missed questions below or in Topic Practice.");
        }
      }

      if (waBtn) {
        const waMsg = encodeURIComponent(`I scored ${state.correctCount}/${attempted} on the Telangana RTA LLR STALL mock exam! Practice here: ${window.location.href}`);
        waBtn.href = `https://api.whatsapp.com/send?text=${waMsg}`;
      }

      renderExamResultReview(state, getCurrentLang(), exam);
      adManager.refreshVisibleSlots();
      return;
    }

    // Active Question Screen (Ad-Free Focus Mode)
    document.body.classList.add("exam-focus-mode");
    if (introCard) introCard.style.display = "none";
    if (activeCard) activeCard.style.display = "block";
    if (resultCard) resultCard.style.display = "none";

    const q = state.currentQuestion;
    if (!q) {
      const qTextEl = document.getElementById("exam-q-text");
      if (qTextEl) qTextEl.textContent = "Questions not loaded. Please refresh the page.";
      return;
    }

    const lang = getCurrentLang();
    const timerDisplay = document.getElementById("timer-seconds-display");
    const timerCircle = document.getElementById("timer-progress-circle");

    if (timerDisplay) timerDisplay.textContent = state.timeLeft;
    if (timerCircle) {
      const totalCircumference = 144.5;
      const fraction = state.timeLeft / 30;
      timerCircle.style.strokeDashoffset = totalCircumference * (1 - fraction);
      if (state.timeLeft <= 5) timerCircle.setAttribute("class", "timer-circle-progress red");
      else if (state.timeLeft <= 15) timerCircle.setAttribute("class", "timer-circle-progress amber");
      else timerCircle.setAttribute("class", "timer-circle-progress");
    }

    // Live tally & progress strip
    const liveTally = document.getElementById("exam-live-tally");
    const progressFill = document.getElementById("exam-progress-fill");
    if (liveTally) {
      liveTally.textContent = `Correct: ${state.correctCount} • Wrong: ${state.wrongCount} • Pass Mark: ${state.passThreshold}`;
    }
    if (progressFill && state.totalQuestions > 0) {
      const pct = Math.min(100, Math.round(((state.currentIndex + 1) / state.totalQuestions) * 100));
      progressFill.style.width = `${pct}%`;
    }

    const isNewQuestion = currentRenderedQId !== q.id;
    if (isNewQuestion) {
      const guessBox = document.getElementById("exam-guess-checkbox");
      if (guessBox) guessBox.checked = false;

      const qBadge = document.getElementById("exam-q-badge");
      const qText = document.getElementById("exam-q-text");
      const visualBox = document.getElementById("exam-q-visual");
      const qImg = document.getElementById("exam-q-img");
      const countSigns = document.getElementById("count-signs");
      const countRules = document.getElementById("count-rules");
      const countPrinciples = document.getElementById("count-principles");
      const freshOptionsContainer = document.getElementById("exam-options-container");

      if (qBadge) qBadge.textContent = `Question ${state.currentIndex + 1} of ${state.totalQuestions}`;

      let sSeen = 0, rSeen = 0, pSeen = 0;
      for (let i = 0; i <= state.currentIndex; i++) {
        const item = exam.questions[i];
        if (!item) continue;
        if (item.category === "road_signs") sSeen++;
        else if (item.category === "rules_of_road") rSeen++;
        else if (item.category === "general_principles") pSeen++;
      }
      let sTotal = 0, rTotal = 0, pTotal = 0;
      exam.questions.forEach(item => {
        if (item.category === "road_signs") sTotal++;
        else if (item.category === "rules_of_road") rTotal++;
        else if (item.category === "general_principles") pTotal++;
      });
      if (countSigns) countSigns.textContent = `${Math.min(sSeen, sTotal)}/${sTotal}`;
      if (countRules) countRules.textContent = `${Math.min(rSeen, rTotal)}/${rTotal}`;
      if (countPrinciples) countPrinciples.textContent = `${Math.min(pSeen, pTotal)}/${pTotal}`;

      // Keep official RTO uppercase in STALL simulator; collapse stray double spaces
      if (qText) qText.textContent = cleanPdfText((q.text && q.text[lang]) || (q.text && q.text.en) || "");

      if (q.image) {
        if (qImg) qImg.src = withAssetVer(q.image);
        if (visualBox) visualBox.style.display = "flex";
      } else if (visualBox) {
        visualBox.style.display = "none";
      }

      let opts = [];
      if (q && q.options) {
        if (Array.isArray(q.options)) opts = q.options;
        else if (typeof q.options === "object") opts = q.options[lang] || q.options.en || q.options.te || q.options.hi || [];
      }

      if (freshOptionsContainer) {
        if (!opts || opts.length === 0) {
          freshOptionsContainer.innerHTML = `<div style="color: #EF4444; padding: 12px; font-weight: 700;">No options available for this question.</div>`;
        } else {
          let html = "";
          opts.forEach((optText, idx) => {
            const isSelected = state.selectedOption === idx;
            const formattedOpt = cleanPdfText(optText);
            html += `<button type="button" class="option-card ${isSelected ? "selected" : ""}" data-option-index="${idx}"><span class="option-badge">${idx + 1}</span><span class="option-text">${formattedOpt}</span></button>`;
          });
          freshOptionsContainer.innerHTML = html;
        }
        currentRenderedQId = q.id;
      }
    } else {
      const freshOptionsContainer = document.getElementById("exam-options-container");
      if (freshOptionsContainer) {
        const cards = freshOptionsContainer.querySelectorAll(".option-card");
        if (cards.length === 0) {
          currentRenderedQId = null;
        } else {
          cards.forEach(card => {
            const idx = parseInt(card.getAttribute("data-option-index"), 10);
            card.classList.toggle("selected", idx === state.selectedOption);
          });
        }
      }
    }

    if (state.isRevealed) {
      const optContainer = document.getElementById("exam-options-container");
      if (optContainer) {
        optContainer.querySelectorAll(".option-card").forEach(card => {
          const idx = parseInt(card.getAttribute("data-option-index"), 10);
          card.classList.remove("selected", "correct", "incorrect", "dimmed");
          if (idx === q.answerIndex) card.classList.add("correct");
          else if (idx === state.selectedOption) card.classList.add("incorrect");
          else card.classList.add("dimmed");
        });
      }

      if (expBox) {
        const isCorrect = state.selectedOption === q.answerIndex;
        expBox.className = "exam-explanation-box " + (isCorrect ? "correct" : "wrong");
        const expText = (q.explanation && (q.explanation[lang] || q.explanation.en)) || "Follow official Telangana RTA rules and guidelines.";
        expBox.innerHTML = `
          <div class="exam-explanation-title">
            <span>${isCorrect ? "✓ Correct Answer!" : `✗ Incorrect! Official Correct Answer: Option ${q.answerIndex + 1}`}</span>
          </div>
          <div class="exam-explanation-text">${expText}</div>
        `;
        expBox.style.display = "block";
      }

      if (btnConfirm) {
        btnConfirm.disabled = false;
        btnConfirm.innerHTML = `<span>CONTINUE</span> ➔`;
        btnConfirm.style.background = "var(--secondary-blue)";
      }
    } else {
      if (expBox) expBox.style.display = "none";
      if (btnConfirm) {
        btnConfirm.disabled = state.selectedOption === null;
        btnConfirm.innerHTML = `<span data-i18n="btn_confirm_next">${t("btn_confirm_next", "CONFIRM & NEXT")}</span> ➔`;
        btnConfirm.style.background = "";
      }
    }
  };
}

// Render Post-Exam Detailed Question Breakdown on Results Card
function renderExamResultReview(state, lang, examEngine) {
  const catBreakdown = document.getElementById("result-category-breakdown");
  const reviewList = document.getElementById("exam-review-list");
  const btnRetakeMissed = document.getElementById("btn-retake-missed");
  const countMissedBtn = document.getElementById("count-missed-btn");
  const countAll = document.getElementById("count-review-all");
  const countWrong = document.getElementById("count-review-wrong");
  const countCorrect = document.getElementById("count-review-correct");

  if (!reviewList) return;

  const history = state.history || [];
  const missedItems = history.filter(h => !h.isCorrect);
  const correctItems = history.filter(h => h.isCorrect);

  if (countAll) countAll.textContent = history.length;
  if (countWrong) countWrong.textContent = missedItems.length;
  if (countCorrect) countCorrect.textContent = correctItems.length;

  if (catBreakdown) {
    let signsC = 0, signsT = 0, rulesC = 0, rulesT = 0, gpC = 0, gpT = 0;
    history.forEach(h => {
      const cat = h.question.category;
      if (cat === "road_signs") { signsT++; if (h.isCorrect) signsC++; }
      else if (cat === "rules_of_road") { rulesT++; if (h.isCorrect) rulesC++; }
      else if (cat === "general_principles") { gpT++; if (h.isCorrect) gpC++; }
    });

    catBreakdown.innerHTML = `
      <span style="background: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 6px; border: 1px solid #FDE68A;">
        Signs: ${signsC}/${signsT} (${signsT > 0 ? Math.round((signsC / signsT) * 100) : 0}%)
      </span>
      <span style="background: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 6px; border: 1px solid #FECACA;">
        Rules: ${rulesC}/${rulesT} (${rulesT > 0 ? Math.round((rulesC / rulesT) * 100) : 0}%)
      </span>
      <span style="background: #EFF6FF; color: #1E40AF; padding: 4px 10px; border-radius: 6px; border: 1px solid #BFDBFE;">
        Principles: ${gpC}/${gpT} (${gpT > 0 ? Math.round((gpC / gpT) * 100) : 0}%)
      </span>
    `;
  }

  if (btnRetakeMissed) {
    if (missedItems.length > 0) {
      btnRetakeMissed.style.display = "inline-flex";
      if (countMissedBtn) countMissedBtn.textContent = missedItems.length;
      btnRetakeMissed.onclick = () => {
        const missedQuestions = missedItems.map(h => h.question);
        const guessBox = document.getElementById("exam-guess-checkbox");
        if (guessBox) guessBox.checked = false;
        currentRenderedQId = null;
        examEngine.startCustomExam(missedQuestions);
      };
    } else {
      btnRetakeMissed.style.display = "none";
    }
  }

  function buildCards(filter = "all") {
    let itemsToRender = history;
    if (filter === "wrong") itemsToRender = missedItems;
    if (filter === "correct") itemsToRender = correctItems;

    if (itemsToRender.length === 0) {
      reviewList.innerHTML = `<div style="text-align: center; color: var(--text-secondary); padding: 24px; font-weight: 600;">No questions match this filter.</div>`;
      return;
    }

    let html = "";
    itemsToRender.forEach((h, idx) => {
      const q = h.question;
      const isCorrect = h.isCorrect;
      const userChoice = h.selected;
      const correctIdx = q.answerIndex;
      const qText = cleanPdfText((q.text && q.text[lang]) || (q.text && q.text.en) || "");
      const qExp = (q.explanation && (q.explanation[lang] || q.explanation.en)) || "Follow standard official Telangana RTA rules.";

      let opts = [];
      if (q.options) {
        if (Array.isArray(q.options)) opts = q.options;
        else if (typeof q.options === "object") opts = q.options[lang] || q.options.en || [];
      }

      let categoryName = "Traffic Sign";
      if (q.category === "rules_of_road") categoryName = "Rule of the Road";
      else if (q.category === "general_principles") categoryName = "Driving Principle";

      html += `
        <div class="review-card ${isCorrect ? "correct" : "wrong"}" data-review-status="${isCorrect ? "correct" : "wrong"}">
          <div class="review-card-top">
            <span class="review-q-num">Q${idx + 1} • ${categoryName} (${q.id})</span>
            <span class="review-q-status ${isCorrect ? "correct" : "wrong"}">
              ${isCorrect ? "✓ Correct" : h.timeout ? "⏰ Timed Out" : "✗ Incorrect"}
              ${h.isGuessed ? " • Guessed" : ""}
            </span>
          </div>
          <h4 class="review-q-title">${qText}</h4>
          ${q.image ? `<div class="review-q-img-wrap"><img src="${withAssetVer(q.image)}" class="review-q-img" alt="Traffic Sign"></div>` : ""}
          <div class="review-options-grid">
            ${opts.map((optText, optIdx) => {
              let optClass = "";
              let suffixTag = "";
              if (optIdx === correctIdx) {
                optClass = "official-correct";
                suffixTag = `<span style="margin-left: auto; font-size: 0.78rem; color: #166534; font-weight: 700;">${isCorrect ? "✓ Your Choice (Correct)" : "✓ Correct Answer"}</span>`;
              } else if (optIdx === userChoice && !isCorrect) {
                optClass = "user-chosen-wrong";
                suffixTag = `<span style="margin-left: auto; font-size: 0.78rem; color: #991B1B; font-weight: 700;">✗ Your Choice</span>`;
              }
              return `
                <div class="review-opt ${optClass}">
                  <div class="review-opt-badge">${optIdx + 1}</div>
                  <div>${cleanPdfText(optText)}</div>
                  ${suffixTag}
                </div>
              `;
            }).join("")}
          </div>
          <div class="review-explanation">
            <strong>Official Rule:</strong> ${qExp}
          </div>
        </div>
      `;
    });

    reviewList.innerHTML = html;
  }

  document.querySelectorAll(".review-filter-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-review-filter") === "all");
  });

  buildCards("all");

  document.querySelectorAll(".review-filter-btn").forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll(".review-filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      buildCards(btn.getAttribute("data-review-filter"));
    };
  });
}

// ==========================================
// 2. TOPIC PRACTICE UI
// ==========================================
function initPracticeUI() {
  const searchInput = document.getElementById("practice-search-input");
  const clearBtn = document.getElementById("btn-practice-search-clear");
  const statusFilter = document.getElementById("practice-status-filter");
  const caseToggleBtn = document.getElementById("btn-practice-case-toggle");

  const updateCaseBtn = () => {
    const isEasy = storage.getPreference("easyReadPractice", false);
    if (caseToggleBtn) {
      caseToggleBtn.classList.toggle("active", isEasy);
      caseToggleBtn.style.background = isEasy ? "#EFF6FF" : "";
      caseToggleBtn.style.borderColor = isEasy ? "#2563EB" : "";
      caseToggleBtn.style.color = isEasy ? "#134074" : "";
      caseToggleBtn.innerHTML = isEasy
        ? `<span>${t("btn_official_caps", "AA Official Caps")}</span>`
        : `<span>${t("btn_easy_read", "Aa Easy-Read")}</span>`;
    }
  };
  updateCaseBtn();

  caseToggleBtn?.addEventListener("click", () => {
    const nextVal = !storage.getPreference("easyReadPractice", false);
    storage.setPreference("easyReadPractice", nextVal);
    updateCaseBtn();
    renderPracticeCard(practice.selectedQuestion);
  });

  document.querySelectorAll("[data-practice-cat]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-practice-cat]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      practice.setCategory(btn.getAttribute("data-practice-cat"));
    });
  });

  statusFilter?.addEventListener("change", e => {
    practice.setFilter(e.target.value);
  });

  const syncClearButton = () => {
    if (clearBtn && searchInput) {
      clearBtn.classList.toggle("visible", searchInput.value.trim().length > 0);
    }
  };

  searchInput?.addEventListener("input", e => {
    syncClearButton();
    practice.setSearch(e.target.value);
  });

  clearBtn?.addEventListener("click", () => {
    if (searchInput) {
      searchInput.value = "";
      syncClearButton();
      practice.setSearch("");
      searchInput.focus();
    }
  });

  practice.onStateChange = state => {
    updateReadinessMeter();
    const matchBadge = document.getElementById("practice-match-count");
    if (matchBadge) {
      matchBadge.textContent = `${state.filteredQuestions.length} / ${allQuestions.length || 412}`;
    }
    renderPracticeMatrix(state.filteredQuestions);
    if (state.reason !== "answer") {
      renderPracticeCard(state.selectedQuestion);
    }
  };

  practice.notifyUpdate();
}

function renderPracticeMatrix(filteredList) {
  const matrix = document.getElementById("practice-matrix");
  if (!matrix) return;
  matrix.innerHTML = "";

  const isAllCategories = practice.activeCategory === "all";

  filteredList.forEach(q => {
    const qState = storage.getQuestionState(q.id);
    const chip = document.createElement("button");
    chip.type = "button";
    const catPrefix = q.category === "road_signs" ? "RS" : q.category === "rules_of_road" ? "RR" : "GP";
    chip.textContent = isAllCategories ? `${catPrefix}-${q.questionNumber}` : q.questionNumber;
    chip.title = `${catPrefix}-${q.questionNumber}: ${q.id} (Status: ${qState.status}, Streak: ${qState.streak})`;
    chip.className = "matrix-chip";

    let bg = "#E2E8F0";
    let color = "#1E293B";
    if (qState.status === "mastered") {
      bg = "#DCFCE7";
      color = "#166534";
    } else if (qState.status === "probation") {
      bg = "#FEF3C7";
      color = "#92400E";
    }

    if (practice.selectedQuestion && practice.selectedQuestion.id === q.id) {
      chip.classList.add("is-selected");
    }

    chip.style.background = bg;
    chip.style.color = color;

    chip.addEventListener("click", () => {
      practice.selectQuestion(q.id);
    });

    matrix.appendChild(chip);
  });
}

function renderPracticeCard(q) {
  const container = document.getElementById("practice-active-q-view");
  if (!container) return;

  if (!q) {
    container.innerHTML = `
      <div style="text-align: center; padding: 36px 16px; color: var(--text-secondary);">
        <div style="font-size: 2rem; margin-bottom: 8px;" aria-hidden="true">${svgIcon("search", 34)}</div>
        <strong style="display: block; font-size: 1.05rem; color: var(--primary-navy); margin-bottom: 6px;">No matching questions found</strong>
        <p style="font-size: 0.88rem; margin: 0 auto; max-width: 42ch; color: var(--text-muted);">Try clearing your search keyword or switching status/category filters.</p>
      </div>
    `;
    return;
  }

  const lang = getCurrentLang();
  const easyRead = storage.getPreference("easyReadPractice", false);
  const qState = storage.getQuestionState(q.id);
  const lastAns = (practice.lastAnswers && practice.lastAnswers[q.id]) || null;
  const isAnswered = lastAns !== null;
  const { index: posIndex, total: posTotal } = practice.getSelectedPosition();

  let statusBadge = `<span style="background: #F1F5F9; color: #475569; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 700;">UNSEEN</span>`;
  if (qState.status === "mastered") {
    statusBadge = `<span style="background: #DCFCE7; color: #166534; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 700;">MASTERED (Streak: ${qState.streak})</span>`;
  } else if (qState.status === "probation") {
    statusBadge = `<span style="background: #FEF3C7; color: #92400E; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 700;">NEEDS PRACTICE (Streak: ${qState.streak})</span>`;
  }

  const catLabel = q.category === "road_signs" ? "Road Signs" : q.category === "rules_of_road" ? "Traffic Rules" : "Driving Principles";
  const imgHtml = q.image
    ? `<div class="question-visual-box" style="margin: 12px auto;"><img src="${withAssetVer(q.image)}" alt="Sign / Scenario" class="question-image" style="max-height: 145px;"></div>`
    : "";

  const opts = q.options[lang] || q.options.en;
  let optionsHtml = `<div class="options-grid" style="margin-top: 14px;">`;
  opts.forEach((optText, idx) => {
    let cls = `practice-opt-btn ${easyRead && lang === "en" ? "is-easy-read" : ""}`;
    let disabledAttr = "";
    if (isAnswered) {
      disabledAttr = "disabled";
      if (idx === q.answerIndex) cls += " is-correct";
      else if (idx === lastAns.selectedIndex && !lastAns.isCorrect) cls += " is-wrong";
    }
    const formattedOpt = formatDisplayText(optText, lang, easyRead);
    optionsHtml += `
      <button type="button" class="${cls}" data-opt-idx="${idx}" ${disabledAttr}>
        <span class="practice-opt-num">${idx + 1}</span>
        <span style="flex: 1; word-break: break-word;">${formattedOpt}</span>
      </button>
    `;
  });
  optionsHtml += `</div>`;

  const qDisplayText = formatDisplayText(q.text[lang] || q.text.en, lang, easyRead);
  const expText = q.explanation[lang] || q.explanation.en || "";
  const expDisplay = isAnswered ? "block" : "none";

  container.innerHTML = `
    <div class="practice-card-top">
      <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
        <span class="spec-pill">${catLabel} • #${q.questionNumber}</span>
        <span style="font-size: 0.76rem; color: var(--text-muted); font-weight: 600;">${q.id}</span>
      </div>
      <div class="practice-card-tools">
        <div id="practice-status-badge-wrap">${statusBadge}</div>
        <button type="button" id="btn-practice-read" class="speech-read-btn" style="padding: 5px 10px; font-size: 0.8rem;">
          ${svgIcon("speak", 15)}
          <span>${t("voice_read", "Read Aloud")}</span>
        </button>
      </div>
    </div>

    <h3 class="practice-q-heading ${easyRead && lang === "en" ? "is-easy-read" : ""}">${qDisplayText}</h3>
    ${imgHtml}
    ${optionsHtml}

    <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
      <label class="guess-flag-container">
        <input type="checkbox" id="practice-guess-checkbox" ${qState.isGuessed ? "checked" : ""}>
        <span class="guess-flag-label">${t("guess_checkbox", "I guessed this answer (keep on probation)")}</span>
      </label>
    </div>

    <div id="practice-explanation-box" style="display: ${expDisplay}; margin-top: 14px; background: #EFF6FF; border-left: 4px solid var(--secondary-blue); padding: 12px 14px; border-radius: 6px; font-size: 0.9rem; color: #1E293B;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 10px;">
        <div style="line-height: 1.5;"><strong>Official Rule:</strong> ${expText}</div>
        <button type="button" id="btn-practice-retry-q" class="btn-secondary-light" style="padding: 4px 10px; font-size: 0.76rem; min-height: 30px; flex-shrink: 0;">Re-try</button>
      </div>
    </div>

    <div class="practice-card-nav">
      <div class="practice-nav-buttons">
        <button type="button" id="btn-practice-prev" class="btn-secondary-light" ${posIndex <= 0 ? "disabled" : ""}>
          ← <span>${t("btn_prev", "Previous")}</span>
        </button>
        <button type="button" id="btn-practice-next" class="btn-primary-solid" ${posIndex >= posTotal - 1 ? "disabled" : ""}>
          <span>${t("btn_next", "Next")}</span> →
        </button>
      </div>
      <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
        <span style="font-size: 0.82rem; font-weight: 700; color: var(--text-muted);" class="tabular-nums">${posIndex + 1} of ${posTotal}</span>
        <button type="button" id="btn-practice-next-unseen" class="btn-outline-primary" style="padding: 7px 12px; font-size: 0.82rem;">
          <span>${t("btn_next_unseen", "Next Unmastered")}</span> ➔
        </button>
      </div>
    </div>
  `;

  container.querySelector("#btn-practice-read")?.addEventListener("click", () => {
    practice.readCurrentQuestion();
  });

  container.querySelector("#btn-practice-prev")?.addEventListener("click", () => {
    practice.prevQuestion();
  });

  container.querySelector("#btn-practice-next")?.addEventListener("click", () => {
    practice.nextQuestion();
  });

  container.querySelector("#btn-practice-next-unseen")?.addEventListener("click", () => {
    const moved = practice.selectNextUnseen();
    if (!moved) showToast("All filtered questions are already mastered!");
  });

  container.querySelector("#btn-practice-retry-q")?.addEventListener("click", () => {
    if (practice.lastAnswers) delete practice.lastAnswers[q.id];
    renderPracticeCard(q);
  });

  container.querySelectorAll(".practice-opt-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.getAttribute("data-opt-idx"), 10);
      const isCorrect = idx === q.answerIndex;
      const guessCheckbox = container.querySelector("#practice-guess-checkbox");
      const isGuessed = guessCheckbox ? guessCheckbox.checked : false;

      container.querySelectorAll(".practice-opt-btn").forEach((b, bIdx) => {
        b.disabled = true;
        if (bIdx === q.answerIndex) b.classList.add("is-correct");
        else if (bIdx === idx && !isCorrect) b.classList.add("is-wrong");
      });

      const expBox = document.getElementById("practice-explanation-box");
      if (expBox) expBox.style.display = "block";

      practice.answerPracticeQuestion(q.id, idx, isGuessed);

      const statusBadgeWrap = document.getElementById("practice-status-badge-wrap");
      const updatedState = storage.getQuestionState(q.id);
      if (statusBadgeWrap) {
        if (updatedState.status === "mastered") {
          statusBadgeWrap.innerHTML = `<span style="background: #DCFCE7; color: #166534; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 700;">MASTERED (Streak: ${updatedState.streak})</span>`;
        } else if (updatedState.status === "probation") {
          statusBadgeWrap.innerHTML = `<span style="background: #FEF3C7; color: #92400E; padding: 3px 9px; border-radius: 999px; font-size: 0.74rem; font-weight: 700;">NEEDS PRACTICE (Streak: ${updatedState.streak})</span>`;
        }
      }
    });
  });
}

// ==========================================
// 3. FLASHCARDS UI
// ==========================================
function initFlashcardsUI() {
  const cardBox = document.getElementById("flashcard-box");
  const btnPrev = document.getElementById("btn-fc-prev");
  const btnNext = document.getElementById("btn-fc-next");
  const btnKnow = document.getElementById("btn-fc-mastered");
  const btnStudy = document.getElementById("btn-fc-study-again");
  const btnRead = document.getElementById("btn-fc-read");

  let emptyView = document.getElementById("fc-empty-view");
  if (!emptyView && cardBox) {
    emptyView = document.createElement("div");
    emptyView.id = "fc-empty-view";
    emptyView.style.display = "none";
    emptyView.style.flexDirection = "column";
    emptyView.style.alignItems = "center";
    emptyView.style.gap = "12px";
    emptyView.style.padding = "20px";
    emptyView.style.textAlign = "center";
    emptyView.style.margin = "auto 0";
    cardBox.appendChild(emptyView);
  }

  btnRead?.addEventListener("click", e => {
    e.stopPropagation();
    flashcards.readCurrentSign();
  });

  cardBox?.addEventListener("click", () => {
    const list = flashcards.getFilteredSigns();
    if (list.length > 0) flashcards.flipCard();
  });

  cardBox?.addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      const list = flashcards.getFilteredSigns();
      if (list.length > 0) flashcards.flipCard();
    }
  });

  btnPrev?.addEventListener("click", () => flashcards.prevCard());
  btnNext?.addEventListener("click", () => flashcards.nextCard());

  btnKnow?.addEventListener("click", () => {
    const list = flashcards.getFilteredSigns();
    const sign = list[flashcards.currentIndex];
    if (sign) flashcards.markMastered(sign.id);
  });

  btnStudy?.addEventListener("click", () => {
    const list = flashcards.getFilteredSigns();
    const sign = list[flashcards.currentIndex];
    if (sign) flashcards.markNeedsPractice(sign.id);
  });

  document.querySelectorAll("[data-fc-filter]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-fc-filter]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      flashcards.setFilter(btn.getAttribute("data-fc-filter"));
    });
  });

  flashcards.onStateChange = state => {
    updateReadinessMeter();
    const frontView = document.getElementById("fc-front-view");
    const backView = document.getElementById("fc-back-view");
    const img = document.getElementById("fc-image");
    const backThumb = document.getElementById("fc-back-thumb");
    const typeBadge = document.getElementById("fc-type-badge");
    const masteryPill = document.getElementById("fc-mastery-pill");
    const signName = document.getElementById("fc-sign-name");
    const signDesc = document.getElementById("fc-sign-desc");
    const counter = document.getElementById("fc-counter");
    const progressBar = document.getElementById("fc-progress-bar");

    const sign = state.currentSign;

    if (!sign || state.total === 0) {
      if (counter) counter.textContent = "0 of 0";
      if (progressBar) progressBar.style.width = "100%";
      if (frontView) frontView.style.display = "none";
      if (backView) backView.style.display = "none";
      if (cardBox) cardBox.classList.remove("is-flipped");
      if (emptyView) {
        emptyView.style.display = "flex";
        emptyView.innerHTML = `
          <div style="font-size: 2.6rem;">✓</div>
          <h3 style="font-size: 1.2rem; color: #166534; font-weight: 800; margin: 0;">All Signs in this Category Mastered!</h3>
          <p style="font-size: 0.9rem; color: #475569; margin: 0; max-width: 36ch;">Select "All 94 Signs" or another category above to keep reviewing.</p>
        `;
      }
      [btnPrev, btnNext, btnKnow, btnStudy].forEach(b => {
        if (b) b.disabled = true;
      });
      return;
    }

    if (emptyView) emptyView.style.display = "none";
    if (btnKnow) btnKnow.disabled = false;
    if (btnStudy) btnStudy.disabled = false;
    if (btnPrev) btnPrev.disabled = state.currentIndex === 0;
    if (btnNext) btnNext.disabled = state.currentIndex >= state.total - 1;

    if (counter) counter.textContent = `Card ${state.currentIndex + 1} of ${state.total}`;
    if (progressBar) {
      progressBar.style.width = `${Math.round(((state.currentIndex + 1) / state.total) * 100)}%`;
    }

    const lang = getCurrentLang();
    const rawName = sign.options[lang] ? sign.options[lang][sign.answerIndex] : sign.options.en[sign.answerIndex];
    const name = cleanPdfText(rawName);
    const desc = sign.explanation[lang] || sign.explanation.en;

    if (img) img.src = withAssetVer(sign.image);
    if (backThumb) backThumb.src = withAssetVer(sign.image);

    if (typeBadge) {
      const sType = (sign.signType || "mandatory").toLowerCase();
      typeBadge.textContent = sType.toUpperCase();
      typeBadge.className = `seo-badge badge-${sType === "cautionary" ? "cautionary" : sType === "informatory" ? "informatory" : "mandatory"}`;
    }

    if (masteryPill) {
      const st = storage.getQuestionState(sign.id);
      if (st.status === "mastered") {
        masteryPill.textContent = "MASTERED";
        masteryPill.style.background = "#DCFCE7";
        masteryPill.style.color = "#166534";
        masteryPill.style.borderColor = "#86EFAC";
      } else if (st.status === "probation") {
        masteryPill.textContent = "REVIEW";
        masteryPill.style.background = "#FEF3C7";
        masteryPill.style.color = "#92400E";
        masteryPill.style.borderColor = "#FCD34D";
      } else {
        masteryPill.textContent = "UNSEEN";
        masteryPill.style.background = "#F1F5F9";
        masteryPill.style.color = "#475569";
        masteryPill.style.borderColor = "#CBD5E1";
      }
    }

    if (signName) signName.textContent = name;
    if (signDesc) signDesc.textContent = desc;

    if (cardBox) cardBox.classList.toggle("is-flipped", state.isFlipped);
    if (frontView) frontView.style.display = state.isFlipped ? "none" : "flex";
    if (backView) backView.style.display = state.isFlipped ? "flex" : "none";
  };

  flashcards.notifyUpdate();
}

// ==========================================
// 4. TRICKY TWINS RENDERER (Includes Memory Hook!)
// ==========================================
function renderTrickyTwins() {
  const container = document.getElementById("twins-container");
  if (!container || !trickyTwins.length) return;

  const lang = getCurrentLang();
  container.innerHTML = "";

  trickyTwins.forEach(pair => {
    const card = document.createElement("article");
    card.className = "card-surface";
    card.style.padding = "20px";

    const titleText = pair.title[lang] || pair.title.en;
    const hookText = pair.memoryHook ? (pair.memoryHook[lang] || pair.memoryHook.en) : "";

    card.innerHTML = `
      <h3 style="font-size: 1.08rem; color: var(--primary-navy); margin-bottom: 14px; font-weight: 800; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">${titleText}</h3>
      <div class="twins-comparison-grid">
        <div style="background: var(--surface-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 12px; text-align: center;">
          <img src="${withAssetVer(pair.signA.image)}" alt="${pair.signA.name.en}" style="max-height: 86px; object-fit: contain; margin-bottom: 8px;">
          <strong style="display: block; font-size: 0.88rem; color: var(--primary-navy); margin-bottom: 4px;">${pair.signA.name[lang] || pair.signA.name.en}</strong>
          <p style="font-size: 0.8rem; color: var(--text-secondary); text-align: left; line-height: 1.4;">${pair.signA.rule[lang] || pair.signA.rule.en}</p>
        </div>

        <div style="background: var(--surface-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 12px; text-align: center;">
          <img src="${withAssetVer(pair.signB.image)}" alt="${pair.signB.name.en}" style="max-height: 86px; object-fit: contain; margin-bottom: 8px;">
          <strong style="display: block; font-size: 0.88rem; color: var(--primary-navy); margin-bottom: 4px;">${pair.signB.name[lang] || pair.signB.name.en}</strong>
          <p style="font-size: 0.8rem; color: var(--text-secondary); text-align: left; line-height: 1.4;">${pair.signB.rule[lang] || pair.signB.rule.en}</p>
        </div>
      </div>
      ${hookText ? `<div class="twins-memory-hook"><strong>Memory Hook:</strong> ${hookText}</div>` : ""}
    `;

    container.appendChild(card);
  });
}

// ==========================================
// 5. RAPID CHEATSHEET RENDERER
// ==========================================
function renderCheatsheet() {
  const container = document.getElementById("cheatsheet-container");
  if (!container || !cheatsheet) return;

  const lang = getCurrentLang();
  const title = cheatsheet.title[lang] || cheatsheet.title.en;

  const rulesHtml = cheatsheet.goldenRules
    .map((gr, idx) => {
      const text = gr.rule[lang] || gr.rule.en;
      return `
        <div class="cheatsheet-rule-card">
          <span class="rule-num-badge">${idx + 1}</span>
          <p style="font-size: 0.92rem; color: var(--text-primary); line-height: 1.5; margin: 0;">${text}</p>
        </div>
      `;
    })
    .join("");

  let handSignalsHtml = "";
  if (popularGuides && popularGuides.handSignals) {
    const hs = popularGuides.handSignals;
    const hsTitle = hs.title[lang] || hs.title.en;
    const hsCards = hs.items
      .map(
        item => `
      <div style="background: var(--surface-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; display: flex; gap: 12px; align-items: center;">
        <img src="${withAssetVer(item.image)}" alt="${item.name.en}" style="width: 68px; height: 68px; object-fit: contain; background: #FFFFFF; border-radius: var(--radius-sm); padding: 4px; border: 1px solid var(--border-color); flex-shrink: 0;">
        <div>
          <span class="seo-badge badge-informatory" style="margin-bottom: 4px;">${item.kind}</span>
          <strong style="display: block; font-size: 0.9rem; color: var(--primary-navy); margin-bottom: 3px;">${item.name[lang] || item.name.en}</strong>
          <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4; margin: 0;">${item.desc[lang] || item.desc.en}</p>
        </div>
      </div>
    `
      )
      .join("");

    handSignalsHtml = `
      <div style="border-top: 2px solid var(--border-color); padding-top: 22px;">
        <h3 style="font-size: 1.15rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 12px;">${hsTitle}</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 12px;">
          ${hsCards}
        </div>
      </div>
    `;
  }

  container.innerHTML = `
    <div class="section-header-block">
      <div>
        <h2 class="section-title">${title}</h2>
        <p class="section-subtitle">Essential 10-minute rapid revision rules before stepping into the RTO testing booth.</p>
      </div>
      <div class="no-print" style="display: flex; gap: 8px; flex-wrap: wrap;">
        <button type="button" id="btn-print-cheatsheet" class="btn-primary-solid">
          ${svgIcon("printer", 16)}
          <span>Print / Save PDF</span>
        </button>
        <a href="cheatsheet/" class="btn-secondary-light">
          <span>Full Printable Sheet ↗</span>
        </a>
      </div>
    </div>
    <div class="cheatsheet-rules-grid">${rulesHtml}</div>
    ${handSignalsHtml}
  `;

  document.getElementById("btn-print-cheatsheet")?.addEventListener("click", () => {
    window.print();
  });
}

// ==========================================
// 6. HYDERABAD RTO GUIDE RENDERER (Sticky Section Jump Nav)
// ==========================================
function renderRtoGuide() {
  const container = document.getElementById("rto-guide-container");
  if (!container || !rtoGuide) return;

  const lang = getCurrentLang();
  const title = (rtoGuide.title && rtoGuide.title[lang]) || rtoGuide.title.en;
  const subtitle = (rtoGuide.subtitle && rtoGuide.subtitle[lang]) || rtoGuide.subtitle.en;
  const savedChecks = JSON.parse(localStorage.getItem("rto_guide_checklist") || "{}");
  const checklistItems = rtoGuide.checklist || [];
  const checkedCount = checklistItems.filter(item => !!savedChecks[item.id]).length;

  const checklistHtml = checklistItems
    .map(item => {
      const itemText = (item.item && item.item[lang]) || item.item.en || "";
      const descText = (item.desc && item.desc[lang]) || item.desc.en || "";
      const isChecked = !!savedChecks[item.id];
      const badgeCls = item.mandatory ? "badge-mandatory" : "badge-informatory";
      const badgeText = item.mandatory
        ? lang === "te" ? "తప్పనిసరి" : lang === "hi" ? "अनिवार्य" : "Mandatory"
        : lang === "te" ? "ఐచ్ఛికం" : lang === "hi" ? "वैकल्पिक" : "Optional";

      return `
      <label style="display: flex; gap: 12px; align-items: flex-start; padding: 12px 14px; background: ${isChecked ? "#F0FDF4" : "#FFFFFF"}; border: 1px solid ${isChecked ? "#86EFAC" : "var(--border-color)"}; border-radius: var(--radius-sm); cursor: pointer; transition: all 0.16s ease;">
        <input type="checkbox" class="rto-check-item" data-id="${item.id}" ${isChecked ? "checked" : ""} style="width: 19px; height: 19px; margin-top: 2px; accent-color: var(--success-green); cursor: pointer;">
        <div style="flex: 1;">
          <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 4px;">
            <strong style="font-size: 0.94rem; color: var(--text-primary); text-decoration: ${isChecked ? "line-through" : "none"};">${itemText}</strong>
            <span class="seo-badge ${badgeCls}">${badgeText}</span>
          </div>
          <p style="font-size: 0.83rem; color: var(--text-secondary); line-height: 1.45; margin: 0;">${descText}</p>
        </div>
      </label>
    `;
    })
    .join("");

  const stepsHtml = (rtoGuide.steps || [])
    .map(step => {
      const stepTitle = (step.title && step.title[lang]) || step.title.en || "";
      const stepDetail = (step.detail && step.detail[lang]) || step.detail.en || "";
      return `
      <div style="display: flex; gap: 14px; align-items: flex-start;">
        <div class="rule-num-badge" style="border-radius: 50%; width: 34px; height: 34px; background: var(--secondary-blue);">${step.step}</div>
        <div style="flex: 1; background: var(--surface-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 14px 16px; margin-bottom: 10px;">
          <h4 style="font-size: 1rem; color: var(--primary-navy); font-weight: 700; margin-bottom: 4px;">${stepTitle}</h4>
          <p style="font-size: 0.86rem; color: var(--text-secondary); line-height: 1.45; margin: 0;">${stepDetail}</p>
        </div>
      </div>
    `;
    })
    .join("");

  const centersHtml = (rtoGuide.centers || [])
    .map(center => {
      const name = (center.name && center.name[lang]) || center.name.en || "";
      const area = (center.area && center.area[lang]) || center.area.en || "";
      const address = (center.address && center.address[lang]) || center.address.en || "";
      return `
      <div class="seo-card" style="display: flex; flex-direction: column; justify-content: space-between;">
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="background: var(--primary-navy); color: #F3CA40; font-size: 0.75rem; font-weight: 800; padding: 3px 9px; border-radius: 6px;">${center.code}</span>
            <span style="font-size: 0.74rem; color: var(--success-green); font-weight: 700;">${center.hours}</span>
          </div>
          <h4 style="font-size: 0.98rem; color: var(--primary-navy); font-weight: 700; margin-bottom: 4px;">${name}</h4>
          <p style="font-size: 0.82rem; color: var(--secondary-blue); font-weight: 600; margin-bottom: 6px;">${area}</p>
          <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.42; margin: 0;">${address}</p>
        </div>
      </div>
    `;
    })
    .join("");

  const feeData = rtoGuide.feeRules || {};
  const feesList = (feeData.fees || [])
    .map(f => {
      const cat = (f.category && f.category[lang]) || f.category.en || "";
      const breakup = (f.breakup && f.breakup[lang]) || f.breakup.en || "";
      return `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 14px; background: #FFFFFF; border: 1px solid var(--border-color); border-radius: var(--radius-sm);">
        <div>
          <strong style="display: block; font-size: 0.9rem; color: var(--text-primary);">${cat}</strong>
          <span style="font-size: 0.79rem; color: var(--text-muted);">${breakup}</span>
        </div>
        <span class="tabular-nums" style="font-size: 1.15rem; font-weight: 800; color: #047857;">${f.amount}</span>
      </div>
    `;
    })
    .join("");

  const retestText = (feeData.retestRule && feeData.retestRule[lang]) || (feeData.retestRule && feeData.retestRule.en) || "";
  const validityText = (feeData.validityRule && feeData.validityRule[lang]) || (feeData.validityRule && feeData.validityRule.en) || "";

  const tipsHtml = (rtoGuide.topTips || [])
    .map(tip => {
      const tipTitle = (tip.title && tip.title[lang]) || tip.title.en || "";
      const tipDesc = (tip.desc && tip.desc[lang]) || tip.desc.en || "";
      return `
      <div style="background: var(--accent-gold-light); border: 1px solid #FDE68A; border-radius: var(--radius-md); padding: 14px 16px;">
        <h4 style="font-size: 0.94rem; color: #92400E; font-weight: 800; margin-bottom: 5px;">${tipTitle}</h4>
        <p style="font-size: 0.84rem; color: #78350F; line-height: 1.45; margin: 0;">${tipDesc}</p>
      </div>
    `;
    })
    .join("");

  container.innerHTML = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 16px; margin-bottom: 16px;">
      <h2 class="section-title">${title}</h2>
      <p class="section-subtitle">${subtitle}</p>
    </div>

    <!-- In-Page Section Jump Bar -->
    <nav class="section-jump-bar" aria-label="RTO Guide Sections">
      <a href="#guide-sec-checklist" class="pill-btn" id="rto-jump-checklist" data-guide-jump="guide-sec-checklist">Checklist (${checkedCount}/${checklistItems.length})</a>
      <a href="#guide-sec-centers" class="pill-btn" data-guide-jump="guide-sec-centers">RTO Centers</a>
      <a href="#guide-sec-fees" class="pill-btn" data-guide-jump="guide-sec-fees">Fees &amp; Validity</a>
      <a href="#guide-sec-dl" class="pill-btn" data-guide-jump="guide-sec-dl">DL 8 &amp; H Track</a>
      <a href="#guide-sec-fines" class="pill-btn" data-guide-jump="guide-sec-fines">Traffic Fines</a>
      <a href="#guide-sec-codes" class="pill-btn" data-guide-jump="guide-sec-codes">TS / TG Codes (01–38)</a>
    </nav>

    <!-- Section 1: Checklist & Workflow -->
    <div id="guide-sec-checklist" class="guide-section-anchor" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 24px; margin-bottom: 32px;">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; gap: 8px;">
          <h3 style="font-size: 1.1rem; color: var(--primary-navy); font-weight: 800;">
            ${lang === "te" ? "తీసుకెళ్లవలసిన పత్రాలు" : lang === "hi" ? "दस्तावेज़ चेकलिस्ट" : "Documents Checklist"}
          </h3>
          <span id="rto-checklist-progress" class="spec-pill">${checkedCount} / ${checklistItems.length} Ready</span>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px;">${checklistHtml}</div>
      </div>

      <div>
        <h3 style="font-size: 1.1rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 12px;">
          ${lang === "te" ? "పరీక్ష రోజు 5 దశల విధానం" : lang === "hi" ? "परीक्षा दिवस के 5 चरण" : "Test-Day 5-Step Process"}
        </h3>
        <div>${stepsHtml}</div>
      </div>
    </div>

    <!-- Section 2: Hyderabad RTO Centers -->
    <div id="guide-sec-centers" class="guide-section-anchor" style="margin-bottom: 28px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
        <h3 style="font-size: 1.12rem; color: var(--primary-navy); font-weight: 800;">
          ${lang === "te" ? "హైదరాబాద్ RTO కార్యాలయాలు & కేంద్రాలు" : lang === "hi" ? "हैदराबाद आरटीओ केंद्र" : "Hyderabad RTO Testing Centers Directory"}
        </h3>
        <a href="https://transport.telangana.gov.in" target="_blank" rel="noopener" style="font-size: 0.82rem; color: var(--secondary-blue); font-weight: 700;">transport.telangana.gov.in ↗</a>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 14px;">${centersHtml}</div>
    </div>

    <!-- Guide Mid-Content Section Break Ad -->
    <aside class="ad-slot-wrapper ad-format-leaderboard is-hidden" id="ad-slot-guide-mid" data-ad-slot="seo_in_content" aria-label="Advertisement">
      <span class="ad-label">${t("advertisement_label", "Advertisement")}</span>
      <div class="ad-slot-inner"></div>
    </aside>

    <!-- Section 3: Fees & Validity -->
    <div id="guide-sec-fees" class="guide-section-anchor" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 18px; margin-bottom: 32px;">
      <div style="background: var(--surface-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 18px;">
        <h3 style="font-size: 1.05rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 12px;">
          ${lang === "te" ? "అధికారిక ఫీజుల వివరాలు" : lang === "hi" ? "आधिकारिक शुल्क" : "Official Government Fees"}
        </h3>
        <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 12px;">${feesList}</div>
        <p style="font-size: 0.82rem; color: var(--text-secondary); line-height: 1.45; margin: 0; background: #FFFFFF; padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
          <strong>${lang === "te" ? "రీ-టెస్ట్ నిబంధన:" : lang === "hi" ? "पुनः परीक्षा नियम:" : "Retest Policy:"}</strong> ${retestText}
        </p>
      </div>

      <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: var(--radius-md); padding: 18px;">
        <h3 style="font-size: 1.05rem; color: #166534; font-weight: 800; margin-bottom: 12px;">
          ${lang === "te" ? "LLR చెల్లుబాటు & తదుపరి ప్రక్రియ" : lang === "hi" ? "वैधता और स्थायी लाइसेंस" : "LLR Validity & Next Steps"}
        </h3>
        <div style="font-size: 0.88rem; color: #14532D; line-height: 1.5; margin-bottom: 12px;">${validityText}</div>
        <div style="background: #FFFFFF; border: 1px solid #86EFAC; border-radius: var(--radius-sm); padding: 12px;">
          <strong style="display: block; font-size: 0.85rem; color: #166534; margin-bottom: 4px;">30-Day Permanent DL Rule:</strong>
          <span style="font-size: 0.82rem; color: #15803D;">Practice driving with an 'L' board sticker and an accompanying permanent DL holder. Book your permanent Driving Test track slot anytime between day 31 and day 180.</span>
        </div>
      </div>
    </div>

    <!-- Section 4: Top Exam-Day Tips -->
    <div style="margin-bottom: 32px;">
      <h3 style="font-size: 1.12rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 12px;">
        ${lang === "te" ? "పరీక్ష హాల్‌లో పాస్ కావడానికి చిట్కాలు" : lang === "hi" ? "परीक्षा हॉल के लिए महत्वपूर्ण टिप्स" : "Exam Hall High-Scorer Tips"}
      </h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 14px;">${tipsHtml}</div>
    </div>

    ${renderPopularGuidesSections(lang)}
  `;

  // Section jump links scroll cleanly within the page
  container.querySelectorAll("[data-guide-jump]").forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      const targetEl = document.getElementById(link.getAttribute("data-guide-jump"));
      if (targetEl) targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // District RTO Code filter listener with empty state
  const rtoSearchInput = document.getElementById("rto-district-search");
  const rtoEmptyMsg = document.getElementById("rto-district-empty");
  rtoSearchInput?.addEventListener("input", e => {
    const q = e.target.value.trim().toLowerCase();
    let visible = 0;
    container.querySelectorAll(".rto-district-chip").forEach(chip => {
      const hay = chip.getAttribute("data-search") || "";
      const match = !q || hay.includes(q);
      chip.style.display = match ? "flex" : "none";
      if (match) visible++;
    });
    if (rtoEmptyMsg) rtoEmptyMsg.style.display = visible === 0 ? "block" : "none";
  });

  // Interactive checklist listeners
  container.querySelectorAll(".rto-check-item").forEach(cb => {
    cb.addEventListener("change", e => {
      const id = e.target.getAttribute("data-id");
      const current = JSON.parse(localStorage.getItem("rto_guide_checklist") || "{}");
      if (e.target.checked) current[id] = true;
      else delete current[id];
      localStorage.setItem("rto_guide_checklist", JSON.stringify(current));

      const label = e.target.closest("label");
      const strong = label ? label.querySelector("strong") : null;
      if (strong) strong.style.textDecoration = e.target.checked ? "line-through" : "none";
      if (label) {
        label.style.background = e.target.checked ? "#F0FDF4" : "#FFFFFF";
        label.style.borderColor = e.target.checked ? "#86EFAC" : "var(--border-color)";
      }
      const nextCount = checklistItems.filter(item => !!current[item.id]).length;
      const pill = document.getElementById("rto-checklist-progress");
      if (pill) pill.textContent = `${nextCount} / ${checklistItems.length} Ready`;
      const jumpBtn = document.getElementById("rto-jump-checklist");
      if (jumpBtn) jumpBtn.textContent = `Checklist (${nextCount}/${checklistItems.length})`;
    });
  });

  adManager.refreshVisibleSlots();
}

function renderPopularGuidesSections(lang) {
  if (!popularGuides) return "";

  const slot = popularGuides.slotAndDownloadGuide;
  const slotTitle = (slot.title && slot.title[lang]) || slot.title.en;
  const slotStepsHtml = slot.steps
    .map(
      s => `
    <div style="background: var(--surface-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 14px;">
      <strong style="display: block; color: var(--secondary-blue); font-size: 0.94rem; margin-bottom: 4px;">
        ${s.step}. ${(s.title && s.title[lang]) || s.title.en}
      </strong>
      <p style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.45; margin: 0;">
        ${(s.detail && s.detail[lang]) || s.detail.en}
      </p>
    </div>
  `
    )
    .join("");

  const dl = popularGuides.dlTrackGuide;
  const dlTitle = (dl.title && dl.title[lang]) || dl.title.en;
  const dlSub = (dl.subtitle && dl.subtitle[lang]) || dl.subtitle.en;
  const dlElig = (dl.eligibility && dl.eligibility[lang]) || dl.eligibility.en;
  const dlTracksHtml = dl.tracks
    .map(tr => {
      const pts = (tr.points[lang] || tr.points.en).map(p => `<li style="margin-bottom: 5px;">${p}</li>`).join("");
      return `
      <div class="seo-card">
        <span class="seo-badge badge-informatory" style="margin-bottom: 8px;">${tr.badge}</span>
        <h4 style="font-size: 1rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 8px;">${tr.title[lang] || tr.title.en}</h4>
        <ul style="padding-left: 18px; font-size: 0.84rem; color: var(--text-secondary); line-height: 1.48; margin: 0;">${pts}</ul>
      </div>
    `;
    })
    .join("");
  const dlDocsHtml = (dl.documents[lang] || dl.documents.en).map(d => `<li style="margin-bottom: 4px;">${d}</li>`).join("");

  const fines = popularGuides.trafficFines;
  const finesTitle = (fines.title && fines.title[lang]) || fines.title.en;
  const finesRowsHtml = fines.items
    .map(
      item => `
    <tr>
      <td style="padding: 10px 12px; border-bottom: 1px solid #E2E8F0; font-size: 0.86rem; color: var(--text-primary); font-weight: 600;">${item.offence[lang] || item.offence.en}</td>
      <td style="padding: 10px 12px; border-bottom: 1px solid #E2E8F0; font-size: 0.86rem; color: #B91C1C; font-weight: 700;">${item.fine}</td>
      <td style="padding: 10px 12px; border-bottom: 1px solid #E2E8F0; font-size: 0.78rem; color: var(--text-muted);">${item.section}</td>
    </tr>
  `
    )
    .join("");

  const rtoChipsHtml = popularGuides.districtRtoCodes
    .map(d => {
      const searchStr = `${d.code} ts-${d.code} tg-${d.code} ${d.district}`.toLowerCase();
      return `
      <div class="rto-district-chip" data-search="${searchStr}" style="display: flex; align-items: center; gap: 10px; background: var(--surface-subtle); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 9px 12px;">
        <span class="tabular-nums" style="background: var(--primary-navy); color: #F3CA40; font-size: 0.74rem; font-weight: 800; padding: 3px 8px; border-radius: 5px; flex-shrink: 0;">TS / TG-${d.code}</span>
        <span style="font-size: 0.84rem; color: var(--text-primary); font-weight: 600;">${d.district}</span>
      </div>
    `;
    })
    .join("");

  return `
    <div style="border-top: 2px solid var(--border-color); padding-top: 26px; margin-bottom: 32px;">
      <h3 style="font-size: 1.12rem; color: var(--primary-navy); font-weight: 800; margin-bottom: 12px;">${slotTitle}</h3>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px;">${slotStepsHtml}</div>
    </div>

    <div id="guide-sec-dl" class="guide-section-anchor" style="border-top: 2px solid var(--border-color); padding-top: 26px; margin-bottom: 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
        <h3 style="font-size: 1.12rem; color: var(--primary-navy); font-weight: 800; margin: 0;">${dlTitle}</h3>
        <a href="dl-test-guide/" style="font-size: 0.82rem; color: var(--secondary-blue); font-weight: 700;">Full DL Track Guide ↗</a>
      </div>
      <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 12px;">${dlSub} <strong>${dlElig}</strong></p>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(290px, 1fr)); gap: 14px; margin-bottom: 14px;">${dlTracksHtml}</div>
      <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: var(--radius-md); padding: 14px;">
        <strong style="display: block; font-size: 0.9rem; color: #166534; margin-bottom: 6px;">${lang === "te" ? "DL ట్రాక్ టెస్ట్‌కు కావలసిన పత్రాలు" : lang === "hi" ? "DL ट्रैक टेस्ट के लिए आवश्यक दस्तावेज़" : "Documents & Vehicle Needed at DL Track"}</strong>
        <ul style="padding-left: 18px; font-size: 0.84rem; color: #14532D; margin: 0;">${dlDocsHtml}</ul>
      </div>
    </div>

    <div id="guide-sec-fines" class="guide-section-anchor" style="border-top: 2px solid var(--border-color); padding-top: 26px; margin-bottom: 32px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
        <h3 style="font-size: 1.12rem; color: var(--primary-navy); font-weight: 800; margin: 0;">${finesTitle}</h3>
        <a href="traffic-fines/" style="font-size: 0.82rem; color: var(--secondary-blue); font-weight: 700;">Traffic Fines &amp; Hand Signals Page ↗</a>
      </div>
      <div style="overflow-x: auto; border: 1px solid var(--border-color); border-radius: var(--radius-md);">
        <table style="width: 100%; border-collapse: collapse; text-align: left; background: #FFFFFF;">
          <thead>
            <tr style="background: var(--surface-subtle);">
              <th style="padding: 10px 12px; border-bottom: 2px solid #E2E8F0; font-size: 0.84rem;">Violation</th>
              <th style="padding: 10px 12px; border-bottom: 2px solid #E2E8F0; font-size: 0.84rem;">Statutory Fine / Penalty</th>
              <th style="padding: 10px 12px; border-bottom: 2px solid #E2E8F0; font-size: 0.84rem;">MV Act</th>
            </tr>
          </thead>
          <tbody>${finesRowsHtml}</tbody>
        </table>
      </div>
    </div>

    <div id="guide-sec-codes" class="guide-section-anchor" style="border-top: 2px solid var(--border-color); padding-top: 26px;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 12px;">
        <div>
          <h3 style="font-size: 1.12rem; color: var(--primary-navy); font-weight: 800; margin: 0;">${lang === "te" ? "తెలంగాణ అన్ని జిల్లాల RTO కోడ్‌లు (TS / TG 01–38)" : lang === "hi" ? "तेलंगाना के सभी जिलों के RTO कोड (TS / TG 01–38)" : "All Telangana District RTO Codes (TS / TG 01–38)"}</h3>
          <span style="font-size: 0.8rem; color: var(--text-muted);">Both legacy TS and updated TG prefixes map to the same district RTA offices.</span>
        </div>
        <input type="text" id="rto-district-search" placeholder="Search district or code (e.g. Warangal, 07)..." style="padding: 8px 12px; border: 1px solid var(--border-strong); border-radius: var(--radius-sm); font-size: 0.85rem; min-width: 240px;">
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px;">${rtoChipsHtml}</div>
      <p id="rto-district-empty" style="display: none; padding: 16px; text-align: center; color: var(--text-muted); font-size: 0.88rem;">No Telangana district matched your search.</p>
    </div>
  `;
}
