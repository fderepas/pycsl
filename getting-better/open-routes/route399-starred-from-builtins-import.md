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

## REPAIR (2026-10-26, e2 executor off 3b2d2e763; code + corpus + docs ffec1ac18 and follow-ups on this branch; inline in `_run_pipeline`, mirror twin `\trusted`, no new def, no emission change, ledger unchanged)
**Design: the callee is resolved through the imports before SB's builtin test.** A name bound by `from builtins import X [as Y]`,
an attribute of a name bound by `import builtins [as b]`, and `__builtins__.X` (not rebound) are builtins for SB
(`PYCSL-R379-STARRED-CALL-ARGUMENT`). Witnesses 5644 (s18), 5645 (v67) PROVED at 3b2d2e763 -> REFUSED; control 5683 (explicit
arguments) PROVED both. (`b.sum(.., **..)` via `import builtins as b` was ill-typed at base and is now refused too.) Docs annotations
§7.55, translational §T.6.66.
Over-refusal measured (emission sweeps vs a worktree at 3b2d2e763, logs `getting-better/repair-r393-400/gates/`): root corpus 2424 -> 2431 .mlw (7 new controls), 0 MOVED / 0 GONE / 0 APPEARED; python-reference 2186 -> 2186, 0 / 0 / 0; mirror 53 / 53, 0 / 0 / 0 (no OWED proof). The FIRST cut over-refused 3 files, each removed by a justified refinement: mirror `frontend/pure_ast` (`class PyCSLSyntaxError(SyntaxError)` raised `(msg, (file, line, col, text))`: the SyntaxError family is now MODELLED by its constructor shape instead of refused) and corpus 0889 / 0890 (a CONTRACT's `r.n` on a TypedDict is the spec notation for a required key, not a runtime attribute read).
