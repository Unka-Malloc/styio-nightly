# Docs / Ecosystem Runbook

**Purpose:** Provide the daily-work entrypoint for maintainers of repository documentation, generated indexes, archive/rollup lifecycle, templates, and external Styio ecosystem handoff material.

**Last updated:** 2026-04-24

## Mission

Own documentation structure and cross-repository clarity. This team protects SSOT discipline, generated indexes, archive provenance, external repository boundaries, handoff notes, reusable templates, and repository-level entry documents such as `README.md` and `docs/BUILD-AND-DEV-ENV.md`. It does not redefine language semantics, accepted tests, or package-manager ownership.

## Owned Surface

Primary paths:

1. `docs/`
2. `docs/design/syntax/`
3. `docs/assets/`
4. `docs/rollups/`
5. `docs/archive/`
6. `workflows/`
7. `templates/`
8. `scripts/docs-index.py`
9. `scripts/docs-audit.py`
10. `scripts/docs-scaffold.py`
11. `scripts/docs_config.py`
12. `scripts/docs-lifecycle.py`
13. `scripts/team-docs-gate.py`
14. `scripts/delivery-gate.sh`

Key SSOTs:

1. [../specs/DOCUMENTATION-POLICY.md](../specs/DOCUMENTATION-POLICY.md)
2. [../specs/REPOSITORY-MAP.md](../specs/REPOSITORY-MAP.md)
3. [../../workflows/DOCS-MAINTENANCE-WORKFLOW.md](../../workflows/DOCS-MAINTENANCE-WORKFLOW.md)

## Daily Workflow

1. Check whether the content already has an owning SSOT before adding a new file.
2. Prefer linking and short summaries over copying rules across documents.
3. Add `Purpose` and `Last updated` metadata to every active docs file.
4. Use [../assets/templates/TEAM-RUNBOOK-TEMPLATE.md](../assets/templates/TEAM-RUNBOOK-TEMPLATE.md) for team runbook structure changes.
5. Regenerate `INDEX.md` files after collection changes.
6. Use `python3 scripts/docs-scaffold.py ...` for new docs files or new docs collection directories so metadata, collection registration, and generated indexes are created together.
7. Keep repository-level bootstrap/build entrypoints under `docs/BUILD-AND-DEV-ENV.md`, and push subsystem-only details back down into the owning docs collection instead of overloading `README.md` or `docs/external/for-ide/`.
8. Run the team runbook maintenance gate before delivery so source/test/docs folder changes cannot land without the mapped runbook update or required runbook format.
9. Use archive lifecycle tooling for raw history/review compression rather than manually moving provenance.
10. Use the unified delivery gate for docs/process deliveries so hygiene, runbook maintenance, and docs audit stay coupled.
11. Keep the ecosystem CLI contract mirror and cross-repo doc gate aligned whenever `styio-spio` or `styio-view` handoff docs change.
12. When a compiler-side machine contract grows, update the owner SSOT and both consumer handoff docs in the same checkpoint instead of leaving one side on preview wording.
13. Keep repository-level build bootstrap docs aligned with the standardized shared baseline: Debian 13, LLVM 18.1.x, CMake/CTest 3.31.6, Python 3.13.5, and Node.js v24.15.0 LTS where Node-backed tooling exists; when CI mirrors differ by host OS, document the mirror explicitly instead of drifting the toolchain version text.
14. Keep `docs/external/for-spio/` aligned with the current `binary` vs `build` split: `--machine-info=json` remains the binary handshake, while `--source-build-info=json` owns the official source-layout contract for `spio build`.
15. When a compiler/runtime/contract adjustment spans multiple checkpoints, add or update an explicit `docs/plans/` implementation plan instead of leaving the execution order only in handoff or runbook prose.
16. When the compiler-side source-build helper changes, keep `scripts/source-build-minimal.sh`, `docs/BUILD-AND-DEV-ENV.md`, and the `--source-build-info=json` handoff wording aligned in the same checkpoint.
17. When a plan remains in `docs/plans/` after one stage closes, make the file say whether it is still `Active`, `Repo-local baseline completed`, or ready for archive; do not force readers to infer status from scattered stage tables.
18. Keep repository entry docs honest about maturity: if repo-local baselines are complete but ecosystem closure is still open, say that explicitly instead of leaving stale `early stage` wording in top-level entrypoints.
19. When an evidence-backed closure retires a gap, move it out of the open gap table, add the smallest closed-evidence note, update the matching checkpoint tree entry, and regenerate affected generated indexes.
20. Keep [../specs/POST-COMMIT-CI-CHECKS.md](../specs/POST-COMMIT-CI-CHECKS.md) aligned with actual GitHub Actions monitoring practice whenever commit, push, or CI handoff rules change.
21. Keep GitHub Actions sibling checkouts for `styio-spio` and `styio-view` pinned to the same branch ref as `styio-nightly` when a workflow runs cross-repository gates.
22. Keep compact syntax references under `docs/design/syntax/` short and defer semantic detail to the owning design SSOT.
23. When syntax tokens change, update the compact syntax page, EBNF, and symbol reference together before regenerating indexes.
24. When standard-stream symbolic definitions change, keep `docs/design/syntax/RESOURCE_IDENTIFIERS.md`, `docs/design/syntax/CONTINUATION_TRANSFER.md`, EBNF, symbol reference, and the language design aligned on canonical, expanded, compatibility, and parser-implementation status.
25. Keep root `workflows/`, `workflows/skills/`, `workflows/workflows.toml`, generated workflow indexes, and `docs/assets/workflow/` mirrors aligned whenever reusable workflows or repo-local skills are added.
26. Keep repo-local skills concise: workflow docs own sequencing, while `skill.toml` owns reusable execution discipline and references.
27. Workflow and skill machine-readable definitions must use TOML (`*.toml`, `skill.toml`, and `agents/openai.toml`); Markdown remains explanatory only.
28. When test coverage changes require `docs/assets/workflow/TEST-CATALOG.md`, keep the catalog as an evidence index and point behavior ownership back to the implementation or test-quality runbook instead of embedding new language semantics there.
29. When language SSOT docs change token-count semantics, update the design page, EBNF, symbol reference, and test catalog in one checkpoint so docs readers do not see conflicting operator depth rules.
30. When syntax is retired, document the cutover in active SSOT docs and add a dated revision note to affected archived milestone pages. Archive pages may preserve provenance, but active catalogs and tests must not keep retired examples as runnable acceptance cases.
31. When the eBioRing Styio repository set changes, refresh the inventory with `gh repo list eBioRing --limit 200`, then update root `README.md`, [../specs/REPOSITORY-MAP.md](../specs/REPOSITORY-MAP.md), and any active ecosystem plan that names the old repository set.

## Change Classes

1. Small: typo, link fix, or local README wording. Run docs audit.
2. Medium: new docs collection, generated index config, SSOT table change, external handoff doc, commit/CI workflow spec, sibling checkout ref policy, or CLI/runtime contract matrix update. Update policy and run generated-index checks.
3. High: repository boundary, archive lifecycle, docs audit rule, or ecosystem ownership change. Use checkpoint workflow and coordinate affected implementation teams.

## Required Gates

Documentation gates:

```bash
python3 scripts/docs-index.py --write
python3 scripts/docs-scaffold.py --help
python3 scripts/team-docs-gate.py
python3 scripts/docs-lifecycle.py validate
python3 scripts/ecosystem-cli-doc-gate.py
python3 scripts/docs-audit.py
```

Unified docs/process delivery floor:

```bash
./scripts/delivery-gate.sh --mode checkpoint --skip-health
```

Optional inventory commands:

```bash
python3 scripts/docs-audit.py --manifest valid --format tree
python3 scripts/docs-audit.py --manifest invalid --format list
python3 scripts/docs-lifecycle.py candidates --family all --format tree
```

Checkpoint-grade:

```bash
./scripts/checkpoint-health.sh --no-asan --no-fuzz
```

## Cross-Team Dependencies

1. Frontend, Sema / IR, Codegen / Runtime, IDE / LSP, and CLI / Nano must review docs that describe their behavior.
2. Test Quality must review test catalog, workflow, and oracle documentation changes.
3. Perf / Stability must review benchmark, soak, and report lifecycle docs.
4. Coordination owner must review repository-boundary and external ecosystem handoff changes.

## Handoff / Recovery

Record unfinished docs/ecosystem work with:

1. Owning SSOT and files changed.
2. Generated indexes that still need refresh.
3. Link or metadata audit failures.
4. Team runbook gate failures, required runbook paths, and template/format violations.
5. External repository or handoff owner affected.
6. Archive/rollup lifecycle action still pending.
