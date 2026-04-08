#!/usr/bin/env python3

import argparse
import json
import pathlib
import re


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select the next source tag that should be staged in the public release repo."
    )
    parser.add_argument("--source-tags-json", required=True, help="GitHub tags API payload")
    parser.add_argument("--releases-json", required=True, help="GitHub releases API payload")
    parser.add_argument(
        "--minimum-tag",
        default="",
        help="Ignore source tags older than this tag (inclusive lower bound)",
    )
    return parser.parse_args()


def semver_key(tag_name: str):
    tag = tag_name.lstrip("v")
    core, _, pre = tag.partition("-")
    major, minor, patch = (core.split(".") + ["0", "0", "0"])[:3]
    pre_parts = []
    if pre:
        for chunk in re.split(r"[.\-]", pre):
            if chunk.isdigit():
                pre_parts.append((0, int(chunk)))
            else:
                pre_parts.append((1, chunk))
    return (int(major), int(minor), int(patch), tuple(pre_parts))


def channel_for_tag(tag_name: str) -> str:
    lowered = tag_name.lower()
    if any(marker in lowered for marker in ("alpha", "beta", "rc")):
        return "beta"
    return "stable"


def main() -> int:
    args = parse_args()
    source_tags = json.loads(pathlib.Path(args.source_tags_json).read_text(encoding="utf-8"))
    releases = json.loads(pathlib.Path(args.releases_json).read_text(encoding="utf-8"))

    seen_release_tags = {
        str(release.get("tag_name") or "")
        for release in releases
        if str(release.get("tag_name") or "")
    }

    pending = []
    minimum_key = semver_key(args.minimum_tag) if args.minimum_tag else None
    for tag in source_tags:
        tag_name = str(tag.get("name") or "")
        source_sha = str((tag.get("commit") or {}).get("sha") or "")
        if not tag_name or not source_sha:
            continue
        if not tag_name.startswith("v"):
            continue
        if minimum_key is not None and semver_key(tag_name) < minimum_key:
            continue
        if tag_name in seen_release_tags:
            continue
        pending.append(
            {
                "found": True,
                "source_tag": tag_name,
                "source_sha": source_sha,
                "version": tag_name[1:],
                "channel": channel_for_tag(tag_name),
            }
        )

    if not pending:
        print(json.dumps({"found": False}))
        return 0

    pending.sort(key=lambda item: semver_key(item["source_tag"]))
    print(json.dumps(pending[0], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
