# FACEBOOK REELS STUDIO — DETAILED IMPLEMENTATION MASTER PLAN v2.1

Date: 2026-10-15
Repo: plthien/Facebook-Reel-Studio
Audience: Codex / engineering implementation agent
Scope: 10–50 owned/administered Facebook Pages; P0 live first; P1–P3 after P0-GO.
Current status: DESIGN PLAN ONLY. No claim of implemented API, live Meta support, approved UI freeze or passing tests.

## 0. Mandatory source material and execution rules

Read ALL current files, not stale chat summaries:
- docs/FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md from main.
- docs/IMPLEMENTATION_PLAN_P0_P3.md from main.
- mockups/facebook-reels-studio-v2.html from design/ui-mockup-v2.
- mockups/UI_V2_BACKEND_CONTRACT_AUDIT.md from design/ui-mockup-v2.
- mockups/README_V2.md from design/ui-mockup-v2.

Branch status: PR #3 holds the v2 mockup; PR #2 holds superseded v1. Neither design is evidence of Meta API capability. Check current GitHub status before merging anything.

Execution order, no shortcuts:
G0 baseline + UI workflow review → G1 approve extension contracts and DB decisions → G2 update canonical technical spec, plan, API schema and test gates → G3 repair/lock UI v2 as visual/behavioral implementation reference → G4 build and run P0 with real Meta Pages → G5 implement P1 → G6 implement P2 → G7 implement P3.

Only DOCUMENTATION + DESIGN may be done before live P0. NEVER implement production P1/P2/P3 as "done" when P0 is not actually verified. The first 4 gates are planning/design tasks, not permission to bypass P0.

Immutable rules:
- Source of truth for external behavior = current documented Meta endpoints PLUS redacted responses from the operator's real authorized Meta App/Pages. Official Meta examples using old Graph versions are reference, not current live proof.
- Internal auth secure cookie; tokens encrypted server-side, never stored in frontend/browser logs/Git.
- Meta IDs = strings; internal IDs = UUIDs; time at API/DB = UTC with offset, UI = Asia/Ho_Chi_Minh.
- PUBLISHED requires confirmed remote Reel evidence, not just a successful request.
- UNCERTAIN permits investigation/reconcile, not an automatic replay of possible external publish.
- N/A, unsupported and failed sync are not numeric 0; lifetime Reel views are not views gained within a date window.
- Implement precisely owned Pages; no SaaS for third parties, other platforms, scraping, browser account automation or unrelated features.
- Clearly report PASS, FAIL, NOT_RUN, BLOCKED_EXTERNAL separately.

## 1. G0 — Inspect repo, review 9 UI screens and workflows

### G0-01 Repository audit
1. Query repository default branch, open design PRs, paths and HEAD SHAs.
2. Establish a separate implementation branch; no direct speculative modifications to main.
3. Record exact baseline source SHAs and design proposal version in docs/reviews/UI_V2_BASELINE.md.
4. Verify source docs and UI are consistent in planned phases and capabilities.
5. Produce an issue register with severity P0/P1/P2, owner, file/function/line, API impact and acceptance test.

### G0-02 Screen-action inventory
Exhaustively inspect each control in Dashboard, Fanpages, Video Library, Publish, Calendar, Reels, Analytics, Activity and Settings, including clickable rows, modals/drawers, selection and hidden errors.

Create docs/ui/UI_V2_SCREEN_CONTRACT_MATRIX.md, one row per real interaction:
Screen | route | UI action/display | phase | backend API | request/response | DB fields | permission gate | loading/empty/error states | test ID | decision.

Decision values: BACKED (already specified), EXTEND (requires contract and implementation), DEFER (remove/disable), DEMO (mock only). Do not ship DEMO success to production.

### G0-03 Confirmed design/backend mismatches to resolve
A. CRITICAL: existing SQL UNIQUE(batch_id,page_id) forbids more than one Reel target per Page per batch, while UI v2 supports many videos per Page. Replace this invariant, see G1.
B. CRITICAL: Publish Review currently shows first 40 rows while N×M target generation can exceed 1000. Must validate and review all targets before submit; limit initially to <=100 explicit targets per batch.
C. CRITICAL: per-target datetime input on Review has no persistent onchange; caption draft state not guaranteed across navigation/reload. Store drafts by stable target identity.
D. CRITICAL: mock a1/p1 IDs are not real UUID variant/page IDs; map asset→immutable content variant→Page UUID before submit.
E. GET /media lacks specified query/search/sort fields despite UI controls.
F. Library Usage History has no standalone backend contract.
G. Selecting all matching results has no selection-token backend and must not be executable in P1–P3.
H. UI Calendar suggests changed schedules but existing backend has no PATCH/reschedule contract. Calendar stays read-only in P3.
I. DB validation enum lacks REQUIRES_TEST even though spec requires it for unknown Meta media requirements.
J. Browser fixture creates 10,000 assets and 100,000 Reels/jobs and uses array.filter for every keystroke. Production MUST use server-side keyset pagination and indexed search.
K. Imported Reels cannot be linked to local assets by title/visual guess.
L. UI metric values, auth health and usage counts are fictional; production must use supported metrics and evidence only.
M. Fake numeric page counts, all-results checkbox, and optional saved analytics views cannot become live capabilities by copying mock scripts.
N. Local Page groups are not presently a DB property; formalize local group_label or remove group filter.
O. App React routes (/library,/reels etc.) differ from mock hash routing; UI freeze defines intent, not copy-paste application.
P. P1/P3 composer review needs explicit video, Page, caption, schedule in local+UTC, duplicate warnings and target count, not just Page/time.

G0 PASS:
- 100% of live-intended controls classified.
- Every above mismatch has disposition with task ID.
- Critical fixes are assigned to G1/G2/G3, not left as vague notes.
- No app code or Meta live test is falsely labeled completed.

## 2. G1 — Decisions: API extension and DB constraints

These are PROPOSED decisions to formally approve in an ADR, not existing implemented API.

### G1-01 Fix multi-video per-Page batch invariant — BLOCKER

Replace UNIQUE(batch_id,page_id) with a per-target identity:
- publish_jobs.target_index INTEGER NOT NULL CHECK target_index >= 0.
- publish_jobs.client_target_id TEXT NOT NULL (client-generated stable opaque identifier).
- UNIQUE(batch_id,target_index).
- UNIQUE(batch_id,client_target_id).
- Remove UNIQUE(batch_id,page_id); many different targets can share the same Page.
- Persist variant_id, page_id, title_override, caption_override, scheduled_at on each job and keep immutable after accepting batch.
- publish_batches client_idempotency_key + request_fingerprint; same key+same canonical intent returns the same batch, same key+changed intent = HTTP 409.
- Entire submit in ONE DB transaction; invalid one target = HTTP 422, ZERO jobs created. No implicit partial.
- Remote Reel ID uniqueness remains protected; verify any Meta-specific remote ID assumptions in P0.
- Migration strategy: if database never deployed, edit initial Alembic model before first deploy. If production tables already exist, add safe forward migration/backfill and test rollback.

DB gate examples:
(1) 2 assets → same Page → one batch, 2 jobs succeeds.
(2) 2 distinct scheduled occurrences for same Page remain distinguishable.
(3) duplicate client_target_id within batch rejected.
(4) 422 rollback leaves no partial jobs.

### G1-02 Publish-batch contract

Existing endpoints:
POST /api/v1/publish-batches/preview
POST /api/v1/publish-batches (Idempotency-Key header)
GET /api/v1/publish-batches/{batch_id}

Use explicit targets; no hidden cartesian-product submission.
Request schema:
~~~json
{
  "name": "Editorial batch",
  "targets": [
    {
      "client_target_id": "target-001",
      "target_index": 0,
      "page_id": "UUID",
      "variant_id": "UUID",
      "scheduled_at": "2026-10-20T12:30:00Z",
      "title_override": "Optional",
      "caption_override": "Caption per Page/video"
    }
  ]
}
~~~

Initial operator-owned app limit: MIN 1, MAX 100 explicit targets per atomic batch request, configurable locally. This is an internal safety limit, NOT a Meta rate limit. If operator chooses 150 targets, UI requests explicit 2-batch workflow with separate confirmations rather than claiming one atomic transaction.

Preflight requirements:
- Every target belongs to the intended managed Page and immutable content variant; Page enabled, scopes/tasks verified and asset validation VALID with P0-proven format limits.
- Reject REQUIRES_TEST/INVALID assets.
- Check future schedule and a configurable lead-time rule; include local and UTC times in UI.
- Detect exact duplicate entries; repeated content use must not be automatically treated as an attempt to defeat content rules.
- Preview returns per-target outcome for ALL target IDs, no omitted rows; no actual publish job created.
- Response includes total/valid/warnings/invalid and canonical server-computed request fingerprint; optional expiry if a preflight artifact is persisted.
- Submit revalidates dynamic permissions/content and checks fingerprint; never trusts client-provided hash alone.
- 422 includes errors per client_target_id and no jobs; 409 for key-intent mismatch; 401/403 for auth/ownership failure.
- Prevent rapid submit double-click and network replay by persisting Idempotency-Key across the same submit intent.

Preview response example:
~~~json
{
  "request_fingerprint":"sha256:...",
  "total":2,
  "valid":1,
  "warnings":0,
  "invalid":1,
  "targets":[
    {"client_target_id":"target-001","ok":true,"errors":[],"warnings":[]},
    {"client_target_id":"target-002","ok":false,"errors":[{"code":"ASSET_INVALID","field":"variant_id"}],"warnings":[]}
  ]
}
~~~

### G1-03 Standard cursor-list contract

Use response structure for GET /media, GET /reels, GET /publish-jobs:
~~~json
{
  "items": [],
  "next_cursor": null,
  "has_more": false,
  "total_count": null,
  "count_is_estimated": false,
  "applied_filters": {}
}
~~~

- limit allowed 25/50/100, default 50.
- Keyset cursor uses stable sort tuple (timestamp, internal UUID), encoded opaque and validates filter/sort consistency; invalid cursor 400.
- Backend handles filtering/sorting across entire scope, not browser arrays. No arbitrary SQL sort field injection.
- total_count optional; if null UI shows items loaded and next/previous cursor, not fabricated number of pages.
- Search debounce 250–350ms, cancel stale requests, loading and empty states; URL stores filter/sort/page cursor state where possible.
- Bulk selection across loaded pages retains explicit IDs only; no select-all-filtered-results scope token in P1–P3.

Extension 1: GET /api/v1/media?q=&tag=&validation_status=&sort=&limit=&cursor=
  q matches asset filename, asset ID, and supported local variant title. tag filters content_variants.tags (NOT a nonexistent media_assets.theme).
  initial sorts: created_at_desc/created_at_asc/filename_asc; extensions require backend indexes and test.
  return id, filename, created_at, duration, resolution, validation, preview metadata, linked usage count with its exact definition.

Extension 2: GET /api/v1/media/{asset_id}/publications?cursor=&limit=
  Join media_assets→content_variants→publish_jobs→published_reels, never title-match imported media.
  response item: reel_id, job_id, page_id, posted_at, origin, fb_video_id, fb_post_id optional, latest metric availability optional P2.
  Count Pages and count Reel publications distinctly; never describe job attempts as Reel usage.

Extension 3: GET /api/v1/reels?q=&page_ids=&origin=&from=&to=&metric_sort=&sort=&limit=&cursor=
  Search by known Reel/video/post ID or locally linked asset titles; imported caption search only if actually indexed.
  Sort includes posted_at_desc with id tie-breaker. Metric sorts allowed only for P0-proven compatible metrics, N/A last.
  Return stable internal Reel ID, Page, source, Meta IDs strings, posted_at, latest metric with collected_at/availability.

Extension 4: GET /api/v1/publish-jobs?q=&page_id=&status=&from=&to=&sort=&limit=&cursor=
  Search by known ID and safe local title. Filters narrow Page/status/time. No raw Meta upload URL or secrets.
  Status/attempt detail remains GET /publish-jobs/{id}.

Extension 5 (optional but recommended for 50 Pages):
  fb_pages.group_label TEXT NULL, locally edited via PATCH /api/v1/pages/{id} with enabled/group_label.
  GET /pages?group_label=... displays local group. Never infer from Facebook category.
  If group label is not approved, remove its filter from production UI instead of inventing data.

### G1-04 Deferred features (must be removed/disabled)
- Selection across ALL matching results with query token; use explicit up-to-100 IDs only.
- Drag & drop reschedule, bulk reschedule; no backend PATCH /jobs/{id} reschedule contract in this release. Calendar is read-only except opening existing safe job action.
- Auto tagging, collection management without DB/API, AI analytics intelligence, competitor scraping, monetization/earnings, comment management, cross-platform publishing.
- Group-by-asset analytics across imported Reels unless data lineage and aggregation contract proven.
- Unproven metrics (watch time, unique viewers, earnings) are N/A; don't invent UI numbers.

### G1-05 Database amendments
- publish_jobs per-target identity and uniqueness G1-01.
- media_assets.validation_status extends PENDING, VALID, INVALID, ERROR with REQUIRES_TEST.
- fb_pages.group_label if approved.
- Outbox events durable in PostgreSQL for publish dispatch/recovery.
- Preserve published_reels UNIQUE(page_id,fb_video_id) and nullable publish_job_id for IMPORTED.
- Index media_assets(created_at,id), publish_jobs(status,scheduled_at,id), published_reels(page_id,posted_at,id), reel_metric_snapshots(reel_id,metric_key,collected_at DESC); add tag/title search indexes only after EXPLAIN review.
- Do not add a mutable total_views as source of truth; most recent compatible snapshot is authoritative.
- Avoid deletes that orphan historical publish evidence; tokens stored as authenticated ciphertext and redacted logs.

G1 output: docs/adr/ADR_UI_V2_API_EXTENSIONS.md with ACCEPTED or PENDING decision per extension, all request/response examples, migrations and phase owner.

## 3. G2 — Harmonize technical specification, detailed plan, and tests

Required commits:
1. Update original technical spec with approved section for v2 large-scale UI, G1 endpoints, corrected DB uniqueness, enum and new pagination behaviors. Version canonical spec as v1.1, preserving a link from v1.
2. Update P0–P3 implementation plan with additional P1 media listing/usage endpoints, P2 Reels large-list sorting, P3 explicit targets/review matrix, and correct calendar scope.
3. Add docs/api/INTERNAL_API_CONTRACTS_V1_1.md AND planned OpenAPI YAML; after backend exists, compare generated FastAPI OpenAPI with the approved contract.
4. Add docs/database/SCHEMA_AMENDMENTS_V1_1.md (draft SQL + Alembic plan).
5. Add docs/ui/UI_V2_SCREEN_CONTRACT_MATRIX.md and docs/test/TEST_GATES_V1_1.md.
6. Update change log, phase ownership, all links and decision log. Avoid silently claiming unproven Meta v26 behavior.

Explicit tests to define:
TC01 same Page/multiple videos allowed.
TC02 duplicate client_target_id rejected.
TC03 Idempotency identical replay no new batch; modified replay 409.
TC04 preflight review fails on missing Page capability and invalid asset.
TC05 preview all 100 targets even when UI renders only 40 at a time.
TC06 >100 target request 422 with clear message and zero jobs.
TC07 media cursor, filtering/sorting consistency across inserts.
TC08 Reels 100k fixture sort global, filter by multiple Pages/origin and N/A.
TC09 jobs status/date/search cursor stability and no raw secrets.
TC10 usage history only if exact asset lineage exists.
TC11 local Page group only; no Facebook category fake data.
TC12 timezone +07 local/UTC roundtrip.
TC13 REQUIRES_TEST is not publishable.
TC14 UNCERTAIN cannot blind retry.
TC15 Page token revoke affects one Page, not all jobs.
TC16 missing metrics N/A, lifetime snapshot never SUM time series.
TC17 Redis restart and two worker lease race have no double local job.
TC18 Meta FINISH timeout state uncertain, not auto replay.
TC19 CSS/playwright keyboard and 1440/1024 screenshots.
TC20 feature blocked by phase/P0 gate never shows fake success.

G2 PASS when ALL user-facing behaviors have an API + database + test owner or marked DEFER, and docs no longer contradict on multi-target uniqueness, metrics, scheduling or selection.

## 4. G3 — Review, correct and lock UI v2 as implementation reference

Mockup is DESIGN REFERENCE, not production code. Runtime frontend should be React/TypeScript consuming cursor APIs, not copying 100k JavaScript fixture arrays.

Nine screen signoff criteria:
- Dashboard: operational alerts prominent; analytics KPI only when P2 metric supported and fresh.
- Fanpages: auth health, enabled state, optional local grouping and explicit permissions.
- Video Library: list default/grid optional, cursor-oriented next/previous, search by actual supported fields, bounded multiselect, asset detail, linked usage history.
- Publish: Quick (one video/multiple Pages) and Batch (many variants/many Page targets), per-target caption/title/time, preserved draft, max100 target review, server preflight and idempotent submit.
- Calendar: Agenda default, week/month summary, job details, no drag-to-reschedule.
- Reels: Page/source/time filters, numeric view metric with freshness/N/A, imported and Studio IDs separate.
- Analytics: selected-Pages aggregation, latest vs gained distinction, source metric provenance, CSV parity.
- Activity: state/attempt timeline, Page retry isolation, UNCERTAIN reconcile action and no blind retry.
- Settings: queue readiness, API/worker/credential health, never expose secrets.

Required mockup fixes:
1. Remove fake all-results selection toggle or label disabled with explanatory text.
2. Persist per-target schedule/caption keyed by stable client target ID, including navigation and review.
3. Cap explicit batch at 100; paginate/virtualize review so all targets visible and all validated.
4. Add 422/409/403/429/P0-blocked example states without pretending a Meta write occurred.
5. If exact counts absent in future backend, use cursor UX with has_more; avoid synthetic total page claims.
6. Explicit mapping between local asset, immutable variant and target Page IDs in composer.
7. Fix accessible focus, Escape, input labels, long captions, narrow screens; no false success toast.
8. Add deterministic fixtures and test UI transitions with Playwright rather than claiming screenshots alone prove behavior.

Freeze deliverables:
docs/ui/UI_V2_FREEZE.md records exact Git commit SHA + SHA256 of mockup, reviewed screen list, token/colors/components, intentional deferrals, known limits, 1440x900 and 1024x768 screenshot snapshots, Playwright results and reviewer decision.

If v2 PR #3 is accepted, merge only the reviewed v2 plus correct spec/contract adjustments. Close/supersede PR #2 v1 without overwriting v2. Any post-freeze change requires a versioned UI change request with BE contract impact.

G3 PASS means UI ready as frontend reference, NOT actual Meta API verified.

## 5. G4 — Implement P0 real Meta API feasibility harness (first runtime phase)

Reference official Meta Facebook API Postman collection for Page Access Token discovery and the Reels start/upload/status/finish phases. Verify current Graph version and scopes in the actual App. Old Postman examples cannot be treated as a tested v26 contract.

Implement tasks:
P0-01 create Python package, type-safe config, redacted HTTP client, minimal secure secrets reading, CLI plus no-secret diagnostics.
P0-02 OAuth with signed one-time state, CSRF safety, Page/User token handling, granted scopes readout; no plaintext tokens in logs/Git.
P0-03 GET /me/accounts using User token; select two Page IDs under operator control and validate actual Page tasks/capabilities.
P0-04 start Reel upload; use returned HTTPS host allowlisted Meta upload URL, upload real file, poll processing with bounded time, finish publish.
P0-05 re-query remote actual Reel by returned video ID and derive whether/how it maps to post ID/permalink.
P0-06 probe available Reel-level metrics on verified object, record graph_metric, object ID/type, value, timestamp; independently probe Page metrics (do not substitute Page metric for Reel metric).
P0-07 discover/import at least one previously published Reel, repeat Page discovery and publish/read on second Page.
P0-08 safe negative tests: auth 190, permissions 200, throttling 429, timeout after START/FINISH, invalid asset 100, all safely logged/redacted.
P0-09 freeze observed Meta adapter inputs/outputs in sanitized fixtures, P0_REPORT.md, P0_CAPABILITIES.md and P0_DECISION.json.

Live safety gates:
- All live tests opt-in; default pytest excludes live_meta.
- Publishing additionally requires RUN_META_PUBLISH_TESTS=1, exact owned Page ID, test media and explicit operator approval of visible target.
- Never blindly delete test Reels; cleanup only when explicitly authorized.
- No network call if credentials/permissions unavailable; report BLOCKED_EXTERNAL, not PASS.
- Use observed version of Meta API; configure, not hard-code assumptions about future media limits, token modes or watch metrics.

P0-GO MUST HAVE:
1. Two Pages owned/administered and discovered with actual publish permission.
2. A verified real test Reel on each Page, remote video_id/permalink or other reliable remote proof.
3. Real ID mapping and actual Reel-level metric result for >=1 Reel (successful zero only if valid response).
4. One preexisting Reel imported/discovered with identity.
5. Failure/permission/rate-limit/timeout cases classified; no duplicate blind publish.
6. Redacted evidence; exact API version; explicit supported/unsupported/blocked matrix.
7. Security tests and unit tests pass.

Decision:
GO only if all required live gates pass.
BLOCKED_EXTERNAL if no credentials/Page role/operator opt-in, or external temporary blocker.
NO_GO_REPLAN if required capability conclusively unsupported; adjust spec and scope before P1.
No P1/P2/P3 code development on a false GO.

## 6. P1 — Core Management (after P0-GO)

P1-01 one-command dev infra: React TS frontend, FastAPI, Postgres/Alembic, Redis/Celery, S3/MinIO, FFmpeg.
P1-02 internal OWNER session, CSRF, encrypted credentials, OAuth, audit logs.
P1-03 /pages and Page health/discovery, disable invalid Page targets, optional local group_label.
P1-04 streaming video upload, SHA256 exact-file dedupe, ffprobe, VALID/REQUIRES_TEST states, signed thumbnail/preview.
P1-05 server-side media search/filter/sort/cursor, immutable content variants and usage join.
P1-06 corrected publish batch/job/outbox schema and API contracts, preview and idempotency.
P1-07 one-Page real publishing from UI using P0 adapter; remote Reel verification.
P1-08 worker leases, DB durable due sweep, retries, uncertain reconciliation and safe cancel.
P1-09 frozen UI shell for Pages/Library/single Publish/Activity/Settings and empty/error/loading states.
P1-10 test gate: unit, contract, DB migrations, queue crash/restart, E2E and owned Page smoke.

P1 acceptance: one Page can connect, upload, choose variant, publish and verify, and system recovers errors without false PUBLISHED/duplicate attempts. Browser never pulls all 10k assets. P0 references retained in evidence.

## 7. P2 — Reels + Analytics (after P1, verified metric capability)

P2-01 per-Page Reel discovery/import and checkpoint pagination.
P2-02 reliable fb_video_id / fb_post_id mapping (when available), imported lineage remains nullable.
P2-03 metric registry enabled only after P0 evidence; poller sync run and timestamped snapshots with source info.
P2-04 aggregation on newest comparable Reel lifetime snapshot; separate Page-level daily metrics; no SUM snapshot history.
P2-05 GET /reels search/filter/cursor and metric sort with global DB semantics; 100k fixture tests.
P2-06 Reel drawer/timeseries, analytics dashboard, Page ranking, freshness and unavailable reasons.
P2-07 CSV same filters and values as UI, retains metric provenance/timezone.
P2-08 compare timestamps/values against real Meta UI, document differences honestly.

P2 acceptance: at least two Pages, imported and Studio Reel identity, supported metric snapshot, metric N/A distinct from zero, no fake “views in last 7 days”, CSV/UI parity and real spot-check report.

## 8. P3 — Bulk Publishing + Calendar + Operations Scale

P3-01 multi-video multi-Page composer producing EXPLICIT targets.
P3-02 stable per-target draft title/caption/schedule; local+UTC preview.
P3-03 server preflight of full batch, target-count cap=100, immutable intent and atomic idempotent submit.
P3-04 scheduler with global/per-Page concurrency settings, durable jobs in Postgres, rate limit backoff.
P3-05 per-Page independent outcomes, accurate failure/reconcile/blocked permission UX.
P3-06 calendar Agenda default, Week/Month summary, no unsupported reschedule.
P3-07 operational Activity filters, audit, alerts, manual safe controls.
P3-08 50 Page simulation, 10k assets/100k Reels/100k history fixtures, 300 jobs/day planning workload, backup restore, worker crashes.
P3-09 controlled 2–3 actual owned Page smoke with operator approval and exact expected job count.

Required P3 example: 20 videos assigned across 10 Pages to create exactly 60 explicit targets → 60 jobs, NOT automatically 200. An invalid target rejects the whole submission and 0 jobs; other Pages run independently only after successful atomic acceptance.

Performance engineering target (not a verified claim): backend list/dashboard p95 under 2s in fixed staging fixture; React render p95 under 500ms for a 50-row response on specified test hardware. Measure and record. Synthetic load does not establish Meta quota or API throughput.

## 9. Expanded test gates and CI

Gate G0: issue register and UI matrix 100% action coverage.
Gate G1: accepted ADR and spec field identity; no old UNIQUE(batch_id,page_id).
Gate G2: canonical spec/plan/openAPI/schema/test docs consistent, links valid.
Gate G3: 9 screens Playwright with screenshots 1440/1024, 60 explicit target draft/preview workflow, keyboard/focus, no hidden unsafe actions.
Gate P0_CODE: Ruff/mypy/pytest nonlive, Meta adapter mocks and secret scanning.
Gate P0_LIVE: actual authorized 2 Page and Reel-level metric evidence + previous Reel import.
Gate P1: schema migration, 1 Page end-to-end, worker recovery and security.
Gate P2: 100k fixture list, metric correctness, import, freshness, CSV parity.
Gate P3: 50 Page simulation, 2–3 Page live smoke, 100-target cap, atomic 422, idempotency, rollback and backup restore.

Adversarial tests:
- simultaneous workers claim one due job: exactly one lease.
- Redis restart: DB due scan recovers.
- START timeout without known ID: UNCERTAIN.
- FINISH timeout or successful API response without remote verification: UNCERTAIN/VERIFYING.
- invalid/revoked Page token: BLOCKED_AUTH and unaffected other Pages.
- retry only from known safe state, never blind UNCERTAIN.
- cancel SCHEDULED before side effect works; irreversible phase 409.
- unavailable insights shows N/A, legitimate 0 only from valid response.
- aggregate latest snapshots never SUM same Reel over time.
- exact IDs remain strings even above JS safe integer range.
- list sort global and cursor stable through concurrent inserts.
- request over limit and repeated Idempotency-Key act correctly.

Commands expected once runtime exists (report actual outputs):
- python -m pytest -q -m "not live_meta"
- python -m pytest -q -m live_meta (operator-controlled only)
- ruff check .
- mypy services/api/app
- frontend TypeScript/ESLint/Vitest/Playwright as configured by repo
- Alembic migrate upgrade/downgrade integration
- k6/Locust/pytest database fixture load with recorded p95

Do not claim tests PASS before actually running them.

## 10. PR and documentation deliverables

Recommended small PR sequence:
PR-A docs G0 issue register and UI matrix.
PR-B docs G1 ADR and G2 canonical spec/plan/schema/OpenAPI/test updates.
PR-C design G3 repaired UI v2 + freeze snapshots and acceptance.
PR-D feat P0 adapter/CLI/test harness, then report live status GO or BLOCKED_EXTERNAL.
PR-E feat P1 base auth/pages/media.
PR-F feat P1 single Page publisher and recovery.
PR-G feat P2 Reels ingestion/analytics.
PR-H feat P3 batch publisher/calendar/scale.

Never merge v1 mockup over frozen v2. Keep branch review and avoid direct main changes without review.

Every PR must contain:
- exact requirements/task IDs and paths changed
- UI→API→DB→test map updates
- migrations/security considerations
- actually executed commands with results
- screenshots if UI
- redacted Meta evidence or explicit BLOCKED_EXTERNAL
- truthful gate status and outstanding blockers.

Create docs/reviews/IMPLEMENTATION_STATUS.md per iteration:
Base SHA; branch/PR; tasks delivered; files; contracts/schema changed; test commands/results; known issues; gate PASS/FAIL/NOT_RUN/BLOCKED_EXTERNAL; next bounded task.

## 11. Final acceptance criteria

G0 PASS = audited screens + issue list, no omitted critical behavior.
G1 PASS = approved contract decisions and multi-target schema fix.
G2 PASS = technical spec and plan consistent with updated API/migrations/tests.
G3 PASS = UI v2 reviewed/frozen with exact SHA and test evidence, no false backend functionality.
P0 CODE READY does not equal P0 LIVE GO.
P0 LIVE GO = two owned Pages, real publish verification, real Reel views metric, previous Reel import and error evidence.
P1 GO = end-to-end verified single Page publishing and safe recovery.
P2 GO = correct sourced analytics and import.
P3 GO = reliable multi-video scheduling and scale test with controlled real Pages.

Do not mark any phase complete due only to code compilation, green mocks, or screenshots.

## 12. Copy-ready instructions for implementing model

You are implementing Facebook Reels Studio in plthien/Facebook-Reel-Studio. Start by reading this file and all 5 source files in section 0. Never assume PR status or source SHAs from memory.

Perform G0 → G1 → G2 → G3 in focused reviewable commits. Correct publishing-job uniqueness, document the approved API extensions, revise canonical spec/plan/tests, repair and lock UI v2 reference with browser evidence. No production P1–P3 coding yet.

After design freeze, implement P0 Meta adapter and guarded live tests. Obtain real opt-in from the operator using only their owned Pages. Record sanitized proof. If credentials/permissions are not supplied, report BLOCKED_EXTERNAL; do not claim P0 GO or proceed with P1/P2/P3.

Only after P0 LIVE GO, proceed P1, P2, P3 in that order, using the contracts and acceptance gates above. Self-review each PR, never invent passing test results, never change scope silently, and never retry an UNCERTAIN remote write without reconciliation.
