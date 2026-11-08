#!/usr/bin/env python3
"""check-collapsed-option-reads — the 31st plane.

WHY IT EXISTS. Three routes in this campaign are ONE defect wearing three hats:

    #44   `None` was the integer 0
    #56   a `None` Optional-union LOCAL read back as the carrier's zero
    #57   `d.get(k)` on a missing key read back as the codomain's zero

Every one of them has the SAME shape, and it is worth stating precisely because it is
counter-intuitive: **THE STORAGE WAS FAITHFUL AND THE READ WAS NOT.** The model really
does carry a distinct absent value — `map 'k (option 'v)` with a genuine `None`, or a
variant with a real `Arm_*_None` constructor — and then a `match … | None -> <literal>`
arm throws it away at the point of use. A reader auditing the REPRESENTATION finds it
faithful and concludes the class is safe; the erasure is one level down, in the read.

This plane enumerates every emitted `| None ->` arm that answers a LITERAL VALUE, and
requires each to be classified. It deliberately does NOT enumerate all ~353 `| None ->`
arms: the overwhelming majority answer a None-PRESERVING form — `()`, `false`, `PNone`,
`IrSNone`, a `const false` map — which is the faithful pattern the tree already uses in
`stmt_control_flow` ("option preserves None-propagation instead of the scalar
`None -> 0` default", `stmt_control_flow.py:2662`). Listing those would bury the ten that
matter, and a plane that cries wolf is a plane that gets ignored.

VERDICTS
  COLLAPSING-OPEN    the arm answers a value and that value is observable. A ROUTE.
  COLLAPSING-DEAD    the arm answers a value but is provably unreachable, and the
                     ARGUMENT for that must be stated — naming the exception or guard that
                     makes it dead. "It looks unreachable" is not an argument.
  FAITHFUL           the arm answers an opaque or a None-preserving constructor.
  UNPROBED           found, not yet measured. Allowed, but it must say what would reach it.

EXIT CODES
  0  every site classified, every classified site found
  1  an UNCLASSIFIED site, or a STALE entry matching no site
  2  refusal: fewer than MIN_SITES scanned (the #44 rule)
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M6 = os.path.join(ROOT, "src", "pycsl", "module6_whyml")

# An option-read arm answering a LITERAL value (not a constructor, not an opaque).
ARM = re.compile(r'\|\s*None\s*->\s*(0\.0|0|""|\(HInt 0\)|\(IrOther ""\))[\s)]')

MIN_SITES = 8

BASELINE = {
    ("expr_ghost_collections.py", "0"):
        "FAITHFUL — and it is the instructive one, because it is the SAME SHAPE as route "
        "#57 and is SOUND. `_handle_map_get_expr` lowers the GHOST contract builtin "
        "`\\map_get(d, k)` (surface syntax at `Module2_Parser.py:2274`), and answering 0 "
        "for an absent key is its DEFINED SEMANTICS, documented on two normative surfaces: "
        "`docs/pycsl-concrete-syntax-reference.md:525` (\"Returns the value stored at key "
        "`k` in dict `d`, or 0 if absent\") and `test-suite/annotations.md:1590`/`:1765`, "
        "the latter spelling out this exact WhyML. **THE DISTINCTION THAT MATTERS: a ghost "
        "SPEC construct may DEFINE its absent-key answer, because it is a spec-language "
        "primitive with no Python counterpart to contradict. A BODY lowering may not, "
        "because there the absent value is Python's `None` and answering 0 makes a false "
        "claim about a real program.** Route #57 is the same `| None -> 0` in the second "
        "position, undocumented and contradicting `.get`. Probed by relaunch #51: the two "
        "reachable spec shapes fail closed anyway.",
    ("expressions.py", "(HInt 0)"):
        "COLLAPSING-DEAD, ARGUMENT STATED: the `hval` value model's absent-key sentinel. "
        "`hval` is a TAGGED union (HInt/HStr/...), so an `(HInt 0)` answer is "
        "distinguishable from an absent value only if something reads the tag; the "
        "hval-value-model wall is a recorded certified boundary of this campaign. "
        "RE-MEASURED IN gen #30, and the answer SPLITS -- so \"COLLAPSING-DEAD\" above "
        "is only half right. CORPUS SIDE: the comparison point this entry named is NOT "
        "REACHABLE from ordinary Python. You cannot get a genuine `HInt 0` into the dict "
        "-- an int store into a `Dict[str, PyVal]` is an L3-tc error (`This expression "
        "has type int, but is expected to have type hval`) -- and `isinstance(v, int)` on "
        "the read does not reach the `_pyval_locals` arm either. The sentinel IS emitted, "
        "and the generated WhyML was read to confirm it: `let v = (match Map.get !d "
        "\"zzz\" with | Some v_ -> v_ | None -> (HInt 0) end)`. MIRROR SIDE, AND THIS "
        "PART IS NOT CLOSED: the 53-file mirror emission contains 30 GENUINE `HInt i` "
        "constructions, so a present-with-value-0 hval really is constructible there and "
        "really is indistinguishable from the absent sentinel. Nothing measured shows a "
        "mirror proof that DEPENDS on telling them apart, and nothing shows one does not. "
        "The honest label for the mirror side is therefore NOT \"collapsing-dead\" but "
        "\"no reader found yet\". NEXT STEP, named so it is not re-derived: find a "
        "mirror method whose contract distinguishes an absent key from a present 0 -- a "
        "`.get` guard followed by a value use -- and probe THAT.",
    ("generic_fold.py", '""'):
        "COLLAPSING-DEAD, ARGUMENT STATED: the generated ADT-fold helpers "
        "(`<C>_gtype` / `<C>_gop`) read a term's type/op tag out of an option and answer "
        "the empty string when absent. These are GENERATED accessors over a total "
        "inductive whose every constructor sets the field, so the `None` arm is "
        "unreachable by construction of the generator, not by a guard on the program. If "
        "the generator ever emits a constructor that omits the field, this becomes live.",
}


def scan():
    sites = []
    for fn in sorted(os.listdir(M6)):
        if not fn.endswith(".py"):
            continue
        path = os.path.join(M6, fn)
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            if line.lstrip().startswith("#"):
                continue          # a comment describing the shape is not the shape
            for m in ARM.finditer(line):
                sites.append((fn, m.group(1), i))
    return sites


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(M6):
        print(f"[!] collapsed-option-reads: {M6} is not a directory. NOT A PASS.")
        return 2

    sites = scan()
    if len(sites) < MIN_SITES:
        print(f"[!] collapsed-option-reads: only {len(sites)} site(s) scanned, expected at "
              f"least {MIN_SITES}. The module path or the recognizer is broken. THIS IS A "
              f"REFUSAL, NOT A PASS.")
        return 2

    seen, unclassified = set(), []
    for (fn, lit, line) in sites:
        key = (fn, lit)
        seen.add(key)
        if key not in BASELINE:
            unclassified.append((fn, lit, line))
        elif args.verbose:
            print(f"    ok   {fn}:{line}  | None -> {lit}")
            print(f"         {BASELINE[key]}")

    stale = [k for k in BASELINE if k not in seen]
    open_n = sum(1 for k in BASELINE if k in seen
                 and BASELINE[k].startswith(("COLLAPSING-OPEN", "UNPROBED")))

    if unclassified or stale:
        for (fn, lit, line) in unclassified:
            print(f"[-] UNCLASSIFIED collapsed option read: {fn}:{line}  | None -> {lit}")
            print( "      An option read that answers a literal THROWS AWAY a distinction")
            print( "      the model was carrying faithfully. Classify it, and if you call")
            print( "      it DEAD, state the exception or guard that makes it dead.")
        for k in stale:
            print(f"[-] STALE baseline entry (matches no site): {k}")
        print(f"[!] collapsed-option-reads: {len(unclassified)} unclassified, "
              f"{len(stale)} stale, over {len(sites)} site(s).")
        return 1

    print(f"[+] collapsed-option-reads: OK — {len(sites)} site(s) over "
          f"{len(seen)} distinct (file, literal) class(es), every one classified "
          f"({open_n} still OPEN/UNPROBED).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
