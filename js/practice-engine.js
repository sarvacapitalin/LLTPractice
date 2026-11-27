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
    this._detachedNav = null; // Preserves Prev/Next targets when current item leaves unseen/probation on answer
    this.lastAnswers = {}; // questionId -> { selectedIndex, isCorrect }
    this.onStateChange = null;
  }

  setQuestions(allQuestions) {
    this.questions = allQuestions;
    this._detachedNav = null;
    this._syncSelectedQuestion();
    this.notifyUpdate();
  }

  setCategory(category) {
    this.activeCategory = category;
    this._detachedNav = null;
    this._syncSelectedQuestion();
    this.notifyUpdate();
  }

  setFilter(filter) {
    this.activeFilter = filter;
    this._detachedNav = null;
    this._syncSelectedQuestion();
    this.notifyUpdate();
  }

  setSearch(query) {
    this.searchQuery = query.toLowerCase().trim();
    this._detachedNav = null;
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
      this._detachedNav = null;
      this.selectedQuestion = found;
      this.notifyUpdate("select");
    }
  }

  getSelectedPosition() {
    const filtered = this.getFilteredQuestions();
    if (!this.selectedQuestion || filtered.length === 0) {
      return { index: -1, total: filtered.length, canPrev: false, canNext: false };
    }
    const index = filtered.findIndex(q => q.id === this.selectedQuestion.id);
    if (index >= 0) {
      return {
        index,
        total: filtered.length,
        canPrev: index > 0,
        canNext: index < filtered.length - 1
      };
    }
    const prevId = this._detachedNav && this._detachedNav.prevId;
    const nextId = this._detachedNav && this._detachedNav.nextId;
    const canPrev = Boolean(prevId && filtered.some(q => q.id === prevId));
    const canNext = Boolean(nextId && filtered.some(q => q.id === nextId));
    return { index: -1, total: filtered.length, canPrev, canNext };
  }

  prevQuestion() {
    const filtered = this.getFilteredQuestions();
    const { index } = this.getSelectedPosition();
    let target = null;
    if (index > 0) {
      target = filtered[index - 1];
    } else if (this._detachedNav && this._detachedNav.prevId) {
      target = filtered.find(q => q.id === this._detachedNav.prevId) || null;
    }
    if (target) {
      this._detachedNav = null;
      this.selectedQuestion = target;
      speech.stop();
      this.notifyUpdate("select");
    }
  }

  nextQuestion() {
    const filtered = this.getFilteredQuestions();
    const { index } = this.getSelectedPosition();
    let target = null;
    if (index >= 0 && index < filtered.length - 1) {
      target = filtered[index + 1];
    } else if (this._detachedNav && this._detachedNav.nextId) {
      target = filtered.find(q => q.id === this._detachedNav.nextId) || null;
    }
    if (target) {
      this._detachedNav = null;
      this.selectedQuestion = target;
      speech.stop();
      this.notifyUpdate("select");
    }
  }

  selectNextUnseen() {
    const filtered = this.getFilteredQuestions();
    if (filtered.length === 0) return false;
    const { index } = this.getSelectedPosition();
    let start = index >= 0 ? index + 1 : 0;
    if (index < 0 && this._detachedNav && this._detachedNav.nextId) {
      const nextIdx = filtered.findIndex(q => q.id === this._detachedNav.nextId);
      if (nextIdx >= 0) start = nextIdx;
    }

    for (let offset = 0; offset < filtered.length; offset++) {
      const candidate = filtered[(start + offset) % filtered.length];
      const st = storage.getQuestionState(candidate.id);
      if (st.status !== "mastered") {
        this._detachedNav = null;
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

      // Search query (matches question prompt, options, explanation, ID, or number)
      if (this.searchQuery) {
        const text = (q.text[lang] || q.text.en || "").toLowerCase();
        const enText = (q.text.en || "").toLowerCase();
        const optsText = ((q.options && (q.options[lang] || q.options.en)) || []).join(" ").toLowerCase();
        const expText = ((q.explanation && (q.explanation[lang] || q.explanation.en)) || "").toLowerCase();
        const id = q.id.toLowerCase();
        const qNum = String(q.questionNumber);
        if (
          !text.includes(this.searchQuery) &&
          !enText.includes(this.searchQuery) &&
          !optsText.includes(this.searchQuery) &&
          !expText.includes(this.searchQuery) &&
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

    const preFiltered = this.getFilteredQuestions();
    const preIndex = preFiltered.findIndex(item => item.id === questionId);

    const isCorrect = selectedIndex === q.answerIndex;
    if (isCorrect) sounds.playSuccess();
    else sounds.playFail();

    this.lastAnswers[questionId] = { selectedIndex, isCorrect };

    storage.recordAttempt(questionId, isCorrect, isGuessed);

    const postFiltered = this.getFilteredQuestions();
    const stillVisible = postFiltered.some(item => item.id === questionId);
    if (stillVisible) {
      this._detachedNav = null;
    } else if (preIndex >= 0) {
      const postIds = new Set(postFiltered.map(item => item.id));
      let prevId = null;
      for (let i = preIndex - 1; i >= 0; i--) {
        if (postIds.has(preFiltered[i].id)) {
          prevId = preFiltered[i].id;
          break;
        }
      }
      let nextId = null;
      for (let i = preIndex + 1; i < preFiltered.length; i++) {
        if (postIds.has(preFiltered[i].id)) {
          nextId = preFiltered[i].id;
          break;
        }
      }
      this._detachedNav = { prevId, nextId };
    }

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
