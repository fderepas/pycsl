# OPEN ROUTE #248 — THE MODEL ASSUMES BUILTIN `==` FOR `Any` VALUES; A USER `__eq__` BREAKS IT

**Status: REPAIRED (gen #36, 2026-10-16; opened the same day), Severity 1.** Residual recorded by the #245 and #246 repairs;
driver-verified to PROVE at the #246 candidate tree (= HEAD 1a86a361).

## Witness
`witnesses-r246/user_eq_str.py`: `f(x: Any, y: Any)` with `requires x == y` and
`ensures isinstance(x, str) == isinstance(y, str)` PROVES. CPython: `W() == "s"` is True for
`class W: def __eq__(self, o): return True`, and the postcondition is False.

## Mechanism
`==` on `Any`/erased values is modelled as structural/value equality of the lowered value, and the
str/list/dict isinstance answers (kept value-applied by #245/#246, control 2331) rely on `==` never
crossing types — true for builtins only.

## Repair direction
Either refuse contract reasoning that combines `==` on `Any` with type tests (fail-closed), or require the
subject to be builtin-typed (a declared non-Any type), or model user classes' `__eq__` (out of scope).
Measure the corpus blast radius first: control 2331 encodes exactly this assumption.

## Repair landed (gen #36, 2026-10-16) -- jointly with #247
Options measured first (base afe28c69). Contract-side isinstance appears in the corpus only in 0632-0634 and the
route files; the mirror has none. A narrow "refuse only when the same contract has `==`" rule is NOT sound: the
program-side form (2351: `if x == y`, two `str` tests), the contract-to-body form (2352: `requires x == y`) and the
callee form (2353: a caller's `requires y == z` + `isinstance(y, list)` discharging the callee's `requires
isinstance(z, list)`, i.e. control 2332's own shape) all PROVED at base. `PyVal` is `Any` (`src/pycsl/errors.py`),
so the hval side has the same issue: `requires d["a"] == d["b"]` (2354) and `requires d == e` (2355, whole-dict map
`=`) PROVED the `str` agreement through the decided `HStr` arm. Rule (narrowest that closes every measured shape):
- `Any`/erased (undecided, non-hval) subject: `str`/`list`/`dict` lose #239's value application and join #246's
  arm -- contract REFUSED (`pycsl_refused_contract_type_test_on_int_erased_value`), program keyed on an unrebound
  parameter's identity (two tests of one parameter still agree: 2363, 2330, 2211), else `(any bool)`.
- hval subject in a CONTRACT: every test whose answer is not the constant `true` (any class but `object`) is
  REFUSED (`pycsl_refused_contract_type_test_on_erased_hval`, #245's symbol). Program side unchanged: a program `==`
  between hvals is ill-typed (measured, fail-closed), and on a contract-equated pair the `HInt` arm is a fresh
  `(any bool)`, so no two program tests are forced to agree (`requires d == e` + two body `str` tests: unprovable).
Unbound-symbol refusals only (no raise, def, declaration or axiom); ledger 3.

## Witnesses (corpus, `gen36_r247`/`gen36_r248`; CPython ground truth: each file's `__main__`, all run OK)
False claims PROVED at afe28c69, FAIL/REFUSED after: 2340-2348 (#247), 2350-2355 (#248). Controls PASS after:
2360-2364. Declared PASS -> FAIL (each was a FALSE claim under a user `__eq__`, or is the price of the refusal):
2310-2313 (hval str/dict/tuple/list "equal values agree"), 2331 (Any `str`), 2332 (`requires isinstance(x, list)`
-> body; true, but its value application is what 2353 exploits). All other #239/#245/#246 files keep their verdict.

## Gates (logs: `/tmp/claude-1000/.../scratchpad/r247/`)
- Witnesses: `witness-base.log`, `witness-after.log`; probes `probe-base.log`; M1 `m1-movers.log`.
- Corpus byte-diff vs a fresh afe28c69 worktree: root 1609 baseline / 1629 candidate, 7 MOVED (0884, 2310-2313,
  2331, 2332), 0 GONE, 0 APPEARED, 20 new sources (`compare-root.log`, `compare-root-declared.log` rc=0); pyref
  2198/2198, 0 MOVED/GONE/APPEARED (`compare-pyref.log`). Movers re-proved: 0884 FAIL -> FAIL (expected FAIL; its
  program dict/list tests on an `Any` param are now identity-keyed, the `str` test on `node.get(..)` `(any bool)`),
  2310-2313/2331/2332 PASS -> FAIL (declared above).
- Mirror: 53/53, 5 MOVED (`frontend/exec_splice`, `frontend/monomorphize`, `frontend/pure_ast`,
  `module6_whyml/expressions`, `module6_whyml/functions`: program `str`/`list` tests on `Any`/erased subjects ->
  identity key or `(any bool)`), 0 GONE; base and after `why3 --type-only` rc=0 (`mirror-typeonly*.log`).
- Planes 61/61 (`planes.log`); sync rc=0 (916 verbatim); mirror-check rc=0.

## Residuals (NOT repaired here; reproducers PROVE at afe28c69 and after)
- **`==` itself on `Any` is builtin equality.** `requires x == y`, `ensures y == x` PROVES (`witnesses-r248/any_eq_symmetry.py`); CPython `A() == B()` is
  True and `B() == A()` False for `A.__eq__ -> True`, `B.__eq__ -> False`. Every consumer of `==`-as-`=` on `Any`
  (not only isinstance) inherits it.
- The sync plane compares class-level DICT constants by KEY SET only, so `_METATYPE_TAGS`' changed VALUES
  (`set`/`frozenset`) were invisible to it (the mirror copy was updated by hand).
