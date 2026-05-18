"""Test 0018 — Python Reference 2.4: Literals"""
_ = 0  # anchor
#@ ensures \result == 42
def test_literals() -> int:
    """Literals are notations for constant values of built-in types."""
    return 42

if __name__ == "__main__":
    assert test_literals() == 42
