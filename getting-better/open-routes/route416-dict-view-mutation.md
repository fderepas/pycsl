# OPEN ROUTE #416 — MUTATING A DICT WHILE ITERATING A VIEW OF IT IS NOT REFUSED (direct `for k in d` IS)
**Status: REPAIRED (candidate, g2 run #3), Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r416/`: `l18_dict_keys_view_mutate.py`, `n04_values_iter_mutate.py`, `n05_items_iter_mutate.py`.

```
#416 MUTATING A DICT WHILE ITERATING A VIEW OF IT IS NOT REFUSED (direct `for k in d` IS)  [old family]
  l18  for k in d.keys(): d[k + 100] = 0;  n04 for v in d.values(): ..;  n05 for k, v in d.items(): ..   RuntimeError
  (for k in d with d[..] = / del / setdefault / clear, and set add / discard, are refused: l01-l03, l23, l24, n06.)
  REPAIR: apply the same mutation-during-iteration refusal when the iterable is `.keys()` / `.values()` /
  `.items()` of the mutated dict.
```

## REPAIR (2026-10-26, g2 executor off 4431ef86f; docs annotations §7.74 / translational §T.6.85)
**The UB-7.1 refusal extended to views.** A `for` whose iterable is `<r>.keys()` / `<r>.values()` / `<r>.items()` counts as
iterating `<r>`: the same `_collect_mutations` census and the same `#@ allow_iteration_mutation` opt-out, refused with the
existing UB-7.1 message (no new message). Implemented INLINE in `_run_pipeline` (mirror twin `\trusted`), not in
`IRScanner.find_iteration_mutations`: a first version there kept the mirror source verbatim and the mirror emission
byte-identical -- because that method's mirror model is a recognised FIXED-SHAPE lowering (`generic_fold.
recognize_find_iteration_mutations`, a tag-subset gate) of the `Var` case only, so the verified mirror would silently have
stopped describing the live body. Measured, then moved.
Measured together on the final candidate (g2 worktree off 4431ef86f; base = the official `bin/byte-diff-sweep.sh` at 4431ef86f
from the clean g1-base tree, cwd = tree root; candidate the same script from the g2 tree): root 2441 -> 2455 .mlw, 2 MOVED
(`1163`, `1164`: #414's shift obligation), 1 GONE (`3269`, #415), 0 APPEARED, 15 new emitting sources (the 20 new witnesses /
controls minus the 5 refused); pyref 2186 -> 2186, 1 MOVED (`0110`: #412's `no_div_zero (0)` inside a `try/except
ZeroDivisionError`, exactly the assert `//` already gets there), 0 GONE, 0 APPEARED; mirrors 53/53, 0 MOVED / 0 GONE / 0
APPEARED. M1 re-proofs base -> candidate: `1163` FAIL -> FAIL (expected FAIL), `1164` PROVED -> PROVED, `3269` FAIL -> REFUSED
(expected FAIL), pyref `0110` FAIL -> FAIL (a pre-existing real/int type error at both).
Movers of this route alone: none (no corpus, pyref, mirror or `pycsl_lib` file iterates a view while mutating it).
Witnesses PROVED rc=0 at base -> REFUSED rc=1 (UB-7.1): 6073 (l18), 6074 (n04), 6075 (n05). Control 6076 (the three views
iterated while a DIFFERENT dict is written): PROVED at base and candidate.
Residual: a view bound to a name first (`ks = d.keys(); for k in ks: d[..] = ..`) and `self.d.keys()` with a field write
(`self.d[k] = ..` is not a `Var` store) are not matched by the detector (not measured whether they prove) -- the same blind spots as the direct `for k in d` form.
