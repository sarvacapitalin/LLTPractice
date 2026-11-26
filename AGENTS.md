# LLTPractice — Project Context & Invariants

**What this project is:** A zero-dependency, vanilla HTML/CSS/ES6 static web app hosted on GitHub Pages (`https://llr.sarvacapital.in/`) that helps driving licence applicants in Hyderabad and Telangana pass the **RTA STALL (Screen Test Aid for Learner Licence)** computerized exam in **English, Telugu (`te`), and Hindi (`hi`)**.

**Core architecture & intent:**
- **Single source of truth:** Verified question banks (`data/questions/telangana/*.json`), guides (`data/*.json`), and extracted diagrams (`assets/signs/`, `assets/scenarios/`) drive both the interactive SPA (`index.html` + `js/*.js`) and the static SEO/LLM pages (`scripts/build_seo_pages.py`). Always fix data or image bugs at the primary source, never by patching derived views alone.
- **Zero-build static hosting + dual discoverability:** Because there is no backend or bundler, the interactive SPA runs purely client-side while `scripts/build_seo_pages.py` pre-renders static HTML subpages, `sitemap.xml`, and `llms-full.txt` so search engines and LLM crawlers can index all content without executing JavaScript.

---

## 1. Domain & Exam Fidelity (Why: match the real Telangana RTA STALL kiosk)
- **Randomized option order:** Shuffle multiple-choice options per question by default (`shuffleOptions` defaults to `true` via `shuffleQuestionOptions()` in `js/exam-engine.js`, remapping `answerIndex` cleanly) to match the latest STALL exam format.
- **Custom & early-stop scoring:** Custom/retry exams (`isCustom === true`) must compute dynamic 60% pass thresholds (`Math.max(1, Math.ceil(totalQs * 0.6))`) and report attempted question counts accurately when exams end early (12 correct = PASS, 9 wrong = FAIL).
- **Trilingual parity:** Keep `en`, `te`, and `hi` keys synchronized across `data/i18n/*.json` and all question/guide datasets; never hardcode `getCurrentLang()` to `"en"`.

## 2. UI, Accessibility & State Resilience (Why: reliable mobile-first & offline-safe UX)
- **Responsive layout & zoom:** Never add `user-scalable=no` or `maximum-scale` to viewport meta tags. Never hardcode inline 2-column CSS grids (`grid-template-columns: 1fr 1fr`) inside dynamic JS templates; use responsive CSS classes (`.options-grid`, `.twins-comparison-grid`).
- **Theme & Dark-mode contrast:** Always use semantic CSS tokens (`var(--card-bg)`, `var(--surface-subtle)`, `var(--text-primary)`, `var(--text-secondary)`, `var(--accent-blue)` for dark-mode text/links, `var(--sign-surface)` behind road-sign PNGs/QR codes, `var(--cta-gold-bg)`/`var(--cta-gold-text)`, and `var(--badge-rto-bg)`/`var(--badge-rto-text)`) instead of hardcoded hex literals or button-fill tokens (`--secondary-blue`). After any CSS/HTML/JS UI change, run a full literal-color scan + independent browser verification across SPA tabs and static pages in both Light and Dark modes.
- **SPA URL syncing:** Keep `?tab=` and `?lang=` synchronized with the address bar via `history.pushState`/`popstate` in `js/app.js` and `js/i18n.js` without reloading (so URLs are shareable and Back/Forward works without interrupting active exam timers). Preserve active query parameters during `#hash` normalization and `?sync=` cleanup.
- **Import & storage resilience:** Sanitize imported JSON state in `storage.importStateJson()` with default `preferences` and `examHistory`, and reset `#input-sync-file` (`e.target.value = ""`) inside a `finally` block so identical files can be re-imported.

## 3. Assets, Cache-Busting & Static SEO/LLM Pages (Why: prevent stale caches & crawler/Bing warnings)
- **Clean JSON image paths:** Keep `"image"` paths in `data/**/*.json` free of query strings (`?v=...`) so `os.path.exists()` QA checks pass. Apply cache-busting at render time via `ASSET_VER` (`withAssetVer()` in `js/app.js`) and update matching `?v=` tags in `index.html` whenever datasets, JS/CSS, or PNG/SVG assets change.
- **Fix primary assets, not derived views:** When an image or question bug is reported in a derived dataset (e.g., `data/tricky-twins.json`, `data/popular-guides.json`), audit and fix the root asset (`assets/signs/`, `assets/scenarios/`, `data/questions/telangana/*.json`) and its extraction script (`scripts/rebuild_*.py`), then visually verify with `read_file`.
- **Title length & SEO rebuilds:** Keep every `<title>` tag **≤ 65 characters** (to avoid Bing Site Scan `"Title too long"` warnings) while preserving the `Telangana RTA Learner's Licence Practice` prefix in `index.html` (required by `scripts/test_runner.py`). Whenever `data/**/*.json` or static routes change, run `python3 scripts/build_seo_pages.py` to regenerate all static pages, `llms-full.txt`, and `sitemap.xml`, and keep JSON-LD `FAQPage` items aligned with visible HTML.

## 4. Verification Before Commit (Why: catch regressions in data, DOM, and ES modules)
- Always run `python3 scripts/validate_workspace.py && python3 scripts/test_runner.py` after edits and confirm all 64+ QA tests pass.
- When testing browser ES modules (`js/*.js`) directly in Node.js (`node --input-type=module`), pre-mock `globalThis.localStorage`, `globalThis.window`, and `globalThis.document` before dynamic `import()`, and reset stateful singletons (e.g., `sounds.ctx`) between test cases.
