#!/usr/bin/env python3

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parent
SCRIPT = ROOT / "discover_pending_source_release.py"


class DiscoverPendingSourceReleaseTests(unittest.TestCase):
    def run_script(self, source_tags, releases, *args):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = pathlib.Path(tmpdir)
            source_path = tmp / "source-tags.json"
            release_path = tmp / "releases.json"
            source_path.write_text(json.dumps(source_tags), encoding="utf-8")
            release_path.write_text(json.dumps(releases), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--source-tags-json",
                    str(source_path),
                    "--releases-json",
                    str(release_path),
                    *args,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)

    def test_selects_oldest_unreleased_semver(self):
        source_tags = [
            {"name": "v0.2.1", "commit": {"sha": "b" * 40}},
            {"name": "v0.2.0", "commit": {"sha": "a" * 40}},
            {"name": "v0.3.0-beta.1", "commit": {"sha": "c" * 40}},
        ]
        releases = [{"tag_name": "v0.2.0"}]
        selected = self.run_script(source_tags, releases)
        self.assertTrue(selected["found"])
        self.assertEqual(selected["source_tag"], "v0.2.1")
        self.assertEqual(selected["channel"], "stable")

    def test_skips_existing_draft_or_published_release_tags(self):
        source_tags = [
            {"name": "v0.2.1", "commit": {"sha": "b" * 40}},
            {"name": "v0.2.2", "commit": {"sha": "c" * 40}},
        ]
        releases = [
            {"tag_name": "v0.2.1", "draft": True},
            {"tag_name": "v0.1.9", "draft": False},
        ]
        selected = self.run_script(source_tags, releases)
        self.assertTrue(selected["found"])
        self.assertEqual(selected["source_tag"], "v0.2.2")

    def test_marks_prerelease_channel_as_beta(self):
        source_tags = [{"name": "v0.3.0-beta.2", "commit": {"sha": "d" * 40}}]
        releases = []
        selected = self.run_script(source_tags, releases)
        self.assertEqual(selected["channel"], "beta")
        self.assertEqual(selected["version"], "0.3.0-beta.2")

    def test_returns_not_found_when_everything_is_released(self):
        source_tags = [{"name": "v0.2.1", "commit": {"sha": "b" * 40}}]
        releases = [{"tag_name": "v0.2.1"}]
        selected = self.run_script(source_tags, releases)
        self.assertFalse(selected["found"])

    def test_honors_minimum_tag_cutoff(self):
        source_tags = [
            {"name": "v0.2.0", "commit": {"sha": "a" * 40}},
            {"name": "v0.2.1", "commit": {"sha": "b" * 40}},
        ]
        releases = []
        selected = self.run_script(source_tags, releases, "--minimum-tag", "v0.2.1")
        self.assertTrue(selected["found"])
        self.assertEqual(selected["source_tag"], "v0.2.1")


if __name__ == "__main__":
    unittest.main()
