#!/usr/bin/env python3
r"""A REFERENCE DRIVER WHOSE CONTRACT IS DISCHARGED BY ITS TAIL `return` ALONE.

THE DEFECT CLASS, and this campaign hit it twice in one window BY ACCIDENT:

  * `python-reference/0209` is "the async with statement". Its body builds an async
    context manager and its contract is `#@ ensures \result == 0`; the function ends
    `return 0`. It PASSED for two years without `async with` being modelled AT ALL —
    the `with` protocol is dropped, the `assert` is dropped, and `return 0` discharges
    the postcondition by itself. It only stopped passing when relaunch #46's route-#39
    refusal made the unmodelled construct LOUD.
  * `python-reference/0044` is "numbers.Complex". Same shape: `c = 3 + 4j`, two
    `assert`s (DROPPED by Module 6), `return 0`, `#@ ensures \result == 0`. It passed
    while a complex literal was being lowered to `int(value.real)` — route #43.

BOTH WERE FOUND AS FALLOUT FROM AN UNRELATED FIX. Neither the suite nor any of the
twenty-three other planes can see this: the driver PASSES, and passing is what the suite
measures. **A DRIVER THAT PASSES WITHOUT THE CONSTRUCT IT NAMES BEING MODELLED IS NOT
EVIDENCE OF ANYTHING**, and the only way to know is to ask whether the proof used it.

WHAT THIS GATE CHECKS — a deliberately CONSERVATIVE, purely mechanical proxy. A driver
is TRIVIALLY DISCHARGED when

  * the annotated function has exactly ONE `#@ ensures`, of the form `\result == <int>`,
    and no other contract clause (`requires` / `assigns` / `raises` / loop clauses);
  * the function body ENDS in a top-level `return <that same int>`;
  * the function contains NO OTHER `return`.

Then the postcondition follows from the tail return alone and every statement above it is
irrelevant to the proof. Python `assert`s are DROPPED by Module 6 (a settled fact of this
campaign), so the extremely common `x = <construct>; assert <property>; return 0` shape is
exactly this.

IT IS A RATCHET, NOT A HARD ZERO, and on purpose. The measured population is large — the
`python-reference` corpus was written as COVERAGE, not as proof obligations — and deleting
it wholesale would lose the crash/refusal coverage those drivers do provide (that coverage
is real: `bin/check-internal-crash-free.py` runs the same files and found three crashes in
them). The ratchet says: no NEW driver may join the population, and every one that leaves
it lowers the number.

WHAT IT DOES NOT CLAIM. A trivially-discharged driver is not WRONG and not a soundness
defect; it is a driver whose PASS carries no information about its subject. Conversely a
driver outside this population is not thereby meaningful — the proxy is conservative in
one direction only. Fixing one means giving it a contract that mentions what it tests.
"""
import argparse
import ast
import warnings
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Corpus drivers deliberately contain invalid escape sequences (they are
# Python-reference material); their SyntaxWarnings are not this gate's output.
warnings.filterwarnings("ignore", category=SyntaxWarning)
ENS = re.compile(r"^#@\s+ensures\s+\\result\s*==\s*(-?\d+)\s*$")
OTHER = re.compile(r"^#@\s+(requires|assigns|loop|\\variant|raises|ensures|act|"
                   r"complete|disjoint|no_exception)\b")

# Measured 2026-09-05 (relaunch #46) on the tree at commit b161b4a5.
RATCHETS = {"python-reference": 116, "pycsl-reference": 9}
# THE SHARPER SUB-POPULATION: a function whose ENTIRE body is a docstring plus a single
# `return <literal>`. It is not merely "proved from the tail return" — it EXERCISES
# NOTHING. `python-reference/0034` ("Integer literals"), `0038` ("Objects, values and
# types") and `0051` ("Instance methods") are literally `'''Ref 2.6.1: ...'''; return 0`.
# These are UNIMPLEMENTED PLACEHOLDERS that count as passing tests, and the headline
# "3178/3197 passed" is padded by exactly this many.
EMPTY_RATCHETS = {"python-reference": 89, "pycsl-reference": 47}
MIN_FUNCS = {"python-reference": 2000, "pycsl-reference": 800}


def scan(root):
    trivial, empty, total = [], [], 0
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git', '__pycache__')]
        for f in sorted(fn):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dp, f)
            src = open(p, encoding="utf-8", errors="replace").read()
            if "# pycsl-expected: FAIL" in src:
                continue
            try:
                tree = ast.parse(src)
            except Exception:
                continue
            lines = src.split("\n")
            for n in tree.body:
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                total += 1
                _b = [s2 for s2 in n.body
                      if not (isinstance(s2, ast.Expr)
                              and isinstance(s2.value, ast.Constant))]
                if (len(_b) == 1 and isinstance(_b[0], ast.Return)
                        and isinstance(_b[0].value, ast.Constant)):
                    empty.append("%s::%s" % (os.path.relpath(p, ROOT), n.name))
                i = n.lineno - 2
                block = []
                while i >= 0 and lines[i].lstrip().startswith("#@"):
                    block.append(lines[i].strip())
                    i -= 1
                ens = [m for m in (ENS.match(b) for b in block) if m]
                others = [b for b in block if OTHER.match(b) and not ENS.match(b)]
                if len(ens) != 1 or others:
                    continue
                want = int(ens[0].group(1))
                rets = [r for r in ast.walk(n) if isinstance(r, ast.Return)]
                if len(rets) != 1:
                    continue
                body = [s for s in n.body
                        if not (isinstance(s, ast.Expr)
                                and isinstance(s.value, ast.Constant))]
                if not body or not isinstance(body[-1], ast.Return):
                    continue
                v = body[-1].value
                if isinstance(v, ast.Constant) and v.value == want:
                    trivial.append("%s::%s" % (os.path.relpath(p, ROOT), n.name))
    return trivial, empty, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    rc = 0
    for suite, ratchet in sorted(RATCHETS.items()):
        root = os.path.join(ROOT, "test-suite", "corpus", suite)
        trivial, empty, total = scan(root)
        if total < MIN_FUNCS[suite]:
            print("[!] vacuous-drivers: only %d annotated function(s) found in %s — the "
                  "corpus path is broken. NOT A PASS." % (total, suite), file=sys.stderr)
            return 2
        print("[*] vacuous-drivers: %-18s %4d of %4d annotated function(s) are "
              "TRIVIALLY DISCHARGED by their tail `return` (ratchet %d)."
              % (suite, len(trivial), total, ratchet))
        if args.verbose:
            for t in trivial:
                print("        %s" % t)
        eratchet = EMPTY_RATCHETS[suite]
        print("[*] vacuous-drivers: %-18s %4d of them are EMPTY PLACEHOLDERS — a "
              "docstring and a single `return <literal>`, exercising nothing "
              "(ratchet %d)." % (suite, len(empty), eratchet))
        if args.verbose:
            for e in empty:
                print("        EMPTY %s" % e)
        if len(empty) > eratchet:
            print("[!] vacuous-drivers: %s EMPTY RATCHET BROKEN — %d > %d. A NEW driver "
                  "was added whose whole body is `return <literal>`. It exercises "
                  "nothing and it counts as a passing test."
                  % (suite, len(empty), eratchet), file=sys.stderr)
            rc = 1
        elif len(empty) < eratchet:
            print("    %s EMPTY is BELOW its ratchet (%d < %d) — lower the constant."
                  % (suite, len(empty), eratchet))
        if len(trivial) > ratchet:
            print("[!] vacuous-drivers: %s RATCHET BROKEN — %d > %d. A NEW driver proves "
                  "its contract from its tail `return` alone, so its PASS says nothing "
                  "about the construct it is named for. Give it a contract that mentions "
                  "what it tests." % (suite, len(trivial), ratchet), file=sys.stderr)
            rc = 1
        elif len(trivial) < ratchet:
            print("    %s is BELOW its ratchet (%d < %d) — lower the constant in this "
                  "script." % (suite, len(trivial), ratchet))
    if rc == 0:
        print("[+] vacuous-drivers: OK — every suite at or below its ratchet.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
