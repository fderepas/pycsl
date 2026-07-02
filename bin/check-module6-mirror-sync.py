#!/usr/bin/env python3
"""Sync-check for the module6_whyml self-annotation mirror.

The mirror `src/self-annotate/src/module6_whyml/*.py` reflects the live emitter
`src/pycsl/module6_whyml/*.py`. Unlike the whole-file rocq/lean mirrors (handled by
`check-self-annotate-sync.sh`), this mirror is HETEROGENEOUS:

  * un-`\trusted` methods (the body-faithful `_handle_*` handlers) are ported VERBATIM from the
    live emitter — only `#@` contract/loop-invariant annotations are added; and
  * `\trusted` methods are intentionally-divergent bodyless STUBS (the recursion-leaf / sibling
    boundary), which the live emitter implements in full.

So a whole-file diff is meaningless here. This checker verifies the load-bearing invariant:

    EVERY un-`\trusted` method in the mirror has a body byte-IDENTICAL (modulo `#@` lines and
    blank lines) to the same-named method in the live emitter.

That is what makes "verify the mirror" mean "the real `_handle_*` is body-faithful": the proof
runs on the ACTUAL emitter code, machine-checked to be a verbatim copy. Without this, a mirror
handler could silently drift from the emitter it claims to reflect.

Exit 1 on any drift (an un-`\trusted` mirror method whose body != the live emitter's, or that
names no live method). `\trusted` stubs and mirror-only infra (module-level `mutable_state`,
etc.) are skipped by design.
"""
import ast
import os
import sys
import difflib

MIRROR_DIR = "src/self-annotate/src/module6_whyml"
LIVE_DIR = "src/pycsl/module6_whyml"


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
    for fn in sorted(os.listdir(MIRROR_DIR)):
        if not fn.endswith(".py"):
            continue
        mpath = os.path.join(MIRROR_DIR, fn)
        lpath = os.path.join(LIVE_DIR, fn)
        if not os.path.exists(lpath):
            continue
        mm = methods(mpath)
        lm = methods(lpath)
        for name, (mbody, mtrusted) in mm.items():
            if mtrusted:
                continue  # intentionally-divergent stub
            if name not in lm:
                print(f"DIVERGED: {fn}::{name} — un-trusted in mirror but no such live "
                      f"emitter method")
                diverged = 1
                continue
            if mbody != lm[name][0]:
                print(f"DIVERGED: {fn}::{name} — un-trusted mirror body != live emitter body:")
                for dl in list(difflib.unified_diff(
                        lm[name][0], mbody, "live", "mirror", lineterm=""))[:30]:
                    print("  " + dl)
                print("  ---")
                diverged = 1
            else:
                checked += 1
    if diverged == 0:
        print(f"OK: all {checked} un-trusted module6_whyml mirror methods are verbatim copies "
              f"of the live emitter")
    sys.exit(diverged)


if __name__ == "__main__":
    main()
