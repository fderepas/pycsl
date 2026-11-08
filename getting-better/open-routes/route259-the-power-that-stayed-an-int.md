# OPEN ROUTE #259 — `**` IS ALWAYS AN INT; `pow(x, e, 0)` HAS NO EXCEPTION OBLIGATION

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 2; driver-reproduced at HEAD e152fa15 (rc=0 both).
- `witnesses-r259/F1_pow_negexp_int.py`: `requires n < 0`; `x = 2 ** n; return x % 1 == 0`; `ensures \result == True`
  PROVES (CPython: `2 ** -1 == 0.5`, result False). `**` lowers to `val function py_pow (x: int) (y: int) : int`.
- `witnesses-r259/F2_pow_mod_zero.py`: `#@ no_exception \all` over `pow(x, 2, m)` PROVES (CPython ValueError for
  m == 0). The route #160 guard (functions.py ~857) checks only the exponent.
Repair: int `**` only when the exponent is provably `>= 0` (otherwise float/opaque or an obligation); 3-arg `pow`
under no_exception requires `m != 0` (and the negative-exponent/modular-inverse case).

## REPAIR (2026-10-17, branch r259 off b35d9c5e)
Rules (inline, no new defs, ledger 3 -- no new axiom; every edited method has a `\trusted` mirror twin):
- `**` (expression site `_emit_bitwise_or_power` AND the `x **= n` twin in `_handle_augassign_stmt`, ONE shared
  decl): `val function py_pow (x: int) (y: int) : int requires { [@expl:int ** needs a non-negative exponent
  (route 259)] y >= 0 }` -- an OBLIGATION at every program call, never an assumption. A negative LITERAL exponent is
  no longer constant-folded (the fold produced the real `0.5` in an int slot). Contracts cannot spell `**` (the
  contract grammar has no power operator), so no logic-side use escapes the obligation.
- builtin `pow(b, e)` (generic unannotated-call arm, `_handle_call_expr`): `val pow_2 ... requires { x1 >= 0 }`;
  a `pow` call with KEYWORDS (dropped by that arm: `pow(2, exp=n)` became `pow_1 2`) owes `requires { false }`.
- route #160's `no_exception` guard (`_reset_function_state`): `pow`'s keywords are folded into their positions
  (`base`/`exp`/`mod`), and a 3-argument `pow` is REFUSED under `no_exception \all`/`ValueError` unless the
  modulus is a NONZERO literal (`pow(x, -1, m)`, the modular inverse, was already refused by the exponent check).
- `math.pow` (opaque external), `float ** int` (L3-tc type error), `0 ** -1` (row + obligation) all fail closed.

Witnesses (all PROVED at b35d9c5e, CPython disagrees; all FAIL after on the named goal/refusal, no type error):
2700 `2 ** n`, 2701 `pow(x, 2, m)` no_exception, 2702 `pow(2, n)`, 2703 `2 ** -1`, 2704 `x **= n`,
2705 `pow(x, 2, mod=0)` no_exception, 2706 `pow(2, exp=n)`. Controls keep PASS: 2707 `2 ** 3 == 8`,
2708 `x ** n` under `n >= 0` (+ `x ** 2`), 2709 `pow(x, 2, 7)` no_exception.
Blast radius: corpus 1 mover (1162, the decl gains its `requires` line; expected FAIL, still FAIL); pyref 0;
mirror 0 (no `**`/`pow` in the mirror). Gates in the #262 section below (one landing).
