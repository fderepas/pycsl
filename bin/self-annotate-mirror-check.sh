#!/usr/bin/env bash
# self-annotate-mirror-check — anti-drift gate.
#
# Verifies that every file under `src/self-annotate/src/` has a
# matching source file under `src/pycsl/`. The mirror's function and
# class *signatures* should match the source's; bodies may diverge
# (trusted stubs use `pass`/return placeholders).
#
# The check is structural, not byte-level: extract function + class
# signatures from each file via Python AST and compare the sets. A
# mismatch means the mirror is stale and the responsible PR must
# refresh it (typically by running `bin/self-annotate-stub-gen.py`).
#
# Skip with: PYCSL_SKIP_MIRROR_CHECK=1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "${PYCSL_SKIP_MIRROR_CHECK:-0}" = "1" ]; then
    echo "[*] mirror-check: skipped via PYCSL_SKIP_MIRROR_CHECK=1"
    exit 0
fi

if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

PROJECT_ROOT="$PROJECT_ROOT" python3 - <<'PY'
import ast
import os
import sys
from pathlib import Path

REPO = Path(os.environ["PROJECT_ROOT"])
MIRROR_ROOT = REPO / "src" / "self-annotate" / "src"
SOURCE_ROOT = REPO / "src" / "pycsl"


def signatures(path):
    """Return a set of (kind, qualname, n_params) per def/class.
    Bodies ignored."""
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError as exc:
        return {("ERROR", str(exc), 0)}
    out = set()
    def walk(node, prefix=""):
        for child in getattr(node, "body", []):
            if isinstance(child, ast.FunctionDef):
                args = child.args
                n = (len(args.args) + len(args.kwonlyargs)
                     + (1 if args.vararg else 0)
                     + (1 if args.kwarg else 0))
                out.add(("func", f"{prefix}{child.name}", n))
            elif isinstance(child, ast.AsyncFunctionDef):
                out.add(("afunc", f"{prefix}{child.name}", 0))
            elif isinstance(child, ast.ClassDef):
                out.add(("class", f"{prefix}{child.name}", 0))
                walk(child, prefix=f"{prefix}{child.name}.")
    walk(tree)
    return out


fail = 0
mirrors = sorted(MIRROR_ROOT.rglob("*.py"))
for m in mirrors:
    rel = m.relative_to(MIRROR_ROOT)
    src = SOURCE_ROOT / rel
    if not src.exists():
        print(f"[!] MISSING SOURCE: {rel} has no counterpart under src/pycsl/")
        fail += 1
        continue
    m_sigs = signatures(m)
    s_sigs = signatures(src)
    only_in_source = s_sigs - m_sigs
    only_in_mirror = m_sigs - s_sigs
    if only_in_source or only_in_mirror:
        print(f"[!] DRIFT in {rel}:")
        for kind, name, n in sorted(only_in_source)[:5]:
            print(f"    -- source has but mirror missing: {kind} {name} ({n} params)")
        if len(only_in_source) > 5:
            print(f"    -- ... and {len(only_in_source) - 5} more source-only")
        for kind, name, n in sorted(only_in_mirror)[:5]:
            print(f"    ++ mirror has but source missing: {kind} {name} ({n} params)")
        if len(only_in_mirror) > 5:
            print(f"    ++ ... and {len(only_in_mirror) - 5} more mirror-only")
        fail += 1

if fail == 0:
    print(f"[+] mirror-check: all {len(mirrors)} mirrors are in sync with src/pycsl/")
    sys.exit(0)
else:
    print(f"[!] mirror-check: {fail} mirror(s) drifted.")
    print(f"    Run: ./bin/self-annotate-stub-gen.py src/pycsl/<file> src/self-annotate/src/<file>")
    sys.exit(1)
PY
