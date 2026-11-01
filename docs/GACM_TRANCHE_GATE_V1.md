# GACM Tranche Gate v1

The MA gate observes changed paths from Git rather than trusting a declared file list. It rejects unsafe, forbidden, outside-allowlist, symlink and submodule changes and checks the frozen tranche specification from the base revision.

The gate returns `PASS`, `FAIL` or `HOLD`/`UNOBSERVABLE` when later controls cannot establish evidence. Segment-aware patterns use `*` for one path segment and `**` for any depth.

## Amendment 2026-11-01 -- later-tranche selection

The CI workflow derives the tranche identifier from the single `GACM-Tranche:` trailer carried by the candidate commits. It does not hardcode a bootstrap tranche. Missing or mixed trailers are rejected or classified as `NOT_A_TRANCHE` by the gate, and a candidate trailer must still match its loaded tranche specification.
