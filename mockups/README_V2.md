# Facebook Reels Studio · UI v2 (PR #3)
Open [interactive HTML](facebook-reels-studio-v2.html) locally as a standalone design demo.

**Not implemented:** OAuth, Meta publishing, production API/DB, uploads, analytics synchronization. Synthetic design data only. 50 Pages / 10k assets / 100k Reels / 100k jobs are **scale labels and deterministic lazy fixture ranges**, not benchmark results or loaded record arrays.

Nine screens: Dashboard, Fanpages, Video Library (default List; Grid toggle; search/filter; cursor-demo and explicit ID selection), Publish Composer (Quick or explicit-assignment Batch; sample **20 assets/10 Pages/60 targets**; max 100 targets, per-target title/caption/local-time/UTC, full paginated Review, demo validation without backend), Calendar (read-only Agenda/Week/Month), Published Reels (origin provenance, latest lifetime metrics), Analytics (N/A/STALE/zero separated), Activity/Queue (UNCERTAIN reconcile only), Settings.

Pages/asset IDs in this demo are simulated `p2`/`a2`; production uses owned Page UUID and content variant UUID. The UI displays Asia/Ho_Chi_Minh and converts to UTC. It never makes real writes. Production requires server-side cursor pagination (25/50/100), caching and request cancellation, lazy previews, indexed filter/sort, and backend analytics aggregates.

See [backend audit](UI_V2_BACKEND_CONTRACT_AUDIT.md), [screen/contract matrix](../docs/ui/UI_V2_SCREEN_CONTRACT_MATRIX.md), [ADR](../docs/adr/ADR_UI_V2_API_EXTENSIONS.md), [API proposals](../docs/api/INTERNAL_API_CONTRACTS_V1_1.md), [test ledger](../docs/test/UI_V2_ACCEPTANCE_TESTS.md) and [freeze candidate](../docs/ui/UI_V2_FREEZE.md). Proposed contracts await review. No evidence of Playwright PASS or actual screenshots yet.
