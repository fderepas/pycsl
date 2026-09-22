#!/usr/bin/env python3
r"""L-PLANE ORACLE: the reference corpus's OWN PASSING contracts, measured against CPython.

WHY THIS EXISTS. `bin/check-value-differential.py` runs each of its 75 CURATED drivers
under CPython and checks the literal in its `#@ ensures \result == <int>` against the
observed answer — the strongest instrument in the battery, because it curates nothing and
re-measures the ground truth on every run. But its population is 75 files that someone
chose.

The PASS-expected files of `test-suite/corpus/pycsl-reference/` AND
`test-suite/corpus/python-reference/` have never been checked that way, and **378 of them
already contain a ZERO-ARGUMENT function with a LITERAL `#@ ensures \result == N`** — a
claim that is directly runnable, with no new drivers to write. This plane extends the
value-differential's reach from a curated 75 to both corpora, for free.

WHAT A FAILURE HERE MEANS, and it is the sharpest verdict in the battery: a corpus test
that PASSES the prover while its own postcondition is FALSE of the program it is written
about. That is a route witness hiding inside a green test.

FIRST MEASUREMENT (gen #30): 216 runnable contracts, **195 AGREE with CPython, 0
DISAGREE**, 21 not runnable standalone. Putting the corpus directory on `sys.path` then
recovered the multi-file ones. The remainder are programs CPython CANNOT run at all —
they name types that only a `#@ datatype` declaration introduces — so they have no ground
truth to disagree with, which is a category and not a gap. Every unrunnable case is
REPORTED with its exception type, never silently dropped: a plane that cannot tell
"agreed" from "could not run" is not a plane.

THE POPULATION GUARD (the #44 rule). A gate of this shape is trivially satisfiable by
running nothing, so it REFUSES (rc=2) if fewer than MIN_RUNNABLE contracts actually
execute. The corpus only grows, so the floor is set just under the first measurement.

WHAT IT DOES NOT CHECK: contracts with parameters, non-literal right-hand sides,
quantifiers, or `\result` of a non-int/bool return. Those are the value-differential
corpus's job, and writing a driver there is the way to cover one.

Usage:  bin/check-corpus-contract-truth.py [--verbose]
"""
import argparse
import contextlib
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPORA = [os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference"),
           os.path.join(ROOT, "test-suite", "corpus", "python-reference")]
MIN_RUNNABLE = 350   # first measurement 366 across both corpora; they only grow


def candidates():
    out = []
    files = []
    for c in CORPORA:
        files += sorted(glob.glob(os.path.join(c, "*.py")))
        files += sorted(glob.glob(os.path.join(c, "**", "*.py"), recursive=True))
    for f in sorted(set(files)):
        src = open(f, errors="replace").read()
        if "# pycsl-expected: FAIL" in src:
            continue
        lines = src.split("\n")
        for i, l in enumerate(lines):
            m = re.match(r"\s*#@\s*ensures\s+\\result\s*==\s*(-?\d+)\s*$", l)
            if not m:
                continue
            for j in range(i + 1, min(i + 6, len(lines))):
                d = re.match(r"def (\w+)\(\s*\)\s*->\s*(int|bool)\s*:", lines[j].strip())
                if d:
                    out.append((f, d.group(1), int(m.group(1))))
                    break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    rows = candidates()
    agree = 0
    disagree = []
    unrunnable = []
    for f, fn, claim in rows:
        src = open(f, errors="replace").read()
        ns = {"__name__": "corpus_contract_probe"}
        # MULTI-FILE tests import a sibling module out of the corpus directory. Putting
        # that directory on `sys.path` turns 8 `ModuleNotFoundError`s into real
        # measurements — coverage the first version left on the table. The path entry is
        # removed again so one test cannot shadow a name for the next.
        sys.path.insert(0, os.path.dirname(f))
        try:
            with contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()):
                exec(compile(src, f, "exec"), ns)
            if fn not in ns:
                unrunnable.append((os.path.basename(f), fn, "not defined after exec"))
                continue
            got = ns[fn]()
        except Exception as e:
            unrunnable.append((os.path.basename(f), fn, type(e).__name__))
            continue
        finally:
            if sys.path and sys.path[0] == os.path.dirname(f):
                sys.path.pop(0)
        if isinstance(got, bool):
            got = int(got)
        if got == claim:
            agree += 1
            if args.verbose:
                print("    ok  %s::%s == %d" % (os.path.basename(f), fn, claim))
        else:
            disagree.append((os.path.basename(f), fn, claim, got))

    print("[*] corpus-contract-truth: %d runnable literal-result contract(s) — "
          "%d AGREE with CPython, %d DISAGREE, %d could not run standalone."
          % (len(rows), agree, len(disagree), len(unrunnable)))
    if args.verbose:
        for b in unrunnable:
            print("    unrunnable  %s::%s (%s)" % b)

    if agree + len(disagree) < MIN_RUNNABLE:
        print("[!] corpus-contract-truth: REFUSING — only %d contract(s) actually ran, "
              "expected at least %d. A gate that cannot tell 'nothing is wrong' from "
              "'I ran nothing' is not a gate." % (agree + len(disagree), MIN_RUNNABLE),
              file=sys.stderr)
        return 2

    if disagree:
        for b in disagree:
            print("[!]   DISAGREES WITH CPYTHON: %s::%s — the contract claims %r, the "
                  "program returns %r" % b, file=sys.stderr)
        print("[!] corpus-contract-truth: NOT OK — a corpus test whose own postcondition "
              "is FALSE of its own program is a route witness hiding inside a green test.",
              file=sys.stderr)
        return 1

    print("[+] corpus-contract-truth: OK — every runnable corpus postcondition is true of "
          "the program it is written about.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
