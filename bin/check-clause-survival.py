#!/usr/bin/env python3
r"""check-clause-survival.py — THE CLAUSE-SURVIVAL PLANE.

THE QUESTION NO OTHER PLANE ASKS: does every `#@ requires` / `#@ ensures` the author wrote
actually REACH the emitted WhyML? Every other gate looks at what the emission CONTAINS.
This one looks for what it is MISSING, by comparing the source clause count against the
emitted one.

The comparison is sound in one direction and that is the whole trick: **the emitter only
ever ADDS `requires` / `ensures` lines** — frame-preservation postconditions (#34), implicit
exception triggers, class invariants, `\result` refinements, the abstract ops' own
contracts. It never merges two source clauses into one line. So

    emitted count < source count   =>   at least one clause did not survive.

The converse is not true (a clause can be emitted as the literal `true` and still be
counted), so this plane is a LOWER BOUND, exactly like `check-emitted-vacuity.py`.

WHAT IT FOUND ON ITS FIRST RUN (route #15, relaunch #43): 25 of 820 corpus files carry a
deficit, and corpus 0706's was `ensures 1 -> 0` with NO CONSTRUCTOR IN THE EMITTED MODULE
AT ALL. `__init__` is never emitted as a function — it is inlined at each allocation site —
so its `#@ requires` and `#@ ensures` are DISCARDED, and

    #@ ensures self.x == 99      over a body `self.x = 0`
    [+] Verification SUCCESS! All contracts formally proven.

61 `__init__` methods across the corpus, the mirror and `src/pycsl_lib` carry such a
contract. The `init_ensures` IR field exists and IS re-checked — but only for classes with
a module-global singleton (`module6_whyml/preamble.py`).

USAGE
    bin/check-clause-survival.py --emit-dir <dir>

`<dir>` holds the emitted `.mlw` for the corpus, e.g. the output of
`bin/byte-diff-sweep.sh`. THE EMISSION MUST BE FRESH: a stale directory makes this plane a
false green, the same way `--emit` does for `check-emitted-vacuity.py`.

RATCHET: the number of files carrying a deficit. It goes down, never up.
"""
import argparse
import io
import os
import re
import sys
import tokenize

CORPUS = "test-suite/corpus/pycsl-reference"

# (#43) 4, and ALL FOUR ARE ROUTE #15 — a constructor contract that never reaches the
# emission. 0661 and 0662 are the ones that show its size: each writes NINETEEN
# non-trivial `#@ requires` on `Inode.__init__` (`\valid(initial, 18)` and eighteen
# per-field range bounds) and every one of them is discarded. 0705 loses a constructor
# `ensures`, 0706 the same. This plane therefore doubles as route #15's tracker: it goes
# to 0 when constructor contracts start being checked. Every one of these is a file
# whose emitted module carries fewer contract clauses than its author wrote. The bulk are
# constructor contracts (`__init__` is inlined, never emitted, so its clauses go nowhere);
# the rest are `requires True` normalizations. LOWER THIS as route #15 is paid off — the
# fix is a checking-only `let <class>__init` emitted beside the inlining.
MAX_DEFICIT_FILES = 4


def _source_counts(path):
    src = open(path, encoding="utf-8").read()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return None
    req = ens = 0
    for t in toks:
        if t.type != tokenize.COMMENT:
            continue
        st = t.string.strip()
        # real COMMENT tokens only — a line scan counts `#@` text inside docstrings, which
        # is how the route-#12 census first reported 95 hits where the truth was 0.
        # A `#@ requires True` / `#@ ensures True` carries no information and IS
        # legitimately normalized away (corpus 0950's only contract is exactly that, and
        # its emitted `let rec function has_bad` correctly has no clause at all). Counting
        # them made the plane's ratchet mostly noise. Excluded, so what remains is the
        # signal: a clause that says something and did not arrive.
        if st.startswith("#@ requires") and st.split(None, 2)[2:] != ["True"]:
            req += 1
        elif st.startswith("#@ ensures") and st.split(None, 2)[2:] != ["True"]:
            ens += 1
    return req, ens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", required=True,
                    help="directory of FRESHLY emitted corpus .mlw (bin/byte-diff-sweep.sh)")
    ap.add_argument("--corpus", default=CORPUS)
    ap.add_argument("--max-deficit-files", type=int, default=MAX_DEFICIT_FILES)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    deficits = []
    compared = 0
    for f in sorted(os.listdir(args.corpus)):
        if not f.endswith(".py"):
            continue
        mlw = os.path.join(args.emit_dir, f[:-3] + ".mlw")
        if not os.path.exists(mlw):
            continue          # refused on purpose (a `pycsl-expected: FAIL` witness)
        sc = _source_counts(os.path.join(args.corpus, f))
        if sc is None:
            continue
        s_req, s_ens = sc
        text = open(mlw, encoding="utf-8").read()
        # COUNT OCCURRENCES ANYWHERE, NOT AT LINE START. The first version of this
        # plane anchored both patterns at `^\s*` and immediately reported a
        # `ensures 5 -> 0` deficit on corpus 0964 — which was ITS OWN BUG: the emitter
        # writes `requires { true } ensures { true }` on ONE line for a leaf method, so
        # every such `ensures` was invisible to the count. Lesson (bd) on the instrument
        # this very plane was written to embody.
        e_req = len(re.findall(r"\brequires\s*\{", text))
        e_ens = len(re.findall(r"\bensures\s*\{", text))
        compared += 1
        if e_req < s_req or e_ens < s_ens:
            deficits.append((f, s_req, e_req, s_ens, e_ens))

    print("[*] clause-survival: %d corpus file(s) compared; %d carry a DEFICIT "
          "(an emitted clause count below the source count)." % (compared, len(deficits)))
    if args.verbose or len(deficits) > args.max_deficit_files:
        for d in deficits:
            print("    DEFICIT  %-50s requires %d->%d  ensures %d->%d" % d)

    if compared == 0:
        print("[!] clause-survival: ZERO files compared — the --emit-dir is empty or "
              "stale. That is a FALSE GREEN, not a pass.")
        return 1
    if len(deficits) > args.max_deficit_files:
        print("[!] clause-survival: RATCHET BROKEN — %d > %d. A clause the author wrote "
              "did not reach the emitted module, and the run will still report 'All "
              "contracts formally proven'." % (len(deficits), args.max_deficit_files))
        return 1
    if len(deficits) < args.max_deficit_files:
        print("[+] clause-survival: %d < ratchet %d — lower the constant."
              % (len(deficits), args.max_deficit_files))
    print("[+] clause-survival: OK — measured %d deficit file(s) of %d compared "
          "(ratchet %d)." % (len(deficits), compared, args.max_deficit_files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
