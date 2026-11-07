# OPEN ROUTE #445 — missing ATTRIBUTE (file class / instance / int receiver) lowered as an opaque getattr or an always-present record field (AttributeError)
**Status: REPAIRED (executor r1, driver run #3, 2026-10-29; routes #444 / #445 / #446 / #453 / #457 / #458 by ONE fail-closed rule), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r445/` (21): `c11_q028_field_typo_self.py`, `c17_w004_inherited_field_missing.py`, `c17_w008_self_method_typo_call.py`, `c26_a003_nested_class_attr.py`, `c26_a004_self_class_attr_typo.py`, `c26_a005_field_set_in_branch_init.py`, `c26_a007_sub_init_no_super_method.py`, `c26_a010_realistic_sub_forgets_super.py`, `c34_q004_init_type_checking_field.py`, `c4_n013_class_attr_undef.py`, `c42_a000.py`, `c42_a011.py`, `c42_a018.py`, `c43_a002.py`, `c43_a003.py`, `c43_a004.py`, `c43_a005.py`, `c43_a006.py`, `c43_a007.py`, `c43_a010.py`, `c43_a021_int_attr_ensures.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F2 -- missing ATTRIBUTE (file class / instance / int receiver) lowered as an opaque getattr or an always-present record field (AttributeError)   (21)
  EXEMPLAR c11/q028_field_typo_self.py  PROVED (rc=0 Verification SUCCESS):
    | class P:
    |     def __init__(self) -> None:
    |         self.count = 1
    | 
    |     def g(self) -> int:
    |         return self.cout
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(p: P) -> int:
    |     return p.g()
    CPython 3.14: f(P())  ->  VIOLATION AttributeError 'P' object has no attribute 'cout'
  MECHANISM: `self.cout` (no such field) lowers to the opaque `getattr_p self <hash>` (no raises; the field-miss fallback,
  expressions.py:19072-19082); `P.zzz` (no such class
  attribute) likewise; a base field set only by a base __init__ that the subclass __init__ never calls (w004) is
  read as the always-present record field `self.q_a`; `self.helpr()` (no such method) lowers to an opaque val;
  a field set in only ONE branch of __init__ and read by a method (c26/a005) proves -- the external read of the
  same shape is refused by #347 (c2/u022), so #347 covers external receivers only, not `self` inside methods.
  The same fallback (`getattr_2 (x: int) (f: int) : int`) serves a non-call attribute LOAD on an `int` receiver:
  `n.zz`, `n.upper`, `n.bit_lenght` prove (c42); on str / list / dict / set / bytes / float receivers the WhyML
  does not type-check, and method CALLS are #440's (refused).
  REPAIR: OBLIGATION per attribute load on a file-class receiver: the attribute must be (a) a field DEFINITELY assigned on
  every path of the __init__ chain actually executed (subclass __init__ without super().__init__() does not run the
  base's), (b) a class-body binding / method / property in the file MRO, or (c) refused (AttributeError). The
  opaque `getattr_<cls>` fallback must not be reachable under a no_exception claim.
  MEMBERS: c11/q028_field_typo_self.py c17/w004_inherited_field_missing.py c17/w008_self_method_typo_call.py c26/a003_nested_class_attr.py c26/a004_self_class_attr_typo.py c26/a005_field_set_in_branch_init.py c26/a007_sub_init_no_super_method.py c26/a010_realistic_sub_forgets_super.py c34/q004_init_type_checking_field.py c4/n013_class_attr_undef.py c42/a000.py c42/a011.py c42/a018.py c43/a002.py c43/a003.py c43/a004.py c43/a005.py c43/a006.py c43/a007.py c43/a010.py c43/a021_int_attr_ensures.py
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


THIS ROUTE: 21/21 route witnesses refused PYCSL-R445-ATTRIBUTE-NOT-DEFINED (np screen); corpus witnesses 6853 (`self.cout` in an UNclaimed method called by the claimer), 6854 (a field stored in one `__init__` branch), 6855 (subclass skips `super().__init__()`), 6856 (`n.zz`), 6857 (`P.zzz`) PROVED at base, REFUSED at candidate; control 6871 (fields on every path through `super().__init__()`, a class attribute) PROVED at base and candidate. Residual: receivers whose class is underivable (#443's), derived as several builtin classes without a deciding `isinstance` guard, or of a class with a non-file base (Enum / NamedTuple / Exception / a stdlib class) or a `__getattr__`; files that add attributes dynamically (`setattr` / `__dict__`); attribute names some code stores through another receiver; the builtin call `getattr(o, "lit")`.

GATES and over-refusal cost: `getting-better/open-routes/README.md` (run #3, 2026-10-29, #444 / #445 / #446 / #453 / #457 / #458 REPAIRED) and `getting-better/systematic-soundness-r3/r1-opaque/GATES.txt`.
