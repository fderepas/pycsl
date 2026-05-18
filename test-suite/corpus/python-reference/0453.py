"""Test 0453 — Python Reference 6.7: Binary arithmetic (variation A)"""
_ = 0  # anchor
#@ ensures \result == a + b - c
def test_binary_a(a: int, b: int, c: int) -> int:
    """Addition and subtraction."""
    return a + b - c

if __name__ == "__main__":
    assert test_binary_a(10, 5, 3) == 12
