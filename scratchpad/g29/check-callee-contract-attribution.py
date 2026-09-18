#!/usr/bin/env python3
r"""WHICH CALLEE DOES THIS CALL SITE GET? — a named, EXECUTABLE ratchet.

THE DEFECT CLASS. A stubbed method call carries the CALLEE'S CONTRACT — its `ensures`,
the `requires` route #167 asserts, the `raises` route #100 discharges. Deciding WHICH
callee that is, is a name resolution, and a name resolution has exactly three honest
answers:

  CORRECT        the call site gets its own callee's contract (or no contract at all,
                 which is merely incomplete).
  REFUSED        the pipeline raises with a diagnostic — fail-CLOSED, the honest answer
                 for a receiver whose class the model cannot pin to ONE class.
  MIS-ATTRIBUTED the call site gets ANOTHER callee's contract. **This is the ratchet, and
                 it is a fail-OPEN: the model does not merely fail to know the answer, it
                 KNOWS A WRONG ONE.**

WHY THIS PLANE EXISTS. Five of gen #29's routes are this one question asked five ways:

  #166  two call sites, one stub NAME — `o.get()` on a `C` and on a `D` both registered
        `o_get_0`, and the clash was resolved by KEEPING THE LONGER declaration.
  #185  a `self.<field>.<m>()` receiver mis-KEYED the callee, so routes #167 and #176
        looked up nothing and emitted neither obligation.
  #186  the same mis-keying on the `raises` wrap, so a declared `#@ raises E when P`
        produced no `assert { not P }`.
  #188  #166's disambiguating suffix is a 100000-bucket hash of the declaration, and two
        declarations whose suffixes collide share one contract again.
  #189  one receiver NAME bound to two classes on two branches resolved to ONE of them,
        and the single call site carried that class's `ensures` on every path.

Every one of them was found by hand, and the battery's thirty-four planes watch value
models, frames, trust honesty, erasures and mirrors — none watches attribution. This is
that plane.

HOW IT MEASURES, and why it is EXECUTABLE rather than static. The answer is not readable
off the source: it depends on `_resolve_dotted_signature`'s receiver branches, on
`IRScanner.find_record_var_classes`, on the `_c<hash>` stub-name suffix and on which arm
of `_handle_dotted_call` a spelling reaches. So the plane GENERATES, for each (receiver
spelling, callee kind) pair, a driver in which TWO classes carry the SAME method name with
DIFFERENT contracts, the call site uses the SECOND one, and the contract asserts what the
FIRST one's contract would give — a claim that is FALSE of the program by construction —
and runs the real pipeline on it:

    pipeline raises            -> REFUSED         (fail-closed)
    verification SUCCEEDS      -> MIS-ATTRIBUTED  (a false contract proved: A FINDING)
    verification FAILS         -> CORRECT         (the model does not decide it away)

A MIS-ATTRIBUTED cell not in the baseline is a failure. So is a baseline entry whose cell
has changed answer, and so is a baseline entry that no longer matches any cell — a
baseline that outlives its site hides the next one.

WHAT IT DOES NOT CHECK, stated so nobody reads more into a green run than is there: only
the receiver spellings and callee kinds NAMED BELOW, only for a two-class file, and only
where the wrong answer is DECIDABLE (a spelling whose stub carries no contract at all
reads CORRECT here, and it is the `check-constant-fallthrough` / `check-emitted-vacuity`
planes that watch whether that silence is itself a decision). Attribution ACROSS MODULES
(an imported class whose method name collides with a local one) is outside this table.
"""
import argparse
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")

# The two classes every driver carries. `Alpha.get` and `Beta.get` share a NAME and
# differ in their CONTRACT, which is the whole point: a call site that reaches `Beta`
# and proves `Alpha`'s answer has been mis-attributed.
PAIR_ENSURES = '''class Alpha:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \\result == 1
    def get(self) -> int:
        return 1


class Beta:
    def __init__(self) -> None:
        self.k = 2

    #@ ensures \\result == 2
    def get(self) -> int:
        return 2
'''

# `Beta.get` is GUARDED and its guard is FALSE at the call site (`self.k == 0`), so the
# call raises ZeroDivisionError in Python. A caller that proves a result has taken
# `Alpha`'s unguarded contract, or has skipped route #167's precondition assert.
PAIR_REQUIRES = '''class Alpha:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \\result == 7
    def get(self) -> int:
        return 7


class Beta:
    def __init__(self) -> None:
        self.k = 0

    #@ requires self.k != 0
    #@ ensures \\result == 1
    def get(self) -> int:
        return self.k // self.k
'''

# `Beta.go` DECLARES that it raises, and the caller declares `#@ no_exception ValueError`
# over a call whose argument satisfies the declared condition. A caller that proves has
# never been handed the `assert { not P }` (routes #100 / #186).
PAIR_RAISES = '''class Alpha:
    def __init__(self) -> None:
        self.k = 1

    #@ ensures \\result == 0
    def go(self, v: int) -> int:
        return 0


class Beta:
    def __init__(self) -> None:
        self.k = 2

    #@ raises ValueError when v < 0
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v
'''

HEAD = "from typing import List\n_ = 0  # anchor\n\n\n"

# (spelling, kind) -> the driver tail that reaches `Beta` through that spelling.
# `{m}` is the method call on the Beta receiver; `{claim}` the FALSE postcondition.
TAILS = {
    "local": '''{ann}#@ ensures {claim}
def probe() -> int:
    o = Beta()
    return o.{call}
''',
    "module-global": '''_bg = Beta()


{ann}#@ ensures {claim}
def probe() -> int:
    return _bg.{call}
''',
    "self-field": '''class Outer:
    def __init__(self) -> None:
        self.inner = Beta()

    {ann}#@ ensures {claim}
    def run(self) -> int:
        return self.inner.{call}
''',
    "two-level-field": '''class Mid:
    def __init__(self) -> None:
        self.leaf = Beta()


class Top:
    def __init__(self) -> None:
        self.mid = Mid()

    {ann}#@ ensures {claim}
    def run(self) -> int:
        return self.mid.leaf.{call}
''',
    "list-element": '''{ann}#@ ensures {claim}
def probe() -> int:
    xs: List[Beta] = [Beta()]
    return xs[0].{call}
''',
    "call-returned": '''def make() -> Beta:
    return Beta()


{ann}#@ ensures {claim}
def probe() -> int:
    return make().{call}
''',
    "parameter": '''{ann}#@ ensures {claim}
def use(b: Beta) -> int:
    return b.{call}
''',
    # THE BRANCH ORDER IS LOAD-BEARING, and getting it wrong once is why this comment
    # exists. `IRScanner.find_record_var_classes` walks `body` then `orelse` into ONE flat
    # map, so the ORELSE binding wins. Put `Beta` — the class the call actually reaches on
    # the `flag > 0` path — in the IF branch and `Alpha` in the ELSE, and the pre-#189
    # emitter resolves `o` to `Alpha` and proves Alpha's claim: MIS-ATTRIBUTED, which is
    # the verdict this cell must be able to produce. With the branches the other way round
    # the same file reads CORRECT and the cell tests nothing (measured, both ways, against
    # the pre-#189 tree).
    "two-branch": '''{ann}#@ ensures {claim}
def probe(flag: int) -> int:
    if flag > 0:
        o = Beta()
    else:
        o = Alpha()
    return o.{call}
''',
}

# (spelling, kind). `kind` selects the class pair, the call and the FALSE claim.
KINDS = {
    # Beta.get answers 2; the claim is Alpha's 1.
    "ensures":  (PAIR_ENSURES,  "get()",   "\\result == 1"),
    # Beta.get's guard is false (k == 0) so Python raises; the claim is Alpha's 7.
    "requires": (PAIR_REQUIRES, "get()",   "\\result == 7"),
    # Beta.go(-1) raises; the claim is Alpha's 0, under a no_exception context.
    "raises":   (PAIR_RAISES,   "go(0 - 1)", "\\result == 0"),
}

CASES = (
    [(s, "ensures") for s in TAILS]
    + [(s, "requires") for s in ("local", "self-field", "two-branch")]
    + [(s, "raises") for s in ("local", "self-field", "two-branch")]
)

# ---------------------------------------------------------------------------
# THE BASELINE.  (spelling, kind) -> the answer this gate expects.
# A cell whose answer differs, a MIS-ATTRIBUTED cell that is not recorded here, or an
# entry with no matching cell, is a FAILURE. Every cell is CORRECT or REFUSED: after
# routes #185/#186/#188/#189 there is no mis-attributed spelling left in this table,
# and a new one appearing is exactly what this plane is for.
# ---------------------------------------------------------------------------
BASELINE = {
    ("local", "ensures"):           "CORRECT",
    ("module-global", "ensures"):   "CORRECT",
    ("self-field", "ensures"):      "CORRECT",
    ("two-level-field", "ensures"): "CORRECT",
    ("list-element", "ensures"):    "REFUSED",
    ("call-returned", "ensures"):   "CORRECT",
    ("parameter", "ensures"):       "CORRECT",
    ("two-branch", "ensures"):      "REFUSED",
    ("local", "requires"):          "CORRECT",
    ("self-field", "requires"):     "CORRECT",
    ("two-branch", "requires"):     "REFUSED",
    ("local", "raises"):            "CORRECT",
    ("self-field", "raises"):       "CORRECT",
    ("two-branch", "raises"):       "REFUSED",
}


def classify(spelling, kind, keep):
    pair, call, claim = KINDS[kind]
    # The `no_exception` context is what makes a missing `assert { not P }` DECIDABLE
    # rather than merely absent. It goes in the template's `{ann}` slot, which sits at
    # the contract block's own indentation (a method's block is indented four spaces).
    indent = "    " if spelling in ("self-field", "two-level-field") else ""
    ann = ("#@ no_exception ValueError\n" + indent) if kind == "raises" else ""
    tail = TAILS[spelling].format(call=call, claim=claim, ann=ann)
    src = HEAD + pair + "\n\n" + tail
    fd, path = tempfile.mkstemp(suffix=".py", prefix="attrib_", dir=keep)
    with os.fdopen(fd, "w") as fh:
        fh.write(src)
    try:
        out = subprocess.run(
            [sys.executable, PYCSL, path],
            capture_output=True, text=True, timeout=600).stdout
    except subprocess.TimeoutExpired:
        return "TIMEOUT", path
    # A BROKEN ENVIRONMENT IS NOT A VERDICT: without why3 on PATH every cell would read
    # REFUSED and the whole table would move off its baseline at once. The rest of the
    # battery treats a missing why3 as SKIP-NOT-FAIL; this matches.
    if "'why3' command not found" in out or "why3 command not found" in out:
        return "NO-WHY3", path
    if "PIPELINE ERROR" in out:
        return "REFUSED", path
    if "Verification SUCCESS" in out:
        return "MIS-ATTRIBUTED", path
    return "CORRECT", path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--keep-dir", default=None,
                    help="write the generated drivers here instead of a temp dir")
    args = ap.parse_args()

    keep = args.keep_dir or tempfile.mkdtemp(prefix="attrib_")
    os.makedirs(keep, exist_ok=True)

    results = []
    for spelling, kind in CASES:
        verdict, path = classify(spelling, kind, keep)
        results.append((spelling, kind, verdict, path))

    if not results:
        print("[!] callee-contract-attribution: 0 case(s) — that is not a measurement. "
              "NOT A PASS.", file=sys.stderr)
        return 2

    nowhy3 = [r for r in results if r[2] == "NO-WHY3"]
    if nowhy3:
        print("[*] callee-contract-attribution: skipped — why3 is not on PATH, so pycsl "
              "could not run (%d of %d case(s)). A missing tool is NOT a verdict."
              % (len(nowhy3), len(results)))
        return 0

    bad = [r for r in results if r[2] == "MIS-ATTRIBUTED"]
    changed = [r for r in results
               if BASELINE.get((r[0], r[1])) not in (None, r[2])]
    unknown = [r for r in results if (r[0], r[1]) not in BASELINE]
    stale = sorted(set(BASELINE) - {(r[0], r[1]) for r in results})

    print("[*] callee-contract-attribution: %d case(s) — %d CORRECT, %d REFUSED, "
          "%d MIS-ATTRIBUTED." % (len(results),
                                  sum(1 for r in results if r[2] == "CORRECT"),
                                  sum(1 for r in results if r[2] == "REFUSED"),
                                  len(bad)))
    if args.verbose or bad or changed or unknown:
        for spelling, kind, verdict, _p in results:
            exp = BASELINE.get((spelling, kind), "(not baselined)")
            mark = "    " if exp == verdict else "CHG "
            print("    %s%-16s %-9s -> %-15s baseline %s"
                  % (mark, spelling, kind, verdict, exp))

    rc = 0
    for spelling, kind, verdict, path in changed:
        print("[!] callee-contract-attribution: %s/%s is now %s, baseline says %s. If it "
              "became MIS-ATTRIBUTED, a call site is proving ANOTHER callee's contract — "
              "read the generated driver at %s and probe it end to end."
              % (spelling, kind, verdict, BASELINE[(spelling, kind)], path),
              file=sys.stderr)
        rc = 1
    for spelling, kind, verdict, path in unknown:
        print("[!] callee-contract-attribution: %s/%s -> %s has no baseline entry. "
              "Classify it (driver at %s)." % (spelling, kind, verdict, path),
              file=sys.stderr)
        rc = 1
    for spelling, kind in stale:
        print("[!] callee-contract-attribution: baseline entry (%s, %s) matches no case. "
              "Remove it — a baseline that outlives its site hides the next one."
              % (spelling, kind), file=sys.stderr)
        rc = 1
    if rc == 0:
        print("[+] callee-contract-attribution: OK — %d case(s), every one at its "
              "baseline; %d MIS-ATTRIBUTED, %s." % (
                  len(results), len(bad),
                  "each one recorded as an OPEN route in getting-better/open-routes/"
                  if bad else "none"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
