# CleanSlate 1.0 beta 7: untouched reference copy

This folder is a byte-for-byte copy of CleanSlate 1.0 beta 7 (GitHub release `1.0-beta7`, the
latest as of 2026-11-14), downloaded from https://github.com/ck2plus/CleanSlate. CK2 does not
load it, because the game only reads `common/`, `events/` and so on at the mod root.

**Do not edit anything in here.** The migration (`../CLEANSLATE_PLAN.md`) builds LI's files from
these, and keeping this copy pristine means a future CleanSlate release can be diffed against it to
see what changed upstream.

- Included: `common`, `decisions`, `dlc_metadata`, `events`, `gfx`, `interface`, `localisation`,
  `map`, `music`, `tutorial`, plus CleanSlate's `master_changelog.txt`, `CleanSlate.mod` and
  `README.md`.
- Left out: `history`, because LI's own history replaces CleanSlate's in phase 1, and CleanSlate's
  `.gitattributes`, because it re-encodes text files and would clash with how this repo stores
  Windows-1252 files.
- Files are Windows-1252 with CRLF line endings, as released.
