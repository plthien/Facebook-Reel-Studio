# UI V2 Backend Contract Audit · repaired candidate
PR #3 branch contains nine UI screens and documentation. **All API/DB adjustments are proposals awaiting approval.** NO production implementation and NO P0 Meta live confirmation.

| Priority | Previous defect | Current design disposition | Backend requirement |
|---|---|---|---|
| BLOCKER | `UNIQUE(batch_id,page_id)` rejects 2 videos for 1 Page | Proposed DDL replaced with per-target index/ID uniques | Alembic migration, transaction tests |
| BLOCKER | N×M generated hidden jobs | Batch adds **one explicit target** at a time; 20/10/60 test fixture | Exact targets[]; max 100 |
| BLOCKER | Review first 40 only | Full target list, paginated in 25 rows; validation all targets | Preview returns diagnostics for every target |
| BLOCKER | Per-target schedule not persisted | Stable target ID + caption, title and localTime in state | UUID variant, Page, ISO UTC, idempotency |
| HIGH | Unreal all-results checkbox | Only explicitly loaded IDs selectable | All-results token DEFER |
| HIGH | Full 10k/100k browser allocations and filtering | Lazy deterministic fixture generation + bounded rows | Production cursor API and backend sort/search |
| HIGH | Imported Reels visually linked to random assets | Imported entries show **no asset attribution** | Verified lineage only |
| HIGH | Metrics zero vs unavailable/stale | Separate fixture status and clear P0 warning | Availability/provenance catalog |
| HIGH | Calendar ambiguous reschedule | Read-only demo, no drag reschedule | PATCH deferred |
| MEDIUM | Page groups lack BE | Group remains labeled proposed | Optional fb_pages.group_label |
| MEDIUM | Job uncertain retry | Reconciliation information only | Safe GET detail/reconcile; no blind retry |

**Traceability**: [per-screen matrix](../docs/ui/UI_V2_SCREEN_CONTRACT_MATRIX.md); [API contract proposals](../docs/api/INTERNAL_API_CONTRACTS_V1_1.md); [ADR](../docs/adr/ADR_UI_V2_API_EXTENSIONS.md); [acceptance ledger](../docs/test/UI_V2_ACCEPTANCE_TESTS.md); [freeze candidate](../docs/ui/UI_V2_FREEZE.md).

Known issues: browser tests and responsive screenshots NOT_RUN; live Meta capability BLOCKED_EXTERNAL; no true server cursor, no production React implementation, no backend request or actual publish. Mock search is deterministic fixture scan until one page of hits is collected, NOT production indexing. No formal freeze approval.
