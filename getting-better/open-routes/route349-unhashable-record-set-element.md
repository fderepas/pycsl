# OPEN ROUTE #349 — A SET LITERAL / DICT KEY OF AN UNHASHABLE RECORD PROVES no_exception
**Status: OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r349/`: `e08_record_hash_dict.py`, `e09_dataclass_unhashable_set.py`.

`@dataclass` (eq=True implies `__hash__ = None`) or an explicit `__hash__ = None`; `s = {d}` under `no_exception` PROVES (emission `let s = ref (any int)`); CPython TypeError unhashable. (e10 dict key: Why3 mutable-type error; e11 raising `__hash__`: FAIL.)

Repair: Refuse unhashable records (eq-dataclass without frozen/unsafe_hash, explicit `__hash__ = None`, `__eq__` without `__hash__`) as set elements / dict keys / hash arguments.
