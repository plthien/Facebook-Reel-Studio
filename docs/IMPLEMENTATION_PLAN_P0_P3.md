# FACEBOOK REELS STUDIO — IMPLEMENTATION PLAN P0–P3

> Canonical technical specification: [TECHNICAL_SPEC_V1](FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md). Do not mark live Meta requirements PASS without redacted real-world evidence.

## 10. Implementation plan — independent phases / exact tasks

### P0 — META FEASIBILITY (no full UI; minimal CLI + adapter skeleton)

**Goal:** Test real Meta App/Page capabilities, freeze external contract from evidence. **No simulated-success acceptance.**

| ID | Task | Output |
|---|---|---|
| P0-01 | Create repository skeleton, config, env validation, HTTP Meta client, redact-safe logging | Minimal testable Python package |
| P0-02 | OAuth Meta auth flow, scopes, permissions check, secure credential handling | Functional account connect test flow |
| P0-03 | GET `/me/accounts`, Page/role/task capability parser | Page discovery diagnostic |
| P0-04 | Start/upload/status/finish Reel POC using returned upload URL | Successful tested Reel, actual ID |
| P0-05 | Verify publication via Facebook Reel list/object/permalink | Published evidence & mapping |
| P0-06 | Page/Post Insights probes including `post_media_view` | Metric availability matrix with raw proof |
| P0-07 | Import 1+ pre-existing Reels, repeat on second Page | Legacy ingestion proof |
| P0-08 | Negative tests and scope loss, timeout handling, sanitized evidence | Failure classification |
| P0-09 | Freeze adapter request/response fixtures and P0 decision | `P0_REPORT.md` and `decision.json` |

**P0 tests:** unit mocks for Meta errors, a live test script `pytest -m live_meta` (skip by default), test fixtures self-owned. Live tests may publish content and must be explicitly enabled `RUN_META_PUBLISH_TESTS=1`; scripts show target Page/video before execution. No live credentials in GitHub Actions or screenshots.

**P0 acceptance:** End-to-end `connect → Page → upload → publish → verify` on 2 Pages; per-Reel metric at least one real Reel; no secret in logs; source ID mapping documented; unsupported metrics labeled. If one path blocked, file issue with reproduction and **do not begin P2 dependent UI**.

### P1 — CORE MANAGEMENT (single-page publishing fully operable)

**Dependencies:** P0 `P0-GO`.

| ID | Task | Output |
|---|---|---|
| P1-01 | Docker Compose, PostgreSQL/Alembic, Redis/Celery, MinIO, API/UI projects | One-command local bring-up |
| P1-02 | Internal login and OWNER authorization | Protected app pages/API |
| P1-03 | Persistent encrypted FB connections and Page discovery/health | Working Fanpages screen |
| P1-04 | Media upload, streaming, hashing, ffprobe/validation, preview | Working Library |
| P1-05 | Content variants, immutable publish batch & job schema | Versioned content and job intent |
| P1-06 | MetaAdapter P0-proven integration + status/error normalization | Real provider adapter |
| P1-07 | Celery queue, Postgres due sweep/outbox, state machine, attempt log | Reliable single-Page publication |
| P1-08 | Recover stale jobs, uncertain reconciling, safe cancel/retry | No blind double-publish |
| P1-09 | Job activity, details, audits and health UI | Observable lifecycle |
| P1-10 | Unit/contract/integration/E2E/live smoke tests, docs | P1 release gate |

**P1 acceptance:** Connect and reauthorize; upload 1 video, publish to 1 Page; remote verify; restart worker at each phase in fixtures, no lost jobs/false success; token 190 visible as blocked; `curl`/OpenAPI contracts verified; tests pass. No multi-Page composer requirement yet.

### P2 — REELS ANALYTICS (views correctness before fancy visuals)

**Dependencies:** P0 verified metric+object mapping; P1 data model/jobs.

| ID | Task | Output |
|---|---|---|
| P2-01 | Reels discovery + cursor pagination/backfill per Page | Ingest old and Studio-created Reels |
| P2-02 | Confirm object ID mapping, remote delete/inaccessible cases | Correct `fb_video_id` ↔ `fb_post_id` |
| P2-03 | Metric catalog per API version/capability | Explicitly enabled metrics |
| P2-04 | Metrics pollers, snapshots and sync runs | Timestamped historical data |
| P2-05 | Aggregation/query layer, careful Page vs Reel semantics | Correct analytics endpoints |
| P2-06 | Dashboard, Reel list/detail, filters, freshness, N/A states | Working analytics UI |
| P2-07 | CSV export + report metadata | Portable audited dataset |
| P2-08 | Data quality tests and live comparison against Meta UI | Reconciliation report |

**P2 acceptance:** At least 2 Pages and multiple Reels, including one imported Reel, metric snapshots can be queried; absent permissions => N/A not zero; lifetime snapshots aren't summed across time; Page metrics never masquerade as Reel metrics; CSV and UI agree; freshness displayed; actual metric parity differences documented with timestamps.

### P3 — BULK PUBLISH & PRODUCTION HARDENING

**Dependencies:** P1 state machine and P2 analytics. Can begin basic batch engine after P1, but overall release still requires P2 validation.

| ID | Task | Output |
|---|---|---|
| P3-01 | Multi-select Pages, per-target caption/title/scheduling form | Bulk composer UI |
| P3-02 | Read-only preview matrix + atomic batch submit | No partial accidental creation |
| P3-03 | Per-target DB uniqueness and Idempotency-Key hash enforcement | Duplicate-safe requests |
| P3-04 | Distributed scheduler and rate-limit aware concurrency | 10–50 Page dispatch |
| P3-05 | Independent target retries and reconciliation workflow | Per-Page outcome / no collateral failures |
| P3-06 | Read-only Agenda/Week/Month calendar; reschedule DEFERRED | Usable operations calendar |
| P3-07 | Queue dashboard, audit, alerting and manual interventions | Production observability |
| P3-08 | 50-Page simulation, soak, crash/restart, backup/restore | Release confidence |
| P3-09 | One controlled live multi-Page launch + complete verification | Go-live evidence |

**P3 acceptance:** 50-page dry simulation; real live smoke of 2–3 owned Pages; batch has exactly expected job count; no duplicated jobs on repeated POST; 1 Page failure isolates; worker crashes do not cause unverified duplicate publication; queue/metrics consistently recovered; scheduler reports deviations without pretending exact publication time.

---

## 11. Test gates, fixtures and acceptance matrix

### 11.1 Automated suites

| Suite | Tool | Must validate |
|---|---|---|
| Static quality | Ruff + mypy + ESLint + TypeScript | No obvious type/lint violations |
| Unit | pytest, Vitest | Domain validators, state transitions, aggregator math |
| API contract | pytest + snapshot/OpenAPI | Response schemas, errors, idempotency |
| DB integration | pytest + PostgreSQL test DB | Alembic migrate up/down, constraints, rows/leases |
| Worker integration | Celery eager/mocked transport + Redis/Postgres containers | Enqueue, dedupe, stale lease recovery |
| Meta adapter contract | HTTP mock fixtures recorded from P0 (sanitized) | upload phases, status shapes, 190/200/429, timeout |
| UI E2E | Playwright | Connect state, upload, compose, review, activity, analytics |
| Security | secret scanning + header/CORS tests | No token/log leaks, CSRF, SSRF restrictions |
| Live Meta | Manual guarded pytest | Actual external behavior with owned Pages only |
| Capacity | locust or k6 + fixtures | 50 pages, 300 due jobs/day simulation, paginated analytics |

### 11.2 Required adversarial tests

1. Double-click Submit and resend same `Idempotency-Key` → one batch only.
2. Same key + modified targets → 409; no silent job change.
3. Two workers claim same due job simultaneously → one owner lease; only one attempted execution.
4. Redis deleted/restarted after job creation → due sweep recovers job.
5. Timeout after Meta START but before response persisted → `UNCERTAIN`, no automatic second START.
6. Timeout after FINISH (Meta possibly published) → `UNCERTAIN`, reconciliation before any retry.
7. Meta upload acknowledged but video processing stuck → bounded wait; safe status and error reporting.
8. Page token revoked during batch → that Page blocked; remaining Pages continue.
9. User cancels while job `SCHEDULED` → no Meta call; cancellation during `FINISHING` returns conflict.
10. All metrics absent (Page threshold/permissions) → N/A with explicit reason; not 0.
11. New views 100 at T1 and 150 at T2 → `current_views=150`, not 250; delta=50.
12. Imported Reel without matching Studio job → dashboard includes record with `origin=IMPORTED`.
13. Facebook IDs larger than JS safe integer range → exact string throughout serialization.
14. API returns 200 `success=true` yet no visible Reel → `VERIFYING/UNCERTAIN`, never `PUBLISHED`.
15. Admin disconnects Page → exclude from queue, no orphan cross-Page token access.
16. Attacker submits arbitrary upload URL → URL never fetched; only allowlisted Meta returned endpoints accepted.
17. Test older API/deprecated metrics → catalog disabled, graceful fallback, no fake trend.
18. Database backup restores with jobs in external phase → recovery marks uncertain/reconciles safely.

### 11.3 Gate signoff checklist

**P0:** Actual token+permissions; 2 Page verification; 1+ verified live Reel with permalink; valid per-Reel views probe; old-Reel read; masked evidence; explicit go/no-go.  
**P1:** One Page fully manageable in UI; every error visible; recovery; migration+deploy; QA signed.  
**P2:** Metrics semantics correct; freshness; N/A; imported Reel; CSV parity; manual Meta UI spot-check logged.  
**P3:** 50 Page mock load; 2–3 Page live run; no duplicates in induced retries; cancellation semantics; backup restore; runbook and on-call checklist.

**No phase may be declared DONE from source code compilation alone.** Every phase must attach reproducible tests, evidence and acceptance criteria output.

---

## 12. Operational runbook

### 12.1 Daily operations

- Check Page auth/permissions statuses and token lifecycle; reconnect when needed.
- Check scheduled overdue, publishing failed/uncertain, oldest queue age.
- Check latest Reel metric sync timestamps, API quota headers and unavailable metrics.
- Inspect DB volume/storage, backup success, expiring signing keys or certificates.

### 12.2 Incident classes

- **S1 double publication suspected:** Freeze affected Page jobs, preserve attempt records, inspect remote video IDs and Page Reels, operator review, never auto delete without confirmation.
- **S2 Meta permission revoked:** Block Page queue, request reauthorization, leave unrelated Page jobs unaffected.
- **S3 Graph API metric removed:** Disable metric registry entry, show N/A reason, retain historical data and schema versions.
- **S4 Redis outage:** Database job intent remains; restart broker then sweep due jobs; check lease conflicts.
- **S5 credential compromise:** Rotate runtime encryption key and credentials as supported, revoke affected Meta authorizations, audit access.

### 12.3 Deployment gate

One-command local stack start; deterministic migrations; health checks; readiness at `/health/ready`; backups + one tested restore; HTTPS on public callback; token-less log scanning; independent worker reload; release tag + rollback instructions.

---


## 14. Instructions for Codex implementation

**Implement P0 only first; do not code P1–P3 before P0 decision.** For each task:

1. Read this spec and the actual repo tree; avoid inventing fake APIs, records, Page tokens or completed live results.
2. Keep changes scoped to current phase; write Alembic migrations rather than undocumented DB mutations.
3. External Meta API adapter must be replaceable/versioned and backed by sanitized live response fixtures.
4. For every PR include: changed files, architecture implications, executed tests, failed tests, live-vs-mocked matrix, evidence path, remaining blockers.
5. Fail closed on token/permission mismatch, Meta ID mismatch, uncertain publish and unsupported metrics.
6. Never implement anti-duplicate detection evasion, credential extraction or scraping to bypass Meta access limits.
7. After each phase run code audit and adversarial tests above, then assess acceptance matrix honestly.

**P0 task prompt for Codex:**

> Build a minimal P0 Meta Feasibility Harness for an internal 10–50 Facebook Page Reels Studio, following sections 0, 2, 10 (P0) and 11 of this specification. Target Graph API v26.0 with a versioned adapter; use official OAuth and Page tokens; perform start/upload/status/finish/verify Reels flow; discover Page Reels and map video/post IDs; attempt post_media_view and page_media_view; demonstrate real live capability on 2 owned Pages only when credentials are explicitly provided. Record redacted evidence, write unit/mock contract tests plus opt-in live tests, do not make fake success claims, and finish with a signed PASS/BLOCKED/FAIL matrix. Do NOT start building the full dashboard or P1 features until P0-GO.

---


## Source references

See [technical specification section 15](FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md#15-verified-sources-and-scope-notes).


## UI v2 design amendments — PROPOSED / AWAITING APPROVAL

The PR #3 reference requires explicit max-100 `targets[]` with stable `target_index`, `client_target_id`, `variant_id`, `page_id`, caption/title override, UTC schedule and independent target identities. One Page may receive multiple videos per batch. Every preview validates every target; submission revalidates atomically, preserves idempotency and fails with 422 (invalid) or 409 (changed idempotency intent). The schema changes are proposals, NOT applied migrations. Use the ADR, `docs/api/INTERNAL_API_CONTRACTS_V1_1.md`, UI traceability matrix and acceptance gates. Calendar rescheduling is deferred. P0 live Meta verification is NOT_RUN; no production P1–P3 implementation is authorized by this design amendment.
