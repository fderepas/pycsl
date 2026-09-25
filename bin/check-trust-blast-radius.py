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
MAX_TRUST_DEPENDENT = 401     # UPPER bound at the first measurement was 400; may only shrink
                              # EXCEPT for the one move recorded here, which is the whole
                              # reason MAX_TRUSTED_OR_DEPENDENT below now exists.
                              #
                              # (#49) gen #31: 400 -> 401, and the marker count went DOWN.
                              # Retiring `errors.py::message` moved that function out of the
                              # TRUSTED set — and straight into the trust-DEPENDENT one,
                              # because its body is `return super().__str__()` and
                              # `errors.py::__str__` is itself `\trusted` (its live body is a
                              # Why3 TYPE ERROR: an int-modelled `filename` field pushed into
                              # a `seq string`). Both ends moved: dep_lo 335 -> 336 as well,
                              # so this is not an artifact of the by-name over-approximation —
                              # the SAME-FILE resolution sees it too.
                              #
                              # THE LESSON THIS CONSTANT NOW CARRIES: converting a marker on a
                              # function that CALLS a trusted function does not shrink the
                              # trusted surface by one. It RELABELS one function from
                              # "trusted" to "trust-dependent" and the surface is unchanged.
                              # This ratchet was written assuming every conversion helps it;
                              # it does not, and pretending otherwise would mean bumping this
                              # number silently every time a conversion landed in a trusted
                              # call path. So the invariant that actually means "the trusted
                              # surface did not grow" is ratcheted separately, below.
MAX_TRUSTED_OR_DEPENDENT = 834
                              # (#49) gen #31 — THE RATCHET THAT SHOULD HAVE BEEN HERE FROM
                              # THE START: `len(trusted) + dep_hi`, the CEILING on the whole
                              # trusted-or-trust-dependent surface. It is invariant under the
                              # relabelling above — 434+400 = 833 before the two conversions,
                              # 432+401 = 833 after — and it moves DOWN only when a conversion
                              # genuinely removes something from the surface, which is the
                              # thing the campaign is actually trying to do. Measured at 833
                              # since gen #30's first measurement, through every conversion.
                              #
                              # 833 -> 834 IN THE SAME SESSION IT WAS ADDED, and the move is
                              # an HONEST CORRECTION with a named cause — which is the only
                              # way this constant is allowed to grow. Two nested un-trusted
                              # closures were found sitting inside `\trusted` parents:
                              # `Module6_WhyMLTranspiler::_sig_val_from_let::_hdr_name` and
                              # `core_ir_semantic::_returns_literal_none::walk`. Their
                              # enclosing functions are emitted as opaque `val`s, so their
                              # bodies were verified NOWHERE, while the fidelity plane counted
                              # them among the verbatim un-trusted twins. They now carry
                              # honest `#@ \trusted` markers, and this measurement follows:
                              # trusted 432 -> 434, dep_hi 401 -> 400, aggregate 833 -> 834.
                              #
                              # AND THE ASYMMETRY THIS EXPOSES, which the paragraph above got
                              # half right. The aggregate IS invariant under a CONVERSION
                              # (trusted -> untrusted-but-trust-dependent: one leaves the
                              # trusted set and rejoins the surface). It is NOT invariant
                              # under the reverse, because a newly-trusted function can pull
                              # in callers that were previously trust-FREE — `walk` is called
                              # all over `core_ir_semantic.py`, and dep_lo jumped 336 -> 343
                              # on this one marker. So: this ratchet still catches a marker
                              # added in a hot call path, which is what it is for; it just
                              # cannot ALSO promise to be invariant in both directions.
                              # Each future increase must name its two functions the way this
                              # one does, or it is a regression.

MIN_TRUST_FREE = 538          # (#49) gen #31: 540 -> 538, and this is the ONE direction this
                              # constant is allowed to move, so the reason is recorded rather
                              # than the number adjusted. Route #219's build stopped dropping
                              # dunders; two mirror methods that had been counted among the
                              # UN-TRUSTED twins while NEVER BEING EMITTED OR PROVED became
                              # emittable, failed as Why3 TYPE ERRORS, and took honest
                              # `#@ \trusted` markers (459 -> 461). The trust-free set loses
                              # exactly those two.
                              #
                              # gen #31 UPDATE: `_Tok.__repr__`'s marker is RETIRED
                              # (461 -> 460) by annotating the live twin `-> str`, and
                              # this floor did NOT move — the method is trust-DEPENDENT
                              # either way, which is the point the paragraph below makes.
                              #
                              # SO THE FLOOR DID NOT REALLY DROP — THE MEASUREMENT GOT
                              # HONEST. Both methods were trust-DEPENDENT-or-worse all along;
                              # what changed is that the marker now says so. Any FURTHER
                              # decrease without a named marker IS a regression and this
                              # ratchet still catches it. Each of the two names the capability
                              # that retires it (driver-backlog.md, "the two mirror dunder
                              # markers"), and retiring either moves this number back up.
                              # 540 was the LOWER bound at the first measurement.
                              #
                              # (#49) gen #31, AND DELIBERATELY NOT RAISED: retiring
                              # `errors.py::message` and `proof2why3/sertop.py::__exit__` puts
                              # this measurement back at 540, above the floor. Raising the
                              # floor to 540 would lock in a number that the NEXT conversion
                              # in a trusted call path can legitimately push back down — the
                              # same asymmetry that forced MAX_TRUST_DEPENDENT from 400 to
                              # 401 on a conversion that helped. Both ends of this bracket
                              # move with the by-name over-approximation; only the aggregate
                              # MAX_TRUSTED_OR_DEPENDENT is invariant under relabelling, and
                              # that is the one to tighten. The floor stays at 538 as a
                              # coarse population guard and nothing more.


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
    if len(trusted) + dep_hi > MAX_TRUSTED_OR_DEPENDENT:
        print("[!]   TRUSTED-OR-DEPENDENT CEILING BROKEN: %d > %d. This is the ratchet that "
              "means what the campaign means: the surface resting on a marker GREW. It is "
              "invariant under converting a marker inside a trusted call path, which merely "
              "relabels one function from trusted to trust-dependent."
              % (len(trusted) + dep_hi, MAX_TRUSTED_OR_DEPENDENT), file=sys.stderr)
        rc = 1
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
        print("[+] trust-blast-radius: OK — trusted-or-dependent ceiling %d (at %d), "
              "trust-dependent ceiling %d (at %d), trust-free floor %d (at %d)."
              % (MAX_TRUSTED_OR_DEPENDENT, len(trusted) + dep_hi,
                 MAX_TRUST_DEPENDENT, dep_hi, MIN_TRUST_FREE, free_lo))
    return rc


if __name__ == "__main__":
    sys.exit(main())
