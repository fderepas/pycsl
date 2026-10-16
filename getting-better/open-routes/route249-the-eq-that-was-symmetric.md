# OPEN ROUTE #249 — `==` ON `Any` IS MODELLED AS MATHEMATICAL EQUALITY; PYTHON `__eq__` NEED NOT BE

**Status: REPAIRED (gen #36, 2026-10-16; opened the same day), Severity 1 (design-level).** Residual of the
#247/#248 repair; driver-verified at the repaired tree (= HEAD 68ba005b): rc=0.

## Witness
`witnesses-r248/any_eq_symmetry.py`: `requires x == y`, `ensures y == x` PROVES. CPython: with
`A.__eq__ -> True` and `B.__eq__ -> False`, `A() == B()` is True and `B() == A()` is False.

## Mechanism
`==` on `Any`/erased values lowers to Why3 `=` (or an equivalence), so reflexivity/symmetry/transitivity
are free. Python only guarantees them for builtin types.

## Repair direction (design decision needed — record before building)
Options: (a) refuse `==`/`!=` between `Any` values in CONTRACTS (fail-closed; measure blast radius —
probably large); (b) lower `Any == Any` to an opaque binary predicate with no laws (program side fresh per
evaluation; contract side uninterpreted `py_eq x y`), keeping Why3 `=` only for declared builtin types;
(c) document "user __eq__ is an equivalence relation" as an explicit assumption in the soundness report
(the TCB) — only acceptable if surfaced, never silently.

## Repair landed (gen #36, 2026-10-16) — option (b)

### Step 1: census (base fded262c, measured before any code)
An erased value has an `int` term (`x: Any` emits `x: int`, a `List[Any]` is an `array int`, a field-less
class is `type a = int`), and every `==`/`!=` on it was Why3 `=`/`<>`; `x in [y]` was `x = y`, a `Set[Any]`
membership was map-key identity. A harness over `_handle_binop` logged every `==`/`!=`/`in` lowering with
its operand kinds (4759 sites: root 3009, pyref 600, mirror 1150; `census-base/`). The classifier prototype
flagged 236 root sites in 112 files (221 contract, 15 program), 84 of the files ONLY through a bare
`list`/`dict` annotation; the other 28 are the #241/#246/#248 witnesses, the `__eq__` drivers 0411-0413, the
unannotated-parameter files 1685-1687 and the TypeVar control 1851 (`census3/`). The final rule's footprint is
the byte-diff below: root 26 files, pyref 0, mirror 9 files (19 converted methods, program `if` tests only).
Counter-programs, every one PROVED at fded262c and FALSE in CPython (corpus
2370-2393, each file's `__main__` is the ground truth): symmetry (contract 2370, program 2376, contract-to-body
2379, through copied locals 2380, a `List[Any]` element 2381, a `Dict[str, Any]` value 2382, `object` 2384,
unannotated 2385, a function returning `Any` 2387, a `Tuple[Any, int]` 2389, a whole `List[Any]` 2390, a
record field declared `Any` 2392, a field-less class defining `__eq__` 2393); transitivity (2371, through a
literal 2374, through an `int` parameter 2386); reflexivity (contract 2372, program 2377: plain `nan`, no
user class needed); `!=` read as `not ==` (2373, program 2378: `__ne__` is its own method); substitutivity
(`requires x == 5` decided `x + 1 == 6`, 2375; `x in s and x == y` decided `y in s` on a `Set[Any]`, 2388);
membership read as `=` (`x in [y]` then `y == x`, 2383: Python's list membership is `y is x or y == x`;
`x is not y` then `x in [y]` decided False, 2391).

### Step 2: the rule
With an ERASED operand, `==`, `!=` and `in`/`not in` lower to UNINTERPRETED polymorphic symbols with NO law:
`val function pycsl_py_eq (a: 'a) (b: 'b) : bool`, `pycsl_py_ne` (its own symbol: `__ne__` is not `not
__eq__`), `pycsl_py_in` (`not in` is its negation, as in Python). No axiom, no definition, ledger 3. One symbol
serves contracts and bodies, so a program test and a clause over the SAME operands agree (control 2398); that
is the assumption that `__eq__`/`__ne__`/`__contains__` are deterministic functions of their operands, the one
every contract evaluation already makes (`requires x == y ensures x == y` still proves). An identity test
(`is`/`is not`, route #42's `py_is` marker) keeps `=` (control 2399). Builtin-typed operand pairs keep `=`
(controls 2395-2397: `int`/`str` symmetry and `int` transitivity still PROVE).

ERASED (an inline explicit-stack walk, duplicated in `functions._reset_function_state`'s pre-scan and in
`expressions._handle_binop`; both mirror twins are `\trusted`): a formal parameter declared `Any`/`object`/
unannotated/a TypeVar/a non-record class defining `__eq__` or `__ne__`; every local bound (assignment,
augmented assignment, `for`/comprehension/tuple target) from an erased expression (flow-insensitive
fixpoint, route #46's shape); `\result` of a function declared `-> Any`/`object`/TypeVar; a call of a module
function so declared, or of such a class's constructor; a read, attribute, method call, arithmetic or
conditional on an erased value; a record field declared `Any`/`object`; an element read (subscript, `.get`,
`.pop`, ...) of a container annotated with `Any`/`object`/a TypeVar inside (`List[Any]`, `Dict[str, Any]`
values, `Dict[Any, int]` keys for `in`, `Set[Any]`, `Tuple[Any, int]`; Module 5 records them as the additive,
only-when-non-empty IR key `r249_erased_containers`), the whole container itself, an unannotated `*args`; a
literal container holding any of these. Option (a) was not needed: (b) costs two declared verdicts (below).

### Blast radius (logs: `/tmp/claude-1000/.../scratchpad/r249/`)
- Witnesses: `witness-base.log` (2370-2393 PROVED, 2395-2399 PASS), `witness-after.log` (2370-2393 Unknown/
  Timeout, 2395-2399 PASS); probes `probe-base.log`, `probe-after.log`.
- Corpus byte-diff vs a fresh fded262c worktree: root 1629 baseline / 1658 candidate, 26 MOVED, 0 GONE,
  0 APPEARED, 29 new sources (`compare-root.log`; `compare-root-declared.log` rc=0 with the 26 declared);
  pyref 2198/2198, 0 MOVED/GONE/APPEARED (`compare-pyref.log`). M1, every mover re-proved base and after
  (`m1-base.log`, `m1-after.log`): 22 FAIL -> FAIL (expected FAIL: 0412, 0884, 1685, 1687, 2242, 2243, 2245,
  2247, 2272, 2273, 2320-2326, 2331, 2350-2353), 2 PASS -> PASS (0411, 0413: `__eq__` drivers, `--no-proof`),
  2 PASS -> FAIL, declared in the files:
  - 1851 (`Box[T].get` `ensures \result == self.v`): a FALSE claim for `T = float` (`nan`); it proved only by
    reflexivity of `==` on a TypeVar value. Still emitted and type-checked (no refusal).
  - 1686 (route #194 control, `f(self, p)` unannotated, `ensures p == 0 ==> \result == 1`, called with `0`):
    TRUE in CPython; the caller's instance `pycsl_py_eq 0 0` is no longer decided. The price of the rule, like
    #248's 2332.
- Mirror: 53/53, 9 MOVED (`core_ir_semantic`, `frontend/Module3_Weaver`, `frontend/Module5_IREmitter`,
  `frontend/exec_splice`, `frontend/pure_ast`, `module6_whyml/auto_trust`, `module6_whyml/preamble`,
  `proof2why3/sertop`, `pycsl`: program-side tests on `Any` operands, 19 methods), 0 GONE; base and after
  `why3 --type-only` rc=0 (`compare-mirror.log`, `mirror-typeonly-base.log`, `mirror-typeonly-after.log`).
- A bare `list`/`dict`/`set` annotation is NOT erased (measured first: erasing it moved 87 more corpus files,
  >= 65 PASS -> FAIL, all `ensures \result == a[i]`-shaped). PyCSL reads it as an `int`-element container
  (translational reference §T.Ann.2 rows 3a/3b), the same declared-type trust as `x: int` — see residuals.
- Ledgers: one new per-function field `_r249_scope`, declared in the `_reset_function_state` mirror stub's
  `#@ assigns` (check-assigns-underdeclaration TRAP 4 > 3 before the declaration, 3 after; route #242's
  precedent). No refusal, raise, def or axiom.
- Planes 61/61 (`planes.log`); `check-self-annotate-sync.sh` rc=0 (916 verbatim, `sync.log`);
  `self-annotate-mirror-check.sh` rc=0 (`mirror-check.log`). No edited live method has an un-`\trusted`
  mirror twin (`_handle_binop`, `_expr_to_whyml`, `_reset_function_state`, `_build_function_ir`).
- NOT re-proved: the 19 converted mirror methods whose program `if` tests now read `pycsl_py_eq/ne/in`
  (type-only clean; a whole/per-function mirror proof did not fit the session's heavy-slot budget).

## Residuals (NOT repaired here; each reproducer PROVES at fded262c and after)
- **Float NaN (a separate value-model route).** A `float` is a Why3 `real`, which has no NaN, so every
  contract comparison of float terms is decided as over the reals: `ensures x == x`, `ensures x <= x`, and
  `requires x != y ensures x < y or y < x` PROVE for `x: float` (CPython `nan`; `witnesses-r249/float_nan_*`). (A program-side float `==`
  is an L3-tc error, fail-closed.) Not an `==`-lowering defect: the orderings share it, and guarding a float
  comparison with an uninterpreted "not NaN" predicate makes `\result == 1.5` unprovable for `return 1.5`
  (no literal can be shown non-NaN without an axiom); the census counts 13 root files with a float `==` in a
  contract. Needs a NaN-carrying float sort.
- **Arithmetic on `Any` is `int` arithmetic** (`witnesses-r249/any_sub_self_is_zero.py`): `return x - x` on
  `x: Any` proves `\result == 0` (`-> int`, so `\result` is not erased; CPython: `__sub__` returns 7). Same
  family as route #227; not an `==` law.
- **Declared-type trust.** `x: int` keeps `=` although a subclass of `int` may override `__eq__` (as #247
  records for classes); a bare `list`/`dict`/`set` param is read as `int` elements (above); a field-less class
  WITHOUT its own `__eq__` keeps `=` (identity), though a subclass instance may override it; a record class
  with `__eq__` stays route #76's (refused in a contract, ill-typed in a program).
- **Sources the pre-scan does not see**: values from unmodelled/opaque calls (`getattr` on a non-erased
  object, a stdlib call returning `Any`), a container FIELD annotated `List[Any]`, a comparison RESULT used as
  a value (a user `__eq__` may return a non-bool); hash-based dict/set operations on erased keys still use
  map-key identity (`witnesses-r249/any_dict_key_identity.py`: `d[x] = 1; return d[x]` proves `\result ==
  1`; CPython: a `__hash__` that changes between calls raises KeyError).
- Each residual reproducer PROVES at fded262c and after (`residual.log`); CPython ground truth in `__main__`.
