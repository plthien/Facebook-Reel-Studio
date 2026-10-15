# Facebook Reels Studio — UI v2 G3 freeze candidate
**Status: G3_READY_FOR_REVIEW — USER APPROVAL PENDING. NOT G3_APPROVED.**

- Repository: `plthien/Facebook-Reel-Studio`; existing PR [#3](https://github.com/plthien/Facebook-Reel-Studio/pull/3), branch `design/ui-mockup-v2`; main untouched, PR unmerged.
- **Exact browser-tested code/test commit:** `59bb8a667861d1442bc8ff023abbcaa335328b98`. Screenshot/lockfile evidence originally committed in `e6e3df345508d982686e1108e07e7b2ebb51aa75`. Subsequent documentation-only freeze metadata is not itself a production build; use the live PR HEAD for final Git identity.
- **Browser evidence:** [successful GitHub Actions run #38720044131](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38720044131); **19/19 Playwright PASS**, contract validator PASS (8 OpenAPI routes, 79 local schema references). GitHub-hosted Ubuntu 24.04, Node 22, Playwright 1.55.0, bundled Chromium 140.0.7339.16 (build 1187).
- **Screenshots:** 23 real Chromium PNGs under [`mockups/screenshots/`](../../mockups/screenshots) on this PR branch: 9 screens at **1440×900**, 9 at **1024×768**, and Library Grid, Review 60, invalid-target Review, Reel drawer, UNCERTAIN drawer. The 18 standard screenshots have exact viewport pixel dimensions; the 5 critical-workflow images are full-page. [Run artifact](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38720044131) also contains evidence and HTML report.

## G3 screen/workflow coverage
Dashboard, Fanpages, Video Library, Quick/Batch Publish, Calendar, Published Reels, Analytics, Activity/Queue, Settings (9/9). Grid/List, bounded simulated cursor, explicit selections, 50/100/105 selection, 100 targets limit, 20-video/10-Page/60-target explicit fixture, all-target review in pages 25+25+10, stable caption/title/time, local (+07:00) → UTC, past/invalid/too-soon checks, canonical Quick video/Page identities, duplicate blocking, changed-intent invalidation, 409/422/401/403/429/503 demo states, UNCERTAIN reconciliation-only, unsupported feature disabled, imported Reel without inferred asset linkage, inaccessible metrics ≠ zero.

## Governing proposed contracts
`docs/adr/ADR_UI_V2_API_EXTENSIONS.md`, `docs/api/INTERNAL_API_CONTRACTS_V1_1.md`, `docs/api/openapi-v1.1.yaml` (OpenAPI 3.1, JSON-encoded YAML 1.2), `docs/database/SCHEMA_AMENDMENTS_V1_1.md`, technical spec and P0–P3 plan. Database target identity: `target_index`, `client_target_id`, the two per-batch unique keys; old `UNIQUE(batch_id,page_id)` eliminated in proposed DDL. Every target is independently validated and submitted atomically with an idempotency fingerprint; **no actual backend or migration implemented**.

## Actual gates and limitations
- **PASS:** baseline F1–F4 reproduced, repaired; V8 functional regression after changes; Playwright 19/19; viewport-size screenshots visually inspected; no app-level horizontal overflow found at tested viewports; browser runtime errors test passed; offline OpenAPI JSON/YAML 1.2 syntax/internal-ref/schema consistency check passed.
- **NOT_RUN:** live Meta API operations, PostgreSQL/Alembic migrations, worker/queue testing, production React implementation, true backend query/capacity benchmarks and real P0 metric support.
- **BLOCKED_EXTERNAL (separate P0 gate):** real owned-Page Meta authorization/publish/insights evidence.
- **DEFER:** selection across all filtered results, reschedule PATCH/drag, unsupported metrics, inferred imported media association, cross-Page reporting not grounded in proven metric data.
- **Awaiting approval:** all proposed API/schema decisions and this G3 implementation reference. **Do not merge PR #3 automatically.**

The large dataset numbers are **synthetic fixture scope**, not benchmark performance; production must use server-side cursor pagination, indexed filtering and sorting, request cancel/cache, and backend analytics aggregates. Full-page Playwright screenshots may place CSS sticky sidebar at a stitched scroll position; compare exact viewport captures for visual alignment.
