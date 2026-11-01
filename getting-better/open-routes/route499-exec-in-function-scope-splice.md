# OPEN ROUTE #499 — A CONSTANT `exec("...")` INSIDE A FUNCTION IS SPLICED AS IF ITS ASSIGNMENTS REBOUND THE FUNCTION's LOCALS: CPYTHON (PEP 667) RUNS IT AGAINST A SNAPSHOT OF locals(), SO `x = 1; exec("x = 2"); return x` RETURNS 1
**Status: OPEN, Severity 1.** Red-team round 44 (driver run #4, 2026-11-01, on 1c30f94b3 = main: 793 probes in g500-g527, 779 CPython-breaching, 139 confirmed (probe, mode) pairs on 111 probes in 5 families). Census `scratchpad/rt44/census.tsv`; the family block below is quoted from `scratchpad/rt44/FINDINGS.txt`.
Witnesses `witnesses-r499/` (11): `g507_s50719_exec_local.py`, `g517_e51700_assign_local.py`, `g517_e51701_assign_param.py`, `g517_e51702_augassign_local.py`, `g517_e51705_assign_from_param.py`, `g517_e51706_two_stmts.py`, `g517_e51707_multiline.py`, `g517_e51708_list_rebind.py`, `g517_e51709_str_local.py`, `g517_e51710_guard_then_div.py`, `g517_e51717_tuple_assign.py`.

Driver repro: session scratchpad `rp44/repro.sh` on 1217d2745 (main's code), 2026-11-01T02:20Z: all 12 rt44 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F4 A CONSTANT `exec("...")` INSIDE A FUNCTION IS SPLICED AS IF ITS ASSIGNMENTS REBOUND THE FUNCTION's LOCALS: CPYTHON (PEP 667) RUNS IT AGAINST A SNAPSHOT OF locals(), SO `x = 1; exec("x = 2"); return x` RETURNS 1 (11)
  EXEMPLAR: g517/e51700_assign_local.py: `#@ ensures \result == 2` f(n): `x = 1; exec("x = 2"); return x`
  CPYTHON: f(0) -> 1 (VIOLATION contract 1); e51710 (`d = 0; exec("d = 5"); return 10 // d` under no_exception \all) -> ZeroDivisionError
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt44 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt44/g517/e51700_assign_local.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt44/g517 && /home/fabrice/git/pycsl-rt44/.venv/bin/python3 -E -s e51700_assign_local.py)
  WHY: src/pycsl/frontend/exec_splice.py (`_ExecSplicer.visit_Expr`) replaces every constant exec expression-statement by its parsed body regardless of scope; the inline-equivalence it asserts holds only at module (and class-body) scope. REPAIR: splice only outside function bodies, or refuse a Name / AnnAssign / AugAssign / unpacking target inside a function.
  PROBES: g507/s50719_exec_local.py g517/e51700_assign_local.py g517/e51701_assign_param.py g517/e51702_augassign_local.py g517/e51705_assign_from_param.py g517/e51706_two_stmts.py g517/e51707_multiline.py g517/e51708_list_rebind.py g517/e51709_str_local.py g517/e51710_guard_then_div.py g517/e51717_tuple_assign.py
```
