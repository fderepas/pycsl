"""Test 0220 — Python Reference 1.1: Alternate Implementations (variation B)"""
_ = 0  # anchor
#@ ensures \result == a * b
def test_alt_impl_b(a: int, b: int) -> int:
    """Multiplication semantics across implementations."""
    return a * b

if __name__ == "__main__":
    assert test_alt_impl_b(3, 4) == 12
