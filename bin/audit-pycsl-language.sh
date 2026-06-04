#!/usr/bin/env bash
# bin/audit-pycsl-language.sh — one-command PyCSL language-consistency audit.
#
# Runs the mechanical subset of the `pycsl-audit-pycsl-language` skill's runbook:
# the checks that confirm a language change is wired and documented consistently.
# It is a CONVENIENCE ENTRY POINT that bundles existing gates (it does not
# duplicate them into cmmi-audit.sh — see the skill for why). The end-to-end
# clause-wiring trace and the semantic-fidelity judgement remain a manual audit;
# this script catches the mechanical drift.
#
# Checks:
#   1. Grammar builds          — Module2_Parser() constructs (no undefined rules /
#      transformer errors); reports any ?contract: alternative lacking a same-named
#      transformer method (advisory).
#   2. Doc coherency           — bin/doc-coherency.py --check (5-surface directive parity)
#   3. Module index            — bin/cmmi-mod-index.py --verify --all (def-count drift)
#   4. Reference corpus        — bin/run-reference-tests.sh (skipped with --quick)
#   5. Self-annotate mirrors   — make self-annotate-verify    (skipped with --quick)
#
# Usage:
#   bin/audit-pycsl-language.sh           # full audit
#   bin/audit-pycsl-language.sh --quick   # mechanical checks only (skip corpus + mirrors)
#
# Exit 0 = consistent; 1 = drift; 2 = prerequisite missing.

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
cd "$REPO_ROOT"

# Determinism + recursion guards (see the skill's house rules).
export PYTHONHASHSEED=0
export CMMI_AUDIT_NESTED=1

QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1

PY="$REPO_ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

FAILED=0
run() {  # run <label> <cmd...>
    local label="$1"; shift
    printf '[..] %s\n' "$label"
    if "$@" > /tmp/audit-pycsl-lang.$$.out 2>&1; then
        printf '[OK] %s\n' "$label"
    else
        printf '[FAIL] %s (exit %d)\n' "$label" "$?"
        sed 's/^/    | /' /tmp/audit-pycsl-lang.$$.out | tail -25
        FAILED=1
    fi
    rm -f /tmp/audit-pycsl-lang.$$.out
}

echo "=== PyCSL language-consistency audit ==="

# 1. Grammar builds + transformer coverage (advisory on orphans).
run "grammar builds (Module2_Parser constructs)" "$PY" - <<'PY'
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path("src/pycsl")))
import Module2_Parser as M
M.Module2_Parser()  # raises if the Lark grammar has undefined rules / build errors
src = pathlib.Path("src/pycsl/Module2_Parser.py").read_text()
m = re.search(r"\?contract:(.*?)(?:\n\s*\n|\n[A-Za-z_]+:)", src, re.S)
alts = re.findall(r"[A-Za-z_][A-Za-z_0-9]*", m.group(1)) if m else []
methods = set(dir(M.PyCSLTransformer))
orphans = [a for a in alts if a not in methods]
print(f"?contract: lists {len(alts)} alternative(s); transformer covers {len(alts)-len(orphans)}")
if orphans:
    print("  (advisory) alternatives without a same-named transformer method:")
    for o in orphans:
        print(f"    - {o}")
PY

# 2. Documentation coherency across the five normative surfaces.
run "doc coherency (5-surface directive parity)" "$REPO_ROOT/bin/doc-coherency.py" --check

# 3. L4 module indices match in-source def counts.
run "module index --verify --all" "$PY" "$REPO_ROOT/bin/cmmi-mod-index.py" --verify --all

if [ "$QUICK" -eq 0 ]; then
    # 4. The corpus still verifies (the real proof the language works).
    run "reference corpus" "$REPO_ROOT/bin/run-reference-tests.sh"
    # 5. PyCSL still proves its own modules under --no-proof.
    run "self-annotate mirrors verify" make self-annotate-verify
else
    echo "[skip] reference corpus + self-annotate mirrors (--quick)"
fi

echo "========================================="
if [ "$FAILED" -eq 0 ]; then
    echo "PyCSL language audit: PASS"
else
    echo "PyCSL language audit: FAIL — see above"
fi
exit "$FAILED"
