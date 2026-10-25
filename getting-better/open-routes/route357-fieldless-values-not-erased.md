# OPEN ROUTE #357 — VALUES OF A FIELD-LESS CLASS OTHER THAN `self` / PARAMETERS ARE NOT ERASED
**Status: OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r357/`: `r01_self_method_returns_self.py`, `r15_type_self_call.py`, `r22_dunder_class_ctor.py`, `r38_self_me_lt_noexc.py`, `r40_self_me_eq.py`, `r41_self_me_into_int.py`, `r50_type_self_ctor_args.py`.

Route #343 erases parameters and the receiver only. `s = self.me()` (`-> "W"`) keeps int laws (r01 `s - s == 0`, r40 `s == s`, r38 `s < s`, r41 into an `int` param); `type(self)()` / `self.__class__()` are emitted `any int` (r15, r22; r50 ignores a required `__init__` arg). CPython 1 / False / TypeError.

Repair: Erase every expression whose static type is a field-less class: method / callee results annotated with it (string annotations included), `type(e)()`, `e.__class__()`; refuse `type(e)(..)` construction when the constructor cannot be checked.
