# OPEN ROUTE #422 — LOCAL DERIVATION GAPS: three local forms with a known class are #UND, admitted 
**Status: OPEN, Severity 1.** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r422/` (3): `c27_str_split_unbound.py`, `c31_enum_value.py`, `c35_nested_def.py`.

```
#422 LOCAL DERIVATION GAPS: three local forms with a known class are #UND, admitted   [documented #UND residual]   (3)
  c27  k = str.split('a b')        c31  k = E.A.value (Enum member value [1])        c35  a NESTED def `-> list` called
  CPython TypeError. REPAIR: read `str.<method>(x, ..)` as the str method row, `<Enum member>.value` as the member's
  initializer class, and a nested def's `-> T` like a module function's.
```
