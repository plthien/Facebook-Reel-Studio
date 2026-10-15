# ADR UI V2 — Proposed API and schema amendments
Date: 2026-10-15 · Status: **PENDING USER APPROVAL** · Scope: PR #3 design; no deployed migration or API.

## Decision D1 — atomic, explicit target intent (P3)
Replace `UNIQUE(batch_id,page_id)` with `target_index INT NOT NULL CHECK(target_index>=0)`, `client_target_id TEXT NOT NULL`, `UNIQUE(batch_id,target_index)` and `UNIQUE(batch_id,client_target_id)`. Each job records `variant_id`, `page_id`, caption/title overrides and UTC `scheduled_at`; after acceptance intent is immutable. Two distinct targets for the same Page in one batch are valid. Preserve remote Reel uniqueness, outbox transaction and recovery protections. Fresh installations update baseline Alembic; deployed installations require safe forward migration/backfill and rollback.

Preview and submit use **1–100 explicit targets** only. No automatic N×M fan-out, no silent split, no partial creation. Client IDs survive edits and review paging. `POST /publish-batches/preview` validates **all** targets without committing. `POST /publish-batches` atomically revalidates, binds an `Idempotency-Key` to a canonical request fingerprint; changed intent with same key → 409, any invalid target → 422 with zero jobs. Implementing this needs transaction/rollback, concurrency and lease tests.

## Decision D2 — cursor lists (P1/P2/P3)
Use allowlisted filters, stable `(sort_value, internal_uuid)` tie-breakers, opaque cursor bound to query/sort, 25/50/100 limits and optional exact/estimated count. Never derive numeric total pages from null `total_count`. Explicit selected IDs can persist across loaded pages; query-wide selection tokens are **DEFER**.

## Decision D3 — provenance and availability
Asset→content variant→publish job→published Reel is the only automatic usage lineage; IMPORTED Reels remain unlinked unless verified. `REQUIRES_TEST` fails closed. Metric `UNAVAILABLE`, `STALE`, measured zero, latest lifetime value, compatible-snapshot delta, and Page media views remain distinct. P0 determines Meta metric capability.

## Decision D4 — deferred scope
No drag/reschedule PATCH in P0–P3 UI v2, no query-wide selection, no inferred imported asset linkage, no unproven analytics KPI. Page `group_label` is optional proposed local DB field; remove filter if not approved.

## Approval gate
These are proposed design contracts only. User approval + migration/API contract tests are mandatory before implementing them. P0 Meta feasibility is a separate live gate.
