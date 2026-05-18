"""Test 0081 — PyCSL Annotation Reference 3.1.1 (variation B)"""
_ = 0  # anchor
#@ ensures \result == -1
def test_negative_literal() -> int:
    """Number atom: negative literal in contracts."""
    return 0 - 1

if __name__ == "__main__":
    assert test_negative_literal() == -1
