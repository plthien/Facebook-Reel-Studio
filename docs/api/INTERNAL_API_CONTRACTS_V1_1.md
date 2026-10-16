# Proposed internal REST API v1.1 — UI v2 reference
**Status: PENDING review; NOT IMPLEMENTED.** Prefix all paths with `/api/v1`; internal IDs UUID; remote Meta IDs strings; server API datetime UTC ISO-8601 with offset; UI Asia/Ho_Chi_Minh.

| Operation | Phase | Query/request | Response / invariants |
|---|---|---|---|
| GET /media | P1 EXTEND | `q,tag,validation_status,sort,limit,cursor` | Cursor envelope; name, ID, filename and indexed variant title search; sorts created_at_desc/asc,filename_asc; `REQUIRES_TEST` non-publishable |
| GET /media/{id}/publications | P1/P2 EXTEND | `limit,cursor` | Verified variant/job/Reel lineage only; imported unlinked unless evidence |
| GET /pages | P1 BACKED + optional EXTEND | `q,status,group_label,limit,cursor` | Group is local optional field, not Facebook Page category |
| GET /reels | P2 EXTEND | `q,page_ids,origin,from,to,sort,metric_sort,limit,cursor` | Return Reel UUID, Meta string IDs, Page, origin, posted_at, metrics availability/collected_at; sort=posted_at_desc for current v2; metric_sort DEFERRED until P0-proven |
| GET /publish-jobs | P1/P3 EXTEND | `q,page_id,status,from,to,sort,limit,cursor` | Stable job ID, status, Page, schedule; sort=scheduled_at_desc/asc or created_at_desc; no token or upload secret |
| POST /publish-batches/preview | P3 EXTEND | Explicit targets array | Full per-target validation, counts/fingerprint; **no jobs created** |
| POST /publish-batches | P3 EXTEND | Same targets; Idempotency-Key | Atomic revalidation; 201/200 same intent, 409 conflict, 422 errors with zero jobs |
| GET /publish-jobs/{id} | P1 BACKED | Job ID | Attempts; UNCERTAIN reconcile info, no blind replay |
| GET /publish-batches/{id} | P3 BACKED | Batch UUID | Batch id, fingerprint, target count and per-target job IDs; ownership-scoped, no sensitive token |

List envelope:
```json
{"items":[],"next_cursor":null,"has_more":false,"total_count":null,"count_is_estimated":false,"applied_filters":{}}
```
Pagination: limit ∈ {25,50,100}, default 50; stable order tuple, opaque cursor bound to filters/sort, invalid cursor HTTP 400; `total_count=null` never means zero results. Search/filters/sort are server-side, not client filtering historical datasets.

Batch request (client generates opaque stable ID per target; UUID values below illustrative):
```json
{"name":"Editorial batch","targets":[{"client_target_id":"target-00001","target_index":0,"variant_id":"00000000-0000-4000-8000-000000000001","page_id":"00000000-0000-4000-8000-000000000002","scheduled_at":"2026-10-20T12:30:00Z","caption_override":"Short caption","title_override":null}]}
```
Preview response:
```json
{"request_fingerprint":"sha256:example-not-a-real-hash","total":1,"valid":1,"warnings":0,"invalid":0,"targets":[{"client_target_id":"target-00001","ok":true,"errors":[],"warnings":[]}]}
```
The server must reject duplicate client IDs, out-of-range target_index, missing ownership, invalid/REQUIRES_TEST media, inactive/unauthorized Pages, invalid/too-soon schedule, >100 targets and unsupported payload fields; no silent truncation. Exact duplicate target intents in one atomic batch generate **blocking** `DUPLICATE_INTENT` with client_target_id (HTTP 422). Canonical tuple: (page_id, variant_id, scheduled_at UTC, trim(title_override||''), trim(caption_override||'')). Different scheduled occurrences / different variants on one Page are permitted. Backend independently enforces minimum lead and clock validation. UI mock default 10 minutes is configurable, not a Meta limit. Prior preview fingerprint is invalidated when target intent changes. Explicit target count is independent of asset count × Page count. The single DB transaction and outbox guarantee no partial writes.

Error examples (proposed):
```json
{"code":"TARGET_VALIDATION_FAILED","status":422,"targets":[{"client_target_id":"target-00001","errors":[{"field":"variant_id","code":"ASSET_INVALID"}]}]}
```
```json
{"code":"IDEMPOTENCY_INTENT_CONFLICT","status":409}
```
429 uses retryable rate-limit metadata but never blindly repeats external FINISH. Dynamic Page authorization must be rechecked before submit. GET media usage counts distinguish actual published Reels, Page count and job attempts. P2 snapshots include `metric_key`, `source`, `collected_at`, `availability`, and measured zero separately from N/A. Date-based view delta only from compatible snapshots; lifetime total is never window gain.

**DEFER:** selection of all filtered matches, rescheduling PATCH, unproven metrics and inferred imported Reel associations.


## G3 targeted clarification — UI sorting and complete Page selection (PROPOSED)

- `GET /media` sort allowlist remains `created_at_desc`, `created_at_asc`, `filename_asc`, with **globally consistent ordering** before cursor pagination. Use a stable internal UUID tie-break for identical values. Fixture uses deterministically generated sortable filename/created_at; real backend must filter/sort before paging.
- `GET /reels` current UI exposes **only `posted_at_desc`**. `metric_sort` is explicitly **disabled/deferred** until P0 provider capability, availability/freshness semantics, and P2 aggregation are verified. Do not ship `views_desc` as a usable sort.
- `GET /publish-jobs` currently proposes `scheduled_at_desc`, `scheduled_at_asc`, `created_at_desc`. Stable UUID tie-break and filter/sort-bound opaque cursor are required. Date/time sorts use UTC on backend; UI shows GMT+7.
- Quick Page Selector must fetch the **entire authorized Page inventory** (10–50 Pages) using existing `GET /pages` cursor until `has_more=false`, before presenting a local “Select ACTIVE Pages in current filter” action. No new bulk-selection endpoint or infinite-result selection token is introduced. P3 submission revalidates every Page's capability.
- Browser hash/Back/Forward sync is **frontend-only**, no new API endpoint.

All of the above are proposed designs, not implemented endpoints or P0 evidence.
