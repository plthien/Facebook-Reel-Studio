# PR #3 final self-review — G3_READY_FOR_REVIEW
Date: 2026-10-15 · Branch `design/ui-mockup-v2` · **Approval pending; not merged.**

## Baseline reproduced on 456b377b8dcc3b0696ff544fe17278e9d3165a86
- **F1 FAIL:** 105 selected IDs → only 100 Composer IDs, five silently omitted.
- **F2 FAIL:** 2020-01-01T09:00 returned no schedule errors and passed validation.
- **F3 FAIL:** Quick chips p2/p3 with targets p4/p3 after changing Page in Review.
- **F4 FAIL:** exact duplicate intent was a nonblocking warning; confirm remained allowed.

## Repairs verified
- **F1 PASS:** 50→50, 100→100; 105 blocked with explicit alert, 105 selections retained; no silent `slice(0,100)` at selection transfer or Quick toggle. Selections persist on cursor/filter/screen return; target cap is separate.
- **F2 PASS:** strict real-calendar ISO local time (+07:00, Asia/Ho_Chi_Minh) and UTC conversion; no invalid/past/exact-now/too-soon schedules; demo min lead 10 min with injectable clock; same checkTargets on all rows and final confirmation.
- **F3 PASS:** Quick page chips canonical, Review Page/Video identity selectors disabled and programmatic edit rejected. Quick one-video invariant and mismatch guards; per-target caption/title/time still editable. Batch asset selection survives switching mode.
- **F4 PASS:** exact canonical (Page, asset/variant, UTC, trimmed title, trimmed caption) duplicate is a blocking `DUPLICATE_INTENT` error, not warning; legitimate different occurrences/videos/Pages allowed. Every changed target invalidates successful preflight intent fingerprint; final demo confirm requires current successful validation and always creates zero jobs.
- Bounded synthetic cursor data, full 60-target review (25+25+10), unavailable/zero/stale metric separation, no attribution of IMPORTED Reels to arbitrary local assets, UNCERTAIN reconcile-only. Tablet collapsed navigation now has accessible labels.
- **Backend design:** repaired legacy spec J3/FR-009 "one job per Page" language. Proposed schema/ADR/API/OpenAPI add per-target keys, 100 target cap, atomic 422, 409 idempotency, READ-only calendar; all pending approval.

## Executed tests and evidence
- Latest code/test reviewed SHA: `59bb8a667861d1442bc8ff023abbcaa335328b98`.
- [Actions Chromium run #38720044131](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38720044131): `npm install --no-audit --no-fund`; `npm run test:contract` PASS (8 paths/79 refs); `npx playwright install --with-deps chromium`; `npm run test:ui` **19 PASS / 0 FAIL (16.1 seconds)**. Ubuntu 24.04, Node 22, Playwright 1.55.0, Chromium 140.0.7339.16.
- **23 screenshots committed** under `mockups/screenshots/`: exactly sized 1440×900 / 1024×768, with five full-page critical workflows. Inspected nine-screen contact sheet and Library/Calendar/Review/invalid state captures. No app-level horizontal overflow in tested viewports; user-facing mock controls never perform actual Meta writes.
- No live Meta test, real DB migration, service load benchmark or backend integration test was run. Synthetic fixture scale is design-only.

## PR diff scope / deferred
The PR contains docs/spec, ADR, OpenAPI, schema proposal, interactive HTML, Playwright/contract tests, GitHub Actions CI, package lockfile and screenshots. It does **not** promote UI v1, change unrelated repositories, contain secrets, merge PR #3 or implement P0/P1/P2/P3.
Deferred: cross-query select-all, calendar reschedule PATCH, speculative Meta metrics, inferred imported asset links. Remaining dependency: user approval for API/schema amendments and G3 freeze; separate P0 live capability gate blocks subsequent runtime implementation. No known F1–F4 blocker remains in the tested prototype.

**Decision: G3_READY_FOR_REVIEW (not G3_APPROVED).**
