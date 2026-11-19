// js/flashcards-engine.js - 94 Road Signs Interactive Flip Card Drills
import { storage } from "./storage-engine.js";
import { sounds } from "./sound-effects.js";
import { speech } from "./speech-engine.js";
import { getCurrentLang } from "./i18n.js";

export class FlashcardsEngine {
  constructor(signs = []) {
    this.signs = signs;
    this.currentIndex = 0;
    this.isFlipped = false;
    this.activeFilter = "all"; // 'all', 'mandatory', 'cautionary', 'informatory', 'unmastered'
    this.onStateChange = null;
  }

  setSigns(signs) {
    this.signs = signs;
    this.notifyUpdate();
  }

  getFilteredSigns() {
    return this.signs.filter(s => {
      if (this.activeFilter === "all") return true;
      if (this.activeFilter === "unmastered") {
        const state = storage.getQuestionState(s.id);
        return state.status !== "mastered";
      }
      return s.signType === this.activeFilter;
    });
  }

  setFilter(filter) {
    this.activeFilter = filter;
    this.currentIndex = 0;
    this.isFlipped = false;
    this.notifyUpdate();
  }

  flipCard() {
    this.isFlipped = !this.isFlipped;
    sounds.playSelect();
    this.notifyUpdate();
  }

  nextCard() {
    const list = this.getFilteredSigns();
    if (this.currentIndex < list.length - 1) {
      this.currentIndex += 1;
      this.isFlipped = false;
      this.notifyUpdate();
    }
  }

  prevCard() {
    if (this.currentIndex > 0) {
      this.currentIndex -= 1;
      this.isFlipped = false;
      this.notifyUpdate();
    }
  }

  markMastered(signId) {
    storage.recordAttempt(signId, true, false);
    // require streak 2
    storage.recordAttempt(signId, true, false);
    sounds.playSuccess();
    this.nextCard();
  }

  markNeedsPractice(signId) {
    storage.recordAttempt(signId, false, false);
    sounds.playFail();
    this.nextCard();
  }

  readCurrentSign() {
    const list = this.getFilteredSigns();
    const sign = list[this.currentIndex];
    if (!sign) return;
    const lang = getCurrentLang();
    const name = sign.options[lang] ? sign.options[lang][sign.answerIndex] : sign.options.en[sign.answerIndex];
    const exp = sign.explanation[lang] || sign.explanation.en;
    speech.readQuestion(name, [exp], lang);
  }

  notifyUpdate() {
    if (this.onStateChange) {
      const list = this.getFilteredSigns();
      this.onStateChange({
        currentSign: list[this.currentIndex] || null,
        currentIndex: this.currentIndex,
        total: list.length,
        isFlipped: this.isFlipped,
        activeFilter: this.activeFilter
      });
    }
  }
}

export const flashcards = new FlashcardsEngine();
