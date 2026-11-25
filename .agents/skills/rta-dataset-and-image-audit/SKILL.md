---
name: rta-dataset-and-image-audit
description: >-
  Audits Telangana RTA question datasets and extracted sign/scenario PNGs for
  PDF multi-line option wrapping leaks, split or glued choices, wrong answer
  indexes, and misaligned images. Use when modifying data/questions/telangana/*.json,
  tricky-twins.json, assets/signs/*.png, or PDF extraction scripts under scripts/.
---

# RTA Dataset & Visual Sign Audit

`scripts/test_runner.py` checks schema, counts (412 total), and file existence,
but does not detect semantic option corruption or swapped sign PNGs. Run this
audit whenever editing question banks, sign images, or PDF rebuild scripts.

## Step 1: Text, Option & Answer Integrity Scan

Run an inline Python check over `data/questions/telangana/*.json`:
1. **Option count & boundaries:** Assert exactly 4 non-empty options per language (`en`, `te`, `hi`).
2. **Split/glued option detection:** Flag options that:
   - End in hanging prepositions (`OF THE`, `TO THE`, `IN THE`, `AND`, `OR`) or glued fragments (e.g. `NONE OF TH`, `E ABOVE`, `PARKINGGHAT`, `ROADMAJOR`).
   - Contain two sentences joined by `.` without abbreviations (`A.C`, `L.L.R`, `D.L`, `M.V`, `E.G`).
   - Have trailing answer digits (`NONE OF THE ABOVE2`).
3. **Question text leak detection:** Flag road-sign `text.en` values that leak an answer option (e.g. `WHAT DOES THIS SIGN MEAN? SLIPPERY ROAD`).
4. **Explanation parity:** Confirm the official answer string (`options.en[answerIndex]`) matches `explanation.en` and `answerIndex` matches the source PDF answer column.

## Step 2: Visual Audit of Extracted Sign & Scenario PNGs

Because Pillow/ImageMagick may not be installed in the sandbox, build 5x5
contact sheets using Python stdlib (`zlib` + `struct`) in the conversation
`scratch/` directory and inspect them directly with `read_file`:
1. Confirm PDF `Do` image transforms sort in true question order on **every** page (verify Page 1 uses ascending `x` order just like Pages 2–15—never `reverse=True`).
2. Visually inspect each 25-sign contact sheet against `road-signs.json` Q1–Q94, plus any updated entries in `data/tricky-twins.json` and `data/popular-guides.json`.

## Step 3: Fix Upstream & Verify Downstream

1. Fix both the JSON/PNG files **and** the generator script (`scripts/rebuild_road_signs_images_and_dataset.py` or `scripts/rebuild_all_clean_datasets.py`) so future rebuilds do not regress.
2. Keep `"image"` paths in JSON clean (no `?v=...`), bump `ASSET_VER` in `js/app.js` and matching `?v=` query strings in `index.html`.
3. Run `python3 scripts/validate_workspace.py && PYTHONPATH=. python3 scripts/test_runner.py` and confirm all 64+ QA tests pass.
