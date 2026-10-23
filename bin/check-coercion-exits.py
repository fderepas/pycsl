#!/usr/bin/env python3
r"""L-PLANE ORACLE: every value the two COERCION helpers can return.

WHY THIS EXISTS — the campaign's own trigger rule (lesson (d)), fired a third time.
`bin/check-argument-coercion.py` classifies the `coerced.append(...)` SITES of
`_coerce_dotted_args`. It does not look inside the two helpers those sites delegate to,
and BOTH of them produced two routes each:

  `_array_coerce_arg`
    * ROUTE #193 — the `stripped == "0"` arm answered `(Array.make 1 0)`, a placeholder
      with a KNOWN LENGTH 1, so `len(sorted(x for x in [3,1,2]))` PROVED `== 1`.
    * ROUTE #201 — the function's TAIL answered the same placeholder, and a STRING literal
      reaches it, so a callee declaring `p: List[int]` and reading `len(p)` PROVED a
      contract CPython refutes.

  `_coerce_to_int`
    * ROUTE #194 — the array/map arms answered the literal `0`, and an int-erased param's
      contract read it.
    * ROUTES #200/#202 — the string arm answers `stable_hash(<literal>)`, and the hash is
      computable from this repository, so a callee contract that NAMES that integer
      decides. Closed at Module 4 rather than here, and this gate records the condition
      that keeps the arm sound.

THE SHARED SHAPE, and the reason one gate covers both: these helpers answer a value for an
actual they could not represent. Every such answer is either FAITHFUL (the value really is
that), OPAQUE (`any`, which decides nothing) or a PASS-THROUGH. A LITERAL that is none of
those is a claim about a value the emitter does not have — which is what both routes were.

WHAT IT MEASURES. Every `return` in the two functions, keyed on source text, WITH ITS
OCCURRENCE COUNT. A new return with no justification FAILS; a count that moves FAILS; a
justification whose return is gone is reported STALE. The count matters here more than
anywhere: `return whyml_str` appears three times in one function and twice in the other,
and they are pass-throughs for five different reasons.

WHAT IT DOES NOT CHECK: whether an opaque is the RIGHT opaque (value-keyed vs fresh), and
whether a pass-through is type-correct at its use site. The witnesses cover the first
(1684, 1690, 1700) and Why3's own typing covers the second.

Usage:  bin/check-coercion-exits.py [--verbose] [--live DIR]
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "src", "pycsl", "module6_whyml")
FUNCS = ("_array_coerce_arg", "_coerce_to_int")

# (function, return-source) -> (occurrences, why this answer is not a claim about a value
#                               the emitter does not have)
JUSTIFIED = {
    ("_array_coerce_arg", "'(any (array int))'"): (2,
        "(#49) ROUTES #193 and #201. TWO exits, and they are the two that used to answer "
        "`(Array.make 1 0)` — a placeholder with a KNOWN LENGTH. `any` stands for EVERY "
        "array of ints, so neither length nor contents is decidable. Declaration-free on "
        "purpose: declaring an abstract op would make this a non-static method and its "
        "mirror is a CONVERTED method with `assigns \\nothing` (#193's first repair did "
        "exactly that and turned three fidelity planes red)."),
    ("_array_coerce_arg", "whyml_str"): (3,
        "PASS-THROUGH, three exits: an already-array-shaped expression (`Array.make`, "
        "`Array.get`, `sorted_1`, `list_new`, `any_1`, `all_1`); a bare identifier or "
        "dotted field read (the callee's responsibility, and clobbering it would sever a "
        "field from its representation invariant); and a function application in an array "
        "slot (`(pack16 x)`, `(materialize !s)`), where clobbering broke "
        "`unpack(pack(x)) == x`. A pass-through makes no claim."),
    ("_coerce_to_int", "'(any int)'"): (3,
        "(#49) ROUTES #194 and #115/#116's descendants. The array-shaped arm, the "
        "map-shaped arm and the genuine-TUPLE arm. Each used to answer a literal or a "
        "hash of the text; none of them has an int that represents the value, so the "
        "honest answer is the one that decides nothing."),
    ("_coerce_to_int", "whyml_str"): (2,
        "PASS-THROUGH: a paren-wrapped APPLICATION or binder whose head token is an "
        "ordinary identifier (route #110's lesson — seven of the emitter's own minted "
        "spellings are ordinary Python identifiers, so a user who NAMES a function "
        "`any_1` must not have its call replaced), and the final fall-through. "
        "Fail-closed: a non-int term passed through is a Why3 type error, not an answer."),
    ("_coerce_to_int", "str(stable_hash(whyml_str))"): (1,
        "THE STRING-LITERAL HASH, and the one exit here that is a SUBSTITUTION rather "
        "than a faithful value or an opaque. Routes #200/#202 showed it is decidable when "
        "a callee's contract can NAME the integer, and that is closed at Module 4 "
        "(`PYCSL-SEM-STRARG`) rather than here, because the emitter's own 46 "
        "erased-parameter sites depend on this arm. THE STANDING CONDITION: this exit is "
        "sound exactly while no actual reaching it can be named by a contract the CALLER "
        "can use. If a new call shape ever delivers a string literal to a contract-read "
        "parameter through a slot the Module 4 refusal does not walk, this entry is false."),
}


def returns(live=None):
    live = live or LIVE
    out = []
    for fn in sorted(os.listdir(live)):
        if not fn.endswith(".py"):
            continue
        try:
            tree = ast.parse(open(os.path.join(live, fn)).read())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in FUNCS:
                for m in ast.walk(node):
                    if isinstance(m, ast.Return) and m.value is not None:
                        try:
                            out.append((node.name, ast.unparse(m.value), fn, m.lineno))
                        except Exception:
                            out.append((node.name, "<unparseable>", fn, m.lineno))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--live", default=None,
                    help="scan this module6_whyml directory instead of the live one — the "
                         "self-test hook (lesson (q): a gate built from a route must be "
                         "run against the pre-route tree)")
    args = ap.parse_args()

    found = returns(args.live)
    if not found:
        print("[!] coercion-exits: REFUSING — ZERO returns found in %s. The functions were "
              "renamed or the walk is broken; this is not a pass." % (", ".join(FUNCS)),
              file=sys.stderr)
        return 2

    from collections import Counter
    seen = Counter((f, src) for f, src, _fn, _l in found)
    unjustified = sorted(k for k in seen if k not in JUSTIFIED)
    stale = sorted(k for k in JUSTIFIED if k not in seen)
    moved = sorted((k, JUSTIFIED[k][0], seen[k]) for k in seen
                   if k in JUSTIFIED and JUSTIFIED[k][0] != seen[k])

    if args.verbose:
        for f, src, fn, ln in sorted(found, key=lambda r: (r[0], r[3])):
            print("    %s %-20s %s:%d  return %s"
                  % ("ok " if (f, src) in JUSTIFIED else "NEW", f, fn, ln, src[:56]))

    print("[*] coercion-exits: %d return(s) across %d function(s), %d distinct, "
          "%d justified." % (len(found), len(FUNCS), len(seen),
                             len(seen) - len(unjustified)))

    rc = 0
    for k in stale:
        print("[!]   STALE justification (no such return any more): %s" % (k,), file=sys.stderr)
        rc = 1
    for k in unjustified:
        print("[!]   UNJUSTIFIED coercion exit: %s" % (k,), file=sys.stderr)
        rc = 1
    for k, want, got in moved:
        print("[!]   COUNT MOVED for %s: baseline %d, found %d. These helpers answer a "
              "value for an actual they could not represent; a new exit sharing an old "
              "justification is how routes #193/#194/#201 all happened."
              % (k, want, got), file=sys.stderr)
        rc = 1
    if rc:
        print("[!] coercion-exits: NOT OK — every value these helpers return must be "
              "FAITHFUL, OPAQUE or a PASS-THROUGH, and classified here.", file=sys.stderr)
    else:
        print("[+] coercion-exits: OK — every coercion exit is justified.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
