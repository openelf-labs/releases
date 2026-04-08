# OpenELF Releases

Public release infrastructure for OpenELF.

- GitHub Releases hosts immutable versioned assets.
- `update.openelf.ai` is the mutable machine endpoint for `latest.json`, `latest-beta.json`, and `install.sh`.
- The actual product source stays in the private [`openelf-labs/openelf`](https://github.com/openelf-labs/openelf) repository.

## Architecture

```text
private source repo               public release repo
openelf-labs/openelf             openelf-labs/releases
---------------------            ----------------------
tag push v0.2.0  ----------->    GitHub Actions
exact commit SHA                -> checkout private source
source-owned scripts            -> build + sign + release upload
                                 -> deploy Pages aliases

users / updater
---------------
update.openelf.ai/latest.json        mutable stable alias
update.openelf.ai/latest-beta.json   mutable beta alias
update.openelf.ai/install.sh         mutable installer
github.com/.../releases/download     immutable version assets
```

## Required Setup

Configure this repository before the first release:

1. Enable GitHub Pages and set the custom domain to `update.openelf.ai`.
2. Create a `release` environment with required reviewers.
3. Add one of:
   - `SOURCE_REPO_APP_ID` + `SOURCE_REPO_APP_PRIVATE_KEY`
   - `SOURCE_REPO_TOKEN`
4. Add signing secrets as needed:
   - `UPDATE_SIGNING_KEY`
   - `MACOS_SIGNING_KEY`
   - `MACOS_SIGNING_KEY_PASSWORD`
   - `APPLE_IDENTITY`
   - `APPLE_APP_PASSWORD`
5. Add environment variables if macOS notarization is enabled:
   - `APPLE_ID`
   - `APPLE_TEAM_ID`
6. In the private source repo, add `RELEASE_REPO_DISPATCH_TOKEN` so tag pushes can trigger this repo via `repository_dispatch`.

## Flow

1. A tag like `v0.2.0` is pushed in the private source repo.
2. The private repo sends `source_repo + source_tag + source_sha` to this public repo via `repository_dispatch`.
3. This repo checks out the exact private commit, builds artifacts, signs them, and publishes a GitHub Release.
4. The workflow then resolves the highest stable tag and highest prerelease tag, downloads each release `manifest.json`, and publishes fresh Pages aliases.

## Notes

- The first public release should be stable. `latest.json` is intentionally not aliased to a beta build.
- Git tag names keep the leading `v`; manifest versions and archive names do not.
- `update.openelf.ai` is the contract boundary. Clients should not couple themselves to GitHub's mutable release URLs.
