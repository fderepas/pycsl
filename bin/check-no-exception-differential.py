#!/usr/bin/env python3
"""SOUNDNESS PLANE — `#@ no_exception` measured against CPython, not against a curated list.

WHY THIS EXISTS. SIX separate soundness routes live in the exception model — #64 (a missing
trigger row), #65 (four rows consulted by NOTHING, one of them the literal `"true"`), #66
(three more missing rows), #68 (three more, one a row that existed and was never injected),
#71 (an ERASED operation, which has no emission site and so can carry no obligation) and #72
(another missing row). Every probe aimed at that surface found something.

The common fact behind all six: **nothing relates `exception_model.TRIGGERS` to the set of
operations the emitter actually EMITS.** `bin/check-trigger-rows-live.py` scans FROM the
table and checks each row is consulted or refused — it cannot see a MISSING row, and it
reported green on all six.

THIS PLANE SCANS FROM THE OTHER SIDE, AND IT CURATES NOTHING. Each driver in
`test-suite/no-exception-differential/` declares `#@ no_exception \\all` and RUNS itself under
`__main__`. The plane executes both halves:

    CPython RAISES  + PyCSL PROVES   -> RED. `no_exception` is a POSITIVE claim about runtime
                                        behaviour, made about a body that demonstrably raises.
    CPython RAISES  + PyCSL refuses  -> green (the honest answer).
    CPython RETURNS + PyCSL PROVES   -> green.
    CPython RETURNS + PyCSL refuses  -> INCOMPLETE. Reported, never fatal.

**THE POPULATION GUARD IS THE POINT.** A gate of this shape is trivially satisfiable by
refusing every program, so it fails unless the corpus contains BOTH at least one driver that
CPython raises on AND at least one it returns from, and unless at least one returner actually
PROVES. Without that, "all green" could mean "the emitter refuses everything", which is not
what anyone wants to certify.

A driver cannot lie about its own behaviour, so this population can only be wrong by being
too SMALL — which is visible in the counts printed on every run.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from pycsl import exception_model as EM          # noqa: E402
DRIVERS = os.path.join(ROOT, "test-suite", "no-exception-differential")
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")
MIN_DRIVERS = 10


# Run the driver under CPython through a wrapper that reports the exception CLASS.
# The drivers stay plain -- nothing about them has to be curated for this to work.
_WRAPPER = (
    "import runpy, sys\n"
    "try:\n"
    "    runpy.run_path(sys.argv[1], run_name='__main__')\n"
    "except BaseException as e:\n"
    "    sys.stderr.write('PYCSL_EXC:' + type(e).__name__ + chr(10))\n"
    "    raise SystemExit(3)\n"
)


def _cpython_raise_class(path):
    """Run the driver under CPython.

    Returns None if it returned normally, otherwise the NAME of the exception class
    it raised -- or the sentinel "?" if it exited non-zero without us being able to
    name the class. "?" is treated as IN SCOPE everywhere below, so an unparseable
    failure keeps the old, conservative verdict rather than quietly excusing itself.
    """
    env = dict(os.environ, PYTHONHASHSEED="0")
    r = subprocess.run([sys.executable, "-c", _WRAPPER, path], cwd=DRIVERS,
                       capture_output=True, text=True, timeout=120, env=env)
    if r.returncode == 0:
        return None
    for line in r.stderr.split("\n"):
        if line.startswith("PYCSL_EXC:"):
            return line[len("PYCSL_EXC:"):].strip() or "?"
    return "?"


def _claimed_exceptions(path):
    """The set of exception names this driver's `#@ no_exception` actually CLAIMS.

    `\all` expands to `KNOWN_EXCEPTIONS` -- FIVE names -- not to "every exception
    Python has. That distinction is the whole point of this function: a body that
    aborts with `AssertionError` violates nothing a `\all` contract said, because
    `AssertionError` is deliberately outside the model (it has no mathematical
    implicit trigger; see the route #16 note in `frontend/desugar.py`).

    Returns None when the driver declares no `no_exception` at all, which makes
    every raise out of scope.
    """
    claimed = set()
    seen = False
    for line in open(path):
        m = re.match(r"\s*#@\s*no_exception\s+(.*)$", line)
        if not m:
            continue
        seen = True
        spec = m.group(1).strip()
        if spec.startswith("\\all"):
            claimed |= set(EM.KNOWN_EXCEPTIONS)
        else:
            for name in spec.split(","):
                name = name.strip()
                if name:
                    claimed.add(name)
    return claimed if seen else None


def _in_scope(raised, claimed):
    """Does `raised` violate a claim over the `claimed` set?

    Uses the model's own subclass relation, so a claim over `OSError` is violated by
    a raised `FileNotFoundError`. The unnameable sentinel is always in scope.
    """
    if raised == "?":
        return True
    if not claimed:
        return False
    return any(EM.handler_catches(c, raised) for c in claimed)


def _pycsl_proves(path):
    env = dict(os.environ, PYTHONHASHSEED="0")
    r = subprocess.run([sys.executable, PYCSL, path], cwd=ROOT, capture_output=True,
                       text=True, timeout=600, env=env)
    out = r.stdout + r.stderr
    if "'why3' command not found" in out:
        return None          # tool missing — never report a verdict from it
    for line in out.split("\n"):
        if line.startswith("[+] Verification SUCCESS"):
            return True
    return False


def main():
    if not os.path.isdir(DRIVERS):
        print("[!] no-exception-differential: driver directory missing — NOT A PASS.",
              file=sys.stderr)
        return 2
    names = sorted(f for f in os.listdir(DRIVERS) if f.endswith(".py"))
    if len(names) < MIN_DRIVERS:
        print("[!] no-exception-differential: only %d driver(s), below the floor of %d. A "
              "gate that cannot tell 'nothing is wrong' from 'I looked at nothing' is not a "
              "gate. NOT A PASS." % (len(names), MIN_DRIVERS), file=sys.stderr)
        return 2

    unsound, incomplete, out_of_scope = [], [], []
    n_raise = n_return = n_return_proved = 0
    for name in names:
        path = os.path.join(DRIVERS, name)
        proves = _pycsl_proves(path)
        if proves is None:
            print("[*] no-exception-differential: SKIP — why3 is not on PATH, so no verdict "
                  "is available. (A missing tool is not a finding.)")
            return 0
        raised = _cpython_raise_class(path)
        if raised is not None:
            n_raise += 1
            claimed = _claimed_exceptions(path)
            if _in_scope(raised, claimed):
                if proves:
                    unsound.append("%s (%s)" % (name, raised))
            else:
                # CPython aborts, and the contract is still TRUE AS WRITTEN, because the
                # exception it raised is not one the contract claimed anything about.
                # Not a failure -- but never silent: this population is the honest
                # measure of how much weaker `\all` is than its name.
                out_of_scope.append("%s (%s%s)" % (name, raised,
                                                   "" if proves else ", not proved"))
        else:
            n_return += 1
            if proves:
                n_return_proved += 1
            else:
                incomplete.append(name)

    print("[*] no-exception-differential: %d driver(s) — %d that CPython RAISES on, %d it "
          "RETURNS from (%d of those prove)." % (len(names), n_raise, n_return,
                                                 n_return_proved))
    rc = 0
    if n_raise == 0 or n_return == 0 or n_return_proved == 0:
        print("[!] no-exception-differential: the corpus does not contain BOTH a raising and "
              "a PROVING non-raising driver. This gate is satisfiable by refusing "
              "everything, so it is meaningless without both. NOT A PASS.", file=sys.stderr)
        rc = 2
    if out_of_scope:
        print("[*]   OUT OF SCOPE — CPython aborts, but with an exception the contract "
              "does NOT claim, so the claim holds as written. `\\all` expands to exactly "
              "%d names (%s), NOT to every exception Python has. Reported, never fatal, "
              "and never silent: %s"
              % (len(EM.KNOWN_EXCEPTIONS), ", ".join(sorted(EM.KNOWN_EXCEPTIONS)),
                 ", ".join(out_of_scope)))
    for name in unsound:
        print("[!]   UNSOUND: %s — CPython raises an exception this contract CLAIMS "
              "cannot happen, and PyCSL PROVES the claim." % name, file=sys.stderr)
        rc = max(rc, 1)
    if incomplete:
        print("[*]   incomplete (CPython returns, PyCSL does not prove — reported, not "
              "fatal): %s" % ", ".join(incomplete))
    if rc:
        print("[!] no-exception-differential: `no_exception` is a POSITIVE claim about "
              "runtime behaviour. A body that demonstrably raises must not satisfy it.",
              file=sys.stderr)
        return rc
    print("[+] no-exception-differential: OK — no driver that CPython raises on satisfies "
          "its `no_exception` claim.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
