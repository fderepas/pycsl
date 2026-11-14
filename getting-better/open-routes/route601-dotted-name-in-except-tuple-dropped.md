# OPEN ROUTE #601 — A DOTTED NAME INSIDE AN `except (A, mod.B)` TUPLE IS SILENTLY DROPPED (Module5 _py_stmt_try), SO THE MODEL LETS mod.B ESCAPE WHERE CPYTHON CATCHES IT
**Status: OPEN, Severity 1, PRE-EXISTING (proves at base 73fd1874f and at L9). Found by red team rt58 (lvQ's report flagged the dotted-handler drop).** A handler that is ONLY a dotted name lowers to an undeclared `PyCSL_Exception` and fails the type check (refused by accident, not by a guard).

## Exemplar (witnesses-r601/)
- d07_dotted_else_branch.py: `except (ZeroDivisionError, builtins.ValueError)` lowers to `with ZeroDivisionError` only; `ensures \result == 2` proves; CPython returns 7.
(Route number #600 skipped: annotations §7.600 is used by dict-value-model-r4.)
