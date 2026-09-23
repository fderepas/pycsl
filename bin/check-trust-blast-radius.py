#!/usr/bin/env python3
r"""L-PLANE ORACLE: how much of the self-annotation mirror DEPENDS on a `\trusted`
contract, as opposed to how many `\trusted` markers there are.

WHY THIS EXISTS (gen #30). The campaign's headline metric is a MARKER COUNT —
`bin/count-trusted-directives.py` reports 459, and a generation's success has been measured
in how many of those became proofs. That number answers "how many places did we say trust
me", and it was never meant to answer "how much of the verified surface rests on those
places". Nothing answered the second question at all.

The parameterized corpus oracle made the gap concrete. Corpus 0053 trusts `double_int`,
whose body is deliberately `x + x + x` under `ensures \result == 2 * x`. `foobar` is NOT
trusted, has a real body, calls `double_int`, and PROVES `\result == 2 * x` while CPython
answers `3 * x`. One marker; two false claims. The marker count sees one.

WHAT THIS MEASURES. Over `src/self-annotate/src/`: every function definition, which ones
carry `#@ \trusted`, and which UNTRUSTED ones reach a trusted one through the call graph
(transitively). Call resolution in Python-without-types is not exact, so the answer is
reported as a BRACKET rather than a number, and both ends are ratcheted:

  LOWER — a call resolves only to a definition IN THE SAME FILE. Conservative: it can
          miss a real cross-file dependency, so the trust-dependent count it gives is a
          FLOOR.
  UPPER — a call by name (`f()` or `o.f()`) resolves to EVERY definition of that name
          anywhere in the mirror. Over-approximate, so the count it gives is a CEILING.

FIRST MEASUREMENT (gen #30): 1373 function definitions, 433 carrying `\trusted`, and
between 335 and 400 untrusted functions that transitively depend on one. So between 768
and 833 of 1373 — **56% to 61% of the mirror is trusted or trust-dependent**, and only
540 to 605 functions (39%–44%) are provably independent of every marker.

WHAT THIS IS NOT. It is not a soundness failure and nothing here is a route. A `\trusted`
contract may be perfectly true; the point is that the marker count understates the size of
the claim by roughly a factor of two, and a campaign that reports "459 markers" without
this bracket is reporting the smaller number.

THE RATCHETS: the trust-dependent UPPER bound may not grow and the trust-free LOWER bound
may not shrink — converting a marker into a proof moves both the right way, and adding a
marker in a hot call path moves both the wrong way even when the marker count is flat.
THE POPULATION GUARD (the #44 rule): rc=2 below MIN_DEFS definitions.

Usage:  bin/check-trust-blast-radius.py [--verbose]
"""
import argparse
import ast
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
MIN_DEFS = 1200               # 1373 at the first measurement
MAX_TRUST_DEPENDENT = 400     # UPPER bound at the first measurement; may only shrink
MIN_TRUST_FREE = 538          # (#49) gen #31: 540 -> 538, and this is the ONE direction this
                              # constant is allowed to move, so the reason is recorded rather
                              # than the number adjusted. Route #219's build stopped dropping
                              # dunders; two mirror methods that had been counted among the
                              # UN-TRUSTED twins while NEVER BEING EMITTED OR PROVED became
                              # emittable, failed as Why3 TYPE ERRORS, and took honest
                              # `#@ \trusted` markers (459 -> 461). The trust-free set loses
                              # exactly those two.
                              #
                              # SO THE FLOOR DID NOT REALLY DROP — THE MEASUREMENT GOT
                              # HONEST. Both methods were trust-DEPENDENT-or-worse all along;
                              # what changed is that the marker now says so. Any FURTHER
                              # decrease without a named marker IS a regression and this
                              # ratchet still catches it. Each of the two names the capability
                              # that retires it (driver-backlog.md, "the two mirror dunder
                              # markers"), and retiring either moves this number back up.
                              # 540 was the LOWER bound at the first measurement.


def scan():
    keys, trusted, calls, per_file = [], set(), {}, {}
    for f in sorted(glob.glob(os.path.join(MIRROR, "**", "*.py"), recursive=True)):
        src = open(f, errors="replace").read()
        lines = src.split("\n")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        for n in ast.walk(tree):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            k = (f, n.name)
            keys.append(k)
            per_file.setdefault(f, set()).add(n.name)
            ann, i = [], n.lineno - 2
            while i >= 0 and (not lines[i].strip() or lines[i].strip().startswith("#")):
                if lines[i].strip().startswith("#@"):
                    ann.append(lines[i].strip())
                i -= 1
            if any("\\trusted" in a for a in ann):
                trusted.add(k)
            c = set()
            for x in ast.walk(n):
                if isinstance(x, ast.Call):
                    if isinstance(x.func, ast.Name):
                        c.add(x.func.id)
                    elif isinstance(x.func, ast.Attribute):
                        c.add(x.func.attr)
            calls[k] = c
    return keys, trusted, calls, per_file


def closure(keys, trusted, calls, resolve):
    reach, changed = set(), True
    while changed:
        changed = False
        for k in keys:
            if k in reach:
                continue
            tgt = set()
            for name in calls[k]:
                tgt |= set(resolve(k, name))
            if (tgt & trusted) or (tgt & reach):
                reach.add(k)
                changed = True
    return reach


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    keys, trusted, calls, per_file = scan()
    total = len(keys)
    if total < MIN_DEFS:
        print("[!] trust-blast-radius: REFUSING — %d function definition(s) found, "
              "expected at least %d. The walk is broken; this is not a pass."
              % (total, MIN_DEFS), file=sys.stderr)
        return 2

    by_name = {}
    for k in keys:
        by_name.setdefault(k[1], []).append(k)

    lower = closure(keys, trusted, calls,
                    lambda k, n: [(k[0], n)] if n in per_file.get(k[0], ()) else [])
    upper = closure(keys, trusted, calls, lambda k, n: by_name.get(n, []))
    dep_lo, dep_hi = len(lower - trusted), len(upper - trusted)
    free_hi, free_lo = total - len(trusted) - dep_lo, total - len(trusted) - dep_hi

    print("[*] trust-blast-radius: %d function definition(s) in the mirror; %d carry "
          "`\\trusted`; between %d and %d untrusted function(s) transitively DEPEND on "
          "one, so %d-%d (%.0f%%-%.0f%%) are trusted-or-trust-dependent and %d-%d are "
          "provably independent of every marker."
          % (total, len(trusted), dep_lo, dep_hi,
             len(trusted) + dep_lo, len(trusted) + dep_hi,
             100.0 * (len(trusted) + dep_lo) / total,
             100.0 * (len(trusted) + dep_hi) / total, free_lo, free_hi))

    if args.verbose:
        for k in sorted(upper - trusted)[:40]:
            print("    depends  %s::%s" % (os.path.relpath(k[0], ROOT), k[1]))

    rc = 0
    if dep_hi > MAX_TRUST_DEPENDENT:
        print("[!]   TRUST-DEPENDENT CEILING BROKEN: %d > %d. A new marker in a hot call "
              "path grows this even when the marker COUNT is flat."
              % (dep_hi, MAX_TRUST_DEPENDENT), file=sys.stderr)
        rc = 1
    if free_lo < MIN_TRUST_FREE:
        print("[!]   TRUST-FREE FLOOR BROKEN: %d < %d. The part of the mirror that rests "
              "on no marker at all got smaller." % (free_lo, MIN_TRUST_FREE),
              file=sys.stderr)
        rc = 1

    if rc:
        print("[!] trust-blast-radius: NOT OK.", file=sys.stderr)
    else:
        print("[+] trust-blast-radius: OK — trust-dependent ceiling %d (at %d), "
              "trust-free floor %d (at %d)."
              % (MAX_TRUST_DEPENDENT, dep_hi, MIN_TRUST_FREE, free_lo))
    return rc


if __name__ == "__main__":
    sys.exit(main())
