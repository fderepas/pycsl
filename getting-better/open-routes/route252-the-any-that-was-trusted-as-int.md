# OPEN ROUTE #252 — AN `Any` VALUE FLOWING INTO AN `int`-TYPED SLOT IS TRUSTED AS AN INT

**Status: REPAIRED (gen #36, 2026-10-16; opened the same day), Severity 1.** Residuals of the #251 repair; driver-reproduced at HEAD
6228d5ae (all three rc=0).

## Witnesses (`witnesses-r252/`)
- `r1_any_to_int_param.py`: `g(a: int, b: int)` with `ensures \result == a - b`; `return g(x, x)` for `x: Any`
  proves `\result == 0` (CPython: a user `__sub__` returns 7 — Python does not enforce the annotation).
- `r4_any_into_int_local_annot.py`: same through `int` record fields (`Box(x, x)`; `b.v - b.w`).
- `r3_noexc_any_sub.py`: `#@ no_exception \all` with `y = x - x` on `x: Any` proves; a user `__sub__` can raise.

## Mechanism
Declared-type trust: an `int`-annotated parameter/field/local receives whatever the caller passes; an `Any`
(erased) actual is not checked against the annotation, so #251's uninterpreted arithmetic is bypassed one call
away. `no_exception`: #251 kept `pycsl_py_sub` total, so a raising user dunder is not an exception site.

## Repair direction
(a) Refuse (or require a proof obligation for) an erased/`Any` value flowing into a slot whose type the model
interprets (int/float/str/bool params, fields, annotated locals) — fail-closed at the call/store; measure blast
radius; (b) under `no_exception`, any `pycsl_py_*` operation on an erased operand is an exception site (refuse
or require proof).

## Repair landed (gen #36, 2026-10-16)

### Step 1: census (base 15f8c4bd, measured before any code)
A harness over `_reset_function_state` classified every flow of an expression into a declared slot with route
#249's OWN erased-operand walk (#251's `r251_erased?` probe): call actual -> callee formal (module function,
method of a known class, record constructor, class `__init__`, positional and keyword, body and contract),
`return`, record-field store; plus every erased `pycsl_py_*` emitted inside a `no_exception` function
(`census-base/`). Erased flows into a BUILTIN slot (`int`/`float`/`str`/`bool`/`bytes`): root 13 (all `return`s of
an erased value from `-> int` in #249/#251 witnesses 2375, 2440-2457), 0 into parameters/fields; pyref 3 (0092's
`N(self._v + other._v)` into an unannotated record field the model types `int`; `dumps_proves`' `\trusted`
`encode`, exempt); mirror 106 ARG + 16 RET sites, all but four in `\trusted` functions (exempt): Module5's
`self._py_op_to_str(expr.op)` (its `op: ast.operator | ast.cmpop | ast.unaryop` normalises to `int`),
pure_ast's `_fstring_format_spec(self, is_raw=False)` -> `_decode_fstring_middle(.., is_raw: bool)`, and
`_process_for`'s `return d` (`d: Dict[str, Any]` from a mirror `-> int`). `no_exception` over an erased
operation: 0 sites in root/pyref/mirror. No program-side narrowing is sound: `isinstance(x, int)` is opaque
since #246/#248, and holds for an `int` subclass that overrides `__sub__`.

### Step 2: the rule
(a) In `_reset_function_state` (mirror twin `\trusted`), each flow above into a builtin-declared slot is entered
into route #249's flow-insensitive fixpoint as a binding of a SENTINEL name no Python identifier can spell
(`#r252:<i>`); if the sentinel is erased, the function is REFUSED (`PyCSLSemanticError`, "an erased ... value
flows into a slot declared as a builtin type: <slot list> ... (route #252) -- refused fail-closed. Annotate the
source value with the builtin type, or declare the slot `Any`."). No copy of the walk, no new def, no new
per-function field. A `\trusted`/abstract function emits no body and is not checked. A WHOLE route-#249
container (`d: Dict[str, Any]` as a value) is not an erased scalar and is skipped. A record local's base class
is read from the record constructor it is bound from (its symbol type is not its class).
(b) In `_handle_binop` / `_expr_to_whyml`'s unary dispatch (mirror twins `\trusted`), an erased operation in a
program body under an active `no_exception` context is prefixed with
`assert { [@expl:PyCSL-R252 an operation on an erased (Any) operand runs a user method that may raise] false }`
(route #186's form for a call that cannot be shown exception-free): arithmetic, ordering, unary, `==`/`!=`/`in`.
Ledger 3, no axiom. Live annotations so the mirror stays emitted (each a correct, narrower-or-equal type, ported
verbatim to the mirror): `_py_op_to_str(self, op: ast.AST)` (was a union of AST classes, normalised to `int`),
`_fstring_replacement`/`_fstring_format_spec(self, is_raw: bool = False)` (every caller passes
`_fstring_prefix_raw`'s `bool`).

### Blast radius and gates (logs: `/tmp/claude-1000/-home-fabrice-git-pycsl/7bdb4936-b536-4d12-86b7-7ad1b607106c/scratchpad/r252/`)
- Witnesses (`witness-base.log`: all 13 PROVED and the 4 controls PASS at 15f8c4bd; `witness-after.log`):
  2470 `g(x, x)` into `int` params, 2471 `Box(x, x)` into `int` fields, 2472 keyword actuals, 2473 method params,
  2474 `b.v = x`, 2475 `return x` from `-> int` (`\result - \result == 0`), 2476 its caller (`y = h(x); y - y`),
  2477 `g(x, x) == 0` in a contract, 2478 unannotated source -- each REFUSED; `no_exception` 2479 `x - x`,
  2480 `x == x`, 2481 `x < y`, 2482 `-x` -- each FAILS on the R252 obligation. Controls 2490 (typed and
  literal flows), 2491 (`Any` into `Any`), 2492 (`int` into `int` fields), 2493 (`no_exception` over `int`):
  PASS both sides. CPython ground truth in each `__main__`.
- Corpus byte-diff vs a fresh 15f8c4bd worktree: root 1694 baseline / 1689 candidate, 0 MOVED, 13 GONE (2375,
  2440-2444, 2449-2451, 2453-2455, 2457: each `def f(x: <erased>) -> int: return <erased expr>`), 0 APPEARED,
  8 new sources (`compare-root.log`, `compare-root-declared.log` rc=0); pyref 2198 / 2197, 0 MOVED, 1 GONE (0092),
  0 APPEARED (`compare-pyref*.log`). M1 (`m1.log`): all 14 FAIL at base, REFUSED after -- verdict FAIL both
  sides. The 13 #249/#251 witnesses now stop at the route-#252 refusal; #251's law-free lowering stays exercised
  by its emitted witnesses (2445-2448, 2452, 2456, 2458) and by 2479-2482.
- Mirror (`compare-mirror.log`): 53/53, 0 MOVED, 0 GONE, 0 APPEARED (the two annotation changes are
  emission-identical).
- Planes 61/61 (`planes.log`); `check-self-annotate-sync.sh` rc=0 (917 verbatim, `sync.log`);
  `self-annotate-mirror-check.sh` rc=0 (`mirror-check.log`). Witness census: 13 own rows appended by running them
  (`_census_row`), pyref 0092's stale VERIFY-FAIL row re-measured (REFUSAL); advice audit: the refusal's advice
  followed both ways (controls 2490, 2491), recorded FOLLOWABLE.

## Residuals (NOT repaired here)
- **Declared-type trust at the boundary**: an `int` SUBCLASS overriding `__sub__` passed to an `int` parameter:
  `def f(x: int) -> int: return x - x` with `ensures \result == 0` PROVES; CPython `f(I(1))` is 7 for
  `class I(int): def __sub__(s, o): return 7` (`residual-after.log`, `res/res_intsub.py`). Every typed parameter
  is affected; the fix is a model decision (exact-type params), not a flow rule.
- Callees the IR does not resolve (imported-module functions, calls through a variable or an attribute chain),
  `Optional[int]`/container-of-builtin slots, and builtins over an erased argument (`abs(x)`) are not checked by
  rule (a); `str`-typed operands keep the string model (#251's residual).
