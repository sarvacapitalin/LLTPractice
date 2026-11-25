// js/practice-engine.js - Topic Practice & 412 Questions Interactive Explorer
import { storage } from "./storage-engine.js";
import { sounds } from "./sound-effects.js";
import { speech } from "./speech-engine.js";
import { getCurrentLang } from "./i18n.js";

export class PracticeEngine {
  constructor(allQuestions = []) {
    this.questions = allQuestions;
    this.activeCategory = "all"; // 'all', 'road_signs', 'rules_of_road', 'general_principles'
    this.activeFilter = "all"; // 'all', 'unseen', 'probation', 'mastered', 'guessed'
    this.searchQuery = "";
    this.selectedQuestion = null;
    this.lastAnswers = {}; // questionId -> { selectedIndex, isCorrect }
    this.onStateChange = null;
  }

  setQuestions(allQuestions) {
    this.questions = allQuestions;
    this._syncSelectedQuestion();
    this.notifyUpdate();
  }

  setCategory(category) {
    this.activeCategory = category;
    this._syncSelectedQuestion();
    this.notifyUpdate();
  }

  setFilter(filter) {
    this.activeFilter = filter;
    this._syncSelectedQuestion();
    this.notifyUpdate();
  }

  setSearch(query) {
    this.searchQuery = query.toLowerCase().trim();
    this._syncSelectedQuestion();
    this.notifyUpdate();
  }

  _syncSelectedQuestion() {
    const filtered = this.getFilteredQuestions();
    if (filtered.length === 0) {
      this.selectedQuestion = null;
    } else if (!this.selectedQuestion || !filtered.some(q => q.id === this.selectedQuestion.id)) {
      this.selectedQuestion = filtered[0];
    }
  }

  selectQuestion(qId) {
    const found = this.questions.find(q => q.id === qId);
    if (found) {
      this.selectedQuestion = found;
      this.notifyUpdate("select");
    }
  }

  getSelectedPosition() {
    const filtered = this.getFilteredQuestions();
    if (!this.selectedQuestion || filtered.length === 0) {
      return { index: -1, total: filtered.length };
    }
    const index = filtered.findIndex(q => q.id === this.selectedQuestion.id);
    return { index, total: filtered.length };
  }

  prevQuestion() {
    const filtered = this.getFilteredQuestions();
    const { index } = this.getSelectedPosition();
    if (index > 0) {
      this.selectedQuestion = filtered[index - 1];
      speech.stop();
      this.notifyUpdate("select");
    }
  }

  nextQuestion() {
    const filtered = this.getFilteredQuestions();
    const { index } = this.getSelectedPosition();
    if (index >= 0 && index < filtered.length - 1) {
      this.selectedQuestion = filtered[index + 1];
      speech.stop();
      this.notifyUpdate("select");
    }
  }

  selectNextUnseen() {
    const filtered = this.getFilteredQuestions();
    if (filtered.length === 0) return false;
    const { index } = this.getSelectedPosition();
    const start = index >= 0 ? index + 1 : 0;

    for (let offset = 0; offset < filtered.length; offset++) {
      const candidate = filtered[(start + offset) % filtered.length];
      const st = storage.getQuestionState(candidate.id);
      if (st.status !== "mastered") {
        this.selectedQuestion = candidate;
        speech.stop();
        this.notifyUpdate("select");
        return true;
      }
    }
    return false;
  }

  readCurrentQuestion() {
    const q = this.selectedQuestion;
    if (!q) return;
    const lang = getCurrentLang();
    const qText = q.text[lang] || q.text.en;
    const qOpts = q.options[lang] || q.options.en;
    speech.toggleQuestionSpeech(qText, qOpts, lang);
  }

  getFilteredQuestions() {
    const lang = getCurrentLang();
    return this.questions.filter(q => {
      // Category filter
      if (this.activeCategory !== "all" && q.category !== this.activeCategory) {
        return false;
      }

      // Status filter
      const state = storage.getQuestionState(q.id);
      if (this.activeFilter === "unseen" && state.status !== "unseen") return false;
      if (this.activeFilter === "probation" && state.status !== "probation") return false;
      if (this.activeFilter === "mastered" && state.status !== "mastered") return false;
      if (this.activeFilter === "guessed" && !state.isGuessed) return false;

      // Search query
      if (this.searchQuery) {
        const text = (q.text[lang] || q.text.en || "").toLowerCase();
        const enText = (q.text.en || "").toLowerCase();
        const id = q.id.toLowerCase();
        const qNum = String(q.questionNumber);
        if (
          !text.includes(this.searchQuery) &&
          !enText.includes(this.searchQuery) &&
          !id.includes(this.searchQuery) &&
          qNum !== this.searchQuery
        ) {
          return false;
        }
      }

      return true;
    });
  }

  answerPracticeQuestion(questionId, selectedIndex, isGuessed = false) {
    const q = this.questions.find(item => item.id === questionId);
    if (!q) return;

    const isCorrect = selectedIndex === q.answerIndex;
    if (isCorrect) sounds.playSuccess();
    else sounds.playFail();

    this.lastAnswers[questionId] = { selectedIndex, isCorrect };

    storage.recordAttempt(questionId, isCorrect, isGuessed);
    this.notifyUpdate("answer");
    return isCorrect;
  }

  notifyUpdate(reason = "update") {
    if (reason !== "answer") {
      this._syncSelectedQuestion();
    }
    if (this.onStateChange) {
      this.onStateChange({
        filteredQuestions: this.getFilteredQuestions(),
        selectedQuestion: this.selectedQuestion,
        activeCategory: this.activeCategory,
        activeFilter: this.activeFilter,
        reason
      });
    }
  }
}

export const practice = new PracticeEngine();
