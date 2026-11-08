# OPEN ROUTE #232 — THE KEYWORD-ONLY PARAMETER THAT BECAME A MODULE CONSTANT

**Status: REPAIRED (gen #36, 2026-10-13), Severity 1.** Was: OPEN (gen #36, 2026-10-13). Surfaced by the chain-probe executor while
re-probing `check_imports` (its `*, stub_dir` params were missing from the emitted signature);
driver reproduced in the corpus language at HEAD a6d084e8.

## Witness (PROVED at HEAD; CPython `g()` returns 0)

    #@ ensures True
    #@ assigns \nothing
    def f(*, k: int) -> int:
        return k

    #@ ensures \result == 1
    #@ assigns \nothing
    def g() -> int:
        if f(k=3) == f(k=4):
            return 1
        return 0

## Mechanism
The keyword-only parameter `k` is dropped from the emitted signature (`let function f () : int`),
the body's read of `k` resolves to an auto-declared opaque `val constant k : int`, and both call
sites become `f ()`, so `f(k=3) = f(k=4)` is a theorem. (A contract mentioning `k` is refused —
"Undefined variable 'k' referenced in contract" — which is why it hid: only contract-free uses leak.)

## Repair direction
Emit keyword-only parameters as ordinary parameters (call sites bind keyword actuals by name), or
refuse keyword-only parameters fail-closed. Census corpus + mirror usage first.

## Census (at 3e758c0b)
* `pycsl-reference`: 11 functions with keyword-only params (all with defaults) — 10 are `__init__`
  (route #82/#147/#149/#155 constructor binding, unaffected) + `0683.py::f` (mutable-default refusal);
  1 positional-only (`1206`, an `__init__`); 12 `*args`; 1 `**kwargs` (`1906`). 120 calls with keywords.
* `python-reference`: 0 keyword-only, 0 positional-only, 2 `*args`, 1 keyword call. Its json tests
  import `src/pycsl_lib/json` (`dump/dumps/load/loads` carry keyword-only params + `**kw`).
* mirror (`src/self-annotate/src/**`): 12 keyword-only functions (all defaulted: `validate_ir`,
  `run_ir_semantic_checks`, `check_imports`, `PyCSLError.__init__`, `ConcurrencyChecker.__init__`,
  `pure_ast.parse/dump/get_source_segment/_Unparser.__init__/block/_str_literal_helper/
  _write_str_avoiding_backslashes`), 11 `*args`, 4 `**kwargs`, 333 keyword calls.

## Related shapes probed (at 3e758c0b, corpus language)
| shape | verdict at 3e758c0b | now |
|---|---|---|
| keyword-only `def f(*, k)` | **UNSOUND** (the witness) | faithful (1974/1975/1976) |
| two keyword-only defaults `f(*, k=3)` / `h(*, k=4)` | **UNSOUND**: `f() == h()` proved (one shared `val constant k`) | faithful (1979) |
| keyword-only default omitted vs given: `f() == f(k=4)` with `k=5` | **UNSOUND** (proved) | faithful |
| positional-only `def f(a, /)` | dropped the same way; calls `f(3)` were an accidental Why3 arity error | faithful (1983) |
| positional-only with defaults `f(a=3, /)` / `h(a=4, /)` | **UNSOUND**: `f() == h()` proved | faithful (1980) |
| `**kw` read in the body (`len(kw)`) | **UNSOUND**: `f(a=3) == f(a=4, b=5)` proved | refused fail-closed (1981) |
| `*args` unannotated | faithful (`seq int`, ladder 1a) | unchanged |
| `*args: int` / star-forwarded `*args` | dropped; any non-empty call is an accidental Why3 arity error (fail-closed by luck), zero-arg calls are consistent | unchanged — left as is |
| keyword actuals reordered `f(b=2, a=1)` | faithful (1977 PASS / 1978 FAIL) | unchanged |
| positional actual into a keyword-only formal `f(3)` | (unreachable: param dropped) | refused fail-closed (1982 plain call, 1985 method call) |
| keyword-only after a modelled `*vals: str` | (dropped) | refused fail-closed (1984) |
| `c.m(k=3)` on a non-`self` receiver | `c_m_0 ()` havoc | keyword dropped by the abstract method-call lowering; a contract naming `k` leaves an unbound `x0` (Why3 rejection, fail-closed); no contract → havoc (sound) |

## The auto-declared `val constant` fallback (`expressions.py::_handle_var_expr`, last arm)
Any `Var` read that resolves to no local / param / shared var / folded module constant / module
global object / nullary ctor / class becomes `val constant <name> : int`. That is sound ONLY for a
name that really denotes ONE fixed value for the whole program (an immutable module global the
model does not otherwise fold). It is UNSOUND whenever the name is a binder the front end failed to
scope: the constant is shared by every call and by every function that uses the same spelling, so
any two reads are provably equal. This route was that defect for dropped PARAMETERS. A further,
different binder of the same family was found while probing (not repaired here — a new route):

    #@ ensures \result == 0            <-- PROVED; CPython f(3) == -1
    def f(x: int) -> int:
        r = 0; s = 0
        match x:
            case y: r = y
        match x + 1:
            case y: s = y
        return r - s

A `match` capture pattern's name is never bound (`if true then r := y` with `val constant y`).
Witness: `witnesses-r232/match_capture_read_as_constant.py`.

## Repair landed (gen #36, 2026-10-13)
* Module 5 `_build_function_symbol_table`: the parameter loop reads `posonlyargs + args + kwonlyargs`.
* Module 5 `_build_function_ir`: `formal_params` = posonly + args (+ modelled vararg) + kwonly;
  positional `defaults` pair with the tail of posonly + args (was `args` alone); keyword-only
  defaults enter `param_defaults` only when a context-free literal (constant / negated number) —
  any other default is omitted so a call leaving it out is refused by the R7 arity check;
  keyword-only after a modelled `*vals` vararg is refused; new IR fields `kwonly_params`,
  `posonly_params`, `kwarg_param`, `kwarg_read` (emitted only when present).
* Module 6 call sites (`_handle_call_expr`): for a callee with those kinds, refuse every call Python
  would reject with TypeError (positional actual reaching a keyword-only formal, keyword naming a
  positional-only formal or an already-bound formal, unknown keyword without `**kwargs`, starred
  actual); keyword actuals already bind by NAME through relaunch #11 + R7. The dotted (method) path
  applies the same refusal, conservatively matched on the method name.
* Module 6 `_reset_function_state`: an emitted (non-`\trusted`) body that reads its `**kwargs`
  parameter is refused (a `**kw` splat forwarded into a call is not a read — the call IR drops it).
* Module 6 `_handle_tuple_unpack_stmt`: when keywords make the abstract call's arity exceed the
  positional count, the unpack reads the arity off the lowered application (mirror `pure_ast` needed it).
* `bin/check-corpus-contract-truth-args.py` had the same `node.args.args` defect (ran `f(a, /, b)`
  as `f(b)`): it now passes posonly params and skips keyword-only functions with the reason.

Gates (gen #36, base worktree at 3e758c0b): corpus byte-diff 0 MOVED / 0 GONE / 0 APPEARED over 1434
(+8 new witness emissions); pyref 9/2199 MOVED, all `stdlib/json/*` (the `json` stub's keyword-only
params now in the `val` signature, omitted keywords filled with their literal defaults; all 9 still
type-check, as at base); mirror 12/53 MOVED, 0 GONE, all type-check (L3-tc) — signature growth
(`validate_ir`/`run_ir_semantic_checks`/`check_imports`/json), `raises { PyCSLIRError }` on
`_build_function_ir`'s stub (the new refusal), `pure_ast` `_write_str_avoiding_backslashes` /
`block` now bind `quote_types`/`extra` (base: `let quote_types = ref 0` and `val constant extra`),
and `Module6_WhyMLTranspiler` (new `_module_method_param_kinds` field). Whole-file re-proofs
identical to base: audit_proof_reverify, frontend/__init__, import_classifier, ir_resolve, ir_schema.
IR conformance 38/38 + 38/38; mirror sync 905/905 + mirror-check 53/53; fast planes 61/61 rc=0.
Witnesses 1974-1985 (FAIL 1974/1978/1979/1980/1981/1982/1984/1985, PASS 1975/1976/1977/1983);
1974/1979/1980/1981 PROVED at 3e758c0b. Whole-file re-proof OWED: pycsl.py and
Module6_WhyMLTranspiler.py (both timed out at 3000s at base AND candidate), core_ir_semantic,
pure_ast, module6_whyml/{expressions,statements,stmt_control_flow} (>1500 lines).
