#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/delivery-gate.sh [options]

Run the common Styio delivery floor by composing repository hygiene, the docs
gate, external audit, and checkpoint health into one entrypoint.

Options:
  --mode <checkpoint|push>  Delivery mode (default: checkpoint)
  --base <ref>              Base ref for team-docs-gate branch checks
  --range <rev-range>       Explicit revision range for repo-hygiene push mode
  --skip-health             Skip checkpoint-health (docs/process-only deliveries)
  --skip-audit              Skip external styio-audit gate
  --audit-bin <path>        Explicit styio-audit executable
  --with-asan               Include the ASan/UBSan leg in checkpoint-health
  --with-fuzz               Include the fuzz-smoke leg in checkpoint-health
  --build-dir <dir>         Forwarded to checkpoint-health
  --asan-build-dir <dir>    Forwarded to checkpoint-health; also enables ASan
  --fuzz-build-dir <dir>    Forwarded to checkpoint-health; also enables fuzz
  -h, --help                Show this help
USAGE
}

log() {
  echo "[delivery-gate] $*"
}

run_cmd() {
  log "$*"
  "$@"
}

default_upstream_base() {
  git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || true
}

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="checkpoint"
BASE_REF=""
REV_RANGE=""
RUN_HEALTH=1
RUN_AUDIT=1
RUN_ASAN=0
RUN_FUZZ=0
AUDIT_BIN="${STYIO_AUDIT_BIN:-}"
BUILD_DIR=""
ASAN_BUILD_DIR=""
FUZZ_BUILD_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --base)
      BASE_REF="$2"
      shift 2
      ;;
    --range)
      REV_RANGE="$2"
      shift 2
      ;;
    --skip-health)
      RUN_HEALTH=0
      shift
      ;;
    --skip-audit)
      RUN_AUDIT=0
      shift
      ;;
    --audit-bin)
      AUDIT_BIN="$2"
      shift 2
      ;;
    --with-asan)
      RUN_ASAN=1
      shift
      ;;
    --with-fuzz)
      RUN_FUZZ=1
      shift
      ;;
    --build-dir)
      BUILD_DIR="$2"
      shift 2
      ;;
    --asan-build-dir)
      ASAN_BUILD_DIR="$2"
      RUN_ASAN=1
      shift 2
      ;;
    --fuzz-build-dir)
      FUZZ_BUILD_DIR="$2"
      RUN_FUZZ=1
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$MODE" in
  checkpoint|push)
    ;;
  *)
    echo "Unsupported mode: $MODE" >&2
    usage >&2
    exit 2
    ;;
esac

REPO_CMD=(python3 scripts/repo-hygiene-gate.py)
DOCS_GATE_CMD=(./scripts/docs-gate.sh)
HEALTH_CMD=(./scripts/checkpoint-health.sh)

if [[ "$MODE" == "checkpoint" ]]; then
  REPO_CMD+=(--mode staged)
  DOCS_GATE_CMD+=(--mode staged)
else
  REPO_CMD+=(--mode push)
  if [[ -n "$REV_RANGE" ]]; then
    REPO_CMD+=(--range "$REV_RANGE")
  fi

  if [[ -z "$BASE_REF" ]]; then
    BASE_REF="$(default_upstream_base)"
  fi

  if [[ -z "$BASE_REF" ]]; then
    echo "push mode requires --base <ref> or a configured upstream branch for team-docs-gate" >&2
    exit 2
  fi

  DOCS_GATE_CMD+=(--mode push --base "$BASE_REF")
fi

if [[ -n "$BUILD_DIR" ]]; then
  HEALTH_CMD+=(--build-dir "$BUILD_DIR")
fi
if [[ -n "$ASAN_BUILD_DIR" ]]; then
  HEALTH_CMD+=(--asan-build-dir "$ASAN_BUILD_DIR")
fi
if [[ -n "$FUZZ_BUILD_DIR" ]]; then
  HEALTH_CMD+=(--fuzz-build-dir "$FUZZ_BUILD_DIR")
fi
if [[ "$RUN_ASAN" -eq 0 ]]; then
  HEALTH_CMD+=(--no-asan)
fi
if [[ "$RUN_FUZZ" -eq 0 ]]; then
  HEALTH_CMD+=(--no-fuzz)
fi

log "mode: ${MODE}"
run_cmd "${REPO_CMD[@]}"
run_cmd "${DOCS_GATE_CMD[@]}"

if [[ "$RUN_AUDIT" -eq 1 ]]; then
  if [[ -z "$AUDIT_BIN" ]]; then
    if [[ -x "$ROOT/../styio-audit/bin/styio-audit" ]]; then
      AUDIT_BIN="$ROOT/../styio-audit/bin/styio-audit"
    elif [[ -x "/home/unka/styio-audit/bin/styio-audit" ]]; then
      AUDIT_BIN="/home/unka/styio-audit/bin/styio-audit"
    elif command -v styio-audit >/dev/null 2>&1; then
      AUDIT_BIN="$(command -v styio-audit)"
    fi
  fi
  if [[ -z "$AUDIT_BIN" || ! -x "$AUDIT_BIN" ]]; then
    echo "styio-audit executable not found; set STYIO_AUDIT_BIN or pass --audit-bin" >&2
    exit 2
  fi
  AUDIT_ROOT="$(cd "$(dirname "$AUDIT_BIN")/.." && pwd)"
  if git -C "$AUDIT_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    log "styio-audit commit: $(git -C "$AUDIT_ROOT" rev-parse HEAD)"
  fi
  run_cmd "$AUDIT_BIN" gate --repo "$ROOT" --project styio
else
  log "styio-audit skipped"
fi

if [[ "$RUN_HEALTH" -eq 1 ]]; then
  run_cmd "${HEALTH_CMD[@]}"
else
  log "checkpoint-health skipped"
fi

log "all checks passed"
