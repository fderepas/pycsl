"""Static gate T5 (negative) — a non-`...` body is NOT an overload stub.

Spec clause O1a (§1.0): "Each `@overload` stub's body is the literal `...`
(Ellipsis) or `pass` — it carries NO executable code; it is a pure signature
declaration. A stub with a non-`...` body is NOT an overload stub (it is a
regular decorated function)."

This driver: an `@overload`-decorated function with a REAL body (`return x`,
not `...`/`pass`). It is NOT collected as an overload stub — it is treated as a
regular decorated function (byte-identical fallback). No guarded postcondition
is synthesized; the function is emitted normally with its own body.

Expected (from spec): prove — the function is a regular function; its own
`#@ ensures \result == x` discharges; the call site sees the function's own
postcondition.
"""

from typing import overload


#@ ensures \result == x
@overload
def f(x: int) -> int:
    return x


#@ ensures \result == 7
def g() -> int:
    return f(7)


if __name__ == "__main__":
    assert g() == 7
    print("PASS")
