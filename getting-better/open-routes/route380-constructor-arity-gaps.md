# OPEN ROUTE #380 — CONSTRUCTOR ARITY GAPS: `init=False`, `super().__init__(..)`, METACLASS `__call__`
**Status: OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r380/`: `b14_dc_init_false_call.py`, `b20_super_init_kw.py`, `b29_metaclass_call_value.py`, `b31_init_false_explicit_init.py`.

`@dataclass(init=False)` called `D(1)` lowers to `{ x = 4 }` (b14, b31 with an explicit `__init__` too... CPython TypeError: takes no arguments); `super().__init__(y=1)` against `__init__(self, x)` (b20, TypeError); a metaclass `__call__` returning 42 while `C(1).x == 1` proves (b29, AttributeError).

Repair: `init=False` = `object.__init__` for arity; arity-check `super().__init__` / `C.__init__(self, ..)` against the next MRO class; refuse construction when a metaclass defines `__call__`.
