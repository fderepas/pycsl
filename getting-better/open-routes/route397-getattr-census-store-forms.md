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

## REPAIR (2026-10-26, e2 executor off 3b2d2e763; code + corpus + docs ffec1ac18 and follow-ups on this branch; inline in `_run_pipeline`, mirror twin `\trusted`, no new def, no emission change, ledger unchanged)
**Design: every Store / Del-context `Attribute` binds, in any target position, on any receiver.** Inside each method of a class,
an attribute store or delete whose receiver is the method's own first parameter (not a `@staticmethod`, never rebound or shadowed
there) binds the name on that class; any other attribute store -- another receiver, a module function, module code, class-scope
code (the `__main__` driver excluded) -- binds the name for EVERY class. `exec` / `eval` join GD's dynamic stores. Witnesses
5633-5638 (g20, g21, k55, k56, k57, k65; k60 is 5629) PROVED at 3b2d2e763 -> REFUSED; control 5681. (A module-function `for o.k in
..` store was already refused at base by route #301 -- no witness.) Docs annotations §7.53, translational §T.6.64.
Over-refusal measured (emission sweeps vs a worktree at 3b2d2e763, logs `getting-better/repair-r393-400/gates/`): root corpus 2424 -> 2431 .mlw (7 new controls), 0 MOVED / 0 GONE / 0 APPEARED; python-reference 2186 -> 2186, 0 / 0 / 0; mirror 53 / 53, 0 / 0 / 0 (no OWED proof). The FIRST cut over-refused 3 files, each removed by a justified refinement: mirror `frontend/pure_ast` (`class PyCSLSyntaxError(SyntaxError)` raised `(msg, (file, line, col, text))`: the SyntaxError family is now MODELLED by its constructor shape instead of refused) and corpus 0889 / 0890 (a CONTRACT's `r.n` on a TypedDict is the spec notation for a required key, not a runtime attribute read).
