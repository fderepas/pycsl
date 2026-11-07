#!/usr/bin/env python3
"""PLANE (#49, route #228) — THE STRING-FOLD INJECTIVITY GUARD HAS TEETH.

`module6_whyml/identifiers.py::stable_hash` folds a string PyCSL cannot model
faithfully to `int(sha256(s)[:8],16) % 2147483647`. It used to justify that with
"distinct strings -> distinct ints **w.h.p.**" — a PROBABILISTIC premise
load-bearing in a deductive verifier's TCB. Route #228 exhibited a collision in
under a second of compute and used it to PROVE a false postcondition:

    struct.pack('<bb6x', 1, 2)                  CPython:  8 bytes
    struct.pack('<xxxxxxxxhxLxxxxxxxx', 1, 2)   CPython: 23 bytes
    both emit  (struct_pack_i2 1322019588 1 2)  <-- ONE TERM, because
                                                    `struct_pack_i2` is a PURE
                                                    `val function` and `slot_id`
                                                    encodes "only the slot types
                                                    (not prefix, not pad)"

`stable_hash` now RECORDS every fold of one emission and REFUSES on a collision,
turning the probabilistic premise into a decidable per-emission check.

WHY THIS PLANE EXISTS AND WHY IT IS SHAPED THIS WAY. The largest emission in the
tree folds **91** distinct strings, so the collision probability in real code is
~2e-6 and THE GUARD'S POPULATION IS EMPTY. By this campaign's own hardest-won
rule, a guard whose population is empty has checked nothing and looks exactly
like a guard that passed. So this plane does NOT sweep the corpus looking for a
collision that is not there — it NEGATIVE-TESTS the guard, by handing PyCSL the
known colliding pair and asserting it REFUSES, and handing it the non-colliding
control and asserting it still ACCEPTS. A one-sided test would pass against a
guard that simply refuses everything.

Usage:  python3 bin/check-stable-hash-fold-injectivity.py [-v]
Exit 0 = the guard refuses the collision AND accepts the control.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")

# The colliding pair (route #228). Both formats parse to PyCSL slot_id `i2`, so they
# share the symbol `struct_pack_i2`, and both quoted forms fold to 1322019588.
COLLIDING = "'<xxxxxxxxhxLxxxxxxxx'"
CONTROL = "'<hL'"
EXPECTED_CONSTANT = 1322019588

PROGRAM = """import struct  # noqa


#@ requires True
#@ ensures \\result == 1
def go() -> int:
    a = struct.pack('<bb6x', 1, 2)
    b = struct.pack(%s, 1, 2)
    if len(a) == len(b):
        return 1
    return 0
"""


def _fold(s: str) -> int:
    import hashlib
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16) % 2147483647


def _run(second_fmt: str) -> tuple:
    """Emit a program whose second struct format is `second_fmt`. Returns (rc, output)."""
    fd, path = tempfile.mkstemp(suffix=".py", prefix="foldinj_")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(PROGRAM % second_fmt)
        env = dict(os.environ, PYTHONHASHSEED="0")
        proc = subprocess.run(
            [sys.executable, PYCSL, path, "--no-proof"],
            capture_output=True, text=True, env=env, timeout=600)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def main() -> int:
    verbose = "-v" in sys.argv
    failures = []

    # LEG 0 — the pair really does collide, and on the QUOTED form, which is what the
    # emitter folds. If this ever stops holding, the rest of the plane is vacuous and
    # must be re-derived rather than silently passing.
    h1 = _fold('"<bb6x"')
    h2 = _fold('"<xxxxxxxxhxLxxxxxxxx"')
    hc = _fold('"<hL"')
    if not (h1 == h2 == EXPECTED_CONSTANT):
        failures.append(
            "LEG 0: the route #228 pair no longer collides at %d (got %d and %d) — "
            "this plane's population is gone; re-derive a colliding pair with "
            "getting-better/open-routes/route228-collide-stable-hash.py before "
            "trusting any verdict below." % (EXPECTED_CONSTANT, h1, h2))
    if hc in (h1, h2):
        failures.append(
            "LEG 0: the CONTROL format collides too (%d) — it cannot serve as a "
            "negative control; pick another." % hc)
    if verbose:
        print("[.] leg 0: '<bb6x' -> %d, '<xxxxxxxxhxLxxxxxxxx' -> %d, control "
              "'<hL' -> %d" % (h1, h2, hc))

    # LEG 1 — the guard REFUSES the colliding program.
    rc, out = _run(COLLIDING)
    if rc == 0:
        failures.append(
            "LEG 1: PyCSL ACCEPTED the colliding program. The route #228 guard in "
            "module6_whyml/identifiers.py::stable_hash is gone or bypassed, and a "
            "false postcondition is provable again.")
    elif "route #228" not in out:
        failures.append(
            "LEG 1: the colliding program was rejected (rc=%d) but NOT by the "
            "fold-injectivity guard — no 'route #228' in the diagnostic, so the "
            "refusal is some other error and this leg proves nothing. Output: %s"
            % (rc, out[-400:]))
    elif verbose:
        print("[.] leg 1: colliding program REFUSED by the fold guard (rc=%d)" % rc)

    # LEG 2 — the guard still ACCEPTS the non-colliding control. Without this leg a
    # guard that refuses unconditionally would pass.
    rc2, out2 = _run(CONTROL)
    if rc2 != 0:
        failures.append(
            "LEG 2: PyCSL REJECTED the non-colliding control (rc=%d). The guard is "
            "over-firing — it must refuse a COLLISION, not a struct program. "
            "Output: %s" % (rc2, out2[-400:]))
    elif verbose:
        print("[.] leg 2: non-colliding control ACCEPTED (rc=0)")

    if failures:
        print("[-] check-stable-hash-fold-injectivity: FAILED")
        for f in failures:
            print("    " + f)
        return 1
    print("[+] check-stable-hash-fold-injectivity: OK — the route #228 fold guard "
          "REFUSES the colliding pair (%d) and ACCEPTS the non-colliding control"
          % EXPECTED_CONSTANT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
