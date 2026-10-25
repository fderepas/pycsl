# OPEN ROUTE #373 — A NESTED `def` IN A METHOD IS LOWERED AS AN OPAQUE `val g_0 () : int`
**Status: OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r373/`: `e04_nested_def_sub.py`, `e32_nested_def_default_self.py`, `e37_nested_def_noann.py`, `e63_nested_def_ne.py`, `e64_nested_def_mul.py`, `e79_nd_self_unannotated_eq.py`, `e83_nd_str_mul0.py`, `e84_nd_list_mul0.py`.

A nested def closing over `self` (field-less class) is lowered at the call site to an abstract int, so `t - t == 0`, `t == t`, `t * 0 == 0` prove; R325 catches float / `W()` bodies only. Slips past #357/R325/R252. CPython AssertionError (1, 0, -1).

Repair: Apply the any_ret / R325 erasure to calls of lifted nested defs, or refuse the opaque `val` stand-in.
