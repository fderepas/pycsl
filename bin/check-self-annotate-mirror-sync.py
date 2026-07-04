#!/usr/bin/env python3
"""Sync-check for the ENTIRE self-annotation mirror (`src/self-annotate/src/`).

The mirror reflects the live emitter `src/pycsl/` (same layout, incl. `frontend/`). It is
HETEROGENEOUS — a whole-file diff is the WRONG tool:

  * un-`\trusted` methods (the body-faithful `_handle_*` handlers) are ported VERBATIM from the
    live emitter — only `#@` contract/loop-invariant annotations are added; and
  * `\trusted` methods are intentionally-divergent bodyless STUBS (the recursion-leaf / sibling
    boundary), which the live emitter implements in full.

So the load-bearing, function-level invariant is what this checks, across EVERY function copied
from `src/pycsl` into the mirror — `self`-methods, module-level helpers, AND the `pycsl.py`
driver functions:

    EVERY un-`\trusted` mirror function has a body byte-IDENTICAL (modulo `#@` lines and blank
    lines) to the same-qualified-named live function.

That is what makes "verify the mirror" mean "the real code is body-faithful": the proof runs on
the ACTUAL emitter code, machine-checked to be a verbatim copy. `\trusted` stubs, mirror-only
functions (no live counterpart), and files with no live counterpart are skipped by design.

Coverage boundary: the mirror is intentionally a SUBSET of the live tree — a live function may be
absent from the mirror (≈147 are, off the verification path), so "live function missing from the
mirror" is NOT treated as drift. Module-level statements (imports, constants) are not diffed;
the load-bearing content is the function bodies. What IS enforced: any function present in BOTH
and un-`\trusted` in the mirror must match live verbatim — this is what catches a stale copy
(e.g. a `pycsl.py` CLI change the mirror didn't track).

This SUPERSEDES the old whole-file `rocq/`/`lean/` tier (empty, abandoned, stale paths) — see
`resync-campaign.md` §Tier-1 and `src/self-annotate/README.md`.

Exit 1 on any drift.
"""
import ast
import os
import sys
import difflib

# Every mirror `.py` under here is checked against its `src/pycsl/` counterpart (same relative
# path — the mirror follows the live layout, including `frontend/` and `module6_whyml/`).
MIRROR_ROOT = "src/self-annotate/src"
LIVE_ROOT = "src/pycsl"


def _strip(lines):
    """Drop `#@` annotation lines and blank lines (the only permitted mirror additions)."""
    return [ln for ln in lines
            if ln.strip() and not ln.strip().startswith("#@")]


def methods(path):
    """{qualified_name: (stripped_body_lines, is_trusted)} for EVERY function in a file —
    `self`-methods, module-level helpers (`whyml_ident`, `stable_hash`, `_short_type`, …),
    AND the driver functions in `pycsl.py` (`main`, `_run_pipeline`, `_run_proofs`, and their
    nested closures). Every `.py` copied from `src/pycsl` into the mirror is covered, not just
    the emitter's `self`-methods — so a drift in a module-level helper or in the CLI driver
    (a live `pycsl.py` change the mirror didn't track) is caught, not silently missed.

    Names are QUALIFIED (`Class.method`, `outer.inner` for nested defs) so same-named functions
    in different scopes don't collide. `is_trusted` iff a `#@ \\trusted` marker sits in the
    contiguous annotation/decorator/blank block immediately above the `def`."""
    src = open(path).read().split("\n")
    tree = ast.parse("\n".join(src))
    out = {}

    def _trusted_above(lineno):
        i = lineno - 2
        trusted = False
        while i >= 0 and (src[i].strip().startswith("#@")
                          or src[i].strip().startswith("@")
                          or src[i].strip() == ""):
            if "\\trusted" in src[i]:
                trusted = True
            i -= 1
        return trusted

    def _walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qn = prefix + child.name
                body = _strip(src[child.lineno - 1:child.end_lineno])
                out[qn] = (body, _trusted_above(child.lineno))
                _walk(child, qn + ".")        # nested closures
            elif isinstance(child, ast.ClassDef):
                _walk(child, prefix + child.name + ".")

    _walk(tree, "")
    return out


def main():
    diverged = 0
    checked = 0
    for root, _dirs, files in os.walk(MIRROR_ROOT):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            mpath = os.path.join(root, fn)
            lpath = mpath.replace(MIRROR_ROOT, LIVE_ROOT, 1)
            if not os.path.exists(lpath):
                continue   # mirror-only file (no live counterpart) — skip
            rel = os.path.relpath(mpath, MIRROR_ROOT)
            mm = methods(mpath)
            lm = methods(lpath)
            for name, (mbody, mtrusted) in mm.items():
                if mtrusted:
                    continue  # intentionally-divergent stub
                if name not in lm:
                    continue  # mirror-only function (e.g. the `mutable_state` decorator,
                              # @dataclass modeling infra) — intentional, not drift
                if mbody != lm[name][0]:
                    print(f"DIVERGED: {rel}::{name} — un-trusted mirror body != live emitter "
                          f"body:")
                    for dl in list(difflib.unified_diff(
                            lm[name][0], mbody, "live", "mirror", lineterm=""))[:30]:
                        print("  " + dl)
                    print("  ---")
                    diverged = 1
                else:
                    checked += 1
    if diverged == 0:
        print(f"OK: all {checked} un-trusted self-annotate mirror functions (self-methods, "
              f"module-level helpers, and pycsl.py driver functions) are verbatim copies of "
              f"the live source")
    sys.exit(diverged)


if __name__ == "__main__":
    main()
