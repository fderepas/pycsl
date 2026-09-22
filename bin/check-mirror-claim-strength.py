#!/usr/bin/env python3
r"""L-PLANE ORACLE: what the VERIFIED half of the self-annotation mirror actually CLAIMS.

WHY THIS EXISTS (gen #30). Two numbers describe the mirror today. `count-trusted-directives`
says how many functions are trusted (459 directives), and `check-trust-blast-radius` says
how much of the rest DEPENDS on them (56%-61%). Neither asks the remaining question, which
is the one a reader assumes has been answered: of the functions that ARE proved, **what do
their contracts say?**

THE MEASUREMENT (gen #30), over every function definition in `src/self-annotate/src/`:

    1373 definitions
     440  (32%)  `#@ \trusted`            — assumed, not proved
     143  (10%)  a real `#@ ensures`      — a VALUE claim about the answer
     624  (45%)  `ensures True` + a real `#@ assigns` — a FRAME claim and nothing more
     166  (12%)  no `#@` clause at all    — of which 52 are NESTED (inner) functions and
                                            114 are module-level functions or methods

So of the 933 un-trusted functions, **143 — 15% — claim anything about the VALUE they
compute.** The other 790 are proved memory-safe and frame-correct (which is real, and is
what `assigns` buys), or carry nothing.

WHY THIS IS NOT A FAILURE, AND WHY IT IS STILL WORTH A GATE. `#@ assigns \nothing` over a
function that really assigns nothing is a true, useful, checkable claim, and the frame
plane family exists precisely to keep it honest. The point is arithmetic: "the mirror
verifies" is a sentence that a reader will hear as "the mirror's behaviour is specified",
and the specified-behaviour fraction is 15%, not 68%. The campaign has been careful to
report the trusted count; this reports the OTHER end of the same ledger.

THE RATCHETS: the real-`ensures` count may only GROW and the no-clause-at-all count may
only SHRINK. Both move the right way when a function gets a value contract, and neither is
affected by converting a `\trusted` marker — which is exactly why it is a separate gate
from the marker count.

THE POPULATION GUARD (the #44 rule): rc=2 below MIN_DEFS definitions.

Usage:  bin/check-mirror-claim-strength.py [--verbose] [--list CLASS]
"""
import argparse
import ast
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
MIN_DEFS = 1200             # 1373 at the first measurement
MIN_REAL_ENSURES = 143      # first measurement; may only grow
MAX_NO_CLAUSE = 166         # first measurement; may only shrink

TRUSTED, VALUE, FRAME, NONE = "trusted", "value", "frame", "none"


def classify():
    out = []
    for f in sorted(glob.glob(os.path.join(MIRROR, "**", "*.py"), recursive=True)):
        src = open(f, errors="replace").read()
        lines = src.split("\n")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        parent = {}
        for p in ast.walk(tree):
            for ch in ast.iter_child_nodes(p):
                parent[ch] = p
        for n in ast.walk(tree):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            ann, i = [], n.lineno - 2
            while i >= 0 and (not lines[i].strip() or lines[i].strip().startswith("#")):
                if lines[i].strip().startswith("#@"):
                    ann.append(lines[i].strip())
                i -= 1
            nested, p = False, parent.get(n)
            while p is not None:
                if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    nested = True
                    break
                p = parent.get(p)
            if any("\\trusted" in a for a in ann):
                cls = TRUSTED
            elif any(re.match(r"#@\s*ensures\s", a)
                     and not re.match(r"#@\s*ensures\s+True\s*$", a) for a in ann):
                cls = VALUE
            elif any(re.match(r"#@\s*(assigns|requires)\s", a) for a in ann):
                cls = FRAME
            else:
                cls = NONE
            out.append((cls, f, n.name, nested))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--list", choices=[TRUSTED, VALUE, FRAME, NONE],
                    help="print the members of one class")
    args = ap.parse_args()

    rows = classify()
    total = len(rows)
    if total < MIN_DEFS:
        print("[!] mirror-claim-strength: REFUSING — %d definition(s) found, expected at "
              "least %d. The walk is broken; this is not a pass." % (total, MIN_DEFS),
              file=sys.stderr)
        return 2

    counts = {c: sum(1 for r in rows if r[0] == c) for c in (TRUSTED, VALUE, FRAME, NONE)}
    nested_none = sum(1 for r in rows if r[0] == NONE and r[3])
    untrusted = total - counts[TRUSTED]

    print("[*] mirror-claim-strength: %d definition(s) — %d `\\trusted` (%.0f%%), %d with "
          "a VALUE claim (%.0f%%), %d with only a FRAME claim (%.0f%%), %d with no clause "
          "at all (%.0f%%, of which %d nested)."
          % (total, counts[TRUSTED], 100.0 * counts[TRUSTED] / total,
             counts[VALUE], 100.0 * counts[VALUE] / total,
             counts[FRAME], 100.0 * counts[FRAME] / total,
             counts[NONE], 100.0 * counts[NONE] / total, nested_none))
    print("[*] mirror-claim-strength: of the %d UN-trusted function(s), %d (%.0f%%) say "
          "something about the VALUE they compute."
          % (untrusted, counts[VALUE], 100.0 * counts[VALUE] / max(untrusted, 1)))

    if args.list:
        for cls, f, name, nested in sorted(rows):
            if cls == args.list:
                print("    %s::%s%s" % (os.path.relpath(f, ROOT), name,
                                        "  (nested)" if nested else ""))

    rc = 0
    if counts[VALUE] < MIN_REAL_ENSURES:
        print("[!]   VALUE-CLAIM FLOOR BROKEN: %d < %d. A function lost its real "
              "postcondition." % (counts[VALUE], MIN_REAL_ENSURES), file=sys.stderr)
        rc = 1
    if counts[NONE] > MAX_NO_CLAUSE:
        print("[!]   NO-CLAUSE CEILING BROKEN: %d > %d. A new mirror function carries no "
              "`#@` clause at all." % (counts[NONE], MAX_NO_CLAUSE), file=sys.stderr)
        rc = 1

    if rc:
        print("[!] mirror-claim-strength: NOT OK.", file=sys.stderr)
    else:
        print("[+] mirror-claim-strength: OK — value-claim floor %d (at %d), no-clause "
              "ceiling %d (at %d)."
              % (MIN_REAL_ENSURES, counts[VALUE], MAX_NO_CLAUSE, counts[NONE]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
