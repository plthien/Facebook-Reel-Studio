# UI v2 ↔ Backend Contract Audit
**Date:** 2026-10-15 · **Status:** design-only, not implemented or Meta-verified

Canonical source: [Technical spec v1](../docs/FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md) and [Implementation plan P0–P3](../docs/IMPLEMENTATION_PLAN_P0_P3.md).
Prototype: [facebook-reels-studio-v2.html](facebook-reels-studio-v2.html).

## Governing principles

- All data are synthetic (50 Pages, 10,000 assets, 100,000 Reels, 100,000 jobs). Browser arrays are **prototype fixtures only** and must NOT become production data architecture.
- No UI publishes to Meta, modifies a real post, changes a Page connection or claims that unverified metrics exist.
- New UI elements are categorized as **EXISTING CONTRACT**, **CONTRACT EXTENSION**, or **DESIGN ONLY / DEFERRED**.
- P0 external live Meta evidence is a hard blocker for P1 and analytics mapping. Phase labels indicate proposed implementation, not completed functionality.
- Do not silently add backend capabilities purely to match screens. Where contracts are missing, implement the specification change, migration, contract tests and acceptance gate first.

## Screen-to-API mapping

| Screen / interaction | Phase | Proposed BE contract | Decision |
|---|---|---|---|
| Dashboard operations / health | P1/P2 | `GET /publish-jobs`, `GET /system/health`, `GET /analytics/overview` | EXISTING CONTRACT; P2 cards gated by P0 metrics |
| Fanpages list/search & health | P1 | `GET /pages?q=&status=&cursor=&limit=`, `GET /pages/{id}/health` | EXISTING CONTRACT |
| Connect Facebook | P1 | `GET /auth/facebook/start` | EXISTING CONTRACT, live OAuth gated |
| Library upload | P1 | `POST /media` | EXISTING CONTRACT; live file picker intentionally nonfunctional in mockup |
| Library list & metadata | P1 | `GET /media`, `GET /media/{id}` | EXISTING CONTRACT with filter contract expansion below |
| Library Grid/List and page size | P1 | `GET /media` | Existing cursor pagination. Grid/List purely presentational |
| Library search by name, asset ID, tag, filename | P1 | `GET /media?q=&tags=&status=&sort=&cursor=&limit=` | **CONTRACT EXTENSION**: existing `GET /media` lists pagination/tag/status only |
| Library sort across entire results | P1 | same expanded `GET /media` | **CONTRACT EXTENSION**: allowlisted sorts, stable cursor tie-breaker |
| Video usage count and per-Page usage history | P1/P2 | `GET /media/{id}/publications` | **CONTRACT EXTENSION** with SQL join to `published_reels` / `publish_jobs` and exact asset lineage; do not fake this from upload count |
| Multi-select across pages | P1/P3 | Client IDs; validate server-side during batch | EXISTING CONTRACT for bounded explicit IDs |
| Select ALL results with filter scope | Post-P3 | Persisted filter snapshot or backend selection token, expiry, preview count | **DEFERRED**; never submit unbounded client selection |
| Multiple videos in a batch | P3 | `POST /publish-batches/preview` and `POST /publish-batches` with explicit `targets[]` | EXISTING CONTRACT supports distinct `variant_id` per target; v2 matrix demonstrates UX |
| Assign Page/caption/time per target | P3 | `targets[]` fields `page_id`, `variant_id`, `caption_override`, `scheduled_at` | EXISTING CONTRACT |
| Auto-build N×M cartesian product | P3 | Client-generated **explicit** target list then server preview | Optional UI convenience; user must review full count and duplicates |
| Publish review with 40 visible rows | P3 | Server validates ALL rows, not only shown 40; atomic submit and Idempotency-Key | EXISTING CONTRACT; virtual/paginated production matrix required |
| Batch limit & large preview | P3 | Configurable max targets, server preflight, 422 per-target error details | **CONTRACT EXTENSION** precise target caps and preview pagination if volume exceeds returned response |
| Job list/detail/UNCERTAIN recovery | P1/P3 | `GET /publish-jobs`, `GET /publish-jobs/{id}`, `POST /publish-jobs/{id}/reconcile` | EXISTING CONTRACT |
| Activity keyword search, bulk filters, sort | P1/P3 | `GET /publish-jobs?q=&status=&page_id=&from=&to=&sort=&cursor=&limit=` | **CONTRACT EXTENSION** to filters/search |
| Reels list, source, Page and snapshots | P2 | `GET /reels`, `GET /reels/{id}`, `GET /analytics/reels/{id}/timeseries` | EXISTING CONTRACT |
| Reels text search, asset grouped view, metric sorts | P2 | `GET /reels?q=&asset_id=&page_ids=&origin=&metric_sort=&cursor=`; aggregated by asset endpoint | **CONTRACT EXTENSION** to list query; grouped asset comparison requires new endpoint |
| Reel metric freshness, N/A | P2 | Metric availability registry, collection/observation timestamps | EXISTING CONTRACT, hard-gated by live P0 |
| Analytics overview, Page ranking & metric availability | P2 | `GET /analytics/overview`, `GET /analytics/pages`, `GET /analytics/metrics/availability` | EXISTING CONTRACT |
| Advanced fast-growing/underperforming saved views | P4 | Normalized window age, comparable snapshots, reference baselines | **DEFERRED**; not presented as live controls in v2 |
| Calendar Agenda/Week/Month read-only | P3 | `GET /publish-jobs?from=&to=&cursor=` | EXISTING CONTRACT, grouped by client |
| Drag-and-drop reschedule | Post-P3 | Conditional `PATCH /publish-jobs/{id}` with version/ETag and strict status handling | **DEFERRED**; NO live drag-to-reschedule UI |
| Multiple user roles/approval workflows | Post-P3 | RBAC + approval endpoints | **DEFERRED**; internal owner scope only |

## Required additive contract patch BEFORE FE coding (minimal set)

### A. List query behavior
Define shared query envelope `{items,next_cursor,has_more?,total_count?}`. `total_count` is optional/approximate if expensive; never require exact total for cursor paging. The 10k/100k totals in the mockup are synthetic fixture labels.

Add allowlisted `q`, `sort`, `direction`, and `limit=25|50|100` for `GET /media`, `GET /reels`, and `GET /publish-jobs` as needed; enforce stable cursor ordering. Each search is server-side, debounced on client. Refilter resets cursor chain; controls must preserve `filter` and `sort` in URL. No SQL text concatenation from user sort.

### B. Media usage history
Specify `GET /api/v1/media/{asset_id}/publications?cursor=&limit=` returning `[{reel_id,page_id,publish_job_id,published_at,fb_video_id,origin,metric_availability}]`. Always scope to assets owned by workspace, never infer Reels to asset via matching titles. Imported Reels without known asset relation must remain unlinked.

### C. Explicit batch size validation
Define upper limits (configurable) for `targets[]`; invalid targets -> reject whole batch, return structured target diagnostics in `preview`. For long matrix, include `preview_id` or segmented read-only preview only if preview cannot fit; lock immutable target intent and verify same intent hash on submit. P3 can start with conservative 100 targets/submit and chunk operator batches; this is a recommended local app limit, not Meta platform limit.

### D. No scope-selection backend in P1–P3
Selection within loaded rows or bounded explicit chosen IDs is supported. Selection of **all** matches across 100k records must stay non-executable until BE filter snapshot/token semantics and race-safe validation exist.

### E. Auth & metric gates
All Page health labels originate only from actual authorization checks. Any platform metric absent or renamed after version upgrades becomes `UNAVAILABLE/REQUIRES_TEST` with source and timestamp, not zero. No dashboard dependency on unsupported watch-time or other unproven metrics.

## UI test gates to add to release plan
1. 50 Page fixtures; Page filter/search persists across cursor requests.
2. 10k assets; first response capped, no preload of entire asset library.
3. 100k Reels; pagination and metric sorts reflect global DB order.
4. 100k jobs; filters return deterministic cursor results under concurrent inserts.
5. Select 50 rows on page A, page to B, selection remains by stable ID; deselect works.
6. Select-all-results remains disabled or prompts unsupported contract, not fake bulk action.
7. Publish 20 assets mapped to 10 Pages with 60 explicit targets; BE confirms 60, not automatically 200.
8. Duplicate POST using same Idempotency-Key produces one batch.
9. Preview validates ALL submitted targets, not just those in currently rendered virtual table.
10. Invalid target makes atomic submit fail 422 without creating other jobs.
11. Transient refresh/navigation retains per-target caption/schedule draft; production draft persistence design to be defined (client storage versus drafts API).
12. Unauthorized Page excluded, invalid asset rejected, unavailable metrics show N/A.
13. UNCERTAIN only allows reconcile/manual decision, no blind retry.
14. Dense Calendar uses aggregated month cells or Agenda, no massive DOM.
15. Frontend list render time target p95 < 500ms on a synthetic 50-row response; backend read p95 < 2s in staging fixture environment (engineering targets, not claims about Meta).
16. P0 live tests with owned Pages are still mandatory even if all UI mocks pass.

## Known limitations of interactive HTML mockup
- Entire 10k/100k datasets are generated **inside browser memory** solely to exercise visible behavior. Real UI MUST request server-side pages and MUST NOT generate or retain these full arrays.
- Pagination uses numeric page UX in demo; backend uses cursors. Production UI must adapt to cursor pagination (next/previous with cursor stack; total page counts only when trusted count exists).
- The mockup's `By Video Asset` comparison, persistence of per-target schedule overrides, sort/search extensions, saved views, all-results selection and drag reschedule require the contract updates above; they are **not approved P1–P3 shipping promises**.
- The mockup never opens real OAuth, uploads files, creates jobs, exports reports, calls Meta, or claims performance numbers.

## Review gate
Approve v2 UI only together with this traceability audit. Before Codex begins P1–P3 frontend: merge a contract/spec patch or delete/defer UI behaviors outside baseline. Keep P0 live API feasibility independently blocked until verified.
