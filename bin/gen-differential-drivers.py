#!/usr/bin/env python3
r"""gen-differential-drivers.py — THE HUNTER-INDEPENDENT SAMPLER (Phase 6 of
`getting-better/convergence-metric-implement.md`).

WHY THIS EXISTS, AND WHY A RED HERE OUTRANKS A RED FROM THE DRIVER.

Measured 2026-09-13: **0 of 56 route files record a plane, ratchet or differential corpus
going red as the way the route was DISCOVERED.** All 56 were found by the driver probing.
The 34 planes have only ever confirmed closures and caught regressions. So the campaign has
no instrument independent of the hunter -- which is exactly why "is it converging?" can
currently only be narrated, not answered: an adaptive hunter's discovery rate tracks their
ideas, not the population.

`check-value-differential.py` is the right harness and the wrong population: its 56 drivers
are hand-written, one per closed route, so it measures what someone already knew. This
script keeps the harness and replaces the population with a MECHANICALLY GENERATED one over
the constructs the campaign has touched. **A RED here outranks a RED from the driver,
because the sampler did not know what it was looking for. That is the whole point.**

HOW IT WORKS

Each template is a small TOTAL Python program with an integer result. For every template
instance the generator:
  1. RUNS IT UNDER CPYTHON to obtain the ground-truth value. The generator never asserts a
     value of its own -- CPython is the oracle, exactly as the plane requires.
  2. Emits a matched PAIR of drivers:
       <name>_agree.py     `#@ ensures \result == <true value>`     MUST PROVE
       <name>_disagree.py  `#@ ensures \result == <true value + 1>` MUST BE REFUSED
     Both directions, always. A one-direction corpus is satisfiable by an emitter that
     refuses everything, which certifies nothing -- the #44 rule, and the reason
     check-value-differential.py carries its own population guard.
  3. DISCARDS any instance CPython raises on. These drivers must be TOTAL; a raising
     program is out of the value plane's scope (route #77's residue mistake, and #80 is
     what happens when the "it raises" claim is itself wrong).

WHERE IT WRITES, AND THE SKIP-LIST INTEGRATION

`test-suite/value-differential/generated/`. `check-value-differential.py`'s standing run
uses `os.listdir(DRIVERS)`, which does not recurse, so a SUBDIRECTORY IS SKIPPED BY
CONSTRUCTION -- the same mechanism that keeps `negative-test/` out of the standing run. The
generated corpus therefore cannot alter the standing gate's verdict, and is run explicitly:

    bin/check-value-differential.py --generated

YIELD AND WHAT "CONVERGING" MEANS

    yield = RED / generated, REPORTED PER TEMPLATE FAMILY.

**Converging = RED per 200 falls to 0 across THREE CONSECUTIVE RUNS WITH THE TEMPLATE SET
FROZEN.** Adding a family resets that clock FOR THE NEW FAMILY ONLY. `--fingerprint` prints
a per-family hash of the template source so a run can prove the set was frozen; a family
whose hash moved has a reset clock and must say so.

THE BLIND SPOT, TO BE STATED ALONGSIDE EVERY RUN (`--blind-spots` prints it):
  * Constructs outside the template set. **Templates are a generator, so template coverage
    is the same blind spot one level up.** This is one independent instrument over a
    template set someone chose -- a real improvement over zero, not a solution.
  * Anything needing a `#@ requires` richer than `\result == <int>`.
  * Unsound REFUSAL MESSAGE TEXT. Route #90's remediation-advice exploit is invisible to any
    program-level sampler, because the defect was in English prose telling the user what to
    write. 62 advice-bearing messages remain unsampled by anything mechanical.

Usage:
  bin/gen-differential-drivers.py [--count N] [--out DIR] [--families a,b,c]
                                  [--seed S] [--fingerprint] [--blind-spots] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, "test-suite", "value-differential", "generated")

# --------------------------------------------------------------------------------------
# TEMPLATE FAMILIES
#
# Each family is (name, builder). The builder takes a random.Random and returns the BODY of
# a total Python program defining `def f() -> int:`. Families are named after the construct
# class the campaign has actually paid for, so that a per-family yield is readable against
# the route ledger.
# --------------------------------------------------------------------------------------


def _fam_field_literal(rng):
    """Routes #85/#87/#88: a dict/list literal stored in a FIELD, then read back. The
    length and the CONTENTS are separate channels and the campaign has been burned by
    probing only one (#81 length wrong/elements right, #87 the mirror image)."""
    n = rng.randint(2, 4)
    vals = [rng.randint(0, 9) for _ in range(n)]
    idx = rng.randrange(n)
    op = rng.choice(["elem", "len", "sum"])
    read = {"elem": "c.xs[%d]" % idx, "len": "len(c.xs)",
            "sum": " + ".join("c.xs[%d]" % i for i in range(n))}[op]
    return ("class C:\n"
            "    def __init__(self) -> None:\n"
            "        self.xs: List[int] = %r\n"
            "\n"
            "def f() -> int:\n"
            "    c: C = C()\n"
            "    return %s\n" % (vals, read))


def _fam_init_capture(rng):
    """Route #79/#82/#83: `__init__` capture shapes. The annotated store, the store nested
    in an `if`, and the parameterless constructor are DIFFERENT arms and #83 showed the
    mechanism story can be wrong even when the hole is real."""
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    shape = rng.choice(["plain", "annotated", "nested", "param"])
    body = {
        "plain": "        self.v = %d\n" % a,
        "annotated": "        self.v: int = %d\n" % a,
        "nested": "        if %d > 0:\n            self.v = %d\n        else:\n"
                  "            self.v = 0\n" % (a, a),
        "param": "        self.v = n\n",
    }[shape]
    sig = "    def __init__(self, n: int) -> None:\n" if shape == "param" \
        else "    def __init__(self) -> None:\n"
    ctor = "C(%d)" % a if shape == "param" else "C()"
    return ("class C:\n" + sig + body +
            "\ndef f() -> int:\n    c: C = %s\n    return c.v + %d\n" % (ctor, b))


def _fam_aliasing(rng):
    """Routes #49/#59/#76: two names bound to the same collection, mutated through one and
    read through the other. `is`/identity semantics live here too."""
    n = rng.randint(2, 4)
    vals = [rng.randint(0, 9) for _ in range(n)]
    newv = rng.randint(0, 9)
    return ("def f() -> int:\n"
            "    a: List[int] = %r\n"
            "    b: List[int] = a\n"
            "    b[0] = %d\n"
            "    return a[0]\n" % (vals, newv))


def _fam_is_identity(rng):
    """Route #42/#52/#90: `is` against a bool/int literal. #90 is here because the guard's
    OWN advice ('annotate X as bool') turned the correct refusal into a proof of a
    falsehood -- the annotation is the one source of bool-ness nothing enforces."""
    v = rng.choice([0, 1, 2, 5])
    lit = rng.choice(["True", "False", "0", "1"])
    return ("def f() -> int:\n"
            "    x: int = %d\n"
            "    if x is %s:\n"
            "        return 7\n"
            "    return 0\n" % (v, lit))


def _fam_dict_set_ops(rng):
    """Routes #54/#60/#61: dict/set literals where Python collapses keys (bool/int identity
    -- `{1: 5, True: 6}` is `{1: 6}`), membership, and the size channel."""
    k = rng.randint(0, 3)
    d = {i: rng.randint(0, 9) for i in range(rng.randint(1, 3))}
    op = rng.choice(["get", "len", "in"])
    read = {"get": "d.get(%d, 0)" % k, "len": "len(d)",
            "in": "(1 if %d in d else 0)" % k}[op]
    return ("def f() -> int:\n"
            "    d: Dict[int, int] = %r\n"
            "    return %s\n" % (d, read))


def _fam_del_stmt(rng):
    """Route #77: `del` on a slice or element, then a read. The erasure emitted a DEFINITE
    value and the emitter then proved definite facts from it."""
    n = rng.randint(3, 5)
    vals = [rng.randint(0, 9) for _ in range(n)]
    form = rng.choice(["elem", "slice"])
    stmt = "    del xs[0]\n" if form == "elem" else "    del xs[0:2]\n"
    return ("def f() -> int:\n    xs: List[int] = %r\n%s    return xs[0]\n"
            % (vals, stmt))


def _fam_assert_stmt(rng):
    """Route #84: `assert` lowers to `()`, which LAUNDERS a refused construct past its own
    guard. Confirmed NOT an assumption (a false assert proves nothing) -- these instances
    exist to keep that confirmed, mechanically, every run."""
    a = rng.randint(1, 9)
    b = rng.randint(1, 9)
    return ("def f() -> int:\n"
            "    x: int = %d\n"
            "    assert x == %d\n"
            "    return x + %d\n" % (a, a, b))


def _fam_renamed_param(rng):
    """Routes #96/#98: a parameter whose emitted `whyml_ident` is RENAMED (a WhyML reserved
    word, a leading capital) lost its frame entirely and the whole of #96 returned. The
    family exists because #98 proved the rename axis is load-bearing."""
    name = rng.choice(["model", "type", "val", "function", "Model", "ref", "end"])
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    return ("def g(%s: int) -> int:\n"
            "    return %s + %d\n"
            "\n"
            "def f() -> int:\n"
            "    return g(%d)\n" % (name, name, b, a))


def _fam_arith_edges(rng):
    """Routes #53/#58: int floor-division and modulo where Euclidean disagrees with Python,
    and the int/bool arithmetic identities. Measured faithful at HEAD -- these instances
    exist to keep that measured rather than remembered."""
    a = rng.choice([7, -7, 5, -5, 9, -9])
    b = rng.choice([2, -2, 3, -3])
    op = rng.choice(["//", "%"])
    return ("def f() -> int:\n"
            "    a: int = %d\n"
            "    b: int = %d\n"
            "    return a %s b\n" % (a, b, op))


FAMILIES = [
    ("field-literal", _fam_field_literal),
    ("init-capture", _fam_init_capture),
    ("aliasing", _fam_aliasing),
    ("is-identity", _fam_is_identity),
    ("dict-set-ops", _fam_dict_set_ops),
    ("del-stmt", _fam_del_stmt),
    ("assert-stmt", _fam_assert_stmt),
    ("renamed-param", _fam_renamed_param),
    ("arith-edges", _fam_arith_edges),
]

# The `List`/`Dict` names the annotations use. Emitted into every driver so the program is
# runnable under plain CPython -- the oracle must not need PyCSL to execute.
PRELUDE = "from typing import Dict, List  # noqa: F401\n"

HEADER = ('"""GENERATED by bin/gen-differential-drivers.py — family %s, instance %s.\n'
          'DO NOT HAND-EDIT. This corpus is a SAMPLER, not a curated list: the expected\n'
          'value below was MEASURED by running this program under CPython, not asserted.\n'
          '%s\n"""\n')


def _run_cpython(body: str):
    """The ORACLE. Returns the int the program evaluates to, or None if it raises."""
    prog = PRELUDE + body + '\n\nif __name__ == "__main__":\n    print(f())\n'
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(prog)
        path = fh.name
    try:
        r = subprocess.run([sys.executable, path], capture_output=True, text=True,
                           timeout=20)
        if r.returncode != 0:
            return None
        return int(r.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired):
        return None
    finally:
        os.unlink(path)


def _driver_text(fam, inst, body, claim, direction):
    note = ("AGREE: claims the value CPython computes. MUST PROVE — this direction is what\n"
            "stops the gate being satisfiable by refusing every program."
            if direction == "agree" else
            "DISAGREE: claims a value CPython REFUTES. MUST BE REFUSED — if PyCSL PROVES\n"
            "this, that is a RED and it outranks a RED from the driver.")
    lines = body.rstrip("\n").split("\n")
    out = [HEADER % (fam, inst, note), PRELUDE, "\n"]
    for ln in lines:
        if ln.startswith("def f()"):
            out.append("#@ ensures \\result == %d\n" % claim)
            out.append("#@ assigns \\nothing\n")
        out.append(ln + "\n")
    out.append('\n\nif __name__ == "__main__":\n    print(f())\n')
    return "".join(out)


def fingerprint():
    """Per-family hash of the template SOURCE. The convergence clock is only meaningful
    while the set is frozen, so a run must be able to PROVE it was."""
    import inspect
    return {name: hashlib.sha256(inspect.getsource(fn).encode()).hexdigest()[:12]
            for name, fn in FAMILIES}


BLIND_SPOTS = """\
BLIND SPOTS OF THIS SAMPLER — state these next to every yield figure:
  * Constructs OUTSIDE the template set. Templates are themselves a generator, so template
    coverage is the same blind spot one level up. This is ONE independent instrument over a
    template set someone chose: a real improvement over zero, NOT a solution.
  * Anything needing a `#@ requires` richer than `\\result == <int>`.
  * UNSOUND REFUSAL MESSAGE TEXT. Route #90 came from a guard's own remediation advice, and
    no program-level sampler can see English prose. 62 advice-bearing messages remain
    unsampled by anything mechanical; the advice-audit generator stays manual.
  * A family whose fingerprint moved has a RESET convergence clock. Three consecutive
    zero-RED runs only count with the template set FROZEN.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=200,
                    help="target number of DRIVERS (agree+disagree pairs, so ~count/2 "
                         "instances). Default 200, the plan's per-run population.")
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--families", default="",
                    help="comma-separated subset of family names")
    ap.add_argument("--seed", type=int, default=0,
                    help="RNG seed. FIXED BY DEFAULT so a run is reproducible; vary it "
                         "deliberately to widen the sample, and record which seed produced "
                         "a RED.")
    ap.add_argument("--fingerprint", action="store_true")
    ap.add_argument("--blind-spots", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="generate and oracle-check but write nothing")
    args = ap.parse_args()

    if args.blind_spots:
        print(BLIND_SPOTS)
        return 0
    if args.fingerprint:
        for k, v in fingerprint().items():
            print("%-16s %s" % (k, v))
        return 0

    fams = FAMILIES
    if args.families:
        want = {s.strip() for s in args.families.split(",") if s.strip()}
        fams = [f for f in FAMILIES if f[0] in want]
        unknown = want - {f[0] for f in FAMILIES}
        if unknown:
            print("[!] unknown family: %s" % ", ".join(sorted(unknown)), file=sys.stderr)
            return 2
    if not fams:
        print("[!] no families selected — REFUSING rather than writing an empty corpus.",
              file=sys.stderr)
        return 2

    rng = random.Random(args.seed)
    per_family = max(1, (args.count // 2) // len(fams))

    if not args.dry_run:
        if os.path.isdir(args.out):
            shutil.rmtree(args.out)
        os.makedirs(args.out)
        with open(os.path.join(args.out, "README.md"), "w") as fh:
            fh.write(
                "# GENERATED value-differential corpus — DO NOT HAND-EDIT\n\n"
                "Written by `bin/gen-differential-drivers.py`. Regenerate, never patch.\n\n"
                "The standing `check-value-differential.py` run SKIPS this directory by\n"
                "construction (`os.listdir` does not recurse) — the same mechanism that\n"
                "keeps `negative-test/` out. Run it explicitly:\n\n"
                "    bin/check-value-differential.py --generated\n\n"
                "Yield = RED / generated, reported per family. Converging = RED per 200\n"
                "falls to 0 across THREE CONSECUTIVE RUNS WITH THE TEMPLATE SET FROZEN\n"
                "(`bin/gen-differential-drivers.py --fingerprint`). Adding a family resets\n"
                "the clock FOR THAT FAMILY ONLY.\n\n"
                "```\n" + BLIND_SPOTS + "```\n")

    written, skipped = 0, 0
    per_fam_counts = {}
    for name, fn in fams:
        made = 0
        attempts = 0
        seen = set()
        while made < per_family and attempts < per_family * 20:
            attempts += 1
            body = fn(rng)
            if body in seen:
                continue
            seen.add(body)
            truth = _run_cpython(body)
            if truth is None:
                skipped += 1      # CPython raised: OUT OF SCOPE, these must be TOTAL
                continue
            inst = "%s_%03d" % (name.replace("-", "_"), made)
            for direction, claim in (("agree", truth), ("disagree", truth + 1)):
                fname = "g_%s_%s.py" % (inst, direction)
                text = _driver_text(name, inst, body, claim, direction)
                if not args.dry_run:
                    with open(os.path.join(args.out, fname), "w") as fh:
                        fh.write(text)
                written += 1
            made += 1
        per_fam_counts[name] = made

    print("[*] gen-differential-drivers: %d driver(s) in %d family(ies), seed %d%s"
          % (written, len(fams), args.seed, "  (DRY RUN, nothing written)"
             if args.dry_run else ""))
    for name, c in per_fam_counts.items():
        print("      %-16s %3d instance(s) -> %3d driver(s)" % (name, c, c * 2))
    if skipped:
        print("      %d instance(s) DISCARDED because CPython raised — these drivers must "
              "be TOTAL, and a raising program is out of the value plane's scope." % skipped)
    if not args.dry_run:
        print("[*] wrote to %s" % os.path.relpath(args.out, ROOT))
        print("[*] next: bin/check-value-differential.py --generated   "
              "(NEEDS AN IDLE BOX — never alongside the reference suite)")
    print()
    print(BLIND_SPOTS)
    return 0


if __name__ == "__main__":
    sys.exit(main())
