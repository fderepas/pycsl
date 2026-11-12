# OPEN ROUTE #590 — raise OF AN INSTANCE OF A NON-EXCEPTION CLASS (dataclass / plain class) PROVES WHILE CPYTHON RAISES TypeError
**Status: REPAIRED (driver run #6, executor u39, branch run6-u39; annotations §7.590). Was: OPEN, Severity 1, pre-existing (rt56 R56-B; proves on 822621340 and int55).** Witnesses witnesses-r590/ (ha1780, ha1781).

## REPAIR (driver run #6, executor u39, base c55a7b233 = run6-int56, branch run6-u39)

- RULE (annotations §7.590), `pycsl.py::_run_pipeline` in route #175's source block (main file; classes resolved over the
  main file and the dependency modules it imports, `_tall175`; twin `\trusted`; inline, no new def, no axiom; no emission
  change): the raised name of `raise X(...)` / `raise X` is REFUSED, `PYCSL-R590-RAISE-NON-EXCEPTION`, when it is a class
  whose bases do not reach a builtin `BaseException` subclass through the classes in view (a base that cannot be placed is
  refused too), a non-exception builtin, or a `def` (`raise mk()` raises whatever `mk` returns); a raised literal /
  display / f-string / operator / comprehension / lambda is refused. Class aliases (`A = E`, route #175's `_alias175`) and
  import aliases (`from m import E as _E`) are followed; an enclosing handler's `except ... as` name is an exception. A
  name that no file in view binds is left to the name rules (the mirror's `frontend/desugar.py` raises an unbound
  `PyCSLParseError`, a mirror-model artefact, not refused here).
- RESIDUAL (named): `raise v` of a LOCAL VARIABLE holding a non-exception, `raise errs[0]`, `raise H.err` are not
  judged here; measured at HEAD they are refused by other rules (route #174) or are Why3-ill-typed (no proof).
- OVER-REFUSAL BY DESIGN (fail-closed): a user exception class derived from a class the files in view do not define and
  that is not a builtin (`class E(json.JSONDecodeError)`, `class E(SomeImportedBase)` whose module is not on the
  program's path) cannot be placed in the hierarchy and is refused when raised; the corpus, python-reference and the
  mirror hold no such raise (see INERTNESS).
- WITNESSES / CONTROLS / INERTNESS: shared with routes #589 / #591 / #590, recorded once in `route589-raise-extra-ctor-args-dropped.md` (section WITNESSES, CONTROLS, INERTNESS).
