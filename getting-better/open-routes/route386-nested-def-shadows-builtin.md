# OPEN ROUTE #386 — A DEF NESTED IN A METHOD NAMED LIKE A BUILTIN STILL LOWERS TO THE BUILTIN
**Status: OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r386/`: `d03_nested_def_shadows_builtin_len.py`, `d13_nested_def_shadows_max_in_method.py`, `d21_nested_def_shadows_min_in_method.py`.

`def len(..)` / `max` / `min` nested in a method: the bare call lowers to the builtin model (e.g. `MinMax.max`); #373's rule fires only for unresolved calls. CPython 0 / -100 / 100 against the ensures.

Repair: A bare call whose name is bound locally in the enclosing scope (nested def, import, loop / with / except target) never resolves to a builtin or library model.
