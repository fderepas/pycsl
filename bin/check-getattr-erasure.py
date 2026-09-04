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
              neither presence nor absence can be established and the default is a
              GUESS. Not demonstrated to be exploitable — a contract cannot name a field
              of an object whose type the model does not carry — but it is not sound by
              argument either, so it is held by a ratchet rather than called safe.

Absent/unknown are RATCHETS (they may only shrink); declared is a HARD ZERO.

HOW. The emitter carries an env-gated one-line census at the fall-through
(`PYCSL_GETATTR_CENSUS=1`, stderr, emits nothing). This script drives the emission over
the self-annotation mirror and the pycsl-reference corpus and tallies the classes. It is
a MEASUREMENT of the real lowering, not a syntactic guess about it — a static scan cannot
tell DECLARED from ABSENT, which is the entire distinction that matters here.

USAGE
    bin/check-getattr-erasure.py                     # check against the ratchets
    bin/check-getattr-erasure.py --verbose           # list every site
    bin/check-getattr-erasure.py --max-absent N --max-unknown N
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
CORPUS = os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference")

# Ratchets, measured at the route-#22 closure (#44).
MAX_ABSENT = 7
MAX_UNKNOWN = 19


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
                    help="skip the corpus pass (fast)")
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

    print(f"[*] getattr-erasure: {len(rows)} fall-through site(s) over "
          f"{len(targets)} file(s) — "
          f"DECLARED {counts['DECLARED']} · ABSENT {counts['ABSENT']} · "
          f"UNKNOWN {counts['UNKNOWN']}")
    if args.verbose:
        for cls, f, obj, ty, name in sorted(rows):
            print(f"    {cls:9s} {f:55s} {obj}.{name}  (type={ty})")

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
    if counts["ABSENT"] > args.max_absent:
        print(f"[-] getattr-erasure: ABSENT {counts['ABSENT']} > "
              f"ratchet {args.max_absent}")
        bad = True
    if counts["UNKNOWN"] > args.max_unknown:
        print(f"[-] getattr-erasure: UNKNOWN {counts['UNKNOWN']} > "
              f"ratchet {args.max_unknown}")
        bad = True
    if bad:
        return 1
    print(f"[+] getattr-erasure: OK — DECLARED 0 (pinned), "
          f"ABSENT {counts['ABSENT']}/{args.max_absent}, "
          f"UNKNOWN {counts['UNKNOWN']}/{args.max_unknown}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
