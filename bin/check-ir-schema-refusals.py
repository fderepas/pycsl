#!/usr/bin/env python3
r'''L-PLANE ORACLE: the EIGHT `ir_schema.validate_ir` refusals, demonstrated EXECUTABLY.

WHY THIS EXISTS (#49, gen #30). `bin/check-refusal-witness-coverage.py` measures which of
the compiler's 198 refusals a corpus witness has ever made FIRE. After its census was
repaired (85 -> 131 demonstrated), 67 remained — and eight of those are
`ir_schema.validate_ir`'s structural checks, which NO corpus witness can ever reach:

    PYCSL-IR-NOTDICT  MISSINGTOP  VERSION  FUNCSLIST  FUNCDICT  MISSINGFUNC
    CONTRACTSDICT  MISSINGCONTRACTS

`validate_ir` runs on the IR THE FRONT-END JUST BUILT (pycsl.py:511) and again at the
JSON boundary (pycsl.py:962). A `.py` source file cannot make Module 5 emit an IR whose
`functions` is not a list or whose `contracts` is not a dict — the front-end constructs
those shapes itself. So these refusals are not "undemonstrated because nobody wrote the
witness"; they are UNREACHABLE FROM SOURCE, and adding corpus files would never move them.

THAT DISTINCTION IS WORTH DRAWING RATHER THAN LEAVING IN A DEBT COUNTER, because the two
call for opposite work: an unwritten witness wants a corpus file, an unreachable-from-
source refusal wants a DIRECT gate. This is the direct gate. It builds a malformed IR for
each of the eight, calls the real `validate_ir`, and asserts the real code fires.

AND THERE WAS NOTHING ELSE. A grep for `validate_ir` or any `PYCSL-IR-*` code across
`test-suite/` finds ZERO hits: before this plane, the IR's own structural contract — the
thing standing between a malformed IR and the lowering — had no test of any kind.

THE CONTROL MATTERS AS MUCH AS THE CARRIERS. A minimal WELL-FORMED IR must validate
CLEANLY; without it, a `validate_ir` that raised unconditionally would pass all eight
carriers and this plane would certify a compiler that refuses everything.

THE #44 GUARD: the eight expected codes are checked against the codes actually PRESENT in
`src/pycsl/ir_schema.py`. If a code is renamed or a check deleted, this plane REFUSES
(rc=2) rather than quietly testing seven — a gate that cannot tell "all carriers fire"
from "the carrier I no longer have does not fire" must refuse.

Usage:  bin/check-ir-schema-refusals.py [--verbose] [--selftest-missing-carrier]
'''
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))


def _func(**over):
    """A well-formed IR function, with overrides."""
    f = {
        "name": "f",
        "symbol_table": {},
        "return_annotation": "int",
        "contracts": {"requires": [], "ensures": [], "assigns": [], "raises": []},
        "body": [],
        "function_variants": [],
        "diverges": False,
        "trusted": False,
        "bounded_int": False,
    }
    f.update(over)
    return f


def _ir(**over):
    ir = {"type_decls": [], "functions": [_func()]}
    ir.update(over)
    return ir


# (expected code, description, the malformed IR)
CARRIERS = [
    ("PYCSL-IR-NOTDICT", "the IR is not a dict at all", ["not", "a", "dict"]),
    ("PYCSL-IR-MISSINGTOP", "a required top-level key is absent",
     {"functions": []}),
    ("PYCSL-IR-VERSION", "a STAMPED but unsupported `ir_version`",
     _ir(ir_version="9.9")),
    ("PYCSL-IR-FUNCSLIST", "`functions` is not a list", _ir(functions={})),
    ("PYCSL-IR-FUNCDICT", "a member of `functions` is not a dict",
     _ir(functions=["nope"])),
    ("PYCSL-IR-MISSINGFUNC", "a function is missing a required IR key",
     _ir(functions=[{k: v for k, v in _func().items() if k != "body"}])),
    ("PYCSL-IR-CONTRACTSDICT", "a function's `contracts` is not a dict",
     _ir(functions=[_func(contracts=[])])),
    ("PYCSL-IR-MISSINGCONTRACTS", "a function's `contracts` is missing a clause kind",
     _ir(functions=[_func(contracts={"requires": [], "ensures": [], "assigns": []})])),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest-missing-carrier", action="store_true",
                    help="pretend one check has vanished from ir_schema.py; must exit 2 "
                         "(proves the #44 guard bites rather than testing seven quietly)")
    args = ap.parse_args()

    src = open(os.path.join(ROOT, "src", "pycsl", "ir_schema.py"),
               encoding="utf-8").read()
    present = set(re.findall(r'code="(PYCSL-IR-[A-Z]+)"', src))
    if args.selftest_missing_carrier and present:
        present.discard(sorted(present)[0])
    expected = {c for c, _d, _i in CARRIERS}
    missing = sorted(expected - present)
    extra = sorted(present - expected)
    if missing:
        print("[!] ir-schema-refusals: REFUSING — %s no longer appear(s) in "
              "src/pycsl/ir_schema.py. A carrier for a check that is gone is not a pass; "
              "delete the carrier deliberately or fix the rename." % ", ".join(missing),
              file=sys.stderr)
        return 2
    if extra:
        print("[!] ir-schema-refusals: REFUSING — NEW structural check(s) %s in "
              "ir_schema.py with no carrier here. Every `validate_ir` refusal must be "
              "demonstrated: add the malformed IR that fires it." % ", ".join(extra),
              file=sys.stderr)
        return 2

    from errors import PyCSLIRError
    from ir_schema import validate_ir

    rc, fired = 0, 0
    # THE CONTROL, first: a well-formed IR must validate cleanly. Without it a
    # `validate_ir` that raised unconditionally would satisfy all eight carriers.
    try:
        validate_ir(_ir())
        if args.verbose:
            print("    control  a minimal well-formed IR validates cleanly")
    except Exception as exc:
        print("[-] ir-schema-refusals: THE CONTROL FAILED — a minimal WELL-FORMED IR was "
              "refused (%r). Every carrier below is meaningless until this passes."
              % (exc,), file=sys.stderr)
        return 1

    for code, desc, ir in CARRIERS:
        try:
            validate_ir(ir)
        except PyCSLIRError as exc:
            got = getattr(exc, "code", None)
            if got == code:
                fired += 1
                if args.verbose:
                    print("    fires    %-26s %s" % (code, desc))
            else:
                print("[-] ir-schema-refusals: %s fired with code %r, expected %r (%s)."
                      % (desc, got, code, desc), file=sys.stderr)
                rc = 1
        except Exception as exc:
            print("[-] ir-schema-refusals: %s raised %r, not a PyCSLIRError."
                  % (desc, exc), file=sys.stderr)
            rc = 1
        else:
            print("[-] ir-schema-refusals: *** %s DID NOT FIRE *** — %s was accepted. The "
                  "IR's structural contract is what stands between a malformed IR and the "
                  "lowering." % (code, desc), file=sys.stderr)
            rc = 1

    print("[*] ir-schema-refusals: %d carrier(s), %d fired with the expected code; "
          "control OK." % (len(CARRIERS), fired))
    if rc:
        print("[!] ir-schema-refusals: NOT OK.", file=sys.stderr)
    else:
        print("[+] ir-schema-refusals: OK — all %d `validate_ir` refusals DEMONSTRATED, "
              "and a well-formed IR still validates." % len(CARRIERS))
    return rc


if __name__ == "__main__":
    sys.exit(main())
