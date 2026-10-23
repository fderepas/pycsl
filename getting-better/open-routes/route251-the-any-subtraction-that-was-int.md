# OPEN ROUTE #251 — ARITHMETIC ON `Any` IS INT ARITHMETIC; A USER `__sub__` BREAKS `x - x == 0`

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Residual of the #249 repair (same family as #227/#249);
driver-verified at HEAD c5c703ad: rc=0.

## Witness
`witnesses-r249/any_sub_self_is_zero.py`: `f(x: Any) -> Any: return x - x` with `ensures \result == 0` PROVES;
CPython can return 7 via a user `__sub__`.

## Mechanism
`Any`/erased values are ints, and `+ - * // %` on them lower to Why3 integer arithmetic with all its laws.

## Repair direction
Mirror #249: arithmetic with an erased operand lowers to uninterpreted `pycsl_py_add/sub/...` (no laws), keeping
integer arithmetic for builtin-typed operands. Measure the corpus blast radius first.
