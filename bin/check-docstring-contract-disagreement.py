#!/usr/bin/env python3
r'''L-PLANE ORACLE: a `pycsl_lib` function whose DOCSTRING states a WEAKER relation than
the `#@ ensures \result ==` clause sitting directly above it.

WHY THIS EXISTS (gen #30, wall-lesson (g3)). Adjudicating the 24 UNADJUDICATED entries of
`check-stdlib-identity-stubs.py` turned up seven stubs whose contract is FALSE of the
function their own header cites. TWO OF THE SEVEN HAD ALREADY SAID SO IN THEIR OWN PROSE:

    #@ ensures \result == num_fields
    def write_row(num_fields: int) -> int:
        """RST: 'writer... converting data into delimited strings.'
        Written bytes >= field count."""        # <-- ">=", and the clause pins "=="

    #@ ensures \result == default
    def context_var_get(default: int) -> int:
        """Get context variable value (returns default if not set)."""
                                                # <-- "if not set", and the clause is
                                                #     UNCONDITIONAL

Whoever wrote the prose knew the shape of the truth and then wrote a stronger clause
anyway. The divergence was sitting in the file and needed no CPython at all — so the
oracle is FREE, and it was being thrown away. A reader who is proving things sees the
clause, not the qualification above it.

WHAT IT MEASURES. Every function under `src/pycsl_lib/` that carries an EQUALITY pin
(`#@ ensures \result == ...`) and whose docstring matches one of the WEAKENING markers
(`>=`, `<=`, "at least", "at most", "if not set", "may", "approximate", "or more",
"roughly", "not guaranteed", "upper/lower bound"). Keyed on (package, function).

THE POPULATION IS 7, AND FOUR OF THEM ARE CONTROLS — which is the point. A marker-hunting
gate whose every hit is a defect is a gate that has not met an innocent case yet, and the
innocent cases here are structural, not accidental: `oper.le` / `oper.ge` quote the RST
line "Return a <= b", where the `<=` IS THE MODELLED RELATION and the contract is an exact,
guarded case split; `token.ISNONTERMINAL` says "type >= NT_OFFSET (256)", which is the
BRANCH CONDITION its own `ensures` pair discharges exactly; `os._encode_name` says "a name
of <= 30 chars round-trips exactly", which is its `requires` being EXPLAINED, so the prose
AGREES with the clause. A weakening word inside a quoted relation, a branch condition, or a
restatement of the guard is not a weakening OF THE CLAIM. Each of the four is baselined
with which of those three it is, so a future hit has to be argued against them.

AND THE GATE FOUND A THIRD DEFECT THE HAND PASS MISSED. `que.Queue.qsize` pins
`\result == self._size` under a docstring quoting "Return the APPROXIMATE size of the
queue" — CPython's own word, and it is approximate because another thread may add or remove
between the call and the answer. The model has no threads, so the exact claim is true OF
THE MODEL; nothing in the file says the model has no threads. Same defect as `os.getenv`,
whose empty-env justification lives in a comment: an UNDECLARED modelling assumption
holding up an exact clause.

CLASSES. `DISAGREES` — the prose is right and the clause over-claims. `QUOTED-RELATION` /
`BRANCH-CONDITION` / `GUARD-RESTATED` — the three innocent shapes above.

THE RATCHET is the set of (package, function) hits. A NEW one fails: it must be argued into
a class. One that DISAPPEARS is reported so its entry goes with it. There is no debt
counter and no ceiling, because a DISAGREES entry is not a debt to be capped — it is a
contract to be weakened or a modelling assumption to be declared, and the three standing
ones are named in `getting-better/driver-handoff-latest.md`.

THE POPULATION GUARD (the #44 rule): rc=2 if the walk sees fewer than MIN_FUNCTIONS
functions or fewer than MIN_PINS equality pins, so "no disagreements" can never mean
"I parsed nothing" or "I matched nothing".

TWO SELF-TESTS, because one would only prove half of it. `--selftest-empty-baseline` must
exit 1: it proves the gate BITES on its own population. `--selftest-no-markers` empties the
WEAKENER list and must find nothing: it proves the MATCHER is what produces the hits, not
the baseline dict agreeing with itself.

Usage:  bin/check-docstring-contract-disagreement.py [--verbose]
                                                    [--selftest-empty-baseline]
                                                    [--selftest-no-markers]
'''
import argparse
import ast
import glob
import os
import re
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "src", "pycsl_lib")
MIN_FUNCTIONS = 800   # 870 at the first measurement
MIN_PINS = 200        # equality pins found; the matcher must keep matching

# A word that WEAKENS a claim, when it appears in prose next to an equality pin.
WEAKENERS = [
    r">=", r"<=", r"\bat least\b", r"\bat most\b", r"\bif not set\b", r"\bmay\b",
    r"\bapproximat", r"\bor more\b", r"\broughly\b", r"\bnot guaranteed\b",
    r"\bupper bound\b", r"\blower bound\b",
]

DISAGREES = "DISAGREES"
QUOTED = "QUOTED-RELATION"
BRANCH = "BRANCH-CONDITION"
GUARD = "GUARD-RESTATED"

BASELINE = {
    ("csvmod", "write_row"): (DISAGREES,
        "Docstring: 'Written bytes >= field count.' Clause: `ensures \\result == "
        "num_fields`. MEASURED on an `io.StringIO`: `csv.writer(sio).writerow("
        "['a','b','c'])` returns 7 — the CHARACTER count — so the docstring is right and "
        "the clause over-claims. Also DIVERGES-BY-HAND in check-stdlib-identity-stubs."),
    ("cvar", "context_var_get"): (DISAGREES,
        "Docstring: 'returns default if not set.' Clause: `ensures \\result == default`, "
        "UNCONDITIONAL. MEASURED: after `cv.set(5)`, `cv.get(0)` is 5. Also "
        "DIVERGES-BY-HAND in check-stdlib-identity-stubs."),
    ("que", "qsize"): (DISAGREES,
        "Docstring quotes CPython's own word: 'Return the APPROXIMATE size of the queue.' "
        "Clause: `ensures \\result == self._size`, exact. `queue.Queue.qsize` is "
        "approximate because another thread may add or remove between the call and the "
        "answer; this model has no threads, so the exact claim is true OF THE MODEL and "
        "NOTHING IN THE FILE SAYS SO. The same undeclared-assumption shape as `os.getenv`, "
        "whose empty-env justification lives in a comment. CLOSING IT = declare the "
        "single-threaded model in the contract's own terms, or weaken the clause. FOUND BY "
        "THIS GATE, not by the hand pass that preceded it."),
    ("oper", "le"): (QUOTED,
        "Docstring is the RST line 'Return a <= b.' The `<=` IS THE MODELLED RELATION, and "
        "the contract is an exact guarded case split (`a <= b ==> \\result == 1`, "
        "`a > b ==> \\result == 0`). Nothing is weakened."),
    ("oper", "ge"): (QUOTED, "The mirror image of `le`; 'Return a >= b.'"),
    ("token", "ISNONTERMINAL"): (BRANCH,
        "Docstring: 'Non-terminal tokens have type >= NT_OFFSET (256).' That `>=` is the "
        "BRANCH CONDITION, and the `ensures` pair discharges both sides of it exactly "
        "(`tok_type >= 256 ==> \\result == 1`, `tok_type < 256 ==> \\result == 0`)."),
    ("os", "_encode_name"): (GUARD,
        "Docstring: 'a name of <= 30 chars round-trips exactly'. That is the stub's OWN "
        "`requires \\str_length(name) <= 30` being EXPLAINED, so the prose AGREES with the "
        "clause. A restatement of the guard is not a weakening of the claim."),
}


def census():
    """Every (package, function) with an equality pin whose docstring carries a weakener.
    Pure AST plus the annotation comment block; nothing is imported or called."""
    hits, functions, pins = [], 0, 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for path in sorted(glob.glob(os.path.join(LIB, "**", "*.py"), recursive=True)):
            src = open(path, encoding="utf-8", errors="replace").read()
            lines = src.splitlines()
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            pkg = os.path.basename(os.path.dirname(path))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                functions += 1
                ann, i = [], node.lineno - 2
                while i >= 0 and (not lines[i].strip() or lines[i].strip().startswith("#")):
                    if lines[i].strip().startswith("#@"):
                        ann.append(lines[i].strip())
                    i -= 1
                if not any(re.search(r"ensures\s+\\result\s*==", a) for a in ann):
                    continue
                pins += 1
                doc = ast.get_docstring(node) or ""
                for w in WEAKENERS:
                    if re.search(w, doc, re.I):
                        hits.append((pkg, node.name, w,
                                     " ".join(doc.split())[:100]))
                        break
    return hits, functions, pins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest-empty-baseline", action="store_true",
                    help="run with an EMPTY baseline; must exit 1 (proves the gate bites)")
    ap.add_argument("--selftest-no-markers", action="store_true",
                    help="run with an EMPTY weakener list; must exit 2 on the pin floor "
                         "or 0 with an empty census, proving the matcher is what finds "
                         "the hits and not the baseline")
    args = ap.parse_args()

    if args.selftest_no_markers:
        del WEAKENERS[:]

    hits, functions, pins = census()

    if functions < MIN_FUNCTIONS:
        print("[!] docstring-contract-disagreement: REFUSING — the walk saw only %d "
              "function(s), expected at least %d. The glob is broken; this is not a pass."
              % (functions, MIN_FUNCTIONS), file=sys.stderr)
        return 2
    if pins < MIN_PINS:
        print("[!] docstring-contract-disagreement: REFUSING — only %d equality pin(s) "
              "matched, expected at least %d. The annotation matcher is broken; this is "
              "not a pass." % (pins, MIN_PINS), file=sys.stderr)
        return 2

    baseline = {} if args.selftest_empty_baseline else BASELINE
    keys = {(p, f) for p, f, _w, _d in hits}
    new = sorted(k for k in keys if k not in baseline)
    gone = sorted(k for k in baseline if k not in keys)
    dis = sorted(k for k in keys if baseline.get(k, (None,))[0] == DISAGREES)

    if args.verbose:
        for p, f, w, d in sorted(hits):
            print("    %-16s %-9s %-18s %-14s %s"
                  % (baseline.get((p, f), ("NEW",))[0], p, f, w, d))

    print("[*] docstring-contract-disagreement: %d function(s) scanned, %d equality "
          "pin(s); %d docstring/contract hit(s), %d DISAGREES, %d innocent."
          % (functions, pins, len(keys), len(dis), len(keys) - len(dis)))

    if args.selftest_no_markers:
        print("[*] selftest: weakener list emptied; %d hit(s) — the matcher is what finds "
              "them." % len(keys))
        return 0 if not keys else 1

    rc = 0
    for k in gone:
        print("[+]   baselined hit %s.%s IS GONE — remove its entry (and check the "
              "contract was WEAKENED, not the docstring deleted)." % k)
    for k in new:
        print("[!]   NEW DOCSTRING/CONTRACT DISAGREEMENT %s.%s — the prose beside an "
              "`ensures \\result ==` pin carries a weakening word. Argue it into DISAGREES "
              "(the prose is right and the clause over-claims), QUOTED-RELATION (the word "
              "IS the modelled relation), BRANCH-CONDITION (it is the case split the "
              "clauses discharge) or GUARD-RESTATED (it is the `requires` being "
              "explained), and add it to the baseline." % k, file=sys.stderr)
        rc = 1
    if rc:
        print("[!] docstring-contract-disagreement: NOT OK — the free oracle fired on "
              "something unargued.", file=sys.stderr)
    else:
        print("[+] docstring-contract-disagreement: OK — %d known hit(s), none new "
              "(%d DISAGREES standing: %s)."
              % (len(baseline), len(dis),
                 ", ".join("%s.%s" % k for k in dis) or "none"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
