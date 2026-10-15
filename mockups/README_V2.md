# Facebook Reels Studio UI v2 — Large-Scale Operations

- **[Interactive standalone HTML](facebook-reels-studio-v2.html)** — open after downloading; no build or API server required.
- **[UI ↔ Backend contract audit](UI_V2_BACKEND_CONTRACT_AUDIT.md)** — screen/API/phase mapping, unsupported behavior, required spec patches and release gates.
- **[Canonical specification](../docs/FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md)**
- **[P0–P3 implementation plan](../docs/IMPLEMENTATION_PLAN_P0_P3.md)**

The UI v2 design is a **prototype only**: 50 Pages, 10,000 video assets, 100,000 Reels, 100,000 jobs are synthetic fixture objects, generated in the browser for illustration. This is not a performance test and not representative of production data loading.

## Key changes from v1
1. Asset grid/list, bounded paginated views, multi-select, usage-history contract warning.
2. Reels-first paginated data management table, Page and origin filters, last-snapshot semantics.
3. Composer split into Quick Publish and Batch Publish; per-target review matrix, immutable explicit target concept and API preflight.
4. Agenda-first calendar, monthly/weekly density summaries; unsafe reschedule controls removed.
5. Action-center dashboard and safe job details; UNCERTAIN reconciliation is not blind retry.
6. Every action that is only a specification contract opens a clearly labeled mock drawer and performs no real write.

## Hard boundaries
P0 Meta API feasibility is NOT completed; no live OAuth, video publishing, Reels discovery or analytics is implemented. Do not merge mockup as proof of provider support. Do not add backend features without updating contracts first.

This branch is for design review. Do not treat it as frontend implementation or P0 approval.
