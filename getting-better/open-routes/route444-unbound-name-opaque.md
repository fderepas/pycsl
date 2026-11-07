# OPEN ROUTE #444 — unbound NAME lowered as an opaque constant (NameError: comprehension-variable leak, undefined / misspelt / later-defined global)
**Status: REPAIRED (executor r1, driver run #3, 2026-10-29; routes #444 / #445 / #446 / #453 / #457 / #458 by ONE fail-closed rule), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
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

## REPAIR (executor r1, driver run #3, 2026-10-29, off db6c57253; annotations §7.180, translational §T.6.190) -- routes #444 / #445 / #446 / #453 / #457 / #458 by ONE fail-closed rule

**Status: REPAIRED (this family's measured witnesses).** CENSUS FIRST: every Module 6 site that lowers an
unrecognised construct to an opaque value is enumerated in
`getting-better/systematic-soundness-r3/r1-opaque/census-fallback-sites.tsv` (436 rows: 254 OPAQUE-CALL, 151
MODELLED, 13 PIPELINE, 6 FACADE-0ARY, 5 GETATTR-DEFAULT, 3 OPAQUE-CONST, 3 RECORD-FIELD, 1 UNKNOWN-OP; column
`after_r1` says which are now FAIL-CLOSED -- 14 rows: the Name fallback, the `getattr_<cls>` / `getattr_2` /
record-field projections for judged receivers, `unknown_op`, the module `get_<attr>` load, the one-operand
`str_concat` / `path_join_op` lowerings).

THE RULE (inline in `_run_pipeline`, allow-list polarity, refuse by default; no emission change, no axiom, no def in a
mirrored file). The claim that speaks for a function is its own `no_exception` JOINED with the claim of every
claiming function that may call it (name / method tail / property / constructor `__init__` / file dunders,
transitively, `_rc444`) -- the exemplar of #445 is a claimed `f` calling an UNclaimed method that reads
`self.cout`. Under that claim, covering the exception CPython raises:
* #444 a Name load must resolve to a binding (parameter, own scope, enclosing def, module scope, real `builtins`);
  comprehension / generator / lambda targets are scoped to them -- `PYCSL-R444-UNBOUND-NAME`;
* #445 an attribute load on a FILE-class receiver (`self`, a class object, a derived file-class receiver) must be a
  class-body binding of the file MRO or a field #347 proves DEFINITELY assigned by the constructor actually run; on
  a receiver derived as one builtin class (or decided by an `isinstance` guard) the real class must have it --
  `PYCSL-R445-ATTRIBUTE-NOT-DEFINED`;
* #446 `@` / `@=` refused under any claim -- `PYCSL-R446-MATMUL-UNMODELLED`;
* #453 an attribute chain on an imported stdlib module must exist on the REAL module (`hasattr`) --
  `PYCSL-R453-MODULE-ATTRIBUTE`; a call admitted only by a #161 METHOD tail needs a (module, function) row
  (`os.path.join` over `str`, `copy.copy`, `dataclasses.replace`) -- `PYCSL-R453-MODULE-FUNCTION-NOT-ADMITTED`;
* #457 an imported name in an `isinstance` / `issubclass` class spec must be accepted by the REAL `isinstance(0, o)`
  -- `PYCSL-R457-CLASS-SPEC-NOT-A-CLASS`;
* #458 an operator on two operands each derived as ONE builtin class is admitted iff the REAL operation on samples of
  the pair raises no TypeError -- `PYCSL-R458-OPERAND-CLASSES`.


THIS ROUTE: 9/9 route witnesses refused PYCSL-R444-UNBOUND-NAME (np screen); corpus witnesses 6850 (`totl`), 6851 (comprehension-target leak), 6852 (undefined global) PROVED at base, REFUSED at candidate; control 6870 (module constant / builtin / loop and local bindings) PROVED at base and candidate. Residual: a nested CLASS body's names, names read after `del` or after their `except` handler, a walrus target of a comprehension that never ran, `global` names bound only by another function, module bindings placed after the call (`if __name__` order) and conditional module bindings (#459) are admitted; a file with a `*` import is not judged; annotations evaluated at def time are not read.

GATES and over-refusal cost: `getting-better/open-routes/README.md` (run #3, 2026-10-29, #444 / #445 / #446 / #453 / #457 / #458 REPAIRED) and `getting-better/systematic-soundness-r3/r1-opaque/GATES.txt`.
