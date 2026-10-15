# UI v2 — executed acceptance & regression ledger
**Result: 19/19 Playwright PASS, 0 FAIL** on code/test commit `59bb8a667861d1442bc8ff023abbcaa335328b98` · [GitHub Actions #38720044131](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38720044131).

Actual CI commands: `npm install --no-audit --no-fund`, `npm run test:contract`, `npx playwright install --with-deps chromium`, `npm run test:ui`. Host: GitHub-hosted Ubuntu 24.04, Node 22, Playwright 1.55.0, Chromium 140.0.7339.16 (build 1187). Test duration 16.1 s. No actual Meta HTTP operations.

| Test | Browser behavior asserted | Actual |
|---|---|---|
| UI01 | Navigate all nine screens, zero uncaught JS errors | PASS |
| UI02 | Library List/Grid toggle, search empty state | PASS |
| UI03 | Cursor next/back, select 25+25, filter selection persistence | PASS |
| UI04 | F1: 50 and 100 assets transfer intact; 105 blocked without loss | PASS |
| UI05 | F3: Quick Page chips and read-only Page identity, caption/schedule persistence | PASS |
| UI06 | Quick add/remove Pages; switch mode without stale targets | PASS |
| UI07 | 20 videos + 10 Pages = exactly 60 explicit targets (25+25+10) | PASS |
| UI08 | Target 51 caption/title/schedule survives review and step navigation | PASS |
| UI09 | F2 strict date parse, past, now, 5-min lead, valid 10-min, UTC | PASS |
| UI10 | F4 exact duplicate on late page blocked; different occurrence permitted | PASS |
| UI11 | Invalid Page/asset, 101st target refusal with visible message | PASS |
| UI12 | Changed intent invalidates preview; no real job created by demo | PASS |
| UI13 | 409/422 plus 401/403/429/503 simulated API error controls | PASS |
| UI14 | UNCERTAIN has reconcile info, no blind retry; drawer Escape | PASS |
| UI15 | Imported Reel without fake local asset link; metric N/A | PASS |
| UI16 | Calendar Agenda/Week/Month; no drag-reschedule | PASS |
| UI17 | 1440/1024 browser viewport no application-level horizontal overflow; drawer scroll | PASS |
| UI18 | 23 screenshot images generated from Chromium at required views/workflows | PASS |
| UI19 | Quick video canonical across Pages; switching to Batch retains all asset IDs | PASS |
| CONTRACT01 | Parse proposed OpenAPI 3.1 JSON-encoded YAML 1.2; 8 routes, 79 refs; schema/legacy checks | PASS |

## Captured screenshots
All **nine screens** at **1440×900 and 1024×768** (18 pixel-exact viewport PNGs), plus `library-grid.png`, `publish-review-60.png`, `publish-invalid.png`, `reel-detail.png`, `uncertain-detail.png` (5 full-page PNGs). Files are committed under `mockups/screenshots/`; [Action artifact/run evidence](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38720044131).

## Baseline failures and closure
Before repair, F1 selected 105→100 silent transfer, F2 accepted 2020 date, F3 chips p2/p3 mismatched targets p4/p3, F4 duplicate marked warning and confirm allowed. Reproduced in executable JavaScript against baseline HEAD; all repaired and confirmed by V8 logic tests + browser regression.

**Not performed:** real Meta OAuth/uploads/finishing/verification/insights, DB schema migrations, worker/queue tests, frontend production implementation, backend database performance; those require later gates. Screenshots and synthetic scale do not prove Meta capability or production load performance. OpenAPI syntax/internal references passed; additional third-party standards lint and generated FastAPI parity remain future backend tasks.


## Additional 16 targeted Playwright test groups — executed PASS
Run [#38726566010](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38726566010), source HEAD `1de100918abe00fa0776c36e8e63305a113ac208` before screenshot auto-commit. **35/35 PASS, 0 FAIL** including all previous 19; `npm run test:contract` PASS. Executed via GitHub Actions: `npm install --no-audit --no-fund`, `npm run test:contract`, `npx playwright install --with-deps chromium`, `npm run test:ui`. No P0 live Meta tests.

| Test IDs | Actual assertions | Result |
|---|---|---|
| QP-01 | All 50 rows rendered, 45 selectable ACTIVE, 5 disabled | PASS |
| QP-02–03 | p50 searched via real UI, exactly one Quick target, immutable Page Review | PASS |
| QP-04–06 | Filter/search hiding does not clear chosen Pages, restore and deselect exact target | PASS |
| QP-07–08 | Bulk 45 ACTIVE, all blocked/expired disabled | PASS |
| QP-09–10 | Per-target caption/title/time survive filter, add Page; canonical identity | PASS |
| SORT-01–03 | Library global newest/oldest/filename across cursor pages | PASS |
| SORT-04–05 | Sort resets cursor but preserves search and explicit selected asset IDs | PASS |
| SORT-06–07 | Reels chronological paging, views sort option disabled/gated | PASS |
| SORT-08–09 | Jobs schedule asc/desc and created_at desc across pages | PASS |
| SORT-10–12 | No duplicate/skip across pages, stable order and independent screen sort choices | PASS |
| NAV-01–03 | Browser Back/Forward restores Library/Reels with sidebar and hash sync | PASS |
| NAV-04–05 | Direct #publish, invalid hash safely falls back Dashboard | PASS |
| NAV-06/08 | Same route clicks do not push extra history; route change closes drawer overlay | PASS |
| NAV-07/09 | Publishing draft survives Back/Forward; no runtime JS errors | PASS |
| VIS-01 | 14 new Chromium screenshots, 7 target workflows at two viewports | PASS |
| PERF-01 | 25-row global sorted page uses at most 26 generated fixture records; avoids materializing 10k/100k dataset for default paging | PASS |

Prior **19 tests remain PASS** (F1–F4, 60 target review, intent fingerprint, Meta mock-only controls, accessibility, 9 screens). New screenshots: quick-selector, quick-p50, quick-45-pages, library-filename-sort, reels-sort-gated, activity-schedule-sort, back-restored-library, each at 1440×900 and 1024×768. **37 screenshot files** total. Inspected actual browser renders for p50/45 selector, status separation, Activity sort and Reels capability gating. No production performance claim based on fixtures.
