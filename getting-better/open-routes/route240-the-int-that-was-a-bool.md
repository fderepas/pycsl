# ROUTE #240 (REPAIRED) — `isinstance(<int>, bool)` IS DECIDED TRUE

**Status: REPAIRED (gen #36, 2026-10-15; opened the same day), Severity 1.** Recorded as a residual by the #239 repair executor;
driver-reproduced at HEAD ab2c2d4f (rc=0 "Verification SUCCESS"; CPython `f(5)` = 0).

## Witness
`witnesses-r240/isinstance_int_is_bool.py`: `def f(x: int)`: `if isinstance(x, bool): return 1` / `return 0`,
`ensures \result == 1` PROVES.

## Mechanism (per the #239 executor)
`_tag_of_value` / isinstance lowering collapses `bool` onto `tag_int` (bool is a subclass of int, so
`isinstance(True, int)` is True — but the converse is false: an int is not a bool). A typed-`int` subject
therefore decides `isinstance(x, bool)` TRUE.

## Repair direction
`isinstance(<int-typed>, bool)` must be opaque (or decided by a modelled bool flag), never true;
`isinstance(<bool-typed>, int)` stays true. Check the hval `HInt` arm (already opaque after #237) and the
`True`/`1` typeof_op collision noted in the #239 doc.

## Probe table (CPython ground truth on every row; "base" = 1e4b380e)
| shape | base emission | base | after emission | after |
|---|---|---|---|---|
| `x: int`, `isinstance(x, bool)` (2240) | `(0 = 0)` | PROVED (CPython `f(5)` = 0) | `(py_isinstance_bool_int_op x)` | FAIL (post Unknown) |
| `x: Any`, bool test inside the int test (2241) | both `(typeof_op x) = 0`, one term | PROVED (CPython 0) | int test `typeof_op x = 0`, bool test `py_isinstance_bool_int_op x` | FAIL |
| `requires isinstance(x, bool)` on `x: int`, caller `g(5)` (2248) | `subtag tag_int tag_int` (closed TRUE) | PROVED (CPython: precondition violated, `m()` = 0) | program `val` in a contract | FAIL closed (L3-tc: unbound symbol — the answer `requires isinstance(x, <unknown class>)` already gets) |
| `b: bool` param called with `5` (2249) | `(0 = 0)` | PROVED (CPython `f(5)` = 0) | `py_isinstance_bool_int_op b` | FAIL |
| `isinstance(<bool>, int)` (control 2250) | `(0 = 0)` | PASS | unchanged | PASS |
| `isinstance(<str>, bool)` (control 2251) | `(1 = 0)` | PASS (`\result == 0`) | unchanged | PASS |
| `isinstance(x, (int, bool))`, `(str, bool)` | receiver-carrying `py_isinstance_*_int_op` disjunction | opaque | unchanged | opaque (sound) |
| `type(x) is bool` / `type(x) == bool` | `(py_type_1 x) = bool`, a program `val` | opaque | unchanged | opaque (but see residual 1) |
| `isinstance(True, bool) == isinstance(1, bool)` (literal subjects) | `typeof_op (1) = 0` twice | FAIL (bool-into-int ref, not a proof) | `isinstance_op 0 0` (fresh) | FAIL |
| `str(True) == str(1)` | — | FAIL | — | FAIL |

## Repair landed (gen #36, 2026-10-15)
`_handle_isinstance`: when the target is `bool` and the subject's tag is `tag_int` or undecided (an `int`, `bool`,
`Any`, untyped or non-`Var` subject), `t_tag` is cleared so the test takes the EXISTING unknown-class arm: the
receiver-carrying `py_isinstance_bool_<t>_op` (a program `val`, fresh per evaluation, never a function of the
collapsed value, so `True` and `1` are never forced to agree), or the historical `isinstance_op 0 0` when the
receiver type cannot be named. The tuple form already took that arm. A subject with a concrete NON-int tag still
decides `bool` FALSE; `isinstance(<bool>, int)` stays TRUE. The first spelling kept a `bool`-DECLARED subject decided
TRUE; `check-corpus-contract-truth-args` rejected control 2250 on `f(5)` (the model admits an int actual for a `bool`
parameter — both are `int`), the ratchet was right, and the exception was dropped (witness 2249). The `True`/`1`
`typeof_op` collision #239 named is now harmless: `typeof_op` is only ever compared with non-bool tags, on which
`True` and `1` agree. Inline, live-only (`_handle_isinstance` has a `\trusted` mirror twin); no new def, raise,
refusal or axiom; ledger 3.

## Residuals (NOT repaired here)
1. **A `let function` FREEZES its fresh devices.** `h(x: int)` = `if isinstance(x, bool): return 1 / return 0`
   is emitted as `let function h`, whose body calls the program `val` `py_isinstance_bool_int_op`; Why3 then gives
   `h` ONE value per argument, and since `True` lowers to `1`, `m()` = `h(True) == h(1)` PROVES `\result == 1`
   (CPython 0) at base AND after (`scratchpad/r240/res/hb.py`; `type(x) == bool` twin `tb.py`). Measured
   directly: `let function r () : int = (any int)` proves `r () = r ()`. Same mechanism as route #241's residual
   (`rr.py`). Needs its own route: a `let function` whose body holds `any`/a program `val` application must not be
   a logic symbol (or the `True`->`1` actual lowering must carry boolness).
2. `hval_isinst_opaque h "bool"` (route #237's spec-side opaque) is a function of the hval, and `True`/`1` are both
   `HInt 1`; spec-only, not probed here.
