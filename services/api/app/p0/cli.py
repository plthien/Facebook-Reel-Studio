"""P0 CLI. Default is read-only. Explicit double opt-in for publication."""
from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
from pathlib import Path

from app.config import Settings
from app.integrations.meta.adapter import MetaAdapter
from app.integrations.meta.client import MetaClient, MetaFailure, RemoteUncertain, numeric_id
from app.p0.evidence import export_evidence, journal_event, redact
from app.p0.media import inspect_mp4
from app.p0.oauth import consume_callback, create_auth_url


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="meta-probe")
    p.add_argument("command", choices=["config-check", "auth-url", "oauth-exchange",
                   "inspect-token", "list-pages", "page-health", "list-reels",
                   "inspect-reel", "probe-insights", "publish-reel", "verify-reel",
                   "reconcile-reel", "export-evidence", "evaluate-gate"])
    p.add_argument("--page-id")
    p.add_argument("--video-id")
    p.add_argument("--video-file")
    p.add_argument("--title")
    p.add_argument("--caption")
    p.add_argument("--object-type", choices=["POST", "PAGE", "VIDEO"], default="POST")
    p.add_argument("--metric", default="post_media_view")
    p.add_argument("--route", choices=["page", "me"], default="page")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--evidence-dir", default="evidence/p0/local")
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        s = Settings.from_env()
        if args.command == "config-check":
            print(json.dumps({"graph_version": s.graph_version,
                  "missing": s.missing("app_id", "app_secret", "user_token", "redirect_uri"),
                  "publish_enabled": False}))
            return 0
        if args.command == "auth-url":
            print(create_auth_url(s))
            return 0
        if args.command == "oauth-exchange":
            url = getpass.getpass("Paste complete HTTPS callback URL (hidden): ")
            code = consume_callback(s, url)
            if s.missing("app_id", "app_secret", "redirect_uri"):
                raise ValueError("App ID, secret and redirect URI required")
            # Exchange server side using a secret-bearing POST, never put secret in URL.
            import httpx
            response = httpx.post("https://graph.facebook.com/" + s.graph_version + "/oauth/access_token",
                                  data={"client_id": s.app_id, "client_secret": s.app_secret,
                                        "redirect_uri": s.redirect_uri, "code": code},
                                  timeout=25, follow_redirects=False, trust_env=False)
            if response.status_code != 200:
                raise MetaFailure("BLOCKED_AUTH", "OAUTH")
            data = response.json()
            if not isinstance(data, dict) or not isinstance(data.get("access_token"), str):
                raise MetaFailure("MALFORMED_RESPONSE", "OAUTH")
            print("OAuth token issued. Store securely in META_USER_TOKEN; token is not displayed.")
            return 0
        if args.command == "export-evidence":
            print(json.dumps(export_evidence(Path(args.evidence_dir)), indent=2))
            return 0
        if args.command == "evaluate-gate":
            print(json.dumps({"P0_CODE_READY": "INCOMPLETE",
                              "P0_LIVE_GO": "P0_BLOCKED_EXTERNAL",
                              "reason": "Requires approved reviewer and actual authorized live evidence"}))
            return 0
        if args.command == "publish-reel" and (args.dry_run or os.getenv("RUN_META_PUBLISH_TESTS") != "1"):
            print(json.dumps({"mode": "DRY_RUN", "page_id": args.page_id,
                             "video_file": args.video_file, "graph_version": s.graph_version,
                             "published": False}))
            return 0
        current_page_id: str | None = None
        current_video_id: str | None = None
        with_client = MetaClient(s.graph_version)
        try:
            adapter = MetaAdapter(with_client)
            pid = numeric_id(args.page_id) if args.page_id else None
            if args.command == "inspect-token":
                if not s.app_id or not s.app_secret or not s.user_token:
                    raise ValueError("META_APP_ID, META_APP_SECRET and META_USER_TOKEN required")
                app_token = s.app_id + "|" + s.app_secret
                result = with_client.graph("GET", "/debug_token", app_token,
                                           params={"input_token": s.user_token})
                data = result.get("data", {})
                print(json.dumps({"is_valid": data.get("is_valid"),
                                  "scopes": data.get("scopes", []),
                                  "expires_at": data.get("expires_at")}))
            elif args.command == "list-pages":
                print(json.dumps([x.safe() for x in adapter.pages(s.user_token)]))
            elif args.command == "page-health" and pid:
                print(json.dumps(adapter.page_health(pid, s.page_token).safe()))
            elif args.command == "list-reels" and pid:
                print(json.dumps(redact(adapter.list_reels(pid, s.page_token))))
            elif args.command in {"inspect-reel", "verify-reel", "reconcile-reel"} and args.video_id:
                if args.command == "inspect-reel":
                    result = adapter.inspect_reel(args.video_id, s.page_token)
                    print(json.dumps(redact({"id": result.get("id"), "status": result.get("status")})))
                else:
                    if not pid:
                        raise ValueError("--page-id required")
                    print(json.dumps(adapter.verify_published_reel(pid, args.video_id, s.page_token).safe()))
            elif args.command == "probe-insights" and args.video_id:
                print(json.dumps(adapter.probe_insights(args.video_id, s.page_token,
                     object_type=args.object_type, metric=args.metric).safe()))
            elif args.command == "publish-reel" and pid and args.video_file and args.title and args.caption:
                media = inspect_mp4(Path(args.video_file))
                page = adapter.page_health(pid, s.page_token)
                current_page_id = pid
                print(json.dumps({"target_page": page.safe(), "file": Path(args.video_file).name,
                                  "media": media, "graph_version": s.graph_version}))
                if "P0" not in args.title.upper() and "TEST" not in args.title.upper():
                    raise ValueError("P0 test title must explicitly contain P0 or TEST")
                if input("Type page ID to authorize upload: ").strip() != pid:
                    raise ValueError("Page confirmation failed")
                import secrets
                test_id = secrets.token_hex(8)
                title = args.title + " [P0 " + test_id + "]"
                caption = args.caption + " [P0 " + test_id + "]"
                print(json.dumps({"test_id": test_id, "publish_title": title,
                                  "publish_caption": caption}))
                session = adapter.start_reel_upload(pid, s.page_token, args.route)
                current_video_id = session.video_id
                journal_event(Path(args.evidence_dir), phase="START", page_id=pid,
                              video_id=session.video_id, state="UPLOAD_STARTED",
                              extra={"graph_version": s.graph_version, "route": args.route, "test_id": test_id})
                print(json.dumps(session.safe()))
                adapter.upload_local_reel(session, s.page_token, Path(args.video_file))
                journal_event(Path(args.evidence_dir), phase="UPLOAD", page_id=pid,
                              video_id=session.video_id, state="PROCESSING")
                ready_evidence = adapter.wait_for_upload_ready(session.video_id, s.page_token)
                journal_event(Path(args.evidence_dir), phase="PROCESSING", page_id=pid,
                              video_id=session.video_id, state="READY_TO_FINISH", extra=ready_evidence)
                if input("Type PUBLISH to submit irreversible FINISH request: ").strip() != "PUBLISH":
                    return 3
                journal_event(Path(args.evidence_dir), phase="FINISH", page_id=pid,
                              video_id=session.video_id, state="FINISH_REQUESTED")
                adapter.finish_reel_publish(pid, session.video_id, s.page_token,
                                            title, caption, args.route)
                mapping = adapter.verify_published_reel(pid, session.video_id, s.page_token)
                journal_event(Path(args.evidence_dir), phase="VERIFY", page_id=pid,
                              video_id=session.video_id, state=mapping.state.value, extra=mapping.safe())
                print(json.dumps(mapping.safe()))
                return 0 if mapping.publication_verified else 4
            else:
                raise ValueError("Required --page-id, --video-id, --video-file, --title or --caption missing")
            return 0
        finally:
            with_client.close()
    except RemoteUncertain as exc:
        known_video_id = exc.video_id if exc.video_id else locals().get("current_video_id")
        journal_event(Path(args.evidence_dir), phase=exc.phase,
                      page_id=locals().get("current_page_id"),
                      video_id=known_video_id, state="UNCERTAIN")
        print(json.dumps({"state": "UNCERTAIN", "phase": exc.phase, "video_id": known_video_id}), file=sys.stderr)
        return 4
    except MetaFailure as exc:
        print(json.dumps({"error": exc.category, "phase": exc.phase, "code": exc.code}), file=sys.stderr)
        return 3
    except (ValueError, OSError) as exc:
        print("P0 validation failed: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
