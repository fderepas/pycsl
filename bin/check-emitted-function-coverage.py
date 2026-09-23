#!/usr/bin/env python3
r'''THE EMITTED-FUNCTION COVERAGE PLANE: does the module the prover sees still CONTAIN the
functions the author wrote?

WHY THIS EXISTS (#49, gen #30). `check-clause-survival` asks whether every `#@ requires` /
`#@ ensures` reached the emission. This asks the blunter question underneath it: **did the
FUNCTION reach the emission at all?** A function the emitter drops takes its contract, its
body and — this is the part that bites — every OBLIGATION ABOUT IT with it, and the run
still prints

    [+] Verification SUCCESS! All contracts formally proven.

ROUTE #216 IS WHAT THIS PLANE IS FOR. Two files identical except for one identifier, under
`--check-behavioral-subtyping`: `Sub.m` violating `Base.m`'s postcondition FAILS with
`goal sub__m_refines_base`; the same violation spelled `__len__` SUCCEEDS, over an emitted
module whose entire body is `type sub = {  }`. No methods, no pair, no goal. The
substitutability obligation did not fail — it was never built.

WHAT IT MEASURES. For every corpus file with a fresh emission that is NOT a
`# pycsl-expected: FAIL` witness, the source `def`s (excluding `__init__`, which is inlined
by design and is route #15's business, not this plane's) are matched against the `let` /
`val` / `with` names in the emitted module. A file where NONE of its functions survived is
a ZERO-COVERAGE file: whatever its verdict says, it says it about nothing.

MEASURED AT THE TREE THIS LANDED ON: 912 files compared, 1 zero-coverage, 5 partial, and
**every single dropped function in the entire corpus is a DUNDER** — `__del__`, `__hash__`,
`__eq__`, `__new__`, `__enter__`. That is a clean partition, and it is the ratchet: a
NON-DUNDER drop is unexplained and refused.

THE MATCHER TOOK THREE REPAIRS AND THEY ARE WORTH RECORDING (lesson (p3): print the
members before you write a ceiling). Each repair REMOVED a false positive, i.e. the first
version of this plane would have reported drops that were not drops:

  1. `let lemma NAME` — a `#@ lemma` lowers to `let lemma sum_nonneg …`. Without `lemma`
     in the keyword set, corpus 0558 and 0581 read as ZERO-COVERAGE.
  2. `let function py_check` — a module-level function can be emitted with a `py_` PREFIX
     (0603). Without it, 0603 read as ZERO-COVERAGE.
  3. `with function size_forest` — a mutually-recursive group is `let rec f … with g …`,
     so the second member is introduced by `with`, not by `let` (0534, 0966). Without it,
     two NON-DUNDER drops appeared, which is exactly the signal this plane refuses on, and
     the plane would have opened with a false alarm.

SOUND IN ONE DIRECTION, like its siblings: a name that MATCHES does not prove the body is
faithful; a name that is ABSENT proves the function is not there.

Usage:  bin/check-emitted-function-coverage.py --emit-dir <dir> [--verbose]
        [--selftest-unknown-drop]
'''
import argparse
import ast
import os
import re
import sys
import warnings

CORPUS = "test-suite/corpus/pycsl-reference"

# A dropped DUNDER was a known, named completeness gap: witness
# `1800_gen30_dunder_call_loses_its_contract.py` pinned the call-site shape (a contractless
# `val`) and route #216 pinned the dangerous corollary (a dropped dunder takes a Liskov
# obligation with it and the run still says SUCCESS). This header said "It closes when
# dunders are emitted."
#
# (#49) gen #31 — IT CLOSED. Route #219 (every check, VC and UB detector switched off by the
# method's NAME) made the case, and `Module5_IREmitter._should_skip_method` now skips only
# the CONSTRUCTOR HOOKS. The measurement across the same 922 corpus files went
#     8 dropped functions, 1 ZERO-COVERAGE   ->   1 dropped function, 0 ZERO-COVERAGE
# and the one that remains is `0496.py::__new__`, still skipped because emitting a
# return-annotated `__new__` is a Why3 TYPE ERROR (review oracle O9) and UB-7.6 already pins
# it to the trivial form. `__post_init__` is skipped too, for route #150's reasons, and does
# not appear here because no corpus file loses its ONLY function to it.
#
# MAX_ZERO_COVERAGE IS NOW ZERO AND THAT IS THE RATCHET THAT MATTERS: 0402 used to be the
# one file whose every function was dropped, and it now emits (and verifies) its `__del__`
# under an honest `#@ assigns self._n`, with corpus 1826 as the twin that proves the check
# bites. A file losing ALL its functions again is a regression, not a known gap.
MAX_ZERO_COVERAGE = 0
MIN_COMPARED = 800

# Empty, and it should stay that way. An entry here says "every function in this file is
# dropped and that is fine"; the campaign spent a generation learning that such a sentence
# outlives its reason (`check-untrusted-emitted`'s allow-list said "dunders are modelled
# structurally" while the emitter simply dropped them, and two mirror functions sat in the
# VERIFIED population for a generation because of it). Mechanically re-checked: an entry is
# only honoured while all of that file's missing defs really are dunders.
KNOWN_ZERO = {}

_KW = r"(?:rec|ghost|function|predicate|lemma|constant)\s+"
_DEF_RE = re.compile(r"\b(?:let|val|with)\s+(?:" + _KW + r")*([A-Za-z_][A-Za-z0-9_']*)")


def emitted_idents(text):
    return set(_DEF_RE.findall(text))


def is_dunder(name):
    return name.startswith("__") and name.endswith("__") and len(name) > 4


def present(d, idents):
    """Does source `def d` appear in the emission under any of its emitted spellings?"""
    cands = {d, "py_" + d}
    return any(i in cands or any(i.endswith("__" + c) for c in cands) for i in idents)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", required=True,
                    help="directory of FRESHLY emitted corpus .mlw (bin/byte-diff-sweep.sh)")
    ap.add_argument("--corpus", default=CORPUS)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest-unknown-drop", action="store_true",
                    help="treat `__enter__` as a non-dunder; the plane must REFUSE (rc=1)")
    args = ap.parse_args()

    def _dunder(n):
        if args.selftest_unknown_drop and n == "__enter__":
            return False
        return is_dunder(n)

    compared = 0
    zero, partial, non_dunder = [], [], []
    for f in sorted(os.listdir(args.corpus)):
        if not f.endswith(".py"):
            continue
        mlw = os.path.join(args.emit_dir, f[:-3] + ".mlw")
        if not os.path.exists(mlw):
            continue                       # refused on purpose, or not emitted
        src_path = os.path.join(args.corpus, f)
        src = open(src_path, encoding="utf-8", errors="replace").read()
        if "# pycsl-expected: FAIL" in src[:4096]:
            continue                       # its clauses are not claims this project makes
        try:
            # Corpus files legitimately contain `\result`-style escapes in docstrings;
            # ast.parse warns about them and the warnings are not this plane's business.
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(src)
        except SyntaxError:
            continue
        defs = [n.name for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name != "__init__"]
        if not defs:
            continue
        compared += 1
        idents = emitted_idents(open(mlw, encoding="utf-8", errors="replace").read())
        missing = [d for d in defs if not present(d, idents)]
        if not missing:
            continue
        for d in missing:
            if not _dunder(d):
                non_dunder.append((f, d))
        if len(missing) == len(defs):
            zero.append((f, missing))
        else:
            partial.append((f, missing))

    for f, miss in zero:
        print("    ZERO-COVERAGE  %-46s none of %d function(s) survived: %s"
              % (f, len(miss), ", ".join(miss)))
    if args.verbose:
        for f, miss in partial:
            print("    PARTIAL        %-46s dropped: %s" % (f, ", ".join(miss)))

    print("[*] emitted-function-coverage: %d corpus file(s) compared; %d ZERO-COVERAGE, "
          "%d partial drop(s), %d dropped function(s) of which %d are NOT dunders."
          % (compared, len(zero), len(partial),
             sum(len(m) for _f, m in zero + partial), len(non_dunder)))

    # (#44) A gate that cannot tell "nothing is dropped" from "I compared nothing".
    if compared < MIN_COMPARED:
        print("[!] emitted-function-coverage: REFUSING — only %d file(s) compared, expected "
              "at least %d. The --emit-dir is empty, stale or partial, and a clean report "
              "over it would be a FALSE GREEN, not a pass." % (compared, MIN_COMPARED))
        return 2

    if non_dunder:
        print("[!] emitted-function-coverage: %d NON-DUNDER function(s) dropped from an "
              "emission whose run can still report 'All contracts formally proven':"
              % len(non_dunder))
        for f, d in non_dunder:
            print("        %-46s %s" % (f, d))
        print("    Every drop measured when this plane landed was a DUNDER (a named gap: "
              "witness 1800, route #216). A drop outside that family is unexplained — and "
              "a dropped function takes every obligation ABOUT it with it, which is how "
              "route #216 certifies a Liskov violation. Diagnose it; do not widen the "
              "family to fit.")
        return 1

    stale = sorted(set(KNOWN_ZERO) - {f for f, _m in zero})
    for f in stale:
        print("[+] emitted-function-coverage: %s is no longer zero-coverage — delete its "
              "KNOWN_ZERO entry." % f)

    unledgered = [f for f, _m in zero if f not in KNOWN_ZERO]
    if unledgered or len(zero) > MAX_ZERO_COVERAGE:
        print("[!] emitted-function-coverage: %d ZERO-COVERAGE file(s) (ratchet %d), %d of "
              "them with no KNOWN_ZERO entry: %s. A file whose every function was dropped "
              "gets its verdict about NOTHING."
              % (len(zero), MAX_ZERO_COVERAGE, len(unledgered), ", ".join(unledgered)))
        return 1

    print("[+] emitted-function-coverage: OK — every dropped function is a DUNDER (the "
          "named gap), %d zero-coverage file(s) all ledgered, 0 non-dunder drops."
          % len(zero))
    return 0


if __name__ == "__main__":
    sys.exit(main())
