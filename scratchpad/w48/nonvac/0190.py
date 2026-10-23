"""Test 0190 — Python Reference 8.4.4: finally clause"""
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def test_finally_clause() -> int:
    """Ref 8.4.4: the `finally` clause runs on EVERY way out of the `try` — including the
    ordinary fall-through — so its effect on a name bound in the `try` is visible after
    the statement. The contract pins the value AFTER both blocks, which is exactly the
    composition a lowering that dropped the `finally` body (or ran it before the `try`)
    would get wrong. Previously the whole body was `return 0`."""
    n = 0
    try:
        n = 1
    finally:
        n = n + 2
    return n

if __name__ == "__main__":
    assert test_finally_clause() == 3
