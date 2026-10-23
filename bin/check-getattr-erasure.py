#!/usr/bin/env python3
"""check-getattr-erasure.py — the ROUTE #22 regression gate.

`expressions._lower_getattr` lowers `getattr(obj, name[, default])`. When it can resolve
`name` to a field the emitted record DECLARES it emits the genuine read; otherwise it
falls through and emits the DEFAULT. Before #44 the fall-through also swallowed reads of
DECLARED fields, and that PROVED A FALSE POSTCONDITION: a class with `self.a: int = 7`
emits `type c = { mutable a: int }`, yet `v = getattr(self, "a", 0); if v: return 7;
return 0` proved `\\result == 0` while Python returns 7 (corpus witnesses 0991 / 0992).

The comment beside the fall-through had carried the soundness argument — "getattr DOES
return default for an ABSENT attribute, so this is sound ... never proves false". The
argument is correct; nothing enforced its premise. This gate enforces it.

WHAT IT MEASURES. Every fall-through is classified by WHY the field was not resolved:

    DECLARED  the record type is known AND declares the name.
              The default is then a WRONG value, not an unknown one.
              *** PINNED AT 0. Any occurrence is the route-#22 unsoundness back. ***
    ABSENT    the record type is known and does NOT declare the name. `getattr` really
              does return the default here, so emitting it is faithful.
    UNKNOWN   the object's static type is `Any` / `object` / a non-record mixin, so
              neither presence nor absence can be established and the default was a
              GUESS. *** THIS BUCKET'S OLD JUSTIFICATION WAS REFUTED BY ROUTE #197. ***
              It read: "Not demonstrated to be exploitable — a contract cannot name a
              field of an object whose type the model does not carry — but it is not
              sound by argument either, so it is held by a ratchet rather than called
              safe." Holding it by a ratchet was right; the reason was wrong. THE
              CONTRACT DOES NOT HAVE TO NAME THE FIELD — the BODY reads it and the
              contract reads `\result`:
                  def peek(o: Any) -> int:           #@ ensures \result == 1
                      v = getattr(o, "a", 0)
                      if v == 0: return 1
                      return 2
              emitted `let v = ref 0 in v := 0;` with `o` UNUSED (Why3 warns so) and
              PROVED, while CPython answers 2 for any object with `a = 7` (witness
              1691). The UNKNOWN fall-through now answers a PER-SITE opaque — route
              #47's own device, hashed on the call's IR so two reads of the SAME
              expression agree — so the read is UNDECIDED rather than guessed. The
              bucket is still ratcheted, because an opaque read is still a read the
              model cannot resolve, but it is no longer a WRONG ANSWER.

Absent/unknown WERE GLOBAL RATCHETS (they may only shrink); declared is a HARD ZERO.

(#49) gen #30 — THE GLOBAL RATCHETS ARE GONE, REPLACED BY A PER-FILE BASELINE, and this is
the redesign THIS FILE'S OWN NOTE ASKED FOR two generations running:

    "these ratchets count EMISSION SITES ACROSS THE WHOLE CORPUS, so they rise whenever a
     witness is ADDED, for reasons that have nothing to do with the emitter's residue
     shrinking. If that keeps happening, the honest redesign is to ratchet the residue PER
     EMITTER SITE rather than per corpus occurrence."

It kept happening. UNKNOWN was raised 19 -> 24 for route #47's four witnesses, 24 -> 25 for
route #197's carrier, and gen #30's refusal witnesses pushed it to 27 — a third bump, each
one individually justified and the sequence indistinguishable from laundering a ratchet.
Rule (k) says never re-baseline a gate to make it green, and "the corpus grew" had become
the standing excuse for doing exactly that.

So the gate is now keyed on (file -> absent, unknown), committed in
`bin/getattr-erasure-sites.tsv`:

  * a baselined file with MORE sites than its row FAILS — strictly stronger than the old
    global cap, which a shrink elsewhere could have paid for;
  * a file with NO row that has ANY site FAILS, so a new witness is a deliberate
    REGISTRATION (`--emit-baseline`, then read the diff) rather than a number bumped;
  * a baselined file with FEWER sites is REPORTED so its row can shrink with it;
  * DECLARED stays a hard zero everywhere, unbaselineable, which is the half that means
    route #22 is back.

The global totals are still printed, but nothing is gated on them and there is no
hand-maintained ceiling left to raise.

HOW. The emitter carries an env-gated one-line census at the fall-through
(`PYCSL_GETATTR_CENSUS=1`, stderr, emits nothing). This script drives the emission over
the self-annotation mirror and the pycsl-reference corpus and tallies the classes. It is
a MEASUREMENT of the real lowering, not a syntactic guess about it — a static scan cannot
tell DECLARED from ABSENT, which is the entire distinction that matters here.

USAGE
    bin/check-getattr-erasure.py                     # check against the per-file baseline
    bin/check-getattr-erasure.py --verbose           # list every site
    bin/check-getattr-erasure.py --mirror-only       # the TCB half, fast
    bin/check-getattr-erasure.py --emit-baseline     # rewrite the TSV (READ THE DIFF)
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
CORPUS = os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference")

# Ratchets, measured at the route-#22 closure (#44).
MIN_TARGET_FILES = 40   # true population 64; a floor on the INPUT, not a ratchet (gen #4)

SITES_TSV = os.path.join(ROOT, "bin", "getattr-erasure-sites.tsv")

# ---------------------------------------------------------------------------------------
# HISTORY OF THE RATCHETS THAT USED TO LIVE HERE. Kept because the sequence is the argument
# for the per-file baseline that replaced them, and deleting it would delete the evidence.
#
# (#49) gen #30, ROUTE #197 — BOTH RATCHETS RAISED BY EXACTLY ONE, AND ONLY BECAUSE THE
# CORPUS GREW BY TWO FILES THAT EXIST TO EXERCISE THESE TWO BUCKETS:
#   * `1691_route197_an_unknown_typed_getattr_was_its_default.py` adds ONE UNKNOWN site —
#     it is route #197's carrier, `getattr(o, "a", 0)` on an `Any`-typed object.
#   * `1692_route197_an_absent_field_still_returns_its_default.py` adds ONE ABSENT site —
#     it is the control showing the repair did NOT touch the faithful case.
# This is NOT re-baselining to make a gate green (rule (k)): no emitter residue grew, and
# the numbers are up by exactly the two sites two new test files contribute. THE PIN THAT
# MATTERS IS UNTOUCHED — DECLARED stays hard-zero, which is the route-#22 regression gate.
# NOTE FOR THE NEXT WINDOW, because this is the second time it has bitten: these ratchets
# count EMISSION SITES ACROSS THE WHOLE CORPUS, so they rise whenever a witness is ADDED,
# for reasons that have nothing to do with the emitter's residue shrinking. If that keeps
# happening, the honest redesign is to ratchet the residue PER EMITTER SITE rather than
# per corpus occurrence.
MAX_ABSENT = 8
# UNKNOWN was 19 at the route-#22 closure and this plane went RED at `5342bea1` (routes
# #47/#48 closing) without anyone noticing, because the plane is driver-run and nobody ran
# it — found at HEAD by relaunch #51. THE DELTA IS EXACTLY THE FIVE SITES ROUTE #47 ADDED
# TO THE CORPUS AS ITS OWN WITNESSES: `1070_route47_getattr_default_dict` (`c.missing`),
# `1071_route47_getattr_default_list` (`c.missing`), `1072_route47_getattr_no_default`
# (`c.missing`) and `1073_route47_same_default_equal` (`c.missing` AND `c.other`). Those
# files exist PRECISELY to be `getattr` sites, so an UNKNOWN there is the witness doing its
# job, not erasure creeping back. CONFIRMED BY THE PLANE'S OWN INSTRUMENT rather than by
# arithmetic: `--mirror-only` reports UNKNOWN 19/19 and rc=0 at the same HEAD, so the
# mirror population has not moved at all. `DECLARED` stays pinned at 0 — that is the half
# that would mean route #22 is back, and it has not budged.
MAX_UNKNOWN = 25
# ---------------------------------------------------------------------------------------


def load_baseline():
    """file -> (absent, unknown). Missing file = every site in it is unregistered."""
    out = {}
    if not os.path.exists(SITES_TSV):
        return out
    for line in open(SITES_TSV, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        out[parts[0]] = (int(parts[1]), int(parts[2]))
    return out


def emit_and_collect(path, import_path=None):
    """Run the emitter over one file with the census on; return its fall-through rows."""
    env = dict(os.environ)
    env["PYCSL_GETATTR_CENSUS"] = "1"
    env["PYTHONHASHSEED"] = "0"
    cmd = [sys.executable, os.path.join(ROOT, "src", "pycsl", "pycsl.py"), path,
           "--no-proof", "--no-typecheck"]
    if import_path:
        cmd += ["--import-path", import_path]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, env=env,
                           cwd=ROOT)
    except subprocess.TimeoutExpired:
        return []
    rows = []
    for line in r.stderr.split("\n"):
        if line.startswith("GETATTR_FALLTHROUGH\t"):
            parts = line.split("\t")
            if len(parts) >= 5:
                rows.append((parts[1], os.path.relpath(path, ROOT), parts[2],
                             parts[3], parts[4]))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--max-absent", type=int, default=MAX_ABSENT)
    ap.add_argument("--max-unknown", type=int, default=MAX_UNKNOWN)
    ap.add_argument("--mirror-only", action="store_true",
                    help="skip the corpus pass (fast); checks only the mirror rows")
    ap.add_argument("--emit-baseline", action="store_true",
                    help="rewrite bin/getattr-erasure-sites.tsv from this run. READ THE "
                         "DIFF: a row that GREW is the thing this gate exists to catch.")
    args = ap.parse_args()

    targets = []
    for root, _d, files in os.walk(MIRROR):
        for fn in sorted(files):
            if fn.endswith(".py"):
                targets.append((os.path.join(root, fn),
                                os.path.join(ROOT, "src", "pycsl")))
    if not args.mirror_only:
        for fn in sorted(os.listdir(CORPUS)):
            if fn.endswith(".py") and "getattr" in open(
                    os.path.join(CORPUS, fn), errors="replace").read():
                targets.append((os.path.join(CORPUS, fn), None))

    rows = []
    for path, imp in targets:
        rows += emit_and_collect(path, imp)

    counts = {"DECLARED": 0, "ABSENT": 0, "UNKNOWN": 0}
    for cls, *_ in rows:
        counts[cls] = counts.get(cls, 0) + 1

    # ZERO-INPUT / SHRINKING-INPUT GUARD (gen #4, the #44 rule). Every verdict below is an
    # UPPER bound (DECLARED pinned at 0, ABSENT and UNKNOWN at ratchets), so an EMPTY sweep
    # satisfies all three and this plane printed
    # "[+] getattr-erasure: OK — DECLARED 0 (pinned), ABSENT 0/7, UNKNOWN 0/24". Its own
    # emit_and_collect returns [] on any emission failure OR timeout, so a broken toolchain
    # produces exactly that. This is the plane window #51 found RED at HEAD with nobody
    # looking; it should not also be able to go green with nothing looked at.
    # True population: 64 files. 40 is a floor well below it.
    if len(targets) < MIN_TARGET_FILES:
        print(f"[!] getattr-erasure: REFUSING — only {len(targets)} file(s) were scanned, "
              f"expected at least {MIN_TARGET_FILES}. The emission failed, timed out, or "
              f"the target list is broken. THIS IS A REFUSAL, NOT A PASS.")
        return 2
    print(f"[*] getattr-erasure: {len(rows)} fall-through site(s) over "
          f"{len(targets)} file(s) — "
          f"DECLARED {counts['DECLARED']} · ABSENT {counts['ABSENT']} · "
          f"UNKNOWN {counts['UNKNOWN']}")
    if args.verbose:
        for cls, f, obj, ty, name in sorted(rows):
            print(f"    {cls:9s} {f:55s} {obj}.{name}  (type={ty})")

    # ---- per-file tally of this run
    per = {}
    for cls, f, _o, _t, _n in rows:
        a, u = per.get(f, (0, 0))
        if cls == "ABSENT":
            a += 1
        elif cls == "UNKNOWN":
            u += 1
        per[f] = (a, u)

    if args.emit_baseline:
        scope = "mirror only" if args.mirror_only else "mirror + corpus"
        with open(SITES_TSV, "w", encoding="utf-8") as fh:
            fh.write("# getattr fall-through sites, per file: file\tABSENT\tUNKNOWN\n")
            fh.write("# Written by bin/check-getattr-erasure.py --emit-baseline (%s).\n"
                     "# DECLARED is never recorded here: it is a hard zero, not a "
                     "baseline.\n" % scope)
            for f in sorted(per):
                a, u = per[f]
                fh.write("%s\t%d\t%d\n" % (f, a, u))
        print("[*] getattr-erasure: wrote %d row(s) to %s — READ THE DIFF."
              % (len(per), os.path.relpath(SITES_TSV, ROOT)))
        return 0

    baseline = load_baseline()
    if not baseline:
        print("[!] getattr-erasure: REFUSING — %s is missing or empty. The per-file "
              "baseline IS the gate; without it this script can only print totals, and a "
              "gate that cannot distinguish 'nothing wrong' from 'I compared nothing' "
              "must refuse." % os.path.relpath(SITES_TSV, ROOT), file=sys.stderr)
        return 2

    bad = False
    if counts["DECLARED"] > 0:
        print("[-] getattr-erasure: *** ROUTE #22 IS BACK *** "
              f"{counts['DECLARED']} site(s) erase a DECLARED record field to the "
              "default. That is a WRONG value, not an unknown one, and it proves false "
              "postconditions (corpus witness 0991).")
        for cls, f, obj, ty, name in sorted(rows):
            if cls == "DECLARED":
                print(f"      {f}: {obj}.{name} (type={ty})")
        bad = True

    scanned = {os.path.relpath(p2, ROOT) for p2, _i in targets}
    grew, unregistered, shrank = [], [], []
    for f in sorted(per):
        a, u = per[f]
        if f not in baseline:
            unregistered.append((f, a, u))
        else:
            ba, bu = baseline[f]
            if a > ba or u > bu:
                grew.append((f, ba, bu, a, u))
            elif a < ba or u < bu:
                shrank.append((f, ba, bu, a, u))
    for f, (ba, bu) in sorted(baseline.items()):
        if f in scanned and f not in per and (ba or bu):
            shrank.append((f, ba, bu, 0, 0))

    for f, ba, bu, a, u in grew:
        print(f"[-] getattr-erasure: {f} GREW — ABSENT {ba}->{a}, UNKNOWN {bu}->{u}. A "
              f"file's fall-through residue may only shrink; a new site in an EXISTING "
              f"file is the emitter erasing more than it used to.")
        bad = True
    for f, a, u in unregistered:
        print(f"[-] getattr-erasure: {f} has {a} ABSENT / {u} UNKNOWN site(s) and NO row "
              f"in {os.path.relpath(SITES_TSV, ROOT)}. Register it deliberately "
              f"(--emit-baseline, then read the diff) — a new witness is a decision, not "
              f"a number to bump.")
        bad = True
    for f, ba, bu, a, u in shrank:
        print(f"[+] getattr-erasure: {f} SHRANK — ABSENT {ba}->{a}, UNKNOWN {bu}->{u}. "
              f"Re-emit the baseline so the row goes down with it.")

    if bad:
        return 1
    print(f"[+] getattr-erasure: OK — DECLARED 0 (pinned); {len(per)} file(s) with sites, "
          f"every one at or below its row; totals ABSENT {counts['ABSENT']}, UNKNOWN "
          f"{counts['UNKNOWN']} (reported, not gated).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
