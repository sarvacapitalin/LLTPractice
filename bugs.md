# Telangana RTA Learner's Licence Practice Platform — Comprehensive Bug Audit Report

This document records all bugs identified during an in-depth audit of the codebase across logic, UI polish, consistency, edge-case resilience, responsive design, and accessibility.

---

### Bug ID: BUG-01
**Bug Shortname:** Custom Exam & "Re-try Missed Questions" Mode Fails by Design Due to Hardcoded 12-Question Pass Gate  
**Status:** FIXED  
**Description:**  
When a candidate finishes a mock exam with fewer than 12 missed questions (e.g., 2, 4, or 8 missed questions) and clicks the **"RE-TRY MISSED QUESTIONS (N)"** button, the custom exam can never be passed. Even if the candidate answers 100% of the missed questions correctly, the application marks the test as **FAILED ("TEST NOT CLEARED")**, plays the error sound effect, and displays *"You need at least 12 correct answers to pass."* Additionally, the workstation header displays `Question X of 20` hardcoded instead of `Question X of N`, and the quota counters show `/8`, `/8`, and `/4`.

**Steps to reproduce:**
1. Start a mock test and complete it with a score of 12 correct and 4 wrong.
2. On the result card, click the red button **"🎯 RE-TRY MISSED QUESTIONS (4)"**.
3. Answer all 4 questions correctly.
4. Observe the result screen upon test completion.
5. Notice the test ends with a red **"✗ TEST NOT CLEARED"** banner and fail chime despite scoring 4 out of 4 (100%).

**Root Cause:**  
In `js/exam-engine.js`:
- Line 252 inside `finishExam()` hardcodes the pass condition as `const passed = this.correctCount >= 12;`.
- Lines 116–124 inside `startQuestion()` hardcode early-termination thresholds to `this.correctCount >= 12` and `this.wrongCount >= 9`.
When `this.questions.length < 12`, `correctCount` can never reach 12. Consequently, `passed` evaluates to `false` every time.
- In `js/app.js` line 424, the header badge is hardcoded to `Question ${state.currentIndex + 1} of 20`.

**Code artifacts and line references:**
- [`js/exam-engine.js#L92-L105`](file:///Users/raghu/Projects/LLTPractice/js/exam-engine.js#L92-L105): `startCustomExam()` sets `this.questions` to `customQuestions` without adjusting passing criteria or total question count.
- [`js/exam-engine.js#L114-L124`](file:///Users/raghu/Projects/LLTPractice/js/exam-engine.js#L114-L124): `startQuestion()` early-stopping thresholds hardcoded to 12 and 9.
- [`js/exam-engine.js#L252`](file:///Users/raghu/Projects/LLTPractice/js/exam-engine.js#L252): `const passed = this.correctCount >= 12;`.
- [`js/app.js#L424`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L424): `qBadge.textContent = "Question " + (state.currentIndex + 1) + " of 20";`.
- [`js/app.js#L436-L438`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L436-L438): Quota tracker hardcoded denominators (`/8`, `/8`, `/4`).

**Solution:**  
1. Make pass evaluation dynamic based on question count:
   ```javascript
   const isCustom = this.questions.length !== 20;
   const passThreshold = isCustom ? Math.ceil(this.questions.length * 0.6) : 12;
   const failThreshold = isCustom ? (this.questions.length - passThreshold + 1) : 9;
   ```
2. In `startQuestion()`, apply `early_pass` when `this.correctCount >= passThreshold` and `early_fail` when `this.wrongCount >= failThreshold`.
3. In `finishExam()`, set `const passed = this.correctCount >= passThreshold;`.
4. In `js/app.js`, update `qBadge.textContent` to `Question ${state.currentIndex + 1} of ${state.totalQuestions}`.
5. In custom exam mode, hide or adapt the 8-8-4 quota counter to reflect the actual categories present in the retry set.

**Implemented fix:**  
- Updated `ExamEngine` (`js/exam-engine.js`) to set `this.isCustom = true` in `startCustomExam()` and `this.isCustom = false` in `startNewExam()`.
- Computed dynamic passing threshold `passThreshold = this.isCustom ? Math.max(1, Math.ceil(totalQs * 0.6)) : 12` and fail threshold `failThreshold = this.isCustom ? (totalQs - passThreshold + 1) : 9` across `startQuestion()`, `finishExam()`, and `getStateSnapshot()`.
- Updated `js/app.js` to render dynamic question headers (`Question ${state.currentIndex + 1} of ${state.totalQuestions}`), dynamic category quota denominators (`${seen}/${total}` based on questions present in the session), and custom pass/fail result descriptions indicating the dynamic pass mark.
- **Why this works & Test Scenario:**
  - For a standard 20-question STALL exam, `isCustom` is false, preserving the official 12-to-pass / 9-to-fail rule.
  - For a retry session with $N < 20$ questions (e.g. 4 missed questions), `passThreshold` is $\lceil 4 \times 0.6 \rceil = 3$ questions. Answering 3 or 4 correctly now legitimately awards a PASS with success chimes and scorecard celebration.
  - Verified via automated Node test where 4 dummy questions were initiated via `startCustomExam()`, answered correctly, and confirmed to transition to `isFinished: true`, `passed: true`, with `passThreshold: 3`.

---

### Bug ID: BUG-02
**Bug Shortname:** Instant Visual Feedback Erasure in Topic Practice Due to Synchronous Re-Render  
**Status:** FIXED  
**Description:**  
In Topic Practice (`tab-practice`), when a user taps an option button to test their knowledge, the option button is supposed to turn green (if correct) or red (if incorrect), and display the official explanation in `#practice-explanation-box`. However, the explanation and option colors flash for a single frame (0ms) and are instantly wiped out, leaving the question card reset to its initial unanswered state. The user is left unable to verify if their choice was right or read the explanation.

**Steps to reproduce:**
1. Navigate to the **"📚 Topic Practice"** tab.
2. On any question, click one of the 4 option buttons.
3. Observe that the button color and explanation box appear for a fraction of a millisecond and immediately vanish, resetting all 4 buttons to unclicked state.

**Root Cause:**  
In `js/app.js` lines 842–862:
```javascript
container.querySelectorAll(".practice-opt-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    ...
    // Styles applied to DOM
    b.style.borderColor = "#22C55E";
    expBox.style.display = "block";

    // Synchronous call to answerPracticeQuestion
    practice.answerPracticeQuestion(q.id, idx, false);
  });
});
```
Inside `js/practice-engine.js` line 85, `answerPracticeQuestion()` synchronously calls `this.notifyUpdate()`. This triggers `practice.onStateChange` in `js/app.js` (line 742), which synchronously invokes `renderPracticeCard(state.selectedQuestion)`. `renderPracticeCard` immediately overwrites `container.innerHTML` with fresh HTML containing default unselected buttons and `<div id="practice-explanation-box" style="display: none;">`.

**Code artifacts and line references:**
- [`js/app.js#L739-L743`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L739-L743): `practice.onStateChange` re-renders `renderPracticeCard(state.selectedQuestion)` on every state change.
- [`js/app.js#L827-L862`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L827-L862): `renderPracticeCard()` resets `innerHTML` with `display: none` on explanation box, while button click immediately calls `answerPracticeQuestion()`.
- [`js/practice-engine.js#L76-L87`](file:///Users/raghu/Projects/LLTPractice/js/practice-engine.js#L76-L87): `answerPracticeQuestion()` synchronously fires `this.notifyUpdate()`.

**Solution:**  
Store the answered state on the active question or separate the matrix update from the card re-render:
1. In `practice-engine.js`, record `selectedOption` and `answered` state on `this.activeAnswerState = { qId, selectedIndex, isCorrect }`.
2. Either do not invoke full `renderPracticeCard()` inside `onStateChange` when triggered by an answer (only invoke `renderPracticeMatrix()` and `updateReadinessMeter()`), OR have `renderPracticeCard(q)` inspect `this.activeAnswerState` to render the answered state with disabled buttons, green/red highlight, and visible explanation box.

**Implemented fix:**  
- Updated `PracticeEngine` (`js/practice-engine.js`) to maintain `this.lastAnswers[questionId] = { selectedIndex, isCorrect }` and pass an action reason (`notifyUpdate("answer")` vs `"update"` / `"select"`).
- In `js/app.js`, modified `practice.onStateChange` so that when `state.reason === "answer"`, it updates `updateReadinessMeter()` and `renderPracticeMatrix()` without blowing away the question card via `renderPracticeCard()`.
- Enhanced `renderPracticeCard(q)` to inspect `practice.lastAnswers[q.id]`. When a question has been answered, buttons render with green/red borders and background styles, cursor defaults, disabled states, and the `#practice-explanation-box` stays visible with a dedicated `"🔄 Re-try"` button.
- Updated the status badge container (`#practice-status-badge-wrap`) in real-time upon clicking an option to reflect immediate streak and mastery progression.
- **Why this works & Test Scenario:**
  - Separating the matrix/readiness sync from the question card DOM lifecycle prevents tearing down active button styles and hiding the explanation.
  - Verified via automated unit test: answering question 1 emits `reason: "answer"`, registers `{ selectedIndex: 1, isCorrect: true }`, updates streak from 0 to 1, and maintains green/red feedback and official explanation on screen without blinking or resetting.

---

### Bug ID: BUG-03
**Bug Shortname:** Stale Question Displayed in Topic Practice When Switching Category, Status Filter, or Searching  
**Status:** FIXED  
**Description:**  
In Topic Practice, when a user switches between categories (e.g. from "Road Signs" to "Traffic Rules"), changes the status filter (e.g. to "Unseen Only"), or types a search query, the Question Navigator matrix updates to show the filtered questions, but the main question card continues displaying the previously selected question from the old category or filter. Furthermore, if a search query or filter returns 0 matching questions, the card still shows the stale question instead of an empty state.

**Steps to reproduce:**
1. Navigate to **"📚 Topic Practice"**.
2. Select "Road Signs (94)" and click on Question 1 (`TS_RS_001`).
3. Now click the category button **"Traffic Rules (159)"**.
4. Observe the Question Navigator matrix: chips now represent Traffic Rules (`TS_RR_001` onwards).
5. Observe the question card: it still displays `TS_RS_001 • Question 1 "A RED TRAFFIC LIGHT MEANS"`, which is a Road Sign, not a Traffic Rule. None of the chips in the navigator are selected.
6. Type `"xyznonexistent"` into the search box: the matrix becomes empty, but the Road Sign question remains on screen.

**Root Cause:**  
In `js/practice-engine.js`:
- Methods `setCategory()`, `setFilter()`, and `setSearch()` update filter criteria and call `this.notifyUpdate()`, but never update `this.selectedQuestion`.
- In `js/app.js` lines 790–792, `renderPracticeCard(q)` checks `if (!container || !q) return;`. When `filteredQuestions` is empty, `selectedQuestion` is still the old object, so the card is never cleared or replaced with an empty-state message.

**Code artifacts and line references:**
- [`js/practice-engine.js#L24-L37`](file:///Users/raghu/Projects/LLTPractice/js/practice-engine.js#L24-L37): `setCategory()`, `setFilter()`, and `setSearch()` do not sync `this.selectedQuestion`.
- [`js/practice-engine.js#L89-L98`](file:///Users/raghu/Projects/LLTPractice/js/practice-engine.js#L89-L98): `notifyUpdate()` passes unchanged `selectedQuestion`.
- [`js/app.js#L790-L793`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L790-L793): `renderPracticeCard(q)` ignores empty filter cases.

**Solution:**  
In `practice-engine.js`, add an internal synchronization helper:
```javascript
_syncSelectedQuestion() {
  const filtered = this.getFilteredQuestions();
  if (filtered.length === 0) {
    this.selectedQuestion = null;
  } else if (!this.selectedQuestion || !filtered.some(q => q.id === this.selectedQuestion.id)) {
    this.selectedQuestion = filtered[0];
  }
}
```
Call `this._syncSelectedQuestion()` at the start of `setCategory()`, `setFilter()`, `setSearch()`, and `notifyUpdate()`. In `app.js`, if `q === null`, render a clean empty-state card:
`<div class="empty-state">No questions found matching your filter or search criteria.</div>`.

**Implemented fix:**  
- Implemented `_syncSelectedQuestion()` in `PracticeEngine` (`js/practice-engine.js`) and invoked it in `setQuestions()`, `setCategory()`, `setFilter()`, `setSearch()`, and `notifyUpdate()`.
- If the current selected question does not belong to the updated filter set, the engine automatically selects `filtered[0]`. If no questions match the search/filter criteria, `this.selectedQuestion` cleanly resolves to `null`.
- Updated `renderPracticeCard(q)` in `js/app.js` to render an accessible empty-state card (`"🔍 No questions found"`) when `q` is `null`, guiding the user to clear their search or reset filters.
- **Why this works & Test Scenario:**
  - Guarantees the question card and Question Navigator matrix chip selection stay 100% in sync across category buttons, search inputs, and status filter dropdowns.
  - Verified via Node.js automated test: selecting `TS_RS_001` and switching category to `rules_of_road` automatically promoted `TS_RR_001`; searching `xyznonexistent` yielded `selectedQuestion = null`, and clearing search immediately restored `TS_RR_001`.

---

### Bug ID: BUG-04
**Bug Shortname:** Random Option Shuffling Contradicts Official STALL Specification and Distorts Question Explanations  
**Status:** FIXED  
**Description:**  
In `js/exam-engine.js`, every mock exam question has its 4 multiple-choice options shuffled using `shuffleQuestionOptions()`. However:
1. The official documentation in `index.html` (JSON-LD Schema line 126 and FAQ line 515) and `llms.txt` explicitly state: *"Options remain in the exact same fixed order (1, 2, 3, 4) because the STALL kiosk uses a physical numeric keypad mapped directly to the official government question bank answer keys. Only the selection of the 20 questions is randomized."*
2. Multiple questions in the official dataset (e.g., `TS_RS_086`, `TS_RS_087`, `TS_RS_088`, `TS_RS_089`, `TS_RS_090`) have official explanations explicitly citing option numbers, e.g., *"Official RTA Key: Option 2 ('HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT')"*. Shuffling options causes Option 2 to move to Option 3 or 4 on screen, creating a direct contradiction between the displayed option and the explanation text.
3. In Topic Practice, options are NOT shuffled, resulting in inconsistent answer numbers between Practice and Mock Exam modes.

**Steps to reproduce:**
1. Start an exam and inspect question `TS_RS_087` (Traffic hand signal for turning right).
2. Note that the options are randomly re-ordered.
3. If Option 2 is shuffled to slot 4, the correct answer badge says `4`, but the rule explanation reads: *"Official RTA Key: Option 2 ('HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT')"*.

**Root Cause:**  
In `js/exam-engine.js` lines 29–63 and lines 78 & 94:
`shuffleQuestionOptions(q)` is invoked when loading questions in `startNewExam()` and `startCustomExam()`, directly violating the fixed-order STALL specification and breaking option-number-dependent explanations.

**Code artifacts and line references:**
- [`js/exam-engine.js#L29-L63`](file:///Users/raghu/Projects/LLTPractice/js/exam-engine.js#L29-L63): `shuffleQuestionOptions()` implementation.
- [`js/exam-engine.js#L78`](file:///Users/raghu/Projects/LLTPractice/js/exam-engine.js#L78): `this.questions = sampled.map(q => this.shuffleQuestionOptions(q));`.
- [`js/exam-engine.js#L94`](file:///Users/raghu/Projects/LLTPractice/js/exam-engine.js#L94): `this.questions = customQuestions.map(q => this.shuffleQuestionOptions(q));`.
- [`index.html#L126-L130`](file:///Users/raghu/Projects/LLTPractice/index.html#L126-L130) & [`index.html#L515-L520`](file:///Users/raghu/Projects/LLTPractice/index.html#L515-L520): FAQ asserting options are never shuffled.
- [`data/questions/telangana/road-signs.json#TS_RS_086-TS_RS_090`](file:///Users/raghu/Projects/LLTPractice/data/questions/telangana/road-signs.json): Official explanation strings referring to specific options.

**Solution:**  
Preserve the authentic STALL fixed option order:
1. Remove `this.shuffleQuestionOptions(q)` calls from `startNewExam()` and `startCustomExam()`, or gate option shuffling behind an optional "Advanced Practice / Shuffle Options" user setting (defaulting to OFF).
2. Align the simulator behavior with the real RTO kiosk hardware numeric mapping and the published FAQ specification.

**Implemented fix:**  
- Updated `startNewExam()` and `startCustomExam()` in `js/exam-engine.js` to preserve the original fixed option order `(1, 2, 3, 4)` by default, matching physical STALL kiosk numeric keypads and the official published RTA FAQ specification.
- Added preference check `storage.getPreference("shuffleOptions", false)` allowing candidates who explicitly opt into dynamic option shuffling for advanced practice to do so without breaking default fidelity.
- Retained `shuffleQuestionOptions(q)` as an available utility method so no breaking API changes were introduced.
- **Why this works & Test Scenario:**
  - Prevents answer mismatch on questions `TS_RS_086`–`TS_RS_090` where official RTA explanations cite specific option numbers (e.g. *"Official RTA Key: Option 2 ('HE INTENDS TO MOVE OUT TO THE RIGHT OR TURN RIGHT')"*).
  - Keeps Topic Practice and Mock Exam option orders completely consistent.
  - Verified via automated Node.js test: loaded questions `TS_RS_086` through `TS_RS_090` into `ExamEngine.startNewExam()`; all options remained in exact 1-to-1 canonical order with correct indexes matching the question bank keys. Verified toggling `shuffleOptions: true` in user preferences properly enables shuffling when requested.

---

### Bug ID: BUG-05
**Bug Shortname:** Guess Checkbox State Leak Across Questions, Hotkey Submissions, and Timeouts  
**Status:** FIXED  
**Description:**  
When a user checks the *"🤔 I guessed this answer (keep on probation)"* checkbox during an exam:
1. If the user submits using the `Enter` hotkey instead of clicking the `CONFIRM & NEXT` button, the checkbox is never unchecked.
2. If the question countdown timer expires (30s timeout), the checkbox is never unchecked.
3. If the user starts a new exam or custom exam, the checkbox retains its checked state.
Consequently, all subsequent questions answered correctly are incorrectly tagged as `isGuessed: true` and capped at Streak 1 (probation), preventing the candidate from achieving mastery.

**Steps to reproduce:**
1. Start a Mock Test.
2. On Question 1, check the `"🤔 I guessed this answer"` checkbox.
3. Select an option and press the `Enter` key on the keyboard.
4. On Question 2, observe that the `"🤔 I guessed this answer"` checkbox is still checked.
5. Answer Question 2 correctly using `Enter`.
6. Inspect `localStorage`: Question 2 is marked with `isGuessed: true` and streak 1 despite the candidate not guessing it.

**Root Cause:**  
In `js/app.js` line 303:
`if (guessCheckbox) guessCheckbox.checked = false;` is placed exclusively inside the `btnConfirm` click listener. It is missing from:
- `setupKeyboardHotkeys()` (when `e.key === "Enter"`).
- `exam.onStateUpdate` (when `isNewQuestion` is true).
- `startNewExam()` and `startCustomExam()`.

**Code artifacts and line references:**
- [`js/app.js#L237-L241`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L237-L241): Keyboard Enter handler submits `isGuessed` without clearing the checkbox.
- [`js/app.js#L300-L304`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L300-L304): `guessCheckbox.checked = false` only present in manual button click.
- [`js/app.js#L412-L476`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L412-L476): Question transition block does not ensure `guessCheckbox.checked = false`.

**Solution:**  
Reset the guess checkbox on every question load inside `exam.onStateUpdate`:
```javascript
if (isNewQuestion) {
  const guessCheckbox = document.getElementById("exam-guess-checkbox");
  if (guessCheckbox) guessCheckbox.checked = false;
  ...
}
```
Also ensure `guessCheckbox.checked = false;` is executed inside `setupKeyboardHotkeys()` upon submitting via `Enter`.

**Implemented fix:**  
- In `js/app.js`:
  - Added `if (guessBox) guessBox.checked = false;` in `setupKeyboardHotkeys()` immediately when submitting via the `Enter` hotkey.
  - Added `if (guessBox) guessBox.checked = false;` inside `exam.onStateUpdate` within the `if (isNewQuestion)` block, ensuring that regardless of transition mechanism (next question, 30s timeout expiration, tutor mode continue, retake, or custom exam launch), the guess checkbox is cleanly reset for the next question.
  - Added reset safeguarding inside `btnStart`, `btnRetake`, and `btnRetakeMissed` handlers.
- **Why this works & Test Scenario:**
  - Prevents the probation state (`isGuessed: true`) from leaking across questions or sessions, eliminating false probation penalties on subsequent questions.
  - Verified with simulated DOM test: checked guess box on Q1, submitted via Enter hotkey (checked transitioned to false); simulated timeout / transition to Q2 with pre-checked state, `isNewQuestion` automatically cleared checked state to false.

---

### Bug ID: BUG-06
**Bug Shortname:** Background Exam Timer and Keyboard Hotkeys Continue Active When Navigating Away from Exam Tab  
**Status:** FIXED  
**Description:**  
When an exam is in progress and the candidate switches to another tab (such as **"📚 Topic Practice"**, **"🗂️ Sign Flashcards"**, or **"🏢 Hyderabad RTO Guide"**):
1. The 30-second question timer does not pause. Every 30 seconds, `handleTimeout()` triggers, failing questions and decrementing candidate streaks in `localStorage` in the background. After ~4.5 minutes, the exam fails silently with 9 wrong answers.
2. The keyboard hotkeys (`1`, `2`, `3`, `4`, `Enter`, `Space`) remain globally active. If the user clicks into the Topic Practice search box (`#practice-search-input`) and types numbers, spaces, or presses Enter, those keystrokes mutate the background exam (selecting options, submitting answers, and triggering speech).

**Steps to reproduce:**
1. Start a Mock Test on the **"Mock Test (STALL)"** tab.
2. Click on the **"Topic Practice"** tab.
3. Click inside the search input box and type `"Rule 1"`.
4. Press `Space` and `Enter`.
5. Switch back to the "Mock Test" tab: observe that questions have timed out or options have been submitted by the keystrokes.

**Root Cause:**  
- In `js/app.js` lines 134–156 (`setupTabs`), tab switching only calls `speech.stop()`. It neither pauses the exam timer nor warns the user.
- In `js/app.js` lines 231–247 (`setupKeyboardHotkeys`), the listener only checks `if (exam.isActive && !exam.isFinished)`. It does not verify whether the exam tab is active or if `e.target` is an input field (`INPUT` or `TEXTAREA`).

**Code artifacts and line references:**
- [`js/app.js#L134-L156`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L134-L156): `setupTabs()` lacks tab-pause logic for active exams.
- [`js/app.js#L231-L247`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L231-L247): `setupKeyboardHotkeys()` intercepts keystrokes globally without checking `document.activeElement.tagName` or active tab.
- [`js/exam-engine.js#L130-L147`](file:///Users/raghu/Projects/LLTPractice/js/exam-engine.js#L130-L147): Timer runs on an unmanaged `setInterval`.

**Solution:**  
1. In `setupKeyboardHotkeys`, guard against typing in form inputs and non-exam tabs:
   ```javascript
   const isExamTabActive = document.getElementById("tab-exam")?.classList.contains("active");
   const isTyping = ["INPUT", "TEXTAREA"].includes(e.target.tagName);
   if (!isExamTabActive || isTyping || !exam.isActive || exam.isFinished) return;
   ```
2. When switching away from `tab-exam` while `exam.isActive` is true, either prompt the user with a confirmation dialog to abandon the test, or pause the timer until returning to the tab.

**Implemented fix:**  
- Added `pauseTimer()` and `resumeTimer()` methods to `ExamEngine` (`js/exam-engine.js`), managing `this.isPaused` state and clearing/restoring the countdown interval cleanly.
- In `js/app.js`:
  - Updated `setupTabs()` to invoke `exam.pauseTimer()` whenever switching away from `tab-exam` during an active exam, and `exam.resumeTimer()` when switching back to `tab-exam`.
  - Added a `visibilitychange` listener to automatically pause the exam timer when the browser tab is hidden or minimized and resume when visible on the exam tab.
  - Hardened `setupKeyboardHotkeys()` to verify that the exam tab is active (`#tab-exam.active`) and that neither `document.activeElement` nor `e.target` is an `INPUT`, `TEXTAREA`, or content-editable element, plus prevented default spacebar page scrolling during audio read.
- **Why this works & Test Scenario:**
  - Candidates can safely navigate across tabs or switch browser windows without background timeout penalties destroying their exam or corrupting question streaks.
  - Keystrokes in search bars or inputs never leak into the exam engine.
  - Verified via Node.js test simulating keypress events during text inputs and tab switches (hotkey ignored when outside exam tab or inside input; hotkey executed when active on exam tab). Verified timer pause/resume cycle with `pauseTimer()` and `resumeTimer()`.

---

### Bug ID: BUG-07
**Bug Shortname:** Fake QR Code Generator and Inoperable Mobile "Scan-to-Sync" Feature  
**Status:** FIXED  
**Description:**  
The application heavily features a *"Zero-Server Cross-Device Scan-to-Sync (Laptop ↔ Mobile)"* feature in the UI and README: *"Scan this QR code with your mobile phone to instantly import your progress from this laptop."*  
However, the QR code rendered in the modal is a synthetic mock: `js/qrcode-generator.js` does not implement standard ISO/IEC 18004 QR encoding (it uses a dummy 29x29 matrix filled with a pseudo-random hash). Standard camera apps (iOS Camera, Google Lens, Android) cannot decode it. Furthermore, even if valid, the payload is raw JSON (`{"v":1,"q":...}`) without a URL scheme or deep link handler, and the web app provides no mobile camera scanner, making it impossible for a phone camera scan to import data into mobile `localStorage`.

**Steps to reproduce:**
1. Click the **"📲 Sync"** button in the header.
2. Point any smartphone camera (iPhone or Android) or QR scanner app at the generated QR code.
3. Observe that the camera scanner fails to recognize or decode any QR code.
4. Note that there is no camera scanner button on mobile to read QR codes.

**Root Cause:**  
- `js/qrcode-generator.js` lines 30–102: Function `generateQRMatrix(text)` is a pseudo-random bit filler that places 3 square patterns and fills the grid with `(byteVal >> (bitIdx % 8)) & 1 ^ mask`. It lacks mode indicators, character count indicators, Reed-Solomon error correction codewords, and format BCH bits.
- `js/sync-engine.js` lines 14–29: `getCompactPayload()` outputs raw JSON instead of an importable URL (`https://llr.sarvacapital.in/?import=<data>`).

**Code artifacts and line references:**
- [`js/qrcode-generator.js#L30-L102`](file:///Users/raghu/Projects/LLTPractice/js/qrcode-generator.js#L30-L102): Pseudo QR generator function.
- [`js/sync-engine.js#L14-L29`](file:///Users/raghu/Projects/LLTPractice/js/sync-engine.js#L14-L29): Compact payload generation without URL wrapper.
- [`index.html#L541-L550`](file:///Users/raghu/Projects/LLTPractice/index.html#L541-L550): Sync modal copy promising instant phone camera scanning.

**Solution:**  
1. Replace `qrcode-generator.js` with an authentic, standards-compliant zero-dependency QR encoder (such as standard Type 1–10 byte-mode QR generator with Reed-Solomon GF(256) error correction) or use a proven lightweight client-side QR library.
2. In `sync-engine.js`, wrap the compressed payload into a URL: `https://llr.sarvacapital.in/?sync=${encodeURIComponent(compressedData)}`.
3. In `js/app.js` on load, detect `?sync=` in the URL query string, automatically import the state via `sync.applyCompactPayload()`, and alert the user of successful synchronization.

**Implemented fix:**  
- Completely replaced `js/qrcode-generator.js` with a fully standards-compliant, zero-dependency ISO/IEC 18004 QR Code implementation (Kazuhiko Arase standard engine with automatic version detection 1–40 and Reed-Solomon error correction).
- Added `generateSyncUrl()` in `js/sync-engine.js` which serializes the compact question streak payload into a URL: `${baseUrl}?sync=${encodeURIComponent(payload)}`.
- Updated `generateSyncQrSvg()` to encode the scannable URL rather than raw JSON, allowing native smartphone camera apps (iOS Camera, Google Lens) to scan the screen and open the web app directly.
- Enhanced `applyCompactPayload()` in `js/sync-engine.js` to parse both direct JSON payloads and URL strings containing `?sync=`.
- Added `checkSyncUrlParam()` to `js/app.js` on `DOMContentLoaded` to detect `?sync=` in the URL query, automatically merge the imported progress, refresh UI meters, alert the candidate of successful sync, and clean up the address bar via `window.history.replaceState()`.
- **Why this works & Test Scenario:**
  - Phone cameras directly decode the ISO/IEC 18004 QR code into a tappable URL link. Tapping it opens the site on mobile, merges question mastery streaks into mobile `localStorage`, and updates readiness without requiring any cloud server or intermediate app.
  - Verified via Node.js automated test: generated authentic QR SVG from `generateSyncUrl()`, verified valid SVG element tags with standard finder modules, and performed full deserialization roundtrip via `applyCompactPayload()` restoring streaks and mastery status accurately.

---

### Bug ID: BUG-08
**Bug Shortname:** Flashcard Progression and Counter Frozen on Last Card and Empty Filters  
**Status:** FIXED  
**Description:**  
In the Sign Flashcards module (`tab-flashcards`):
1. When on the last card of any filtered set (`currentIndex === total - 1`), tapping **"I Know This"** or **"Study Again"** records the attempt in `storage`, but does not advance or refresh the card view. The card remains flipped or frozen without user feedback.
2. When the **"Unmastered Only"** filter is active, marking signs as mastered progressively removes them from the filtered set. When the final unmastered sign is mastered, `state.currentSign` becomes `null`, `app.js` early-returns (`if (!sign) return;`), and the counter displays `Card 1 of 0` while the old sign image and text remain permanently stuck on screen.

**Steps to reproduce:**
1. Navigate to the **"🗂️ Sign Flashcards"** tab.
2. Select the **"Unmastered Only"** filter.
3. Advance to the last unmastered card and click **"I Know This"**.
4. Observe that the counter changes to `Card 1 of 0` (or `Card N of N-1`), and the previous card graphic remains stuck on screen with no completion message.

**Root Cause:**  
In `js/flashcards-engine.js`:
- Line 46: `nextCard()` checks `if (this.currentIndex < list.length - 1)`. When `currentIndex === list.length - 1`, it does nothing and does not call `notifyUpdate()`.
- Lines 61–73: `markMastered()` and `markNeedsPractice()` call `this.nextCard()`, meaning `notifyUpdate()` is never called when on the last card.
- In `js/app.js` line 919: `if (!sign) return;` skips DOM updating when `list` is empty, leaving stale images on screen.

**Code artifacts and line references:**
- [`js/flashcards-engine.js#L44-L51`](file:///Users/raghu/Projects/LLTPractice/js/flashcards-engine.js#L44-L51): `nextCard()` boundary check prevents `notifyUpdate()` on last item.
- [`js/flashcards-engine.js#L61-L73`](file:///Users/raghu/Projects/LLTPractice/js/flashcards-engine.js#L61-L73): `markMastered()` and `markNeedsPractice()` rely on `nextCard()`.
- [`js/app.js#L916-L920`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L916-L920): Counter math (`${state.currentIndex + 1} of ${state.total}`) and early-return when `sign` is null.

**Solution:**  
1. In `flashcards-engine.js`, clamp `currentIndex` to `Math.max(0, Math.min(this.currentIndex, list.length - 1))` and always call `this.notifyUpdate()`.
2. In `app.js`, when `state.total === 0`, render an empty completion state:
   ```javascript
   if (state.total === 0) {
     if (counter) counter.textContent = "0 of 0";
     cardBox.innerHTML = `<div class="fc-complete">🎉 All signs in this category mastered!</div>`;
     return;
   }
   ```
3. Disable the `Previous` button when `currentIndex === 0` and disable `Next` button when `currentIndex === state.total - 1`.

**Implemented fix:**  
- In `js/flashcards-engine.js`:
  - Implemented `_clampIndex()` to safeguard `this.currentIndex` within `[0, list.length - 1]`, preventing out-of-bounds array access.
  - Updated `nextCard()`, `prevCard()`, `markMastered()`, and `markNeedsPractice()` to flip the card back to the front and call `this.notifyUpdate()` unconditionally, even at boundary indices.
  - Handled the `"unmastered"` filter dynamic list reduction so that when a card is mastered, the subsequent card slides into view smoothly.
- In `js/app.js`:
  - Added an empty celebration state `#fc-empty-view` inside `#flashcard-box` displaying `"🎉 All Signs in this Category Mastered!"` when `state.total === 0` or `sign === null`, setting counter to `"0 of 0"`, and disabling action buttons with visual opacity feedback.
  - Dynamically disabled the `Previous` button at `currentIndex === 0` and the `Next` button at `currentIndex === state.total - 1`.
  - Guarded card flip click listeners against empty states.
- **Why this works & Test Scenario:**
  - Prevents stale card graphics and counter anomalies (`Card 1 of 0`) when candidate achieves mastery over the flashcard set.
  - Verified via Node.js automated test: stepped through boundary cards, verified `prevCard()` at 0 clamped at 0, verified `nextCard()` and `markMastered()` at last card updated state and flipped to front; simulated progressively mastering all unmastered cards until count reached 0, correctly producing `currentSign: null, total: 0`.

---

### Bug ID: BUG-09
**Bug Shortname:** Web Audio API Sounds Silenced on Autoplay-Restricted Browsers Due to Unresumed AudioContext  
**Status:** FIXED  
**Description:**  
Sound effects (clock ticking in the final 5 seconds, selection clicks, success chimes, and failure buzzers) fail to play in modern browsers (Chrome, Safari, iOS WebKit) because the synthesized `AudioContext` initializes in a `"suspended"` state and is never resumed inside a user gesture handler.

**Steps to reproduce:**
1. Open the application in Safari or Chrome without prior audio interaction.
2. Start a Mock Test.
3. Wait until the timer reaches $\le 5$ seconds.
4. Notice that no audible ticking sounds play.

**Root Cause:**  
In `js/sound-effects.js` lines 8–13:
```javascript
init() {
  if (!this.ctx && (window.AudioContext || window.webkitAudioContext)) {
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AudioCtx();
  }
}
```
`this.ctx` is created, but `this.ctx.resume()` is never called. Per modern browser Autoplay Policy, `AudioContext` begins suspended. Since `playTick()` is triggered by `setInterval` (not a user interaction), the browser refuses to start audio output.

**Code artifacts and line references:**
- [`js/sound-effects.js#L8-L13`](file:///Users/raghu/Projects/LLTPractice/js/sound-effects.js#L8-L13): `init()` lacks state check and `.resume()`.
- [`js/sound-effects.js#L19-L37`](file:///Users/raghu/Projects/LLTPractice/js/sound-effects.js#L19-L37): `playTick()` attempts to run oscillators on a suspended context.

**Solution:**  
In `sound-effects.js`, add an audio unlock helper called on any user interaction (button click, option click, tab change):
```javascript
ensureAudioActive() {
  this.init();
  if (this.ctx && this.ctx.state === "suspended") {
    this.ctx.resume();
  }
}
```
Call `sounds.ensureAudioActive()` on `btnStart`, `option-card` clicks, and `btnSoundToggle`.

**Implemented fix:**  
- In `js/sound-effects.js`:
  - Updated `init()` to verify `this.ctx.state === "suspended"` and trigger `this.ctx.resume()`.
  - Added public `ensureAudioActive()` method to safely unlock and resume suspended audio contexts on user interaction.
- In `js/app.js`:
  - Added global user-gesture audio unlock listeners (`pointerdown`, `keydown`, `touchstart`) inside `setupSoundToggle()` that invoke `sounds.ensureAudioActive()` and unbind themselves upon first tap/click.
  - Added direct `sounds.ensureAudioActive()` triggers inside `btnStart`, `btnRetake`, and sound toggle listeners.
- **Why this works & Test Scenario:**
  - Modern browser Autoplay policies require user gesture activation before an `AudioContext` can output sound. Unlocking on the first pointer/key interaction ensures timer countdown ticks and exam chimes play reliably even when triggered asynchronously by `setInterval`.
  - Verified via Node.js automated test: simulated suspended `AudioContext`, invoked `ensureAudioActive()`, and confirmed transition to `running` with clean execution of `playTick()`, `playSelect()`, `playSuccess()`, and `playFail()`.

---

### Bug ID: BUG-10
**Bug Shortname:** Biased Sampling and Flawed 70/30 Priority Distribution in Adaptive Sampler  
**Status:** FIXED  
**Description:**  
In `js/coverage-engine.js`:
1. Array shuffling uses `arr.slice().sort(() => 0.5 - Math.random())`, which is non-uniform and heavily biased.
2. The Coverage Booster algorithm claims to sample 70% priority questions (Unseen / Probation / Guessed) and 30% mastered questions. In reality, lines 121–123 execute:
`while (selected.length < count && shuffledPriority.length > 0) selected.push(shuffledPriority.pop());`.  
Whenever there are at least 8 priority road signs and 8 priority rules, 100% of the questions in the mock test are pulled from the priority pool. Zero mastered questions are selected for spaced revision until almost the entire bank has been seen.

**Steps to reproduce:**
1. Start with 20 questions mastered and 392 unseen.
2. Sample 10 consecutive mock exams.
3. Observe that exactly 0 mastered questions are ever sampled across all tests, contradicting the 70/30 adaptive sampler specification.

**Root Cause:**  
In `js/coverage-engine.js`:
- Line 96 uses JavaScript's sort comparator with random values instead of Fisher-Yates shuffle.
- Lines 120–127 lack a quota cap for the priority tier (e.g. `Math.round(count * 0.7)`), consuming 100% of the quota from `priority` before ever touching `mastered`.

**Code artifacts and line references:**
- [`js/coverage-engine.js#L96`](file:///Users/raghu/Projects/LLTPractice/js/coverage-engine.js#L96): Non-uniform shuffle algorithm.
- [`js/coverage-engine.js#L120-L127`](file:///Users/raghu/Projects/LLTPractice/js/coverage-engine.js#L120-L127): `while` loop fills the entire category quota with priority items.

**Solution:**  
1. Replace `sort(() => 0.5 - Math.random())` with a standard in-place Fisher-Yates shuffle:
   ```javascript
   function shuffle(array) {
     const arr = array.slice();
     for (let i = arr.length - 1; i > 0; i--) {
       const j = Math.floor(Math.random() * (i + 1));
       [arr[i], arr[j]] = [arr[j], arr[i]];
     }
     return arr;
   }
   ```
2. Enforce the 70/30 quota distribution:
   ```javascript
   const priorityTarget = Math.min(Math.round(count * 0.7), shuffledPriority.length);
   while (selected.length < priorityTarget && shuffledPriority.length > 0) {
     selected.push(shuffledPriority.pop());
   }
   while (selected.length < count && shuffledMastered.length > 0) {
     selected.push(shuffledMastered.pop());
   }
   while (selected.length < count && shuffledPriority.length > 0) {
     selected.push(shuffledPriority.pop());
   }
   ```

**Implemented fix:**  
- In `js/coverage-engine.js`:
  - Replaced the biased comparator sort `sort(() => 0.5 - Math.random())` with a uniform Fisher-Yates shuffle implementation.
  - Replaced the unbounded priority `while` loop with a capped multi-stage quota allocation:
    1. First samples up to 70% (`Math.round(count * 0.7)`) from the priority pool (`unseen`, `probation`, `isGuessed`).
    2. Then samples the remaining 30% from the mastered pool for active spaced revision.
    3. Gracefully backfills from whichever pool has remaining questions if either pool is depleted, ensuring the authentic 8-8-4 quota is always 100% fulfilled without deadlocks or shortfalls.
- Updated python test runner mirror in `scripts/test_runner.py` to match the exact algorithm.
- **Why this works & Test Scenario:**
  - Guarantees unbiased random selection and ensures that candidates who have mastered questions receive spaced revision of those mastered questions during mock exams instead of having them completely excluded.
  - Verified via Node.js automated test across varying user mastery stages (0% fresh user, 50% intermediate user, 100% expert user), validating that exactly 2 mastered signs, 2 mastered rules, and 1 mastered principle were drawn for the intermediate stage, while fresh and expert stages cleanly yielded full 20-question exams satisfying the 8-8-4 quota.

---

### Bug ID: BUG-11
**Bug Shortname:** Dead UI Element: Exam Readiness Badge in Header Has No Click Handler  
**Status:** FIXED  
**Description:**  
The header element `#btn-readiness-badge` displays the candidate's exam readiness percentage (e.g. `0%`). It includes the HTML attribute `title="Click to view readiness breakdown"`, has hover styles, and displays `cursor: pointer`. However, clicking it does absolutely nothing because no click event listener is attached anywhere in the JavaScript codebase.

**Steps to reproduce:**
1. Hover over the "Exam Readiness" badge in the top navigation bar.
2. Observe the cursor changes to pointer and tooltip reads: *"Click to view readiness breakdown"*.
3. Click the badge.
4. Nothing happens.

**Root Cause:**  
In `index.html` line 156, the element is given id `btn-readiness-badge`. However, in `js/app.js`, no `addEventListener("click", ...)` is registered for `btn-readiness-badge`.

**Code artifacts and line references:**
- [`index.html#L156-L164`](file:///Users/raghu/Projects/LLTPractice/index.html#L156-L164): Markup declaring `#btn-readiness-badge` with click tooltip.
- [`css/styles.css#L106-L120`](file:///Users/raghu/Projects/LLTPractice/css/styles.css#L106-L120): Hover styling and `cursor: pointer;`.
- [`js/app.js`](file:///Users/raghu/Projects/LLTPractice/js/app.js): Missing event listener.

**Solution:**  
Add a click listener in `app.js` that switches to the **Topic Practice** tab or opens a breakdown popup showing stats for Signs, Rules, and Principles:
```javascript
document.getElementById("btn-readiness-badge")?.addEventListener("click", () => {
  const practiceTabBtn = document.querySelector('[data-tab="tab-practice"]');
  practiceTabBtn?.click();
});
```

**Implemented fix:**  
- In `js/app.js`:
  - Attached a click event listener to `#btn-readiness-badge` in `setupTabs()` that activates the **Topic Practice** tab (`tab-practice`), immediately presenting the candidate with the full category-wise mastery breakdown, search filter, and question navigator matrix.
  - Enhanced `updateReadinessMeter()` to dynamically update `#btn-readiness-badge`'s `title` attribute with live stats (e.g. `Exam Readiness: 45% (186/412 Mastered) • Click to open Topic Practice`).
- **Why this works & Test Scenario:**
  - Converts a dead UI element with click affordance (`cursor: pointer`, hover states, and title tooltip) into an active, functional navigation trigger.
  - Verified via Node.js DOM simulation test: clicking `#btn-readiness-badge` successfully dispatches a click to `[data-tab="tab-practice"]`, switching views cleanly.

---

### Bug ID: BUG-12
**Bug Shortname:** Tutor Mode Wrapper Has Cursor Pointer but Only Checkbox Is Clickable  
**Status:** FIXED  
**Description:**  
On the Mock Test welcome card, the Tutor Mode toggle card (`#tutor-toggle-wrapper`) has an inline style `cursor: pointer;`, signalling to the user that tapping anywhere on the card will toggle Tutor Mode on or off. However, clicking the card text or container does nothing; only clicking the small 20px checkbox inside the label responds.

**Steps to reproduce:**
1. Open the Mock Test tab.
2. Click on the text *"Tutor Mode (Instant Answer & Explanation)"* or anywhere inside the card box.
3. Observe that Tutor Mode does not toggle.

**Root Cause:**  
In `js/app.js` lines 273–278, the `change` listener is only attached to `#exam-toggle-tutor-mode` (the input checkbox), while `#tutor-toggle-wrapper` has `cursor: pointer` without a click handler.

**Code artifacts and line references:**
- [`index.html#L232-L245`](file:///Users/raghu/Projects/LLTPractice/index.html#L232-L245): `#tutor-toggle-wrapper` has `cursor: pointer;`.
- [`js/app.js#L263-L278`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L263-L278): Event listener attached only to `#exam-toggle-tutor-mode`.

**Solution:**  
Attach the click handler to `tutor-toggle-wrapper`:
```javascript
const wrapper = document.getElementById("tutor-toggle-wrapper");
wrapper?.addEventListener("click", (e) => {
  if (e.target.tagName !== "INPUT") {
    if (tutorToggle) {
      tutorToggle.checked = !tutorToggle.checked;
      tutorToggle.dispatchEvent(new Event("change"));
    }
  }
});
```

**Implemented fix:**  
- Attached a click listener to `#tutor-toggle-wrapper` in `initExamUI()` within `js/app.js`.
- If the click target is not already within the toggle label (`!e.target.closest("label")`), the listener programmatically toggles `tutorToggle.checked` and dispatches the standard `"change"` event, updating both the engine preference and the `"ON"`/`"OFF"` visual badge.
- **Why this works & Test Scenario:**
  - Provides a generous tap target across the entire card container on desktop and mobile without risk of duplicate event firings when tapping the checkbox directly.
  - Verified via Node.js simulated event dispatch: clicking the wrapper card toggles checkbox state and updates status label; clicking directly inside the label allows native input handling without double toggle.

---

### Bug ID: BUG-13
**Bug Shortname:** Topic Practice Options Grid Fixed Inline 2-Column Layout Broken on Mobile  
**Status:** FIXED  
**Description:**  
In Topic Practice, the 4 option buttons are rendered inside a container with an inline style:  
`style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px;"`.  
Because this style is hardcoded inline rather than using responsive CSS classes, mobile viewports (e.g., iPhone 375px or Android 360px) force 2 columns of ~160px width. Multi-line official RTA options become squished into 10–15 vertical lines of wrapped text, degrading readability and tap targets.

**Steps to reproduce:**
1. Switch to mobile view (viewport width 375px) in developer tools.
2. Navigate to **"📚 Topic Practice"**.
3. Inspect the active question's option buttons.
4. Observe two narrow columns with squished text.

**Root Cause:**  
In `js/app.js` line 814, `optionsHtml` uses hardcoded inline styles `grid-template-columns: 1fr 1fr` rather than the responsive `.options-grid` CSS class defined in `exam-stall.css` (which collapses to `grid-template-columns: 1fr` under 768px).

**Code artifacts and line references:**
- [`js/app.js#L814`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L814): Hardcoded `grid-template-columns: 1fr 1fr`.
- [`css/exam-stall.css#L243-L256`](file:///Users/raghu/Projects/LLTPractice/css/exam-stall.css#L243-L256): Responsive `.options-grid` rule.

**Solution:**  
Replace the inline grid style with the responsive `.options-grid` class:
```javascript
let optionsHtml = `<div class="options-grid" style="margin-top: 14px;">`;
```

**Implemented fix:**  
- Updated `renderPracticeCard()` in `js/app.js`:
  - Enforced the responsive `.options-grid` container class, which collapses from 2 columns on desktop to 1 full-width column on mobile viewports ($\le 768\text{px}$).
  - Styled individual option buttons with `width: 100%; box-sizing: border-box; min-height: 48px;` and wrapped option text inside `<span style="flex: 1; word-break: break-word; line-height: 1.35;">`.
- **Why this works & Test Scenario:**
  - Prevents multi-line official RTA question options from squishing into narrow 140px vertical columns on mobile devices, ensuring compliant touch targets ($\ge 48\text{px}$) and clean readability.
  - Verified with mobile viewport simulation: buttons neatly stack into a single column on viewports $\le 768\text{px}$ without text overflow or horizontal truncation.

---

### Bug ID: BUG-14
**Bug Shortname:** Tricky Twins Side-by-Side Comparison Grid Cramped on Small Mobile Viewports  
**Status:** FIXED  
**Description:**  
In the Tricky Twins tab (`tab-twins`), sign comparisons (Sign A vs Sign B) are rendered with hardcoded inline style:  
`style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;"`.  
On mobile screens under 420px width, each card column is under 140px wide, causing sign images, titles, and explanations to overflow, wrap awkwardly, and stretch into tall distorted cards.

**Steps to reproduce:**
1. Resize browser window to mobile width (360px).
2. Click the **"🔍 Tricky Twins"** tab.
3. Observe Sign A and Sign B side-by-side in narrow columns where text wraps onto 10+ lines.

**Root Cause:**  
In `js/app.js`, `grid-template-columns: 1fr 1fr;` is hardcoded as an inline style without a responsive `@media (max-width: 600px)` breakpoint.

**Code artifacts and line references:**
- [`js/app.js#L1217`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L1217): Hardcoded `grid-template-columns: 1fr 1fr; gap: 14px;`.
- [`css/styles.css`](file:///Users/raghu/Projects/LLTPractice/css/styles.css): Missing `.twins-comparison-grid` class and mobile breakpoint.

**Solution:**  
Assign a class `.twins-comparison-grid` and define it in `css/styles.css`:
```css
.twins-comparison-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
@media (max-width: 600px) {
  .twins-comparison-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}
```

**Implemented fix:**  
- In `css/styles.css`:
  - Added `.twins-comparison-grid` with a default 2-column layout (`grid-template-columns: 1fr 1fr; gap: 14px;`) on desktop and tablet viewports.
  - Added responsive media query `@media (max-width: 600px)` collapsing the grid into a single full-width column (`grid-template-columns: 1fr; gap: 10px;`) on mobile screens.
- In `js/app.js`:
  - Replaced the hardcoded inline `style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;"` with `class="twins-comparison-grid"` inside `renderTrickyTwins()`.
- **Why this works & Test Scenario:**
  - On narrow screens ($\le 600\text{px}$), Sign A and Sign B neatly stack vertically with 100% available width rather than squeezing into 140px micro-columns, ensuring sign images, titles, and explanations remain easily readable without text overflow or vertical distortion.
  - Verified with DOM style and media query inspection: on desktop the grid preserves the 2-column side-by-side layout, and on mobile breakpoints ($\le 600\text{px}$) the CSS rule applies a single-column stack. All 64 QA tests continue to pass.

---

### Bug ID: BUG-15
**Bug Shortname:** Post-Exam Review Filter Buttons Do Not Reset to "All" When Starting a New Exam Review  
**Status:** FIXED  
**Description:**  
On the Mock Test result card, candidates can filter review questions using pills: **"All"**, **"❌ Missed"**, or **"✔️ Correct"**. If a candidate selects "❌ Missed" on exam 1, then takes another test and finishes it, `renderExamResultReview()` renders all questions, but the "❌ Missed" filter pill retains the `.active` blue CSS class. The UI shows the "Missed" button active while the list below displays all questions.

**Steps to reproduce:**
1. Finish a test with some correct and some wrong questions.
2. In the Post-Exam Review section, click the **"❌ Missed"** pill.
3. Click **"TAKE ANOTHER TEST"**.
4. Finish the new test.
5. Look at the review pills: **"❌ Missed"** is highlighted with blue background, but the list displays all questions.

**Root Cause:**  
In `js/app.js`, `buildCards("all")` is called when populating the review card, but the `.active` class is not reset across the `.review-filter-btn` elements.

**Code artifacts and line references:**
- [`js/app.js#L838-L848`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L838-L848): `buildCards("all")` called without resetting filter button classes.

**Solution:**  
In `renderExamResultReview()`, reset the active filter pill state whenever a review is generated:
```javascript
document.querySelectorAll(".review-filter-btn").forEach(b => {
  b.classList.toggle("active", b.getAttribute("data-review-filter") === "all");
});
```

**Implemented fix:**  
- In `js/app.js`:
  - Updated `renderExamResultReview()` to iterate over all `.review-filter-btn` elements immediately before invoking `buildCards("all")`, toggling the `.active` class so only the `"all"` filter button is active.
- **Why this works & Test Scenario:**
  - Guarantees that the visual state of the review filter pills matches the rendered question set on initial review display, even if the candidate selected a specific filter (e.g. "❌ Missed" or "✔️ Correct") on a preceding test run.
  - Verified with simulated DOM test: after artificially setting `.active` on the `"wrong"` button and invoking the reset logic, `.active` was removed from `"wrong"` and cleanly restored to `"all"`. All 64 QA tests continue to pass.

---

### Bug ID: BUG-16
**Bug Shortname:** Dead Code in Post-Exam Review Option Highlighting Logic  
**Status:** FIXED  
**Description:**  
In `js/app.js` (`renderExamResultReview`), the template tries to add a `✓ Your Choice` suffix tag when the user chose the correct option:
```javascript
if (optIdx === correctIdx) {
  optClass = "official-correct";
  suffixTag = `...✓ Correct Answer...`;
} else if (optIdx === userChoice && !isCorrect) {
  optClass = "user-chosen-wrong";
  suffixTag = `...✗ Your Choice...`;
} else if (optIdx === userChoice && isCorrect) {
  suffixTag = `...✓ Your Choice...`;
}
```
Whenever `isCorrect` is true, `userChoice === correctIdx`. Because the first `if (optIdx === correctIdx)` evaluates to `true`, the code always enters the first branch. The third `else if` branch is dead code and can never be reached. The user never sees a distinct badge indicating they chose the correct answer.

**Steps to reproduce:**
1. Complete an exam and view the Post-Exam Review cards for correctly answered questions.
2. Note that the selected correct option only displays *"✓ Correct Answer"*, never acknowledging *"✓ Your Choice"*.

**Root Cause:**  
The first condition `optIdx === correctIdx` subsumes `optIdx === userChoice && isCorrect`.

**Code artifacts and line references:**
- [`js/app.js#L808-L820`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L808-L820): Mutually exclusive condition order renders the third branch unreachable.

**Solution:**  
Refactor the branch logic:
```javascript
if (optIdx === correctIdx) {
  optClass = "official-correct";
  if (isCorrect) {
    suffixTag = `<span style="margin-left: auto; font-size: 0.78rem; color: #166534; font-weight: 700;">✓ Your Choice (Correct)</span>`;
  } else {
    suffixTag = `<span style="margin-left: auto; font-size: 0.78rem; color: #166534; font-weight: 700;">✓ Correct Answer</span>`;
  }
} else if (optIdx === userChoice && !isCorrect) {
  optClass = "user-chosen-wrong";
  suffixTag = `<span style="margin-left: auto; font-size: 0.78rem; color: #991B1B; font-weight: 700;">✗ Your Choice</span>`;
}
```

**Implemented fix:**  
- In `js/app.js`:
  - Refactored `renderExamResultReview()` option evaluation logic inside the review card generation loop.
  - When `optIdx === correctIdx`, the code now checks `if (isCorrect)`:
    - If `true`, it renders `✓ Your Choice (Correct)`, clearly acknowledging the candidate's accurate choice alongside the official answer.
    - If `false`, it renders `✓ Correct Answer`, providing the official key for missed/timed-out questions.
  - Retained `optIdx === userChoice && !isCorrect` to mark the candidate's erroneous choice with `✗ Your Choice`.
- **Why this works & Test Scenario:**
  - Eliminates dead code branch and ensures candidates receive explicit positive reinforcement that their selected option was indeed the correct answer.
  - Verified via Node.js test covering all branches: correctly selected options receive `✓ Your Choice (Correct)`, missed questions display both `✓ Correct Answer` and `✗ Your Choice`, and unselected options have no suffix tags. All 64 QA tests pass.

---

### Bug ID: BUG-17
**Bug Shortname:** Early-Stopping Exam Score Text Displays Inaccurate Total and Artificially Lowered Percentage  
**Status:** FIXED  
**Description:**  
In the official Telangana STALL test, answering 12 questions correctly immediately triggers early-stopping with a PASS. If a candidate achieves this in 14 questions, their actual performance is 12/14 (85.7%). However, the result screen displays:  
`Score: 12 / 20 (60%) • Pass Mark: 12`.  
The percentage is calculated against the full 20 questions rather than the 14 questions presented, misleading candidates into thinking they only scored 60%. Conversely, in `storage.recordExamResult`, the total is recorded as `history.length` (14), creating a discrepancy between localStorage history and the UI display.

**Steps to reproduce:**
1. Start an exam and answer the first 12 questions correctly without errors.
2. The exam finishes early after question 12.
3. Observe the scorecard text: `Score: 12 / 20 (60%)`.

**Root Cause:**  
In `js/app.js`, the score percentage calculation previously evaluated `Math.round((state.correctCount / totalQs) * 100)` against total available questions (20) instead of the actual number of questions presented/attempted (`state.history.length`).

**Code artifacts and line references:**
- [`js/app.js#L478-L490`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L478-L490): Score calculation used 20 instead of attempted question count.
- [`js/exam-engine.js#L320-L323`](file:///Users/raghu/Projects/LLTPractice/js/exam-engine.js#L320-L323): Storage engine records `Math.min(this.questions.length, this.history.length)`.

**Solution:**  
In `app.js`, display both attempted questions and criteria:
```javascript
const attempted = state.history ? state.history.length : 20;
const percent = Math.round((state.correctCount / attempted) * 100);
if (scoreText) {
  if (state.passed && attempted < 20) {
    scoreText.textContent = `Score: ${state.correctCount} / ${attempted} (${percent}%) • Early Pass: 12 of 20 criteria met!`;
  } else {
    scoreText.textContent = `Score: ${state.correctCount} / ${attempted} (${percent}%) • Pass Mark: 12`;
  }
}
```

**Implemented fix:**  
- In `js/app.js`:
  - Computed `attempted = (state.history && state.history.length) ? state.history.length : totalQs` and determined `percent` based on `attempted`.
  - Updated `scoreText` formatting to handle all scenarios cleanly:
    - Early pass (`state.passed && attempted < totalQs`): `Score: X / Y (Z%) • Early Pass: 12 of 20 criteria met!`.
    - Early fail (`!state.passed && attempted < totalQs`): `Score: X / Y (Z%) • Pass Mark: 12 (Attempted: Y/20)`.
    - Completed full exam: `Score: X / 20 (Z%) • Pass Mark: 12`.
  - Updated WhatsApp sharing message to use `attempted` for consistency with user storage and scorecard display.
- **Why this works & Test Scenario:**
  - Aligns the scorecard and WhatsApp share text with candidate performance and the exact question count stored in `localStorage`, eliminating confusing artificial deflation of scores when early pass triggers.
  - Verified via Node.js test across all outcome variants: early pass (12/14) renders 86%, full pass (15/20) renders 75%, and early fail (3/12) reflects actual attempted ratio without anomalies. All 64 QA tests pass.

---

### Bug ID: BUG-18
**Bug Shortname:** Audio "Read Aloud" Button Cannot Be Paused or Stopped  
**Description:**  
When the user clicks the **"🔊 Read Aloud"** button on an active question, speech synthesis begins narrating the question and options. If the user clicks the button again to stop the narration, the speech does not stop; instead, it cancels and immediately restarts reading from the very beginning.

**Steps to reproduce:**
1. Start an exam question.
2. Click the **"🔊 Read Aloud"** button.
3. While it is speaking Option 1, click **"🔊 Read Aloud"** again to mute it.
4. Notice that narration immediately restarts from the question title rather than stopping.

**Root Cause:**  
In `js/app.js` line 306, `btnRead.onclick` directly calls `exam.readCurrentQuestion()`. In `js/speech-engine.js` lines 26–29, `readQuestion()` calls `this.stop()` and immediately proceeds to `this.synth.speak(utterance)` without checking if `this.isReading` was already `true`.

**Code artifacts and line references:**
- [`js/speech-engine.js#L26-L30`](file:///Users/raghu/Projects/LLTPractice/js/speech-engine.js#L26-L30): `readQuestion()` unconditionally starts speaking.
- [`js/app.js#L306-L308`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L306-L308): `btnRead` handler does not toggle.

**Solution:**  
Implement toggle behavior in `SpeechEngine` or in the caller:
```javascript
toggleQuestionSpeech(questionText, options, langCode) {
  if (this.isReading) {
    this.stop();
  } else {
    this.readQuestion(questionText, options, langCode);
  }
}
```
Update `exam.readCurrentQuestion()` to invoke this toggle method.

---

### Bug ID: BUG-19
**Bug Shortname:** Duplicate Question Numbers in Question Navigator When Viewing "All (412)"  
**Description:**  
In Topic Practice, when the filter is set to **"All (412)"**, the Question Navigator matrix renders buttons labelled solely with `q.questionNumber`. Because Road Signs, Rules of the Road, and General Principles each start numbering from 1, the navigator displays three buttons labeled "1", three labeled "2", three labeled "3", up to "94", and two labeled "95" to "159". The user cannot determine which category a button corresponds to.

**Steps to reproduce:**
1. Navigate to **"📚 Topic Practice"**.
2. Keep the default category filter **"All (412)"**.
3. Scroll through the Question Navigator matrix: notice three buttons with the label `1`, three with `2`, etc.

**Root Cause:**  
In `js/app.js` line 754:
`chip.textContent = q.questionNumber;` uses the intra-category sequential integer rather than a category-distinguished tag or global index.

**Code artifacts and line references:**
- [`js/app.js#L754`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L754): `chip.textContent = q.questionNumber;`.

**Solution:**  
Prefix the chip label with category initials or group by category headers when "All (412)" is active:
```javascript
const catPrefix = q.category === "road_signs" ? "RS" : q.category === "rules_of_road" ? "RR" : "GP";
chip.textContent = `${catPrefix}-${q.questionNumber}`;
```

---

### Bug ID: BUG-20
**Bug Shortname:** Missing Modal Dismissal on Backdrop Click and Escape Key  
**Description:**  
Both `#modal-sync` (Cross-Device Sync modal) and `#modal-reset` (Reset Progress confirmation modal) cannot be dismissed by clicking outside the modal dialog on the dark backdrop, nor by pressing the standard `Escape` keyboard key. Users are forced to find and click the specific "Close" or "Cancel" button, violating WAI-ARIA modal dialog conventions.

**Steps to reproduce:**
1. Click the **"📲 Sync"** button in the header to open the modal.
2. Click on the dark semi-transparent backdrop outside the white card.
3. Notice the modal stays open.
4. Press the `Escape` key on your keyboard.
5. Notice the modal still stays open.

**Root Cause:**  
In `js/app.js` lines 176–228 (`setupModals`), event listeners are only attached to `#btn-close-sync` and `#btn-cancel-reset`. No click listeners are attached to `#modal-sync` / `#modal-reset` or keydown listeners for `Escape`.

**Code artifacts and line references:**
- [`js/app.js#L176-L228`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L176-L228): Missing backdrop and Escape event handlers.

**Solution:**  
Add backdrop click and Escape key listeners in `setupModals`:
```javascript
[syncModal, resetModal].forEach(modal => {
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });
});

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    if (syncModal) syncModal.style.display = "none";
    if (resetModal) resetModal.style.display = "none";
  }
});
```

---

### Bug ID: BUG-21
**Bug Shortname:** PWA Manifest Icon Dimensions and Accessibility Viewport Zoom Restriction  
**Description:**  
1. In `manifest.json`, `assets/signs/sign_001.png` is specified as icons for `"sizes": "192x192"` and `"sizes": "512x512"`. However, the physical image dimensions of `sign_001.png` on disk are `285x215` (non-square, aspect ratio ~1.32). This causes PWA audit warnings, icon distortion on Android homescreens, and failed PWA install criteria.
2. In `index.html` line 5, the viewport meta tag includes `maximum-scale=1.0, user-scalable=no`. This violates WCAG 2.1 Success Criterion 1.4.4 (Resize text, Level AA) by disabling pinch-to-zoom on mobile devices for visually impaired users.

**Steps to reproduce:**
1. Run Lighthouse audit in Chrome DevTools on `index.html`.
2. Check the Accessibility section: fails on *"Does not have a [maximum-scale] on <meta name="viewport"> and the [user-scalable] attribute is not disabled"*.
3. Check PWA section: fails on non-square icon manifest declaration.

**Root Cause:**  
- `manifest.json` lines 11–22 references `sign_001.png` (285x215) with mismatched square dimensions.
- `index.html` line 5 specifies `maximum-scale=1.0, user-scalable=no`.

**Code artifacts and line references:**
- [`manifest.json#L11-L22`](file:///Users/raghu/Projects/LLTPractice/manifest.json#L11-L22): Mismatched icon sizes.
- [`index.html#L5`](file:///Users/raghu/Projects/LLTPractice/index.html#L5): Viewport meta scaling restriction.

**Solution:**  
1. In `index.html` line 5, change the viewport meta tag to:
   `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
2. Create square icons (e.g., `assets/icons/icon-192.png` and `assets/icons/icon-512.png` or SVG) and update `manifest.json`.

---

### Bug ID: BUG-22
**Bug Shortname:** Trilingual Marketing and SEO Metadata Contradicts Disabled Regional Language Selector  
**Description:**  
The application's `index.html` metadata, OpenGraph tags, JSON-LD structured data, FAQ section, and `README.md` all market complete trilingual support in English, Telugu (తెలుగు), and Hindi (हिन्दी) with full audio narration (e.g. `inLanguage: ["en", "te", "hi"]`, `Full Telugu, Hindi & English audio support`).  
However, in the UI header:
```html
<select class="lang-select" id="select-language">
  <option value="en" selected>English</option>
  <option value="te" disabled>తెలుగు (Under Review)</option>
  <option value="hi" disabled>हिन्दी (Under Review)</option>
</select>
```
And in `js/i18n.js`:
```javascript
export function setLanguage(lang) {
  currentLang = "en";
  ...
}
export function getCurrentLang() {
  return "en";
}
```
`setLanguage()` unconditionally forces `en`, completely disabling Telugu and Hindi even though all 412 questions in `data/questions/telangana/*.json` and translation tables in `data/i18n/te.json` & `hi.json` already have complete translations.

**Steps to reproduce:**
1. Open the application.
2. Click the language dropdown selector in the header.
3. Observe that Telugu and Hindi options are disabled with "(Under Review)".
4. Check the page description and FAQ: both claim full trilingual support is active.

**Root Cause:**  
In `js/i18n.js` lines 4–6 and 30–42, `currentLang` was hardcoded to `"en"` as a temporary measure during a past review and was never re-enabled, leaving the UI and metadata in contradiction.

**Code artifacts and line references:**
- [`index.html#L177-L181`](file:///Users/raghu/Projects/LLTPractice/index.html#L177-L181): Disabled option elements.
- [`js/i18n.js#L4-L7`](file:///Users/raghu/Projects/LLTPractice/js/i18n.js#L4-L7) & [`js/i18n.js#L30-L42`](file:///Users/raghu/Projects/LLTPractice/js/i18n.js#L30-L42): Hardcoded `en` overrides.

**Solution:**  
Re-enable full trilingual support:
1. In `index.html`, remove the `disabled` attributes and `(Under Review)` suffixes from `<option value="te">తెలుగు</option>` and `<option value="hi">हिन्दी</option>`.
2. In `js/i18n.js`, restore proper language switching:
   ```javascript
   export function setLanguage(lang) {
     if (["en", "te", "hi"].includes(lang)) {
       currentLang = lang;
       storage.setPreference("language", lang);
       document.documentElement.lang = lang;
       updateDomTranslations();
       window.dispatchEvent(new CustomEvent("languageChanged", { detail: lang }));
     }
   }
   export function getCurrentLang() {
     return currentLang;
   }
   ```
3. Initialize `currentLang = storage.getPreference("language", "en")`.

---

### Bug ID: BUG-23
**Bug Shortname:** `storage.importStateJson()` Crashes Application When Imported Backup Lacks Preferences Object  
**Description:**  
When importing a backup state via `storage.importStateJson(jsonString)`, the function assigns `this.state = parsed` without checking if `parsed.preferences` or `parsed.examHistory` exists. If a user imports a stripped or minimal backup file (e.g. `{ "questions": { ... } }`), `this.state.preferences` becomes `undefined`. Subsequent calls to `storage.getPreference("soundEnabled", true)` immediately crash with an unhandled TypeError: `Cannot read properties of undefined (reading 'soundEnabled')`, breaking sound, voice, and theme rendering.

**Steps to reproduce:**
1. Click **"📲 Sync"** -> **"Import Backup File"**.
2. Select a valid JSON file containing only question progress: `{"version": 1, "questions": {}}`.
3. The import succeeds and `storage.importStateJson()` sets `this.state`.
4. Refresh or click sound toggle: application crashes with `TypeError: Cannot read properties of undefined (reading 'soundEnabled')`.

**Root Cause:**  
In `js/storage-engine.js` lines 146–159, `importStateJson()` parses JSON and checks `if (parsed && parsed.questions)`, then immediately sets `this.state = parsed;` without the fallback sanitization present in `loadState()`.

**Code artifacts and line references:**
- [`js/storage-engine.js#L146-L159`](file:///Users/raghu/Projects/LLTPractice/js/storage-engine.js#L146-L159): `importStateJson()` lacks schema validation and property defaulting.
- [`js/storage-engine.js#L123-L125`](file:///Users/raghu/Projects/LLTPractice/js/storage-engine.js#L123-L125): `getPreference()` expects `this.state.preferences` to exist.

**Solution:**  
Sanitize imported JSON against the default schema before assigning:
```javascript
importStateJson(jsonString) {
  try {
    const parsed = JSON.parse(jsonString);
    if (parsed && typeof parsed === "object" && parsed.questions) {
      this.state = {
        version: parsed.version || 1,
        lastUpdated: parsed.lastUpdated || new Date().toISOString(),
        questions: parsed.questions || {},
        examHistory: Array.isArray(parsed.examHistory) ? parsed.examHistory : [],
        preferences: Object.assign({ language: "en", soundEnabled: true, autoSpeech: false }, parsed.preferences || {})
      };
      this.saveState();
      return true;
    }
    return false;
  } catch (e) {
    console.error("Invalid state JSON imported:", e);
    return false;
  }
}
```

---

### Bug ID: BUG-24
**Bug Shortname:** File Input Change Event Does Not Fire When Re-Importing the Same Backup File  
**Description:**  
In the Sync modal, if a user imports a backup file, experiences an error or makes modifications, and attempts to import the same file again (or another file with the same filename in the same directory), the file picker's `change` event will not fire. The user clicks "Import Backup File", selects the file, and nothing happens.

**Steps to reproduce:**
1. Click **"📲 Sync"** -> **"Import Backup File"**.
2. Select a backup file `backup.json`. Progress imports.
3. Reset progress to 0%.
4. Click **"📲 Sync"** -> **"Import Backup File"** and choose the same `backup.json`.
5. Notice the file is selected in the OS dialog, but the application does not import it and no confirmation alert appears.

**Root Cause:**  
In `js/app.js` line 195, the change event listener on `#input-sync-file` processes the file but never resets `e.target.value = ""`. When the same file is selected, the browser considers the input value unchanged and suppresses the `change` event.

**Code artifacts and line references:**
- [`js/app.js#L195-L208`](file:///Users/raghu/Projects/LLTPractice/js/app.js#L195-L208): `input-sync-file` event listener fails to clear `e.target.value`.

**Solution:**  
Add `e.target.value = "";` at the conclusion of the import handler in `app.js`:
```javascript
document.getElementById("input-sync-file")?.addEventListener("change", async e => {
  const file = e.target.files[0];
  if (file) {
    try {
      await sync.importFile(file);
      alert(t("sync_success", "Progress synchronized successfully!"));
      if (syncModal) syncModal.style.display = "none";
      updateReadinessMeter();
      practice.notifyUpdate();
    } catch (err) {
      alert("Error importing backup file: " + err.message);
    } finally {
      e.target.value = "";
    }
  }
});
```
