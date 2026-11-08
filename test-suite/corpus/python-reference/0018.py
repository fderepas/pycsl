"""Test 0018 — Python Reference 2.4: Literals"""
_ = 0  # anchor
#@ ensures \result == 42
#@ assigns \nothing
def test_literals() -> int:
    """Ref 2.4: a literal is a notation for a CONSTANT value of a built-in type — the
    same notation always denotes the same value, so a contract may name it. Previously
    the whole body was `return 42` and the postcondition was discharged by the tail
    `return` alone, exercising nothing (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    n = 40
    s = "ab"
    if len(s) == 2:
        return n + 2
    return 0

if __name__ == "__main__":
    assert test_literals() == 42
