# UI v2 — Backend Contract & Implementation Addendum (P1–P3)

**Status:** Proposed contract change; requires approval/merge before implementation. **Not Meta API changes.** Canonical source: `docs/FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md` + `docs/IMPLEMENTATION_PLAN_P0_P3.md`.

## 1. Exact v1 contradictions and resolutions

| v1 item | Why it blocks v2 | Proposed resolution | Phase |
|---|---|---|---|
| `UNIQUE(batch_id,page_id)` | A batch cannot send 2 different videos to the same Page | Replace with `UNIQUE(batch_id,target_key)`; allow multiple rows/Page, preserve unique job identity | P3 |
| `media_assets` has no `display_title`, `category`, `tags` | Library cannot reliably search/filter by title/category/tag across all assets | Add mutable editorial metadata columns + `PATCH /media/{id}`; bytes/hash remain immutable | P1 |
| `GET /media` lacks `q`,`sort`,`category` | Mock filter would search client-only | Extend cursor endpoint and indexes | P1 |
| `fb_pages` no group field | Bulk Page-group selector cannot persist | Add `group_key`, optional patch/list filter | P1 |
| `GET /media/{id}` lacks publications | No asset usage history without a join endpoint | Add `GET /media/{id}/publications` derived ONLY from linked STUDIO publish jobs | P2 |
| `GET /reels` lacks full text + availability filter | Reels management data table cannot filter true N/A | Extend q/availability, compatible latest snapshot join | P2 |
| `GET /publish-jobs` single page_id | Agenda cannot filter multiple Pages & summary counts | Extend `page_ids` plus range; add `GET /publish-jobs/calendar-summary` | P3 |
| Media check allows only PENDING/VALID/INVALID/ERROR | v1 prose references `REQUIRES_TEST` but SQL rejects it | Add `REQUIRES_TEST` to check constraint or map to PENDING + validated report; prefer explicit status | P1 |

## 2. P1 schema & APIs (internal-only)

### 2.1 DB migration (illustrative Alembic target)

```sql
ALTER TABLE media_assets
  ADD COLUMN display_title text,
  ADD COLUMN category text,
  ADD COLUMN tags jsonb NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN metadata_updated_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE fb_pages ADD COLUMN group_key text;
-- Backfill: display_title = filename; group_key may remain NULL (Ungrouped).
UPDATE media_assets SET display_title = filename WHERE display_title IS NULL;
-- Replace existing validation_status check explicitly through Alembic migration.
-- Add enum value 'REQUIRES_TEST' to check when the P0 media contract is not confirmed.
CREATE INDEX idx_media_created_id ON media_assets(created_at DESC,id DESC);
CREATE INDEX idx_media_category ON media_assets(category);
CREATE INDEX idx_media_validation_created ON media_assets(validation_status,created_at DESC);
-- For practical partial/search performance, enable pg_trgm on supported PostgreSQL deployments:
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_media_title_trgm ON media_assets USING gin (display_title gin_trgm_ops);
CREATE INDEX idx_media_filename_trgm ON media_assets USING gin (filename gin_trgm_ops);
CREATE INDEX idx_media_tags_gin ON media_assets USING gin (tags jsonb_path_ops);
CREATE INDEX idx_pages_group ON fb_pages(group_key);
```

Maintain immutable binary identity via `sha256` and `storage_key`. Mutable editorial data never changes the original file bytes. Enforce category/tag length and normalized case in application validation; not all Unicode labels require separate indexed categories.

### 2.2 P1 API extensions

```http
GET /api/v1/media?q=me+chong&category=Drama&status=VALID&sort=created_desc&limit=50&cursor=opaque
GET /api/v1/pages?group=Drama&status=ACTIVE&limit=50&cursor=opaque
PATCH /api/v1/media/{asset_id}
Content-Type: application/json
{"display_title":"Drama mẹ chồng - Tập 01","category":"Drama","tags":["Series","Original"]}
PATCH /api/v1/pages/{page_id}
Content-Type: application/json
{"group_key":"Drama"}
```

List response includes `items`, `next_cursor`, `total_count` **optional** (count query only if bounded; otherwise `count_is_estimate` explicit), validation status and editorial metadata. Use stable `(created_at,id)` cursor ordering for `created_desc`; when sort is by metadata/usage, cursor must encode sort key + ID + normalized filter hash. Never page in JS after loading only 50 items. Enforce limit <=100, q length caps, field allowlists for ORDER BY, Postgres query timeouts and parameterized statements.

P1 tests: search a title beyond page 1; filter category+status combination; switch sort then paginate without duplicates/omissions on fixed dataset; patch metadata without touching file hash; no token leakage; 12.5k fixture catalog p95 query target agreed in staging.

## 3. P2: Reels / media usage / analytics

New internal read-only endpoint:

```http
GET /api/v1/media/{asset_id}/publications?cursor=opaque&limit=50
```

Derive via `content_variants.asset_id = media_assets.id` → `publish_jobs.variant_id` → `published_reels.publish_job_id`. Return only actual linked **STUDIO** publications with Page, posted_at, available Reel ID, permalink and latest compatible metric when proven. Return **no invented linkage** for IMPORTED Reels, unless there is a separately approved explicit mapping stored in a future schema. An asset may have 0 publications.

Extend:

```http
GET /api/v1/reels?q=drama&page_ids={uuid}&origin=IMPORTED&availability=UNAVAILABLE&metric_sort=views_desc&limit=50&cursor=opaque
```

- Searching Reel text: Studio -> variant title/caption; Imported -> `published_reels.caption`/remote IDs only (when available). Do not promise import thumbnail or transcript.
- `availability` supported values derive from latest snapshot with metric catalog enabled and proven; `UNAVAILABLE` is not 0, `ERROR` has its own reason.
- `metric_sort=views_desc` puts numeric views first, nulls last; deterministic tiebreaker (`posted_at,id`), no forced zero.
- API returns `metric_key`, `value`, `availability`, `collected_at`, `source_object_id`, `api_version`, `unavailable_reason` where relevant; respect scope.
- Add Postgres plan/index for latest snapshot per Reel and valid metrics. Review EXPLAIN with 100k Reels and concurrent sync inserts; materialize latest table only if measured performance justifies it.

**Gate:** If P0 per-Reel metric mapping is NO-GO, hide view ranking/analytics features in real UI; do not present mock data as actual. Imported Reels display generic thumbnail unless a supported Meta preview URL field was validated in P0/P2.

## 4. P3: multi-video batch compatibility migration

### 4.1 Schema

```sql
-- Alembic migration: backfill target keys before making column NOT NULL.
ALTER TABLE publish_jobs ADD COLUMN target_key text;
UPDATE publish_jobs SET target_key = id::text WHERE target_key IS NULL;
ALTER TABLE publish_jobs ALTER COLUMN target_key SET NOT NULL;
-- Actual index/constraint name must be read from current PostgreSQL catalog in Alembic.
ALTER TABLE publish_jobs DROP CONSTRAINT publish_jobs_batch_id_page_id_key;
ALTER TABLE publish_jobs ADD CONSTRAINT uq_publish_jobs_batch_target_key UNIQUE(batch_id,target_key);
CREATE INDEX idx_publish_jobs_page_due_v2 ON publish_jobs(page_id,scheduled_at,id);
```

**Do not copy/paste constraint name blindly:** Alembic introspects actual v1 migration. All already created jobs get unique backfilled target keys. No change to `(page_id,fb_video_id)` Reel uniqueness or `client_idempotency_key` semantics.

### 4.2 Additive preview/submit contract

```json
{
  "name":"Demo drama series",
  "targets":[
    {
      "target_key":"00000000-0000-4000-8000-000000010001",
      "page_id":"00000000-0000-4000-8000-000000000101",
      "variant_id":"00000000-0000-4000-8000-000000000201",
      "caption_override":"Episode 01",
      "scheduled_at":"2026-10-20T11:00:00Z"
    },
    {
      "target_key":"00000000-0000-4000-8000-000000010002",
      "page_id":"00000000-0000-4000-8000-000000000101",
      "variant_id":"00000000-0000-4000-8000-000000000202",
      "caption_override":"Episode 02",
      "scheduled_at":"2026-10-20T12:00:00Z"
    }
  ]
}
```

- Existing P1 callers with no `target_key`: **compatibility path** backend generates a stable target_key from canonical request ordinal within the idempotent request and persists it. New UI supplies explicit distinct target UUID strings generated client-side before review. The request fingerprint includes canonical ordered targets and overrides; same key + different body returns 409.
- Exactly one row per target (not one row per Page). Repeated `page_id` in same batch is allowed. Exact duplicate target_key in request is 422. Duplicate `(page_id,variant_id,scheduled_at)` should be rejected with user-readable 422 at preview/submit unless the operator clearly marks a permitted deliberate repeat through a later feature; v2 does not support that bypass.
- Max 100 targets/submit initial **internal safety limit**, not a Meta quota; make configurable, test memory/response size. Bulk of more than 100 should be split into separate independent batches only after the owner confirms boundaries.
- `preview` has **zero side effects** and returns each target's validation errors/warnings; `submit` atomically creates all intended jobs or rejects all with 422. After acceptance Meta execution is one independent job per Page×variant×occurrence.
- Client calculations: `round-robin`, cross-product mapping and staggering compute the exact `targets` array *before* preview. Backend has no hidden auto-mapping feature. Date/time must serialize as UTC while review displays Asia/Ho_Chi_Minh and UTC.
- Reuse v1 `caption_override`, `title_override` and `scheduled_at` fields; no Meta native schedule endpoint assumed.
- `UNCERTAIN` reconciliation remains strict; batch-level retry/repost is not enabled. User can operate on only proven-safe jobs.

### 4.3 P3 calendar API

```http
GET /api/v1/publish-jobs?from=2026-10-15T00:00:00Z&to=2026-10-22T00:00:00Z&page_ids={uuid1},{uuid2}&status=SCHEDULED&cursor=opaque&limit=50
GET /api/v1/publish-jobs/calendar-summary?from=2026-10-01T00:00:00Z&to=2026-11-01T00:00:00Z&timezone=Asia%2FHo_Chi_Minh&page_ids={uuid1},{uuid2}
```

Summary response (illustrative) returns `date_local`, `total`, and status counts, **not full jobs**. Query uses UTC range and converts to requested allowed timezone for grouping; no month view enumerating 100k jobs. Agenda fetches page size 50.

## 5. Phase implementation / required gate changes

| Phase/task update | Deliverable | New gate |
|---|---|---|
| **P0 (unchanged)** | Live Meta evidence for two owned Pages, publish, Reel-level view probe, import mapping | No v2 work may claim P0 PASS without external evidence |
| P1-03 | Page group attribute / PATCH filter | Page group consistent across composer and listing |
| P1-04 | Asset editable title, category, tags; q/sort/stable cursor | 12,480 asset fixture backend test; search beyond page one |
| P1-10 | Correct state of `REQUIRES_TEST`; validation UI blocked accordingly | Invalid/unproven never enters publish queue |
| P2-01/02 | Imported Reels have no phantom asset; publications endpoint only Studio join | Usage count matches DB JOIN, imported not linked |
| P2-03/06 | Metric search/sort/availability semantics verified by P0 | N/A != 0; cursor stable under metric_sort |
| P3-01/02 | Bulk Publisher target-matrix preview, separate immutable target-key per job | Two videos → same Page → two persisted jobs; preview rows = submit rows |
| P3-03 | Backfilled migration and uniqueness; idempotency fingerprint | Same key/payload no duplicate; changed payload 409 |
| P3-06 | Calendar range filters + date rollup API | Agenda ≤50 rows; 50 Pages ×3 jobs/day month rendered as counts |
| P3-08 | Multi-Page load tests + failure isolation after schema amendment | 100 targets/batch, 50 Pages simulation, zero blind resend |

### Adversarial acceptance tests

1. Seed 50 Pages, 12,480 media_assets, 100k published_reels; run EXPLAIN ANALYZE and instrument list API p95 target under staged environment.
2. Search for item #12000 by name and tag; never require first 50 loaded; output after cursor filters retains stable sort.
3. Create two variants A+B into same Page X in same batch -> 2 jobs with different target_key; both independent after worker restart.
4. Single video on 3 Pages -> 3 jobs, no regression.
5. Identical target_key within same request -> 422, no rows; same Page+variant+instant duplicate -> preview error.
6. Idempotent same key + same fingerprint -> same batch, no duplicate; same key different payload -> 409.
7. Timeout after FINISH -> UNCERTAIN and reconciliation, no automatic repost even if another target succeeded.
8. Asset INVALID/REQUIRES_TEST -> explicit validation error on preview and blocked submit.
9. Imported Reel with no publish_job never contributes to `GET /media/{id}/publications`.
10. Views N/A/source mapping absent -> no ranking as zero; no numeric “0 views” without real successful metric response.
11. 100-target simulated batch always <=100 jobs and distributes according to explicit matrix; 101 target preview rejected before submit.
12. Calendar summary matches SQL count, with GMT+7 day boundaries and no double counting; Page filter actually affects results.

**Prioritization:** Do not widen Meta permissions in order to satisfy a visual design. All new BE functionality above is internal PostgreSQL/FastAPI work; P0 remains the hard external dependency. Additional V2 contract changes require product approval/PR merge before Codex modifies models.