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
        if args.command in {"export-evidence", "evaluate-gate"}:
            doc = {"P0_CODE_READY": "UNVERIFIED", "P0_LIVE_GO": "P0_BLOCKED_EXTERNAL",
                   "reason": "No authorized live evidence supplied"}
            print(json.dumps(doc))
            return 0
        if args.command == "publish-reel" and (args.dry_run or os.getenv("RUN_META_PUBLISH_TESTS") != "1"):
            print(json.dumps({"mode": "DRY_RUN", "page_id": args.page_id,
                             "video_file": args.video_file, "graph_version": s.graph_version,
                             "published": False}))
            return 0
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
                print(json.dumps(adapter.list_reels(pid, s.page_token)))
            elif args.command in {"inspect-reel", "verify-reel", "reconcile-reel"} and args.video_id:
                if args.command == "inspect-reel":
                    result = adapter.inspect_reel(args.video_id, s.page_token)
                    print(json.dumps({"id": result.get("id"), "status": result.get("status")}))
                else:
                    if not pid:
                        raise ValueError("--page-id required")
                    print(json.dumps(adapter.verify_published_reel(pid, args.video_id, s.page_token).safe()))
            elif args.command == "probe-insights" and args.video_id:
                print(json.dumps(adapter.probe_insights(args.video_id, s.page_token,
                     object_type=args.object_type, metric=args.metric).safe()))
            elif args.command == "publish-reel" and pid and args.video_file and args.title and args.caption:
                if not Path(args.video_file).is_file():
                    raise ValueError("Video file does not exist")
                page = adapter.page_health(pid, s.page_token)
                print(f"Target: {page.name} (Page {pid}); file: {Path(args.video_file).name}")
                if input("Type page ID to authorize upload: ").strip() != pid:
                    raise ValueError("Page confirmation failed")
                session = adapter.start_reel_upload(pid, s.page_token, args.route)
                print(json.dumps(session.safe()))
                adapter.upload_local_reel(session, s.page_token, Path(args.video_file))
                status = adapter.get_upload_status(session.video_id, s.page_token)
                processing = status.get("status")
                phase = processing.get("processing_phase", {}) if isinstance(processing, dict) else {}
                ready = isinstance(phase, dict) and str(phase.get("status", "")).lower() == "complete"
                print(json.dumps({"video_id": session.video_id, "processing_ready": ready}))
                if not ready:
                    print("Upload not proven ready. Stop without FINISH; reconcile manually.", file=sys.stderr)
                    return 4
                if input("Type PUBLISH to submit irreversible FINISH request: ").strip() != "PUBLISH":
                    return 3
                adapter.finish_reel_publish(pid, session.video_id, s.page_token,
                                            args.title, args.caption, args.route)
                result = adapter.verify_published_reel(pid, session.video_id, s.page_token)
                print(json.dumps(result.safe()))
                return 0 if result.publication_verified else 4
            else:
                raise ValueError("Required --page-id, --video-id, --video-file, --title or --caption missing")
            return 0
        finally:
            with_client.close()
    except RemoteUncertain as exc:
        print(json.dumps({"state": "UNCERTAIN", "phase": exc.phase, "video_id": exc.video_id}), file=sys.stderr)
        return 4
    except MetaFailure as exc:
        print(json.dumps({"error": exc.category, "phase": exc.phase, "code": exc.code}), file=sys.stderr)
        return 3
    except (ValueError, OSError) as exc:
        print("P0 validation failed: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
