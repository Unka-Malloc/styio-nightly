# Nightly Test Framework Findings 2026-04-29

**Purpose:** Preserve the test framework audit findings that were first recorded in the ignored local defect queue, so they remain visible as durable tracked work without committing `docs/audit/defects/` records.

**Last updated:** 2026-05-02

**Scope:** `styio-nightly` test framework, CTest registration, fuzz/performance gates, and CI gate coverage.

**Status:** Open durable findings migrated from `docs/audit/defects/TEST-FRAMEWORK-GAPS-2026-04-29.md`.

## Findings

| ID | Severity | Area | Defect | Evidence | Required closure |
| --- | --- | --- | --- | --- | --- |
| NIGHTLY-TEST-001 | High | Golden coverage | Missing stdout goldens are treated as configure-time warnings and skipped tests instead of a blocking defect. A newly added `t*.styio` sample can be present without any asserted output. | `tests/CMakeLists.txt` emits `message(WARNING "Missing golden: ...")` and continues when `tests/data/expected/*.out` is absent. | Add a gate that fails when any tracked sample lacks a golden, or explicitly list intentional non-golden samples in a reviewed allowlist. |
| NIGHTLY-TEST-002 | Medium | CI completeness | The checkpoint/CI path emphasizes focused labels and selected binaries, but does not make full `ctest` execution the primary blocking contract. This makes it easier for newly registered, unlabeled, or mis-labeled tests to avoid regular gate coverage. | `.github/workflows/ci.yml` delegates to `scripts/checkpoint-health.sh`; that script runs targeted labels, selected parser/security/soak checks, and selected sanitizer diagnostics rather than an unconditional full CTest pass. | Add a blocking full-suite CTest step to PR/push CI, or add a machine-checked inventory rule proving every registered test is covered by an enforced gate label. |
| NIGHTLY-TEST-003 | Medium | Fuzz coverage | Fuzz smoke coverage is conditional on a pre-existing fuzz build directory, while deep fuzzing is isolated to the nightly workflow. PRs can therefore merge parser/lexer changes without any blocking fuzz execution if the fuzz build is not available in the gate path. | `scripts/checkpoint-health.sh` only runs fuzz smoke when the fuzz build exists; `.github/workflows/nightly-fuzz.yml` runs scheduled fuzz targets separately. | Build and run short fuzz smoke targets in PR CI for parser/lexer-sensitive changes, and keep nightly fuzz as extended coverage. |
| NIGHTLY-TEST-004 | Medium | Performance regressions | Performance/report checks can be skipped or report-only, so regular gate output can stay green while budget coverage is incomplete. | `benchmark/perf-route.sh` supports skipped report sections such as configure reuse and deep-soak skips; existing reports already include skipped sections. | Define a minimal blocking performance budget for release-relevant routes and record any intentional skip in a tracked exception file with owner and expiry. |
| NIGHTLY-TEST-005 | Low | Temporary files | Some milestone tests use shared `/tmp` paths and shell-managed scratch files. This is fragile under parallel or repeated local runs. | Milestone shell tests in `tests/CMakeLists.txt` create temporary script/input/output paths under `/tmp`. | Move shell-based milestone tests to per-test temporary directories or CTest-provided working directories. |

## Closure Expectations

Before marking these findings closed:

1. Add a blocking missing-golden detector or an explicit reviewed allowlist.
2. Make the regular CI contract prove that every registered CTest test is covered by an enforced gate.
3. Add a short fuzz smoke step to the PR/push path for parser and lexer surfaces.
4. Define which performance checks are blocking and which remain observational.
5. Re-run the repository's official test and documentation gates, then link the passing run or local command transcript in the closing change.

## Migration Note

The original local defect queue file was intentionally not retained under `docs/audit/defects/`, because that directory is ignored and blocked by repository hygiene. This tracked shard keeps the finding content available for ownership and closure while keeping the PR history free of transient defect records.
