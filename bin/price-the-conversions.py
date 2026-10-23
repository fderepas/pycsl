#!/usr/bin/env python3
r"""price-the-conversions.py — what does a CONVERTED mirror function actually claim?

The campaign reports a `\trusted` MARKER COUNT and its complement, the number of converted
functions. Neither says what a conversion ESTABLISHES. This prices them.

A conversion with `#@ ensures True; #@ assigns \nothing` still proves purity, type safety,
termination and — synthesized, not written — frame preservation for every record field. It
does NOT say the function computes the right thing. The split below is the difference.

MEASUREMENT ONLY. This is not a plane and it gates nothing: there is no honest ratchet here
yet, because a function whose live body genuinely has no functional postcondition worth
stating (a `__repr__`, a dispatcher) should not be pushed into inventing one.

USAGE
    bin/price-the-conversions.py [--list <bucket>]
      buckets: real-ensures | purity-only | frame-only | neither
"""
import ast
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
TRUSTED = re.compile(r"^\s*#@\s*\\trusted\b")
ENSURES = re.compile(r"^\s*#@\s*ensures\b")
ENSURES_TRUE = re.compile(r"^\s*#@\s*ensures\s+True\s*$")
ASSIGNS = re.compile(r"^\s*#@\s*assigns\b")
ASSIGNS_NOTHING = re.compile(r"^\s*#@\s*assigns\s+\\nothing\s*$")

# The #44 rule: a gate that cannot tell "nothing is wrong" from "I looked at nothing" is not
# a gate, and a census that cannot tell it is not a census either.
MIN_DEFS = 1000


def main():
    buckets = {"real-ensures": [], "purity-only": [], "frame-only": [], "neither": []}
    nested_neither = [0]
    total = [0]
    trusted = [0]

    for dirpath, _dirs, files in os.walk(MIRROR):
        for fname in sorted(files):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            src = io.open(path, encoding="utf-8").read()
            lines = src.split("\n")
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            rel = os.path.relpath(path, MIRROR)

            def walk(node, pre, in_def):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        qual = pre + child.name
                        first = (min(d.lineno for d in child.decorator_list)
                                 if child.decorator_list else child.lineno) - 1
                        i, block = first - 1, []
                        while i >= 0 and (not lines[i].strip()
                                          or lines[i].lstrip().startswith("#")):
                            block.append(lines[i])
                            i -= 1
                        total[0] += 1
                        if any(TRUSTED.match(b) for b in block):
                            trusted[0] += 1
                        else:
                            ens = [b for b in block if ENSURES.match(b)]
                            real = any(not ENSURES_TRUE.match(e) for e in ens)
                            asg = [b for b in block if ASSIGNS.match(b)]
                            name = "%s::%s" % (rel, qual)
                            if real:
                                buckets["real-ensures"].append(name)
                            elif any(ASSIGNS_NOTHING.match(a) for a in asg):
                                buckets["purity-only"].append(name)
                            elif asg:
                                buckets["frame-only"].append(name)
                            else:
                                buckets["neither"].append(name)
                                if in_def:
                                    nested_neither[0] += 1
                        walk(child, qual + ".", True)
                    elif isinstance(child, ast.ClassDef):
                        walk(child, pre + child.name + ".", in_def)
                    else:
                        walk(child, pre, in_def)

            walk(tree, "", False)

    if total[0] < MIN_DEFS:
        print("[!] price-the-conversions: REFUSING — only %d definition(s) found in %s, "
              "expected at least %d. THIS IS A REFUSAL, NOT A MEASUREMENT."
              % (total[0], MIRROR, MIN_DEFS), file=sys.stderr)
        return 2

    conv = total[0] - trusted[0]
    print("[*] price-the-conversions: %d mirror definition(s); %d carry `\\trusted`, "
          "%d are CONVERTED." % (total[0], trusted[0], conv))
    order = [("real-ensures", "a FUNCTIONAL postcondition (`#@ ensures` that is not `True`)"),
             ("purity-only", "PURITY only (`#@ assigns \\nothing`)"),
             ("frame-only", "a NON-TRIVIAL FRAME only (`#@ assigns <fields>`)"),
             ("neither", "neither a real `ensures` nor an `assigns`")]
    for key, label in order:
        n = len(buckets[key])
        pct = (100.0 * n / conv) if conv else 0.0
        print("      %5d  %4.0f%%  %s" % (n, pct, label))
    print("             of the %d in the last bucket, %d are NESTED CLOSURES (no `#@` block "
          "by design — FOLDED into an enclosing definition)."
          % (len(buckets["neither"]), nested_neither[0]))
    print("    A conversion with no functional postcondition still proves PURITY or a FRAME, "
          "TYPE SAFETY, TERMINATION, and the SYNTHESIZED per-field frame-preservation "
          "`ensures` the abstract `val` merely assumed. It does not say the function "
          "computes the right thing.")

    if "--list" in sys.argv:
        which = sys.argv[sys.argv.index("--list") + 1]
        if which not in buckets:
            print("[!] unknown bucket %r; pick one of %s"
                  % (which, ", ".join(buckets)), file=sys.stderr)
            return 2
        for name in buckets[which]:
            print("   ", name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
