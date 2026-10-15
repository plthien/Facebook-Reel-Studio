# Facebook Reels Studio — UI v2 ↔ Backend / Spec Alignment Audit

**Status:** Design proposal, 2026-10-15. **Primary authority:** `docs/FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md` and `docs/IMPLEMENTATION_PLAN_P0_P3.md`. This document does not establish an implemented backend or a passed Meta API probe.

## Executive decision

**Visual update:** Keep v1's dark sidebar, white cards and blue/purple primary. Rebuild Library, Reels table, Publish Matrix and Calendar around high-volume data; move Activity to operational navigation. Use desktop-first, pagination and bulk operations with bounded selection.

**Contract outcome:** The v1 schema and endpoints support single-asset/multiple-Pages, per-Reel analytics subject to P0, and paginated data. The **multi-asset/multiple-posts-to-the-same-Page-in-one-batch workflow is NOT supported by v1 SQL** (`UNIQUE(batch_id,page_id)`). This requires the specific **P3 addendum** in `UI_V2_IMPLEMENTATION_ADDENDUM.md`. Full-library search/sort, asset display metadata, Page group, Reels availability filter, calendar rollups and asset usage view also require **internal, implementable** enhancements. Anything dependent on Meta data is marked P0-gated.

## Source of truth and vocabulary

| Concept | Actual schema | UI responsibility |
|---|---|---|
| Video Asset | `media_assets` | Immutable uploaded bytes + mutable editorial metadata (P1 addendum), validated codec/duration, hash. No invented Meta stats. |
| Content Variant | `content_variants` | Caption, title, tags, one `variant_id` per target. Saved as separate rows. |
| Publish Batch | `publish_batches` | Idempotent atomic *intent* submission, not a remote all-or-nothing publish. |
| Publish Job | `publish_jobs` | Exactly one variant x Page x scheduled occurrence per row. Runtime independently succeeds/fails. |
| Published Reel | `published_reels` | Remote FB video ID, optional FB post ID, origin, permalink if returned. Imported Reel has no automatic media asset link. |
| Reel Metric Snapshot | `reel_metric_snapshots` | Observed lifetime count + availability + collected_at + metric proof. Missing != zero. |
| Page Metric Snapshot | `page_metric_snapshots` | Separate Page-level daily metric, must never be displayed as Reel views. |

## 9-screen traceability matrix

**A** = contract exists in v1 spec, **B** = BE contract addendum is needed and implementable inside our own app, **C** = requires P0 real Meta probe and capability gate.

| UI / route | UI action or data | Backend endpoint / query | DB model | Phase | Contract |
|---|---|---|---|---|---|
| Overview `/dashboard` | Health, failed/uncertain jobs | `GET /system/health`, `GET /publish-jobs` | `fb_pages`, `publish_jobs` | P1/P3 | A |
| Overview | Current lifetime Reel views, snapshot growth | `GET /analytics/overview`, `GET /analytics/reels/{id}/timeseries` | `published_reels`, `reel_metric_snapshots` | P2 | A+C |
| Fanpages `/pages` | List, discover, enabled/health | `GET /pages`, `POST /pages/discover`, `PATCH /pages/{id}`, `GET /pages/{id}/health` | `fb_connections`, `fb_pages` | P0/P1 | A+C |
| Fanpages | Page group / operator label | `PATCH /pages/{id}` group field; `GET /pages?group` | `fb_pages.group_key` (new) | P1 | B |
| Video Library `/library` | 25/50/100 server-side paging; validation | `GET /media?cursor&limit&status`, `GET /media/{id}` | `media_assets` | P1 | A |
| Video Library | Title/tag/category global search/sort | `GET /media?q&category&tag&sort` | `media_assets.display_title/category/tags`, indexes | P1 | B |
| Video Library | Asset detail, Studio usage count/history | `GET /media/{id}/publications` plus optional derived summary | joins `media_assets→content_variants→publish_jobs→published_reels` | P2 | B |
| Publisher `/publish/new` | Quick 1 asset → 1 or N Pages | `POST /publish-batches/preview`, `POST /publish-batches` | `publish_batches`, `publish_jobs` | P1/P3 | A+C |
| Publisher | N assets → N Page allocations (including repeat Page) | Same endpoints with `target_key` and independent `variant_id` per target | new `publish_jobs.target_key`, amended uniqueness | P3 | B+C |
| Publisher | Caption/title and GMT+7 per target | POST targets `caption_override`, `title_override`, `scheduled_at` UTC | existing `publish_jobs` | P1/P3 | A |
| Publisher | Draft selection / row edits | Client-side in-memory draft (no API required); user re-confirm after reload | **No DB draft**; not marketed as server autosave | P3 | A/UI-only |
| Calendar `/calendar` | Agenda: jobs by date/status/Pages | `GET /publish-jobs?from&to&page_ids&status&cursor` | `publish_jobs`, `fb_pages` | P3 | B extends A |
| Calendar | Month/week count summaries | `GET /publish-jobs/calendar-summary?from&to&timezone` | `publish_jobs` aggregates | P3 | B |
| Reels `/reels` | Server-side list, Page, origin, date, sort | `GET /reels?...` | `published_reels`, latest snapshots | P2 | A+C |
| Reels | Search and filter metric availability | `GET /reels?q&availability&metric_sort` | joined Reel metadata + latest availability | P2 | B+C |
| Reels | Imported Reel thumbnail/title | Caption/metadata fallback; **no phantom asset link** | `published_reels.caption` | P2 | A; thumbnail only if Meta-proven |
| Analytics `/analytics` | Current lifetime views, snapshots, CSV | `GET /analytics/overview`, `GET /analytics/export.csv`, `GET /analytics/reels/{id}/timeseries` | metric definitions + snapshots | P2 | A+C |
| Analytics | Unsupported metrics UI = N/A with reason | `GET /analytics/metrics/availability` | `metric_definitions`, availability flags | P2 | A+C |
| Activity `/activity` | Cursor-list jobs, filter and details | `GET /publish-jobs`, `GET /publish-jobs/{id}` | `publish_jobs`, `publish_attempts` | P1/P3 | A |
| Activity | Reconcile UNCERTAIN, safe cancel | `POST /publish-jobs/{id}/reconcile`, `/cancel` | jobs/attempts | P1/P3 | A+C |
| Settings `/settings` | Redacted health, auth, readiness, audit | `GET /system/health`, `GET /pages/{id}/health`, `GET /audit` | connections/pages/audit | P1 | A |

## Hard limits / no fake functionality

1. All simulated counts/Pages/Reels/Jobs are explicitly labeled DEMO. Preview, Confirm, Reconcile, Upload and Meta Login **do not cause external side effects** in HTML mockup.
2. **No P0-PROVEN Facebook metric may be claimed before running actual live proof.** `page_media_view` is never substituted for per-Reel `post_media_view`.
3. A post's video ID and post ID remain separate strings. `IMPORTED` must not inherit a `media_asset_id` simply because title/thumbnail looks similar. Source availability may be N/A.
4. **One asset x one Page x schedule = one job; many assets x same Page = multiple jobs.** Requires P3 uniqueness migration before UI batch confirm becomes enabled in production.
5. Composer's `round-robin`, `all targets`, and spacing options only **prepare request rows client-side**; backend accepts explicit target rows, not hidden batch automation. 100-target cap (configurable) is a proposed application-side limit, not a Meta quota.
6. `Post /publish-batches` is all-or-nothing for **DB target validation**, not for eventual remote Facebook publishing; failures are independent per job.
7. No “select all 78,400 matching results” behavior. Mockup selects only displayed asset IDs (preserving selection across pages; max 100); large server-side all-matching selection needs a separate future API, therefore excluded.
8. Calendar month summarizes counts only, no massive DOM of all jobs. Agenda is the operational view.
9. No automatic video transformation, hash evasion, competitor scraping, AI caption generation, Ads, external monetization or remote scheduling bypass.
10. List rows and snapshot charts are placeholders. Do not ship code that creates and sorts 78,400 in-memory Reel objects in production: queries are server-side, paginated and indexed.

## Data semantics (must hold before UI code is implemented)

- `current_views` is the **latest lifetime** snapshot of a *specific Reel*; `views_gained_in_window` requires comparable snapshots at both boundaries. A snapshot is not a day bucket.
- Page daily media views and Reel lifetime media views are separate KPI families. Do not sum old lifetime snapshots across time or use a generic “7-day views” label for latest lifetime values.
- `UNAVAILABLE` / `ERROR` = `value=null`; only a valid response can be zero. UI's N/A filter relies on availability data.
- Use `collected_at`, `source_object_id`, `metric_key`, API version and known freshness in detail/export. If `permalink_url` missing, hide external link.
- Reels with `IMPORTED` origin can exist with `publish_job_id=NULL`; no editable publisher job is implied.
- Client selection uses internal UUID **strings**; Meta object IDs are strings and must never become JS numbers.
- Time edit field shows Asia/Ho_Chi_Minh; submit serializes ISO 8601 UTC `Z` and UI preview must display *both local and UTC*.

## UX acceptance gates for implementation

| Gate | Real app expectation | Phase |
|---|---|---|
| UX-01 | Backend filtering over 12,480 assets does not silently limit search to loaded rows; cursor stable across sort/filter | P1 |
| UX-02 | 25/50/100 rows per page; no more than one page worth of DOM by default; network calls cancel stale query | P1 |
| UX-03 | Select 50 current rows, move page, selected IDs still correct; invalid assets cannot be submitted | P1/P3 |
| UX-04 | `IMPORTED` Reel without asset link shows a generic preview; no fictional asset usage | P2 |
| UX-05 | `post_media_view` unavailable → N/A and human-readable reason; zero only when actual metric 0 | P2 |
| UX-06 | Month view displays date-level counts, Agenda retrieves cursor page, neither loads 100k jobs | P3 |
| UX-07 | Two targets `(asset A, Page X, 18:00)` and `(asset B, Page X, 19:00)` persist as separate jobs after migration | P3 |
| UX-08 | Same submit key+fingerprint returns same batch; same key+different body produces 409; no blind retry | P3 |
| UX-09 | Confirm never submits when any target is invalid; final review includes local time, UTC, caption and target count | P3 |
| UX-10 | P0 LIVE tests run with two owned Pages, Reel publish verified, Reel-level metric verified or documented no-go | P0 |

**Test datasets:** UI fixture 50 Pages / 12,480 assets / 78,400 Reels / 2,840 jobs (generated locally, no API). Separate backend tests should exercise at least 50 Pages, >=10k assets, >=100k Reels and 300 scheduled jobs/day with real Postgres EXPLAIN/latency measurements; thresholds specified in implementation tests, not inferred from mockup.