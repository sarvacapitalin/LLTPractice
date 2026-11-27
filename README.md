# 🚦 Telangana RTA Learner's Licence (LLR) Practice Platform
### Official STALL Computerized Test Simulator • Hyderabad RTO (Telangana)

A complete, authentic, and mobile-friendly web application designed to prepare candidates for the **Telangana Road Transport Authority (RTA) Learner's Licence Test (LLR / STALL)** conducted across Hyderabad (Kondapur, Uppal, Mehdipatnam, Khairatabad, Malakpet, Medchal, Ibrahimpatnam) and all districts of Telangana.

---

## 🌟 Key Features

### 1. 🎯 Authentic RTA STALL Computerized Exam Simulator
- **Exact Official Structure**: 20 multiple-choice questions per test.
- **Stratified Category Quota**:
  - **8 Road Signs** (Mandatory, Cautionary, Informatory)
  - **8 Traffic Rules of the Road**
  - **4 General Driving Principles**
- **30-Second Countdown Timer per Question**:
  - 🟢 Green (>15s) $\to$ 🟡 Amber (6–15s) $\to$ 🔴 Red ($\le 5$s with audible warning ticks).
- **Early-Stopping Logic**:
  - Passing score: **12 correct out of 20 (60%)**.
  - Reaching 12 correct immediately ends the test with **PASS**.
  - Reaching 9 incorrect immediately ends the test with **FAIL**.
- **Two-Step Touch Submission**: Tap an option to select, then tap **"CONFIRM & NEXT"** to submit. Prevents accidental submissions on mobile touchscreens.
- **Scorecard & WhatsApp Share**: One-click sharing of test scorecards with family or instructors.

---

### 2. 🛡️ 95% Exam Readiness Tracker & 2-Streak Mastery System
Solves the common pitfall where a candidate passes 3–4 random mock tests while having seen only ~15% of the total question bank.
- **Coverage Goal**: Candidate must achieve **95% Readiness** ($\ge 391$ of 412 questions mastered) before being certified test-ready.
- **2-Streak Mastery Rule**:
  - Questions start as `Unseen`.
  - Answering correctly once moves a question to `Probation` (Streak 1).
  - Answering correctly **twice consecutively** certifies it as `Mastered` (Streak 2).
  - Any incorrect answer drops the streak back to 0 (Probation).
- **"🤔 I Guessed This" Flag**:
  - If a candidate selects an answer by luck and checks this box, the question remains in `Probation` even if correct, ensuring it will be re-tested until true mastery is achieved.
- **🔄 Reset Readiness to 0%**:
  - Candidate can reset all progress, streaks, and history with one click to restart preparation from scratch.
- **Coverage Booster Adaptive Sampler**:
  - When starting a mock test, the algorithm assigns 70% probability to Unseen, Probation, and Guessed questions, actively driving the candidate toward 95% readiness.

---

### 3. 🌐 Complete Telangana RTA Question Bank (412 Questions)
Covering 100% of the questions from the official Telangana RTA question bank PDFs:
- **94 Road Signs**: 43 Mandatory (including police & driver hand signals) + 37 Cautionary + 14 Informatory signs with extracted diagrams (`assets/signs/sign_001.png` to `sign_094.png`).
- **159 Traffic Rules of the Road**: Including junction/intersection scenario diagrams (`assets/scenarios/`).
- **159 General Driving Principles**: Defensive driving, night driving, parking, breakdown procedures, and first aid.
- **Language Status (English Active; Telugu/Hindi Temporarily Paused)**: Public UI and SEO pages currently serve verified **English** only while hybrid Telugu/Hindi strings inside the JSON banks undergo translation audit (JSON `te`/`hi` keys remain stored for QA schema parity).

---

### 4. 📲 Zero-Server Cross-Device "Scan-to-Sync" (Laptop $\leftrightarrow$ Mobile)
Practice seamlessly across multiple devices:
- Start studying on a laptop monitor during the day.
- Click **"Sync Devices"** to generate a compressed QR code.
- Scan the QR code with your mobile phone camera or import the JSON backup to continue practice on mobile while commuting.
- No logins, passwords, or cloud databases required; 100% private and stored in `localStorage`.

---

### 5. 📚 High-Impact Study Tools
- **Topic Practice**: Interactive 412-question browser with filters for Unseen, Missed (Probation), Mastered, and Guessed questions, complete with instant explanations.
- **94-Sign Flip Flashcards**: Interactive cards with sign graphics on the front and official meanings, do's, and don'ts on the back.
- **Tricky Twins**: Side-by-side comparisons of commonly confused signs (e.g. *No Parking* vs *No Stopping*, *Guarded* vs *Unguarded Level Crossings*, *1-Bar* vs *2-Bar Distance Markers*).
- **⚡ Rapid Cheatsheet**: Top 10 golden rules to review in 10 minutes right before walking into the RTO testing room.
- **🏢 Hyderabad RTO Guide**: Test-day checklist of documents to carry, token/biometric room workflow, and pitfalls to avoid.

---

### 6. 🔊 Audio Voice Narrator & Sound Effects
- **Web Speech API**: Speaks question and options aloud in Indian accents (`en-IN`, `te-IN`, `hi-IN`).
- **Web Audio API**: Synthesized ticking clock, selection clicks, and success chimes without loading external audio files.

---

## 🚀 How to Run Locally

This project is built with **100% vanilla modern web standards** (HTML5, CSS3, ES6 Modules). It has **zero dependencies**, requires no `npm install`, and works immediately in any modern web browser.

```bash
# 1. Navigate to the project folder
cd /path/to/LLTPractice

# 2. Start a simple local HTTP server (using Python 3 built-in server)
python3 -m http.server 8000

# 3. Open in your browser:
# Laptop browser: http://localhost:8000
# Mobile phone on same Wi-Fi: http://<YOUR_LAPTOP_IP>:8000
```

---

## 🌐 Free Internet Hosting (Deploy in 1 Click)

### Option 1: GitHub Pages (Recommended - 100% Free Forever)
1. Initialize git and push to a new GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial release of Telangana LLR practice website"
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
2. In your GitHub repository:
   - Go to **Settings** $\to$ **Pages**.
   - Under **Build and deployment** $\to$ **Source**, select `Deploy from a branch`.
   - Select Branch: `main`, Folder: `/ (root)`, and click **Save**.
3. Your website will be live in ~60 seconds at `https://<your-username>.github.io/<repo-name>/`!

### Option 2: Cloudflare Pages / Netlify / Vercel
- Drag and drop this project directory into [Cloudflare Pages](https://pages.cloudflare.com/) or [Netlify](https://www.netlify.com/).
- No build command required. Publish directory: `./`.

---

## 📁 Project Directory Layout

```
LLTPractice/
├── index.html                   # Dual-layout responsive SPA shell
├── manifest.json                # PWA configuration for home screen install
├── sw.js                        # Service worker for offline practice resilience
├── css/
│   ├── styles.css               # Main styling (accessible typography, responsive grid)
│   └── exam-stall.css           # Authentic RTA STALL computerized test styling
├── js/
│   ├── app.js                   # Application coordinator & event bindings
│   ├── i18n.js                  # Trilingual localization manager
│   ├── storage-engine.js        # LocalStorage state machine & streak tracker
│   ├── coverage-engine.js       # 95% readiness calculator & adaptive sampler
│   ├── exam-engine.js           # STALL exam logic, 30s timer, early stopping
│   ├── practice-engine.js       # 412 questions topic practice & explanation viewer
│   ├── flashcards-engine.js     # 94-sign flip drill
│   ├── tricky-twins-engine.js   # Side-by-side confusing sign viewer
│   ├── cheatsheet-engine.js     # 10-minute morning revision viewer
│   ├── sync-engine.js           # QR code & cross-device state synchronization
│   ├── qrcode-generator.js      # Zero-dependency SVG QR code generator
│   ├── speech-engine.js         # Web Speech API voice reader
│   └── sound-effects.js         # Web Audio API sound synthesizer
├── data/
│   ├── questions/telangana/
│   │   ├── road-signs.json      # 94 Road Signs questions
│   │   ├── rules-of-road.json   # 159 Traffic Rules questions
│   │   └── general-principles.json # 159 Driving Principles questions
│   ├── i18n/
│   │   ├── en.json              # English UI translation strings
│   │   ├── te.json              # Telugu UI translation strings
│   │   └── hi.json              # Hindi UI translation strings
│   ├── states.json              # State-specific passing rules & quotas
│   ├── rto-guide.json           # Hyderabad RTO testing procedures & checklist
│   ├── tricky-twins.json        # Confusing sign comparison data
│   ├── last-minute-cheatsheet.json # Top 10 golden rules
│   ├── audit_report.json        # Independent auditor certification report
│   └── qa_test_report.json      # Automated test execution report
├── assets/
│   ├── signs/                   # 94 extracted road sign PNG images (sign_001.png..sign_094.png)
│   └── scenarios/               # 20 extracted scenario diagram PNG images
└── scripts/                     # Data extraction and automated test runners
    └── test_runner.py           # Automated test suite
```

---

## 🏛️ Telangana RTA LLR Test Rules Reference

| Parameter | Official Telangana RTA Specification |
| :--- | :--- |
| **Test Format** | Screen Test for Aid to Learner's Licence (STALL) |
| **Total Questions** | 20 multiple choice questions |
| **Category Quota** | 8 Road Signs (40%) + 8 Traffic Rules (40%) + 4 Driving Principles (20%) |
| **Time per Question** | 30 seconds countdown (10 minutes total maximum) |
| **Passing Score** | 12 correct out of 20 (60%) |
| **Early Stopping** | Test terminates immediately upon reaching 12 correct (PASS) or 9 wrong (FAIL) |
| **Languages Active** | English (Telugu & Hindi temporarily paused in UI while translations are audited; official RTO kiosks support English, Telugu, Hindi/Urdu) |
| **Permitted Mistakes** | Maximum 8 mistakes before test termination |

---

## 👩‍💻 Developed with ❤️ for Telangana Learners
Designed specifically to empower learner drivers in Hyderabad and across Telangana to pass their computer test on the first attempt with 100% confidence!
