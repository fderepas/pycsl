#!/usr/bin/env python3
r"""L-PLANE ORACLE: every CONSTANT the emitter substitutes for a RETURN VALUE.

WHY THIS EXISTS (gen #30, route #198). `bin/check-argument-coercion.py` classifies every
substitution the emitter makes to a call's ARGUMENTS, and names its own gap in its own
header:

    "the RETURN side. A callee's result flowing back into a caller's typed slot is the
     mirror image of this and has no plane yet — the honest gap in this instrument."

Route #198 came out of exactly that gap. `stmt_control_flow::_handle_return_stmt` lowered a
BARE `return` to the unit `"()"` and then to the literal `"0"`, so an int-returning
function's bare return emitted `raise (Return 0)` and

    #@ requires x > 0
    #@ ensures \result == 0
    def f(x: int) -> int:
        if x > 0:
            return

PROVED, while CPython answers `None` and the TRUE twin `\result != 0` was REFUSED. Nothing
in the battery looked at that line. The SAME program spelled `return None` had been correct
since route #191 — one statement, two spellings, two answers.

WHAT IT MEASURES. Every assignment of a STRING CONSTANT to the value variable inside the
emitter's return-statement handlers: the WhyML text that becomes the returned value. Each
site is keyed on (file, function, target, literal) and must carry a justification here,
TOGETHER WITH ITS OCCURRENCE COUNT.

THE COUNT IS THE LOAD-BEARING PART, and it is this gate's own first finding about itself.
Keyed on the literal alone, the gate would NOT have caught route #198: `val = "0"` was
already justified for the `False`-literal arm, so a SECOND `val = "0"` — the bare-return
arm — would have matched that entry and passed. A justification covers the sites it was
written for and no others, so the baseline pins HOW MANY there are. A new arm reaching an
already-blessed literal moves the count and fails.

A NEW site with no justification FAILS; a count that moves FAILS; a justification whose
site has disappeared is reported as STALE (the #44 rule applied to this gate's own
baseline: an entry that no longer describes the code is not evidence).

WHAT IT DOES NOT CHECK, stated rather than implied:
  * The COMPUTED return values — `_expr_to_whyml(...)`, `_seq_init_expr(...)`,
    `materialize` bridges. Those are pass-through and are the argument plane's shape, not
    this one's.
  * The CALLER's side of the same boundary: a callee's result flowing into a caller's
    typed slot. That is still nobody's plane. This gate covers where the value is MINTED,
    not where it is consumed.
  * Constants minted elsewhere and merely NAMED here (the `materialize_*` bridges).

Usage:  bin/check-return-boundary-substitutions.py [--verbose]
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "src", "pycsl", "module6_whyml")

# The value variables a return handler builds its payload in.
VALUE_TARGETS = {"val", "seq_val"}

# (file, function, target, literal) -> (occurrences, why this constant is FAITHFUL).
JUSTIFIED = {
    ("stmt_control_flow.py", "_handle_return_stmt", "val", "()"): (1,
        "the UNIT payload for a bare `return`. Not an answer yet — it is the marker the "
        "arms below dispatch on, and the int arm's own entry is the one that matters."),
    ("stmt_control_flow.py", "_handle_return_stmt", "val", "pycsl_none"): (1,
        "(#49) ROUTE #198. A bare `return` IS `return None` in Python, and route #191 "
        "already made the typed `None` leaf read back as this shared opaque. Before #198 "
        "this arm answered the literal `0`, so `#@ ensures \\result == 0` PROVED over "
        "`def f(x: int) -> int: if x > 0: return` while CPython answers `None`, with the "
        "TRUE twin `\\result != 0` REFUSED (witnesses 1693/1694). `(any int)` would also "
        "have been sound and is strictly weaker: `any` is fresh at every evaluation and "
        "cannot keep two `None`s equal."),
    ("stmt_control_flow.py", "_handle_return_stmt", "val", "(any int)"): (2,
        "(#49) ROUTE #117. An `array int` local returned from a function whose WhyML "
        "return type is `int` cannot be carried by `exception Return int`. It was the "
        "literal `0` — `if x > 0: return xs` PROVED `\\result == 0` while CPython "
        "returned the list. The value is genuinely UNKNOWN here, so `(any int)`, which "
        "stands for every int and decides nothing, is the honest answer."),
    ("stmt_control_flow.py", "_handle_return_stmt", "val", "1"): (2,
        "the Python literal `True` returned from an int-modelled function. FAITHFUL: "
        "Python's `True == 1` is True and `bool` is modelled as `int` throughout, so this "
        "is a representation change and not a substitution."),
    ("stmt_control_flow.py", "_handle_return_stmt", "val", "0"): (2,
        "the Python literal `False` returned from an int-modelled function. FAITHFUL for "
        "the same reason as the `True` arm above (`False == 0` is True). THE STANDING "
        "CONDITION, and it is the one route #198 broke: this justification covers ONLY "
        "the `val == \"false\"` arm. Any OTHER path that lands the literal `0` in the "
        "return value is a substitution, not a representation change, and needs its own "
        "entry — the bare-return arm had reached this same literal with no entry at all."),
    ("stmt_control_flow.py", "_handle_return_stmt", "seq_val", "Seq.empty"): (4,
        "`return []` from a function returning a sequence carrier (`array int`, "
        "`array string`, `array emit_ir`). FAITHFUL: the empty list really is the empty "
        "sequence, so unlike route #193's 1024-long placeholder this one has the length "
        "it claims (route #196 is the same correction at the argument boundary)."),
}


def sites(live=None):
    live = live or LIVE
    out = []
    for fn in sorted(os.listdir(live)):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(live, fn)
        try:
            tree = ast.parse(open(path).read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if "return_stmt" not in node.name:
                continue
            for m in ast.walk(node):
                if (isinstance(m, ast.Assign) and len(m.targets) == 1
                        and isinstance(m.targets[0], ast.Name)
                        and m.targets[0].id in VALUE_TARGETS
                        and isinstance(m.value, ast.Constant)
                        and isinstance(m.value.value, str)):
                    out.append((fn, node.name, m.targets[0].id, m.value.value, m.lineno))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    # SELF-TEST HOOK, and it is not a convenience: a gate nobody has ever seen FAIL is a
    # claim, not an instrument. `--live <other tree>/src/pycsl/module6_whyml` runs the same
    # walk over another checkout, which is how this gate was shown to fire on the pre-#198
    # emitter rather than merely asserted to.
    ap.add_argument("--live", default=None,
                    help="scan this module6_whyml directory instead of the live one")
    args = ap.parse_args()

    found = sites(args.live)
    # THE ZERO-CHECK REFUSAL (the #44 rule): a gate that cannot tell "nothing is wrong"
    # from "I looked at nothing" is not a gate. The return handler has carried constant
    # substitutions since the emitter existed; zero means the walk broke.
    if not found:
        print("[!] return-boundary: REFUSING — ZERO return-value substitution sites found. "
              "The AST walk or the handler's name has changed; this is not a pass.",
              file=sys.stderr)
        return 2

    from collections import Counter
    seen = Counter((f, fn, t, lit) for f, fn, t, lit, _ in found)
    unjustified = sorted(k for k in seen if k not in JUSTIFIED)
    stale = sorted(k for k in JUSTIFIED if k not in seen)
    moved = sorted((k, JUSTIFIED[k][0], seen[k]) for k in seen
                   if k in JUSTIFIED and JUSTIFIED[k][0] != seen[k])

    if args.verbose:
        for f, fn, t, lit, ln in sorted(found, key=lambda r: (r[0], r[4])):
            mark = "ok " if (f, fn, t, lit) in JUSTIFIED else "NEW"
            print("    %s %s:%d  %s = %r" % (mark, f, ln, t, lit))

    print("[*] return-boundary: %d substitution site(s), %d distinct, %d justified."
          % (len(found), len(seen), len(seen) - len(unjustified)))

    rc = 0
    for k in stale:
        print("[!]   STALE justification (no such site any more): %s" % (k,), file=sys.stderr)
        rc = 1
    for k in unjustified:
        print("[!]   UNJUSTIFIED return-value substitution: %s" % (k,), file=sys.stderr)
        rc = 1
    for k, want, got in moved:
        print("[!]   COUNT MOVED for %s: baseline %d, found %d. A justification covers the "
              "sites it was written for and no others — a NEW arm reaching an already-"
              "blessed literal is exactly how route #198 would have slipped through a "
              "literal-only key." % (k, want, got), file=sys.stderr)
        rc = 1
    if rc:
        print("[!] return-boundary: NOT OK — every constant substituted for a return value "
              "must carry a justification here, and every justification must have a site.",
              file=sys.stderr)
    else:
        print("[+] return-boundary: OK — every return-value constant is justified.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
