# UI v2 screen ↔ backend ↔ test traceability
Status: Design decisions only. BACKED means documented (NOT implemented); EXTEND means proposed; DEFER is disabled; DEMO never a real mutation.

| Screen | Action/visible state | Decision | Phase/API & schema | Gate / test |
|---|---|---|---|---|
| Dashboard | Action Center; uncertain/auth alerts | BACKED/DEMO | P1 GET /publish-jobs, health aggregate; no full history loads | UI01/UI12 |
| Dashboard | Views KPIs | DEFER | P0/P2 capability registry; no invented views | UI14 |
| Fanpages | Search, health, authorization | BACKED | P1 GET /pages, GET /pages/{id}/health, auth start; permissions | UI01/UI12 |
| Fanpages | Group filter | EXTEND | P1 optional fb_pages.group_label | UI03 |
| Video Library | List default/Grid; bounded cursor, search/tag/status | EXTEND | P1 GET /media; media.validation_status REQUIRES_TEST | UI02/UI03 |
| Video Library | Explicit IDs across loaded pages | BACKED | client state + server revalidation | UI04 |
| Video Library | All matching filtered results | DEFER | no selection-scope contract | UI13 |
| Video Library | Usage history drawer | EXTEND/DEMO | P1 GET /media/{id}/publications; variants/jobs/Reels lineage | UI05 |
| Publish | Quick: one asset→selected Pages | BACKED | P3 explicit targets; UUID/UTC conversion | UI06 |
| Publish | Batch: manually assign each video/Page | EXTEND | P3 targets[]; `client_target_id` and target_index; no `UNIQUE(batch_id,page_id)` | UI07/UI08 |
| Publish | Per-target title/caption/time persist | EXTEND/DEMO | P3 stable target identity; overrides, scheduled_at UTC | UI07 |
| Publish | Full matrix pages/100-target cap | EXTEND | P3 preview validates all; atomic POST with 409/422 | UI08/UI09/UI10/UI11 |
| Publish | Final demo confirmation | DEMO | no backend publish invoked | UI08 |
| Published Reels | Page/origin/search/date/cursor | EXTEND | P2 GET /reels; stable Reel UUID, posted_at | UI03 |
| Published Reels | Lifetime, stale/unavailable/zero, snapshot | BACKED/DEMO | P0 metric gate, P2 snapshot registry | UI14 |
| Published Reels | Imported asset attribution | DEFER | no title-based linkage | UI14 |
| Analytics | Lifetime/delta/Page metric availability | BACKED/DEMO | P2 analytics, metric snapshots; no unproven metric | UI14 |
| Calendar | Agenda/Week/Month; job detail | BACKED/DEMO | P3 GET /publish-jobs date filters | UI01/UI13 |
| Calendar | Drag-reschedule | DEFER | conditional PATCH not approved | UI13 |
| Activity/Queue | Status/Page/date/query, uncertain handling | EXTEND | P1/P3 GET /publish-jobs; reconcile endpoint | UI12 |
| Settings | Meta/scopes/worker readiness | BACKED/DEMO | P0/P1 health and authorization gate | UI01/UI14 |
| All screens | Loading, empty, 409/422/API errors | DEMO | production 401/403/409/422/429 with accessible UX | UI03/UI11 |
| All screens | Responsive, keyboard focus, drawer Escape | BACKED/DEMO | browser-only; no backend contract | UI15/UI16 |

**Important:** UI demo uses synthetic IDs such as `a2,p2`; production must translate selected asset→immutable variant UUID and Page UUID before POST; do not pass these demo IDs to API. The 100k sizes are synthetic design fixtures, not measured performance.
