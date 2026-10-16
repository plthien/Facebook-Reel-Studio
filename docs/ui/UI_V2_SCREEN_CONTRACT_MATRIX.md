# UI v2 control-level ↔ API ↔ DB ↔ test matrix
**Status key:** BACKED = documented only, not implemented; EXTEND = proposed addition, pending approval; DEFER = disabled/unsupported; DEMO = local interaction, no production API. **All Meta-dependent actions require P0 live capability evidence.**

| UI element / screen | Phase | API / request-response contract | DB & validation support | Test | Decision |
|---|---|---|---|---|---|
| Dashboard → Publish / action links | P1–P3 | Local navigation; dashboard aggregates GET /publish-jobs, GET /pages | Backend aggregate only, no 100k history load | UI01 | BACKED/DEMO |
| Dashboard health/metrics KPIs | P0/P2 | GET /system/health; GET /analytics/overview, metric availability | N/A until P0 proven, no fake metric totals | UI01 | BACKED/DEMO |
| Fanpages Connect Meta | P1 | GET /auth/facebook/start | OAuth server flow; scopes and owned Pages | UI01 | BACKED/DEMO |
| Fanpages search/status/group | P1 | GET /pages?q=&status=&group_label=&cursor=&limit= | fb_pages statuses; group_label optional locally | UI01 | BACKED/EXTEND |
| Fanpage Health detail | P1 | GET /pages/{id}/health | Permission/task checks, no tokens to UI | UI01 | BACKED/DEMO |
| Library Upload | P1 | POST /media | Media validation including REQUIRES_TEST; demo no upload | UI02 | BACKED/DEMO |
| Library List/Grid | P1 | GET /media cursor envelope, view client-side | 25/50/100 bounded page, lazy preview | UI02 | EXTEND |
| Library search/status/tag/sort | P1 | GET /media q,tag,validation_status,sort | Indexed search; allowlisted sort, stable cursor | UI02–03 | EXTEND |
| Library page-size/cursor next/back | P1 | GET /media limit,cursor,next_cursor,has_more | Count optional, cursor bound to filter/sort | UI03 | EXTEND |
| Library row checkbox, select visible/deselect | P1/P3 | Explicit client IDs, later server revalidation | Preserve selected IDs across cursor/filter | UI03–04 | BACKED/DEMO |
| Library transfer to Publisher | P3 | Selected IDs→immutable variant UUID before preview | 50/100 preserved, 105 blocked with no truncation; selection retained | UI04 | EXTEND |
| Library select every matching result | Post-P3 | Missing selection-scope-token contract | Disabled/no query-wide selection | UI04 | DEFER |
| Library asset drawer / Usage History | P1/P2 | GET /media/{id}, GET /media/{id}/publications | Verified asset→variant→job→Reel lineage | UI02 | EXTEND/DEMO |
| Publish Quick/Batch mode | P3 | Targets[] explicit, never cartesian product | Quick exactly 1 asset to selected Pages; mode switch preserves choices | UI05–06, UI19 | BACKED/DEMO |
| Publish sample 20/10/60 preset | Design only | No API; deterministic fixture | 60 explicit targets, not 200 | UI07 | DEMO |
| Quick Page chips add/remove | P3 | targets[].page_id per approved Page | Chips canonical; stable Quick client target IDs | UI05–06 | BACKED/DEMO |
| Quick Review Video/Page selection | P3 | Identity fixed by Quick mode | Both disabled; mismatch rejected | UI05, UI19 | BACKED/DEMO |
| Batch add/delete explicit target | P3 | POST /publish-batches/preview targets[] | client_target_id,target_index per row, max 100 | UI07, UI11 | EXTEND/DEMO |
| Batch Review variant/Page editors | P3 | targets[].variant_id/page_id UUID | Every edit invalidates fingerprint | UI08, UI10 | EXTEND/DEMO |
| Per-target caption/title editors | P3 | targets[].caption_override/title_override | Stable target identity and per-target state | UI05, UI08 | BACKED/DEMO |
| Target local datetime / default | P3 | targets[].scheduled_at UTC from Asia/Ho_Chi_Minh | Real date, future, minimum lead, immutable accepted intent | UI09 | EXTEND/DEMO |
| Review pagination/total counts | P3 | preview validates ALL 1..100 targets | Never validates visible 25 only; 422 atomic | UI07, UI11 | EXTEND/DEMO |
| Review duplicate warnings/errors | P3 | Preview targets[].errors/warnings, 422 code DUPLICATE_INTENT | Page+variant+UTC+trimmed overrides; identical blocks | UI10 | EXTEND |
| Review Validate | P3 | POST /publish-batches/preview | Fingerprint current intent, no jobs created | UI12 | EXTEND/DEMO |
| Review confirm / error-state demo | P3 | POST /publish-batches Idempotency-Key; 409/422 | Revalidate all, atomic, no real create in mock | UI11–13 | EXTEND/DEMO |
| Calendar Create Batch, Agenda/Week/Month | P3 | Local navigation; GET /publish-jobs?from=&to= | Read-only job grouping, mock counts | UI16 | BACKED/DEMO |
| Calendar Job detail | P3 | GET /publish-jobs/{id} | Status, attempts, ownership | UI16 | BACKED/DEMO |
| Calendar drag/reschedule | Post-P3 | Conditional PATCH not in v1.1 contract | Disabled, cannot change real dates | UI16 | DEFER |
| Reels Sync control | P2 | POST /pages/{id}/reels/sync | P0 availability, quota and Page permission | UI15 | BACKED/DEMO |
| Reels search/Page/origin/date | P2 | GET /reels?q=&page_ids=&origin=&from=&to=&cursor= | Stable Reel identity, Page/origin, no inferred asset link | UI15 | EXTEND/DEMO |
| Reels snapshot/detail | P2 | GET /reels/{id}, GET /analytics/reels/{id}/timeseries | Freshness, availability, measured zero distinct | UI15 | BACKED/DEMO |
| Analytics CSV, tabs, chart | P2 | GET /analytics/overview, pages, metric availability, export | Charts marked MOCK until P0-proven snapshots | UI01 | BACKED/DEMO |
| Activity System Health, filter/query/page/date | P1/P3 | GET /publish-jobs status/page/q/date/cursor | Stable job IDs/status and indexed query | UI14 | EXTEND/DEMO |
| Activity Job detail, UNCERTAIN reconcile | P1/P3 | GET /publish-jobs/{id}, POST /publish-jobs/{id}/reconcile | No blind external replay after UNCERTAIN | UI14 | BACKED/DEMO |
| Settings Fanpages and readiness | P0/P1 | GET /pages, GET /system/health; no secrets | Capability P0 unverified | UI01 | BACKED/DEMO |
| Settings 401/403/409/422/429/503, loading/empty | Design only | Demonstration of future failure handling | No network requests | UI13 | DEMO |
| Drawer close/Escape, tablet nav labels | UI | No backend operation | Focus management and responsive table scroll | UI14, UI17 | DEMO |

**CURRENT VERIFIED EVIDENCE:** [35/35 Chromium and contract PASS, run #38727389515](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38727389515) on `3adf11d259df40687177623810e1b6d1cb7cb62f`, **37 screenshot PNGs** ([Freeze Manifest](UI_V2_FREEZE.md)), [test ledger](../test/UI_V2_ACCEPTANCE_TESTS.md), [OpenAPI proposed reference](../api/openapi-v1.1.yaml), [schema DDL proposal](../database/SCHEMA_AMENDMENTS_V1_1.md). Production mapping of `aN` to immutable content variant UUID and `pN` to internal Page UUID is mandatory; demo IDs never belong in real API POST. The 50/10k/100k fixture counts are design targets only.


## G3 targeted repair traceability (2026-10-15)

| UI/control | Phase | Existing contract, request/response | State/DB validation | Test | Status |
|---|---|---|---|---|---|
| Quick Page Selector search, filter, selected count, checkbox & scoped eligible selection | P1/P3 | `GET /pages?q=&status=&group_label=&limit=&cursor=`; retrieve **all authorized Pages** across all cursor pages before local select-all | 50 known Pages, 45 ACTIVE, 5 BLOCKED_AUTH/EXPIRED disabled; canonical `composerPages[]` → one Quick target each; capability revalidated on P3 submit | QP-01–QP-10 | BACKED/DEMO, optional local group EXTEND |
| Library sort menu and cursor controls | P1 | `GET /media?sort=created_at_desc|created_at_asc|filename_asc`; filter+stable sort before cursor | Deterministic global fixture permutation, no 10k-object allocation; cursor/history reset, selection/search retained | SORT-01–05,10–12, PERF-01 | EXTEND/DEMO |
| Published Reels sort and disabled metric option | P2 | `GET /reels?sort=posted_at_desc` | Reel-level latest lifetime views sorting DEFER until P0 proof, N/A/freshness semantics; no cross-level metric | SORT-06–07 | EXTEND/DEMO; metric DEFER |
| Activity scheduled/created sort | P1/P3 | `GET /publish-jobs?sort=scheduled_at_desc|scheduled_at_asc|created_at_desc` | UTC values with stable per-ID tie-break, projected local schedule and createdAt fixture | SORT-08–12, PERF-01 | EXTEND/DEMO |
| Sidebar route clicks, direct hash, Back/Forward, drawer close | Frontend only | Hash router; **no new API** | Draft assets, mode, explicit targets and overrides preserved; invalid hash safely replaced with dashboard | NAV-01–09 | BACKED/DEMO |

Updated contract sort allowlists are proposals only. Screen history is frontend-only. Query-wide Library result selection and unsanctioned Meta metrics remain DEFERRED.

**G3_READY_FOR_APPROVAL — USER APPROVAL PENDING.** All referenced APIs, schema and database amendments are PROPOSED / NOT IMPLEMENTED; Meta P0 NOT_RUN / BLOCKED_EXTERNAL, production backend NOT_IMPLEMENTED. Historical 19/23 baseline is recorded in [Freeze Manifest](UI_V2_FREEZE.md).
