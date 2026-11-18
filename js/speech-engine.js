// js/speech-engine.js - Web Speech API Voice Reader
export class SpeechEngine {
  constructor() {
    this.synth = window.speechSynthesis;
    this.isReading = false;
    this.onStateChange = null;
    this.langMap = {
      en: "en-IN",
      te: "te-IN",
      hi: "hi-IN"
    };
  }

  isSupported() {
    return 'speechSynthesis' in window;
  }

  stop() {
    if (this.synth) {
      this.synth.cancel();
      this.isReading = false;
      if (this.onStateChange) this.onStateChange(false);
    }
  }

  readQuestion(questionText, options, langCode = 'en') {
    if (!this.isSupported() || !this.synth) return;
    this.stop();

    const targetLang = this.langMap[langCode] || "en-IN";
    let speechScript = `${questionText}. `;
    if (options && options.length) {
      options.forEach((opt, idx) => {
        speechScript += ` Option ${idx + 1}: ${opt}. `;
      });
    }

    const utterance = new SpeechSynthesisUtterance(speechScript);
    utterance.lang = targetLang;
    utterance.rate = 0.95; // Slightly slower for clarity

    // Try to pick an Indian English/Telugu/Hindi voice if available
    const voices = this.synth.getVoices();
    const matchingVoice = voices.find(v => v.lang.startsWith(targetLang) || v.lang.startsWith(langCode));
    if (matchingVoice) {
      utterance.voice = matchingVoice;
    }

    utterance.onstart = () => {
      this.isReading = true;
      if (this.onStateChange) this.onStateChange(true);
    };

    utterance.onend = () => {
      this.isReading = false;
      if (this.onStateChange) this.onStateChange(false);
    };

    utterance.onerror = () => {
      this.isReading = false;
      if (this.onStateChange) this.onStateChange(false);
    };

    this.synth.speak(utterance);
  }
}

export const speech = new SpeechEngine();
