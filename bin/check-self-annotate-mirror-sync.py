#!/usr/bin/env python3
"""Sync-check for the ENTIRE self-annotation mirror (`src/self-annotate/src/`).

The mirror reflects the live emitter `src/pycsl/` (same layout, incl. `frontend/`). It is
HETEROGENEOUS — a whole-file diff is the WRONG tool:

  * un-`\trusted` methods (the body-faithful `_handle_*` handlers) are ported VERBATIM from the
    live emitter — only `#@` contract/loop-invariant annotations are added; and
  * `\trusted` methods are intentionally-divergent bodyless STUBS (the recursion-leaf / sibling
    boundary), which the live emitter implements in full.

So the load-bearing, method-level invariant is what this checks:

    EVERY un-`\trusted` mirror method has a body byte-IDENTICAL (modulo `#@` lines and blank
    lines) to the same-named live emitter method.

That is what makes "verify the mirror" mean "the real code is body-faithful": the proof runs on
the ACTUAL emitter code, machine-checked to be a verbatim copy. `\trusted` stubs, mirror-only
infra, and files with no live counterpart are skipped by design.

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
    """{method_name: (stripped_body_lines, is_trusted)} for every `self`-method in a file.

    `is_trusted` iff a `#@ \\trusted` marker sits in the contiguous annotation/decorator/blank
    block immediately above the `def`."""
    src = open(path).read().split("\n")
    tree = ast.parse("\n".join(src))
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not (node.args.args and node.args.args[0].arg == "self"):
            continue  # skip module-level helpers (mutable_state, etc.)
        i = node.lineno - 2
        trusted = False
        while i >= 0 and (src[i].strip().startswith("#@")
                          or src[i].strip().startswith("@")
                          or src[i].strip() == ""):
            if "\\trusted" in src[i]:
                trusted = True
            i -= 1
        body = _strip(src[node.lineno - 1:node.end_lineno])
        out[node.name] = (body, trusted)
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
                    print(f"DIVERGED: {rel}::{name} — un-trusted in mirror but no such live "
                          f"emitter method")
                    diverged = 1
                    continue
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
        print(f"OK: all {checked} un-trusted self-annotate mirror methods are verbatim copies "
              f"of the live emitter")
    sys.exit(diverged)


if __name__ == "__main__":
    main()
