#!/usr/bin/env python3
r"""AN IR NODE KIND WHOSE MODULE-6 LOWERING IS A WHY3 CONSTANT — a named ratchet.

THE DEFECT CLASS, and it is the one that produced FIVE routes in two windows. A Python
value the model does not represent has to lower to SOMETHING. When that something is a
Why3 CONSTANT — `0`, `1`, `true`, `false` — the model does not merely lose the value: it
becomes indistinguishable from that constant, and every comparison against the constant is
then DECIDED, and decided wrongly.

    #40  the `...` literal, and the builtin name `Ellipsis`, WERE the integer `0`.
         `x = 0; if x is ...:` proved; `x = ...; if x == 0:` proved; `return ...`
         proved `\result == 0`.
    #41  a generator / non-empty set / non-empty tuple local WAS the integer `0`.
         `x == 0`, `x < 1` and `x + 5` all proved.
    #42  a `bool` literal under `is` WAS the integer `1`/`0`, because Module 5 collapsed
         `ast.Is` onto `==` and Module 6 int-encodes `bool`. `<int> is True` proved.
    #43  a COMPLEX literal WAS `int(value.real)`. `3j == 0` proved.
    #44  `None` WAS the integer `0`. `None == 0` proved, `<int> is None` proved, and the
         CONTRACT `ensures \result == None` proved for a function returning `0`.

Every one was found by hand, one at a time, and four of the five were found AFTER an
earlier route had already established the shape. THE POINT OF THIS PLANE IS THAT THE SIXTH
IS FOUND WHEN IT IS WRITTEN.

WHAT IT CHECKS. Every `if` in `src/pycsl/module6_whyml/` that is keyed on an IR NODE KIND
— `isinstance(node, <X>Expr)`, or a `== "<Kind>"` / `in ("<Kind>", ...)` test on a node's
type tag — and whose whole body is a `return "<literal>"` (or a two-armed
`return "<a>" if C else "<b>"`) for a Why3 constant. The baseline is keyed on
(function, kind, literal), never on line numbers, so it survives ordinary edits and fails
only when a NEW arm appears, a known one changes its answer, or a baseline entry outlives
its site.

WHAT IT DOES NOT CHECK, stated so nobody reads more into a green run than is there:

  * the TAIL fall-through of a handler. That is `bin/check-constant-fallthrough.py`, the
    twenty-third plane, and the two are deliberately disjoint: that one watches what a
    lowering answers when it recognized NOTHING, this one watches what it answers when it
    recognized a node kind EXACTLY and still had nothing to say about it.
  * a constant reached through a helper (`self._some_default()`), or built by string
    formatting. Only a literal `return` in the arm is seen.
  * MODULE 5. Routes #40, #43 and #44 were all born in `_py_expr_constant` /
    `_py_expr_name`, where a Python literal is turned into a constant IR NODE before
    Module 6 ever sees it. That producer side has no plane yet and is the honest gap in
    this instrument; the arms below are where those constants come to REST.
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M6 = os.path.join(ROOT, "src", "pycsl", "module6_whyml")

# Why3 constants a lowering can DECIDE with.
DECIDING = {"true", "false", "0", "1", "0.0", "-1"}

# ---------------------------------------------------------------------------
# THE BASELINE.  (function, kind, literal) -> why this constant answer is not a route.
# Anything not listed here is a FAILURE, whether it is new or merely un-triaged.
# ---------------------------------------------------------------------------
BASELINE = {
    ("_expr_to_whyml", "NoneExpr", "0"):
        "route #44: the STRUCTURAL `None` (an absent slice bound, an optional-field "
        "slot, a union arm) really is the int witness 0 under the Optional convention "
        "the union/carrier recognizers are built on. The VALUE positions that made it a "
        "route -- a `None`-bound local's reads, and the `is None` comparison "
        "fall-through -- are intercepted upstream of this arm and lower to the opaque "
        "`pycsl_none`. Witnesses 1058-1064.",
    ("_expr_to_whyml", '"None"', "0"):
        "route #44: the dict-shaped twin of the NoneExpr arm above, on the same terms.",
    ("_expr_to_whyml", "SliceExpr", "0"):
        "a bare `Slice` node in a VALUE position has no value; the real bounds are read "
        "by the subscript handler, which never routes the slice itself through here.",
    ("_expr_to_whyml", '"Slice"', "0"):
        "the dict-shaped twin of the SliceExpr arm above.",
    ("_expr_to_whyml", "UnknownPyExprExpr", "0"):
        "route #41: an UNRECOGNIZED expression. The literal 0 is retained deliberately "
        "-- moving it would move every existing genexp site -- and the unsoundness it "
        "used to carry is closed one level up, at the BINDING: a local bound to an "
        "UnknownPyExpr reads as the per-name opaque `pycsl_erased_<x>`. Witnesses "
        "1041-1045.",
    ("_expr_to_whyml", "str", "0"):
        "the `_PYAST_IRNODE_CTORS` guard inside the IfExp-of-constructors recognizer: a "
        "REFUSAL to lift an arm that is not a real ADT application. Not a value.",
    ("_to_bool", '"Var"', "true"):
        "self-tcb-reduction T1.a / Tier-5: the truthiness of a dict/set/map-typed local, "
        "whose Why3 type carries no int at all, so the default `<> 0` coercion is a TYPE "
        "ERROR rather than a wrong answer. `true` is a sound OVER-approximation for the "
        "type-safety+frame contracts proved here -- the real check is the `in` or the "
        "projection that follows -- and it is gated on @mutable_state / "
        "`_hvalmap_local_vars`, so it is inert elsewhere.",
    ("_to_bool", "int", "true|false"):
        "route #31's repair, not its defect: a collection whose SIZE the emitter KNOWS "
        "(`_known_collection_sizes`, and only while the name is not in "
        "`_rebound_collections`) has an EXACT truth value. The unknown-size case falls "
        "through to `Array.length x <> 0`.",
    ("_match_pattern_cond", '"Wildcard"', "true"):
        "route #30's repair, not its defect: a `case _:` wildcard genuinely matches "
        "everything. The kinds that do NOT are refused above it.",
    ("_expr_to_whyml", '"UnknownPyExpr|GenExp"', "0"):
        "route #41, dict-shaped: the same arm as UnknownPyExprExpr above, extended to "
        "GenExp for R2a parity. Closed at the BINDING, not here — see that entry.",
    ("_lower_getattr", '"DictLit|ArrayLit|SetLit|Call"', "0"):
        "ROUTE #47, OPEN AND RECORDED, NOT CLASSIFIED-SAFE. "
        "getting-better/open-routes/route47-getattr-default-erasure.md: `getattr(o, "
        "<absent>, {})` really does return the default at runtime, but this coercion "
        "models that default as the INTEGER 0, so `d == 0` is DECIDED where Python says "
        "`{} == 0` is False. MEASURED, proves at 4289185b. This entry exists so the plane "
        "stays green while the route is open; DELETE IT when the opaque per-kind default "
        "lands, and the plane will then be the thing that notices if it regresses.",
    ("_emit_term_retval", '"Bool"', "true|false"):
        "a `#@ proof`-bridge term whose value IS the bool literal -- faithful.",
}


def kind_of_test(t):
    """The single IR node KIND this `if` test is keyed on, or None if it is keyed on
    zero kinds or on more than one (an ambiguous test is not this plane's business)."""
    names = []
    for n in ast.walk(t):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "isinstance" and len(n.args) == 2
                and isinstance(n.args[1], ast.Name)):
            names.append(n.args[1].id)
        if isinstance(n, ast.Compare) and len(n.ops) == 1:
            if isinstance(n.ops[0], ast.Eq):
                r = n.comparators[0]
                if (isinstance(r, ast.Constant) and isinstance(r.value, str)
                        and r.value[:1].isupper()):
                    names.append('"%s"' % r.value)
            elif isinstance(n.ops[0], ast.In):
                r = n.comparators[0]
                if isinstance(r, ast.Tuple) and r.elts and all(
                        isinstance(e, ast.Constant) and isinstance(e.value, str)
                        and e.value[:1].isupper() for e in r.elts):
                    names.append('"%s"' % "|".join(e.value for e in r.elts))
    return names[0] if len(names) == 1 else None


def literal_body(stmts):
    """The Why3 literal this arm answers with, or None. A one-statement body that is a
    `return "<lit>"` or `return "<a>" if C else "<b>"`."""
    body = [s for s in stmts
            if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    if len(body) != 1 or not isinstance(body[0], ast.Return):
        return None
    v = body[0].value
    if isinstance(v, ast.Constant) and isinstance(v.value, str):
        return v.value.strip()
    if (isinstance(v, ast.IfExp) and isinstance(v.body, ast.Constant)
            and isinstance(v.orelse, ast.Constant)
            and isinstance(v.body.value, str) and isinstance(v.orelse.value, str)):
        return "%s|%s" % (v.body.value.strip(), v.orelse.value.strip())
    return None


def scan():
    hits = []
    for dp, _dn, fn in os.walk(M6):
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            tree = ast.parse(open(p, encoding="utf-8").read())
            for fu in ast.walk(tree):
                if not isinstance(fu, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for st in ast.walk(fu):
                    if not isinstance(st, ast.If):
                        continue
                    k = kind_of_test(st.test)
                    if k is None:
                        continue
                    lit = literal_body(st.body)
                    if lit is None:
                        continue
                    if all(x in DECIDING for x in lit.split("|")):
                        hits.append((fu.name, k, lit,
                                     os.path.relpath(p, ROOT), st.lineno))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    hits = scan()
    if not hits:
        print("[!] singleton-constant-lowering: scanned 0 site(s) in %s — that is not a "
              "measurement, the module path is broken. NOT A PASS." % M6, file=sys.stderr)
        return 2

    keys = {(h[0], h[1], h[2]) for h in hits}
    unknown = [h for h in hits if (h[0], h[1], h[2]) not in BASELINE]
    stale = sorted(set(BASELINE) - keys)

    print("[*] singleton-constant-lowering: %d node-kind arm(s) answering a Why3 "
          "CONSTANT." % len(hits))
    if args.verbose or unknown:
        for nm, k, lit, rel, ln in sorted(hits):
            mark = "NEW " if (nm, k, lit) not in BASELINE else "    "
            print("    %s%-28s %-22s -> %-12s %s:%d" % (mark, nm, k, lit, rel, ln))
            if (nm, k, lit) in BASELINE:
                print("         %s" % BASELINE[(nm, k, lit)])

    rc = 0
    for nm, k, lit, rel, ln in unknown:
        print("[!] singleton-constant-lowering: %s:%d — `%s` answers the Why3 constant "
              "`%s` for node kind %s, and no entry in this gate's baseline says why the "
              "model gets to DECIDE with it. PROBE IT END TO END: write a driver whose "
              "contract is FALSE of the program and whose guard consumes that value, and "
              "run Python to confirm the true answer. Then either classify it here or "
              "make the answer opaque." % (rel, ln, nm, lit, k), file=sys.stderr)
        rc = 1
    for nm, k, lit in stale:
        print("[!] singleton-constant-lowering: baseline entry (%s, %s, %s) no longer "
              "matches any site. Remove it — a baseline that outlives its site hides the "
              "next one." % (nm, k, lit), file=sys.stderr)
        rc = 1
    if rc == 0:
        print("[+] singleton-constant-lowering: OK — %d arm(s), every one classified."
              % len(hits))
    return rc


if __name__ == "__main__":
    sys.exit(main())
