# Proposed PostgreSQL schema amendments v1.1 — NOT MIGRATED
Date: 2026-10-15 · ADR status **PENDING** · Scope P3 database/contract proposal. No database exists in this UI-only PR. Never mark migration PASS.

## 1. Per-target job identity — blocker
Replace `UNIQUE(batch_id,page_id)` with:
```sql
-- Future fresh-install publish_jobs table fragment:
target_index integer NOT NULL CHECK (target_index >= 0),
client_target_id text NOT NULL CHECK(length(client_target_id) BETWEEN 1 AND 128),
page_id uuid NOT NULL REFERENCES fb_pages(id),
variant_id uuid NOT NULL REFERENCES content_variants(id),
scheduled_at timestamptz NOT NULL,
caption_override text,
title_override text,
CONSTRAINT uq_publish_jobs_batch_index UNIQUE(batch_id,target_index),
CONSTRAINT uq_publish_jobs_batch_client_target UNIQUE(batch_id,client_target_id)
-- NO UNIQUE(batch_id,page_id)
```
Existing PostgreSQL DDL is illustrative: combine columns with the canonical table model, preserve UUID PK, job statuses, audit fields and `UNIQUE(meta_video_id)`. A Page can appear multiple times per batch when targets differ.

## 2. Batch intent/idempotency
```sql
-- Proposed publish_batches constraints:
client_idempotency_key text NOT NULL UNIQUE,
request_fingerprint text NOT NULL,
target_count integer NOT NULL CHECK(target_count BETWEEN 1 AND 100);
-- Future index names must be checked against actual Alembic revisions:
CREATE INDEX IF NOT EXISTS idx_publish_jobs_batch_index ON publish_jobs(batch_id,target_index);
CREATE INDEX IF NOT EXISTS idx_publish_jobs_due ON publish_jobs(scheduled_at,id)
WHERE status IN ('SCHEDULED','RETRY_WAIT','QUEUED');
CREATE INDEX IF NOT EXISTS idx_publish_jobs_status_page_date ON publish_jobs(status,page_id,scheduled_at,id);
CREATE INDEX IF NOT EXISTS idx_media_created_id ON media_assets(created_at,id);
CREATE INDEX IF NOT EXISTS idx_reels_page_date_id ON published_reels(page_id,posted_at,id);
CREATE INDEX IF NOT EXISTS idx_reel_snapshot_recent ON reel_metric_snapshots(reel_id,metric_key,collected_at DESC);
```
Submit entire batch and per-target jobs plus durable outbox intents in **one database transaction**; 422 means rollback/no jobs. Same Idempotency-Key and canonical intent returns same immutable batch; same key with changed intent returns 409. Canonical target identity includes Page UUID, immutable variant UUID, UTC, trimmed title/caption; exact duplicate *within one batch* is a **blocking validation failure**. Distinct publication occurrences with different schedules are allowed. Prevent unique violations leaking raw SQL in responses.

## 3. Media and optional local Page group
```sql
-- Extend media validation CHECK for fresh installation:
CHECK(validation_status IN ('PENDING','VALID','INVALID','ERROR','REQUIRES_TEST'));
-- Optional, only if Page grouping approved:
ALTER TABLE fb_pages ADD COLUMN IF NOT EXISTS group_label text;
CREATE INDEX IF NOT EXISTS idx_pages_group_label ON fb_pages(group_label,id);
```
`REQUIRES_TEST` (format/capability not verified at P0) cannot be targeted by preview/submit. `UNAVAILABLE` metrics are not recorded as numeric zero.

## 4. Migration and integrity gates
- **Fresh DB not yet deployed:** edit baseline Alembic revision before first deployment, review generated schema and apply in a staging DB.
- **Existing DB:** forward additive nullable columns → deterministic per-batch backfill index+client IDs → validate no duplicates/nulls → NOT NULL → drop old unique constraint → add new unique constraints within safe maintenance window. Do not guess existing constraint names. Provide reversible downgrades only if safe; rolling back to old uniqueness is impossible once same-Page multivideo batches exist—document irreversible data downgrade.
- Confirm legacy jobs keep stable state, existing remote Reel identity, ownership and attempts.
- Worker outbox, idempotency and UNCERTAIN reconciliation are unchanged and must survive restart/lease races.
- Test two videos same Page succeeds, exact duplicate intent fails 422, duplicate ID/index fails, different schedule valid, 101 target fails atomically, invalid Page/media fails atomically, key reuse same intent idempotent, key reuse changed intent 409, crash between transaction/dispatch safely recovers.
- Use EXPLAIN ANALYZE for filter/sort/query indexes at 10k assets/100k Reels/100k jobs; never assert performance until measured.

**Status:** proposed DDL only, migration NOT_RUN. P0 Meta live remains BLOCKED_EXTERNAL.
