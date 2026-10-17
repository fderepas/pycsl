# OPEN ROUTE #259 — `**` IS ALWAYS AN INT; `pow(x, e, 0)` HAS NO EXCEPTION OBLIGATION

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 2; driver-reproduced at HEAD e152fa15 (rc=0 both).
- `witnesses-r259/F1_pow_negexp_int.py`: `requires n < 0`; `x = 2 ** n; return x % 1 == 0`; `ensures \result == True`
  PROVES (CPython: `2 ** -1 == 0.5`, result False). `**` lowers to `val function py_pow (x: int) (y: int) : int`.
- `witnesses-r259/F2_pow_mod_zero.py`: `#@ no_exception \all` over `pow(x, 2, m)` PROVES (CPython ValueError for
  m == 0). The route #160 guard (functions.py ~857) checks only the exponent.
Repair: int `**` only when the exponent is provably `>= 0` (otherwise float/opaque or an obligation); 3-arg `pow`
under no_exception requires `m != 0` (and the negative-exponent/modular-inverse case).
