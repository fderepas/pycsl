# OPEN ROUTE #358 — PROTOCOL OPERATIONS ON ERASED VALUES HAVE NO EXCEPTION CHECK
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r357 executor off 1a9cfa42 — see REPAIR). Was OPEN, Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r358/`: `r07_for_over_self.py`, `r11_self_missing_attr.py`, `r14_bool_len_negative.py`, `r19_join_self.py`, `r24_object_for.py`, `r25_object_attr.py`, `r32_any_attr.py`, `r46_not_self_len.py`, `r51_self_attr_eq.py`.

Under no_exception: `for z in self` / `for z in x` (`x: object`) go through `iter_length`/`iter_get` (r07, r24: TypeError); a missing `self.zz` or `x.foo` on `object` / `Any` is an opaque read (r11, r51, r25, r32: AttributeError); `if self` / `not self` lower to `self <> 0` and never call `__len__` (r14, r46: ValueError for `__len__ -> -1`); `"".join([self])` is not in R343's builtin list (r19: TypeError).

Repair: Extend R343's failing assertion beyond builtin names: iteration / comprehension over an erased value, loads of attributes not known as fields on an erased base, truth tests on an erased receiver (the `x: object` truth test already fails, r45), str/list methods with erased arguments.
