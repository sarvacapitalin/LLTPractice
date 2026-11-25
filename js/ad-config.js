// js/ad-config.js - Central Google AdSense configuration for llr.sarvacapital.in
export const ADSENSE_CONFIG = {
  // Flip enabled to true and insert your verified AdSense slotIds once approved.
  enabled: false,
  clientId: "ca-pub-6573213692692289",
  slots: {
    home_study: {
      slotId: "0000000001",
      format: "auto",
      layoutKey: "leaderboard",
      dimensions: "728×90 Desktop • 320×100 Mobile",
      title: "Home Dashboard Companion",
      rationale: "Positioned below Start Test & Category Mastery; auto-hidden during active exam"
    },
    exam_result: {
      slotId: "0000000002",
      format: "auto",
      layoutKey: "leaderboard",
      dimensions: "728×90 Desktop • 336×280 / 320×100 Mobile",
      title: "Post-Exam Scorecard Transition",
      rationale: "Shown during natural pause between test score summary and detailed Q&A review"
    },
    practice_rail: {
      slotId: "0000000003",
      format: "auto",
      layoutKey: "rectangle",
      dimensions: "300×250 Companion / Responsive",
      title: "Topic Practice Navigator Rail",
      rationale: "Separated 150px+ from answer buttons inside secondary study rail"
    },
    study_tool: {
      slotId: "0000000004",
      format: "auto",
      layoutKey: "leaderboard",
      dimensions: "728×90 Desktop • 320×100 Mobile",
      title: "Study Tool Section Break",
      rationale: "Placed cleanly below Flashcards, Tricky Twins, and Cheatsheet controls"
    },
    seo_in_content: {
      slotId: "0000000005",
      format: "auto",
      layoutKey: "leaderboard",
      dimensions: "Responsive In-Content Banner",
      title: "Guide Section Divider",
      rationale: "Inserted strictly between major sections (e.g., Mandatory vs Cautionary signs)"
    },
    seo_multiplex: {
      slotId: "0000000006",
      format: "autorelaxed",
      layoutKey: "multiplex",
      dimensions: "Responsive Multiplex Grid",
      title: "End-of-Guide Related Resources",
      rationale: "Low-friction discovery grid placed above the page footer"
    }
  }
};
