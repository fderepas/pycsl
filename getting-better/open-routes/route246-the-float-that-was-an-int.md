# OPEN ROUTE #246 — ON AN `Any` PARAMETER, `isinstance(x, int)` CANNOT TELL `1` FROM `1.0`

**Status: REPAIRED (gen #36, 2026-10-16; opened the same day), Severity 1.** Residual of the #245 repair; driver-reproduced at
8260571f (both rc=0) and present at HEAD dfaaeb82.

## Witnesses (`witnesses-r245/`)
- `any_int_vs_float_in_contract.py`: `requires x == y`, `ensures isinstance(x, int) == isinstance(y, int)` PROVES.
- `any_int_vs_float_program_side.py`: `if isinstance(x, int): if not isinstance(y, int): return 0` with
  `ensures \result == 1` PROVES. CPython `f(1, 1.0)` breaks both. float/set analogues also prove.

## Mechanism
An `Any` parameter is stored as an int; #239 lowered `isinstance(x, T)` to `subtag (typeof_op x) T`, a
function of the STORED integer, so Python values of different types that compare equal (1 / 1.0,
{1} / frozenset({1})) get the same answer in contracts and program bodies.

## Repair direction
Fail-closed for classes with cross-type `==` (int/float/bool/complex, set/frozenset, bytes/bytearray,
user classes): a program-side test is a fresh opaque per evaluation and a contract-side test is refused —
while keeping #239's `requires isinstance(x, int)` -> body link (control 2212) where it is sound (e.g. tie
the type tag to the PARAMETER rather than to its value, or keep the link only for classes whose `==` never
crosses types).

## Repair landed (gen #36, 2026-10-16)
`expressions._handle_isinstance`, the route #239 undecided-subject arm (inline; the mirror twin is a `\trusted`
stub, so nothing to re-port). For a class whose builtin `==` can cross types -- every TAGGED class but
`str`/`list`/`dict`/`object`: `int`, `float`, `set`/`frozenset` (which share `dict`'s tag), user record/variant
classes; `bool` and the tuple form already took the unknown-class arm (#240):
- CONTRACT side: REFUSED at the WhyML type-check, the application of the UNBOUND symbol
  `pycsl_refused_contract_type_test_on_int_erased_value <subject> "<T>"` (route #245's answer; no declaration).
- PROGRAM side: never a function of the stored value. On an UNREBOUND PARAMETER (a bare, non-`ref` Why3
  parameter of the function being emitted, in a plain `let`), the tag is keyed on the parameter's IDENTITY:
  `(typeof_op "pycsl_param_tag:<fn>:<x>") = <lit>` -- one Python object per invocation, so two tests of it agree
  (2211/2330 keep PASS), another parameter / a rebinding never share it. No contract can name the key (refused),
  and a plain `let` body is invisible to callers. Everywhere else (rebound `!x`, non-Var subjects, and any
  `let function` candidate, whose body IS visible to callers per #242) it is a fresh `(any bool)`, which also
  demotes a logic candidate to a plain `let`.
`str`/`list`/`dict` keep #239's value application in both contexts (2331, 2332): `requires isinstance(x, list)`
still decides the body. No raise, def, declaration or axiom; ledger 3.

Options measured first (baseline emissions at f777e2bd): `typeof_op` appears in 11 corpus files (0634, 0884 and
the #239/#240 route files) and 6 mirror files, of which only 4 mirror sites test `int`/`float` (all non-Var or
`ref` subjects). "Fresh opaque everywhere" would have cost 2211 (a true claim); the identity key keeps it. 2212
cannot be kept by any value- or identity-keyed contract term: its postcondition about `x` is instantiated per
call, and with two `==` actuals of different types the same proof yields a false claim (2325). 2212 is now
expected FAIL (refused), its docstring records why.

## Witnesses (corpus, `gen36_r246`; CPython ground truth: each file's `__main__`, all run OK)
False claims PROVED at f777e2bd, REFUSED (unbound refusal symbol) or FAIL after: 2320 (contract, int, 1/1.0;
refused), 2321 (program, int), 2322 (program, float), 2323 (program, set/frozenset), 2324 (rebinding to an `==`
float), 2325 (callee postcondition, two `==` actuals; refused), 2326 (callee requires discharged by an `==`
value; refused). Controls PASS at base and after: 2330 (float test of one param twice), 2331 (`str` contract,
`requires x == y`), 2332 (`requires isinstance(x, list)` -> body), 2333 (program int test on a rebound name, within
bounds). #239 controls: 2210 FAIL/FAIL, 2211 PASS/PASS, 2213-2215 PASS/PASS; 2212 PASS -> FAIL (above).

## Gates (logs: `/tmp/claude-1000/.../scratchpad/r246/`)
- Witnesses: `witness-base.log`, `witness-after.log`, `m1-movers.log`, `m1-0634-0884.log`.
- Corpus byte-diff vs a fresh f777e2bd worktree: root 1598 baseline / 1609 candidate, 10 MOVED (0634, 2200-2204,
  2210-2212, 2241), 0 GONE, 0 APPEARED, 11 new sources; pyref 2198/2198, 0 MOVED/GONE/APPEARED
  (`compare-root.log`, `compare-pyref.log`). Every mover re-proved at base and after: 0634 FAIL -> FAIL (now
  refused; expected FAIL), 2200/2203/2210/2241 FAIL -> FAIL, 2201/2202/2204 FAIL -> FAIL (now refused), 2211
  PASS -> PASS (identity key), 2212 PASS -> FAIL (declared above).
- Mirror: 53/53, 3 MOVED (`frontend/module_collect`, `frontend/pure_ast`, `module6_whyml/expressions`: 5 int/float
  program tests on non-Var / `ref` subjects -> `(any bool)`), 0 GONE; base and after `why3 --type-only` rc=0.
- Planes 61/61 (`planes.log`); sync rc=0 (916 verbatim); mirror-check rc=0.

## Residuals (NOT repaired here; reproducers in `witnesses-r246/`, PROVE at f777e2bd AND after)
- **`set`/`frozenset` share `dict`'s tag.** `def f(d: Dict[int, int])`, `if isinstance(d, set): return 1`,
  `ensures \result == 1` PROVES (`dict_set_tag.py`); CPython `f({})` = 0. A DECIDED subject's tag is compared
  with `tag_dict` for `set`. (On an undecided subject the set test is now opaque/refused.)
- **A user `__eq__` crosses every type.** `requires x == y`, `ensures isinstance(x, str) == isinstance(y, str)`
  PROVES (`user_eq_str.py`, control 2331's shape); CPython `x = W()` with `__eq__` always True, `y = "s"`. Same
  builtin-values reading of `==` as #245's recorded residual (`UserString`, `Mapping`/`UserList` subclasses).
