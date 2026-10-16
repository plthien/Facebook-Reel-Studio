# Facebook Reels Studio UI v2 — Authoritative Freeze Manifest

## Current status — authoritative G3 freeze candidate (2026-10-15)

| Field | Verified result |
|---|---|
| Freeze candidate | **Facebook Reels Studio UI v2** |
| Gate status | **G3_READY_FOR_APPROVAL** |
| Approval status | **USER APPROVAL PENDING — NOT G3_APPROVED** |
| Repository | `plthien/Facebook-Reel-Studio` |
| Pull request | [PR #3](https://github.com/plthien/Facebook-Reel-Studio/pull/3) — OPEN, not merged |
| Branch / proposed base | `design/ui-mockup-v2` → `main` |
| UI implementation SHA (last HTML modification) | `1de100918abe00fa0776c36e8e63305a113ac208` |
| Targeted test-suite last-modification SHA | `7f99f2e5b21fc46f0f69d2f74ce169ea951b0635` |
| **CI-tested repository snapshot SHA** | **`3adf11d259df40687177623810e1b6d1cb7cb62f`** |
| Verified CI | [GitHub Actions run #38727389515](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38727389515) — **SUCCESS**, checked out `3adf11d259df40687177623810e1b6d1cb7cb62f` |
| Playwright | **35/35 PASS, 0 FAIL**, previous 19 tests + 16 targeted groups |
| Contract validation | **PASS**, 8 OpenAPI 3.1 routes / 79 schema references, legacy/schema checks |
| Screenshots | **37 non-empty tracked Chromium PNGs**: 18 baseline screen + 5 original workflow + 14 targeted |
| Covered screens | **9/9** — Dashboard, Fanpages, Video Library, Publish, Calendar, Reels, Analytics, Activity, Settings |
| Meta P0 | **NOT_RUN / BLOCKED_EXTERNAL** |
| Production backend | **NOT_IMPLEMENTED** (no real FastAPI/PostgreSQL/worker/Meta publishing integration) |

**Source and SHA interpretation:** `1de100918abe00fa0776c36e8e63305a113ac208` last changed the HTML UI. `7f99f2e5b21fc46f0f69d2f74ce169ea951b0635` last changed the targeted Playwright suite. **`3adf11d259df40687177623810e1b6d1cb7cb62f` is the complete source checkout actually tested** by the latest successful CI run, including both Playwright suites, contract validator and CI workflow. A subsequent documentation-only commit has a *different* final PR HEAD. To avoid embedding a commit's own SHA in that commit, consult the [live PR #3](https://github.com/plthien/Facebook-Reel-Studio/pull/3) and its updated description for the final documentation HEAD and its own CI run; do not claim that earlier CI tested future documentation edits.

### Actual test evidence

[Run #38727389515](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38727389515) on GitHub-hosted Ubuntu 24.04 used Node 22, Playwright 1.55.0 and Chromium 140.0.7339.16. Job logs confirm `npm ci --no-audit --no-fund`, `npm run test:contract`, `npx playwright install --with-deps chromium` and `npm run test:ui`, **35 passed in 16.2 seconds** and contract **PASS**. Test report and screenshot artifacts were uploaded. This is fixture/browser evidence only, **not** real Meta P0 proof.

### Screen and workflow acceptance

- **Quick Publisher:** full 50 Page fixture, 45 ACTIVE, 5 unavailable/unauthorized; searchable `p50` through browser UI, multi-select, filters and no loss of hidden selected Pages or caption/title/schedule; immutable Page and Video identity in Review.
- **Global sorting:** Library `created_at_desc/asc`, `filename_asc`; Reels `posted_at_desc` only, views sort visibly disabled until P0/P2 verification; Activity `scheduled_at_desc/asc`, `created_at_desc`. Fixture global sort precedes cursor paging without allocating 100k records for normal pages.
- **Hash navigation:** direct routes, Back/Forward, accurate sidebar/header, invalid hash fallback, no duplicate same-route history, drawer dismissal and unsent publisher draft retention.
- **Preserved F1–F4:** 50/100 selected assets transfer intact; 105 selection blocks with no silent truncation; strict scheduled dates/UTC/lead; Quick canonical intent; duplicate and stale preview blocking; 20 videos/10 Pages → 60 explicit targets, Review pagination 25+25+10. No actual jobs are created.
- 50 Pages, 10k assets, 100k Reels and 100k jobs are **synthetic design scale, not real backend performance evidence**.

## Screenshot manifest — 37 verified PNG files

File inventory checked against GitHub's **CI-tested commit tree** `3adf11d259df40687177623810e1b6d1cb7cb62f`. All expected paths are present, unique and non-empty. Baseline and targeted two-viewport PNGs use **1440×900** and **1024×768**; five original workflow captures are full-page.

| Baseline screen (9 × 2 = 18) | Actual 1440×900 / 1024×768 files |
|---|---|
| dashboard | [`dashboard-1440x900.png`](../../mockups/screenshots/dashboard-1440x900.png) · [`dashboard-1024x768.png`](../../mockups/screenshots/dashboard-1024x768.png) |
| pages | [`pages-1440x900.png`](../../mockups/screenshots/pages-1440x900.png) · [`pages-1024x768.png`](../../mockups/screenshots/pages-1024x768.png) |
| library | [`library-1440x900.png`](../../mockups/screenshots/library-1440x900.png) · [`library-1024x768.png`](../../mockups/screenshots/library-1024x768.png) |
| publish | [`publish-1440x900.png`](../../mockups/screenshots/publish-1440x900.png) · [`publish-1024x768.png`](../../mockups/screenshots/publish-1024x768.png) |
| calendar | [`calendar-1440x900.png`](../../mockups/screenshots/calendar-1440x900.png) · [`calendar-1024x768.png`](../../mockups/screenshots/calendar-1024x768.png) |
| reels | [`reels-1440x900.png`](../../mockups/screenshots/reels-1440x900.png) · [`reels-1024x768.png`](../../mockups/screenshots/reels-1024x768.png) |
| analytics | [`analytics-1440x900.png`](../../mockups/screenshots/analytics-1440x900.png) · [`analytics-1024x768.png`](../../mockups/screenshots/analytics-1024x768.png) |
| activity | [`activity-1440x900.png`](../../mockups/screenshots/activity-1440x900.png) · [`activity-1024x768.png`](../../mockups/screenshots/activity-1024x768.png) |
| settings | [`settings-1440x900.png`](../../mockups/screenshots/settings-1440x900.png) · [`settings-1024x768.png`](../../mockups/screenshots/settings-1024x768.png) |

| Original workflow captures (5) | File |
|---|---|
| library-grid | [`library-grid.png`](../../mockups/screenshots/library-grid.png) |
| publish-review-60 | [`publish-review-60.png`](../../mockups/screenshots/publish-review-60.png) |
| publish-invalid | [`publish-invalid.png`](../../mockups/screenshots/publish-invalid.png) |
| reel-detail | [`reel-detail.png`](../../mockups/screenshots/reel-detail.png) |
| uncertain-detail | [`uncertain-detail.png`](../../mockups/screenshots/uncertain-detail.png) |

| Targeted Page Selector / sorting / browser navigation (7 × 2 = 14) | Actual 1440×900 / 1024×768 files |
|---|---|
| quick-selector | [`quick-selector-1440x900.png`](../../mockups/screenshots/quick-selector-1440x900.png) · [`quick-selector-1024x768.png`](../../mockups/screenshots/quick-selector-1024x768.png) |
| quick-p50 | [`quick-p50-1440x900.png`](../../mockups/screenshots/quick-p50-1440x900.png) · [`quick-p50-1024x768.png`](../../mockups/screenshots/quick-p50-1024x768.png) |
| quick-45-pages | [`quick-45-pages-1440x900.png`](../../mockups/screenshots/quick-45-pages-1440x900.png) · [`quick-45-pages-1024x768.png`](../../mockups/screenshots/quick-45-pages-1024x768.png) |
| library-filename-sort | [`library-filename-sort-1440x900.png`](../../mockups/screenshots/library-filename-sort-1440x900.png) · [`library-filename-sort-1024x768.png`](../../mockups/screenshots/library-filename-sort-1024x768.png) |
| reels-sort-gated | [`reels-sort-gated-1440x900.png`](../../mockups/screenshots/reels-sort-gated-1440x900.png) · [`reels-sort-gated-1024x768.png`](../../mockups/screenshots/reels-sort-gated-1024x768.png) |
| activity-schedule-sort | [`activity-schedule-sort-1440x900.png`](../../mockups/screenshots/activity-schedule-sort-1440x900.png) · [`activity-schedule-sort-1024x768.png`](../../mockups/screenshots/activity-schedule-sort-1024x768.png) |
| back-restored-library | [`back-restored-library-1440x900.png`](../../mockups/screenshots/back-restored-library-1440x900.png) · [`back-restored-library-1024x768.png`](../../mockups/screenshots/back-restored-library-1024x768.png) |

**Total: 18 + 5 + 14 = 37 distinct tracked PNGs**. [Browse screenshot directory](../../mockups/screenshots/). Existing captures verified; no regeneration was required for this documentation-only task.

## Proposed contracts, restrictions and approval gate

Proposed, **NOT IMPLEMENTED**: [control-level matrix](UI_V2_SCREEN_CONTRACT_MATRIX.md), [API v1.1](../api/INTERNAL_API_CONTRACTS_V1_1.md), [OpenAPI definition](../api/openapi-v1.1.yaml), [database schema amendments](../database/SCHEMA_AMENDMENTS_V1_1.md) and [ADR](../adr/ADR_UI_V2_API_EXTENSIONS.md). The per-target uniqueness scheme is a **design**, not an applied database migration. Meta P0 owned Page OAuth/publish/insights remains **NOT_RUN / BLOCKED_EXTERNAL**; real API/worker/backend/scale testing **NOT_IMPLEMENTED / NOT_RUN**. Cross-query select-all, calendar drag/reschedule, unverified view metrics and inferred imported media lineage remain deferred. User approval remains pending: **G3_READY_FOR_APPROVAL is not G3_APPROVED**, and PR #3 is not merged.

## Historical baseline / superseded evidence — not current

- Initial `59bb8a667861d1442bc8ff023abbcaa335328b98` with [Actions #38720044131](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38720044131) had **19/19** Playwright PASS and **23** original screenshots; original screenshot commit `e6e3df345508d982686e1108e07e7b2ebb51aa75`. **Historical only**, superseded by 35/37.
- Later HTML-change SHA `1de100918abe00fa0776c36e8e63305a113ac208` and [Actions #38726566010](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38726566010) had **35/35** PASS with expanded screenshots, followed by screenshot evidence commit `0da3acd102e3462a4b30bfc5256901ef0a01ea5e`. Also historical for CI attribution; the authoritative CI run is **#38727389515 on `3adf11d259df40687177623810e1b6d1cb7cb62f`**.
- F1–F4 originally failed on `456b377b8dcc3b0696ff544fe17278e9d3165a86` before repair. The current full suite covers their regression.

