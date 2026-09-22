#!/usr/bin/env python3
r"""L-PLANE ORACLE: every value `_handle_fstring_expr` can return.

WHY THIS EXISTS, and it is the campaign's own trigger rule rather than a hunch. Lesson (d)
says: BUILD THE PLANE WHEN TWO ROUTES LAND IN ONE FUNCTION IN ONE DAY. Two did, in one
session:

  * ROUTE #199 — the EMPTY f-string (`f""`, no segments) answered the integer `0`, so
    `s = f""` then `s == ""` DECIDED FALSE and a contract false of CPython PROVED.
  * ROUTE #203 — a SINGLE-PART f-string (`f"{n}"`, no literal text) returned the part
    ITSELF, so `s == "5"` compared `5` against `stable_hash('"5"')` and DECIDED FALSE.

Both are the same defect in the same function: **an f-string that is not a string.** An
f-string is a STRING in Python, always; every value this handler returns must therefore be
something that behaves like one in the model it is returning into — a Why3 `string`, a
string-valued abstract op, or a value in the int-hash string domain. What is NOT allowed is
a raw operand or a bare literal that a comparison against a string can DECIDE against.

WHAT IT MEASURES. Every `return` in `_handle_fstring_expr`, keyed on its source text, with
an occurrence count. A NEW return with no justification FAILS; a count that moves FAILS; a
justification whose return has disappeared is reported STALE. The count is load-bearing for
the same reason it is in `bin/check-return-boundary-substitutions.py`: a justification
covers the returns it was written for and no others, and route #203's raw `return acc` is
textually identical to two OTHER `return acc`s in the same function that are perfectly
sound.

AND ONE STRUCTURAL PIN, because the RETURN SET ALONE DOES NOT SEE ROUTE #203. That route
did not add or change an exit: it added a WRAP before an exit whose source text
(`return acc`) was already there and already justified. Run against the pre-#203 tree, the
return-set half of this gate is GREEN — measured, not assumed, via `--live`. So the gate
also pins the two tokens that make the int-model joiner's single-part case sound:
`len(parts) == 1` and `str_of_int_hash`. That is a crude structural check and it is
labelled as one; its job is to fail when the wrap is deleted, which is the only way #203
comes back.

>>> A GATE BUILT FROM A ROUTE MUST BE RUN AGAINST THE PRE-ROUTE TREE. This one passed
>>> there on its first design, which is how the blind spot was found rather than shipped.

WHAT IT DOES NOT CHECK, stated rather than implied:
  * whether the value is CORRECT — only that every exit is classified and that the set of
    exits has not changed silently. A wrong-but-classified answer is this plane's blind
    spot, and the witnesses (1695/1696, 1705/1706) are what cover that.
  * the OTHER string builders (`str()`, `%`, `.join`, `+`). Each was probed this session
    and found fail-closed, and each has its own handler; this plane is scoped to the one
    function that produced two routes.

Usage:  bin/check-fstring-lowering.py [--verbose] [--live DIR]
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "src", "pycsl", "module6_whyml")
FN = "_handle_fstring_expr"

# return-source -> (occurrences, why this exit is a STRING and not a decidable non-string)
JUSTIFIED = {
    "str(stable_hash('\"\"'))": (1,
        "(#49) ROUTE #199 — the EMPTY f-string. `f\"\"` IS the empty string, and in the "
        "int-hash string model the empty string IS `stable_hash('\"\"')` — the very "
        "constant the comparison emits. Answering it closes the false proof AND makes the "
        "TRUE contract provable (witnesses 1695/1696). Not an opaque: the value is "
        "available and exact here."),
    "acc": (3,
        "the ACCUMULATED string. Three exits share this text and all three are sound, each "
        "for its own reason: the all-string concat chain (`str_concat_op`/`concat`), the "
        "`@mutable_state` / `-> str` chain (`int_to_string` + `str_concat_op`), and the "
        "int-model joiner — which is sound ONLY because ROUTE #203 added the "
        "`len(parts) == 1` wrap. Before #203 the third one returned the part itself and "
        "`f\"{n}\"` WAS the integer `n` (witnesses 1705/1706). THE COUNT IS THE GUARD: a "
        "fourth `return acc` would be a new exit sharing a justification written for "
        "three others."),
    "f'(str_hash_op {_w})'": (1,
        "a STRING-typed part folded into the int-hash domain by the declared "
        "`val str_hash_op (s: string) : int`. Opaque: no literal's hash is provably equal "
        "to it."),
    "_w": (1,
        "a NON-string part passed through into the int-hash domain. Sound only as an "
        "ARGUMENT of the joiner: every multi-part f-string wraps it in `val str_concat "
        "(x: int) (y: int) : int`, which has no axioms, and the SINGLE-part case is "
        "wrapped by route #203's `str_of_int_hash`. If a caller of `_part` is ever added "
        "that does neither, this entry is false — that is exactly how #203 happened."),
}


# Tokens that MUST appear in the function's source. Each is the load-bearing half of a
# repair whose deletion would reopen a route without changing the return set.
REQUIRED_TOKENS = {
    "len(parts) == 1":
        "(#49) ROUTE #203's SCOPE. The wrap must fire only for a single-part f-string; "
        "wrapping every part would change what `str_concat` receives and move every "
        "multi-part f-string in the mirror (575 of them).",
    "str_of_int_hash":
        "(#49) ROUTE #203's ANSWER. The value-keyed opaque that makes `f\"{n}\"` not be "
        "`n`. `val function`, so two equal `n`s give equal strings (witness 1706); an "
        "`any` would be fresh at every evaluation and would lose that while still passing "
        "witness 1705.",
}


def source_of(live=None):
    live = live or LIVE
    for fn in sorted(os.listdir(live)):
        if not fn.endswith(".py"):
            continue
        try:
            src = open(os.path.join(live, fn)).read()
            tree = ast.parse(src)
        except SyntaxError:
            continue
        lines = src.split("\n")
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == FN:
                return "\n".join(lines[node.lineno - 1:node.end_lineno])
    return None


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
            if isinstance(node, ast.FunctionDef) and node.name == FN:
                for m in ast.walk(node):
                    if isinstance(m, ast.Return) and m.value is not None:
                        try:
                            out.append((fn, ast.unparse(m.value), m.lineno))
                        except Exception:
                            out.append((fn, "<unparseable>", m.lineno))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--live", default=None,
                    help="scan this module6_whyml directory instead of the live one "
                         "(the self-test hook: run it against a pre-repair checkout and "
                         "watch this gate go red)")
    args = ap.parse_args()

    found = returns(args.live)
    # THE ZERO-CHECK REFUSAL (the #44 rule): a gate that cannot tell "nothing is wrong"
    # from "I looked at nothing" is not a gate.
    if not found:
        print("[!] fstring-lowering: REFUSING — ZERO returns found in %s. The function was "
              "renamed or the walk is broken; this is not a pass." % FN, file=sys.stderr)
        return 2

    from collections import Counter
    seen = Counter(src for _f, src, _l in found)
    unjustified = sorted(s for s in seen if s not in JUSTIFIED)
    stale = sorted(s for s in JUSTIFIED if s not in seen)
    moved = sorted((s, JUSTIFIED[s][0], seen[s]) for s in seen
                   if s in JUSTIFIED and JUSTIFIED[s][0] != seen[s])

    if args.verbose:
        for f, src, ln in sorted(found, key=lambda r: r[2]):
            print("    %s %s:%d  return %s"
                  % ("ok " if src in JUSTIFIED else "NEW", f, ln, src[:70]))

    print("[*] fstring-lowering: %d return(s) from %s, %d distinct, %d justified."
          % (len(found), FN, len(seen), len(seen) - len(unjustified)))

    rc = 0
    body = source_of(args.live)
    if body is None:
        print("[!] fstring-lowering: REFUSING — could not read %s's source." % FN,
              file=sys.stderr)
        return 2
    for tok in sorted(REQUIRED_TOKENS):
        if tok not in body:
            print("[!]   MISSING STRUCTURAL TOKEN %r — %s"
                  % (tok, REQUIRED_TOKENS[tok]), file=sys.stderr)
            rc = 1
    for s in stale:
        print("[!]   STALE justification (no such return any more): %r" % (s,), file=sys.stderr)
        rc = 1
    for s in unjustified:
        print("[!]   UNJUSTIFIED f-string exit: %r" % (s,), file=sys.stderr)
        rc = 1
    for s, want, got in moved:
        print("[!]   COUNT MOVED for %r: baseline %d, found %d. An f-string is a STRING in "
              "Python, always — a new exit sharing an old justification is how routes #199 "
              "and #203 both happened." % (s, want, got), file=sys.stderr)
        rc = 1
    if rc:
        print("[!] fstring-lowering: NOT OK — every value this handler returns must be "
              "classified here.", file=sys.stderr)
    else:
        print("[+] fstring-lowering: OK — every f-string exit is justified.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
