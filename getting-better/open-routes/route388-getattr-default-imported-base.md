# OPEN ROUTE #388 — `getattr(o, "k", d)` DEFAULTS DESPITE AN IMPORTED BASE HAVING `k`
**Status: OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r388/`: `g01_getattr_exception_args.py`, `g02_getattr_abc_impl.py`, `g05_getattr_namedtuple_count.py`.

Exception `args`, ABC `_abc_impl`, NamedTuple `count`: #376 residual 1 (outside bases not read), now a measured false proof. CPython `()` / an `_abc_data` / a method.

Repair: Refuse a non-dunder getattr default fold when the receiver's MRO has a base outside the file (allow-list `object`).
