"""Test 0454 — Python Reference 6.7: Binary arithmetic (variation B)"""
_ = 0  # anchor
#@ ensures \result == a * b
def test_binary_b(a: int, b: int) -> int:
    """Multiplication."""
    return a * b

if __name__ == "__main__":
    assert test_binary_b(6, 7) == 42
