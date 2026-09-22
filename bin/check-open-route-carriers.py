#!/usr/bin/env python3
r"""L-PLANE ORACLE: the OPEN routes' carriers still behave exactly as recorded — so the day
one of them changes, somebody notices.

WHY THIS EXISTS (gen #30). A route that is CLOSED gets a corpus witness: an expected-FAIL
file that fails, and an expected-PASS control that proves. A route that is DEMONSTRATED BUT
OPEN gets neither, and the reason is worth stating because it is not laziness:

>>> AN OPEN ROUTE'S CARRIER **PROVES A FALSE CONTRACT TODAY**. Marking it
>>> `# pycsl-expected: FAIL` makes the suite red (it is an XPASS, and the XPASS rule is
>>> there precisely so a negative witness that starts proving is a failure). Marking it
>>> `PASS` writes "this false proof is expected" into the corpus. Neither is acceptable, so
>>> the carrier lives OUTSIDE the corpus — and then nothing runs it.

This gate runs it. Each entry records the verdict the route's ledger row says the carrier
produces TODAY, and a CHANGE IS THE POINT: if a carrier stops proving, the route is
probably closed and this file must be updated in the same commit that closes it. The
message says so, so a green battery cannot quietly outlive a fixed route.

THE CARRIERS (gen #30):

  route #214 — `getting-better/open-routes/route214-carrier-two-unknown-receivers.py`.
    Two `getattr` reads on DIFFERENT unknown-class objects with DIFFERENT attribute names
    share route #47's DEFAULT-KEYED constant, so `d == e` is provable and
    `#@ ensures \result == 0` PROVES. CPython answers 1. Both repairs were measured and
    are blocked — the faithful one breaks corpus 1073 (a true equality) because a local
    built from a known class is typed `Any` at that point; the refusal would hit 104 sites,
    nearly all in the mirror.

Route #212's carrier is NOT here: its single-file half (corpus 1721) genuinely FAILS, so it
is an ordinary expected-FAIL witness, and its two-file halves live in the probe ledger with
their commands.

Usage:  bin/check-open-route-carriers.py [--verbose]
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python3")
PY = PY if os.path.exists(PY) else "python3"
DRIVER = os.path.join(ROOT, "src", "pycsl", "pycsl.py")

# carrier path -> (expected verdict TODAY, route, what the verdict means)
CARRIERS = {
    "getting-better/open-routes/route214-carrier-two-unknown-receivers.py": (
        "SUCCESS", "#214",
        "two `getattr` reads on different unknown receivers share route #47's "
        "default-keyed constant, so `\\result == 0` PROVES while CPython answers 1"),
}
FLAGS = ["--memory-model", "hoare"]


def verdict(path):
    p = subprocess.run([PY, DRIVER] + FLAGS + [path], capture_output=True, text=True,
                       timeout=600)
    out = (p.stdout or "") + (p.stderr or "")
    if "PIPELINE ERROR" in out:
        return "REFUSED"
    if "Verification SUCCESS" in out:
        return "SUCCESS"
    return "FAILED"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    import shutil
    if shutil.which("why3") is None:
        print("[!] open-route-carriers: REFUSING — `why3` is not on PATH, so every carrier "
              "would report FAILED. Source the environment first.", file=sys.stderr)
        return 2

    rc = 0
    for rel, (want, route, why) in sorted(CARRIERS.items()):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print("[!]   MISSING CARRIER %s (route %s). An open route with no carrier is "
                  "an open route nobody can reproduce." % (rel, route), file=sys.stderr)
            rc = 1
            continue
        got = verdict(path)
        if args.verbose:
            print("    %-9s %s (route %s)" % (got, rel, route))
        if got != want:
            print("[+]   CARRIER CHANGED: %s (route %s) now reports %s, recorded as %s. "
                  "If the route is CLOSED, give it a corpus witness and remove this entry "
                  "IN THE SAME COMMIT — %s." % (rel, route, got, want, why),
                  file=sys.stderr)
            rc = 1

    print("[*] open-route-carriers: %d carrier(s) checked." % len(CARRIERS))
    if rc:
        print("[!] open-route-carriers: NOT OK — and a change here is usually GOOD news "
              "that needs recording, not a regression.", file=sys.stderr)
    else:
        print("[+] open-route-carriers: OK — every open route's carrier still reproduces "
              "exactly as its ledger row says.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
