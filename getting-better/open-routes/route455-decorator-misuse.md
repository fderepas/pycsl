# OPEN ROUTE #455 — builtin DECORATOR misuse not modelled: `@property` / `@typing.overload` on a module or nested function, then called (TypeError / NotImplementedError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r455/` (6): `c18_k009_deco_property_module.py`, `c21_d000_overload_no_impl.py`, `c21_d001_typing_overload_dot.py`, `c21_d002_property_nested.py`, `c21_d004_property_realistic.py`, `c21_d008_property_ensures.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F12 -- builtin DECORATOR misuse not modelled: `@property` / `@typing.overload` on a module or nested function, then called (TypeError / NotImplementedError)   (6)
  EXEMPLAR c21/d004_property_realistic.py  PROVED (rc=0 Verification SUCCESS):
    | @property
    | def size(p: str) -> int:
    |     return len(p)
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(path: str) -> int:
    |     return size(path)
    CPython 3.14: f('ab')  ->  VIOLATION TypeError 'property' object is not callable
  MECHANISM: A builtin DECORATOR on a module-level or nested function is ignored: `@property def size(p)` lowers to a
  plain `let size` that `f` calls (mlw/d004), but CPython binds `size` to a property object (not callable);
  `@typing.overload` without an implementation lowers to the stub's body (mlw/d000), while CPython's overload
  stub raises NotImplementedError. Every other decorator tried at module level is refused (user decorators,
  classmethod, functools.cached_property / lru_cache, typing.final / no_type_check, abc.abstractmethod: c18 / c21),
  so property and overload are presumably admitted as known (class-body) decorators regardless of the site.
  REPAIR: ALLOW-LIST of decorators PER DEFINITION SITE: property (and setter / deleter) only on a method in a class body,
  never at module or nested-function level; a call of a name whose only definitions are @overload stubs (no
  undecorated implementation) is refused (NotImplementedError); everything else stays refused as today.
  MEMBERS: c18/k009_deco_property_module.py c21/d000_overload_no_impl.py c21/d001_typing_overload_dot.py c21/d002_property_nested.py c21/d004_property_realistic.py c21/d008_property_ensures.py
```
