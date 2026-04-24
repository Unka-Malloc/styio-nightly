# Dependency Usage Boundary

**Purpose:** Record dependency authorization boundaries for `styio` / `styio-nightly`.

**Last updated:** 2026-04-24

`styio` / `styio-nightly` is an Apache-2.0 compiler/runtime source project. Its current build, test, docs, and fixture dependency boundary is:

- CMake and CTest drive native compiler/runtime build and test workflows.
- LLVM integration, Tree-sitter grammar tooling, GitHub Actions, Python standard library tooling, and Bash scripts are external build, parser, CI, and automation surfaces.
- Rust, JavaScript, TypeScript, Zig, Nix, and Bazel surfaces are fixture/tooling surfaces unless separately promoted with explicit manifest evidence.
- Repository workflows may invoke system tools such as `git`, `cmake`, shell utilities, and configured compiler/runtime tools through explicit process boundaries.

Dependency policy:

- No dependency may require commercial authorization, paid licensing, subscription access, membership access, trial-only terms, proprietary-use approval, or private registry access.
- Any future dependency must be listed here with its license evidence, source boundary, and usage boundary before it can pass audit.
- Fixture-only dependencies must stay fixture-scoped and must not become runtime requirements without this file being updated.
- Generated reports and gate summaries must summarize dependency and license evidence without copying target repository source.
