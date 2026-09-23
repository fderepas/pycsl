#!/usr/bin/env python3
r'''L-PLANE ORACLE: FIVE front-end / lowering BACKSTOP refusals, demonstrated EXECUTABLY.

WHY THIS EXISTS (#49, gen #30). `bin/check-refusal-witness-coverage.py` measures which of
the compiler's 219 raise sites a corpus witness has ever made FIRE. After the census was
repaired it stood at 184 demonstrated and 17 not — and the 17 are not seventeen unwritten
witnesses. Read one by one, several of them CANNOT BE REACHED BY A `.py` SOURCE FILE at
all, for two different reasons, and the two call for opposite work:

  (A) THE SHAPE IS BUILT BY THE FRONT-END ITSELF. `_check_span` fires when an IR function
      carries no `line`; `_check_callable_params` fires on a malformed `callable:...->...`
      tag; the Module 6 statement dispatch fires on an `OpaqueStmt`. Module 5 stamps the
      spans, encodes the tags and classes the statements, so no source program can produce
      those shapes. These are the same category as the eight `PYCSL-IR-*` checks that
      `bin/check-ir-schema-refusals.py` already covers, and they want a DIRECT gate, not a
      corpus file.

  (B) AN EARLIER, STRICTER CHECK OWNS THE SHAPE. `Module3_Weaver._desugar_for` refuses a
      `ForExpand` with no clauses — but a source file spelling that (`#@ for i in
      range(0, 3):` with nothing indented under it) is refused FIRST by
      `Module1_Ingestor._fold_blocks`, which requires a 4-space-indented body under every
      block header. MEASURED: corpus witness
      `1772_gen30_witness_for_range_empty_body.py` was written for the Module 3 site and
      its census row reads `[Module1]: \`for i in range(0, 3)\`: empty body`. The witness
      is real, the refusal is real, and they are DIFFERENT REFUSALS — lesson (n3), a check
      that runs first retires the one behind it.

      THE DISTINCTION IS KEPT: (B) is demonstrated here but is NOT moved into the coverage
      plane's NOT_SOURCE_REACHABLE set, because "no spelling I know of reaches it" is
      weaker than "the front-end constructs the shape itself". Only the (A) sites are
      reclassified.

WHAT THIS PLANE DOES. For each carrier it calls the REAL function with the malformed
input and asserts the real code raises with the expected error code (or message fragment,
for the one site that carries no code). For each it also runs a WELL-FORMED CONTROL that
must NOT raise — without the control, a function that raised unconditionally would pass
every carrier and this plane would certify a compiler that refuses everything.

THE #44 GUARD: the expected codes and message fragments are checked against the text
actually present in the shipping sources. If a check is renamed, moved or deleted, this
plane REFUSES (rc=2) rather than quietly testing four — a gate that cannot tell "all
carriers fire" from "the carrier I no longer have does not fire" must refuse.

Usage:  bin/check-frontend-ir-backstop-refusals.py [--verbose] [--selftest-missing-carrier]
'''
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))

# (file the check lives in, text that must still be present) — the #44 guard's population.
GUARD_TEXT = [
    ("src/pycsl/core_ir_semantic.py", "PYCSL-SEM-SPAN"),
    ("src/pycsl/core_ir_semantic.py", "PYCSL-TY3-CALLABLE-SHAPE"),
    ("src/pycsl/module6_whyml/statements.py", "PYCSL-IR-OPAQUESTMT"),
    ("src/pycsl/frontend/Module3_Weaver.py", " in range(...)`: empty body"),
    ("src/pycsl/frontend/Module1_Ingestor.py", "`: empty body"),
]


EXPECTED_CARRIERS = ["span-missing", "callable-tag-no-arrow", "callable-tag-empty-part",
                     "opaque-stmt", "for-expand-empty-body"]


def carriers():
    """[(name, kind, expect, fire_fn, control_fn)] — kind is 'code' or 'msg'."""
    from core_ir_semantic import _check_span, _check_callable_params
    from module6_whyml.statements import StatementEmissionMixin
    from frontend.Module2_Parser import ForExpand, Number
    from frontend.Module3_Weaver import PyCSLWeaver

    class _Dispatch(StatementEmissionMixin):
        """The dispatch is reached with no emitter state: the OpaqueStmt branch is taken
        before any `self` field is read, which is what makes this callable at all."""

    return [
        ("span-missing", "code", "PYCSL-SEM-SPAN",
         lambda: _check_span({"name": "f"}, "ir-semantic"),
         lambda: _check_span({"name": "f", "line": 1, "col": 0}, "ir-semantic")),
        ("callable-tag-no-arrow", "code", "PYCSL-TY3-CALLABLE-SHAPE",
         lambda: _check_callable_params({"symbol_table": {"p": "callable:int"}}),
         lambda: _check_callable_params({"symbol_table": {"p": "callable:int,int->int"}})),
        ("callable-tag-empty-part", "code", "PYCSL-TY3-CALLABLE-SHAPE",
         lambda: _check_callable_params({"symbol_table": {"p": "callable:int,->"}}),
         lambda: _check_callable_params({"symbol_table": {"p": "callable:->int"}})),
        ("opaque-stmt", "code", "PYCSL-IR-OPAQUESTMT",
         lambda: _Dispatch()._stmts_to_whyml(
             [{"type": "totally_unknown_kind", "zz": 1}], set(), set(), "  "),
         lambda: _Dispatch()._stmts_to_whyml([], set(), set(), "  ")),
        ("for-expand-empty-body", "msg", " in range(...)`: empty body",
         lambda: PyCSLWeaver._desugar_for(
             [ForExpand(var="i", lo=Number(0), hi=Number(3), clauses=[])]),
         lambda: PyCSLWeaver._desugar_for([])),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest-missing-carrier", action="store_true",
                    help="drop one carrier; the #44 guard must REFUSE (rc=2)")
    args = ap.parse_args()

    # (#44) THE GUARD, FIRST: a carrier whose check no longer exists in the source is a
    # carrier this plane would silently stop testing.
    missing = []
    for rel, needle in GUARD_TEXT:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path) or needle not in open(path, errors="replace").read():
            missing.append("%s :: %r" % (rel, needle))
    if missing:
        print("[!] frontend-ir-backstops: REFUSING — the shipping source no longer "
              "contains %d expected check(s):" % len(missing))
        for m in missing:
            print("        " + m)
        print("    A gate that cannot tell 'all carriers fire' from 'the carrier I no "
              "longer have does not fire' must REFUSE. Re-point the carrier or delete it "
              "deliberately. THIS IS A REFUSAL, NOT A PASS.")
        return 2

    from errors import PyCSLSemanticError, PyCSLParseError
    refusals = (PyCSLSemanticError, PyCSLParseError)

    rows = carriers()
    if args.selftest_missing_carrier:
        rows = rows[:-1]
    # The count guard is the OTHER half of #44, and `--selftest-missing-carrier` exists to
    # prove it fires: dropping a carrier must REFUSE, not quietly test four. The self-test
    # is therefore NOT exempt from this check — exempting it would test nothing.
    if len(rows) < len(EXPECTED_CARRIERS):
        print("[!] frontend-ir-backstops: REFUSING — %d carrier(s), expected %d (%s). A "
              "carrier that silently disappears takes its refusal out of coverage with it. "
              "THIS IS A REFUSAL, NOT A PASS."
              % (len(rows), len(EXPECTED_CARRIERS), ", ".join(EXPECTED_CARRIERS)))
        return 2
    if [r[0] for r in rows] != EXPECTED_CARRIERS:
        print("[!] frontend-ir-backstops: REFUSING — carrier names %s do not match the "
              "expected %s." % ([r[0] for r in rows], EXPECTED_CARRIERS))
        return 2

    bad = []
    for name, kind, expect, fire, control in rows:
        try:
            fire()
            bad.append("%s: the malformed input did NOT raise" % name)
        except refusals as exc:
            got = getattr(exc, "code", None)
            if kind == "code" and got != expect:
                bad.append("%s: raised with code %r, expected %r" % (name, got, expect))
            elif kind == "msg" and expect not in str(exc):
                bad.append("%s: message %r does not contain %r" % (name, str(exc), expect))
            elif args.verbose:
                print("    CARRIER  %-24s fired: %s" % (name, str(exc)[:90]))
        except Exception as exc:                       # noqa: BLE001
            bad.append("%s: raised %s, not a PyCSL refusal (%s)"
                       % (name, type(exc).__name__, str(exc)[:80]))
        try:
            control()
            if args.verbose:
                print("    CONTROL  %-24s well-formed input accepted" % name)
        except refusals as exc:
            bad.append("%s: the WELL-FORMED CONTROL was refused (%s) — this plane would "
                       "certify a compiler that refuses everything" % (name, str(exc)[:70]))
        except Exception as exc:                       # noqa: BLE001
            bad.append("%s: control raised %s (%s)"
                       % (name, type(exc).__name__, str(exc)[:80]))

    if bad:
        print("[!] frontend-ir-backstops: %d carrier/control failure(s):" % len(bad))
        for b in bad:
            print("        " + b)
        return 1

    print("[*] frontend-ir-backstops: %d backstop refusal(s) DEMONSTRATED executably, "
          "each with a well-formed control that is accepted." % len(rows))
    print("[+] frontend-ir-backstops: OK — four are unreachable from a .py source because "
          "the front-end builds the shape itself (span, callable tag, opaque stmt); the "
          "fifth (for-expand empty body) is owned by Module1's earlier block check, which "
          "is why corpus witness 1772 fires [Module1] and not [Module3].")
    return 0


if __name__ == "__main__":
    sys.exit(main())
