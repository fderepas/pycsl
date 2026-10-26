# OPEN ROUTE #405 — DYNAMIC SUBCLASSES ESCAPE THE CLOSED-WORLD CLOSURE OF #395 / #396 / route #277
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r405/`: `a18_type_subclass_main.py`, `f15_make_dataclass_hash.py`, `f16_type_subclass_eq_hetero.py`, `f13_type_subclass_getattr.py`, `f17_type_subclass_method_override.py`.

```
#405 DYNAMIC SUBCLASSES ESCAPE THE CLOSED-WORLD CLOSURE OF #395 / #396 / route #277  [slips past §7.50 / §7.53 / CLASS-EXACT default]
  a18  __main__: D = type("D", (B,), {"__hash__": None}); f(b: B) hashes {b} PROVED            TypeError
  f15  D = dataclasses.make_dataclass("D", [], bases=(B,)) (eq, not frozen)                     TypeError
  f16  type() subclass with __hash__ 0 and a raising __eq__; {b, c}                             ZeroDivisionError
  f13  getattr(r, "k", 0) == 0 with S = type("S", (R,), {"k": 5})                               5
  f17  `b.g()` ensures \result == 1 with type("D", (B,), {"g": lambda s: 2}) -- the override refinement check
       (route #277, default ON) never sees the dynamic override                                 2
  (A `class D(B)` statement in __main__ (a19), in a def (a20), types.new_class (f14) and exec (n03) ARE refused.)
  REPAIR: any call of `type` with 3 arguments, `types.new_class`, `dataclasses.make_dataclass(.., bases=..)` or
  `collections.namedtuple`-like factories anywhere in the file (driver included) whose bases argument is not a
  literal tuple of modelled classes makes every file class named in it OPEN: unhashable at hashing sites,
  UNKNOWN for GD, and its method calls unverifiable (or simply refuse the 3-argument `type` call).
```
