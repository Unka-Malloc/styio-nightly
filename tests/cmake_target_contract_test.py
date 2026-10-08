#!/usr/bin/env python3
"""Configure the actual src target modules and compare frozen target properties.

The golden file was captured from fd3b3e2 before the target-file split. LLVM and
Tree-sitter are fixed external inputs here; actual builds remain a separate gate.
"""
from __future__ import annotations

import argparse
import itertools
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/cmake/target_contract"
GOLDEN = FIXTURE / "baseline.json"


def capture(cmake, root, directory, nano, tree, size, pipeline, msvc, identity=()):
    cmd = [cmake, "-S", str(FIXTURE), "-B", str(directory),
           f"-DSTYIO_CONTRACT_SOURCE_ROOT={root}",
           f"-DSTYIO_BUILD_NANO={'ON' if nano else 'OFF'}",
           f"-DSTYIO_ENABLE_TREE_SITTER={'ON' if tree else 'OFF'}",
           f"-DSTYIO_NANO_OPTIMIZE_FOR_SIZE={'ON' if size else 'OFF'}",
           f"-DSTYIO_NANO_INCLUDE_PIPELINE_CHECK={'ON' if pipeline else 'OFF'}",
           f"-DSTYIO_CONTRACT_MSVC={'ON' if msvc else 'OFF'}"]
    cmd.extend(identity)
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode:
        raise RuntimeError(f"{' '.join(cmd)}\n{proc.stdout}\n{proc.stderr}")
    result = {}
    for line in (directory / "target-properties.txt").read_text().splitlines():
        target, prop, value = line.split("|", 2)
        for path, marker in ((directory, "<BINARY_DIR>"), (FIXTURE, "<FIXTURE_DIR>")):
            # CMake uses forward slashes even when Python runs on Windows.
            value = value.replace(path.as_posix(), marker).replace(str(path), marker)
        result.setdefault(target, {})[prop] = value.split(";") if value else []
    return result


def expected(baseline, nano, tree, size, pipeline, msvc):
    result = json.loads(json.dumps(baseline))
    if not nano:
        for name in ("styio_nano", "styio_nano_core", "styio-nano"):
            del result[name]
    if not tree:
        ide = result["styio_ide_core"]
        ide["COMPILE_DEFINITIONS"].remove("STYIO_HAS_TREE_SITTER")
        ide["INCLUDE_DIRECTORIES"] = ide["INCLUDE_DIRECTORIES"][:-2]
        for prop in ("LINK_LIBRARIES", "INTERFACE_LINK_LIBRARIES"):
            ide[prop] = ide[prop][:-2]
    if nano:
        if not pipeline:
            result["styio_nano_core"]["SOURCES"].remove("StyioTesting/PipelineCheck.cpp")
        for name in ("styio_nano", "styio_nano_core"):
            result[name]["COMPILE_OPTIONS"] = (["$<$<NOT:$<CONFIG:Debug>>:/O1>" if msvc else "-Os"]
                                                if size else [])
    if msvc:
        result["styio_observable_core"]["COMPILE_OPTIONS"] = ["$<$<COMPILE_LANGUAGE:CXX>:/utf-8>"]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cmake", default=shutil.which("cmake"))
    args = parser.parse_args()
    if not args.cmake:
        parser.error("CMake is required; this contract test is not a production build")
    baseline = json.loads(GOLDEN.read_text())
    count = 0
    with tempfile.TemporaryDirectory(prefix="styio-cmake-contract-") as temp:
        for settings in itertools.product((False, True), repeat=5):
            nano, tree, size, pipeline, msvc = settings
            # Size and pipeline inclusion cannot affect an absent nano target.
            if not nano and (not size or not pipeline):
                continue
            actual = capture(args.cmake, ROOT, Path(temp) / str(count), *settings)
            wanted = expected(baseline, *settings)
            if actual != wanted:
                differences = [(target, prop, wanted.get(target, {}).get(prop), actual.get(target, {}).get(prop))
                               for target in sorted(set(actual) | set(wanted))
                               for prop in sorted(set(actual.get(target, {})) | set(wanted.get(target, {})))
                               if wanted.get(target, {}).get(prop) != actual.get(target, {}).get(prop)]
                raise AssertionError(f"Target contract changed for {settings}:\n" +
                                     "\n".join(map(str, differences)))
            count += 1
        settings = (True, True, True, True, False)
        actual = capture(args.cmake, ROOT, Path(temp) / "custom", *settings,
                         identity=("-DSTYIO_BUILD_VERSION=0.2.0",
                                   "-DSTYIO_FULL_RELEASE_CHANNEL=local-validation"))
        wanted = expected(baseline, *settings)
        for target in ("styio", "styio_cli_contract_core", "styio_nano"):
            definitions = wanted[target]["COMPILE_DEFINITIONS"]
            definitions[definitions.index('STYIO_PROJECT_VERSION="0.0.1"')] = 'STYIO_PROJECT_VERSION="0.2.0"'
            if target != "styio_nano":
                definitions[definitions.index('STYIO_RELEASE_CHANNEL="nightly"')] = 'STYIO_RELEASE_CHANNEL="local-validation"'
        assert actual == wanted, "Custom build identity changed unrelated target properties"
        invalid = {
            "STYIO_BUILD_VERSION": ("", "0.2", "0.2.0-dev", "01.2.0", "65536.0.0", "99999999999999999999.0.0", "0.2.0;injected", '0.2.0"'),
            "STYIO_FULL_RELEASE_CHANNEL": ("", "local validation", "local;injected", 'local"', "local\\path", "local/channel"),
        }
        for key, values in invalid.items():
            for index, value in enumerate(values):
                try:
                    capture(args.cmake, ROOT, Path(temp) / f"invalid-{key}-{index}",
                            *settings, identity=(f"-D{key}={value}",))
                except RuntimeError as error:
                    assert (f"{key} must" in str(error) or
                            f"{key} components must" in str(error)), str(error)
                else:
                    raise AssertionError(f"Invalid {key} accepted: {value!r}")
    print("Custom identity propagation, fixed Nano channel, and invalid identity rejection passed")
    print(f"CMake target contract passed: {count} configurations; source order, links, settings and nano alias unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
