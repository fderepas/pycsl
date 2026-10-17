# OPEN ROUTE #270 — #264's DEFINITE-ASSIGNMENT ANALYSIS MISSES EXCEPTION EDGES FROM CALLS (AND TREATS GENERATORS AS NO-RETURN)

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 4; driver-reproduced at HEAD eced7036 (rc=0; CPython
UnboundLocalError). Witnesses `witnesses-r270/`:
- a20: `if c: y = 2`; `try: C.g(1)` (declared `raises ValueError when x > 0`) `except ValueError: pass else: y = 1`;
  `return y` with `ensures \result >= 0` proves. The analysis (pycsl.py ~2524-3005) adds exception edges only from
  local read/write/nop ops; a call reading no local creates none, so the handler path is invisible.
- a25: `fail()` is a GENERATOR (`yield 1; raise ValueError`) — treated as never-returning by #264's no-return rule
  (body ends in raise, no return) although calling a generator only builds it.
Repair: every potentially-raising operation (calls, division, subscripts, attribute access...) inside a `try` adds
an exception edge carrying the pre-state; generator functions are never "no-return".
