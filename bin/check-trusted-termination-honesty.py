#!/usr/bin/env python3
r"""check-trusted-termination-honesty.py — the THIRD honesty plane for `#@ \trusted`.

A bodyless `val` asserts more than the contract written above it. The campaign already
measures two of those silent assertions:

    check-trusted-frame-honesty.py   — is the stub's `#@ assigns` honest about what the
                                       LIVE body WRITES?
    check-trusted-raises-honesty.py  — is it honest about what the LIVE body RAISES? (an
                                       emitted `val` with no `raises` tells Why3 the call
                                       CANNOT raise)

THE THIRD ONE HAD NO INSTRUMENT: **does the live body TERMINATE?** PyCSL functions are
total by default — Why3 emits a termination VC and every loop needs a `#@ loop variant` —
and a `\trusted` / `\abstract` stub has no body lowered, so there is no loop, no variant
obligation, and every caller's call is assumed to RETURN.

WHY THIS ONE IS NOT ONLY A TRUST SURFACE. The raises plane probed its exploit and found a
trust surface rather than a demonstrated unsoundness ("a stub that says `ensures \result
== 1` over a body that always raises is a FALSE REVIEW, not a broken lowering"). The
termination assertion crossed that line twice in gen #30:

  * ROUTE #206 — `#@ happy availability: targets parse total` PROVED for a target whose
    body is one call to a `\trusted` method containing `while True: acc = acc + 1`. The
    policy's stated purpose is that an attacker-controlled input cannot cause
    non-termination; CPython hangs. (Witness 1711; route #93 had closed the same hole for
    a bodyless TARGET and not for a bodyless CALLEE.)
  * ROUTE #207 — the sibling for exceptions, through the same method-call arm.

So a `\trusted` loop without a variant is not merely "the reviewer's problem": it is the
raw material a policy claim is built from.

WHAT IT MEASURES. Every `#@ \trusted` / `#@ \abstract` function in the mirror, in
`src/pycsl_lib/`, and in the corpus, whose LIVE body contains a `while`/`for` with no
`#@ loop variant` anywhere in it, or which calls ITSELF. FIRST MEASUREMENT (gen #30):

    7440 functions scanned across the three trees; 52 trusted/abstract bodies whose
    termination is assumed and unverified — mirror 47, stdlib 2, corpus 3. The three
    corpus members are ROUTE WITNESSES (1254, 1255, 1711), where a non-terminating
    trusted body is the point of the file, and they are named individually so a NEW
    corpus entry is visible rather than lost in a count.

THE RATCHET: the total may not grow. Adding a variant to a trusted body, or giving the
function a real body, is the way down. THE POPULATION GUARD (the #44 rule): rc=2 if fewer
than MIN_FUNCTIONS functions are parsed at all.

Usage:  bin/check-trusted-termination-honesty.py [--verbose]
"""
import argparse
import ast
import glob
import os
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREES = (("mirror", os.path.join(ROOT, "src", "self-annotate", "src")),
         ("stdlib", os.path.join(ROOT, "src", "pycsl_lib")),
         ("corpus", os.path.join(ROOT, "test-suite", "corpus")))
MIN_FUNCTIONS = 6500          # 7440 across the three trees at the first measurement
MAX_SILENT = 53               # (#49) gen #31: 52 -> 53, DELIBERATELY and with the member
                              # named. Route #219's build stopped dropping dunders, so
                              # `errors.py::PyCSLError.__str__` became emittable, failed as a
                              # Why3 TYPE ERROR (an int-modelled field into a `seq string`)
                              # and took an honest `#@ \trusted` marker — which is what puts
                              # it in THIS population. The "loop" this plane reports is a
                              # SELF-CALL, and the self-call is `super().__str__()`: a call to
                              # the BASE class's method, not recursion. The heuristic is
                              # CONSERVATIVE BY DESIGN (it cannot tell `super().m()` from
                              # `self.m()` without a class graph) and is left that way — an
                              # exception carved for one entry is how a population filter
                              # starts lying, which this campaign has now measured six times.
                              # It retires with the marker: see driver-backlog.md heading
                              # "the two mirror dunder markers".
                              # 47 mirror + 2 stdlib + 3 corpus at the first measurement
                              # (the mirror figure counts self-recursive trusted bodies too,
                              # which a first pass double-counted against the loop figure)

# The corpus members are ROUTE WITNESSES: a trusted non-terminating body is the POINT of
# the file, and each is `# pycsl-expected: FAIL` for exactly that reason. They are named
# so that a NEW corpus entry is visible rather than lost in a count.
KNOWN_CORPUS = {
    "1254_route93_total_target_trusted_evades.py::parse",
    "1255_route93_total_target_abstract_evades.py::parse",
    "1711_route206_total_target_calls_trusted_stub.py::spin",
}


def scan():
    rows, functions = [], 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for label, root in TREES:
            for f in sorted(glob.glob(os.path.join(root, "**", "*.py"), recursive=True)):
                src = open(f, errors="replace").read()
                lines = src.split("\n")
                try:
                    tree = ast.parse(src)
                except SyntaxError:
                    continue
                for n in ast.walk(tree):
                    if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    functions += 1
                    ann, i = [], n.lineno - 2
                    while i >= 0 and (not lines[i].strip()
                                      or lines[i].strip().startswith("#")):
                        if lines[i].strip().startswith("#@"):
                            ann.append(lines[i].strip())
                        i -= 1
                    if not any("\\trusted" in a or "\\abstract" in a for a in ann):
                        continue
                    end = getattr(n, "end_lineno", n.lineno) or n.lineno
                    body_text = lines[n.lineno - 1:end]
                    has_loop = any(isinstance(x, (ast.While, ast.For))
                                   for x in ast.walk(n))
                    has_variant = any("loop variant" in l for l in body_text)
                    recursive = any(
                        isinstance(x, ast.Call)
                        and (getattr(x.func, "attr", None) == n.name
                             or getattr(x.func, "id", None) == n.name)
                        for x in ast.walk(n))
                    if (has_loop and not has_variant) or recursive:
                        rows.append((label, os.path.basename(f), n.name,
                                     "loop-without-variant" if has_loop else "self-call"))
    return rows, functions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--max-silent", type=int, default=MAX_SILENT)
    args = ap.parse_args()

    rows, functions = scan()
    if functions < MIN_FUNCTIONS:
        print("[!] trusted-termination-honesty: REFUSING — only %d function(s) parsed, "
              "expected at least %d. The walk is broken; this is not a pass."
              % (functions, MIN_FUNCTIONS), file=sys.stderr)
        return 2

    loops = [r for r in rows if r[3] == "loop-without-variant"]
    percent = {}
    for label, _t in TREES:
        percent[label] = sum(1 for r in rows if r[0] == label)

    print("[*] trusted-termination-honesty: %d function(s) scanned; %d `\\trusted`/"
          "`\\abstract` bod(ies) whose TERMINATION is assumed and unverified — %s."
          % (functions, len(rows),
             ", ".join("%s %d" % (k, percent[k]) for k, _ in TREES)))
    if args.verbose:
        for r in sorted(rows):
            print("    %-7s %-48s %-34s %s" % r)

    corpus_now = {"%s::%s" % (r[1], r[2]) for r in rows if r[0] == "corpus"}
    rc = 0
    for extra in sorted(corpus_now - KNOWN_CORPUS):
        print("[!]   NEW CORPUS ENTRY %s — a trusted non-terminating body in the corpus "
              "is either a route witness (name it in KNOWN_CORPUS) or a mistake."
              % extra, file=sys.stderr)
        rc = 1
    if len(rows) > args.max_silent:
        print("[!]   SILENT-TERMINATION RATCHET BROKEN — %d > %d. A new `\\trusted` body "
              "with a variant-less loop assumes termination that nothing checks; under a "
              "`happy ... total` policy that assumption became route #206."
              % (len(rows), args.max_silent), file=sys.stderr)
        rc = 1

    if rc:
        print("[!] trusted-termination-honesty: NOT OK.", file=sys.stderr)
    else:
        print("[+] trusted-termination-honesty: OK — %d assumed-terminating trusted "
              "bod(ies), ratchet %d; %d of them are loops without a `#@ loop variant`."
              % (len(rows), args.max_silent, len(loops)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
