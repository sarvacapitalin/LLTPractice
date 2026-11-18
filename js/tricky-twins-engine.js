// js/tricky-twins-engine.js - Confusing Road Signs Comparison Engine
import { getCurrentLang } from "./i18n.js";

export class TrickyTwinsEngine {
  constructor(twinsData = []) {
    this.twins = twinsData;
  }

  setTwins(twinsData) {
    this.twins = twinsData;
  }

  getPairs() {
    return this.twins;
  }

  getPairById(id) {
    return this.twins.find(p => p.id === id);
  }
}

export const trickyTwins = new TrickyTwinsEngine();
