# GACM measured autonomy levels v1

MA-3 adds a recommendation-only autonomy policy. The repository variable `GACM_AUTONOMY_LEVEL` is read by CI and defaults to level 0 when missing or invalid. No workflow changes the variable.

Risk is computed from every changed path. Unlisted paths, policy, workflow, schema, tranche, gate, metrics, governance and contract surfaces are high risk. Other `src/gacm/**` paths are medium; ordinary tests and non-governance notes are low. A declared tranche class lower than its computed class fails.

Level 0 requires Chris approval for every class. Level 1 allows low-risk pull requests with green required checks. Level 2 additionally allows medium-risk pull requests. High-risk pull requests always require Chris approval. Approval must be by `chriskulbaba2025`, be `APPROVED`, and target the current head SHA.

Reports recommend `HOLD`, `PROMOTE`, or `DEMOTE`; they never change the level. UNKNOWN escapes and discrepancies block promotion. Trivial runs of 20 or fewer changed lines, excluding `runs/`, do not count.
