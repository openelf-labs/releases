#!/usr/bin/env python3

import argparse
import json
import pathlib
from datetime import datetime, timezone


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select a GitHub release that carries release-state.json."
    )
    parser.add_argument("--releases-json", required=True, help="Path to GitHub releases API JSON")
    parser.add_argument("--release-tag", default="", help="Exact release tag to select")
    parser.add_argument(
        "--state-asset-name",
        default="release-state.json",
        help="State asset filename to look for",
    )
    return parser.parse_args()


def parse_created_at(value: str) -> datetime:
    if not value:
        return datetime.max.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    args = parse_args()
    releases = json.loads(pathlib.Path(args.releases_json).read_text(encoding="utf-8"))

    candidates = []
    for release in releases:
        tag_name = str(release.get("tag_name") or "")
        if args.release_tag and tag_name != args.release_tag:
            continue

        state_asset = None
        for asset in release.get("assets") or []:
            if str(asset.get("name") or "") == args.state_asset_name:
                state_asset = asset
                break
        if state_asset is None:
            continue

        candidates.append(
            {
                "found": True,
                "release_id": release.get("id"),
                "tag_name": tag_name,
                "is_draft": bool(release.get("draft")),
                "created_at": release.get("created_at"),
                "state_asset_id": state_asset.get("id"),
                "state_asset_name": state_asset.get("name"),
            }
        )

    if not candidates:
        print(json.dumps({"found": False}))
        return 0

    candidates.sort(key=lambda item: parse_created_at(str(item.get("created_at") or "")))
    print(json.dumps(candidates[0], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
