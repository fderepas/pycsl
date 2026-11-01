# OPEN ROUTE #506 — A DIVISION (AND, BY THE SAME PATH, OTHER IMPLICIT-EXCEPTION TRIGGERS) INSIDE A SET / TUPLE DISPLAY, `len([...])`, OR AN `assert` TEST LOSES ITS ZeroDivisionError OBLIGATION — EVEN IN THE CLAIMED FUNCTION ITSELF UNDER `#@ no_exception ZeroDivisionError`
**Status: OPEN, Severity 1.** Found by route-repair executor u5 (driver run #4, 2026-11-01) while repairing #502, outside the callee summary #502 covers. Driver repro (session scratchpad `rp506/r.sh`, on main 51b6042ea's code, 2026-11-01T09:45Z): 8/8 witnesses rc=0 `Verification SUCCESS` while CPython breaks the claim.
Witnesses `witnesses-r506/` (8): `u5_setlit_own_claim.py`, `u5_tuplit_own_claim.py`, `u5_lenlist_own_claim.py`, `u5_assert_own_claim.py` (the function claims `#@ no_exception ZeroDivisionError` and evaluates `{10 // n}` / `(1, 10 // n)` / `len([10 // n])` / `assert 10 // n >= 0 or True`; CPython `f(0)` raises ZeroDivisionError), and the four `*_callee_handler.py` twins (a callee evaluates the same expression; the caller's `except ZeroDivisionError: return 2` arm is dead in the model; CPython returns 2 under `ensures \result == 1`).

```
WHAT: the per-operation trigger obligations of the exception model (pycsl-exception-model: division / modulo by zero, and
      by the same lowering path probably the other TRIGGERS rows) are injected where the lowered expression is a value the
      emitted WhyML keeps; a set display, a tuple display, the argument list of `len([...])` and an `assert` test whose value
      is short-circuited (`... or True`) are lowered WITHOUT the element expressions' obligations (the display / len is
      modelled by size, the assert test folds), so the operation's precondition is never asserted.
CPYTHON: f(0) -> ZeroDivisionError (own-claim forms) / 2 (callee-handler forms).
PROPOSED SYSTEMATIC REPAIR: refuse-by-default — every TRIGGERS-shaped sub-expression of a function body must either reach a
      lowering that asserts its obligation or be refused; walk the source AST for trigger shapes and check, per site, that the
      emitted VC carries it (or refuse with a named code); in particular evaluate display elements / len arguments / assert
      tests for their side conditions even when only their size or truth is modelled.
```
