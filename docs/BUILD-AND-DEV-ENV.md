# Styio Build And Dev Environment

**Purpose:** Provide the repository-level entry point for bootstrapping a fresh machine, configuring the compiler build, and finding the next subsystem-specific docs.

**Last updated:** 2026-04-19

## Who This Is For

1. Contributors bringing up `styio-nightly` on a fresh Debian/Ubuntu VM or container.
2. Contributors who need the common compiler build, test, and docs-audit commands.
3. IDE/LSP contributors who need the repo-level prerequisites before following `docs/external/for-ide/`.

## Fresh Machine Bootstrap

On a fresh Debian/Ubuntu host, start from the repository root:

```bash
./scripts/bootstrap-dev-env.sh
```

That script installs the common native toolchain used by this repository, including `clang-18`, `lld-18`, `llvm-18-dev`, `cmake`, `ninja`, `python3`, the official Node.js `v24.15.0` LTS binary line, and a local `lit` venv for test tooling.

## Standardized Baseline

`styio-nightly` and `styio-spio` share the same standardized native baseline:

1. Development host standard: Debian `13` (`trixie`).
2. Compiler toolchain standard: LLVM / Clang / LLD `18.1.x` via the `clang-18` package line.
3. CMake / CTest standard: `3.31.6`.
4. Validation Python standard: `3.13.5`.
5. Node.js standard for grammar maintenance: `v24.15.0` LTS.
6. Repository compatibility floor: CMake `3.20+` and C++20.
7. CI mirror: GitHub Actions on `ubuntu-24.04`, plus Python `3.13.5` and `cmake==3.31.6` installed before validation steps.

## Required Toolchains

1. LLVM `18.1.x` discoverable by `find_package(LLVM ...)`; `18.1.0` remains the compatibility floor accepted by CMake discovery.
2. A C++20 compiler and CMake / CTest `3.31.6` for the standardized local and CI toolchain.
3. Python `3.13.5` for docs and lifecycle scripts in the standardized validation pipeline.
4. Node.js `v24.15.0` LTS when regenerating the Tree-sitter grammar.
5. Optional ICU development headers when building with `-DSTYIO_USE_ICU=ON`.

## Typical Build And Test Commands

Configure:

```bash
cmake -S . -B build \
  -DSTYIO_ENABLE_TREE_SITTER=ON \
  -DSTYIO_USE_ICU=OFF
```

Build:

```bash
cmake --build build -j4
```

Stable full-compiler source-build helper:

```bash
./scripts/source-build-minimal.sh
```

Run milestone and pipeline tests:

```bash
ctest --test-dir build -L milestone
ctest --test-dir build -L styio_pipeline
ctest --test-dir build -L security
```

Run repo docs validation:

```bash
./scripts/docs-gate.sh
./scripts/delivery-gate.sh --mode checkpoint --skip-health
```

Run the full checkpoint delivery floor:

```bash
./scripts/delivery-gate.sh --mode checkpoint
```

## Subsystem-Specific Follow-Ups

1. IDE and LSP targets: [external/for-ide/BUILD.md](./external/for-ide/BUILD.md)
2. IDE integration doc index: [external/for-ide/INDEX.md](./external/for-ide/INDEX.md)
3. Team-owned workflow and delivery rules: [teams/INDEX.md](./teams/INDEX.md)
4. Repository workflow assets: [assets/INDEX.md](./assets/INDEX.md)

## Related Docs

1. Repository docs entry: [README.md](./README.md)
2. Documentation policy: [specs/DOCUMENTATION-POLICY.md](./specs/DOCUMENTATION-POLICY.md)
3. Repository ecosystem map: [specs/REPOSITORY-MAP.md](./specs/REPOSITORY-MAP.md)
4. Agent and contributor rules: [specs/AGENT-SPEC.md](./specs/AGENT-SPEC.md)
