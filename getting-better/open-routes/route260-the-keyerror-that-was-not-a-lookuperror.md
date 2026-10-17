# OPEN ROUTE #260 — `except LookupError` DOES NOT CATCH A RAISED `KeyError`

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 2; driver-reproduced at HEAD e152fa15 (rc=0).
`witnesses-r260/F3_keyerror_lookup.py`: `try: raise KeyError("k") / except LookupError: r = 7 / return r`,
`ensures \result == 0` PROVES vacuously (CPython 7). Emission `try raise KeyError with LookupError -> ... end`;
KeyError and LookupError are distinct Why3 exceptions and an undeclared `raises { KeyError }` makes the normal
path unreachable. Routes #174/#175 refuse broad/user classes but not builtin subclass pairs.
Repair: an `except C` must catch every modelled builtin subclass of C (KeyError/IndexError -> LookupError,
ZeroDivisionError -> ArithmeticError, ...) or be refused; an exception escaping a function that does not declare
it must not make the postcondition vacuous (it must be reported/refused).

## Repair (gen #36, 2026-10-17)
1. `exception_model.EXCEPTION_BASES` (data only; `bases_closure`/`handler_catches` unchanged) now lists
   EVERY CPython builtin exception class with all its proper ancestors (3.14 `__mro__` minus `object`),
   not only the OSError family. Handler expansion (`stmt_control_flow._handle_try_stmt`), the escaping
   set (`IRScanner.collect_escaping_exceptions`, `_callee_raised_in`), `#@ raises` summarisation and
   route #176's callee-raise all go through `handler_catches`, so `except LookupError` gets a `KeyError`
   arm, `except Exception` / `BaseException` catch every raised builtin. Mirror twin re-ported verbatim.
2. The silent `raises` addition (partial correctness for undeclared exceptions is the documented trust
   boundary, §T.10.3) is kept, but the non-vacuity gate no longer passes a function with NO surfaced
   normal-exit goal when its spec carries an unconditioned (undeclared, emitter-added) `raises { E }`
   arm: every normal exit is dead and the postcondition is discharged by the model's raise alone, so it
   is reported VACUOUS (`-> NoReturn` stays exempt; a declared `#@ raises` is not touched). This catches
   the witness shape independently of (1) (measured: hierarchy reverted, gate alone fails F3).
Witnesses: 2730 (F3, PROVED -> FAIL), 2733 (always-raising undeclared, PROVED -> VACUOUS); controls 2731
(IndexError under LookupError, true claim; now proved through the arm), 2732 (exact handler), 2734
(reachable undeclared raise keeps PASS). Corpus root/pyref: 0 movers from this half; mirror 0 movers.
Vacuity-rider census (functions with an undeclared arm and zero normal-exit goals): corpus 5 — 0738/0741
`-> NoReturn` (exempt, PASS kept), 2479/2480/1301 expected-FAIL (FAIL kept); pyref 0; stdlib 0; mirror 14
measured candidates all have goals, 15 in the big files inspected (live `Return` arms) — measurement OWED.
