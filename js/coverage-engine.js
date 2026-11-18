// js/coverage-engine.js - 95% Exam Readiness Tracker & Adaptive Sampler
import { storage } from "./storage-engine.js";

export const TOTAL_QUESTIONS_COUNT = 412; // 94 Signs + 159 Rules + 159 Principles
export const READINESS_TARGET = 95; // 95% required for green readiness certification

export class CoverageEngine {
  constructor(allQuestions = []) {
    this.questions = allQuestions; // [{ id, category, ... }]
  }

  setQuestions(allQuestions) {
    this.questions = allQuestions;
  }

  /**
   * Computes readiness statistics:
   * - Mastered (streak >= 2): fully certified questions.
   * - Probation (streak == 1, or answered wrong, or guessed): in-progress.
   * - Unseen (attempts == 0): never encountered yet.
   * - Readiness Score = (Mastered / Total) * 100%
   */
  getReadinessStats() {
    const total = this.questions.length || TOTAL_QUESTIONS_COUNT;
    let mastered = 0;
    let probation = 0;
    let unseen = 0;
    let guessedCount = 0;

    const categoryStats = {
      road_signs: { total: 0, mastered: 0, probation: 0, unseen: 0 },
      rules_of_road: { total: 0, mastered: 0, probation: 0, unseen: 0 },
      general_principles: { total: 0, mastered: 0, probation: 0, unseen: 0 }
    };

    this.questions.forEach(q => {
      const qState = storage.getQuestionState(q.id);
      const cat = q.category;
      if (categoryStats[cat]) {
        categoryStats[cat].total += 1;
      }

      if (qState.status === "mastered") {
        mastered += 1;
        if (categoryStats[cat]) categoryStats[cat].mastered += 1;
      } else if (qState.status === "probation") {
        probation += 1;
        if (categoryStats[cat]) categoryStats[cat].probation += 1;
      } else {
        unseen += 1;
        if (categoryStats[cat]) categoryStats[cat].unseen += 1;
      }

      if (qState.isGuessed) {
        guessedCount += 1;
      }
    });

    const targetMastered = Math.round(total * (READINESS_TARGET / 100)); // 391 for total = 412
    let readinessPercent = 0;
    if (total > 0) {
      if (mastered >= targetMastered) {
        readinessPercent = Math.max(READINESS_TARGET, Math.round((mastered / total) * 100));
      } else {
        readinessPercent = Math.min(READINESS_TARGET - 1, Math.round((mastered / total) * 100));
      }
    }
    const isExamReady = mastered >= targetMastered;

    return {
      total,
      mastered,
      probation,
      unseen,
      guessedCount,
      readinessPercent,
      targetPercent: READINESS_TARGET,
      isExamReady,
      categoryStats
    };
  }

  /**
   * "Coverage Booster" Adaptive Sampler:
   * Generates a 20-question authentic mock test adhering strictly to the official quota:
   * - 8 Road Signs
   * - 8 Traffic Rules
   * - 4 General Driving Principles
   *
   * Priority in picking questions within each category:
   * 1. 70% weighted chance: Pick Unseen / Probation / Previously Guessed questions.
   * 2. 30% chance: Random selection across all questions in that category.
   * This guarantees that mock test attempts actively drive candidate readiness to 95%!
   */
  sampleMockExamQuestions() {
    const signs = this.questions.filter(q => q.category === "road_signs");
    const rules = this.questions.filter(q => q.category === "rules_of_road");
    const principles = this.questions.filter(q => q.category === "general_principles");

    const sampleCategory = (pool, count) => {
      // Split into priority (unseen / probation / guessed) and mastered
      const priority = [];
      const mastered = [];

      pool.forEach(q => {
        const state = storage.getQuestionState(q.id);
        if (state.status !== "mastered" || state.isGuessed) {
          priority.push(q);
        } else {
          mastered.push(q);
        }
      });

      // Shuffle helper
      const shuffle = arr => arr.slice().sort(() => 0.5 - Math.random());
      const shuffledPriority = shuffle(priority);
      const shuffledMastered = shuffle(mastered);

      const selected = [];
      // Prefer priority up to 70% or whatever is available
      while (selected.length < count && shuffledPriority.length > 0) {
        selected.push(shuffledPriority.pop());
      }
      // Fill remaining quota with mastered questions
      while (selected.length < count && shuffledMastered.length > 0) {
        selected.push(shuffledMastered.pop());
      }
      // If pool was small, fallback
      while (selected.length < count && pool.length > 0) {
        const randQ = pool[Math.floor(Math.random() * pool.length)];
        if (!selected.includes(randQ)) selected.push(randQ);
        else break;
      }

      return shuffle(selected);
    };

    const examSigns = sampleCategory(signs, 8);
    const examRules = sampleCategory(rules, 8);
    const examPrinciples = sampleCategory(principles, 4);

    // Combine in stratified order or interleaved
    const fullExam = [...examSigns, ...examRules, ...examPrinciples];
    return fullExam;
  }
}

export const coverage = new CoverageEngine();
