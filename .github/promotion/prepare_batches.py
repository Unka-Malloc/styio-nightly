#!/usr/bin/env python3
"""Prepare only dated downstream promotion branches; never push upstream."""
from pathlib import Path
import json, os, re, runpy, subprocess, sys


def git(*args, check=True):
    return subprocess.run(['git', *args], text=True, capture_output=True, check=check)


def run(*args):
    subprocess.run(args, check=True)


def edit(path, replacements):
    p = Path(path)
    text = p.read_text()
    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f'{path}: missing {old!r}')
        text = text.replace(old, new)
    p.write_text(text)


def commit(message):
    git('add', '-A')
    git('diff', '--cached', '--check')
    git('commit', '-m', message)


def refresh_stats():
    sys.path.insert(0, str(Path('scripts').resolve()))
    measure = runpy.run_path('scripts/docs-audit.py')['measure_markdown']
    p = Path('docs/teams/DOC-STATS.md')
    lines = p.read_text().splitlines()
    total_words = total_chars = 0
    for i, line in enumerate(lines):
        match = re.search(r'\]\(\./([^/]+\.md)\)', line)
        if not line.startswith('|') or not match:
            continue
        name = match.group(1)
        chars, words = measure(Path('docs/teams') / name)
        parts = line.split('|')
        parts[-3] = f' {words:,} '
        parts[-2] = f' {chars:,} '
        lines[i] = '|'.join(parts)
        if name.endswith('-RUNBOOK.md'):
            total_words += words
            total_chars += chars
    for i, line in enumerate(lines):
        if line.startswith('| **Total**'):
            lines[i] = f'| **Total** | Team runbooks only | **{total_words:,}** | **{total_chars:,}** |'
    p.write_text('\n'.join(lines).replace('**Last updated:** 2026-07-02', '**Last updated:** 2026-09-28') + '\n')


def checks():
    refresh_stats()
    run(sys.executable, 'scripts/docs-index.py', '--write')
    for args in [('scripts/workflow-scheduler.py', 'check'), ('tests/workflow_scheduler_test.py',), ('scripts/docs-audit.py',), ('scripts/syntax-convergence-gate.py',), ('scripts/team-docs-gate.py',)]:
        run(sys.executable, *args)


BASE = '9d211fcd2dd799183d3e30a32dbc05c27acafb00'
PREFIX = 'upstream/2026-09-28-'
git('config', 'user.name', 'Unka-Malloc')
git('config', 'user.email', '33834801+Unka-Malloc@users.noreply.github.com')
git('checkout', '-b', PREFIX + '00-ci-foundation', BASE)
workflow = '.github/workflows/styio-ci-gate.yml'
edit(workflow, [
    ('repository: styio-org/styio-pafio\n          ref: ${{ steps.lane.outputs.ecosystem_ref }}', 'repository: Unka-Malloc/pafio-nightly\n          # Freeze the existing v1 docs contract during staged compiler promotion.\n          ref: d68d1649741630bee5775b2d6650797148835ed3'),
    ('repository: styio-org/styio-view\n          ref: ${{ steps.lane.outputs.ecosystem_ref }}', 'repository: Unka-Malloc/vityo-nightly\n          ref: 6adfa4c2b2d11ba01a74f321cfebb6323ebac6ea'),
    ('^m1_t01_int_arith$|^m2_t01_simple_func$', '^scalar_expressions_t01_int_arith$|^functions_t01_simple_func$'),
    ('-L milestone', '-L language_feature'),
    ('--output-on-failure', '--output-on-failure --no-tests=error'),
])
with Path(workflow).open('a') as f:
    f.write('''
  required-ci-gate:
    name: styio-ci-gate
    if: ${{ always() }}
    needs: [styio-ci-gate, test-smoke, test-golden-standard]
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    permissions: {}
    steps:
      - name: Require every existing CI lane to succeed
        shell: bash
        env:
          LINUX_RESULT: ${{ needs.styio-ci-gate.result }}
          SMOKE_RESULT: ${{ needs.test-smoke.result }}
          GOLDEN_RESULT: ${{ needs.test-golden-standard.result }}
        run: |
          set -euo pipefail
          for name in LINUX_RESULT SMOKE_RESULT GOLDEN_RESULT; do
            result="${!name:-missing}"
            printf '%s=%s\\n' "$name" "$result"
            if [[ "$result" != success ]]; then
              exit 1
            fi
          done
''')
edit('.github/workflows/styio-audit.yml', [('--project Styio', '--project styio')])
# Preserve every convergence record, replacing only retired paths.
feature_dirs = {'m1': 'scalar_expressions', 'm2': 'functions', 'm3': 'control_flow', 'm4': 'wave_dispatch', 'm5': 'file_resources', 'm6': 'state_resources', 'm7': 'stream_processing', 'm8': 'final_bindings', 'm9': 'stdio_output', 'm10': 'stdio_input', 'm11': 'native_interop', 'm12': 'task_resources'}
p = Path('docs/design/syntax/SYNTAX-CONVERGENCE-MATRIX.json')
text = p.read_text()
for old, new in feature_dirs.items():
    text = text.replace('tests/milestones/' + old + '/', 'tests/features/' + new + '/')
p.write_text(text)
edit('scripts/syntax-convergence-gate.py', [('parts[0:2] == ("tests", "milestones")', 'parts[0:2] in (("tests", "milestones"), ("tests", "features"))')])
edit('docs/specs/GOLDEN-STANDARD-TEST-SUITE.md', [
    ('smallest milestone and fuzz smoke checks', 'smallest language-feature and fuzz smoke checks'),
    ('`ctest --test-dir build/golden -L milestone`', '`ctest --test-dir build/golden -L language_feature --no-tests=error`'),
    ('against `tests/milestones/**/expected`', 'against `tests/features/**/expected`'),
])
p = Path('docs/teams/TEST-QUALITY-RUNBOOK.md')
p.write_text(p.read_text() + '''
### Staged Upstream CI Baseline (2026-09-28)

The dated upstream contribution sequence retains the existing Linux, smoke,
and golden-standard jobs. The required `styio-ci-gate` check aggregates all
three results and fails on failed, cancelled, skipped, missing, or unexpected
results. CTest selections must find real tests (`--no-tests=error`). Smoke and
language-feature goldens use the existing `tests/features/` layout, and the
syntax convergence checker validates their expected-output files as well.

The existing cross-repository v1 documentation check is retained. Its Pafio
and Vityo inputs use immutable historical revisions from their accessible
repositories so unrelated sibling changes do not alter a compiler promotion.
These pins establish the historical v1 baseline, not current sibling-version
compatibility; any pin update must rerun that same check.
''')
p = Path('docs/teams/DOCS-ECOSYSTEM-RUNBOOK.md')
p.write_text(p.read_text() + '\n### Staged upstream validation (2026-09-28)\n\nKeep convergence fixtures and golden-standard commands aligned with tests/features. Preserve every convergence record and require its output oracle. Historical sibling pins document the existing v1 contract; they do not certify the latest sibling versions.\n')
checks()
commit('fix(ci): restore executable upstream validation contracts')
results = [{'branch': PREFIX + '00-ci-foundation', 'sha': git('rev-parse', 'HEAD').stdout.strip(), 'tree': git('rev-parse', 'HEAD^{tree}').stdout.strip()}]
# Batch 1 contains the service layer and its original integration fix only.
git('checkout', '-b', PREFIX + '01-services')
conflicts = [
    {'docs/assets/workflow/TEAM-RUNBOOK-MAINTENANCE-GATE.md', 'docs/external/INDEX.md', 'docs/external/for-pafio/Styio-Nano-Pafio-Coordination.md', 'docs/teams/CLI-NANO-RUNBOOK.md', 'docs/teams/DOC-STATS.md', 'docs/teams/DOCS-ECOSYSTEM-RUNBOOK.md', 'docs/teams/INDEX.md', 'docs/teams/TEST-QUALITY-RUNBOOK.md', 'workflows/TEAM-RUNBOOK-MAINTENANCE-GATE.md'},
    {'docs/teams/DOC-STATS.md', 'docs/teams/DOCS-ECOSYSTEM-RUNBOOK.md', 'scripts/ecosystem-cli-doc-gate.py'},
]
for source, allowed in zip(('9aba960', '48b99ac'), conflicts):
    full = git('rev-parse', source).stdout.strip()
    r = git('cherry-pick', '-x', full, check=False)
    if r.returncode:
        unresolved = set(git('diff', '--name-only', '--diff-filter=U').stdout.splitlines())
        if not unresolved or not unresolved <= allowed:
            raise RuntimeError(r.stdout + r.stderr + str(unresolved))
        for name in sorted(unresolved):
            # Retain upstream governance, security cleanups and Pafio terms.
            git('checkout', '--ours', '--', name)
            p = Path(name)
            text = p.read_text()
            for module in ('StyioConfig', 'StyioIDE', 'StyioLSP'):
                text = text.replace('src/' + module + '/', 'src/StyioServices/' + module + '/')
            p.write_text(text)
        git('add', '-A')
        git('-c', 'core.editor=true', 'cherry-pick', '--continue')
# Retain the upstream checkout directory spelling after the source migration.
edit('.github/workflows/styio-audit.yml', [('working-directory: styio\n', 'working-directory: Styio\n')])
edit('.github/workflows/styio-ci-gate.yml', [('      - name: Five-layer pipeline tests', '      - name: IDE and LSP service tests\n        working-directory: styio-nightly\n        run: ctest --test-dir build/ci -L ide --output-on-failure --no-tests=error\n\n      - name: Five-layer pipeline tests')])
run(sys.executable, 'scripts/docs-index.py', '--write')
checks()
commit('fix(services): preserve upstream governance and validate relocated IDE services')
results.append({'branch': PREFIX + '01-services', 'sha': git('rev-parse', 'HEAD').stdout.strip(), 'tree': git('rev-parse', 'HEAD^{tree}').stdout.strip()})
expected = ['4469ec893df22f66162a499536ee9970d4882570', 'd2f9af36bea2e52b7e6469d5d2c713a61ef3632b']
if [item['tree'] for item in results] != expected:
    raise RuntimeError('Prepared trees differ from the locally audited candidates: ' + json.dumps(results))
Path(os.environ.get('EVIDENCE_OUT', '../prepared-batches.json')).write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
