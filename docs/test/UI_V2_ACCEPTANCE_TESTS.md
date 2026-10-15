# UI v2 Acceptance / execution ledger
**Status: test specifications, not evidence of passing browser tests.** Browser screenshots are **NOT_RUN** because the GitHub-linked mockup was edited through the connector and no current-commit checkout/browser session was available in the execution environment.

| Test ID | Scenario | Expected | Actual status |
|---|---|---|---|
| UI01 | Navigate Dashboard, Pages, Library, Publish, Calendar, Reels, Analytics, Activity, Settings | All render, nav active | NOT_RUN |
| UI02 | Library List(default) ↔ Grid | Same bounded fixtures | NOT_RUN |
| UI03 | Search, status/Page filters, next/previous, empty result | Deterministic cursor demo and empty state | NOT_RUN |
| UI04 | Select on first page, move next, select again, back | Selected IDs retained | NOT_RUN |
| UI05 | Transfer selected assets to batch | Exact IDs, no silent trim | NOT_RUN |
| UI06 | Quick Publish 1 video and 2 Pages | Exactly 2 target identities | NOT_RUN |
| UI07 | Edit caption/title/schedule on two targets, move steps | Changes persist by target ID | NOT_RUN |
| UI08 | Demo sample: 20 videos / 10 Pages / 60 explicit targets | Count 60, not 200; review pages 1–3 | NOT_RUN |
| UI09 | Edit item 55, review page 1 again | Item 55 maintained; all validated | NOT_RUN |
| UI10 | Attempt 101st target | Explicit limit; never silently truncate | NOT_RUN |
| UI11 | Invalid Page/asset; HTTP 409/422 mock | Disable confirm, show conflict/error | NOT_RUN |
| UI12 | Open UNCERTAIN job | Only reconcile detail, never retry | NOT_RUN |
| UI13 | All-result selection and drag-reschedule | Unsupported/disabled, no data mutations | NOT_RUN |
| UI14 | Imported Reel, N/A, stale, measured zero, lifetime | Correct labels; mock origin disclosed | NOT_RUN |
| UI15 | Dialog Escape, focus, keyboard traversal | Accessible close and cycling | NOT_RUN |
| UI16 | Desktop 1440×900, tablet 1024×768 | Screenshots and no overflow blocking workflows | NOT_RUN |
| UI17 | JS console errors | Zero uncaught runtime errors | NOT_RUN |
| STATIC01 | JS generated in mockup | JavaScript compiled via `new Function(script)` | PASS (syntax only; not browser execution) |

Required future evidence: run the Playwright file under `tests/ui-v2.spec.js` with local HTTP server at port 8765 and browser installed, capture both viewport screenshots into `mockups/screenshots/` (paths not present until run). Document exact run command/CI logs, browser versions, failures and reviewed HEAD SHA. No claim of E2E/visual PASS before this evidence exists.


### Executed 2026-10-15: V8 JavaScript functional smoke, no browser

Loaded **actual PR #3 HTML** through GitHub connector, extracted script, executed with stub DOM/location and asserted:

- 20 asset IDs / 10 Page choices / exactly 60 explicit targets: PASS; zero invalid targets.
- Review third page renders 10 targets (51–60): PASS.
- Caption on target 51 persists across composer step navigation: PASS.
- 2026-10-21 19:30 Asia/Ho_Chi_Minh converts to 2026-10-21T12:30:00.000Z: PASS.
- Change one target to blocked Page: invalid count 1: PASS.
- Adding 101st target: blocked at 100 with explicit message: PASS.
- Default cursor demo returns bounded 25 records: PASS.

These tests **do not cover browser layout, focus, DOM events, actual Playwright, screenshot or Meta/API calls**. Those remain NOT_RUN/BLOCKED_EXTERNAL.
