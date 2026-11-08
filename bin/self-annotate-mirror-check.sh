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


def signatures(path, skip_trusted=False):
    """Return a set of (kind, qualname, n_params) per def/class. Bodies ignored.

    The self-annotation mirror is heterogeneous: `\\trusted` methods are intentionally-divergent
    STUBS, often RELOCATED into a different mixin class than the live method they stub (so a CF
    handler can call them cross-class). Those must NOT be compared structurally — with
    skip_trusted, a mirror method whose contiguous `#@`/decorator block carries a `\\trusted`
    marker is dropped. (The live source has no `#@`, so skip_trusted is a no-op there.)"""
    src = path.read_text().split("\n")
    try:
        tree = ast.parse("\n".join(src))
    except SyntaxError as exc:
        return {("ERROR", str(exc), 0)}
    out = set()
    def is_trusted(node):
        # The block above a `def` is `#@` contract lines, decorators, blank lines AND plain `#`
        # comments. Omitting plain `#` stopped the walk at any justification comment sitting
        # between the `\trusted` marker and the `def` — so the stub was compared as if it were
        # un-trusted, and a legitimately RELOCATED stub then read as drift. Same defect, same
        # fix as in check-self-annotate-mirror-sync.py.
        i = node.lineno - 2
        while i >= 0 and (src[i].strip().startswith("#")
                          or src[i].strip().startswith("@")
                          or src[i].strip() == ""):
            # THE DIRECTIVE, NOT A PROSE MENTION (gen #4) — same repair as in
            # check-self-annotate-mirror-sync.py, same defect, same 46 functions. A
            # justification comment that merely NAMES the marker used to make this
            # plane treat a converted, emitted-and-proved method as an
            # intentionally-divergent stub and skip it.
            if src[i].strip().startswith("#@") and "\\trusted" in src[i]:
                return True
            i -= 1
        return False
    # Mirror-only infra shims (the `@mutable_state` decorator placeholder the mirror defines so
    # `@mutable_state`-marked classes parse) have no live counterpart by design.
    MIRROR_ONLY = {"mutable_state"}
    def walk(node, prefix=""):
        for child in getattr(node, "body", []):
            if isinstance(child, ast.FunctionDef):
                if skip_trusted and (is_trusted(child) or child.name in MIRROR_ONLY):
                    continue
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
            else:
                # DESCEND THROUGH COMPOUND STATEMENTS (gen #4), same repair as in
                # check-self-annotate-mirror-sync.py: a `def` nested inside a `try:` / `if:` /
                # `with:` / `for:` body was invisible to this walk. Both sides are walked the
                # same way so it produced no FALSE drift, only silent lost coverage.
                for sub in ("body", "orelse", "finalbody", "handlers"):
                    for item in getattr(child, sub, []) or []:
                        walk(item, prefix=prefix)
    walk(tree)
    return out


# (#49) gen #31 — EVERY NAME DEFINED ANYWHERE UNDER src/pycsl, so a RELOCATED def can be
# told apart from a STALE one. This script's question is "is the mirror stale?", and a def the
# mirror carries in a DIFFERENT FILE from the live one is not stale — it is the
# `#@ sibling_concrete` device: a mirror file has no MRO, so it must carry a CONCRETE copy of
# a sibling mixin's method for its own `self._m(...)` sites to lower to a real body instead of
# a receiver-less abstract `val` (lesson (ay)). The script ALREADY skips `\trusted` stubs for
# exactly this reason ("intentionally divergent / RELOCATED"); un-trusted relocations were the
# half it had not been told about, and they made this script print a permanent red that no
# battery ran — which is how three of them DRIFTED unnoticed (see the commit that added
# bin/check-sibling-concrete-fidelity.py). Their bodies are that plane's question; staleness
# stays this one's. A name that exists NOWHERE live is still drift, and still fails here.
LIVE_NAMES = set()
for _sp in SOURCE_ROOT.rglob("*.py"):
    try:
        _st = ast.parse(_sp.read_text())
    except (SyntaxError, OSError):
        continue
    for _n in ast.walk(_st):
        if isinstance(_n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            LIVE_NAMES.add(_n.name)

fail = 0
mirrors = sorted(MIRROR_ROOT.rglob("*.py"))
for m in mirrors:
    rel = m.relative_to(MIRROR_ROOT)
    src = SOURCE_ROOT / rel
    if not src.exists():
        print(f"[!] MISSING SOURCE: {rel} has no counterpart under src/pycsl/")
        fail += 1
        continue
    # Skip \trusted stubs (intentionally divergent / relocated). The mirror is a chosen SUBSET
    # of the source's defs, so source-only entries are expected and NOT drift. Drift = an
    # un-\trusted mirror def whose signature is ABSENT from the source (renamed, param-count
    # changed, or a stray def) — that means the verbatim copy no longer matches.
    m_sigs = signatures(m, skip_trusted=True)
    s_sigs = signatures(src)
    only_in_mirror = m_sigs - s_sigs
    # RELOCATED, not stale: the BARE name is defined somewhere under src/pycsl. Dropped here
    # and checked verbatim by bin/check-sibling-concrete-fidelity.py.
    only_in_mirror = {(k, n, c) for (k, n, c) in only_in_mirror
                      if n.rsplit(".", 1)[-1] not in LIVE_NAMES}
    if only_in_mirror:
        print(f"[!] DRIFT in {rel}:")
        for kind, name, n in sorted(only_in_mirror)[:8]:
            print(f"    ++ un-trusted mirror def not in source: {kind} {name} ({n} params)")
        if len(only_in_mirror) > 8:
            print(f"    ++ ... and {len(only_in_mirror) - 8} more")
        fail += 1

if fail == 0:
    print(f"[+] mirror-check: all {len(mirrors)} mirrors are in sync with src/pycsl/ "
          f"(a def the mirror RELOCATES into a sibling file is not staleness; its body is "
          f"checked by bin/check-sibling-concrete-fidelity.py)")
    sys.exit(0)
else:
    print(f"[!] mirror-check: {fail} mirror(s) drifted.")
    print(f"    Run: ./bin/self-annotate-stub-gen.py src/pycsl/<file> src/self-annotate/src/<file>")
    sys.exit(1)
PY
