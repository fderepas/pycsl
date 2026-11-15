# OPEN ROUTE #601 — A DOTTED NAME INSIDE AN `except (A, mod.B)` TUPLE IS SILENTLY DROPPED (Module5 _py_stmt_try), SO THE MODEL LETS mod.B ESCAPE WHERE CPYTHON CATCHES IT
**Status: REPAIRED (driver run #7, executor u44, branch run7-u44 off 952bf7891; annotations §7.601). Mechanism: a fail-closed front-end refusal in `pycsl.py::_run_pipeline` (twin `\trusted`; `_py_stmt_try`, whose twin is VERIFIED, is untouched): an element of a handler tuple that is not a bare name, in any function the file lowers (`\trusted` / abstract ones are not lowered) or at module level, is refused (`PYCSL-R601-HANDLER-TUPLE-NON-NAME`).** Opened as: Status OPEN, Severity 1, PRE-EXISTING (proves at base 73fd1874f and at L9). Found by red team rt58 (lvQ's report flagged the dotted-handler drop).** A handler that is ONLY a dotted name lowers to an undeclared `PyCSL_Exception` and fails the type check (refused by accident, not by a guard).

## Exemplar (witnesses-r601/)
- d07_dotted_else_branch.py: `except (ZeroDivisionError, builtins.ValueError)` lowers to `with ZeroDivisionError` only; `ensures \result == 2` proves; CPython returns 7.
(Route number #600 skipped: annotations §7.600 is used by dict-value-model-r4.)

## The repair (driver run #7, executor u44)

RULE (annotations §7.601, `PYCSL-R601-HANDLER-TUPLE-NON-NAME`), a front-end refusal in `pycsl.py::_run_pipeline`
(twin `\trusted`), placed after Module 6 and routes #590 / #597: in every unit the file lowers -- each top-level
def and each method of a top-level class (Module 5's names) whose IR function is not `\trusted` / abstract, and
every other top-level / class-body statement -- an element of an `except (...)` tuple that is not a bare name is
refused. `Module5_IREmitter._py_stmt_try` (twin VERIFIED) is untouched: no emission moves. The mirror's three
dotted tuple handlers (`audit_proof_reverify._cache_load`, `_coqc_version`, `_lean_version`) are in `\trusted`
functions and are not judged. A handler that is ONLY a dotted name is left as it is (it lowers to the undeclared
`PyCSL_Exception` and fails the Why3 type check; rt58 d01 / d03 / d12-d14).
Advice: import the class by name and write `except (A, B):` (control 9964: `from builtins import ValueError`,
`except (ZeroDivisionError, ValueError)`, the true two-path claim).

## Witnesses and measurements (u44)

- rt58 d07 (and corpus 9953) REFUSED PYCSL-R601-HANDLER-TUPLE-NON-NAME in default / typed / store; 9954 (dotted
  element first) likewise, PROVED at base 952bf7891 (full proof, default). Control 9964 PROVED x3 at HEAD.
- Over-refusal: corpus root / pyref 0 MOVED / 0 GONE / 0 APPEARED; mirror 53 / 53 identical (the mirror's three
  dotted tuple handlers are in `\trusted` functions). Logs: `/home/fabrice/git/pycsl-u44/scratchpad/u44/`.
