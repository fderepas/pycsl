# OPEN ROUTE #500 — ir_inline (METHOD CALLS ON A MODULE-GLOBAL INSTANCE ARE SPLICED): A `return` NESTED IN A BRANCH OF THE METHOD PASSES THE TAIL-RETURN CHECK (IT INSPECTS ONLY TOP-LEVEL STATEMENTS) AND, ONCE SPLICED, RETURNS FROM THE CALLER
**Status: OPEN, Severity 1.** Red-team round 44 (driver run #4, 2026-11-01, on 1c30f94b3 = main: 793 probes in g500-g527, 779 CPython-breaching, 139 confirmed (probe, mode) pairs on 111 probes in 5 families). Census `scratchpad/rt44/census.tsv`; the family block below is quoted from `scratchpad/rt44/FINDINGS.txt`.
Witnesses `witnesses-r500/` (6): `g520_g52000_nested_if_return.py`, `g520_g52001_nested_if_return_stmt.py`, `g526_r52604_field_write_skipped.py`, `g526_r52606_param_dependent.py`, `g526_r52608_nested_two_levels.py`, `g526_r52609_method_calls_method.py`.

Driver repro: session scratchpad `rp44/repro.sh` on 1217d2745 (main's code), 2026-11-01T02:20Z: all 12 rt44 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F5 ir_inline (METHOD CALLS ON A MODULE-GLOBAL INSTANCE ARE SPLICED): A `return` NESTED IN A BRANCH OF THE METHOD PASSES THE TAIL-RETURN CHECK (IT INSPECTS ONLY TOP-LEVEL STATEMENTS) AND, ONCE SPLICED, RETURNS FROM THE CALLER (6)
  EXEMPLAR: g520/g52000_nested_if_return.py: `g = C()`; `C.m(n)`: `if n > 0: return 1` / `return 2`; `#@ ensures \result == 1` f: `r = g.m(5); return r + 10`
  CPYTHON: f(0) -> 11 (VIOLATION contract 11)
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt44 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt44/g520/g52000_nested_if_return.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt44/g520 && /home/fabrice/git/pycsl-rt44/.venv/bin/python3 -E -s g52000_nested_if_return.py)
  WHY: src/pycsl/frontend/ir_inline.py `_expand` (the `for st in body[:-1]` check, ~line 290) refuses only a TOP-LEVEL non-tail Return; a Return inside an If (or loop / match) is spliced into the caller as a caller return. REPAIR: walk the whole body for Return nodes (any depth) before splicing.
  PROBES: g520/g52000_nested_if_return.py g520/g52001_nested_if_return_stmt.py g526/r52604_field_write_skipped.py g526/r52606_param_dependent.py g526/r52608_nested_two_levels.py g526/r52609_method_calls_method.py
```
