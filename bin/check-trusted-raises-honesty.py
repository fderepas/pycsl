#!/usr/bin/env python3
r"""check-trusted-raises-honesty.py — the TRUSTED-RAISES plane.

A `#@ \trusted` mirror stub is believed, not proved: its `#@ requires` / `#@ ensures` /
`#@ assigns` / `#@ raises` are asserted by a reviewer and Module 6 emits a bodyless `val`
carrying exactly them. `check-trusted-frame-honesty.py` already asks whether such a stub's
`#@ assigns` is honest about what the LIVE body WRITES. Nobody had asked the sibling
question:

    IS THE STUB HONEST ABOUT WHAT THE LIVE BODY *RAISES*?

It matters for the same reason the frame does. An emitted `val` with NO `raises` clause
tells Why3 the call CANNOT raise. Every caller then reasons on a single exit path: a
`try/except` around the call has a handler Why3 knows is dead, and the caller's own
contract need not account for the exceptional exit. If the live body does contain a
`raise`, the stub is asserting something false — and unlike a missing `assigns`, nothing
in the proof will ever contradict it, because a `\trusted` body is never lowered.

This is the shape of routes #20 and #21 one level up: a claim that a control-flow path
does not exist, believed because nothing looks.

*** PROBED, AND IT IS A TRUST SURFACE RATHER THAN A DEMONSTRATED UNSOUNDNESS. *** The
obvious exploit — a `\trusted` stub whose body is `raise ValueError(...)`, called inside a
`try/except ValueError` whose handler returns a different value, with a contract asserting
the non-exceptional result — was built and run (`scratchpad/w9/probes/tr1.py`) and
correctly FAILS. The reason is the honest one: whatever such a stub's contract claims is
claimed BY THE REVIEWER, and `\trusted` means exactly that. A stub that says
`ensures \result == 1` over a body that always raises is a FALSE REVIEW, not a broken
lowering.

That is why this is a RATCHET and not a route. What it measures is how much of the mirror's
believed surface makes a control-flow claim nobody checked, and the honest thing to do with
such a number is to publish it and shrink it.

WHAT IT MEASURES. For every `\trusted` mirror stub, whether its LIVE counterpart contains
a `raise` statement, and whether the stub carries a `#@ raises` line.

    DECLARED   live body raises, stub says so.
    SILENT     live body raises, stub says NOTHING.  <- the population held by the ratchet
    (a stub whose live body has no `raise` is not counted either way)

It is a LOWER BOUND in one direction and an over-count in the other, and both are stated
rather than hidden: only DIRECT `raise` statements are counted, so a stub whose live body
raises only through a callee is missed; and a `raise` on a path the contract's `#@
requires` excludes is counted although the stub may be honest. The ratchet is therefore a
measurement to shrink, not a bug count.

FIRST MEASUREMENT (#44): 70 `\trusted` stubs have a raising live counterpart; 2 declare
`#@ raises` and 68 are SILENT.

USAGE
    bin/check-trusted-raises-honesty.py [--verbose] [--max-silent N]
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
LIVE = os.path.join(ROOT, "src", "pycsl")

MAX_SILENT = 68


def raising_live_functions():
    """{name: set(files)} for every LIVE function containing a direct `raise`."""
    out = {}
    for root, _d, files in os.walk(LIVE):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                tree = ast.parse(open(path, errors="replace").read())
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            for n in ast.walk(tree):
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if any(isinstance(x, ast.Raise) for x in ast.walk(n)):
                    out.setdefault(n.name, set()).add(os.path.relpath(path, ROOT))
    return out


def directive_block(lines, lineno):
    """The contiguous comment block immediately above a def."""
    blk = []
    for line in reversed(lines[max(0, lineno - 45):lineno - 1]):
        if line.strip().startswith("#") or not line.strip():
            blk.append(line)
        else:
            break
    return blk


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--max-silent", type=int, default=MAX_SILENT)
    args = ap.parse_args()

    raising = raising_live_functions()
    declared, silent = [], []
    for root, _d, files in os.walk(MIRROR):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                src = open(path, errors="replace").read()
                tree = ast.parse(src)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            lines = src.split("\n")
            for n in ast.walk(tree):
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                blk = directive_block(lines, n.lineno)
                if not any("\\trusted" in b for b in blk):
                    continue
                if n.name not in raising:
                    continue
                rel = os.path.relpath(path, MIRROR)
                row = (rel, n.name, sorted(raising[n.name])[0])
                if any("#@ raises" in b for b in blk):
                    declared.append(row)
                else:
                    silent.append(row)

    total = len(declared) + len(silent)
    print(f"[*] trusted-raises-honesty: {total} `\\trusted` stub(s) whose LIVE counterpart "
          f"contains a `raise`; {len(declared)} declare `#@ raises`, {len(silent)} are "
          f"SILENT (the emitted `val` tells Why3 the call CANNOT raise).")
    if args.verbose or len(silent) > args.max_silent:
        for rel, name, livefile in sorted(silent):
            print(f"    SILENT    {rel:44s} {name:38s} live: {livefile}")
    if len(silent) > args.max_silent:
        print(f"[-] trusted-raises-honesty: SILENT RATCHET BROKEN — {len(silent)} > "
              f"{args.max_silent}. A `\\trusted` stub with no `#@ raises` asserts that its "
              f"call has ONE exit path; nothing will ever contradict it, because a "
              f"`\\trusted` body is never lowered.")
        return 1
    if len(silent) < args.max_silent:
        print(f"[+] trusted-raises-honesty: silent {len(silent)} < ratchet "
              f"{args.max_silent} — lower the constant.")
    print(f"[+] trusted-raises-honesty: OK — measured {len(declared)} declared / "
          f"{len(silent)} silent (ratchet {args.max_silent}). NOTE: direct `raise` "
          f"statements only, so this is a LOWER BOUND on the population.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
