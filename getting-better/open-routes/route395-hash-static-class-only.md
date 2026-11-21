# OPEN ROUTE #395 — THE HASH CHECK READS THE STATIC CLASS ONLY: AN UNHASHABLE SUBCLASS INSTANCE AT A BASE-TYPED HASHING SITE
**Status: REPAIRED, candidate (gen #37, 2026-10-26; e1 executor off 3b2d2e763 -- sound refusal, see REPAIR; repaired with routes #392 / #394 / #395). Was OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
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

## REPAIR (2026-10-26, e1 executor off 3b2d2e763, with routes #392 / #394 / #395; code + corpus + census + docs in commit 3445dc472; docs annotations §7.50 / translational §T.6.61)
**Design: a closed-world step in the §7.33 unhashability fixpoint (inline, mirror twin `\trusted`, no emission change).** A file class B is unhashable when a proper file subclass is unhashable, or defines its own `def __hash__` whose IR function is not a verified (`\trusted` / `\abstract`-free) `no_exception \all` method; the step runs inside the fixpoint, so frozen records with a field of such a base are unhashable too. Message of `PYCSL-R349-UNHASHABLE-RECORD` extended (route #395).
Residual (measured, not landed): requiring a verified `__hash__` on the STATIC class itself (a raising own `__hash__` still PROVES `{d}`, probe `p1_own_hash_raise`) refuses PASS controls 4694 / 4940 / 5043 (their `__hash__` has no contract); a raising `__eq__` on a hash collision is not modelled.
Witnesses c112 5577, c113 5578, c114 5579, c116 5580. Control 5592.
Gates (candidate vs base worktree at 3b2d2e763): root byte-diff 2423 -> 2426 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (+3 controls); pyref 2186 -> 2186, 0/0/0; mirror 53/53 0/0/0 (no OWED proof); `pycsl_lib` --no-proof screen identical (104 files). Every witness PROVED at base (rc=0) and is REFUSED on the candidate (rc=1); controls 5590-5592 PROVED at base and candidate. Census rows written with `_census_row` (31 new; the 90 `is HASHED by` rows re-measured: message extended, prefix identical).
