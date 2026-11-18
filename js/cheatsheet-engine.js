// js/cheatsheet-engine.js - Rapid 10-Minute Morning Revision Cheatsheet Engine
import { getCurrentLang } from "./i18n.js";

export class CheatsheetEngine {
  constructor(cheatsheetData = null) {
    this.data = cheatsheetData;
  }

  setData(cheatsheetData) {
    this.data = cheatsheetData;
  }

  getGoldenRules() {
    return this.data ? this.data.goldenRules : [];
  }
}

export const cheatsheetEngine = new CheatsheetEngine();
