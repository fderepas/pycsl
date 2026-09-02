#!/usr/bin/env python3
r"""check-avatar-frame-parity.py — the AVATAR-FRAME plane.

WHAT IT MEASURES.

Every `self.<m>(...)` call site in a converted mirror method is emitted as an application of
an abstract AVATAR, `val self__<m>_<arity> ...`. The avatar's `writes` clause is the ONLY
thing a caller knows about the callee's effect: if the avatar declares no frame, Why3 infers
NO effect, and every caller may then declare `assigns \nothing` however much state the real
callee writes. That is an assumption STRONGER than the mirror's own `#@ assigns`, i.e.
unsound, and it is invisible to `check-trusted-frame-honesty`, which compares a SOURCE
declaration against a LIVE closure and never looks at what the emitted avatar says.

Relaunch #32 discovered the intra-file half of this (a `\trusted` stub's `#@ assigns` was
UNOBSERVABLE when the label filter emptied the declared set) and built the rule that fixes
it: the avatar declares `writes { _pyobj_state }` when the callee declares a non-empty
`#@ assigns` the record cannot label. Relaunch #33 measured the residue and found the rule
is **INTRA-FILE ONLY**.

THE RESIDUE, and it is a real one. A mixin method is DEFINED (and its `#@ assigns`
declared) in one mirror file and INHERITED by another. In the inheriting file the emitter
has no declaration to read — `_module_method_writes` is keyed on the methods THIS file
declares — so `_declared_w` is empty, the `_pyobj_state` rule does not fire, and the avatar
is minted frameless. Measured: `module6_whyml/stmt_control_flow.mlw` emits

    val self__add_abstract_op_1 (x0: int) : int

with no receiver and no frame, while the SAME method in `statements.mlw` and
`expressions.mlw` — where it IS declared — carries

    val self__add_abstract_op_1 (self: statementemissionmixin) (x0: string) : unit
      writes { self._abstract_ops }

TWO BUCKETS, and they are different findings:

  (A) SAME-FILE — the method is declared in this very file with a non-`\nothing`
      `#@ assigns` and the avatar is still frameless. This would be a failure of #32's
      rule itself. **Measured 0, and 0 is the ratchet.**
  (B) INHERITED — the method is not declared here, and EVERY mirror file that does declare
      it says non-`\nothing`. The honest frame is knowable but not visible at this emission
      site. **Measured 11.**

REOPENING CAPABILITY for (B): resolve a called method's declared `#@ assigns` through the
IMPORTED-mixin registry (the emitter already imports the class and its method stubs — it
prints `Imported class from '<mod>': <Cls> (record + N method stub(s))`) instead of only
through `_module_method_writes`, which is this file's own declarations. The cheaper,
source-level alternative is the one #32 used for `_add_abstract_op` in `statements.py` and
`expressions.py`: add a `\trusted` protocol stub with the honest `#@ assigns` to each
inheriting mirror — correct, but it costs one marker per stub.

`--emit-dir` must point at a directory of emitted mirror `.mlw` files (the `l3sweep.sh`
output). Without it the gate emits them itself is NOT attempted — it fails loudly instead,
because a silently-skipped plane is worse than no plane.
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning)

MIRROR_ROOT = "src/self-annotate/src"

# --------------------------------------------------------------------------------------
# RATCHETS — the honest measurement at the tree that introduced this gate (relaunch #33).
#   (A) SAME-FILE ... 0  — a HARD 0. #32's rule covers this case and must keep covering it.
#   (B) INHERITED ... 11, every one named by the run:
#         frontend/__init__, frontend/ir_resolve, pycsl   ->  _py_stmts_to_ir
#         module6_whyml/functions   -> _collect_array_var_assigns, _is_emit_ir_expr,
#                                      _is_string_expr
#         module6_whyml/statements  -> _handle_return_stmt
#         module6_whyml/stmt_control_flow -> _add_abstract_op, _is_string_expr,
#                                      _seq_init_expr, _to_bool
# --------------------------------------------------------------------------------------
MAX_SAME_FILE = 0
MAX_INHERITED = 11

_AVATAR = re.compile(r"^\s*val self__([A-Za-z0-9_]+)_\d+ ")


def _declared_assigns(path: str):
    """{method name: True if its `#@ assigns` names anything but `\\nothing`}."""
    try:
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        tree = ast.parse(src)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return {}
    lines = src.split("\n")
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        block = []
        for line in reversed(lines[max(0, node.lineno - 45):node.lineno - 1]):
            if line.strip().startswith("#") or not line.strip():
                block.append(line)
            else:
                break
        assigns = [l for l in block if "#@ assigns" in l]
        if assigns:
            out[node.name] = "\\nothing" not in assigns[0]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", required=True,
                    help="directory of emitted mirror .mlw files (scratchpad l3sweep output)")
    ap.add_argument("--max-same-file", type=int, default=MAX_SAME_FILE)
    ap.add_argument("--max-inherited", type=int, default=MAX_INHERITED)
    args = ap.parse_args()

    if not os.path.isdir(args.emit_dir):
        print("[!] avatar-frame-parity: --emit-dir %r is not a directory. A silently "
              "skipped plane is worse than no plane." % (args.emit_dir,))
        return 2

    decl = {}
    for dirpath, dirnames, filenames in os.walk(MIRROR_ROOT):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if fn.endswith(".py"):
                path = os.path.join(dirpath, fn)
                decl[os.path.relpath(path, MIRROR_ROOT)] = _declared_assigns(path)

    same_file, inherited = [], []
    scanned = 0
    for mlw in sorted(os.listdir(args.emit_dir)):
        if not mlw.endswith(".mlw"):
            continue
        owner = None
        for rel in decl:
            if rel[:-3].replace("/", "_") + ".mlw" == mlw:
                owner = rel
        with open(os.path.join(args.emit_dir, mlw), encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        for i, line in enumerate(lines):
            m = _AVATAR.match(line)
            if not m:
                continue
            scanned += 1
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if "writes {" in line or "writes {" in nxt:
                continue
            name = m.group(1)
            for key in ("_" + name, name):
                if owner and key in decl[owner]:
                    if decl[owner][key]:
                        same_file.append((mlw, key))
                    break
                declaring = [r for r in decl if key in decl[r]]
                if declaring and all(decl[r][key] for r in declaring):
                    inherited.append((mlw, key, declaring[0]))
                    break

    print("[*] avatar-frame-parity: %d abstract `self__` avatar(s) scanned across %d "
          "emitted mirror(s); %d SAME-FILE frameless-yet-declared, %d INHERITED "
          "frameless-yet-declared."
          % (scanned, len(os.listdir(args.emit_dir)), len(same_file), len(inherited)))
    for mlw, key in sorted(same_file):
        print("    SAME-FILE  %-44s %s" % (mlw, key))
    for mlw, key, src in sorted(inherited):
        print("    INHERITED  %-44s %-32s declared in %s" % (mlw, key, src))

    rc = 0
    if len(same_file) > args.max_same_file:
        print("[!] avatar-frame-parity: SAME-FILE RATCHET BROKEN — %d > %d. A frameless "
              "avatar lets every caller assume the callee changes NOTHING."
              % (len(same_file), args.max_same_file))
        rc = 1
    if len(inherited) > args.max_inherited:
        print("[!] avatar-frame-parity: INHERITED RATCHET BROKEN — %d > %d."
              % (len(inherited), args.max_inherited))
        rc = 1
    if rc == 0:
        for got, want, what in ((len(same_file), args.max_same_file, "same-file"),
                                (len(inherited), args.max_inherited, "inherited")):
            if got < want:
                print("[+] avatar-frame-parity: %s %d < ratchet %d — lower the constant."
                      % (what, got, want))
        print("[+] avatar-frame-parity: OK (ratchets %d same-file / %d inherited)."
              % (args.max_same_file, args.max_inherited))
    return rc


if __name__ == "__main__":
    sys.exit(main())
