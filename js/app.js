// js/app.js - Main Application Coordinator
import { initI18n, setLanguage, getCurrentLang, t, updateDomTranslations } from "./i18n.js";
import { storage } from "./storage-engine.js";
import { sounds } from "./sound-effects.js";
import { speech } from "./speech-engine.js";
import { coverage, TOTAL_QUESTIONS_COUNT } from "./coverage-engine.js";
import { exam } from "./exam-engine.js";
import { practice } from "./practice-engine.js";
import { flashcards } from "./flashcards-engine.js";
import { sync } from "./sync-engine.js";

let allQuestions = [];
let roadSigns = [];
let rulesOfRoad = [];
let generalPrinciples = [];
let trickyTwins = [];
let cheatsheet = null;
let rtoGuide = null;
let currentRenderedQId = null;
let datasetsLoaded = false;

// Initialize on DOM load
window.addEventListener("DOMContentLoaded", async () => {
  await initI18n();
  setupLanguageSelector();
  setupSoundToggle();
  setupTabs();
  setupModals();
  setupKeyboardHotkeys();

  // Load question datasets
  await loadAllDatasets();

  // Initialize feature engines
  initExamUI();
  initPracticeUI();
  initFlashcardsUI();
  renderTrickyTwins();
  renderCheatsheet();
  renderRtoGuide();
  updateReadinessMeter();

  // UNREGISTER all Service Workers and wipe ALL caches to fix stale module serving.
  // The SW was cache-busting HTML/CSS/app.js but sub-modules (exam-engine.js, etc.)
  // loaded from the old SW cache, breaking the exam. SW is disabled for stability.
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistrations().then(regs => {
      regs.forEach(reg => {
        console.log("[SW] Unregistering:", reg.scope);
        reg.unregister();
      });
    });
  }
  if ("caches" in window) {
    caches.keys().then(keys => {
      keys.forEach(k => {
        console.log("[Cache] Deleting:", k);
        caches.delete(k);
      });
    });
  }
});

async function loadAllDatasets() {
  try {
    const v = "v=13";
    const [signsRes, rulesRes, gpRes, twinsRes, cheatRes, guideRes] = await Promise.all([
      fetch(`data/questions/telangana/road-signs.json?${v}`).then(r => r.json()).catch(() => []),
      fetch(`data/questions/telangana/rules-of-road.json?${v}`).then(r => r.json()).catch(() => []),
      fetch(`data/questions/telangana/general-principles.json?${v}`).then(r => r.json()).catch(() => []),
      fetch(`data/tricky-twins.json?${v}`).then(r => r.json()).catch(() => []),
      fetch(`data/last-minute-cheatsheet.json?${v}`).then(r => r.json()).catch(() => null),
      fetch(`data/rto-guide.json?${v}`).then(r => r.json()).catch(() => null)
    ]);

    roadSigns = signsRes;
    rulesOfRoad = rulesRes;
    generalPrinciples = gpRes;
    allQuestions = [...roadSigns, ...rulesOfRoad, ...generalPrinciples];

    trickyTwins = twinsRes;
    cheatsheet = cheatRes;
    rtoGuide = guideRes;

    coverage.setQuestions(allQuestions);
    practice.setQuestions(allQuestions);
    flashcards.setSigns(roadSigns);

    datasetsLoaded = true;
    console.log(`Loaded ${allQuestions.length} total questions (Signs: ${roadSigns.length}, Rules: ${rulesOfRoad.length}, Principles: ${generalPrinciples.length})`);
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
    if (exam.isActive) exam.notifyUpdate();
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
    if (icon) icon.textContent = enabled ? "🔔" : "🔕";
  });
}

// Navigation Tabs
function setupTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => {
        t.classList.remove("active");
        t.setAttribute("aria-selected", "false");
      });
      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");

      const targetId = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
      });
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");

      // Pause audio on tab change
      speech.stop();
    });
  });
}

// Readiness Meter Update
function updateReadinessMeter() {
  const stats = coverage.getReadinessStats();
  const badgeVal = document.getElementById("header-readiness-val");
  const fill = document.getElementById("header-readiness-fill");

  if (badgeVal) badgeVal.textContent = `${stats.readinessPercent}%`;
  if (fill) {
    fill.style.width = `${Math.min(stats.readinessPercent, 100)}%`;
    if (stats.isExamReady) {
      fill.style.background = "#22C55E";
    } else {
      fill.style.background = "#FFD54F";
    }
  }
}

// Modals Setup (Sync, Reset)
function setupModals() {
  const syncModal = document.getElementById("modal-sync");
  const resetModal = document.getElementById("modal-reset");

  // Sync Modal
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
        alert(t("sync_success", "Progress synchronized successfully!"));
        if (syncModal) syncModal.style.display = "none";
        updateReadinessMeter();
        practice.notifyUpdate();
      } catch (err) {
        alert("Error importing backup file: " + err.message);
      }
    }
  });

  // Reset Modal
  const openReset = () => {
    if (resetModal) resetModal.style.display = "flex";
  };
  document.getElementById("btn-reset-readiness-mini")?.addEventListener("click", openReset);

  document.getElementById("btn-cancel-reset")?.addEventListener("click", () => {
    if (resetModal) resetModal.style.display = "none";
  });

  document.getElementById("btn-confirm-reset")?.addEventListener("click", () => {
    storage.resetReadiness();
    if (resetModal) resetModal.style.display = "none";
    updateReadinessMeter();
    practice.notifyUpdate();
    flashcards.notifyUpdate();
    alert("Practice progress reset to 0%. All streaks cleared!");
  });
}

// Keyboard shortcuts (1-4 for options, Enter for confirm)
function setupKeyboardHotkeys() {
  window.addEventListener("keydown", e => {
    // If exam is active
    if (exam.isActive && !exam.isFinished) {
      if (["1", "2", "3", "4"].includes(e.key)) {
        exam.selectOption(parseInt(e.key, 10) - 1);
      } else if (e.key === "Enter") {
        const guessBox = document.getElementById("exam-guess-checkbox");
        const isGuessed = guessBox ? guessBox.checked : false;
        exam.confirmAndSubmit(isGuessed);
      } else if (e.key === " " || e.key === "Spacebar") {
        // Spacebar toggles audio reading
        exam.readCurrentQuestion();
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
  const btnRetakeMissed = document.getElementById("btn-retake-missed");
  const btnConfirm = document.getElementById("btn-confirm-next");
  const btnRead = document.getElementById("btn-read-question");
  const guessCheckbox = document.getElementById("exam-guess-checkbox");
  const optionsContainer = document.getElementById("exam-options-container");
  const tutorToggle = document.getElementById("exam-toggle-tutor-mode");
  const tutorLabel = document.getElementById("tutor-mode-status-label");
  const explanationBox = document.getElementById("exam-explanation-box");

  // Initialize Tutor Mode preference (Default: OFF)
  const initialTutor = storage.getPreference("tutorMode", false);
  if (tutorToggle) tutorToggle.checked = initialTutor;
  if (tutorLabel) tutorLabel.textContent = initialTutor ? "ON" : "OFF";
  exam.setTutorMode(initialTutor);

  tutorToggle?.addEventListener("change", (e) => {
    const on = e.target.checked;
    exam.setTutorMode(on);
    storage.setPreference("tutorMode", on);
    if (tutorLabel) tutorLabel.textContent = on ? "ON" : "OFF";
  });

  btnStart?.addEventListener("click", () => {
    if (!datasetsLoaded || allQuestions.length === 0) {
      alert("Questions are still loading. Please wait a moment and try again.");
      return;
    }
    currentRenderedQId = null;
    exam.startNewExam();
  });

  btnRetake?.addEventListener("click", () => {
    currentRenderedQId = null;
    exam.startNewExam();
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

  // Event delegation on options container for fast, reliable click handling
  optionsContainer?.addEventListener("click", (e) => {
    if (exam.isRevealed) return; // Prevent changing answers while revealed in Tutor Mode
    const card = e.target.closest(".option-card");
    if (card) {
      const idx = parseInt(card.getAttribute("data-option-index"), 10);
      if (!isNaN(idx)) {
        exam.selectOption(idx);
      }
    }
  });

  speech.onStateChange = isReading => {
    if (btnRead) {
      if (isReading) btnRead.classList.add("reading");
      else btnRead.classList.remove("reading");
    }
  };

  exam.onStateUpdate = state => {
    updateReadinessMeter();

    if (!state.isActive && !state.isFinished) {
      if (introCard) introCard.style.display = "block";
      if (activeCard) activeCard.style.display = "none";
      if (resultCard) resultCard.style.display = "none";
      currentRenderedQId = null;
      return;
    }

    if (state.isFinished) {
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
      const percent = Math.round((state.correctCount / totalQs) * 100);
      if (scoreText) scoreText.textContent = `Score: ${state.correctCount} / ${totalQs} (${percent}%) • Pass Mark: 12`;

      if (state.passed) {
        if (badge) { badge.className = "result-badge-big pass"; badge.textContent = "✓"; }
        if (title) { title.className = "result-title pass"; title.textContent = t("result_pass", "CONGRATULATIONS! YOU PASSED"); }
        if (desc) desc.textContent = t("result_pass_desc", "You reached the passing mark of 12 correct! You are well prepared for the real RTA exam.");
      } else {
        if (badge) { badge.className = "result-badge-big fail"; badge.textContent = "✗"; }
        if (title) { title.className = "result-title fail"; title.textContent = t("result_fail", "TEST NOT CLEARED"); }
        if (desc) desc.textContent = t("result_fail_desc", "You need at least 12 correct answers to pass. Review your missed questions below or in Topic Practice.");
      }

      if (waBtn) {
        const waMsg = encodeURIComponent(`I scored ${state.correctCount}/${totalQs} on the Telangana RTA LLR STALL mock exam! Practice here: ${window.location.href}`);
        waBtn.href = `https://api.whatsapp.com/send?text=${waMsg}`;
      }

      // Render the Detailed Post-Exam Review Section
      renderExamResultReview(state, getCurrentLang(), exam);
      return;
    }

    // Active Question Screen
    if (introCard) introCard.style.display = "none";
    if (activeCard) activeCard.style.display = "block";
    if (resultCard) resultCard.style.display = "none";

    const q = state.currentQuestion;
    if (!q) {
      // Questions failed to load — show error in question text
      const qTextEl = document.getElementById("exam-q-text");
      if (qTextEl) qTextEl.textContent = "⚠️ Questions not loaded. Please refresh the page.";
      return;
    }

    const lang = getCurrentLang();
    const timerDisplay = document.getElementById("timer-seconds-display");
    const timerCircle = document.getElementById("timer-progress-circle");

    // 1. Always update 30s countdown timer on every tick
    if (timerDisplay) timerDisplay.textContent = state.timeLeft;
    if (timerCircle) {
      const totalCircumference = 144.5;
      const fraction = state.timeLeft / 30;
      const offset = totalCircumference * (1 - fraction);
      timerCircle.style.strokeDashoffset = offset;

      if (state.timeLeft <= 5) {
        timerCircle.setAttribute("class", "timer-circle-progress red");
      } else if (state.timeLeft <= 15) {
        timerCircle.setAttribute("class", "timer-circle-progress amber");
      } else {
        timerCircle.setAttribute("class", "timer-circle-progress");
      }
    }

    // 2. Only re-render question body when question changes
    //    Re-query DOM elements fresh each time (never rely on stale closure reference)
    const isNewQuestion = (currentRenderedQId !== q.id);
    if (isNewQuestion) {
      const qBadge = document.getElementById("exam-q-badge");
      const qText = document.getElementById("exam-q-text");
      const visualBox = document.getElementById("exam-q-visual");
      const qImg = document.getElementById("exam-q-img");
      const countSigns = document.getElementById("count-signs");
      const countRules = document.getElementById("count-rules");
      const countPrinciples = document.getElementById("count-principles");
      const freshOptionsContainer = document.getElementById("exam-options-container");

      // Header badge
      if (qBadge) qBadge.textContent = `Question ${state.currentIndex + 1} of 20`;

      // Category quota counters
      let sSeen = 0, rSeen = 0, pSeen = 0;
      for (let i = 0; i <= state.currentIndex; i++) {
        const item = exam.questions[i];
        if (item) {
          if (item.category === "road_signs") sSeen++;
          else if (item.category === "rules_of_road") rSeen++;
          else if (item.category === "general_principles") pSeen++;
        }
      }
      if (countSigns) countSigns.textContent = `${Math.min(sSeen, 8)}/8`;
      if (countRules) countRules.textContent = `${Math.min(rSeen, 8)}/8`;
      if (countPrinciples) countPrinciples.textContent = `${Math.min(pSeen, 4)}/4`;

      // Question text
      if (qText) qText.textContent = (q.text && q.text[lang]) || (q.text && q.text.en) || "";

      // Image
      if (q.image) {
        if (qImg) qImg.src = q.image;
        if (visualBox) visualBox.style.display = "flex";
      } else {
        if (visualBox) visualBox.style.display = "none";
      }

      // Populate options — build HTML and inject
      let opts = [];
      if (q && q.options) {
        if (Array.isArray(q.options)) {
          opts = q.options;
        } else if (typeof q.options === "object") {
          opts = q.options[lang] || q.options.en || q.options.te || q.options.hi || [];
        }
      }

      if (freshOptionsContainer) {
        if (!opts || opts.length === 0) {
          console.warn("No options found for question:", q.id, q);
          freshOptionsContainer.innerHTML = `<div style="color: #EF4444; padding: 12px; font-weight: 700;">No options available for this question.</div>`;
        } else {
          let html = "";
          opts.forEach((optText, idx) => {
            const isSelected = (state.selectedOption === idx);
            html += `<div class="option-card ${isSelected ? 'selected' : ''}" role="button" tabindex="0" data-option-index="${idx}"><div class="option-badge">${idx + 1}</div><div class="option-text">${optText}</div></div>`;
          });
          freshOptionsContainer.innerHTML = html;
          console.log(`[Exam] Q${state.currentIndex + 1} rendered with ${opts.length} options (id=${q.id})`);
        }
        // Only mark as rendered AFTER successfully writing to DOM
        currentRenderedQId = q.id;
      } else {
        console.error("[Exam] exam-options-container element not found in DOM!");
      }
    } else {
      // Same question, different tick — only update selected state without DOM rebuild
      const freshOptionsContainer = document.getElementById("exam-options-container");
      if (freshOptionsContainer) {
        const cards = freshOptionsContainer.querySelectorAll(".option-card");
        if (cards.length === 0) {
          // Safety net: options disappeared somehow — force a re-render next tick
          console.warn("[Exam] Options container is empty on existing question — forcing re-render");
          currentRenderedQId = null;
        } else {
          cards.forEach((card) => {
            const idx = parseInt(card.getAttribute("data-option-index"), 10);
            if (idx === state.selectedOption) {
              card.classList.add("selected");
            } else {
              card.classList.remove("selected");
            }
          });
        }
      }
    }

    // 3. Handle Tutor Mode feedback state vs standard state
    const expBox = document.getElementById("exam-explanation-box");
    if (state.isRevealed) {
      // Highlight correct & wrong options
      const optContainer = document.getElementById("exam-options-container");
      if (optContainer) {
        optContainer.querySelectorAll(".option-card").forEach((card) => {
          const idx = parseInt(card.getAttribute("data-option-index"), 10);
          card.classList.remove("selected", "correct", "incorrect", "dimmed");
          if (idx === q.answerIndex) {
            card.classList.add("correct");
          } else if (idx === state.selectedOption) {
            card.classList.add("incorrect");
          } else {
            card.classList.add("dimmed");
          }
        });
      }

      // Display official rule explanation
      if (expBox) {
        const isCorrect = (state.selectedOption === q.answerIndex);
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

      // Transform button to CONTINUE
      if (btnConfirm) {
        btnConfirm.disabled = false;
        btnConfirm.innerHTML = `<span>CONTINUE</span> ➔`;
        btnConfirm.style.background = "var(--secondary-blue)";
      }
    } else {
      if (expBox) expBox.style.display = "none";
      if (btnConfirm) {
        btnConfirm.disabled = (state.selectedOption === null);
        btnConfirm.innerHTML = `<span data-i18n="btn_confirm_next">CONFIRM & NEXT</span> ➔`;
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

  // Category breakdown
  if (catBreakdown) {
    let signsC = 0, signsT = 0;
    let rulesC = 0, rulesT = 0;
    let gpC = 0, gpT = 0;

    history.forEach(h => {
      const cat = h.question.category;
      if (cat === "road_signs") { signsT++; if (h.isCorrect) signsC++; }
      else if (cat === "rules_of_road") { rulesT++; if (h.isCorrect) rulesC++; }
      else if (cat === "general_principles") { gpT++; if (h.isCorrect) gpC++; }
    });

    catBreakdown.innerHTML = `
      <span style="background: #FEF3C7; color: #92400E; padding: 4px 10px; border-radius: 4px; border: 1px solid #FDE68A;">
        🚸 Signs: ${signsC}/${signsT} (${signsT > 0 ? Math.round((signsC/signsT)*100) : 0}%)
      </span>
      <span style="background: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 4px; border: 1px solid #FECACA;">
        🛑 Rules: ${rulesC}/${rulesT} (${rulesT > 0 ? Math.round((rulesC/rulesT)*100) : 0}%)
      </span>
      <span style="background: #EFF6FF; color: #1E40AF; padding: 4px 10px; border-radius: 4px; border: 1px solid #BFDBFE;">
        🚗 Principles: ${gpC}/${gpT} (${gpT > 0 ? Math.round((gpC/gpT)*100) : 0}%)
      </span>
    `;
  }

  // Re-try Missed Questions Button
  if (btnRetakeMissed) {
    if (missedItems.length > 0) {
      btnRetakeMissed.style.display = "inline-flex";
      if (countMissedBtn) countMissedBtn.textContent = missedItems.length;
      btnRetakeMissed.onclick = () => {
        const missedQuestions = missedItems.map(h => h.question);
        currentRenderedQId = null;
        examEngine.startCustomExam(missedQuestions);
      };
    } else {
      btnRetakeMissed.style.display = "none";
    }
  }

  // Build review cards
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
      const qText = (q.text && q.text[lang]) || (q.text && q.text.en) || "";
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
        <div class="review-card ${isCorrect ? 'correct' : 'wrong'}" data-review-status="${isCorrect ? 'correct' : 'wrong'}">
          <div class="review-card-top">
            <span class="review-q-num">Q${idx + 1} • ${categoryName} (${q.id})</span>
            <span class="review-q-status ${isCorrect ? 'correct' : 'wrong'}">
              ${isCorrect ? "✓ Correct" : (h.timeout ? "⏰ Timed Out" : "✗ Incorrect")}
              ${h.isGuessed ? " • 🤔 Guessed" : ""}
            </span>
          </div>

          <h4 class="review-q-title">${qText}</h4>

          ${q.image ? `
            <div class="review-q-img-wrap">
              <img src="${q.image}" class="review-q-img" alt="Traffic Sign">
            </div>
          ` : ''}

          <div class="review-options-grid">
            ${opts.map((optText, optIdx) => {
              let optClass = "";
              let optBadge = optIdx + 1;
              let suffixTag = "";

              if (optIdx === correctIdx) {
                optClass = "official-correct";
                suffixTag = `<span style="margin-left: auto; font-size: 0.78rem; color: #166534; font-weight: 700;">✓ Correct Answer</span>`;
              } else if (optIdx === userChoice && !isCorrect) {
                optClass = "user-chosen-wrong";
                suffixTag = `<span style="margin-left: auto; font-size: 0.78rem; color: #991B1B; font-weight: 700;">✗ Your Choice</span>`;
              } else if (optIdx === userChoice && isCorrect) {
                suffixTag = `<span style="margin-left: auto; font-size: 0.78rem; color: #166534; font-weight: 700;">✓ Your Choice</span>`;
              }

              return `
                <div class="review-opt ${optClass}">
                  <div class="review-opt-badge">${optBadge}</div>
                  <div>${optText}</div>
                  ${suffixTag}
                </div>
              `;
            }).join("")}
          </div>

          <div class="review-explanation">
            <strong>💡 Official Rule / Explanation:</strong> ${qExp}
          </div>
        </div>
      `;
    });

    reviewList.innerHTML = html;
  }

  buildCards("all");

  // Wire up review filter pills
  document.querySelectorAll(".review-filter-btn").forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll(".review-filter-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const filter = btn.getAttribute("data-review-filter");
      buildCards(filter);
    };
  });
}

// ==========================================
// 2. TOPIC PRACTICE UI
// ==========================================
function initPracticeUI() {
  const container = document.getElementById("practice-active-q-view");
  const matrix = document.getElementById("practice-matrix");
  const searchInput = document.getElementById("practice-search-input");
  const statusFilter = document.getElementById("practice-status-filter");

  // Category filter buttons
  document.querySelectorAll("[data-practice-cat]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll("[data-practice-cat]").forEach(b => {
        b.style.background = "#F1F5F9";
        b.style.color = "#334155";
      });
      btn.style.background = "var(--secondary-blue)";
      btn.style.color = "#FFFFFF";
      practice.setCategory(btn.getAttribute("data-practice-cat"));
    });
  });

  statusFilter?.addEventListener("change", e => {
    practice.setFilter(e.target.value);
  });

  searchInput?.addEventListener("input", e => {
    practice.setSearch(e.target.value);
  });

  practice.onStateChange = state => {
    updateReadinessMeter();
    renderPracticeMatrix(state.filteredQuestions);
    renderPracticeCard(state.selectedQuestion);
  };
}

function renderPracticeMatrix(filteredList) {
  const matrix = document.getElementById("practice-matrix");
  if (!matrix) return;
  matrix.innerHTML = "";

  filteredList.forEach(q => {
    const qState = storage.getQuestionState(q.id);
    const chip = document.createElement("button");
    chip.textContent = q.questionNumber;
    chip.title = `Q${q.questionNumber}: ${q.id} (Status: ${qState.status}, Streak: ${qState.streak})`;

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
      chip.style.border = "2px solid #2563EB";
      chip.style.transform = "scale(1.1)";
    } else {
      chip.style.border = "1px solid #CBD5E1";
    }

    chip.style.background = bg;
    chip.style.color = color;
    chip.style.borderRadius = "4px";
    chip.style.padding = "4px 8px";
    chip.style.fontSize = "0.78rem";
    chip.style.fontWeight = "600";
    chip.style.cursor = "pointer";

    chip.addEventListener("click", () => {
      practice.selectQuestion(q.id);
    });

    matrix.appendChild(chip);
  });
}

function renderPracticeCard(q) {
  const container = document.getElementById("practice-active-q-view");
  if (!container || !q) return;

  const lang = getCurrentLang();
  const qState = storage.getQuestionState(q.id);

  let statusBadge = `<span style="background: #F1F5F9; color: #475569; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">UNSEEN</span>`;
  if (qState.status === "mastered") {
    statusBadge = `<span style="background: #DCFCE7; color: #166534; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">MASTERED (Streak: ${qState.streak})</span>`;
  } else if (qState.status === "probation") {
    statusBadge = `<span style="background: #FEF3C7; color: #92400E; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">NEEDS PRACTICE (Streak: ${qState.streak})</span>`;
  }

  let imgHtml = "";
  if (q.image) {
    imgHtml = `
      <div style="text-align: center; margin: 12px 0;">
        <img src="${q.image}" alt="Sign / Scenario" style="max-height: 150px; object-fit: contain; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      </div>
    `;
  }

  const opts = q.options[lang] || q.options.en;
  let optionsHtml = `<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px;">`;
  opts.forEach((optText, idx) => {
    optionsHtml += `
      <button class="practice-opt-btn" data-opt-idx="${idx}" style="text-align: left; background: #FFFFFF; border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 10px 12px; cursor: pointer; font-size: 0.92rem; font-weight: 500; display: flex; align-items: center; gap: 8px; transition: all 0.2s;">
        <span style="width: 26px; height: 26px; border-radius: 50%; background: #F1F5F9; border: 1px solid #CBD5E1; display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700; flex-shrink: 0;">${idx + 1}</span>
        <span>${optText}</span>
      </button>
    `;
  });
  optionsHtml += `</div>`;

  const expText = q.explanation[lang] || q.explanation.en || "";

  container.innerHTML = `
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
      <span style="font-weight: 700; color: var(--secondary-blue); font-size: 0.88rem;">${q.id} • Question ${q.questionNumber}</span>
      <div>${statusBadge}</div>
    </div>
    <h3 style="font-size: 1.15rem; color: var(--text-primary); margin-bottom: 8px;">${q.text[lang] || q.text.en}</h3>
    ${imgHtml}
    ${optionsHtml}
    <div id="practice-explanation-box" style="display: none; margin-top: 14px; background: #EFF6FF; border-left: 4px solid var(--secondary-blue); padding: 12px; border-radius: 4px; font-size: 0.9rem; color: #1E293B;">
      <strong>Explanation:</strong> ${expText}
    </div>
  `;

  // Attach option click handlers
  container.querySelectorAll(".practice-opt-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const idx = parseInt(btn.getAttribute("data-opt-idx"), 10);
      const isCorrect = idx === q.answerIndex;

      container.querySelectorAll(".practice-opt-btn").forEach((b, bIdx) => {
        b.disabled = true;
        if (bIdx === q.answerIndex) {
          b.style.borderColor = "#22C55E";
          b.style.background = "#DCFCE7";
        } else if (bIdx === idx && !isCorrect) {
          b.style.borderColor = "#EF4444";
          b.style.background = "#FEE2E2";
        }
      });

      const expBox = document.getElementById("practice-explanation-box");
      if (expBox) expBox.style.display = "block";

      practice.answerPracticeQuestion(q.id, idx, false);
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

  cardBox?.addEventListener("click", () => {
    flashcards.flipCard();
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
      document.querySelectorAll("[data-fc-filter]").forEach(b => {
        b.style.background = "#F1F5F9";
        b.style.color = "#334155";
      });
      btn.style.background = "var(--secondary-blue)";
      btn.style.color = "#FFFFFF";
      flashcards.setFilter(btn.getAttribute("data-fc-filter"));
    });
  });

  flashcards.onStateChange = state => {
    updateReadinessMeter();
    const frontView = document.getElementById("fc-front-view");
    const backView = document.getElementById("fc-back-view");
    const img = document.getElementById("fc-image");
    const typeBadge = document.getElementById("fc-type-badge");
    const signName = document.getElementById("fc-sign-name");
    const signDesc = document.getElementById("fc-sign-desc");
    const counter = document.getElementById("fc-counter");

    if (counter) counter.textContent = `Card ${state.currentIndex + 1} of ${state.total}`;

    const sign = state.currentSign;
    if (!sign) return;

    const lang = getCurrentLang();
    const name = sign.options[lang] ? sign.options[lang][sign.answerIndex] : sign.options.en[sign.answerIndex];
    const desc = sign.explanation[lang] || sign.explanation.en;

    if (img) img.src = sign.image;
    if (typeBadge) typeBadge.textContent = (sign.signType || "ROAD SIGN").toUpperCase();
    if (signName) signName.textContent = name;
    if (signDesc) signDesc.textContent = desc;

    if (state.isFlipped) {
      if (frontView) frontView.style.display = "none";
      if (backView) backView.style.display = "flex";
    } else {
      if (frontView) frontView.style.display = "flex";
      if (backView) backView.style.display = "none";
    }
  };
}

// ==========================================
// 4. TRICKY TWINS RENDERER
// ==========================================
function renderTrickyTwins() {
  const container = document.getElementById("twins-container");
  if (!container || !trickyTwins.length) return;

  const lang = getCurrentLang();
  container.innerHTML = "";

  trickyTwins.forEach(pair => {
    const card = document.createElement("div");
    card.style.background = "#FFFFFF";
    card.style.border = "1px solid var(--border-color)";
    card.style.borderRadius = "var(--radius-lg)";
    card.style.padding = "20px";
    card.style.boxShadow = "var(--shadow-md)";

    const titleText = pair.title[lang] || pair.title.en;

    card.innerHTML = `
      <h3 style="font-size: 1.15rem; color: var(--primary-navy); margin-bottom: 14px; font-weight: 700; border-bottom: 2px solid var(--border-color); padding-bottom: 8px;">${titleText}</h3>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
        <!-- Sign A -->
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; text-align: center;">
          <img src="${pair.signA.image}" alt="${pair.signA.name.en}" style="max-height: 90px; object-fit: contain; margin-bottom: 8px;">
          <strong style="display: block; font-size: 0.9rem; color: var(--text-primary); margin-bottom: 4px;">${pair.signA.name[lang] || pair.signA.name.en}</strong>
          <p style="font-size: 0.8rem; color: var(--text-secondary); text-align: left; line-height: 1.35;">${pair.signA.rule[lang] || pair.signA.rule.en}</p>
        </div>

        <!-- Sign B -->
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 12px; text-align: center;">
          <img src="${pair.signB.image}" alt="${pair.signB.name.en}" style="max-height: 90px; object-fit: contain; margin-bottom: 8px;">
          <strong style="display: block; font-size: 0.9rem; color: var(--text-primary); margin-bottom: 4px;">${pair.signB.name[lang] || pair.signB.name.en}</strong>
          <p style="font-size: 0.8rem; color: var(--text-secondary); text-align: left; line-height: 1.35;">${pair.signB.rule[lang] || pair.signB.rule.en}</p>
        </div>
      </div>
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
  container.innerHTML = "";

  const title = cheatsheet.title[lang] || cheatsheet.title.en;

  let rulesHtml = `<ol style="padding-left: 20px; display: flex; flex-direction: column; gap: 12px;">`;
  cheatsheet.goldenRules.forEach(gr => {
    const text = gr.rule[lang] || gr.rule.en;
    rulesHtml += `<li style="font-size: 0.98rem; color: var(--text-primary); line-height: 1.45;">${text}</li>`;
  });
  rulesHtml += `</ol>`;

  container.innerHTML = `
    <h2 style="font-size: 1.35rem; color: var(--primary-navy); margin-bottom: 12px; font-weight: 800;">⚡ ${title}</h2>
    <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 18px;">Read these essential golden rules in 10 minutes right before entering the RTO examination room.</p>
    ${rulesHtml}
  `;
}

// ==========================================
// 6. HYDERABAD RTO GUIDE RENDERER
// ==========================================
function renderRtoGuide() {
  const container = document.getElementById("rto-guide-container");
  if (!container || !rtoGuide) return;

  container.innerHTML = `
    <h2 style="font-size: 1.35rem; color: var(--primary-navy); margin-bottom: 8px; font-weight: 800;">🏢 ${rtoGuide.title}</h2>
    <p style="color: var(--text-secondary); margin-bottom: 20px;">Detailed test-day walkthrough for Hyderabad & Telangana RTA testing centres.</p>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
      <!-- Checklist -->
      <div style="background: #F8FAFC; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px;">
        <h3 style="font-size: 1.05rem; color: var(--secondary-blue); margin-bottom: 10px; font-weight: 700;">📋 What to Carry</h3>
        <ul style="padding-left: 18px; font-size: 0.88rem; color: var(--text-secondary); display: flex; flex-direction: column; gap: 6px;">
          ${(rtoGuide.checklist || []).map(item => `<li>${item}</li>`).join("")}
        </ul>
      </div>

      <!-- Test Center Workflow -->
      <div style="background: #F8FAFC; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px;">
        <h3 style="font-size: 1.05rem; color: var(--secondary-blue); margin-bottom: 10px; font-weight: 700;">🏛️ Testing Room Workflow</h3>
        <ol style="padding-left: 18px; font-size: 0.88rem; color: var(--text-secondary); display: flex; flex-direction: column; gap: 6px;">
          ${(rtoGuide.steps || rtoGuide.workflow || []).map(step => `<li>${step}</li>`).join("")}
        </ol>
      </div>

      <!-- Common Pitfalls -->
      <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-radius: var(--radius-md); padding: 16px;">
        <h3 style="font-size: 1.05rem; color: #92400E; margin-bottom: 10px; font-weight: 700;">⚠️ Common Pitfalls to Avoid</h3>
        <ul style="padding-left: 18px; font-size: 0.88rem; color: #78350F; display: flex; flex-direction: column; gap: 6px;">
          ${(rtoGuide.topTips || rtoGuide.commonPitfalls || []).map(item => `<li>${item}</li>`).join("")}
        </ul>
      </div>
    </div>
  `;
}
