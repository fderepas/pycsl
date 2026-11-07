# OPEN ROUTE #458 — binary operator on MISMATCHED builtin classes lowered by one operand's class: `str / str` -> path join, `int + str` / `bool + str` -> str_concat (TypeError)
**Status: REPAIRED (executor r1, driver run #3, 2026-10-29; routes #444 / #445 / #446 / #453 / #457 / #458 by ONE fail-closed rule), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r458/` (19): `c27_o003.py`, `c27_o010.py`, `c29_o000.py`, `c29_o004.py`, `c29_o010.py`, `c29_o016.py`, `c29_o023.py`, `c29_r000_realistic_path.py`, `c29_r003_concat_ensures.py`, `c31_o007.py`, `c31_o008.py`, `c37_o002.py`, `c37_o003.py`, `c37_o004.py`, `c37_o008.py`, `c37_o009.py`, `c37_o011.py`, `c37_o012.py`, `c37_o013.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F15 -- binary operator on MISMATCHED builtin classes lowered by one operand's class: `str / str` -> path join, `int + str` / `bool + str` -> str_concat (TypeError)   (19)
  EXEMPLAR c29/r000_realistic_path.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(base: str, name: str) -> int:
    |     full = base / name
    |     return len(full)
    CPython 3.14: f('/etc', 'hosts')  ->  VIOLATION TypeError unsupported operand type(s) for /: 'str' and 'str'
  MECHANISM: The BinOp lowering picks an implementation from ONE operand's class without checking the pair: `s / t` with
  two str operands lowers to `path_join_op s t` (the pathlib `Path / str` model, mlw/o003) and `n + s` (int + str)
  lowers to `str_concat n (str_hash_op s)` (mlw/o010); `True + s` likewise. CPython raises TypeError for all.
  Other mismatched pairs are refused (#441: `s / n`, `s - n`, `s + n`, `xs + n`) or fail to type-check (c27 / c29).
  REPAIR: ALLOW-LIST of (operator, left class, right class) triples -- the CPython numeric tower (int/bool/float), sequence
  concat / repeat (str+str, list+list, tuple+tuple, bytes+bytes, seq*int, int*seq), set and dict operators, and
  `/` only with a pathlib.Path operand -- every other pair is refused under no_exception (TypeError); the str
  concat and path-join lowerings must assert both operand classes.
  MEMBERS: c27/o003.py c27/o010.py c29/o000.py c29/o004.py c29/o010.py c29/o016.py c29/o023.py c29/r000_realistic_path.py c29/r003_concat_ensures.py c31/o007.py c31/o008.py c37/o002.py c37/o003.py c37/o004.py c37/o008.py c37/o009.py c37/o011.py c37/o012.py c37/o013.py
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


THIS ROUTE: 19/19 route witnesses refused PYCSL-R458-OPERAND-CLASSES (np screen); corpus witnesses 6866 (`str / str`), 6867 (`int + str`) PROVED at base, REFUSED at candidate; control 6874 (`str + str`, `int + bool`) PROVED at base and candidate. Residual: operands derived as SEVERAL classes (a Union an `isinstance` guard may narrow) or underivable, an augmented target whose class the propagation does not derive, `str` / `bytes` `%` formatting, `None` operands (#252's) and file-class operands (their dunders: #441 / #349) are not judged.

GATES and over-refusal cost: `getting-better/open-routes/README.md` (run #3, 2026-10-29, #444 / #445 / #446 / #453 / #457 / #458 REPAIRED) and `getting-better/systematic-soundness-r3/r1-opaque/GATES.txt`.
