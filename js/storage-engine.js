// js/storage-engine.js - LocalStorage State Machine & 2-Streak Mastery Manager

const STORAGE_KEY = "TS_LLR_PRACTICE_STATE_V1";

export class StorageEngine {
  constructor() {
    this.state = this.loadState();
  }

  getDefaultState() {
    return {
      version: 1,
      lastUpdated: new Date().toISOString(),
      // questions[id] = { attempts: int, correct: int, streak: int, isGuessed: bool, lastAnswered: ISO, status: 'unseen'|'probation'|'mastered' }
      questions: {},
      examHistory: [],
      preferences: {
        language: "en",
        soundEnabled: true,
        autoSpeech: false
      }
    };
  }

  loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return this.getDefaultState();
      const parsed = JSON.parse(raw);
      if (!parsed.questions) parsed.questions = {};
      if (!parsed.examHistory) parsed.examHistory = [];
      if (!parsed.preferences) parsed.preferences = { language: "en", soundEnabled: true, autoSpeech: false };
      return parsed;
    } catch (e) {
      console.warn("Error reading localStorage, using default:", e);
      return this.getDefaultState();
    }
  }

  saveState() {
    try {
      this.state.lastUpdated = new Date().toISOString();
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.state));
    } catch (e) {
      console.error("Failed to save state to localStorage:", e);
    }
  }

  /**
   * Records an attempt on a question with 2-Streak Mastery rule:
   * - Correct answer with isGuessed = false: streak += 1.
   * - Correct answer with isGuessed = true: streak stays at 1 (probation, does not advance to mastered).
   * - Incorrect answer: streak resets to 0 (probation).
   * - Status:
   *   - streak >= 2 -> 'mastered'
   *   - streak == 1 -> 'probation'
   *   - attempts == 0 -> 'unseen'
   *   - streak == 0 && attempts > 0 -> 'probation'
   */
  recordAttempt(questionId, isCorrect, isGuessed = false) {
    if (!this.state.questions[questionId]) {
      this.state.questions[questionId] = {
        attempts: 0,
        correct: 0,
        streak: 0,
        isGuessed: false,
        lastAnswered: null,
        status: "unseen"
      };
    }

    const q = this.state.questions[questionId];
    q.attempts += 1;
    q.lastAnswered = new Date().toISOString();

    if (isCorrect) {
      q.correct += 1;
      if (isGuessed) {
        // Guessed right: keep on probation (streak capped at 1)
        q.isGuessed = true;
        q.streak = Math.min(q.streak + 1, 1);
        q.status = "probation";
      } else {
        q.isGuessed = false;
        q.streak += 1;
        q.status = q.streak >= 2 ? "mastered" : "probation";
      }
    } else {
      q.isGuessed = false;
      q.streak = 0;
      q.status = "probation";
    }

    this.saveState();
    return q;
  }

  getQuestionState(questionId) {
    return this.state.questions[questionId] || {
      attempts: 0,
      correct: 0,
      streak: 0,
      isGuessed: false,
      lastAnswered: null,
      status: "unseen"
    };
  }

  recordExamResult(examRecord) {
    this.state.examHistory.push({
      date: new Date().toISOString(),
      score: examRecord.score,
      total: examRecord.total,
      passed: examRecord.passed,
      signsCorrect: examRecord.signsCorrect,
      rulesCorrect: examRecord.rulesCorrect,
      principlesCorrect: examRecord.principlesCorrect,
      details: examRecord.details
    });
    this.saveState();
  }

  getPreference(key, defaultVal) {
    if (!this.state.preferences) {
      this.state.preferences = { language: "en", soundEnabled: true, autoSpeech: false };
    }
    return this.state.preferences[key] !== undefined ? this.state.preferences[key] : defaultVal;
  }

  setPreference(key, val) {
    if (!this.state.preferences) {
      this.state.preferences = { language: "en", soundEnabled: true, autoSpeech: false };
    }
    this.state.preferences[key] = val;
    this.saveState();
  }

  /**
   * Resets all question progress and streaks back to 0 (Fresh Start).
   * Preserves language preferences.
   */
  resetReadiness() {
    this.state.questions = {};
    this.state.examHistory = [];
    this.saveState();
  }

  exportStateJson() {
    return JSON.stringify(this.state, null, 2);
  }

  importStateJson(jsonString) {
    try {
      const parsed = JSON.parse(jsonString);
      if (parsed && typeof parsed === "object" && parsed.questions && typeof parsed.questions === "object") {
        const mergedPrefs = Object.assign(
          { language: "en", soundEnabled: true, autoSpeech: false },
          (parsed.preferences && typeof parsed.preferences === "object") ? parsed.preferences : {}
        );
        // Keep language locked to English while Telugu/Hindi translations are suspended
        mergedPrefs.language = "en";
        this.state = {
          version: parsed.version || 1,
          lastUpdated: parsed.lastUpdated || new Date().toISOString(),
          questions: parsed.questions || {},
          examHistory: Array.isArray(parsed.examHistory) ? parsed.examHistory : [],
          preferences: mergedPrefs
        };
        this.saveState();
        return true;
      }
      return false;
    } catch (e) {
      console.error("Invalid state JSON imported:", e);
      return false;
    }
  }
}

export const storage = new StorageEngine();
