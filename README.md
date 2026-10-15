# Facebook Reels Studio

Internal web application for operating **10–50 Facebook Fanpages** owned/managed by the operator: Reels publishing, scheduling, job recovery and per-Reel analytics.

> **Current status:** specification and implementation plan only. No production integration, OAuth approval, live Meta API feasibility proof or application implementation is claimed.

## Project documents

- [Technical specification v1](docs/FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md) — product scope, architecture, Meta integration probes, database DDL, API contracts, UI, security and operational requirements. Includes the canonical P0–P3 implementation plan.
- [Implementation plan P0–P3](docs/IMPLEMENTATION_PLAN_P0_P3.md) — phase-by-phase task list, acceptance gates, test matrix, operational runbook and Codex handoff.

## Delivery sequence

1. **P0 — Meta API feasibility:** prove real Page access, Reels publishing, ID mapping and per-Reel views on owned Pages. Do not substitute mocked evidence.
2. **P1 — Core management:** authentication, Page management, media library, single-Page publisher and resilient job queue.
3. **P2 — Analytics:** discover Reels, collect verified metrics, maintain snapshots and build dashboards.
4. **P3 — Bulk publishing:** schedule and manage independent jobs across 10–50 Pages, verify recovery and capacity.

**Stop/go:** P1–P3 are blocked until P0 live tests pass or the product scope is explicitly revised. Never store Meta credentials in Git, logs or client-side code.

**Scope:** Internal use only. No TikTok, Instagram, Ads Manager, content monetization reporting, browser-based account automation or competitor scraping during P0–P3.
