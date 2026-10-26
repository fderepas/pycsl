# OPEN ROUTE #395 — THE HASH CHECK READS THE STATIC CLASS ONLY: AN UNHASHABLE SUBCLASS INSTANCE AT A BASE-TYPED HASHING SITE
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r395/`: `c112_field_base_sub_dataclass.py`, `c113_field_base_sub_eqonly.py`, `c114_field_base_sub_hashnone.py`, `c116_field_base_sub_hashraise_cond.py`.

```
#395 THE HASH CHECK READS THE STATIC CLASS ONLY: AN UNHASHABLE SUBCLASS INSTANCE AT A BASE-TYPED HASHING SITE  [#349 family; S1 shape]
  c112 b: B (hashable, has a field), main passes @dataclass D(B)       {b} no_exception PROVED   CPython TypeError
  c113 D(B) with __eq__ only                                                                   TypeError
  c114 D(B) with __hash__ = None                                                               TypeError
  c116 D(B).__hash__ raises ValueError (conditional, to pass the vacuity gate)                 ValueError
  (D is constructed only in __main__; constructing it in verified code ill-types the call, c101-c103. The same filter
  "class named only by __main__" is S1's reference filter, measured harmless for field-less bases a49-a51 only because the
  base lowers to `int` and the goal is unprovable.)
  REPAIR: a class is hashable at a site only if it AND every file subclass is hashable with a verified no_exception
  __hash__ (any descendant with __hash__ None / eq-without-hash / a raising __hash__ makes the base unhashable at
  hashing sites), or require `@final` on the base.
```
