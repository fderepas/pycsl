"""Test 0190 — Python Reference 8.4.4: finally clause"""
_ = 0  # anchor
#@ ensures \result == 0
def test_finally_clause() -> int:
    """Ref 8.4.4: finally clause."""
    return 0

if __name__ == "__main__":
    assert test_finally_clause() == 0
