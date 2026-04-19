#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL_VENV="${STYIO_NIGHTLY_TOOL_VENV:-$HOME/.local/venvs/styio-nightly-tools}"

usage() {
  cat <<EOF
Usage: $(basename "$0")

Install the Debian/Ubuntu packages required to build, test, and maintain
styio-nightly on a fresh Linux container or VM.

Optional environment:
  STYIO_NIGHTLY_TOOL_VENV   Python virtualenv used for lit
                            Default: $TOOL_VENV
EOF
}

log() {
  printf '[styio-nightly env] %s\n' "$*"
}

fail() {
  printf '[styio-nightly env] %s\n' "$*" >&2
  exit 1
}

as_root() {
  if [[ $EUID -eq 0 ]]; then
    "$@"
    return
  fi

  if command -v sudo >/dev/null 2>&1; then
    sudo "$@"
    return
  fi

  fail "sudo is required to install system packages"
}

ensure_debian_like() {
  if [[ ! -r /etc/os-release ]]; then
    fail "/etc/os-release is missing; only Debian/Ubuntu hosts are supported"
  fi

  # shellcheck disable=SC1091
  . /etc/os-release

  local family="${ID_LIKE:-}"
  if [[ "${ID:-}" != "debian" && "${ID:-}" != "ubuntu" && "${family}" != *debian* && "${family}" != *ubuntu* ]]; then
    fail "unsupported distribution: ${PRETTY_NAME:-unknown}. Expected Debian/Ubuntu."
  fi
}

install_system_packages() {
  local packages=(
    build-essential
    ca-certificates
    clang-18
    cmake
    curl
    git
    libcurl4-openssl-dev
    libedit-dev
    libffi-dev
    libicu-dev
    libssl-dev
    libxml2-dev
    libzstd-dev
    lld-18
    llvm-18-dev
    llvm-18-tools
    ninja-build
    nodejs
    npm
    pkg-config
    python3
    python3-pip
    python3-venv
    rsync
    unzip
    wget
    zip
  )

  log "installing system packages"
  as_root apt-get update
  as_root env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${packages[@]}"
}

install_lit() {
  log "installing lit into $TOOL_VENV"
  python3 -m venv "$TOOL_VENV"
  "$TOOL_VENV/bin/python" -m pip install --upgrade pip
  "$TOOL_VENV/bin/python" -m pip install "lit==18.1.8"
}

print_summary() {
  cat <<EOF

styio-nightly bootstrap complete.

Suggested shell exports:
  export CC=/usr/bin/clang-18
  export CXX=/usr/bin/clang++-18
  export LLVM_DIR=/usr/lib/llvm-18/lib/cmake/llvm
  export PATH="$TOOL_VENV/bin:\$PATH"

Typical next steps:
  cmake -S "$ROOT" -B "$ROOT/build"
  cmake --build "$ROOT/build" -j"$(nproc)"
EOF
}

main() {
  if [[ "${1:-}" == "--help" ]]; then
    usage
    exit 0
  fi

  ensure_debian_like
  install_system_packages
  install_lit
  print_summary
}

main "$@"
