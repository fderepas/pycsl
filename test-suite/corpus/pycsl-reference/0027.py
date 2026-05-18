"""Test 0027 — PyCSL Annotation Reference 3.2.7"""
_ = 0  # anchor
#@ ensures \result == a + b - 1
def test_additive_operators(a: int, b: int) -> int:
    """Additive operators + and - in contracts."""
    return a + b - 1

if __name__ == "__main__":
    assert test_additive_operators(3, 4) == 6
