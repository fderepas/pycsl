"""Test 0189 — Python Reference 8.4.3: else clause"""
_ = 0  # anchor
#@ ensures \result == 99
#@ assigns \nothing
def test_else_clause() -> int:
    """Ref 8.4.3: the `else` clause of a `try` runs ONLY when the `try` block completed
    WITHOUT raising, and it runs BEFORE the enclosing `finally`. So on the no-exception
    path the `else` body's effect is visible in the returned value, and the `except`
    body's is not. The contract pins that value, so it is an obligation on the emitter's
    try-statement lowering rather than on any literal. Previously the whole body was
    `return 0` and the postcondition was discharged by the tail `return` alone,
    exercising no `try` at all (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    n = 0
    try:
        n = 1
    except ValueError:
        n = 99
    else:
        n = n + 2
    return n

if __name__ == "__main__":
    assert test_else_clause() == 3
