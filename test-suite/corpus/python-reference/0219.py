"""Test 0219 — Python Reference 1.1: Alternate Implementations (variation A)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result >= x
def test_alt_impl_a(x: int) -> int:
    """Integer arithmetic behaves same across implementations."""
    return x + x

if __name__ == "__main__":
    assert test_alt_impl_a(5) == 10
