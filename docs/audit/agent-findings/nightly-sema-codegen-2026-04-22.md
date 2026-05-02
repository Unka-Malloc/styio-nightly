# Nightly Sema / Codegen Fail-Closed Findings 2026-04-22

**Purpose:** Record sema and codegen fail-closed findings from the parallel external audit pass.

**Last updated:** 2026-04-22

**Scope:** `src/StyioSema`, `src/StyioLowering`, `src/StyioCodeGen`, and focused regressions under `tests/security/`.

**Status:** Partially remediated during this pass.

## Closed During This Pass

- Unknown user function calls now fail closed in sema/lowering instead of reaching codegen as `SGCall` and becoming integer `0`.
- User function arity mismatches now fail during typecheck/lowering, and `SGCall` codegen has a defensive exact-arity guard before LLVM call emission.
- Runtime list-operation SGCall arity mismatches now throw `StyioTypeError` instead of returning integer `0`.
- LLVM verifier failures in `StyioToLLVM::execute()` now throw instead of printing and returning.
- Regression coverage added:
  - `StyioSecurityNightlySemantics.RejectsUnknownFunctionDuringTypecheck`
  - `StyioSecurityNightlySemantics.RejectsUserFunctionArityMismatchDuringTypecheck`
  - `StyioSecurityNightlyCodegen.UnknownSgCallFailsClosed`
  - `StyioSecurityNightlyCodegen.SgCallArityMismatchFailsBeforeLlvmEmission`

## Remaining Risks

- Many unsupported AST lowering handlers still synthesize `SGConstInt(0)` and need a dedicated negative matrix.
- Function body type inference remains shallow; defensive lowering/codegen guards now catch missed call issues, but deeper sema coverage is still needed.
- Some non-call codegen fallbacks still return zero/null placeholders and should be converted incrementally with targeted tests.
