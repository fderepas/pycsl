# OPEN ROUTE #444 — unbound NAME lowered as an opaque constant (NameError: comprehension-variable leak, undefined / misspelt / later-defined global)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r444/` (9): `c1_o150_comp_var_leak.py`, `c1_o170_global_unbound.py`, `c11_q021_realistic_typo.py`, `c4_n000_gen_var_leak.py`, `c4_n004_nested_comp_leak.py`, `c4_n007_undef_in_cond.py`, `c4_n009_global_defined_later.py`, `c4_n018_undef_default.py`, `c4_n019_typo_param.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F1 -- unbound NAME lowered as an opaque constant (NameError: comprehension-variable leak, undefined / misspelt / later-defined global)   (9)
  EXEMPLAR c11/q021_realistic_typo.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(items: List[int]) -> int:
    |     total = 0
    |     for it in items:
    |         total += it
    |     return totl
    CPython 3.14: f([1])  ->  VIOLATION NameError name 'totl' is not defined
  MECHANISM: A Name load with no binding in any scope (local, parameter, global, builtin, import) is emitted as a fresh
  `val constant <name> : int` (the final fallback of the Name lowering, src/pycsl/module6_whyml/expressions.py:18939-18941;
  mlw/o170: `(a + uNDEF_G)`; mlw/o150: the comprehension target `x` read after
  `[x for x in xs]` becomes `val constant x`). Nothing is owed, so NameError-freedom 'proves'. Also: a name
  bound only AFTER the def at module level that is never assigned (n009 `LATE`), a misspelt parameter (n019).
  REPAIR: ALLOW-LIST of bindings: under a no_exception claim, every Name load must resolve to a parameter, a local
  definitely assigned on every path (route #264's analysis already exists for UnboundLocalError), a module-level
  binding executed before the call (def / class / import / top-level assignment), or a builtin of the real builtins
  module; comprehension / generator targets are scoped to their comprehension. Otherwise refuse
  (PYCSL-R-UNBOUND-NAME, NameError). Never emit a `val constant` for an unresolved name.
  MEMBERS: c1/o150_comp_var_leak.py c1/o170_global_unbound.py c11/q021_realistic_typo.py c4/n000_gen_var_leak.py c4/n004_nested_comp_leak.py c4/n007_undef_in_cond.py c4/n009_global_defined_later.py c4/n018_undef_default.py c4/n019_typo_param.py
```
