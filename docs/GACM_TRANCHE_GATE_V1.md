# GACM Tranche Gate v1

The MA gate observes changed paths from Git rather than trusting a declared file list. It rejects unsafe, forbidden, outside-allowlist, symlink and submodule changes and checks the frozen tranche specification from the base revision.

The gate returns `PASS`, `FAIL` or `HOLD`/`UNOBSERVABLE` when later controls cannot establish evidence. Segment-aware patterns use `*` for one path segment and `**` for any depth.
