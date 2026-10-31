# GACM Foundation Progression and Acceptance Synchronization Gate v1

Gate ID: `GACM-FOUNDATION-PROGRESSION-AND-ACCEPTANCE-SYNCHRONIZATION-GATE`

This gate is mandatory with the whole-machine integrity and instruction/authority drift gates. It enforces one Foundation, one authoritative application candidate, one governance acceptance, and one frozen SHA pair.

The gate requires:

- one exact `AUTHORITATIVE` application candidate;
- at most one unaccepted authoritative candidate beyond the previous frozen pair;
- qualification PASS bound to that exact SHA and still current;
- post-qualification mutation, supersession, or candidate mismatch to invalidate acceptance;
- governance acceptance bound to the exact application SHA, not only a branch name;
- application and governance local-to-remote currentness;
- a previous accepted frozen pair before work begins;
- the next Foundation to remain unauthorized until the current pair is accepted and frozen.

Unknown, missing, stale, contradictory, superseded, or ambiguous identity is fail-closed. Temporary development commits are not authority until one exact candidate is declared and qualified.

