---
name: bug-audit-and-fix-loop
description: >-
  Structured workflow for auditing a codebase into bugs.md, fixing bugs one at a
  time with per-bug commits and optional cooldown pacing, and independently
  verifying every fix against the live codebase. Use when asked to audit bugs
  into bugs.md, run a sequential bug-fix loop, or independently verify prior fixes.
---

# Bug Audit, Sequential Fix Loop & Independent Verification

## Phase 1: Structured Audit (`bugs.md`)
For each bug discovered (logic, UI polish, responsiveness, accessibility, consistency), record:
- `Bug ID:` (`BUG-01`, `BUG-02`, ...)
- `Bug Shortname:`
- `Description:`
- `Steps to reproduce:`
- `Root Cause:`
- `Code artifacts and line references:`
- `Solution:` (optimal solution)

## Phase 2: Sequential Fix Loop
Process one bug at a time from `bugs.md`:
1. Implement the optimal fix in code.
2. Verify with workspace test suites and targeted unit/integration checks.
3. Update `bugs.md` with `**Status:** FIXED` and an `**Implemented fix:**` section explaining the fix, why it works, and the test scenario/steps.
4. Commit and push the individual bug fix before moving to the next bug.
5. If rate-limit pacing is requested (e.g., 15-minute wait between fixes), use the `schedule` tool (`DurationSeconds`) rather than shell `sleep`.

## Phase 3: Independent Verification Pass
When verifying fixes (especially after subsequent commits):
1. Do not trust prior status markers alone—inspect the live source files and run real module/DOM tests for every `BUG-XX` entry.
2. Check for regressions introduced by later commits.
3. If any fix is incomplete or regressed, reopen it in `bugs.md`, implement the optimal fix, re-verify, and re-close with updated notes.
