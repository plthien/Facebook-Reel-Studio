# Controlled P0 Meta validation

**Safety gate:** Do not run write tests until the operator confirms both Page IDs, app roles/scopes, correct API route, owned MP4, and test content. Never publish to all Pages or auto-delete test Reels.

Stage A — explicitly enabled read-only probes: inspect auth scopes/tasks, Page health, previous Page Reels, candidate metrics. Verify at least two Pages with server responses. Store timestamps, HTTP status, Graph version, failure code, operation, object identity and safe evidence file path. No mocks count.

Stage B — first Page: separate owner consent; create START, inspect video ID and upload host, upload the real MP4, poll processing state, finish only after observed positive readiness, verify Page ownership and remote published state. Inspect mapping and Reel-specific views. Never retry FINISH automatically if it times out.

Stage C — second Page: separate owner consent and redo controlled publish and verification. Confirm distinct Page IDs and Video IDs.

Stage D — collect nonsecret evidence and fill capability matrix, record reviewer signature and decision. If any identity/status field is ambiguous, mark UNCERTAIN and reconcile read-only. If token/consent/test pages unavailable, record BLOCKED_EXTERNAL, not PASS.

**Current operational blocker:** The provided CLI has not yet demonstrated a live Meta upload contract. Do not treat its returned finish acknowledgement as publication proof or use it unattended. Live tests have not been executed.

