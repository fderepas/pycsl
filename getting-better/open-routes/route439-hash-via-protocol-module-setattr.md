# OPEN ROUTE #439 — A HASHED VALUE WHOSE CLASS COMES THROUGH A Protocol, A FOREIGN USER MODULE, OR setattr OWES NO TypeError
**Status: OPEN, Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r439/` (5): `pp08_protocol.py`, `pp11_callable_obj.py`, `j5_usermod_callee.py`, `j6_usermod_from.py`, `s0_setattr_dyn_name.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#439 A HASHED VALUE WHOSE CLASS COMES THROUGH A Protocol, A FOREIGN USER MODULE, OR setattr OWES NO TypeError   (5)
  pp08 c: Pr (a Protocol with __len__); {c} PROVED; f([1])                                       CPython TypeError
  pp11 a Protocol with __call__ satisfied by an unhashable class   j5 / j6 an imported user-module function hashes its argument
  (import m / from m import h)   s0 setattr(o, name, [1]) then {o.k}
  REPAIR (proposed, allow-list / refuse by default): A Protocol-typed value is #UNK for hashing (structural typing admits list/dict/set); a call into an imported user module is
  treated as the R-gate treats an un-claimed callee (§7.47 / route #430), its exceptions reaching the caller; a field
  written by setattr with a non-literal name is #UNK.
```
