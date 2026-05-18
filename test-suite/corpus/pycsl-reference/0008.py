"""Test 0008 — PyCSL Annotation Reference 3.1.1"""
_ = 0  # anchor
#@ ensures \result == 42
def test_number_literal() -> int:
    """Number atom: integer literal in contracts."""
    return 42

if __name__ == "__main__":
    assert test_number_literal() == 42
