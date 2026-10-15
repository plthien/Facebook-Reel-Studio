# Facebook Reels Studio UI v2 — G3 review reference

- **[Standalone interactive HTML](facebook-reels-studio-v2.html)** — nine-screen design reference; no runtime backend, OAuth or real publish.
- **[37 verified browser screenshots](screenshots/)** — 18 baseline viewport captures, 5 original workflow screenshots and 14 targeted captures at 1440×900 / 1024×768.
- **[UI/API contract matrix](../docs/ui/UI_V2_SCREEN_CONTRACT_MATRIX.md)** · **[OpenAPI proposal](../docs/api/openapi-v1.1.yaml)** · **[Schema amendments](../docs/database/SCHEMA_AMENDMENTS_V1_1.md)** · **[Freeze candidate](../docs/ui/UI_V2_FREEZE.md)**.

## Test locally (Node 22)
```bash
npm ci
npx playwright install --with-deps chromium
npm run test:contract
npm run test:ui
```
The Playwright config serves the standalone HTML at `http://127.0.0.1:8765` with `python3 -m http.server`. No production framework required. Current GitHub Actions evidence on tested checkout `3adf11d259df40687177623810e1b6d1cb7cb62f`: [run #38727389515](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38727389515) — **35/35 PASS**, contract PASS and 37 tracked screenshots, with `npm ci` successful. **G3_READY_FOR_APPROVAL — USER APPROVAL PENDING.** The earlier 19/23 run is historical only; see [Freeze Manifest](../docs/ui/UI_V2_FREEZE.md).

## Design operations & limits
50 Pages, 10,000 assets, 100,000 Reels and 100,000 jobs are **deterministic lazy synthetic fixtures**, not production benchmark data. Library defaults to List with Grid switch; cursor simulation, filter/search and explicit selected IDs. Transfer preserves all 50/100 selected assets; for 105 it shows a blocking error and keeps 105 for correction. Batch adds one explicit target per assignment, **never N×M**; demo 20 assets, 10 Pages, 60 explicit targets with all-target Review paging 25+25+10. Max 100 atomic targets. Quick mode fixes one video and selected Pages; per-target caption, title, local scheduled time and UTC remain editable. Strict past/invalid/too-soon validation (configurable mock 10-minute lead), exact duplicate blocking and intent-change revalidation. Confirmation always says **DEMO ONLY, 0 jobs created**.

Published Reels do not invent imported asset attribution; unavailable, stale and measured zero metrics differ; Analytics never assumes P0-supported values; Calendar read-only; Activity UNCERTAIN requires remote reconciliation. 401/403/409/422/429/503 are local mock states, not actual HTTP responses. All requested backend API/database changes are **pending review**. Production requires authenticated Meta adapter/live P0 gate, server-side stable cursor filtering, query cache/cancellation, lazy previews and verified metrics. No production P1–P3 implementation on this branch.

See [review report](../docs/reviews/UI_V2_FINAL_REVIEW.md), [acceptance evidence](../docs/test/UI_V2_ACCEPTANCE_TESTS.md) and [backend audit](UI_V2_BACKEND_CONTRACT_AUDIT.md).


## G3 targeted updates (Page Selector, sorting, browser history)
- **Quick Page Selector:** Search all 50 loaded Page entries by name/internal ID/Meta ID; 45 ACTIVE eligible, 5 expired/blocked disabled. Group/status filters, visible selected count, scrollable checkbox list, full selected-Pages summary, scoped select-all/clear; p50 selectable. Existing Page picks and caption/title/time survive filters and screen navigation.
- **Sorting controls:** Library newest/oldest/filename; Reels newest only, views sort disabled pending Meta P0/P2; Activity schedule newest/oldest and job creation newest. Synthetic fixtures use lazy arithmetic global sort before cursor, **not client sorting the first 25 rows**; production uses existing proposed API sorting and UUID-tie-breaking server-side. No 100k records allocated for default page/sort.
- **Browser routes:** Direct #publish, Back, Forward and invalid hash are supported without losing unsent drafts or keeping stale drawer overlays.
- **Reproducible QA:** `npm ci && npx playwright install --with-deps chromium && npm run test:contract && npm run test:ui`. [current GitHub Actions #38727389515](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38727389515): **35/35 Chromium tests PASS**, contract PASS; **37 PNG screenshots** in `mockups/screenshots/`, including 14 new two-viewport targeted screenshots.
- This is still a standalone demo reference. No real Meta or P1–P3 backend was implemented.
