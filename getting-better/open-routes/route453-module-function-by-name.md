# OPEN ROUTE #453 — MODULE receiver not judged: a module function admitted by its TAIL name (#161 METHODS) and a NONEXISTENT module attribute (sys.maxint, math.PI) lower to opaque values
**Status: REPAIRED (executor r1, driver run #3, 2026-10-29; routes #444 / #445 / #446 / #453 / #457 / #458 by ONE fail-closed rule), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r453/` (56): `c13_m003_shutil_copy.py`, `c13_m004_os_replace.py`, `c13_m010_itertools_count.py`, `c13_m020_math_copy.py`, `c13_m021_os_path_lower.py`, `c16_m003_heapq_count.py`, `c16_m004_os_path_get.py`, `c16_m005_itertools_count.py`, `c16_m006_shutil_copy.py`, `c16_m007_os_replace.py`, `c16_m010_math_union.py`, `c16_m011_re_strip.py`, `c16_m013_shutil_copy.py`, `c16_m020_realistic_backup.py`, `c16_m021_realistic_atomic_write.py`, `c16_m022_realistic_counter.py`, `c16_m023_shutil_copy_ensures.py`, `c18_z011_math_attr_direct.py`, `c18_z012_module_const_typo.py`, `c21_a000_sys_maxint.py`, `c21_a001_string_letters.py`, `c21_a003_os_errno.py`, `c21_a004_sys_setdefaultencoding.py`, `c21_a005_collections_Mapping.py`, `c21_a006_math_PI.py`, `c21_a008_string_uppercase.py`, `c21_a009_types_StringType.py`, `c21_a021_module_attr_ensures.py`, `c21_a023_from_mod_attr_typo.py`, `c25_t003_math_copy.py`, `c25_t007_math_count.py`, `c25_t008_math_get.py`, `c25_t009_math_keys.py`, `c25_t010_math_values.py`, `c25_t011_math_items.py`, `c25_t016_math_union.py`, `c25_t017_math_intersection.py`, `c25_t018_math_difference.py`, `c25_t019_math_issubset.py`, `c25_t020_math_issuperset.py`, `c25_t021_math_strip.py`, `c25_t022_math_lstrip.py`, `c25_t023_math_rstrip.py`, `c25_t024_math_lower.py`, `c25_t025_math_upper.py`, `c25_t026_math_startswith.py`, `c25_t027_math_endswith.py`, `c25_t028_math_replace.py`, `c25_t029_math_join.py`, `c25_t030_math_find.py`, `c25_t031_math_rfind.py`, `c25_t033_math_isdigit.py`, `c25_t034_math_isalpha.py`, `c25_t035_math_isalnum.py`, `c25_t036_math_isspace.py`, `c25_t037_math_bit_length.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F10 -- MODULE receiver not judged: a module function admitted by its TAIL name (#161 METHODS) and a NONEXISTENT module attribute (sys.maxint, math.PI) lower to opaque values   (56)
  EXEMPLAR c16/m020_realistic_backup.py  PROVED (rc=0 Verification SUCCESS):
    | import shutil
    | 
    | 
    | 
    | #@ no_exception \all
    | def f(path: str) -> int:
    |     shutil.copy(path, path + '.bak')
    |     return len(path)
    CPython 3.14: f('/nonexistent/rt36.cfg')  ->  VIOLATION FileNotFoundError [Errno 2] No such file or directory: '/nonexistent/rt36.cfg'
  MECHANISM: Route #161 classifies `m.f(..)` with a dot as a METHOD call and admits it when the tail f is in _R161_METHODS
  (copy, count, get, update, lower, union, ...); #440 judges builtin / file classes only, #443 explicitly does not
  judge a module object (`import m`). So shutil.copy (FileNotFoundError), os.replace, itertools.count(<str>)
  (TypeError) and even NON-EXISTENT module attributes (math.copy, re.strip, heapq.count, os.path.get:
  AttributeError) lower to opaque raise-free vals (`shutil_copy_2 ..`, mlw/m020). A NONEXISTENT module
  ATTRIBUTE load (`sys.maxint`, `math.PI`, `collections.Mapping`, `os.errno`: legacy Python-2 / removed names)
  lowers to `(get_maxint sys)` with `val get_maxint (x: int) : int` (mlw/a000) -- no existence check at all.
  COVERAGE MAP (c25, `math.<tail>(n)` for every #161 method tail): 27 / 38 tails PROVED; refused only the 10
  mutating tails (append extend insert clear reverse sort setdefault update add discard, by a mutation gate) and
  split (#72).
  REPAIR: ALLOW-LIST of (module, function) pairs, refuse by default: a call whose receiver is a module object is admitted
  only for an explicit (module, name) row (with its argument codes / obligations, as #441's rows) or a module of
  the verified program that defines the name; the method-name tail arm must never apply to a module receiver.
  A module ATTRIBUTE load is admitted only when `hasattr(<real module>, name)` holds at verification time (the
  pipeline already imports real modules for #443's ten-module list) -- refuse otherwise (AttributeError).
  MEMBERS: c13/m003_shutil_copy.py c13/m004_os_replace.py c13/m010_itertools_count.py c13/m020_math_copy.py c13/m021_os_path_lower.py c16/m003_heapq_count.py c16/m004_os_path_get.py c16/m005_itertools_count.py c16/m006_shutil_copy.py c16/m007_os_replace.py c16/m010_math_union.py c16/m011_re_strip.py c16/m013_shutil_copy.py c16/m020_realistic_backup.py c16/m021_realistic_atomic_write.py c16/m022_realistic_counter.py c16/m023_shutil_copy_ensures.py c18/z011_math_attr_direct.py c18/z012_module_const_typo.py c21/a000_sys_maxint.py c21/a001_string_letters.py c21/a003_os_errno.py c21/a004_sys_setdefaultencoding.py c21/a005_collections_Mapping.py c21/a006_math_PI.py c21/a008_string_uppercase.py c21/a009_types_StringType.py c21/a021_module_attr_ensures.py c21/a023_from_mod_attr_typo.py c25/t003_math_copy.py c25/t007_math_count.py c25/t008_math_get.py c25/t009_math_keys.py c25/t010_math_values.py c25/t011_math_items.py c25/t016_math_union.py c25/t017_math_intersection.py c25/t018_math_difference.py c25/t019_math_issubset.py c25/t020_math_issuperset.py c25/t021_math_strip.py c25/t022_math_lstrip.py c25/t023_math_rstrip.py c25/t024_math_lower.py c25/t025_math_upper.py c25/t026_math_startswith.py c25/t027_math_endswith.py c25/t028_math_replace.py c25/t029_math_join.py c25/t030_math_find.py c25/t031_math_rfind.py c25/t033_math_isdigit.py c25/t034_math_isalpha.py c25/t035_math_isalnum.py c25/t036_math_isspace.py c25/t037_math_bit_length.py
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


THIS ROUTE: 56/56 route witnesses refused (np screen): PYCSL-R453-MODULE-ATTRIBUTE for the nonexistent attributes / functions (`math.copy`, `os.path.lower`, `sys.maxint` ...), PYCSL-R453-MODULE-FUNCTION-NOT-ADMITTED for the real functions admitted by a #161 tail (`shutil.copy`, `os.replace`, `itertools.count`); corpus witnesses 6860-6863 PROVED at base, REFUSED at candidate; control 6872 (`sys.maxsize`, `os.path.join` over `str`) PROVED at base and candidate. Allow-list rows (measured need): `os.path.join` (/ `posixpath.join`) over `str`, `copy.copy` (corpus control 6027), `dataclasses.replace` (corpus control 5591). Residual: a module outside the standard library (a sibling / user module) is not judged; a name bound by two different imports is not judged; a module-function call whose tail is NOT a #161 method name stays #161's (refused by name).

GATES and over-refusal cost: `getting-better/open-routes/README.md` (run #3, 2026-10-29, #444 / #445 / #446 / #453 / #457 / #458 REPAIRED) and `getting-better/systematic-soundness-r3/r1-opaque/GATES.txt`.
