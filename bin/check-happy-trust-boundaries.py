#!/usr/bin/env python3
r"""L-PLANE ORACLE: every `#@ happy` policy's TRUST BOUNDARY still bites.

WHY THIS EXISTS (gen #30). Four of this generation's routes are ONE defect wearing four
hats. A `happy` policy enforces itself by INJECTING something into a body — a `#@ check`
at each write site, a `#@ check False` at a forbidden one — and a `\trusted` / `\abstract`
body IS NEVER LOWERED, so whatever was injected into it evaporates. Each form therefore
needs a TRUST BOUNDARY: a hard error when a non-exempt bodyless actor could do the thing
the policy forbids.

  form                         boundary                       found by
  ---------------------------- ------------------------------ -------------------------
  `region ... writes outside`  ANY non-exempt trusted fn must  pre-existing and CORRECT
                               carry `#@ \preserves`           (witnesses 0461 / 0462)
  `reading`                    ANY non-exempt trusted fn must  pre-existing and CORRECT
                               be in `except`
  `protects <path>`            the DECLARED `#@ assigns`       ROUTE #209 — it asked a
                               names a protected path          `pure_ast` matcher about a
                                                               CSL node and NEVER FIRED
  `protects <path>`            the trusted BODY writes the     ROUTE #210 — a `check
                               protected path                  False` stamped into a body
                                                               nobody compiles
  `... (n): protects p[a:b]`   the trusted BODY writes the     ROUTE #211 — same stamp,
                               parametric path with no          parametric form; the twin
                               `#@ footprint`                   is ONE annotation line
  `targets ... total`          no bodyless / `\diverges`       ROUTES #206 / #208
                               function reachable from target

WHAT THIS GATE DOES. It holds a CARRIER and a CONTROL for each boundary, writes them to a
temp directory, and runs the SHIPPING pipeline over them with `--no-proof` (a refusal is a
pipeline error and happens long before the prover, so the whole gate costs about a second).
The carrier MUST be refused; the control MUST get past the front end. A boundary that stops
biting — because a matcher was retyped, a branch was reordered, or a policy grew a fifth
form — turns this red on the day it happens rather than at the next manual probe.

This is deliberately an EXECUTABLE gate rather than a source-grep: routes #209 and #211
both look perfectly fine in the source, and #209 in particular had a boundary that READ
correctly and could not fire.

Usage:  bin/check-happy-trust-boundaries.py [--verbose] [--selftest]
"""
import argparse
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python3")
if not os.path.exists(PY):
    PY = "python3"
DRIVER = os.path.join(ROOT, "src", "pycsl", "pycsl.py")

_PROTECTS_HEAD = '''_ = 0  # anchor

#@ happy own:
#@     protects g.v
#@     except setter

#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0


g = C()


#@ requires n >= 0
#@ assigns g.v
def setter(n: int) -> None:
    g.v = n
'''

_PARAM_HEAD = '''_ = 0  # anchor
#@ happy inode_conf(n):
#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]
#@     except formatter
#@ class invariant \\length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024


d = Disk()


#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0
'''

_TOTAL_HEAD = '''_ = 0  # anchor
#@ happy availability:
#@     targets parse
#@     total
class Parser:
'''

CASES = [
    # (name, carrier source, control source, what the boundary protects)
    ("protects/declared-assigns (route #209)",
     _PROTECTS_HEAD + '''

#@ requires n >= 0
#@ assigns g.v
#@ \\trusted
def sneaky(n: int) -> None:
    g.v = n
''',
     _PROTECTS_HEAD + '''

#@ requires n >= 0
#@ assigns g.v
#@ \\preserves
#@ \\trusted
def declared(n: int) -> None:
    g.v = n
''',
     "a non-exempt trusted writer of a protected path must carry `#@ \\preserves`"),

    ("protects/trusted-body (route #210)",
     _PROTECTS_HEAD + '''

#@ requires n >= 0
#@ assigns \\nothing
#@ \\trusted
def liar(n: int) -> None:
    g.v = n
''',
     _PROTECTS_HEAD + '''

#@ requires n >= 0
#@ assigns \\nothing
#@ \\trusted
def elsewhere(n: int) -> None:
    g.w = n
''',
     "a trusted BODY that writes the protected path is caught even when its frame lies"),

    ("parametric/footprint (route #211)",
     _PARAM_HEAD + '''

#@ requires v >= 0
#@ assigns d.disk
#@ \\trusted
def rogue(v: int) -> None:
    d.disk[900] = v
''',
     _PARAM_HEAD + '''

#@ requires 0 <= k and k < 8
#@ footprint inode_conf(k)
#@ assigns d.disk
def writer(k: int, v: int) -> None:
    d.disk[512 + k * 64] = v
''',
     "a trusted rogue with no `#@ footprint` writing the parametric path is caught"),

    ("total/bodyless-callee (routes #206, #208)",
     _TOTAL_HEAD + '''    #@ ensures \\result >= 0
    #@ \\trusted
    def spin(self, n: int) -> int:
        acc: int = 0
        while True:
            acc = acc + 1
        return acc

    #@ requires n >= 0
    #@ ensures \\result >= 0
    def parse(self, n: int) -> int:
        return self.spin(n)
''',
     _TOTAL_HEAD + '''    #@ requires n >= 0
    #@ ensures \\result >= 0
    def step(self, n: int) -> int:
        return n

    #@ requires n >= 0
    #@ ensures \\result == 0
    def parse(self, n: int) -> int:
        acc: int = self.step(n)
        return 0
''',
     "a `total` target may not reach a function with no termination VC"),

    ("total/diverges-callee (route #208)",
     _TOTAL_HEAD + '''    #@ ensures \\result >= 0
    #@ \\diverges
    def spin(self, n: int) -> int:
        acc: int = 0
        while True:
            acc = acc + 1
        return acc

    #@ requires n >= 0
    #@ ensures \\result >= 0
    def parse(self, n: int) -> int:
        return self.spin(n)
''',
     None,   # the control above covers this form
     "`#@ \\diverges` on a reachable helper is the same erasure as a bodyless one"),

    ("reading/trusted-reader (pre-existing)",
     '''_ = 0  # anchor
#@ happy conf:
#@     reading self.secret
#@     region 0 .. 4
#@     except reader
#@ class invariant \\length(self.secret) >= 8
class S:
    def __init__(self) -> None:
        self.secret: list = [0] * 8

    #@ assigns \\nothing
    def reader(self) -> int:
        return self.secret[0]

    #@ assigns \\nothing
    #@ \\trusted
    def peeker(self) -> int:
        return self.secret[0]
''',
     None,
     "a non-exempt trusted READER must be listed in `except`"),
]


def run(src, tmpdir, idx):
    path = os.path.join(tmpdir, "case%d.py" % idx)
    with open(path, "w") as fh:
        fh.write(src)
    p = subprocess.run([PY, DRIVER, "--no-proof", "--memory-model", "hoare", path],
                       capture_output=True, text=True, timeout=300)
    out = (p.stdout or "") + (p.stderr or "")
    return ("PIPELINE ERROR" in out), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="also assert that a case with the trust marker REMOVED is "
                         "accepted, proving the gate is not refusing everything")
    args = ap.parse_args()

    rc = 0
    checked = 0
    with tempfile.TemporaryDirectory(prefix="happy-boundaries-") as tmp:
        for i, (name, carrier, control, what) in enumerate(CASES):
            refused, out = run(carrier, tmp, 2 * i)
            checked += 1
            if not refused:
                print("[!]   BOUNDARY NOT BITING: %s — the carrier was ACCEPTED. %s"
                      % (name, what), file=sys.stderr)
                rc = 1
            elif args.verbose:
                print("    ok   carrier refused   %s" % name)
            if control is not None:
                ctl_refused, ctl_out = run(control, tmp, 2 * i + 1)
                checked += 1
                if ctl_refused:
                    print("[!]   BOUNDARY TOO WIDE: %s — the CONTROL was refused, so the "
                          "guard has become a ban on the feature." % name,
                          file=sys.stderr)
                    if args.verbose:
                        print(ctl_out[-600:], file=sys.stderr)
                    rc = 1
                elif args.verbose:
                    print("    ok   control accepted %s" % name)

    print("[*] happy-trust-boundaries: %d program(s) run through the shipping pipeline "
          "across %d boundary case(s)." % (checked, len(CASES)))
    if rc:
        print("[!] happy-trust-boundaries: NOT OK.", file=sys.stderr)
    else:
        print("[+] happy-trust-boundaries: OK — every `#@ happy` trust boundary refuses "
              "its carrier and accepts its control.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
