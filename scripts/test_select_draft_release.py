#!/usr/bin/env python3

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parent
SCRIPT = ROOT / "select_draft_release.py"


class SelectDraftReleaseTests(unittest.TestCase):
    def run_script(self, payload, *args):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = pathlib.Path(tmpdir) / "releases.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--releases-json", str(path), *args],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)

    def test_selects_oldest_draft_with_state_asset(self):
        payload = [
            {
                "draft": True,
                "tag_name": "v0.2.2",
                "created_at": "2026-04-08T12:00:00Z",
                "assets": [{"id": 2, "name": "release-state.json"}],
            },
            {
                "draft": True,
                "tag_name": "v0.2.1",
                "created_at": "2026-04-08T11:00:00Z",
                "assets": [{"id": 1, "name": "release-state.json"}],
            },
        ]
        selected = self.run_script(payload)
        self.assertTrue(selected["found"])
        self.assertEqual(selected["tag_name"], "v0.2.1")
        self.assertEqual(selected["state_asset_id"], 1)

    def test_filters_by_requested_tag(self):
        payload = [
            {
                "draft": True,
                "tag_name": "v0.2.1",
                "created_at": "2026-04-08T11:00:00Z",
                "assets": [{"id": 1, "name": "release-state.json"}],
            },
            {
                "draft": True,
                "tag_name": "v0.2.2",
                "created_at": "2026-04-08T12:00:00Z",
                "assets": [{"id": 2, "name": "release-state.json"}],
            },
        ]
        selected = self.run_script(payload, "--release-tag", "v0.2.2")
        self.assertTrue(selected["found"])
        self.assertEqual(selected["tag_name"], "v0.2.2")

    def test_returns_not_found_without_state_asset(self):
        payload = [
            {
                "draft": True,
                "tag_name": "v0.2.1",
                "created_at": "2026-04-08T11:00:00Z",
                "assets": [{"id": 1, "name": "checksums.txt"}],
            }
        ]
        selected = self.run_script(payload)
        self.assertFalse(selected["found"])


if __name__ == "__main__":
    unittest.main()
