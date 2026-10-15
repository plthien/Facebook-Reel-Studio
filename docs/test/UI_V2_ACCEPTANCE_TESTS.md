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
