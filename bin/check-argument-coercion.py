#!/usr/bin/env python3
r"""AN ARGUMENT COERCION THAT SUBSTITUTES A DIFFERENT VALUE — a named ratchet.

THE DEFECT CLASS. A call site's ACTUAL is lowered to WhyML text before the callee's
parameter type is known. When the two disagree, `_coerce_dotted_args` and its siblings do
not refuse — they SUBSTITUTE. Most substitutions are bridges (a `seq` materialized into an
`array`, element-by-element, nothing lost). A few REPLACE the value with a different one,
and each of those is a place where the model can answer a question about the argument that
the program would answer differently.

    #192  an actual whose lowered text was `"0"` became `(None: option <R>)` at an
          `Optional[<record>]` slot, and `(Arm_N_None : _union_*)` at a synthesized-union
          slot. The guard said "restricted to a literal `0` actual, so a genuinely
          int-valued expression still fails LOUDLY" — and a literal `0` IS a genuinely
          int-valued expression. It held only because, before route #191, the Python
          `None` ALSO lowered to `"0"`: the two shared a spelling, so the test was a
          COINCIDENCE. `self.tag(0)` PROVED `\result == 1` where CPython answers 2.
    #193  an actual whose lowered text was `"0"` became `(Array.make 1 0)` — a DEFINITE
          length-1 array — at an `array int` slot. `sorted_1` carries
          `ensures { Array.length result = Array.length a }`, so
          `len(sorted(x for x in [3, 1, 2]))` PROVED `== 1` where CPython answers 3. The
          defence beside it — "the abstract vals have no axioms about their input
          CONTENTS" — was a statement about contents, and the law being read was length.

Both were found by the PREVIOUS route's repair, in the SAME function, within a day. That
is the signature the campaign's own lesson names: THE ROUTES CLUSTER WHERE THERE IS NO
PLANE. This is the plane.

WHAT IT CHECKS. Every `coerced.append(...)` / `cargs.append(...)` in the argument-coercion
functions of `src/pycsl/module6_whyml/`, classified into PASS-THROUGH (the argument is
appended unchanged — nothing to justify) and SUBSTITUTION (anything else). Every
SUBSTITUTION must carry a baseline entry saying why the model gets to answer with that
value instead of the one the program has. The baseline is keyed on
(function, appended-expression source), never on line numbers, so it survives ordinary
edits and fails only when a NEW substitution appears, a known one changes its answer, or a
baseline entry outlives its site.

WHAT IT DOES NOT CHECK, stated so nobody reads more into a green run than is there:

  * the GUARD. This plane sees WHAT is substituted, not WHEN. A substitution whose guard
    is keyed on a WhyML SPELLING rather than on a value is exactly route #192's shape, and
    the only instrument for that is a probe. The baseline text is where that reasoning is
    recorded; the gate makes sure the text exists and is re-read whenever the arm moves.
  * the RETURN side. A callee's result flowing back into a caller's typed slot is the
    mirror image of this and has no plane yet — the honest gap in this instrument.
  * coercions that happen INSIDE `_expr_to_whyml` rather than at the call boundary. Those
    are `bin/check-singleton-constant-lowering.py` (a node kind answering a constant) and
    `bin/check-constant-fallthrough.py` (a handler answering one having recognized
    nothing). The three are deliberately disjoint.
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M6 = os.path.join(ROOT, "src", "pycsl", "module6_whyml")

# The accumulators an argument-coercion loop appends to.
ACCUMULATORS = {"coerced", "cargs"}

# Appended expressions that are the ACTUAL, unchanged. Nothing to justify.
PASS_THROUGH = {"arg", "a", "_s", "whyml_str"}

# ---------------------------------------------------------------------------
# THE BASELINE.  (function, appended source) -> why this substitution is not a route.
# Anything not listed here is a FAILURE, whether it is new or merely un-triaged.
# ---------------------------------------------------------------------------
BASELINE = {
    ("_coerce_dotted_args", "'0'"):
        "THE EMPTY-LIST PLACEHOLDER into an int-erased param. `[]` lowers to the "
        "emitter's `(Array.make 1024 0)` stand-in, and a param the callee int-erases "
        "cannot take an array at all (L3-tc `array int` vs `int`). The int witness `0` "
        "loses nothing the placeholder had: the placeholder is not `[]` either, and the "
        "callee is a `\\trusted` `val` with `ensures true`, so NO property of the "
        "argument is provable on either side. GUARD IS SPELLING-KEYED on the exact "
        "placeholder literal -- re-probe it whenever anything changes what `[]` lowers "
        "to (that is the route #192 shape).",
    ("_coerce_dotted_args", "self._coerce_to_int(arg)"):
        "the int-erasure bridge. THIS ENTRY'S FIRST VERSION WAS REFUTED ONE HOUR AFTER "
        "THIS PLANE LANDED, and the refutation is why the entry is worth reading. It said "
        "the bridge \"DECIDES nothing about the value ... and the receiving param is "
        "int-erased, so no law reads it\". A CONTRACT ON AN INT-ERASED PARAM IS A LAW "
        "THAT READS IT: route #194 gave a callee the TRUE contract `ensures p == 0 ==> "
        "\\result == 1` and called it with an array-shaped actual, which the bridge "
        "answered with the LITERAL `0` -- the collection discarded, the contract "
        "discharged, `\\result == 1` PROVED where CPython answers 2 (witness 1685). The "
        "array/map arms now answer Why3's `(any int)`, which stands for EVERY int and "
        "decides nothing. What remains here is the STRING/TUPLE hash (routes #113/#114): "
        "it is injective-by-luck only, and a caller cannot predict the hash it would have "
        "to name in a contract to exploit it -- but that is a claim about difficulty, not "
        "about soundness, so re-probe it if anything ever makes the hash predictable.",
    ("_coerce_dotted_args", "'(Array.make 0 (IrOther \"\"))'"):
        "THE EMPTY-LIST PLACEHOLDER into a `List[\"ExprIR\"]` param. Gated on the exact "
        "`(Array.make 1024 0)` literal, which is what `[]` lowers to, so the actual "
        "really IS the empty list and the genuinely EMPTY emit_ir array is the FAITHFUL "
        "value -- length 0 is the right answer, unlike route #193's length 1. Same "
        "spelling-keyed guard caveat as the `'0'` arm above.",
    ("_coerce_dotted_args", "f'(materialize_emit_ir {arg})'"):
        "a seq->array BRIDGE, not a substitution of value: `materialize_emit_ir` carries "
        "`Array.length result = Seq.length s` AND a pointwise `result[i] = Seq.get s i`, "
        "so the array is pinned element-by-element to the actual. Nothing is erased and "
        "no axiom is added.",
    ("_coerce_dotted_args", "f'(materialize_str {arg})'"):
        "the `array string` twin of the `materialize_emit_ir` bridge above; same "
        "length + pointwise laws.",
    ("_coerce_dotted_args", "f'(materialize {arg})'"):
        "the `array int` twin of the `materialize_emit_ir` bridge above; same "
        "length + pointwise laws.",
    ("_coerce_dotted_args", "self._array_coerce_arg(arg)"):
        "ROUTE #193's site. The placeholder for an iterable the IR could not represent "
        "is Why3's `any (array int)` -- it stands for EVERY array of ints, so neither "
        "its length nor its contents is decidable. It used to be `(Array.make 1 0)`, a "
        "DEFINITE length-1 array, and `sorted_1`'s `Array.length result = Array.length "
        "a` read that length (witness 1683).",
    ("_coerce_dotted_args", "'(any_map ())'"):
        "the map twin of route #193's answer, and it was fixed for the same reason one "
        "route earlier: this used to be `(const (None: option int))`, a DEFINITE EMPTY "
        "map, so a callee's `requires 1 not in d` discharged against it while the "
        "program passes a map containing 1. `any_map` is unconstrained and polymorphic, "
        "so nothing about the actual is decided.",
    ("_coerce_dotted_args", "f'(None: {ptype})'"):
        "ROUTE #192's site. An omitted / explicit `None` actual lifts into an "
        "`Optional[<record>]` parameter's `option` type -- the FAITHFUL value of that "
        "argument. Recognised by `pycsl_none` ONLY: the `\"0\"` spelling was dropped in "
        "#192, because after route #191 a `\"0\"` actual can only be a genuine integer "
        "and re-tagging it as `None` decided `start is None` wrongly (witness 1679).",
    ("_coerce_dotted_args", "f'(Some {_s})'"):
        "the other half of the `option <record>` lift: a PRESENT record actual is "
        "wrapped in `Some`. Gated on the actual being a bare local the emitter itself "
        "pre-declared with THIS record's default literal, so an int-erased or "
        "differently-typed actual is NOT re-tagged and fails LOUDLY.",
    ("_coerce_dotted_args", "f'({_none} : {ptype})' if _none else arg"):
        "ROUTE #192's `_union_*` twin: an omitted / explicit `None` actual becomes the "
        "synthesized union's own nullary `None` arm. Same `pycsl_none`-only recognition "
        "as the `option` lift above (witness 1680). Falls back to the unchanged actual "
        "when the union has no nullary arm, so it can only ever be faithful or loud.",
    ("_handle_struct_call", "self._coerce_to_int(arg)"):
        "the `struct`-packing twin of the int-erasure bridge; same reasoning as "
        "`_coerce_dotted_args`'s entry.",
    ("_call_bytes_methods", "self._array_coerce_arg(a)"):
        "a bytes method's array argument goes through route #193's repaired coercion, so "
        "an unrepresentable actual is `any (array int)` here too.",
    ("_call_bytes_methods", "self._coerce_to_int(a)"):
        "a bytes method's int argument goes through the int-erasure bridge; same "
        "reasoning as `_coerce_dotted_args`'s entry.",
}


def scan():
    """Every accumulator append in the tree, as (function, source, rel, lineno)."""
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
                for n in ast.walk(fu):
                    if not (isinstance(n, ast.Call)
                            and isinstance(n.func, ast.Attribute)
                            and n.func.attr == "append"
                            and len(n.args) == 1
                            and isinstance(n.func.value, ast.Name)
                            and n.func.value.id in ACCUMULATORS):
                        continue
                    src = ast.unparse(n.args[0])
                    hits.append((fu.name, src, os.path.relpath(p, ROOT), n.lineno))
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    hits = scan()
    if not hits:
        print("[!] argument-coercion: scanned 0 append site(s) in %s — that is not a "
              "measurement, the module path or the accumulator names are broken. "
              "NOT A PASS." % M6, file=sys.stderr)
        return 2

    subs = [h for h in hits if h[1] not in PASS_THROUGH]
    if not subs:
        print("[!] argument-coercion: %d append site(s) and NOT ONE substitution — the "
              "classifier is broken, a coercion path that substitutes nothing has never "
              "existed in this tree. NOT A PASS." % len(hits), file=sys.stderr)
        return 2

    keys = {(h[0], h[1]) for h in subs}
    unknown = [h for h in subs if (h[0], h[1]) not in BASELINE]
    stale = sorted(set(BASELINE) - keys)

    print("[*] argument-coercion: %d append site(s) — %d PASS-THROUGH, %d SUBSTITUTION."
          % (len(hits), len(hits) - len(subs), len(subs)))
    if args.verbose or unknown:
        for nm, src, rel, ln in sorted(subs):
            mark = "NEW " if (nm, src) not in BASELINE else "    "
            print("    %s%-24s %-46s %s:%d" % (mark, nm, src[:46], rel, ln))
            if (nm, src) in BASELINE:
                print("         %s" % BASELINE[(nm, src)])

    rc = 0
    for nm, src, rel, ln in unknown:
        print("[!] argument-coercion: %s:%d — `%s` substitutes `%s` for the caller's "
              "actual, and no entry in this gate's baseline says why the model gets to "
              "answer with it. PROBE IT END TO END: give the callee a contract that is "
              "TRUE of its own body and READS the substituted property, call it with an "
              "actual of the substituted-away shape, and run Python to confirm the true "
              "answer. Routes #192 and #193 are both exactly that probe."
              % (rel, ln, nm, src), file=sys.stderr)
        rc = 1
    for nm, src in stale:
        print("[!] argument-coercion: baseline entry (%s, %s) no longer matches any "
              "site. Remove it — a baseline that outlives its site hides the next one."
              % (nm, src), file=sys.stderr)
        rc = 1

    if rc == 0:
        print("[+] argument-coercion: OK — %d substitution(s), every one classified."
              % len(subs))
    return rc


if __name__ == "__main__":
    sys.exit(main())
