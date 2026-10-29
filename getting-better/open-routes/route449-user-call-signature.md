# OPEN ROUTE #449 — USER-FUNCTION call signature not checked: extra positional / unknown or duplicate keyword silently dropped (TypeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r449/` (17): `c12_u000_fncall.py`, `c12_u001_fncall.py`, `c12_u002_fncall.py`, `c12_u003_fncall.py`, `c12_u010_fncall.py`, `c12_u011_fncall.py`, `c12_u013_fncall.py`, `c12_u021_nested_arity.py`, `c12_u024_realistic_arity.py`, `c12_u025_realistic_kw.py`, `c12_u026_static_through_class.py`, `c26_g000_star_formal_kw.py`, `c26_g003_default_then_extra_kw.py`, `c26_g004_extra_pos_ensures.py`, `c5_g000.py`, `c5_g002.py`, `c5_g003.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F6 -- USER-FUNCTION call signature not checked: extra positional / unknown or duplicate keyword silently dropped (TypeError)   (17)
  EXEMPLAR c12/u024_realistic_arity.py  PROVED (rc=0 Verification SUCCESS):
    | def parse(path: str, mode: int) -> int:
    |     return len(path) + mode
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(path: str, mode: int) -> int:
    |     return parse(path, mode, True)
    CPython 3.14: f('x', 1)  ->  VIOLATION TypeError parse() takes 2 positional arguments but 3 were given
  MECHANISM: A call to a FILE function binds arguments to formals by position / name and silently DROPS the rest:
  `parse(path, mode, True)` -> `(parse path mode)`; `total(items, start=1)` -> `(total items 0)` (the unknown
  keyword is dropped and the default used); `g(1, 2, b=3)` (duplicate b), nested defs, later-defined module
  functions, `C.s(1, 2)` staticmethod. Constructors (#369), methods called on instances, keyword-only /
  positional-only violations (#232) and a MISSING argument (c5 g001 / g004) are already
  refused -- the gap is SURPLUS arguments to plain functions / staticmethods (also with a `*args` formal and an
  unknown keyword, c26/g000).
  REPAIR: OBLIGATION (static): apply CPython's argument-binding algorithm to every call of a resolved file function
  (positional count <= #positional formals unless *args, every keyword names a formal unless **kwargs, no formal
  bound twice, every formal without default bound); refuse (TypeError) otherwise. Reuse #369's constructor check,
  which already does this for __init__.
  MEMBERS: c12/u000_fncall.py c12/u001_fncall.py c12/u002_fncall.py c12/u003_fncall.py c12/u010_fncall.py c12/u011_fncall.py c12/u013_fncall.py c12/u021_nested_arity.py c12/u024_realistic_arity.py c12/u025_realistic_kw.py c12/u026_static_through_class.py c26/g000_star_formal_kw.py c26/g003_default_then_extra_kw.py c26/g004_extra_pos_ensures.py c5/g000.py c5/g002.py c5/g003.py
```
