# OPEN ROUTE #397 — GD's INSTANCE-ATTRIBUTE CENSUS SEES ONLY `self.k = v` / `self.k: T = v` STORES
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r397/`: `k60_subclass_for_target.py`, `g20_for_target_attr.py`, `g21_tuple_target_attr.py`, `k55_list_target.py`, `k56_with_target.py`, `k57_two_tuple_target.py`, `k65_dataclass_post_init_for.py`.

```
#397 GD's INSTANCE-ATTRIBUTE CENSUS SEES ONLY `self.k = v` / `self.k: T = v` STORES  [slips past GD §7.43]
  g20 `for self.k in range(5, 6)` in __init__;  g21 `(self.k,) = (5,)`;  k55 `[self.k] = [5]`;  k56 `with nullcontext(5) as self.k`;
  k57 `self.k, self.j = 5, 6` (getattr "j");  k65 `for self.k in [5]` in a dataclass __post_init__     CPython 5 / 6
  (The default is folded to 0; the model has no field k at all. k58 `a, *self.k = ..` and k59 for-target in another method
  were refused/ill-typed.)
  REPAIR: collect every Store-context `ast.Attribute` on `self` (and on any receiver) in every target position (for /
  async for / with / comprehension / tuple / list / starred / augmented / walrus-free) as a binding of that name; better,
  refuse a getattr default when any attribute store of that name in a non-simple target exists.
```
