# P0 setup — operator-owned local environment

Requires Python 3.12+, 1–2 owned test Pages, an authorized Meta developer app, an HTTPS callback URL, and a real test MP4. This code is a feasibility probe, **not production publishing**. Use only own Pages/media.

1. Install: `python -m pip install -e '.[dev]'`.
2. Supply environment variables from `.env.example` using a local secret store. Never commit `.env`. In particular use `META_GRAPH_VERSION=v26.0`, `META_APP_ID`, `META_APP_SECRET`, `META_REDIRECT_URI`, `META_USER_TOKEN`, and `META_PAGE_TOKEN`.
3. Run `python scripts/meta_probe.py config-check`.
4. Run `python scripts/meta_probe.py auth-url` on the operator's trusted machine. Complete Meta login on a browser; run `python scripts/meta_probe.py oauth-exchange` and enter returned callback URL at hidden prompt. Current bootstrap **does not store or print issued tokens**; provide a separately obtained short-lived token through an encrypted local secret manager. OAuth exchange needs operational extension before the login can be considered operator-ready.
5. Run read probes: `python scripts/meta_probe.py inspect-token`, `python scripts/meta_probe.py list-pages`, `python scripts/meta_probe.py page-health --page-id 123`, `python scripts/meta_probe.py list-reels --page-id 123`, `python scripts/meta_probe.py inspect-reel --video-id 123`, `python scripts/meta_probe.py probe-insights --video-id 123 --object-type POST`.
6. Test intent without posting: `python scripts/meta_probe.py publish-reel --page-id 123 --video-file test.mp4 --title 'P0 test' --caption 'Operator authorized P0 test' --dry-run`. This is a **configuration preview**, NOT a validation of the input file or provider.
7. Controlled production write requires `RUN_META_PUBLISH_TESTS=1`, explicit Page, file, title/caption and two terminal confirmations. **Do not enable until upload/status field requirements are verified and any remaining code deficiencies addressed.**

No ordinary unit test makes a real network call. `python -m pytest -q -m 'not live_meta'` only executes mocks. Live read tests require `RUN_META_READ_TESTS=1` and `python -m pytest -q -m live_meta`.

