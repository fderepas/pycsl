#!/usr/bin/env python3
r"""A MODULE-6 LOWERING WHOSE FALL-THROUGH IS A WHY3 CONSTANT — a named ratchet.

THE DEFECT CLASS, and it is this campaign's most productive single shape. When a
lowering does not recognize what it was given, the value it answers with becomes the
model's claim about the program. If that answer is a WHY3 CONSTANT — `true`, `false`,
`0`, `1` — the model does not merely lose the value, it DECIDES with it:

    #29  `\is_sorted` / `\array_eq` / `\permutation` fell through to `return "true"`
         under a heap memory model.  A DESCENDING array proved sorted.
    #30  `_match_pattern_cond` fell through to `return "true"`.  `case [1,2]:` on an
         int took the arm.
    #31  `_to_bool` answered `true` for every array local.  `a = []; if a:` was taken.
    #40  the `...` literal WAS the integer `0`, so `... == 0` proved outright.
    #41  a generator/set/tuple local WAS the integer `0`, so `x == 0`, `x < 1` and
         `x + 5` all proved.

Every one of those was a fall-through — the tail of a handler, or the final `else` of
its last `if` — and every one of them was found by hand, one at a time, after it had
been in the tree for months.  THE POINT OF THIS PLANE IS THAT THE NEXT ONE IS FOUND
WHEN IT IS WRITTEN.

WHAT IT CHECKS.  Every function in `src/pycsl/module6_whyml/` whose FALL-THROUGH is a
bare `return "<c>"` for a Why3 constant `c`.  The fall-through is the last statement of
the body, or — when that is an `if` with an `else` — the last statement of that `else`.
The baseline below is keyed on (function name, literal), never on line numbers, so it
survives ordinary edits and fails only when a NEW site appears or a known one changes
its answer.

WHAT IT DOES NOT CHECK, stated so nobody reads more into a green run than is there:
a constant returned from a GUARDED branch in the middle of a handler is not a
fall-through and is not counted — routes #22 and #24 lived there, and the honest
instrument for those is `bin/check-getattr-erasure.py` and
`bin/check-computed-rhs-erasure.py`, which watch the real emission.  A `return ""` is
counted separately and treated as SAFE-BY-CONSTRUCTION: an empty string is not a Why3
term, so it produces a syntax error at the use site rather than a decision.
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M6 = os.path.join(ROOT, "src", "pycsl", "module6_whyml")

# Why3 constants a lowering can DECIDE with.
DECIDING = {"true", "false", "0", "1", "0.0"}
# Not a Why3 term at all -> a syntax error at the use site, never a decision.
INERT = {""}

# ---------------------------------------------------------------------------
# THE BASELINE.  (function, literal) -> why this fall-through is not a route.
# Anything not listed here is a FAILURE, whether it is new or merely un-triaged.
# ---------------------------------------------------------------------------
BASELINE = {
    ("_handle_length2d_expr", "true"):
        "route #29: REFUSED before emission under typed/store; under the value models "
        "the branch above returns the real formula.",
    ("_handle_valid2d_expr", "true"):
        "route #29: same shape as _handle_length2d_expr, refused on the same terms.",
    ("_handle_issorted_expr", "true"):
        "route #29: refused under typed/store (witnesses 1004-1006).",
    ("_handle_arrayeq_expr", "true"):
        "route #29: refused under typed/store (witness 1007).",
    ("_handle_permutation_expr", "true"):
        "route #29: refused under typed/store (witness 1008).",
    ("_handle_sum_node_expr", "0"):
        "route #29: the `\\sum` atom, refused under typed/store on the same evidence.",
    ("_dv_missing_default", "0"):
        "the `.get(k)` default when the model carries no default -- an INT-typed "
        "dict read whose absent case really is the int 0 in the value model.",
    ("_feq", "false"):
        "preamble term-equality: a structural `feq` over two DIFFERENT constructors is "
        "genuinely false; the equal case is decided in the branches above.",
}

BASELINE_INERT = {
    "_dv_empty_default", "_getattr_self_field", "_iter_elem_class", "_handle_sum_call",
    "_tag_of_type", "_expr_to_whyml", "_stmts_disp_class", "_get_str", "ir_kind",
    "ir_get_str_present",
}


def literal_of(node):
    if (isinstance(node, ast.Return) and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)):
        return node.value.value.strip()
    return None


def real_body(stmts):
    return [s for s in stmts
            if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]


def scan():
    deciding, inert = [], []
    for dp, _dn, fn in os.walk(M6):
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            tree = ast.parse(open(p, encoding="utf-8").read())
            for fu in ast.walk(tree):
                if not isinstance(fu, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                body = real_body(fu.body)
                if not body:
                    continue
                hits = []
                lit = literal_of(body[-1])
                if lit is not None:
                    hits.append((body[-1].lineno, lit, "TAIL"))
                elif isinstance(body[-1], ast.If) and body[-1].orelse:
                    ol = real_body(body[-1].orelse)
                    if ol:
                        lit2 = literal_of(ol[-1])
                        if lit2 is not None:
                            hits.append((ol[-1].lineno, lit2, "ELSE"))
                for ln, l, kind in hits:
                    rel = os.path.relpath(p, ROOT)
                    if l in DECIDING:
                        deciding.append((fu.name, l, rel, ln, kind))
                    elif l in INERT:
                        inert.append((fu.name, l, rel, ln, kind))
    return deciding, inert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    deciding, inert = scan()
    if not deciding and not inert:
        print("[!] constant-fallthrough: scanned 0 site(s) in %s — that is not a "
              "measurement, the module path is broken. NOT A PASS." % M6, file=sys.stderr)
        return 2

    unknown = [d for d in deciding if (d[0], d[1]) not in BASELINE]
    unknown_inert = [d for d in inert if d[0] not in BASELINE_INERT]
    stale = sorted({k for k in BASELINE} - {(d[0], d[1]) for d in deciding})

    print("[*] constant-fallthrough: %d DECIDING fall-through(s) (a Why3 constant the "
          "model can branch on), %d INERT (`\"\"`, not a Why3 term)."
          % (len(deciding), len(inert)))
    if args.verbose or unknown:
        for nm, lit, rel, ln, kind in sorted(deciding):
            mark = "NEW " if (nm, lit) not in BASELINE else "    "
            print("    %s%-6s %-30s -> %-6s  %s:%d" % (mark, kind, nm, lit, rel, ln))
            if (nm, lit) in BASELINE:
                print("             %s" % BASELINE[(nm, lit)])

    rc = 0
    for nm, lit, rel, ln, kind in unknown:
        print("[!] constant-fallthrough: %s:%d `%s` falls through to the Why3 constant "
              "`%s`, and no entry in this gate's baseline says why that is not a "
              "decision the model gets to make. Add a classification (with a probe that "
              "consumes it in a GUARD) or make the answer opaque."
              % (rel, ln, nm, lit), file=sys.stderr)
        rc = 1
    for nm, lit, rel, ln, kind in unknown_inert:
        print("[!] constant-fallthrough: %s:%d `%s` falls through to `\"\"`. That is "
              "inert only while nothing treats an empty lowering as a term — add it to "
              "BASELINE_INERT once you have checked the use site."
              % (rel, ln, nm), file=sys.stderr)
        rc = 1
    for nm, lit in stale:
        print("[!] constant-fallthrough: baseline entry (%s, %s) no longer matches any "
              "site. Remove it — a baseline that outlives its site hides the next one."
              % (nm, lit), file=sys.stderr)
        rc = 1
    if rc == 0:
        print("[+] constant-fallthrough: OK — %d deciding / %d inert, every one "
              "classified." % (len(deciding), len(inert)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
