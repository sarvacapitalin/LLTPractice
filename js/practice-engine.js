// js/practice-engine.js - Topic Practice & 412 Questions Interactive Explorer
import { storage } from "./storage-engine.js";
import { sounds } from "./sound-effects.js";
import { speech } from "./speech-engine.js";
import { t, getCurrentLang } from "./i18n.js";

export class PracticeEngine {
  constructor(allQuestions = []) {
    this.questions = allQuestions;
    this.activeCategory = "all"; // 'all', 'road_signs', 'rules_of_road', 'general_principles'
    this.activeFilter = "all"; // 'all', 'unseen', 'probation', 'mastered', 'guessed'
    this.searchQuery = "";
    this.selectedQuestion = null;
    this.onStateChange = null;
  }

  setQuestions(allQuestions) {
    this.questions = allQuestions;
    if (this.questions.length > 0 && !this.selectedQuestion) {
      this.selectedQuestion = this.questions[0];
    }
    this.notifyUpdate();
  }

  setCategory(category) {
    this.activeCategory = category;
    this.notifyUpdate();
  }

  setFilter(filter) {
    this.activeFilter = filter;
    this.notifyUpdate();
  }

  setSearch(query) {
    this.searchQuery = query.toLowerCase().trim();
    this.notifyUpdate();
  }

  selectQuestion(qId) {
    const found = this.questions.find(q => q.id === qId);
    if (found) {
      this.selectedQuestion = found;
      this.notifyUpdate();
    }
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
        const id = q.id.toLowerCase();
        const qNum = String(q.questionNumber);
        if (!text.includes(this.searchQuery) && !id.includes(this.searchQuery) && qNum !== this.searchQuery) {
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

    storage.recordAttempt(questionId, isCorrect, isGuessed);
    this.notifyUpdate();
    return isCorrect;
  }

  notifyUpdate() {
    if (this.onStateChange) {
      this.onStateChange({
        filteredQuestions: this.getFilteredQuestions(),
        selectedQuestion: this.selectedQuestion,
        activeCategory: this.activeCategory,
        activeFilter: this.activeFilter
      });
    }
  }
}

export const practice = new PracticeEngine();
