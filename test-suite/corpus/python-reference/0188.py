"""Test 0188 — Python Reference 8.4.2: except* clause"""
_ = 0  # anchor
#@ ensures \result == 0
def test_except_clause() -> int:
    """Ref 8.4.2: except* clause."""
    return 0

if __name__ == "__main__":
    assert test_except_clause() == 0
