# UI v2 ↔ Backend Audit — final G3 review candidate
**Status: G3_READY_FOR_REVIEW; proposed contracts PENDING APPROVAL; zero real production API calls.**
Existing PR [#3](https://github.com/plthien/Facebook-Reel-Studio/pull/3) (same branch). Test evidence [GitHub Actions #38720044131](https://github.com/plthien/Facebook-Reel-Studio/actions/runs/38720044131): 19/19 Chromium tests PASS, offline OpenAPI/schema check PASS, 23 screenshots.

| Former mismatch / hazard | UI disposition | Required backend contract and status |
|---|---|---|
| Library 105 selected silently loses 5 | **FIXED**: reject >100 transfer, retain all IDs and show alert | P3 max 100 explicit targets; EXTEND, pending |
| Invalid/past/too-soon schedule accepted | **FIXED**: strict calendar +07→UTC + configurable 10-min demo lead | Server authoritative 422 schedule revalidation; EXTEND |
| Quick chips p2/p3 but targets p4/p3 | **FIXED**: Page chips canonical, Review Page/Video disabled, per-target overrides persist | P3 exact target identity; BACKED / EXTEND |
| Exact duplicate only warned | **FIXED**: Page+variant+UTC+trimmed overrides block duplicates | `DUPLICATE_INTENT` 422; EXTEND |
| Validated preview reused after edit | **FIXED**: fingerprints reset, current successful validation required | 409 idempotency + 422 full revalidation; EXTEND |
| Old `UNIQUE(batch_id,page_id)` | **FIXED IN PROPOSED SPEC**: per-target uniqueness | DDL pending review/migration, not implemented |
| 40-row partial Review | **FIXED**: 25/25/10 for 60; validation covers all | Full `targets[]` preview and 100 cap; EXTEND |
| Browser eagerly instantiates 100k fixtures | **FIXED IN DEMO**: bounded lazy records | Real backend keyset cursor and indexed filters mandatory |
| Imported Reel matched arbitrary asset | **FIXED**: imported asset unlinked | Verified lineage only; BACKED/EXTEND |
| Unavailable metrics displayed as 0 | **FIXED**: N/A vs measured zero, stale and mock badges | P0 capability evidence + snapshot provenance; BACKED/DEMO |
| UNCERTAIN blind retry and rescheduling | **DISABLED**: reconcile only, calendar read-only | Safe reconcile BACKED; PATCH reschedule DEFER |
| Filtered all-result selection | **DEFERRED**: explicit loaded IDs only | Backend scope token not in P1–P3 |

Full per-control traceability: [UI V2 screen/API matrix](../docs/ui/UI_V2_SCREEN_CONTRACT_MATRIX.md). Proposed [OpenAPI v1.1](../docs/api/openapi-v1.1.yaml), [internal API contracts](../docs/api/INTERNAL_API_CONTRACTS_V1_1.md), [database amendments](../docs/database/SCHEMA_AMENDMENTS_V1_1.md), [ADR](../docs/adr/ADR_UI_V2_API_EXTENSIONS.md), [acceptance tests](../docs/test/UI_V2_ACCEPTANCE_TESTS.md), [freeze candidate](../docs/ui/UI_V2_FREEZE.md).

Hard boundary: Meta P0 live provider capability is **BLOCKED_EXTERNAL**, not verified. The prototype never creates a real Page, upload, Reel, job, or metric. The 50 Pages/10k assets/100k Reels/100k jobs are synthetic scale design fixtures, not performance proof.
