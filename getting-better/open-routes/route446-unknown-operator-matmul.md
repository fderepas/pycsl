# OPEN ROUTE #446 — unknown binary operator `@` / `@=` lowered as `unknown_op` with no raises (TypeError)
**Status: REPAIRED (executor r1, driver run #3, 2026-10-29; routes #444 / #445 / #446 / #453 / #457 / #458 by ONE fail-closed rule), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r446/` (7): `c1_o048_matmul.py`, `c11_q042_matmul_field.py`, `c11_q044_matmul_bool.py`, `c27_o026.py`, `c4_a047_augelem_7.py`, `c4_a074_matmul_user.py`, `c5_x001_matmul_in_cond.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F3 -- unknown binary operator `@` / `@=` lowered as `unknown_op` with no raises (TypeError)   (7)
  EXEMPLAR c1/o048_matmul.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(a: int, b: int) -> int:
    |     return a @ b
    CPython 3.14: f(1, 2)  ->  VIOLATION TypeError unsupported operand type(s) for @: 'int' and 'int'
  MECHANISM: `a @ b` lowers to `(unknown_op a b)` declared `val unknown_op (x: int) (y: int) : int` -- no raises, no precondition
  (ast.MatMult is the ONLY operator missing from the IR map _PY_OP_MAP, frontend/Module5_IREmitter.py:2078-2095,
  so it becomes `?`, which expressions.py:7403-7405 lowers to `unknown_op`; mlw/o048). `@=`, `@` on bool / field / user class (no __matmul__) are the same.
  REPAIR: ALLOW-LIST of (operator, operand class pair): an operator with no lowering rule for its operand classes is
  REFUSED under no_exception (TypeError), never lowered to `unknown_op`. `@` on int / bool / float / str / list has
  no row; on a file class only when the class (MRO) defines __matmul__ / __rmatmul__ (then its contract speaks).
  MEMBERS: c1/o048_matmul.py c11/q042_matmul_field.py c11/q044_matmul_bool.py c27/o026.py c4/a047_augelem_7.py c4/a074_matmul_user.py c5/x001_matmul_in_cond.py
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


THIS ROUTE: 7/7 route witnesses refused PYCSL-R446-MATMUL-UNMODELLED (np screen); corpus witnesses 6858 (`a @ b`), 6859 (`xs[0] @= b`) PROVED at base, REFUSED at candidate. No control: `@` has no lowering, so every use under a claim is refused (0 claimed corpus / mirror uses). Residual: `unknown_op` stays reachable WITHOUT a claim (no exception is then claimed).

GATES and over-refusal cost: `getting-better/open-routes/README.md` (run #3, 2026-10-29, #444 / #445 / #446 / #453 / #457 / #458 REPAIRED) and `getting-better/systematic-soundness-r3/r1-opaque/GATES.txt`.
