# Facebook Reels Studio — Interactive UI Mockup v1

**Review status:** UI / workflow proposal; not implemented product.

## Preview
[Open the standalone mockup HTML](facebook-reels-studio-v1.html) (download and open in Chrome/Edge). No API server, accounts or build dependencies required; online fonts are optional.

### Navigation / planned phases

| Screen | Route | Target phase |
|---|---|---|
| Tổng quan | `/dashboard` | P2 |
| Fanpages | `/pages` | P1 |
| Video Library | `/library` | P1 |
| Đăng Reels | `/publish/new` | P1 single / P3 bulk |
| Lịch đăng | `/calendar` | P3 |
| Reels | `/reels` | P2 |
| Analytics | `/analytics` | P2 |
| Hoạt động | `/activity` | P1 / P3 |
| Cài đặt | `/settings` | P1 / P3 |

Interactions included: Page search/filter, video selection, Page selection, individual caption and schedule editing, publish review, calendar week/month switch, job details, metrics range, demo modal states and responsive sidebar.

## Product truthfulness rules
- Persistent `DỮ LIỆU MÔ PHỎNG` label; all shown Pages, numbers and Reels are fictional.
- No OAuth, upload, publishing, scheduling, analytics fetching or credentials are functional.
- API-dependent metrics are not promised. `N/A` is different from zero.
- `UNCERTAIN` jobs must be reconciled before retry.
- Source-of-truth and acceptance requirements: [canonical technical spec](../docs/FACEBOOK_REELS_STUDIO_TECHNICAL_SPEC_V1.md).

## Visual direction
Dark navy navigation `#111B2B`; soft off-white canvas `#F5F7FB`; indigo primary `#596CE9`; green/amber/red status semantics; 1440px desktop-first. Tables, cards, status labels and page-specific publishing controls optimized for 10–50 Pages.

**Review first**: visual hierarchy, terminology, per-Page publishing workflow, insights/provenance and accessibility. Do not treat this PR as P0 completion or production implementation.
