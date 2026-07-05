"""Test 0874 — string-valued `or`/`and` faithful lowering (POSITIVE).

When BOTH operands of a Python `or`/`and` are string-typed, the expression is a
STRING (not a bool): Python string truthiness is non-emptiness, so `s or t`
returns the first operand when non-empty else the second, and `s and t` returns
the second when the first is non-empty else the first. The emitter lowers this to
a faithful `string`-typed if-then-else over `str_length_op … > 0` (the program-
safe bridge for `String.length`), with NO int leak and NO new axiom.

Each concrete case pins a CONCRETE result — a non-empty first operand (hit) and an
empty first operand (default) for both `or` and `and` — and must discharge (Z3).
"""


#@ ensures \result == "a"
def or_first_truthy() -> str:
    """"a" or "b" == "a" — first operand non-empty (truthy)."""
    return "a" or "b"


#@ ensures \result == "b"
def or_first_falsy() -> str:
    """"" or "b" == "b" — first operand empty (falsy) -> second."""
    return "" or "b"


#@ ensures \result == "b"
def and_first_truthy() -> str:
    """"a" and "b" == "b" — first operand non-empty -> second."""
    return "a" and "b"


#@ ensures \result == ""
def and_first_falsy() -> str:
    """"" and "b" == "" — first operand empty (falsy) -> first."""
    return "" and "b"


if __name__ == "__main__":
    assert or_first_truthy() == "a"
    assert or_first_falsy() == "b"
    assert and_first_truthy() == "b"
    assert and_first_falsy() == ""
