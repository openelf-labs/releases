# OpenELF Releases

Public downloads for OpenELF.

- Download released builds from [GitHub Releases](https://github.com/openelf-labs/releases/releases).
- Install from the stable channel:

```bash
curl -fsSL https://update.openelf.ai/install.sh | sh
```

- Machine-readable update endpoints:
  - `https://update.openelf.ai/latest.json`
  - `https://update.openelf.ai/latest-beta.json`

## Channels

- `stable`: recommended for most users
- `beta`: preview builds that may change faster

## Prelaunch Bypass

`Finalize Release` supports a prelaunch-only notarization bypass for internal trial releases.

- Default behavior stays strict: macOS app assets publish only after Apple notarization succeeds.
- When `bypass_notarization=true` is passed on manual finalize, or repo variable `PRELAUNCH_NOTARIZATION_BYPASS=true` is set, the workflow may publish the release without notarized macOS app assets.
- In that bypass mode, signed CLI archives, checksums, and the manifest are still published; the macOS installer falls back to the CLI tarball until notarized app assets are added later.
