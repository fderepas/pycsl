"""Test 0189 — Python Reference 8.4.3: else clause"""
_ = 0  # anchor
#@ ensures \result == 0
def test_else_clause() -> int:
    """Ref 8.4.3: else clause."""
    return 0

if __name__ == "__main__":
    assert test_else_clause() == 0
