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

REOPENING CAPABILITY for (B), and TWO ROUTES WERE SPIKED AND MEASURED (#33):

  ROUTE 1 — read the declaration from ANOTHER `<cls>__<m>` entry in `_module_method_writes`
  (the callee's own class prefix rather than the caller's). **MEASURED: no mirror moved,
  0 of 53.** `ir_resolve` injects a dependency's method stubs only for classes the file
  IMPORTS, and an inheriting mirror does not import the defining mixin — `stmt_control_flow`
  reports only `Imported from 'exception_model'`. There is nothing to find.

  ROUTE 2 — when the file has NO declaration for the callee at all, mint the avatar with
  the coarse `writes { _pyobj_state }`. Sound in the MODEL, and it does move the emission
  (7 mirrors), but **REFUTED**: 5 of 53 then fail L3-tc with "this expression depends on
  variable _pyobj_state, which is left out in the specification", and the only way to
  satisfy that is a non-`\nothing` `#@ assigns` on the CALLER. The first caller reached is
  `types._rhs_yields_map`, whose newly-flagged callee `_self_field_py_type` is a PURE
  lookup — so the rule forces a source declaration that is FALSE IN THE OTHER DIRECTION.
  Over-claiming is precisely what #32 measured and refused ("the cruder 'always emit the
  coarse cell when the filtered set is empty' rule was tried first and REFUSED"). A rule
  that cannot tell a writing callee from a pure one may not speak for either.
  (Two emitter pieces from that spike ARE independently correct and are recorded here for
  reuse: an avatar carrying the cell must register its name in `_pyobj_state_writers`,
  because `_add_abstract_op` DEDUPES and only the FIRST caller's mint sets
  `_obj_state_written`, so every later caller emitted `writes { }`; the caller-side re-arm
  then behaves exactly as it already does for a concrete sibling.)

  WHAT REMAINS, and it is a COST/SCALE item, not a floor: the source-level route #32 used
  by hand for `_add_abstract_op` in `statements.py` and `expressions.py` — add a `\trusted`
  protocol stub carrying the honest `#@ assigns` to each inheriting mirror. It is HONEST
  (all 11 methods declare a real frame where they are defined), it costs ONE MARKER PER
  STUB, and it triggers the same caller fixpoint #32 closed in 5-6 iterations per file,
  followed by a whole-file re-proof of each. Budget it as a segment, not as an increment.

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
