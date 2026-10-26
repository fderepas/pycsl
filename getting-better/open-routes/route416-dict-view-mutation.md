# OPEN ROUTE #416 — MUTATING A DICT WHILE ITERATING A VIEW OF IT IS NOT REFUSED (direct `for k in d` IS)
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r416/`: `l18_dict_keys_view_mutate.py`, `n04_values_iter_mutate.py`, `n05_items_iter_mutate.py`.

```
#416 MUTATING A DICT WHILE ITERATING A VIEW OF IT IS NOT REFUSED (direct `for k in d` IS)  [old family]
  l18  for k in d.keys(): d[k + 100] = 0;  n04 for v in d.values(): ..;  n05 for k, v in d.items(): ..   RuntimeError
  (for k in d with d[..] = / del / setdefault / clear, and set add / discard, are refused: l01-l03, l23, l24, n06.)
  REPAIR: apply the same mutation-during-iteration refusal when the iterable is `.keys()` / `.values()` /
  `.items()` of the mutated dict.
```
