"""string-valued `or`/`and` POSITIVE driver.

When BOTH operands of a Python `or`/`and` are string-typed, the expression is a
STRING (Python truthiness of a string is non-emptiness): `s or t` returns the
first operand when non-empty else the second; `s and t` returns the second when
the first is non-empty else the first. Each concrete case discharges.
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
