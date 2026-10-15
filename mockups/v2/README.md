# Facebook Reels Studio — UI Mockup v2 (High-volume Operations)

A standalone, interactive, offline HTML mockup of the Facebook Reels Studio internal tool for 10–50 owned/managed Fanpages, built against the P0–P3 technical specification.

## Quick preview

- **Open:** [`facebook_reels_studio_ui_mockup_v2.html`](facebook_reels_studio_ui_mockup_v2.html) directly in Chrome or Edge. No npm, server, account or internet connection.
- **Edit:** `index.html`, `style.css`, `app.js`; run `python build.py` to rebuild the single-file version.
- **Screens:** Overview, Fanpages, Video Library, Bulk Publisher, Calendar/Agenda, Reels, Analytics, Activity, Settings (9 in total).
- **Simulator sizes:** 50 Pages, 12,480 assets, 78,400 Reels, 2,840 jobs. This is generated in the local browser only. The real backend must use indexed pagination and not ship fixtures to clients.

## Prototype interactions

- Library: list/grid view, search/filter/sort, current-page multi-select, cross-page selected asset IDs, media detail drawer and transfer selection to composer.
- Publisher: one-video quick mode, multiple-video batch mode, Page selection, round-robin/cross-product target mapping, staggered schedule, per-target caption/time, final review with local+UTC time. **No actual publish**.
- Reels: filter/sort, pagination, Reel detail with N/A and snapshot provenance. Imported Reels **are not** linked to a local asset.
- Calendar: agenda/week/month count views; job drawer.
- Activity: per-job status, safe reconciliation explanation; no blind retry button.
- Settings: explicit Meta P0 gate, alignment matrix.

## Backend parity requirements

Read both docs before implementing UI:

1. [`UI_V2_BACKEND_ALIGNMENT.md`](UI_V2_BACKEND_ALIGNMENT.md): 9-screen matrix from UI controls to endpoint + DB tables + phase, including gated functionality.
2. [`UI_V2_IMPLEMENTATION_ADDENDUM.md`](UI_V2_IMPLEMENTATION_ADDENDUM.md): required new FastAPI contracts, Postgres migration, v1 `UNIQUE(batch_id,page_id)` fix, capacity & test gates.

All sample counts and names are fictional and labeled “DỮ LIỆU MÔ PHỎNG”. No Meta OAuth, publishing, uploads, analytics sync or server API calls are performed. No real authorization credential is required or stored. Source spec remains authoritative unless reviewed addendum is approved.

## Prototype acceptance

- 9 screens render without JavaScript errors.
- Video library searches across 12,480 simulated assets; per-page selection survives navigation.
- Invalid media is blocked when making a publication matrix.
- Batch mode creates explicit target rows, each with Page/video/time/caption, max 100 per submit in the design.
- Review shows local and UTC schedule; modal/asset/reel/job drawers can open/close.
- Reels metric availability `N/A` never displays numeric zero.
- Imported Reel is not incorrectly associated with local asset.

**Status:** v2 design review only. Do **not** merge as functional implementation or claim P0 external Meta proof.