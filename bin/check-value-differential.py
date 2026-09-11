#!/usr/bin/env python3
"""SOUNDNESS PLANE — a `#@ ensures` VALUE claim measured against CPython, not a curated list.

WHY THIS EXISTS. The most serious defect class this campaign has found is not an exception
hole at all: it is a FALSE POSTCONDITION ABOUT ORDINARY, TOTAL PYTHON — a claim that needs
no `no_exception`, no memory-model flag and no opt-in of any kind. Routes #53 (a float is an
exact real), #58 (int true-division likewise), #73 and #74 (a hand-added oracle shadowing the
user's own function) and #76 (`==` on a class instance decided structurally where Python
decides by identity) are ALL of that shape. Every one was found by a human-authored probe.

`check-no-exception-differential.py` scans the EXCEPTION surface the same way and curates
nothing. This is its VALUE twin, and it curates nothing either: each driver states a literal
value in its own `#@ ensures \\result == <int>` and RUNS ITSELF under `__main__`, so the
ground truth is MEASURED by CPython rather than asserted by whoever wrote the driver.

    claim DISAGREES with CPython + PyCSL PROVES   -> RED. A postcondition proved about a
                                                    program that demonstrably refutes it.
    claim DISAGREES with CPython + PyCSL refuses  -> green (the honest answer). This is the
                                                    population that gives the gate teeth.
    claim AGREES with CPython    + PyCSL PROVES   -> green, and this is the direction that
                                                    stops the gate being satisfiable by
                                                    refusing every program.
    claim AGREES with CPython    + PyCSL refuses  -> INCOMPLETE. Reported, never fatal.
    CPython RAISES                                -> OUT OF SCOPE. Reported, never fatal.
                                                    These drivers are meant to be TOTAL.

THE POPULATION GUARD IS THE POINT (the #44 rule). A gate of this shape is trivially
satisfiable by refusing everything, so it REFUSES (rc=2) unless the corpus contains BOTH at
least one AGREEING driver that actually PROVES and at least one DISAGREEING driver. Without
both, "all green" could mean "the emitter refuses everything", which certifies nothing.

PARSING IS FAIL-CLOSED. A driver whose claimed literal cannot be parsed from its `#@ ensures`
is an ERROR (rc=1), never a silent skip — an unreadable driver must not excuse itself.

NEGATIVE-TESTED. `--negative-test` runs `negative-test/n01_...py`, in which a `#@ \\trusted`
stub's ASSUMED `ensures` lets PyCSL prove `\\result == 99` about a program CPython evaluates
to 1, and FAILS unless this plane rules it UNSOUND. A gate never observed to fail is not
known to be a gate. That driver lives in a subdirectory the standing run SKIPS.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")
DRIVERS = os.path.join(ROOT, "test-suite", "value-differential")
NEGDIR = os.path.join(DRIVERS, "negative-test")

# `#@ ensures \result == <int>`  — the ONLY shape this plane accepts, deliberately.
_CLAIM = re.compile(r"^#@\s*ensures\s*\\result\s*==\s*(-?\d+)\s*$")


def _claimed_value(path):
    """The literal this driver claims. None if it cannot be parsed (-> fail closed)."""
    found = []
    with open(path) as fh:
        for line in fh:
            m = _CLAIM.match(line.strip())
            if m:
                found.append(int(m.group(1)))
    return found[0] if len(found) == 1 else None


def _cpython_value(path):
    """(value, raised) — what CPython actually computes. `raised` marks a non-total driver."""
    r = subprocess.run([sys.executable, path], cwd=DRIVERS, capture_output=True,
                       text=True, timeout=120)
    if r.returncode != 0:
        return None, True
    out = r.stdout.strip().split("\n")[-1].strip() if r.stdout.strip() else ""
    try:
        return int(out), False
    except ValueError:
        return None, True


def _pycsl_proves(path):
    env = dict(os.environ, PYTHONHASHSEED="0")
    r = subprocess.run([sys.executable, PYCSL, path, "--import-path",
                        os.path.join(ROOT, "src", "pycsl")],
                       cwd=ROOT, capture_output=True, text=True, timeout=900, env=env)
    out = r.stdout + r.stderr
    if "'why3' command not found" in out:
        return None          # A MISSING TOOL IS NOT A FINDING. Never rule from it.
    for line in out.split("\n"):
        if line.startswith("[+] Verification SUCCESS"):
            return True
    return False


def _classify(path):
    """-> (verdict, detail). Verdicts: unsound / honest / agree_proved / incomplete /
    out_of_scope / unparseable / no_tool."""
    claimed = _claimed_value(path)
    if claimed is None:
        return "unparseable", "no single `#@ ensures \\result == <int>` line"
    actual, raised = _cpython_value(path)
    if raised:
        return "out_of_scope", "CPython did not return an int"
    proves = _pycsl_proves(path)
    if proves is None:
        return "no_tool", "why3 missing"
    if actual != claimed:
        return ("unsound" if proves else "honest",
                "claims %d, CPython computes %d" % (claimed, actual))
    return ("agree_proved" if proves else "incomplete",
            "claims %d, CPython computes %d" % (claimed, actual))


def main():
    negative = "--negative-test" in sys.argv
    if not os.path.isdir(DRIVERS):
        print("[!] value-differential: %s missing — REFUSING rather than passing."
              % DRIVERS, file=sys.stderr)
        return 2

    if negative:
        names = sorted(n for n in os.listdir(NEGDIR) if n.endswith(".py"))
        if not names:
            print("[!] value-differential --negative-test: no negative driver found; a "
                  "gate never observed to fail is not known to be a gate.", file=sys.stderr)
            return 2
        bad = []
        for n in names:
            verdict, detail = _classify(os.path.join(NEGDIR, n))
            print("[*]   negative %s -> %s (%s)" % (n, verdict, detail))
            if verdict == "no_tool":
                print("[!] value-differential --negative-test: why3 missing. A MISSING TOOL "
                      "IS NOT A FINDING — refusing.", file=sys.stderr)
                return 2
            if verdict != "unsound":
                bad.append(n)
        if bad:
            print("[!] value-differential --negative-test: %s was NOT ruled unsound. The "
                  "plane's RED path does not fire, so a green standing run means nothing."
                  % ", ".join(bad), file=sys.stderr)
            return 1
        print("[+] value-differential --negative-test: OK — the RED path fires on a real "
              "program (a `\\trusted` ASSUMED `ensures` proving 99 where CPython computes 1).")
        return 0

    names = sorted(n for n in os.listdir(DRIVERS)
                   if n.endswith(".py") and not n.startswith("_"))
    buckets = {k: [] for k in ("unsound", "honest", "agree_proved", "incomplete",
                               "out_of_scope", "unparseable", "no_tool")}
    for n in names:
        verdict, detail = _classify(os.path.join(DRIVERS, n))
        buckets[verdict].append((n, detail))

    if buckets["no_tool"]:
        print("[!] value-differential: why3 is not on PATH. A MISSING TOOL IS NOT A "
              "FINDING — refusing rather than reporting green.", file=sys.stderr)
        return 2

    print("[*] value-differential: %d driver(s) — %d AGREE with CPython (%d prove), "
          "%d DISAGREE (%d correctly refused)."
          % (len(names), len(buckets["agree_proved"]) + len(buckets["incomplete"]),
             len(buckets["agree_proved"]),
             len(buckets["unsound"]) + len(buckets["honest"]), len(buckets["honest"])))

    rc = 0
    if not buckets["agree_proved"] or not (buckets["unsound"] or buckets["honest"]):
        print("[!] value-differential: the corpus lacks BOTH an AGREEING driver that PROVES "
              "and a DISAGREEING driver. This gate is satisfiable by refusing everything, "
              "so it is meaningless without both. NOT A PASS.", file=sys.stderr)
        rc = 2
    for n, d in buckets["unparseable"]:
        print("[!]   UNPARSEABLE: %s — %s. Fail-closed: an unreadable driver does not "
              "excuse itself." % (n, d), file=sys.stderr)
        rc = max(rc, 1)
    for n, d in buckets["unsound"]:
        print("[!]   UNSOUND: %s — PyCSL PROVES a postcondition the program REFUTES (%s)."
              % (n, d), file=sys.stderr)
        rc = max(rc, 1)
    if buckets["out_of_scope"]:
        print("[*]   OUT OF SCOPE (CPython did not return an int; these drivers are meant "
              "to be TOTAL) — reported, never fatal: %s"
              % ", ".join(n for n, _ in buckets["out_of_scope"]))
    if buckets["incomplete"]:
        print("[*]   incomplete (claim is TRUE of the program, PyCSL does not prove it — "
              "reported, not fatal): %s"
              % ", ".join(n for n, _ in buckets["incomplete"]))
    if rc:
        print("[!] value-differential: an `#@ ensures` is a claim about what the program "
              "COMPUTES. A program that demonstrably computes something else must not "
              "satisfy it.", file=sys.stderr)
        return rc
    print("[+] value-differential: OK — no driver proves a value claim that CPython refutes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
