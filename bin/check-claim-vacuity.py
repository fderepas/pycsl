#!/usr/bin/env python3
r"""L-PLANE ORACLE: corpus contracts that are TRIVIALLY TRUE — a second kind of vacuity,
which the shipping non-vacuity gate is not looking for and was never meant to.

TWO DIFFERENT VACUITIES, AND ONLY ONE HAD AN INSTRUMENT (gen #30).

  CONTEXT VACUITY — the assumed context is INCONSISTENT, so the function proves anything.
  `pycsl.py::_run_vacuity_gate` probes exactly this, per function, by injecting `ensures {
  false }` and asking whether it proves. It is default-on and fail-closed, and it is
  correct on its own terms.

  CLAIM VACUITY — the context is perfectly consistent and the CONTRACT SAYS NOTHING.
  `#@ ensures True` is discharged by every program ever written. The gate above passes it,
  correctly: the context is consistent, so nothing is wrong by that definition.

Nothing measured the second one, and the second one is most of the corpus.

THE MEASUREMENT (gen #30): **1791 of 3888 corpus files — 46% — carry at least one `#@
ensures True`** (1847 occurrences), and 1131 carry a `#@ requires True`. The shape of the
population is what makes it matter:

    840 files named `*_call_fails.py`  — every one carries `ensures True`
    840 files named `*_call_proves.py` — every one carries `ensures True`

Those two families are the stdlib L5 witnesses, and their names assert OPPOSITE outcomes.
Their contracts are IDENTICAL and neither can fail. A representative one says so in its
own docstring: "callers that don't establish the function's precondition fail to verify
under full proof. The corpus runner uses `--no-proof` for fast iteration; the failure mode
is exercised manually with `--proof`." Run it with the prover on and it VERIFIES —
`ensures True` over an unresolved stdlib call is discharged, so the documented failure mode
does not occur. Measured on a 40-file sample of the `--no-proof` population: 38 verify
under full proof, 1 fails, 1 reports a mutex-invariant diagnostic. Then measured on the
`*_call_fails.py` family directly, 60 sampled of the 840: **60 of 60 VERIFY under full
proof.** Not one of the sampled negative witnesses fails, because not one of them claims
anything a program could contradict.

WHAT THIS IS NOT: not a route, not a compiler defect, and not an argument that `ensures
True` should be rejected — a placeholder contract is a legitimate thing to write while a
model is being built. It IS an argument that "N tests pass" must not be read as "N
contracts hold", and that a witness whose name claims a failure mode owes a contract that
can fail.

THE RATCHET: the claim-vacuous file count may only SHRINK. Giving one of these files a real
postcondition is the way down, and it is the cheapest verification work in the repo.
THE POPULATION GUARD (the #44 rule): rc=2 below MIN_FILES corpus files.

Usage:  bin/check-claim-vacuity.py [--verbose] [--family NAME]
"""
import argparse
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "test-suite", "corpus")
MIN_FILES = 3500              # 3888 at the first measurement
MAX_VACUOUS_FILES = 1791      # 1792 at the first measurement; ONE repaired the same day
                              # (statistics/median_high_call_fails.py), so the ceiling
                              # follows it down — that is what "may only shrink" means
MAX_VACUOUS_REQUIRES = 1131   # ditto, for `requires True`

# (#49) gen #30 — WHAT THIS DETECTOR CANNOT SEE, MEASURED RATHER THAN ASSUMED. The count
# below is reported as "N files carry a trivially true postcondition", which reads as a
# complete census and was never checked to be one. Three broader syntactic families were
# scanned over all 3973 corpus files to find out what the three spellings miss:
#   * `ensures A <op> A` for the SAME text on both sides (`\result >= \result`,
#     `x == x`, `\old(n) <= \old(n)`): ZERO additional files.
#   * `ensures <lit> <op> <lit>` for every comparison, not just `==` (`1 > 0`, `2 != 3`):
#     ZERO additional files beyond the one `1 == 1` already counted (corpus 0317).
# So for THIS corpus the three spellings are complete over literal and reflexive
# tautologies, and the headline number is not an undercount hiding behind a narrow regex.
# The operator set of TRIVIAL_LIT was widened anyway, so a future `ensures 1 > 0` is caught
# by construction rather than by someone repeating this audit.
#
# STILL INVISIBLE, and named so the claim stays honest: SEMANTIC tautologies that are not
# syntactic (`ensures \result == \result + 0`, `ensures n >= 0 or n < 0`,
# `ensures True and \result == \result`). Catching those needs the expression
# evaluator, not a regex — `pycsl.py::_run_vacuity_gate` is the mechanism that could, and
# wiring it to this census is the reopening capability.
TRIVIAL_ENSURES = (
    re.compile(r"#@\s*ensures\s+True\s*$"),
    re.compile(r"#@\s*ensures\s+\\result\s*==\s*\\result\s*$"),
)
TRIVIAL_LIT = re.compile(r"#@\s*ensures\s+(-?\d+)\s*(==|!=|>=|<=|>|<)\s*(-?\d+)\s*$")
TRIVIAL_REQUIRES = re.compile(r"#@\s*requires\s+True\s*$")


def scan():
    files = sorted(glob.glob(os.path.join(CORPUS, "**", "*.py"), recursive=True))
    vac_files, req_files, occurrences = set(), set(), 0
    fam = collections.Counter()
    for f in files:
        for raw in open(f, errors="replace"):
            line = raw.strip()
            hit = any(p.match(line) for p in TRIVIAL_ENSURES)
            if not hit:
                m = TRIVIAL_LIT.match(line)
                if m:
                    _a, _op, _b = int(m.group(1)), m.group(2), int(m.group(3))
                    hit = {"==": _a == _b, "!=": _a != _b, ">=": _a >= _b,
                           "<=": _a <= _b, ">": _a > _b, "<": _a < _b}[_op]
            if hit:
                occurrences += 1
                vac_files.add(f)
                fam[os.path.basename(f).rsplit("_", 1)[-1][:-3]] += 1
            elif TRIVIAL_REQUIRES.match(line):
                req_files.add(f)
    return files, vac_files, req_files, occurrences, fam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--family", help="list the claim-vacuous files whose name ends in "
                                     "_NAME.py")
    args = ap.parse_args()

    files, vac, req, occ, fam = scan()
    if len(files) < MIN_FILES:
        print("[!] claim-vacuity: REFUSING — %d corpus file(s) found, expected at least "
              "%d. The walk is broken; this is not a pass." % (len(files), MIN_FILES),
              file=sys.stderr)
        return 2

    print("[*] claim-vacuity: %d corpus file(s); %d carry a TRIVIALLY TRUE postcondition "
          "(%d occurrence(s)); %d carry `requires True`."
          % (len(files), len(vac), occ, len(req)))
    top = fam.most_common(4)
    print("[*] claim-vacuity: top name families — %s"
          % ", ".join("%s: %d" % (k or "(none)", v) for k, v in top))
    if args.family:
        for f in sorted(x for x in vac if x.endswith("_%s.py" % args.family)):
            print("    %s" % os.path.relpath(f, ROOT))
    elif args.verbose:
        for f in sorted(vac)[:40]:
            print("    %s" % os.path.relpath(f, ROOT))

    rc = 0
    if len(vac) > MAX_VACUOUS_FILES:
        print("[!]   CLAIM-VACUOUS FILE COUNT GREW: %d > %d. A new corpus file whose "
              "postcondition is `True` adds a test that cannot fail."
              % (len(vac), MAX_VACUOUS_FILES), file=sys.stderr)
        rc = 1
    if len(req) > MAX_VACUOUS_REQUIRES:
        print("[!]   `requires True` FILE COUNT GREW: %d > %d."
              % (len(req), MAX_VACUOUS_REQUIRES), file=sys.stderr)
        rc = 1

    if rc:
        print("[!] claim-vacuity: NOT OK.", file=sys.stderr)
    else:
        print("[+] claim-vacuity: OK — %d/%d claim-vacuous file(s) at the ceiling (%d); "
              "the two families whose names assert opposite outcomes (`*_call_proves.py`, "
              "`*_call_fails.py`) still carry the SAME contract."
              % (len(vac), len(files), MAX_VACUOUS_FILES))
    return rc


if __name__ == "__main__":
    sys.exit(main())
