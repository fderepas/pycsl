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

      THE DISTINCTION WAS KEPT IN GEN #30, and gen #31 DISSOLVED IT for this one site by
      making the evidence structural instead of a search. `ForExpand` is constructed in
      EXACTLY ONE place in the front-end (`Module2_Parser._parse_for_block`, as its final
      `return`), and the statement immediately before it is `if not clauses:
      self._err(...)`. An empty-clause `ForExpand` therefore cannot exist in any tree the
      parser produces — which is (A)-strength, not "no spelling I know of". The site is now
      in the coverage plane's NOT_SOURCE_REACHABLE_FRAGMENTS, and
      `forexpand_construction_invariant()` below re-derives the invariant from the shipping
      AST on every run and REFUSES if a second construction site appears, so the
      reclassification cannot outlive the fact it rests on.

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
import ast
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
    ("src/pycsl/frontend/pure_ast.py", "type_comments not yet implemented"),
    ("src/pycsl/frontend/exec_splice.py", "splice rejects a nested exec"),
]


EXPECTED_CARRIERS = ["span-missing", "callable-tag-no-arrow", "callable-tag-empty-part",
                     "opaque-stmt", "type-comments-parse", "for-expand-empty-body",
                     "exec-splice-nested"]


def carriers():
    """[(name, kind, expect, fire_fn, control_fn)] — kind is 'code' or 'msg'."""
    from core_ir_semantic import _check_span, _check_callable_params
    from module6_whyml.statements import StatementEmissionMixin
    from frontend.Module2_Parser import ForExpand, Number
    from frontend.Module3_Weaver import PyCSLWeaver
    from frontend import pure_ast
    from frontend.exec_splice import splice_constant_exec

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
        # `type_comments` is an API PARAMETER of `pure_ast.parse`, not a source construct:
        # the pipeline never passes it, so no `.py` file can reach this refusal.
        ("type-comments-parse", "msg", "type_comments not yet implemented",
         lambda: pure_ast.parse("x = 1\n", type_comments=True),
         lambda: pure_ast.parse("x = 1\n")),
        ("for-expand-empty-body", "msg", " in range(...)`: empty body",
         lambda: PyCSLWeaver._desugar_for(
             [ForExpand(var="i", lo=Number(0), hi=Number(3), clauses=[])]),
         lambda: PyCSLWeaver._desugar_for([])),
        # (#49) gen #31 — CATEGORY (B), and DELIBERATELY NOT RECLASSIFIED. The constant-exec
        # splice refuses a NESTED `exec(...)`, and `check-refusal-witness-coverage` counts it
        # as having no witness. Running it through the pipeline never reaches it: EVERY
        # spelling tried (`exec("exec('x=1')")` in a function, the same at module scope, and
        # `exec("if True:\n    x = 1")`) is refused FIRST by `Module3_Weaver`'s name-rebinding
        # check at line 3287 — the weaver runs BEFORE `splice_constant_exec` in
        # `_run_pipeline`. The plain `exec("x = 1")` DOES splice and verifies, so the splice
        # itself is live; it is the nested spelling that never arrives.
        # WHY THIS IS (B) AND NOT (A): "three spellings are refused earlier" is not "the
        # front-end constructs the shape itself". Gen #31 upgraded `for-expand-empty-body`
        # from (B) to (A) by PROVING a single-construction-site invariant; no comparable
        # invariant has been established here — the weaver's check is a large accumulation
        # over several unrelated shapes, and reading it is not the same as bounding it. So
        # this carrier DEMONSTRATES the refusal can fire and the coverage plane's count is
        # left alone. That asymmetry is the point of keeping the two categories apart.
        ("exec-splice-nested", "msg", "splice rejects a nested exec",
         lambda: splice_constant_exec(pure_ast.parse(
             'def f():\n    x = 0\n    exec("exec(\'x = 1\')")\n')),
         lambda: splice_constant_exec(pure_ast.parse(
             'def f():\n    x = 0\n    exec("x = 1")\n'))),
    ]


def forexpand_construction_invariant():
    """(#49) gen #31 — PROVE the `for-expand-empty-body` refusal is UNREACHABLE from source,
    rather than reporting that no spelling was found.

    Gen #30 demonstrated this carrier here but DECLINED to reclassify the site in
    `check-refusal-witness-coverage.py`, and said exactly why: "no spelling I know of
    reaches it" is weaker than "the front-end constructs the shape itself". That was the
    right call on the evidence it had. The evidence is now stronger, and it is STRUCTURAL:

      * `ForExpand` is CONSTRUCTED IN EXACTLY ONE PLACE in the whole front-end —
        `Module2_Parser._parse_for_block` — and
      * that construction is immediately preceded by `if not clauses: self._err(...)`,
        which raises.

    So a `ForExpand` whose `clauses` is empty cannot exist in any tree the parser produces,
    and `Module3_Weaver._desugar_for`'s `if not c.clauses` is a backstop on a shape only a
    hand-built node can have — the SAME category as the span / callable-tag / opaque-stmt
    sites, not the weaker "an earlier check owns the shape" category.

    THE THREE SPELLINGS THAT WERE RUN before this was written down, because "unreachable"
    earns nothing from a reading alone: an empty `#@ for` body is refused by
    `Module1_Ingestor._fold_blocks` ("`for i in range(0, 3)`: empty body" — that is what
    corpus 1772 actually fires); a body holding only a comment, a nested `#@ for`, or an
    `assigns` clause is refused by the Module 2 grammar ("for block requires at least one
    clause (got NAME 'assigns')"). Two different refusals stand in front of this one, and
    the invariant below is why there is no third spelling to look for.

    This function RE-DERIVES the invariant from the shipping AST every run. If a second
    construction site appears, or the guard in front of the existing one is removed or
    renamed, it returns a reason string and this plane REFUSES — which also invalidates the
    reclassification in the coverage plane, by design.
    """
    rel = "src/pycsl/frontend/Module2_Parser.py"
    path = os.path.join(ROOT, rel)
    try:
        tree = ast.parse(open(path, errors="replace").read())
    except Exception as exc:
        return "%s does not parse: %s" % (rel, exc)

    sites = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "ForExpand"):
                sites.append((fn, node))
    if len(sites) != 1:
        return ("ForExpand is constructed at %d site(s), expected exactly 1 (%s)"
                % (len(sites), ", ".join(sorted({f.name for f, _ in sites})) or "none"))

    fn, call = sites[0]
    # The construction must be the function's LAST statement, and the statement before it
    # must be `if not <name>: <something that raises>` over the SAME name passed as the
    # clause list argument.
    if len(fn.body) < 2:
        return "%s has no guard statement before the ForExpand construction" % fn.name
    last, prev = fn.body[-1], fn.body[-2]
    if not (isinstance(last, ast.Return) and last.value is call):
        return ("the single ForExpand construction is not %s's final `return` — the guard "
                "below no longer dominates it" % fn.name)
    clause_arg = call.args[3] if len(call.args) >= 4 else None
    if clause_arg is None:
        for kw in call.keywords:
            if kw.arg == "clauses":
                clause_arg = kw.value
    if not isinstance(clause_arg, ast.Name):
        return "the ForExpand `clauses` argument is not a plain name; the guard cannot be matched"
    if not (isinstance(prev, ast.If) and isinstance(prev.test, ast.UnaryOp)
            and isinstance(prev.test.op, ast.Not)
            and isinstance(prev.test.operand, ast.Name)
            and prev.test.operand.id == clause_arg.id):
        return ("the statement before the ForExpand construction is not `if not %s:` — the "
                "emptiness guard is gone or renamed" % clause_arg.id)
    raises = any(isinstance(n, ast.Raise)
                 or (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                     and n.func.attr == "_err")
                 for n in ast.walk(prev))
    if not raises:
        return ("`if not %s:` no longer raises (no `raise` and no `self._err(...)`), so an "
                "empty-clause ForExpand can now be built" % clause_arg.id)
    return None


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

    # (#49) gen #31 — the STRUCTURAL invariant that licenses reclassifying
    # `for-expand-empty-body` as NOT SOURCE-REACHABLE in check-refusal-witness-coverage.py.
    # It is re-derived from the shipping AST on every run, so the reclassification cannot
    # outlive the fact it rests on.
    why = forexpand_construction_invariant()
    if why is not None:
        print("[!] frontend-ir-backstops: REFUSING — the ForExpand single-construction-site "
              "invariant no longer holds:")
        print("        " + why)
        print("    `check-refusal-witness-coverage.py` classifies the Module 3 for-block "
              "empty-body refusal as NOT SOURCE-REACHABLE ON THE STRENGTH OF THIS "
              "INVARIANT. With it broken, that site may now be reachable and owes a corpus "
              "witness again. THIS IS A REFUSAL, NOT A PASS.")
        return 2

    from errors import PyCSLSemanticError, PyCSLParseError
    refusals = [PyCSLSemanticError, PyCSLParseError]
    # `pure_ast` raises its own `PyCSLSyntaxError` for the type_comments backstop; it is a
    # PyCSL refusal like the others and must count as one, not as a foreign exception.
    try:
        from errors import PyCSLSyntaxError
        refusals.append(PyCSLSyntaxError)
    except ImportError:
        try:
            from frontend.pure_ast import PyCSLSyntaxError
            refusals.append(PyCSLSyntaxError)
        except ImportError:
            pass
    refusals = tuple(refusals)

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
    print("[+] frontend-ir-backstops: OK — SIX of the seven are unreachable from a .py "
          "source: four "
          "because the front-end builds the shape itself (span, callable tag, opaque "
          "stmt), one because `type_comments` is an API parameter the pipeline never "
          "passes, and the for-expand empty body because ForExpand has EXACTLY ONE "
          "construction site, guarded by `if not clauses: self._err(...)` (invariant "
          "re-derived from the shipping AST above). That is why corpus witness 1772 fires "
          "[Module1] and not [Module3], and why gen #31 could reclassify the site. The "
          "SEVENTH — the exec-splice nested-exec refusal — is demonstrated here and "
          "DELIBERATELY NOT reclassified: every spelling tried is refused earlier by "
          "Module3_Weaver's name-rebinding check, and 'three spellings are refused first' "
          "is category (B), not the (A)-strength invariant the for-expand site earned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
