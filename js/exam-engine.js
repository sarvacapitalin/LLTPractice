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
    this.onStateUpdate = null; // UI callback
  }

  startNewExam() {
    this.questions = coverage.sampleMockExamQuestions();
    this.currentIndex = 0;
    this.selectedOption = null;
    this.correctCount = 0;
    this.wrongCount = 0;
    this.history = [];
    this.isActive = true;
    this.isFinished = false;

    this.startQuestion();
  }

  startQuestion() {
    if (this.currentIndex >= this.questions.length) {
      this.finishExam("completed");
      return;
    }

    // Check early stopping rule:
    // Pass if 12 correct reached
    if (this.correctCount >= 12) {
      this.finishExam("early_pass");
      return;
    }
    // Fail if 9 wrong reached (max remaining correct = 20 - wrongCount < 12)
    if (this.wrongCount >= 9) {
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
    if (!this.isActive || this.isFinished) return;
    this.selectedOption = index;
    sounds.playSelect();
    this.notifyUpdate();
  }

  confirmAndSubmit(isGuessed = false) {
    if (this.selectedOption === null || !this.isActive) return;

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

    // Move to next question or check early stopping
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

    const passed = this.correctCount >= 12;
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
    const passed = this.correctCount >= 12;

    return {
      isActive: this.isActive,
      isFinished: this.isFinished,
      currentIndex: this.currentIndex,
      totalQuestions: 20,
      currentQuestion: currentQ,
      selectedOption: this.selectedOption,
      timeLeft: this.timeLeft,
      correctCount: this.correctCount,
      wrongCount: this.wrongCount,
      passed,
      history: this.history
    };
  }
}

export const exam = new ExamEngine();
