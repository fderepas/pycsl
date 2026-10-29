# OPEN ROUTE #450 — `super().m(..)` lowered as opaque `m_k (super_0 ())`: base lacks m / arity mismatch (AttributeError / TypeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r450/` (6): `c11_q092_super_arg_class.py`, `c3_b080_super_missing.py`, `c5_s000_super_missing_arg.py`, `c5_s003_super_self_only.py`, `c5_s006_super_field.py`, `c5_s008_super_two_level.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F7 -- `super().m(..)` lowered as opaque `m_k (super_0 ())`: base lacks m / arity mismatch (AttributeError / TypeError)   (6)
  EXEMPLAR c3/b080_super_missing.py  PROVED (rc=0 Verification SUCCESS):
    | class B:
    |     def h(self) -> int:
    |         return 1
    | 
    | 
    | class Q(B):
    |     def g(self) -> int:
    |         return super().m()
    | 
    | 
    | #@ no_exception \all
    | def f(p: Q) -> int:
    |     return p.g()
    CPython 3.14: f(Q())  ->  VIOLATION AttributeError 'super' object has no attribute 'm'
  MECHANISM: `super().m(..)` lowers to `(m_1 (super_0 ()))` with both `val`s opaque and raise-free (mlw/b080); nothing checks
  that a base class in the MRO defines m, nor m's arity (s000 `super().h(1)` vs `def h(self)`), nor fields read as
  `super().v` (instance fields are not visible through super).
  REPAIR: Resolve `super()` statically to the next class in the file MRO after the enclosing class; `super().m(..)` is
  admitted only when that MRO slice defines METHOD m (not an instance field) and the call matches its signature
  (F6's binding check); it then lowers to a direct call of that base method, so its contract speaks. A builtin base
  goes through #440's (class, method) table (s004 / s009 are already refused by #393). Else refuse.
  MEMBERS: c11/q092_super_arg_class.py c3/b080_super_missing.py c5/s000_super_missing_arg.py c5/s003_super_self_only.py c5/s006_super_field.py c5/s008_super_two_level.py
```
