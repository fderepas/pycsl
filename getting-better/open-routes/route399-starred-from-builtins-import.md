# OPEN ROUTE #399 — SB IS BYPASSED BY `from builtins import X`: THE NAME COUNTS AS "IMPORTED" BUT STILL LOWERS TO THE BUILTIN MODEL
**Status: OPEN, Severity 1.** Red-team round 31 (2026-10-26, probes around systematic rules S1/GD/TC/SB and the §7.46/§7.47 hash rules); driver-reproduced on 7859e8fb0 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt31/driver-repro.txt`).
Witnesses `witnesses-r399/`: `s18_from_builtins_sorted.py`, `v67_from_builtins_sum.py`.

```
#399 SB IS BYPASSED BY `from builtins import X`: THE NAME COUNTS AS "IMPORTED" BUT STILL LOWERS TO THE BUILTIN MODEL  [slips past SB §7.45]
  s18  from builtins import sorted; sorted(xs, **{"reverse": True}) proved ascending              CPython [2, 1]
  v67  from builtins import sum; sum([1, 2], **{"start": 10}) == 3 proved                         CPython 13
  (v68 `sorted as srt`, v75 `int as I` are refused by the shadowing rule; `*` forms v69-v76 are ill-typed in WhyML.)
  REPAIR: resolve `from builtins import X [as Y]` and `builtins.X` to the builtin X before the SB test; SB then refuses.
```
