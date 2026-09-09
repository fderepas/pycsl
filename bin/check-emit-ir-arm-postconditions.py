#!/usr/bin/env python3
"""THE 28th PLANE — the emit_ir always-present arms are sound only while the methods that
REACH them carry no real postcondition, and until now that was PROSE.

`bin/check-type-keyed-constant-answers.py` (the 27th plane) classifies sixteen type-keyed
arms that answer a Why3 bool constant. Two of them — the emit_ir ALWAYS-PRESENT arm in
`_handle_binop` and its truthiness twin in `_to_bool` — are justified by a claim that is
CONDITIONAL rather than structural:

    "it is sound for the type-safety+frame contracts the mirror carries, because deleting a
     branch cannot make an `ensures True` false ... these arms fire at exactly NINE sites in
     SEVEN methods ... and EVERY ONE of the seven carries `#@ ensures True`. So the scope
     claim holds today, by measurement, and would be broken by giving any of those seven a
     real postcondition."

That last sentence names a way to make nine emission sites unsound, and NOTHING IN THE TREE
FAILED IF YOU DID IT. Deleting a branch cannot falsify `ensures True`; it can absolutely
falsify `ensures \\result > 0`. This plane is that missing gate.

WHAT IT CHECKS: every method in the REACHING SET below carries no postcondition stronger
than `True`.

HOW THE TWO PLANES COMPOSE, which is why a baseline list is honest here rather than a
staleness trap:
  * the 27th plane owns the ARMS. If an arm's guard signature changes, or a new arm starts
    answering a bool constant, it FAILS ("matches no arm — the lowering changed and the
    classification is stale"). Measured: it did exactly that during route #55.
  * this plane owns the METHODS that reach them.
Neither can drift without one of the two going red. What NEITHER catches is a NEW method
starting to reach an existing, unchanged arm; the reaching set is re-derived by emitter
instrumentation (`scratchpad/w49/always_present_trace.patch`) over the 53-file mirror
emission, and REACHING_SET_DERIVED_AT records when that was last done.
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys

MIRROR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "src", "self-annotate", "src")

# Derived by emitter instrumentation over the whole 53-file mirror emission — NINE sites in
# SEVEN names (`_handle_return_stmt` exists in two files, so eight method instances).
REACHING_SET = {
    "_field_type_from_annotation",
    "_handle_lambda_expr",
    "_handle_array_slice_set_stmt",
    "_handle_critical_section_stmt",
    "_handle_return_stmt",
    "_handle_match_stmt",
    "_try_union_is_none_match",
}
REACHING_SET_DERIVED_AT = "42a4f84b (relaunch #49), re-verified at the landed tree 2026-09-09"
EXPECTED_INSTANCES = 8


def _ensures_above(lines, lineno):
    """The `#@ ensures` clauses in the contract block immediately above a `def`."""
    out = []
    i = lineno - 2
    while i >= 0:
        s = lines[i].strip()
        if s.startswith("#") or s == "":
            m = re.match(r"#@\s*ensures\s+(.*)", s)
            if m:
                out.append(m.group(1).strip())
            i -= 1
            continue
        break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    seen, offenders = [], []
    for dp, dn, fn in os.walk(MIRROR):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            try:
                src = open(p, encoding="utf-8").read()
                tree = ast.parse(src)
            except (OSError, SyntaxError):
                continue
            lines = src.splitlines()
            for n in ast.walk(tree):
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if n.name not in REACHING_SET:
                    continue
                ens = _ensures_above(lines, n.lineno)
                rel = os.path.relpath(p, MIRROR)
                seen.append((n.name, rel, ens))
                real = [e for e in ens if e not in ("True", "true")]
                if real:
                    offenders.append((n.name, rel, real))

    if args.verbose:
        for name, rel, ens in sorted(seen):
            print(f"    {name:36} {rel:42} ensures={ens or ['<none>']}")

    print(f"[*] emit-ir-arm-postconditions: {len(seen)} method instance(s) reaching the "
          f"emit_ir always-present arms; {len(offenders)} carry a postcondition stronger "
          f"than `True` (must be 0). Reaching set derived at {REACHING_SET_DERIVED_AT}.")

    # A gate that cannot tell "nothing is wrong" from "I looked at nothing" is not a gate
    # (the #44 rule). The reaching set is a fixed list, so its instance count is knowable.
    if len(seen) != EXPECTED_INSTANCES:
        print(f"[!] emit-ir-arm-postconditions: found {len(seen)} instance(s), expected "
              f"{EXPECTED_INSTANCES}. A method in the reaching set was renamed, removed or "
              f"duplicated — re-derive the set with the emitter instrumentation "
              f"(`scratchpad/w49/always_present_trace.patch`) before changing this number. "
              f"NOT A PASS.", file=sys.stderr)
        return 2

    if offenders:
        for name, rel, real in offenders:
            print(f"[!]   {name} ({rel}) now carries: {real}", file=sys.stderr)
        print("[!] emit-ir-arm-postconditions: RATCHET BROKEN. The emit_ir always-present "
              "arms DELETE a branch, and that is sound for `ensures True` only. A real "
              "postcondition on a method reaching them is proved over a STRICT SUBSET of "
              "the reachable states — the shape of routes #50, #51 and #55. Either give "
              "the arm a faithful lowering for this method, or keep the contract trivial.",
              file=sys.stderr)
        return 1

    print("[+] emit-ir-arm-postconditions: OK — every method reaching the emit_ir "
          "always-present arms keeps a trivial postcondition.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
