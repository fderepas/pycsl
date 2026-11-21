r"""Test 0930 — TAIL-return `bool` -> `int` coercion (W8 capability (vii)).

Python `bool` is modelled as WhyML `int` throughout PyCSL (bool params, bool record
fields, `True`/`False` literals, and the early/in-loop `raise (Return …)` path all
coerce via `_bool_ir_to_int_wrap`). The TAIL (non-raise) return was the ONE position
that did NOT: a function whose only exit is its final `return` emitted the raw WhyML
`bool` into an `int`-typed `let`, e.g.

    def is_op(x: int) -> bool: return x == 55
    ->  let is_op (x: int) : int = (x = 55)          (* ill-typed *)

which failed L3 type-check ("This expression has type bool, but is expected to have
type int"). That is a PRE-EXISTING emitter bug, not a modelling choice: the same
function written with an `if`/early return already coerced correctly, so the two
spellings of one program disagreed.

The fix applies the SAME normalization the raise path uses, at the tail position, and
only when the function's WhyML return type is `int` — unit / string / array / record /
union returns are untouched.

IDEMPOTENCE. A few Compare lowerings already produce the int form themselves: the
string relational operators emit `(if (str_lt_op s t) then 1 else 0)` directly
(corpus 0477-0480). Re-wrapping those would give `(if (if … then 1 else 0) then 1
else 0)` — ill-typed AND a corpus byte-diff. `str_lt` / `str_le` below pin that
guard: they are tail-return `-> bool` string comparisons and must emit exactly ONE
coercion layer.

NON-VACUITY / ANTI-FACADE. Every postcondition here is a two-sided VALUE
specification of the coerced Python truth value (`x == 55 ==> \result == 1` AND
`x != 55 ==> \result == 0`), never `ensures True`. Both directions are needed: a
coercion that collapsed to the constant 1 satisfies the first and fails the second,
and vice versa. MUTATION TEST: flipping `is_op`'s first clause to `\result == 0`
leaves the goal Unknown, so these are falsifiable. `both` / `either` pin the BoolOp
sources, `not_op` the UnaryOp source, `lit_true` / `lit_false` the literal atoms, and
`mixed` shows the tail and the early-return positions of ONE function agreeing.

`str_lt` / `str_le` carry only `\result == 1 or \result == 0`: their role here is the
BYTE-level idempotence guard above, and PyCSL has no TERM-level string relational
symbol (`str_lt_op` is a program `val`, unusable inside an `ensures`), so a two-sided
value spec cannot be written for them. The `1 or 0` clause still fails if the coercion
emitted a raw bool or an unconstrained int.

KNOWN ADJACENT GAP (not fixed here). Because a `-> bool` function's WhyML result is
`int`, a postcondition may not compare `\result` to a Python bool TERM
(`\result == (x == 55)` emits `result = (x = 55)`, int vs bool). The contract side has
no matching bool->int coercion; the implication shape above is the workaround. That is
a separate capability from this statement-level fix.

BYTE-INERT: no corpus or `pycsl_lib` function declares `-> bool`, and an
`int`-returning function whose tail value was a bool-source expression could not have
been emitting before (it did not type-check). Full 774-file corpus byte-diff = 0.
No new axiom, no abstract val.
"""


#@ requires True
#@ ensures x == 55 ==> \result == 1
#@ ensures x != 55 ==> \result == 0
def is_op(x: int) -> bool:
    return x == 55


#@ requires True
#@ ensures x != 55 ==> \result == 1
#@ ensures x == 55 ==> \result == 0
def not_op(x: int) -> bool:
    return not (x == 55)


#@ requires True
#@ ensures (x == 1 and y == 2) ==> \result == 1
#@ ensures not (x == 1 and y == 2) ==> \result == 0
def both(x: int, y: int) -> bool:
    return x == 1 and y == 2


#@ requires True
#@ ensures (x == 1 or y == 2) ==> \result == 1
#@ ensures not (x == 1 or y == 2) ==> \result == 0
def either(x: int, y: int) -> bool:
    return x == 1 or y == 2


#@ requires True
#@ ensures \result == 1
def lit_true() -> bool:
    return True


#@ requires True
#@ ensures \result == 0
def lit_false() -> bool:
    return False


#@ requires True
#@ ensures \result == 1 or \result == 0
def str_lt(s: str, t: str) -> bool:
    return s < t


#@ requires True
#@ ensures \result == 1 or \result == 0
def str_le(s: str, t: str) -> bool:
    return s <= t


#@ requires True
#@ ensures x > 0 ==> \result == 1
#@ ensures x <= 0 ==> \result == 0
def mixed(x: int) -> bool:
    if x > 10:
        return True
    return x > 0


if __name__ == "__main__":
    assert is_op(55)
    assert not is_op(1)
    assert not_op(1)
    assert both(1, 2)
    assert not both(1, 3)
    assert either(1, 3)
    assert lit_true()
    assert not lit_false()
    assert str_lt("a", "b")
    assert str_le("a", "a")
    assert mixed(11)
    assert mixed(1)
    assert not mixed(0)
