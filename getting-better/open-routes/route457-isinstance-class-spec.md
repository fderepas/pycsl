# OPEN ROUTE #457 — #441 CLASS-SPEC code admits any imported name: `isinstance(x, sqrt)`, `isinstance(x, Any)`, `(int, join)` (TypeError)
**Status: REPAIRED (executor r1, driver run #3, 2026-10-29; routes #444 / #445 / #446 / #453 / #457 / #458 by ONE fail-closed rule), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r457/` (5): `c23_i000.py`, `c23_i001.py`, `c23_i002.py`, `c23_i004.py`, `c23_i005.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F14 -- #441 CLASS-SPEC code admits any imported name: `isinstance(x, sqrt)`, `isinstance(x, Any)`, `(int, join)` (TypeError)   (5)
  EXEMPLAR c23/i005.py  PROVED (rc=0 Verification SUCCESS):
    | from json import loads
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(x: int) -> int:
    |     if isinstance(x, loads):
    |         return 1
    |     return 0
    CPython 3.14: f(1)  ->  VIOLATION TypeError isinstance() arg 2 must be a type, a tuple of types, or a union
  MECHANISM: #441's isinstance row codes argument 2 as CL (class or tuple of classes) but, as its residual (4) states, the code
  admits ANY imported name -- a function (`sqrt`, `math.sqrt`, `json.loads`, `os.path.join` inside a tuple) and
  `typing.Any`; #442 then simply does not narrow, and the call lowers to an opaque test with no raises.
  Subscripted generics (`List[int]`, `Sequence[int]`), TypeVar, Literal, non-runtime Protocols ARE refused.
  REPAIR: ALLOW-LIST for CL: a name resolving (statically, through the import) to an object `o` with `isinstance(o, type)`
  (checked on the real imported object, as #442 does for builtins), a PEP 604 / typing.Union of such, or a tuple
  of these; refuse functions, typing.Any and every other special form (TypeError).
  MEMBERS: c23/i000.py c23/i001.py c23/i002.py c23/i004.py c23/i005.py
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


THIS ROUTE: 5/5 route witnesses refused PYCSL-R457-CLASS-SPEC-NOT-A-CLASS (np screen); corpus witnesses 6864 (`loads`), 6865 (`Any`) PROVED at base, REFUSED at candidate; control 6873 (`isinstance(x, (Fraction, str))`) PROVED at base and candidate. Residual: an imported name from a module outside the standard library is not judged.

GATES and over-refusal cost: `getting-better/open-routes/README.md` (run #3, 2026-10-29, #444 / #445 / #446 / #453 / #457 / #458 REPAIRED) and `getting-better/systematic-soundness-r3/r1-opaque/GATES.txt`.
