// js/exam-engine.js - Authentic Telangana STALL Computerized Exam Simulator
import { storage } from "./storage-engine.js";
import { sounds } from "./sound-effects.js";
import { speech } from "./speech-engine.js";
import { coverage } from "./coverage-engine.js";
import { t, getCurrentLang } from "./i18n.js";

export class ExamEngine {
  constructor() {
    this.questions = [];
    this.currentIndex = 0;
    this.selectedOption = null;
    this.timer = null;
    this.timeLeft = 30;
    this.correctCount = 0;
    this.wrongCount = 0;
    this.history = []; // records per question
    this.isActive = false;
    this.isFinished = false;
    this.isCustom = false;
    this.tutorMode = false; // When true: instant right/wrong feedback on submit
    this.isRevealed = false; // When true in tutorMode: answer is currently revealed
    this.onStateUpdate = null; // UI callback
  }

  setTutorMode(enabled) {
    this.tutorMode = Boolean(enabled);
  }

  shuffleQuestionOptions(q) {
    if (!q || !q.options) return q;
    const opts = q.options.en || (Array.isArray(q.options) ? q.options : null);
    if (!opts || opts.length < 2) return q;

    const n = opts.length;
    const indices = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [indices[i], indices[j]] = [indices[j], indices[i]];
    }

    const newAnswerIndex = indices.indexOf(q.answerIndex);

    let newOptions;
    if (Array.isArray(q.options)) {
      newOptions = indices.map(i => q.options[i]);
    } else {
      newOptions = {};
      for (const [lang, arr] of Object.entries(q.options)) {
        if (Array.isArray(arr)) {
          newOptions[lang] = indices.map(i => arr[i] || "");
        } else {
          newOptions[lang] = arr;
        }
      }
    }

    return {
      ...q,
      options: newOptions,
      answerIndex: newAnswerIndex,
      originalAnswerIndex: q.answerIndex
    };
  }

  startNewExam() {
    const sampled = coverage.sampleMockExamQuestions();

    // Guard: if questions failed to load, don't start
    if (!sampled || sampled.length === 0) {
      console.error("[ExamEngine] startNewExam: No questions available — datasets not loaded!");
      this.isActive = false;
      this.isFinished = false;
      this.notifyUpdate();
      return;
    }

    // Maintain authentic STALL fixed option sequence (1, 2, 3, 4) matching physical kiosk keys
    // and official government answer explanations, with optional toggle via user preference
    const shouldShuffle = storage.getPreference("shuffleOptions", false);
    this.questions = shouldShuffle ? sampled.map(q => this.shuffleQuestionOptions(q)) : sampled.slice();

    this.currentIndex = 0;
    this.selectedOption = null;
    this.correctCount = 0;
    this.wrongCount = 0;
    this.history = [];
    this.isActive = true;
    this.isFinished = false;
    this.isCustom = false;
    this.isRevealed = false;

    this.startQuestion();
  }

  startCustomExam(customQuestions) {
    if (!customQuestions || customQuestions.length === 0) return;
    const shouldShuffle = storage.getPreference("shuffleOptions", false);
    this.questions = shouldShuffle ? customQuestions.map(q => this.shuffleQuestionOptions(q)) : customQuestions.slice();
    this.currentIndex = 0;
    this.selectedOption = null;
    this.correctCount = 0;
    this.wrongCount = 0;
    this.history = [];
    this.isActive = true;
    this.isFinished = false;
    this.isCustom = true;
    this.isRevealed = false;

    this.startQuestion();
  }

  startQuestion() {
    this.isRevealed = false;
    if (this.currentIndex >= this.questions.length) {
      this.finishExam("completed");
      return;
    }

    const totalQs = this.questions.length;
    const passThreshold = this.isCustom ? Math.max(1, Math.ceil(totalQs * 0.6)) : 12;
    const failThreshold = this.isCustom ? (totalQs - passThreshold + 1) : 9;

    // Check early stopping rule:
    if (this.correctCount >= passThreshold) {
      this.finishExam("early_pass");
      return;
    }
    if (this.wrongCount >= failThreshold) {
      this.finishExam("early_fail");
      return;
    }

    this.selectedOption = null;
    this.timeLeft = 30;

    // Start 30s countdown timer FIRST to guarantee ticking even if UI render encounters an edge case
    clearInterval(this.timer);
    this.timer = setInterval(() => {
      this.timeLeft -= 1;
      if (this.timeLeft <= 5) {
        sounds.playTick();
      }

      if (this.timeLeft <= 0) {
        clearInterval(this.timer);
        this.handleTimeout();
      } else {
        try {
          this.notifyUpdate();
        } catch (err) {
          console.error("Error in timer notifyUpdate:", err);
        }
      }
    }, 1000);

    // Initial UI render notification
    try {
      this.notifyUpdate();
    } catch (err) {
      console.error("Error in startQuestion notifyUpdate:", err);
    }

    // Auto-read if user enabled voice
    if (storage.getPreference("autoSpeech", false)) {
      try {
        this.readCurrentQuestion();
      } catch (e) {
        console.warn("Speech reader:", e);
      }
    }
  }

  selectOption(index) {
    if (!this.isActive || this.isFinished || this.isRevealed) return;
    this.selectedOption = index;
    sounds.playSelect();
    this.notifyUpdate();
  }

  confirmAndSubmit(isGuessed = false) {
    if (this.selectedOption === null || !this.isActive) return;
    if (this.isRevealed) {
      // In tutorMode when already revealed, clicking confirm acts as Continue
      this.continueToNext();
      return;
    }

    clearInterval(this.timer);
    speech.stop();

    const currentQ = this.questions[this.currentIndex];
    const isCorrect = this.selectedOption === currentQ.answerIndex;

    // Record in storage engine
    storage.recordAttempt(currentQ.id, isCorrect, isGuessed);

    if (isCorrect) {
      this.correctCount += 1;
      sounds.playSuccess();
    } else {
      this.wrongCount += 1;
      sounds.playFail();
    }

    this.history.push({
      question: currentQ,
      selected: this.selectedOption,
      isCorrect,
      isGuessed,
      timeLeft: this.timeLeft
    });

    if (this.tutorMode) {
      // Pause on current question to show correct/wrong highlight & explanation
      this.isRevealed = true;
      this.notifyUpdate();
    } else {
      // Normal exam mode: instantly advance to next question
      this.currentIndex += 1;
      this.startQuestion();
    }
  }

  continueToNext() {
    if (!this.isActive || this.isFinished) return;
    this.isRevealed = false;
    this.currentIndex += 1;
    this.startQuestion();
  }

  handleTimeout() {
    speech.stop();
    const currentQ = this.questions[this.currentIndex];
    sounds.playFail();

    // Timeout is counted as incorrect
    this.wrongCount += 1;
    storage.recordAttempt(currentQ.id, false, false);

    this.history.push({
      question: currentQ,
      selected: null,
      isCorrect: false,
      isGuessed: false,
      timeLeft: 0,
      timeout: true
    });

    this.currentIndex += 1;
    this.startQuestion();
  }

  finishExam(reason) {
    clearInterval(this.timer);
    speech.stop();
    this.isActive = false;
    this.isFinished = true;

    const totalQs = this.questions.length;
    const passThreshold = this.isCustom ? Math.max(1, Math.ceil(totalQs * 0.6)) : 12;
    const passed = this.correctCount >= passThreshold;
    if (passed) {
      sounds.playSuccess();
    } else {
      sounds.playFail();
    }

    // Tally by category
    let signsCorrect = 0;
    let rulesCorrect = 0;
    let principlesCorrect = 0;

    this.history.forEach(item => {
      if (item.isCorrect) {
        if (item.question.category === "road_signs") signsCorrect += 1;
        else if (item.question.category === "rules_of_road") rulesCorrect += 1;
        else if (item.question.category === "general_principles") principlesCorrect += 1;
      }
    });

    storage.recordExamResult({
      score: this.correctCount,
      total: Math.min(this.questions.length, this.history.length),
      passed,
      signsCorrect,
      rulesCorrect,
      principlesCorrect,
      details: this.history.map(h => ({
        id: h.question.id,
        isCorrect: h.isCorrect,
        isGuessed: h.isGuessed
      }))
    });

    this.notifyUpdate();
  }

  readCurrentQuestion() {
    const q = this.questions[this.currentIndex];
    if (!q) return;
    const lang = getCurrentLang();
    const qText = q.text[lang] || q.text.en;
    const qOpts = q.options[lang] || q.options.en;
    speech.readQuestion(qText, qOpts, lang);
  }

  notifyUpdate() {
    if (this.onStateUpdate) {
      this.onStateUpdate(this.getStateSnapshot());
    }
  }

  getStateSnapshot() {
    const currentQ = this.questions[this.currentIndex] || null;
    const totalQs = this.questions.length;
    const passThreshold = this.isCustom ? Math.max(1, Math.ceil(totalQs * 0.6)) : 12;
    const passed = this.correctCount >= passThreshold;

    return {
      isActive: this.isActive,
      isFinished: this.isFinished,
      isCustom: this.isCustom,
      passThreshold,
      currentIndex: this.currentIndex,
      totalQuestions: totalQs,
      currentQuestion: currentQ,
      selectedOption: this.selectedOption,
      timeLeft: this.timeLeft,
      correctCount: this.correctCount,
      wrongCount: this.wrongCount,
      passed,
      tutorMode: this.tutorMode,
      isRevealed: this.isRevealed,
      history: this.history
    };
  }
}

export const exam = new ExamEngine();
