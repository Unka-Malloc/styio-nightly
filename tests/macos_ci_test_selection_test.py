#!/usr/bin/env python3
"""Prove the macOS CTest label union preserves coverage without repeated selection.

The configure-only fixture exercises real CTest selection, not compiler behavior.
It deliberately includes unique future members and substring-matching labels.
"""
from __future__ import annotations

import argparse
import itertools
import json
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = ("styio_pipeline", "algorithm_equivalence", "resource_topology")
UNION = "(" + "|".join(LABELS) + ")"


def inventory(ctest: str, build: Path, label: str) -> list[dict]:
    result = subprocess.run(
        [ctest, "--test-dir", str(build), "--show-only=json-v1", "-L", label],
        check=True, text=True, capture_output=True,
    )
    # Backtrace indexes are local to each filtered JSON backtrace graph.
    return [{key: value for key, value in test.items() if key != "backtrace"}
            for test in json.loads(result.stdout)["tests"]]


def check_workflow() -> None:
    workflow = (ROOT / ".github/workflows/styio-ci-gate.yml").read_text()
    macos = workflow.split("\n  macos-ci-gate:\n", 1)[1].split("\n  test-smoke:\n", 1)[0]
    commands = [shlex.split(line.strip()) for line in macos.splitlines()
                if line.strip().startswith("ctest ")]
    selected = [cmd for cmd in commands if "-L" in cmd and
                any(label in cmd[cmd.index("-L") + 1] for label in LABELS)]
    assert selected == [["ctest", "--test-dir", "build/macos-ci", "-L", UNION,
                         "--output-on-failure", "--no-tests=error"]], selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cmake", default=shutil.which("cmake"))
    parser.add_argument("--ctest", default=shutil.which("ctest"))
    args = parser.parse_args()
    if not args.cmake or not args.ctest:
        parser.error("CMake and CTest are required")
    check_workflow()
    with tempfile.TemporaryDirectory(prefix="styio-macos-selection-") as directory:
        source = Path(directory)
        build = source / "build"
        fixture = ["cmake_minimum_required(VERSION 3.20)",
                   "project(selection NONE)", "enable_testing()"]
        expected = set()
        cases = []
        for bits in itertools.product((False, True), repeat=len(LABELS)):
            if any(bits):
                cases.append(("member_" + "".join(str(int(bit)) for bit in bits),
                              ";".join(label for label, bit in zip(LABELS, bits) if bit)))
        cases += [("substring_" + label, "prefix_" + label + "_suffix") for label in LABELS]
        cases.append(("unrelated", "docs"))
        for name, labels in cases:
            fixture += [f'add_test(NAME {name} COMMAND "${{CMAKE_COMMAND}}" -E true)',
                        f'set_tests_properties({name} PROPERTIES LABELS "{labels}")']
            if name != "unrelated":
                expected.add(name)
        (source / "CMakeLists.txt").write_text("\n".join(fixture) + "\n")
        subprocess.run([args.cmake, "-S", str(source), "-B", str(build)],
                       check=True, text=True, capture_output=True)
        original = {}
        original_count = 0
        for label in LABELS:
            for test in inventory(args.ctest, build, label):
                original_count += 1
                original[test["name"]] = test
        combined = inventory(args.ctest, build, UNION)
        names = [test["name"] for test in combined]
        assert set(original) == expected, "Fixture no longer covers all original selectors"
        assert len(names) == len(set(names)), "Union selected a test more than once"
        assert {test["name"]: test for test in combined} == original, "Union changed membership or test settings"
        assert original_count > len(names), "Fixture did not exercise overlap"
        print(f"macOS CTest selection passed: {original_count} overlapping selections -> "
              f"{len(names)} unique tests; identical membership/settings, including unique and substring labels")


if __name__ == "__main__":
    main()
