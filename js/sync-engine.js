// js/sync-engine.js - Cross-device State Synchronization
import { storage } from "./storage-engine.js";
import { createQRCodeSvg } from "./qrcode-generator.js";

export class SyncEngine {
  constructor() {
    this.onSyncComplete = null;
  }

  /**
   * Compresses localStorage question streaks into a compact payload:
   * e.g. { v: 1, q: { "TS_RS_001": [streak, attempts, isGuessed] } }
   */
  getCompactPayload() {
    const rawState = storage.state;
    const compactQuestions = {};
    for (const [id, q] of Object.entries(rawState.questions)) {
      if (q.attempts > 0) {
        // [attempts, correct, streak, isGuessed ? 1 : 0]
        compactQuestions[id] = [q.attempts, q.correct, q.streak, q.isGuessed ? 1 : 0];
      }
    }

    return JSON.stringify({
      v: 1,
      t: Date.now(),
      q: compactQuestions
    });
  }

  generateSyncQrSvg() {
    const payload = this.getCompactPayload();
    return createQRCodeSvg(payload, 240);
  }

  applyCompactPayload(payloadString) {
    try {
      const data = JSON.parse(payloadString);
      if (!data || !data.q) return false;

      // Merge into current state (taking max streak)
      for (const [id, item] of Object.entries(data.q)) {
        const [attempts, correct, streak, isGuessed] = item;
        const existing = storage.getQuestionState(id);

        const newAttempts = Math.max(existing.attempts, attempts);
        const newCorrect = Math.max(existing.correct, correct);
        const newStreak = Math.max(existing.streak, streak);
        const newIsGuessed = isGuessed === 1;

        storage.state.questions[id] = {
          attempts: newAttempts,
          correct: newCorrect,
          streak: newStreak,
          isGuessed: newIsGuessed,
          lastAnswered: new Date().toISOString(),
          status: newStreak >= 2 ? "mastered" : (newAttempts > 0 ? "probation" : "unseen")
        };
      }

      storage.saveState();
      if (this.onSyncComplete) this.onSyncComplete();
      return true;
    } catch (e) {
      console.error("Failed to parse sync payload:", e);
      return false;
    }
  }

  exportFile() {
    const jsonStr = storage.exportStateJson();
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `telangana_llr_practice_backup_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  importFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = e => {
        const content = e.target.result;
        const ok = storage.importStateJson(content);
        if (ok) {
          if (this.onSyncComplete) this.onSyncComplete();
          resolve(true);
        } else {
          // Try compact payload
          const compactOk = this.applyCompactPayload(content);
          if (compactOk) resolve(true);
          else reject(new Error("Invalid backup file format"));
        }
      };
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }
}

export const sync = new SyncEngine();
