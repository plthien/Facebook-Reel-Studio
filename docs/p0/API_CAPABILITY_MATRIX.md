# P0 API capability matrix — 2026-10-16

| Operation | Graph version | Candidate endpoint | Status | Evidence |
|---|---|---|---|---|
| OAuth state / code exchange | v26.0 | /oauth/access_token | NOT_TESTED | local code only |
| User token inspection | v26.0 | /debug_token | NOT_TESTED | local code only |
| Page discovery | v26.0 | /me/accounts | NOT_TESTED | no authorized Pages supplied |
| Page health | v26.0 | /{page-id} | NOT_TESTED | no authorized Pages supplied |
| Reel START | v26.0 | /{page-id}/video_reels | NOT_TESTED | no authorized Pages supplied |
| Binary upload | Meta-provided URL | rupload.facebook.com | NOT_TESTED | no live upload |
| Status | v26.0 | /{video-id} | NOT_TESTED | no live video |
| Reel FINISH | v26.0 | /{page-id}/video_reels | NOT_TESTED | no live publish |
| Reel verification/ID mapping | v26.0 | /{video-id} | NOT_TESTED | no live published Reel |
| Existing Reels | v26.0 | /{page-id}/video_reels | NOT_TESTED | no prior content checked |
| Reel views | v26.0 | /{post-id}/insights | NOT_TESTED | metric candidate unverified |
| Page media views | v26.0 | /{page-id}/insights | NOT_TESTED | metric candidate unverified |

Every live entry requires time, status, Meta code/subcode, trace ID where available, exact object type, sanitized response and reviewer approval. No live capability is presently SUPPORTED.

